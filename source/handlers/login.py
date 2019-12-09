import json

from tornado.options import options
from dal import models
from dal.db_configs import redis, pf_redis
from handlers.base.pub_func import Emoji, AuthFunc, TimeFunc
from handlers.base.pub_web import _AccountBaseHandler
from handlers.base.pub_wx_web import WxTicketUrl, WxOauth2
from handlers.base.webbase import BaseHandler
from libs.msgverify import check_msg_token


# 登录
class LoginState(_AccountBaseHandler):
    def get(self):
        user = self.current_user
        if not user:
            return self.send_success()

        user_data = {
            "id": user.id,
            "phone": user.phone,
            "avatar": user.headimgurl,
            "sex": user.sex,
            "birthday": TimeFunc.time_to_str(user.birthday, "date"),
            "wx_unionid": user.wx_unionid,
            "realname": user.realname,
            "nickname": user.nickname,
        }
        return self.send_success(user=user_data)

    @BaseHandler.check_arguments("action:str")
    def post(self):
        action = self.args["action"]
        if action == "phone":
            return self.login_by_phone_code()
        elif action == "wx":
            return self.login_by_wx_ticket()
        else:
            return self.send_fail(404)

    @BaseHandler.check_arguments("phone:str", "code:str")
    def login_by_phone_code(self):
        """
        手机号+验证码登录，已注册用户直接登录，未注册用户生成新账号并登录
            phone:手机号
            code:验证码
        """
        phone = self.args["phone"].strip()
        code = self.args["code"].strip()

        if len(phone) != 11:
            return self.send_fail("请填写正确的手机号")

        check_msg_res = check_msg_token(phone, code, use="login")
        if not options.debug and not check_msg_res:
            return self.send_fail("验证码错误或已失效")

        # 登录
        success, user_or_msg = AuthFunc.login_by_phone_code(self.session, phone)
        if not success:
            return self.send_fail(user_or_msg)

        # 设置cookie
        self.set_current_user(user_or_msg)

        # 返回微信绑定状态，三者缺一要求重新绑定
        if user_or_msg.wx_unionid and user_or_msg.nickname and user_or_msg.headimgurl:
            wx_bind = True
        else:
            wx_bind = False

        # 更新门店联系人 ID
        contacts = self.session.query(models.ShopContact) \
            .filter(models.ShopContact.phone == phone) \
            .all()
        if contacts:
            for contact in contacts:
                contact.account_id = user_or_msg.id
            self.session.commit()

        return self.send_success(wx_bind=wx_bind)

    @BaseHandler.check_arguments("scene_id:int")
    def login_by_wx_ticket(self):
        """微信扫描二维码登录"""
        scene_id = self.args['scene_id']

        wx_userinfo = pf_redis.get('pf_scene_openid:%s' % scene_id)
        if not wx_userinfo:
            return self.send_success(done=False)
        wx_userinfo = json.loads(wx_userinfo.decode())

        if len(str(scene_id)) == 9:
            success, user_or_msg = AuthFunc.login_by_wx(self.session, wx_userinfo)
            if not success:
                return self.send_fail(user_or_msg)

            user = user_or_msg
            self.set_current_user(user)
        else:
            return self.send_fail("scene_id 无效")

        pf_redis.delete('pf_scene_openid:%s' % scene_id)

        # 更新微信信息
        AuthFunc.update_through_wx(self.session, wx_userinfo, user, action="bind")
        # 手机绑定状态
        phone_bind = bool(user.phone)
        return self.send_success(done=True, phone_bind=phone_bind)

    def delete(self):
        self.clear_current_user()
        return self.send_success()


