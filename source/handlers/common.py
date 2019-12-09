#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
common类的接口除LoginVerifyCode外，都需要登录后才能调用。
"""
import json

import tornado.web
from tornado.options import options

import dal.models as models
from dal.db_configs import redis
from handlers.base.pub_web import _AccountBaseHandler
from handlers.base.webbase import BaseHandler
from libs.msgverify import gen_msg_token


class LoginVerifyCode(_AccountBaseHandler):
    """未登录用户获取短信验证码，用于注册或登录"""
    @BaseHandler.check_arguments("action:str", "phone:str")
    def get(self):
        action = self.args["action"]
        phone = self.args["phone"]
        if len(phone) != 11:
            return self.send_fail("请填写正确的手机号")
        if action not in models.VerifyCodeUse.login_verify_code_use:
            return self.send_fail("invalid action")
        # 发送验证码
        result, code = gen_msg_token(phone, action)
        if result is True:
            if options.debug:
                return self.send_success(code=code)
            else:
                return self.send_success()
        else:
            return self.send_fail(result)


# APP 最新版本信息
class LastestVersion(tornado.web.RequestHandler):
    """
    返回格式：
    {
        "Android": {
            "verCode": "1803221906",
            "verDate": "2018-03-22",
            "log": "VIP购买，推荐邀请，修复已知bug",
            "url": "http://d.senguo.cc/android/SenguoPurchaser-V1.0.3-1803221906-release.apk",
            "verName": "1.0.3",
            "level": 0
        }
    }

    字段描述：
    verCode: 应用版本代码
    verName: 应用版本号
    verDate: 版本发布日期
    log: 更新内容描述
    url: APK 下载地址
    level: 版本等级 0-正常，等待用户自己更新 1-重要版本，在应用启动时提示更新，用户可以选择忽略当前版本 2-重大版本，不更新则不能使用应用
    """
    def post(self):
        try:
            data = json.loads(redis.get("cgapp_update_info").decode())
        except ValueError as e:
            data = {}
        return self.write(data)


# 利楚地区
class BankAreaList(_AccountBaseHandler):
    @BaseHandler.check_arguments("query_type:str", "parent_code?:int")
    def get(self):
        query_type = self.args["query_type"]
        parent_code = self.args.get("parent_code", 0)
        if query_type == "provinces":
            provinces = self.session.query(models.LcAreaCode.province_code,
                                           models.LcAreaCode.province_text) \
                .distinct().all()
            return self.send_success(data=[{
                "province_code": province.province_code,
                "province_text": province.province_text,
            } for province in provinces])
        elif query_type == "cities":
            cities = self.session.query(models.LcAreaCode.city_code,
                                        models.LcAreaCode.city_text) \
                .filter(models.LcAreaCode.province_code == parent_code) \
                .distinct().all()
            return self.send_success(data=[{
                "city_code": city.city_code,
                "city_text": city.city_text,
            } for city in cities])
        else:
            return self.send_fail("query_type invalid")


# 利楚银行列表
class BankList(_AccountBaseHandler):
    def get(self):
        banks = self.session.query(models.LcParentBank).all()
        return self.send_success(banks=[{
            "no": bank.parent_bank_no,
            "name": bank.parent_bank_name,
        } for bank in banks])


# 利楚银行支行列表
class BranchBankList(_AccountBaseHandler):
    @BaseHandler.check_arguments("city_code:str", "bank_no:int")
    def get(self):
        city_code = self.args["city_code"]
        bank_no = self.args["bank_no"]
        branch_banks = self.session.query(models.LcBank) \
            .filter(models.LcBank.city_code == city_code,
                    models.LcBank.parent_bank_no == bank_no) \
            .all()
        return self.send_success(banks=[{
            "id": bank.id,
            "city_code": bank.city_code,
            "parent_bank_no": bank.parent_bank_no,
            "bank_no": bank.bank_no,
            "bank_name": bank.bank_name,
        } for bank in branch_banks])
