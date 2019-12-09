import time

import tornado.escape
import tornado.web
import tornado.websocket
from sqlalchemy import or_
from tornado.web import Finish
import dal.models as models
from celerywork.log_async_work import purchasing_dynamics
from dal.db_configs import DBSession, statistic_DBSession, auth_redis, redis
from dal.redis_keys import KEY_PURCHASING_DYNAMICS_NOTIFICATIONS
from handlers.base.webbase import BaseHandler
from settings import MP_APPID, APP_OAUTH_CALLBACK_URL, AUTH_COOKIE_DOMAIN, AUTH_COOKIE_EXPIRE_DAYS


# 全局基类方法
class GlobalBaseHandler(BaseHandler):
    @property
    def session(self):
        if hasattr(self, "_session"):
            return self._session
        self._session = DBSession()
        return self._session

    @property
    def statistic_session(self):
        if hasattr(self, "_statistic_session"):
            return self._statistic_session
        self._statistic_session = statistic_DBSession()
        return self._statistic_session

    # 关闭数据库会话
    def on_finish(self):
        if hasattr(self, "_session"):
            self._session.close()
        if hasattr(self, "_statistic_session"):
            self._statistic_session.close()

    # 判断是否为微信浏览器
    def is_wexin_browser(self):
        if "User-Agent" in self.request.headers:
            ua = self.request.headers["User-Agent"]
        else:
            ua = ""
        return "MicroMessenger" in ua

    # 判断是否为PC浏览器
    def is_pc_browser(self):
        if "User-Agent" in self.request.headers:
            ua = self.request.headers["User-Agent"]
        else:
            ua = ""
        return not ("Mobile" in ua)

    # 判断是否是采购助手APP
    def is_caigou_app(self):
        if "User-Agent" in self.request.headers:
            ua = self.request.headers["User-Agent"]
        else:
            ua = ""
        return "senguo:cgapp" in ua

    # 判断采购助手客户端操作系统
    def client_os(self):
        ua = self.request.headers.get("User-Agent", "")
        if "senguo:ioscgapp" in ua:
            return "ios"
        elif "senguo:androidcgapp" in ua:
            return "android"
        else:
            return ""

    # 错误页面的处理
    def write_error(self, status_code, error_msg='', error_deal='', **kwargs):
        if status_code == 400:
            self.send_fail("参数错误: %s" % error_msg, 400)
        elif status_code == 401:
            self.send_fail(error_msg or "未授权调用", 401)
        elif status_code == 404:
            self.send_fail(error_msg or "地址错误", 404)
        elif status_code == 500:
            from handlers.servererror import ServerAlarm
            ServerAlarm.send_server_error(self.request.uri, **kwargs)
            self.send_fail(error_msg or "系统错误", 500)
        elif status_code == 403:
            self.send_fail(error_msg or "没有权限", 403)
        else:
            super().write_error(status_code, **kwargs)

    # 导出csv文件
    def export_to_csv(self, data_content, file_name):
        import csv
        import io
        csv_file = io.StringIO()
        csv_writer = csv.writer(csv_file)
        csv_writer.writerows(data_content)
        filename = 'attachment; filename="%s"' % (file_name + ".csv")
        self.set_header('Content-Type', 'application/octet-stream;charset=UTF-8')
        self.set_header('Content-Disposition', filename.encode("utf-8"))
        return self.write(csv_file.getvalue().encode("utf-8-sig"))

    def export_xlsx(self, workbook, filename):
        from openpyxl.writer.excel import save_virtual_workbook
        virtual_workbook = save_virtual_workbook(workbook)
        filename = 'attachment; filename="%s"' % (filename + ".xlsx")
        self.set_header('Content-Type', 'application/vnd.ms-excel;charset=UTF-8')
        self.set_header('Content-Disposition', filename.encode("utf-8"))
        return self.write(virtual_workbook)


