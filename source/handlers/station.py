# -*- coding:utf-8 -*-

import datetime
from sqlalchemy import or_
from tornado.options import options
from dal import models
from handlers.base.pub_func import ProvinceCityFunc, AuthFunc, TimeFunc
from handlers.base.pub_web import StationBaseHandler, PurchaseBaseHandler
from handlers.base.webbase import BaseHandler
from libs.msgverify import check_msg_token


# 中转站
class TransferStation(StationBaseHandler):
    def should_check_identity(self):
        # 注册接口不要求登录中转站
        if self.request.method.upper() == "POST":
            return False
        return super().should_check_identity()

    def get(self, station_id):
        station = models.TransferStation.get_by_id(self.session, station_id)
        if not station:
            return self.send_fail("没有找到该中转站")

        staff = self.session.query(models.Staff) \
            .filter(models.Staff.account_id == self.current_user.id,
                    models.Staff.station_id == station.id,
                    models.Staff.status == 0) \
            .first()
        if not staff:
            return self.send_fail("您不是该中转站的员工")
        if staff.admin_status != 1 and staff.super_admin_status != 1:
            return self.send_fail("您无权查看该中转站的信息")

        station_data = {
            "id": station.id,
            "name": station.name,
            "creator_id": station.creator_id,
            "province": station.province,
            "city": station.city,
            "address": station.address,
            "create_time": TimeFunc.time_to_str(station.create_time),
            "status": station.status,
        }
        return self.send_success(station=station_data)

    @BaseHandler.check_arguments("name:str", "city_code:int", "address:str", "phone:str", "code:str")
    def post(self):
        name = self.args["name"]
        city_code = self.args["city_code"]
        address = self.args["address"]
        phone = self.args["phone"]
        code = self.args["code"]

        province_code = ProvinceCityFunc.city_to_province(city_code)
        if not province_code:
            return self.send_fail("请填写正确的省份")

        if len(phone) != 11:
            return self.send_fail("请填写正确的手机号")

        check_msg_res = check_msg_token(phone, code, use="station_register")
        if not options.debug and not check_msg_res:
            return self.send_fail("验证码过期或者不正确")

        # 检查用于注册的手机号
        success, errmsg = AuthFunc.update_passportinfo(self.current_user.passport_id, "phone", phone)
        if not success:
            if errmsg == "NOT EXIST":
                return self.send_fail("请登录后重试")
            elif errmsg == "SAME VALUE":
                pass
            elif errmsg == "ALREADY BIND":
                return self.send_fail("该手机号已被注册")
        self.current_user.phone = phone

        existed_station = self.session.query(models.TransferStation) \
            .join(models.Staff, models.Staff.station_id == models.TransferStation.id) \
            .filter(models.Staff.super_admin_status == 1,
                    models.Staff.status == 0,
                    models.Staff.account_id == self.current_user.id) \
            .first()
        if existed_station:
            return self.send_fail("您已经是 {} 的超级管理员了".format(existed_station.name))

        # 添加新中转站
        new_station = models.TransferStation(
            name=name,
            province=province_code,
            city=city_code,
            address=address,
            creator_id=self.current_user.id,
        )
        self.session.add(new_station)
        self.session.flush()

        # 添加默认超管
        super_admin = models.Staff(
            station_id=new_station.id,
            account_id=self.current_user.id,
            super_admin_status=1,
            admin_status=1,
            purchaser_status=0,
            date_onboarding=datetime.date.today(),
        )
        super_admin.set_admin_permissions(None, grant_all=True)
        super_admin.set_purchaser_permissions(None, grant_all=True)
        self.session.add(super_admin)

        # 添加设置项
        config = models.Config(id=new_station.id)
        self.session.add(config)

        self.session.commit()
        self.clear_current_user()
        return self.send_success()

    @BaseHandler.check_arguments("name?:str")
    def put(self, station_id):
        name = self.args.get("name")

        station = models.TransferStation.get_by_id(self.session, station_id)
        if not station:
            return self.send_fail("中转站无效")

        if name is not None:
            station.name = name

        self.session.commit()
        return self.send_success()


# 中转站列表Mixin
class TransferStationListMixin:
    @BaseHandler.check_arguments("role?:str")
    def get(self):
        role = self.args.get("role", "").strip()
        # 当前用户作为管理员和采购员的所有中转站
        station_query_set = self.session.query(models.TransferStation)\
            .join(models.Staff, models.Staff.station_id == models.TransferStation.id)\
            .filter(models.TransferStation.status == 0,
                    models.Staff.status == 0,
                    models.Staff.account_id == self.current_user.id)
        if role == "admin":
            stations = station_query_set.filter(or_(models.Staff.super_admin_status == 1,
                                                    models.Staff.admin_status == 1))\
                                        .all()
        elif role == "purchaser":
            stations = station_query_set.filter(models.Staff.purchaser_status == 1)\
                                        .all()
        else:
            # 默认拿管理员的中转站列表
            stations = station_query_set.filter(or_(models.Staff.super_admin_status == 1,
                                                    models.Staff.admin_status == 1)) \
                .all()
        station_list = []
        for station in stations:
            station_list.append({
                "id": station.id,
                "name": station.name,
                "creator_id": station.creator_id,
                "province": station.province,
                "city": station.city,
                "address": station.address,
                "create_time": TimeFunc.time_to_str(station.create_time),
                "status": station.status,
            })

        return self.send_success(station_list=station_list)


# 小程序获取中转站列表
class PurchaseTransferStationList(TransferStationListMixin, PurchaseBaseHandler):
    pass


# 平台获取中转站列表
class TransferStationList(TransferStationListMixin, StationBaseHandler):
    pass


# 当前用户登录的中转站Mixin
class CurrentTransferStationMixin:
    def should_check_identity(self):
        return False

    def get(self):
        station = self.current_station

        data = {}
        if station:
            data = {
                "id": station.id,
                "name": station.name,
                "province": station.province,
                "city": station.city,
                "address": station.address,
                "create_time": TimeFunc.time_to_str(station.create_time),
                "status": station.status,
            }
        return self.send_success(data=data)

    @BaseHandler.check_arguments("station_id:int")
    def put(self):
        station_id = self.args["station_id"]
        change_station = self.session.query(models.TransferStation) \
            .join(models.Staff, models.Staff.station_id == models.TransferStation.id)\
            .filter(models.TransferStation.status == 0,
                    models.Staff.status == 0,
                    models.Staff.account_id == self.current_user.id,
                    models.TransferStation.id == station_id,
                    or_(models.Staff.super_admin_status == 1,
                        models.Staff.admin_status == 1,
                        models.Staff.purchaser_status == 1))\
            .first()
        if not change_station:
            return self.send_fail("中转站切换失败")
        self.set_current_station_cookie(change_station.id, domain=self._ARG_DEFAULT)
        return self.send_success()


# 采购小程序获取当前用户登录的中转站
class PurchaseCurrentTransferStation(CurrentTransferStationMixin, PurchaseBaseHandler):
    pass


# 中转站获取当前用户登录的中转站
class CurrentTransferStation(CurrentTransferStationMixin, StationBaseHandler):
    pass