# 微信/手机绑定
class AccountBind(_AccountBaseHandler):
    @BaseHandler.check_arguments("action:str")
    def post(self):
        action = self.args["action"]

        if action == "wx":
            return self.bind_wx()
        elif action == "phone":
            return self.bind_phone()
        else:
            return self.send_fail("invalid action")

    @BaseHandler.check_arguments("scene_id:int")
    def bind_wx(self):
        """绑定微信"""
        scene_id = self.args['scene_id']

        wx_userinfo = pf_redis.get('pf_scene_openid:%s' % scene_id)
        if not wx_userinfo:
            return self.send_success(done=False)
        wx_userinfo = json.loads(wx_userinfo.decode())
        wx_unionid = wx_userinfo["unionid"]

        # 绑定微信
        if len(str(scene_id)) == 8:
            bind_key = "ph_scene_bind_account:%s" % scene_id
            bind_user_id = redis.get(bind_key) or -1
            user = models.AccountInfo.get_by_id(self.session, bind_user_id)

            # scene_id 不对或者 Redis 的 key 过期了
            if not user or not user.passport_id:
                return self.send_fail("请刷新页面后重试")

            success, errmsg = AuthFunc.update_passportinfo(user.passport_id, "wx_unionid", wx_unionid)
            if not success:
                if errmsg == "NOT EXIST":
                    return self.send_fail("账户不存在，请联系森果客服 400-027-0135")
                elif errmsg == "SAME VALUE":
                    # 重复绑定是为了取微信信息
                    pass
                elif errmsg == "ALREADY BIND":
                    return self.send_fail("该微信已被其他账户绑定")
                else:
                    return self.send_fail("绑定失败，请联系森果客服 400-027-0135")

            redis.delete(bind_key)
        else:
            return self.send_fail("scene_id 无效")

        pf_redis.delete('pf_scene_openid:%s' % scene_id)
        redis.delete("ph_scene_bind_account:%s" % scene_id)

        # 更新微信信息
        AuthFunc.update_through_wx(self.session, wx_userinfo, user, action="bind")
        return self.send_success(done=True)

    @BaseHandler.check_arguments("phone:str", "code:str")
    def bind_phone(self):
        """绑定手机"""
        code = self.args["code"]
        phone = Emoji.filter_emoji(self.args["phone"].strip())

        if not self.current_user:
            return self.write_error(401)

        if len(phone) != 11:
            return self.send_fail("请填写正确的手机号")

        check_msg_res = check_msg_token(phone, code, use="bind")
        if not options.debug and not check_msg_res:
            return self.send_fail("验证码过期或者不正确")

        # 尝试合并账号
        success, errmsg = AuthFunc.merge_passport(self.session, self.current_user.passport_id, phone)
        if success:
            self.clear_current_user()
            return self.send_success()
        elif errmsg != "USE UPDATE":
            return self.send_fail(errmsg)

        # 尝试使用 UPDATE
        success, errmsg = AuthFunc.update_passportinfo(self.current_user.passport_id, "phone", phone)
        if not success:
            if errmsg == "NOT EXIST":
                return self.send_fail("账户不存在，请联系森果客服 400-027-0135")
            elif errmsg == "SAME VALUE":
                return self.send_fail("无需重复绑定")
            elif errmsg == "ALREADY BIND":
                return self.send_fail("该手机号已绑定，请更换手机号绑定或联系森果客服 400-027-0135")
            else:
                return self.send_fail("绑定失败，请联系森果客服 400-027-0135")

        self.current_user.phone = phone

        # 更新门店联系人 ID
        contacts = self.session.query(models.ShopContact) \
            .filter(models.ShopContact.phone == phone) \
            .all()
        if contacts:
            for contact in contacts:
                contact.account_id = self.current_user.id

        self.session.commit()
        self.clear_current_user()
        return self.send_success()


# 微信登录二维码
class WxTicket(_AccountBaseHandler):
    @BaseHandler.check_arguments("action:str")
    def get(self):
        # 用途
        action = self.args["action"]

        if action == "login":
            ticket_url, scene_id = WxTicketUrl.get_ticket_url(source="login")
        elif action == "bind":
            if not self.current_user:
                return self.write_error(401)
            ticket_url, scene_id = WxTicketUrl.get_ticket_url(source="bind")
            # 使用随机场景值记录用户 ID
            h = "ph_scene_bind_account:%s" % scene_id
            redis.set(h, self.current_user.id, 10 * 60)
        else:
            return self.send_fail("action invalid")

        return self.send_success(ticket_url=ticket_url, scene_id=scene_id)


# 小程序登录
class AppletLogin(_AccountBaseHandler):
    @_AccountBaseHandler.check_arguments("code:str", "userInfo:dict",
                                         "rawData:str", "signature:str", "encryptedData:str",
                                         "iv:str",
                                         "source?:str")
    def post(self):
        """
            前端wx.getUserInfo方法返回的用户信息:
                {
                    user_info:用户信息对象，不包含 openid 等敏感信息
                    rawData:不包括敏感信息的原始数据字符串，用于计算签名
                    signature:使用 sha1( rawData + sessionkey ) 得到字符串，用于校验用户信息
                    encryptedData:包括敏感数据在内的完整用户信息的加密数据(包含unionid)
                    iv:加密算法的初始向量
                }

            source: 登录请求的来源 "purchase"-采购助手 "demand"-订货助手
        """
        if self.current_user:
            return self.send_fail("无需重复登录")

        from handlers.applet import ResolveData
        res_status, res_content = ResolveData().resolve(self.args)
        if not res_status:
            return self.send_fail(res_content)
        user_info = res_content

        success, user_or_msg = AuthFunc.login_by_wx(self.session, user_info)
        if not success:
            return self.send_fail(user_or_msg)
        AuthFunc.update_through_wx(self.session, user_info, user_or_msg, action="bind")

        user = user_or_msg
        self.set_current_user(user)

        # 设置当前中转站
        station = self.session.query(models.TransferStation) \
            .join(models.Staff, models.Staff.station_id == models.TransferStation.id) \
            .filter(models.TransferStation.status == 0,
                    models.Staff.status == 0,
                    models.Staff.account_id == user.id,
                    models.Staff.purchaser_status == 1) \
            .first()
        if station:
            self.set_current_station_cookie(station.id, domain=self._ARG_DEFAULT)

        # #缓存session_key
        # redis_name = "session_key:%s:%d"%(appid,customer_id)
        # redis_session.set(redis_name,session_key,7*24*60*60)
        phone_bind = bool(user.phone)
        return self.send_success(phone_bind=phone_bind)


# 微信授权回调
class WxOAuth(_AccountBaseHandler):
    @BaseHandler.check_arguments("code:str", "state?:str")
    def post(self):
        code = self.args["code"]

        wx_userinfo = WxOauth2.get_userinfo(code, mode="")
        if not wx_userinfo:
            return self.send_error(401)

        success, user_or_msg = AuthFunc.login_by_wx(self.session, wx_userinfo)
        if not success:
            return self.send_error(403, error_msg=user_or_msg)
        user = user_or_msg

        self.set_current_user(user_or_msg)

        # 更新微信信息
        AuthFunc.update_through_wx(self.session, wx_userinfo, user, action="bind")
        # 手机绑定状态
        phone_bind = bool(user.phone)
        return self.send_success(phone_bind=phone_bind)