# 登录、账户等基类方法
class _AccountBaseHandler(GlobalBaseHandler):
    _wx_oauth_weixin = "https://open.weixin.qq.com/connect/oauth2/authorize?appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_userinfo&state=onfuckweixin#wechat_redirect"

    # overwrite this to specify which account is used
    __account_model__ = models.AccountInfo
    __account_cookie_name__ = "passport"
    __token_cookie_name__ = "passport_hash"
    __wexin_oauth_url_name__ = "oauth"

    # 获取当前用户（判断用户是否登录）
    def get_current_user(self):
        if not self.__account_model__ or not self.__account_cookie_name__:
            raise Exception("overwrite model to support authenticate.")
        # 如果已登录，直接返回
        if hasattr(self, "_user"):
            return self._user
        # 检查account_cookie要存在，不存在则退出
        account_cookie = self.get_secure_cookie(self.__account_cookie_name__, max_age_days=int(AUTH_COOKIE_EXPIRE_DAYS))
        if not account_cookie:
            self.clear_current_user()
            return None
        # 检查account_cookie未过期，过期则退出
        passport_id, create_time = [int(i) for i in account_cookie.decode().split("|")]
        if time.time() - create_time >= int(AUTH_COOKIE_EXPIRE_DAYS)*24*60*60:
            self.clear_current_user()
            return None
        # 检查hash，hash不存在退出
        passport_hash = self.get_secure_cookie(self.__token_cookie_name__, max_age_days=int(AUTH_COOKIE_EXPIRE_DAYS))
        if not passport_hash:
            self.clear_current_user()
            return None
        # hash有更新，也退出
        passport_hash = passport_hash.decode()
        real_hash = (auth_redis.get("passport_hash:{}".format(passport_id)) or b"").decode()
        if real_hash and real_hash!=passport_hash:
            self.clear_current_user()
            return None
        # 查询用户
        current_user = self.__account_model__.get_by_passport_id(self.session, passport_id)
        if not current_user:
            self.clear_current_user()
            return None
        # 设置用户
        self._user = current_user
        return self._user

    # 设置当前用户
    _ARG_DEFAULT = []
    def set_current_user(self, user, domain=AUTH_COOKIE_DOMAIN):
        if not self.__account_model__ or not self.__account_cookie_name__:
            raise Exception("overwrite model to support authenticate.")
        self.set_secure_cookie(
            self.__token_cookie_name__,
            self.__account_model__.calc_passport_hash(user.passport_id),
            domain=domain,
            expires_days=int(AUTH_COOKIE_EXPIRE_DAYS),
        )
        self.set_secure_cookie(
            self.__account_cookie_name__,
            str(user.passport_id) + "|" + str(int(time.time())),
            domain=domain,
            expires_days=int(AUTH_COOKIE_EXPIRE_DAYS),
        )

    # 清除当前用户
    def clear_current_user(self):
        if not self.__account_model__ or not self.__account_cookie_name__:
            raise Exception("overwrite model to support authenticate.")
        self.clear_cookie(self.__account_cookie_name__, domain=AUTH_COOKIE_DOMAIN)
        self.clear_cookie(self.__token_cookie_name__, domain=AUTH_COOKIE_DOMAIN)

    # 平台设置中转站cookie
    def set_current_station_cookie(self, ph_station_id, domain=_ARG_DEFAULT):
        if domain is _AccountBaseHandler._ARG_DEFAULT:
            self.set_secure_cookie("ph_station_id", str(ph_station_id))
        else:
            self.set_secure_cookie("ph_station_id", str(ph_station_id), domain=domain)

    # 清除平台当前的中转站
    def clear_current_station_cookie(self, domain=_ARG_DEFAULT):
        if domain is _AccountBaseHandler._ARG_DEFAULT:
            self.clear_cookie("ph_station_id")
        else:
            self.clear_cookie("ph_station_id", domain=domain)

    # 门店订货设置中转站cookie
    def set_demand_station_cookie(self, demand_station_id, domain=_ARG_DEFAULT):
        if domain is _AccountBaseHandler._ARG_DEFAULT:
            self.set_secure_cookie("ph_demand_station_id", str(demand_station_id))
        else:
            self.set_secure_cookie("ph_demand_station_id", str(demand_station_id), domain=domain)

    # 清除门店订货中转站cookie
    def clear_demand_station_cookie(self, domain=_ARG_DEFAULT):
        if domain is _AccountBaseHandler._ARG_DEFAULT:
            self.clear_cookie("ph_demand_station_id")
        else:
            self.clear_cookie("ph_demand_station_id", domain=domain)

    # 设置店铺cookie
    def set_current_shop_cookie(self, ph_shop_id, domain=_ARG_DEFAULT):
        if domain is _AccountBaseHandler._ARG_DEFAULT:
            self.set_secure_cookie("ph_shop_id", str(ph_shop_id))
        else:
            self.set_secure_cookie("ph_shop_id", str(ph_shop_id), domain=domain)

    # 清除当前店铺
    def clear_current_shop_cookie(self, domain=_ARG_DEFAULT):
        if domain is _AccountBaseHandler._ARG_DEFAULT:
            self.clear_cookie("ph_shop_id")
        else:
            self.clear_cookie("ph_shop_id", domain=domain)

    # 获取服务号微信授权登录链接
    def get_wexin_oauth_link(self, next_url=""):
        if not self.__wexin_oauth_url_name__:
            raise Exception("you have to complete this wexin oauth config.")
        if next_url:
            para_str = "?next="+tornado.escape.url_escape(next_url)
        else:
            para_str = ""
        # 微信中使用公众号授权
        if self.is_wexin_browser():
            if para_str:
                para_str += "&"
            else:
                para_str = "?"
            para_str += "mode=mp"
            redirect_uri = tornado.escape.url_escape(
                APP_OAUTH_CALLBACK_URL+\
                self.reverse_url(self.__wexin_oauth_url_name__) + para_str)
            link = self._wx_oauth_weixin.format(appid=MP_APPID, redirect_uri=redirect_uri)
            return link

    def get_current_user_info(self):
        current_user = self.current_user
        user_info = {}
        if current_user:
            user_info["id"] = current_user.id
            user_info["nickname"] = current_user.nickname or current_user.realname
            user_info["imgurl"] = current_user.head_imgurl_small or ""
            user_info["phone"] = current_user.phone or ""
        return user_info


# 中转站相关接口继承
class StationBaseHandler(_AccountBaseHandler):
    def __init__(self, application, request, **kwargs):
        self.current_station = None
        self.current_staff = None
        super().__init__(application, request, **kwargs)

    def should_check_identity(self):
        return True

    def prepare(self):
        if not self.current_user:
            self.write_error(401, "请先登录再使用")
            raise Finish()

        # 获取中转站和员工身份(优先从cookie中获取)
        station_id = self.get_secure_cookie("ph_station_id")
        filters = list()
        if station_id:
            filters.append(models.TransferStation.id == station_id)
        staff_station = self.session.query(models.Staff, models.TransferStation)\
            .join(models.TransferStation, models.TransferStation.id == models.Staff.station_id)\
            .filter(*filters,
                    models.TransferStation.status == 0,
                    models.Staff.status == 0,
                    models.Staff.account_id == self.current_user.id,
                    or_(models.Staff.super_admin_status == 1,
                        models.Staff.admin_status == 1))\
            .first()

        # 如果没有中转站或员工身份
        if not staff_station:
            if self.should_check_identity():
                self.clear_current_user()
                self.clear_current_station_cookie()
                self.write_error(401, "没有有效的管理员身份")
                raise Finish()

        self.current_staff = staff_station[0] if staff_station else None
        self.current_station = staff_station[1] if staff_station else None


# 订货助手相关接口继承
class DemandBaseHandler(_AccountBaseHandler):
    def prepare(self):
        if not self.current_user:
            self.write_error(401, "请先登录再使用")
            raise Finish()


# 门店相关接口继承
class ShopBaseHandler(_AccountBaseHandler):
    def __init__(self, application, request, **kwargs):
        self.current_contact = None
        self.current_shop = None
        self.current_station = None
        self.current_staff = None
        super().__init__(application, request, **kwargs)

    def prepare(self):
        if not self.current_user:
            self.write_error(401, "请先登录再使用")
            raise Finish()

        # 获取门店、联系人和中转站身份(优先从cookie中获取)
        demand_station_id = self.get_secure_cookie("ph_demand_station_id")
        shop_id = self.get_secure_cookie("ph_shop_id")
        filters = list()
        if demand_station_id:
            filters.append(models.TransferStation.id == demand_station_id)
        if shop_id:
            filters.append(models.Shop.id == shop_id)
        contact_shop_station = self.session.query(models.ShopContact, models.Shop, models.TransferStation) \
            .join(models.Shop, models.Shop.id == models.ShopContact.shop_id) \
            .join(models.TransferStation, models.TransferStation.id == models.Shop.station_id) \
            .filter(*filters,
                    models.Shop.status == 0,
                    models.ShopContact.status == 0,
                    models.TransferStation.status == 0,
                    models.ShopContact.account_id == self.current_user.id) \
            .first()

        # 如果没有门店、联系人和中转站身份
        if not contact_shop_station:
            self.clear_current_user()
            self.clear_current_shop_cookie()
            self.clear_demand_station_cookie()
            self.write_error(401, "没有访问订货单的权限")
            raise Finish()

        self.current_contact = contact_shop_station[0] if contact_shop_station else None
        self.current_shop = contact_shop_station[1] if contact_shop_station else None
        self.current_station = contact_shop_station[2] if contact_shop_station else None


# 采购端
class PurchaseBaseHandler(_AccountBaseHandler):
    def __init__(self, application, request, **kwargs):
        self.current_station = None
        self.current_staff = None
        super().__init__(application, request, **kwargs)

    def prepare(self):
        if not self.current_user:
            self.write_error(401, "请先登录再使用")
            raise Finish()

        # 获取中转站和采购员身份(优先从cookie中获取)
        station_id = self.get_secure_cookie("ph_station_id")
        filters = list()
        if station_id:
            filters.append(models.TransferStation.id == station_id)
        staff_station = self.session.query(models.Staff, models.TransferStation) \
            .join(models.TransferStation, models.TransferStation.id == models.Staff.station_id) \
            .filter(*filters,
                    models.TransferStation.status == 0,
                    models.Staff.status == 0,
                    models.Staff.account_id == self.current_user.id,
                    models.Staff.purchaser_status == 1) \
            .first()

        if not staff_station:
            self.clear_current_user()
            self.clear_current_station_cookie()
            self.write_error(401, "没有有效的采购员权限")
            raise Finish()

        self.current_staff = staff_station[0] if staff_station else None
        self.current_station = staff_station[1] if staff_station else None

    # 记录采购动态(用于采购小程序和平台之间的通信)
    def record_purchasing_dynamics(self, record_type, purchase_goods, **last_data_dict):
        # 记录采购动态
        purchase_goods_dict = purchase_goods.to_dict()

        # 当前操作用户
        purchase_goods_dict["creator_id"] = self.current_user.id

        # 获取上一次的采购单价、数量、重量、小计
        purchase_goods_dict["last_price"] = last_data_dict.get("last_price")
        purchase_goods_dict["last_actual_amount"] = last_data_dict.get("last_actual_amount")
        purchase_goods_dict["last_actual_weight"] = last_data_dict.get("last_actual_weight")
        purchase_goods_dict["last_subtotal"] = last_data_dict.get("last_subtotal")

        # 上一次的商品名称
        purchase_goods_dict["last_goods_name"] = last_data_dict.get("last_goods_name")
        # 上一次的供货商id
        purchase_goods_dict["last_firm_id"] = last_data_dict.get("last_firm_id")

        purchasing_dynamics.delay(record_type, purchase_goods_dict)

        # 发送采购动态更新提醒
        staff_ids = self.session.query(models.Staff)\
            .filter(models.Staff.purchaser_status == 1,
                    models.Staff.station_id == self.current_station.id,
                    models.Staff.status == 0)\
            .all()
        for staff in staff_ids:
            redis.set(KEY_PURCHASING_DYNAMICS_NOTIFICATIONS
                      .format(purchase_goods.purchase_order_id, staff.id, self.current_station.id), "purchasing_dynamics")
