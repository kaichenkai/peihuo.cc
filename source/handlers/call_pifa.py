#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调用批发系统数据。
"""

import requests

from handlers.base.pub_func import TimeFunc
from libs.senguo_encrypt import PfSimpleEncrypt
from settings import PF_ROOT_HOST_NAME


class GetPifaData:
    def __init__(self, passport_id, auth_token):
        self.encrypted_passport_id = PfSimpleEncrypt.encrypt(passport_id)
        self.auth_token = auth_token

    def get_sales_record(self, order_id):
        """ 根据小票单号查询批发系统的销售记录 """
        order_id = PfSimpleEncrypt.encrypt(order_id)
        url = "{}/oauth/peihuo/salesrecord/{}".format(PF_ROOT_HOST_NAME, order_id)

        parameters = {
            'passport_id': self.encrypted_passport_id,
            'auth_token': self.auth_token
        }

        result = requests.get(url, json=parameters, verify=False)

        ret_dict = {}
        err_dict = {"result_status": "Failed", "msg": "批发系统接口异常"}
        res_dict = result.json() if result else err_dict

        ret_dict["result_status"] = res_dict.get('result_status', '')
        ret_dict["msg"] = res_dict.get('msg', '')

        if ret_dict["result_status"] == "Success":
            ret_dict["records"] = res_dict.get("records", {})
            ret_dict["multi"] = res_dict.get("multi", False)

        return ret_dict

    def get_pf_shops(self, phone):
        """ 获取可以在线订货的批发店铺 """
        url = "{}/oauth/caigou/shop".format(PF_ROOT_HOST_NAME)

        phone = PfSimpleEncrypt.encrypt(phone)
        parameters = {
            'passport_id': self.encrypted_passport_id,
            'auth_token': self.auth_token,
            'phone': phone,
        }

        result = requests.get(url, params=parameters, verify=False)

        ret_dict = {}
        err_dict = {"success": False, "msg": "批发系统接口异常"}
        res_dict = result.json() if result else err_dict

        ret_dict["success"] = res_dict.get('success', False)
        ret_dict["msg"] = res_dict.get('msg', '')
        ret_dict["data_list"] = []

        if ret_dict["success"]:
            ret_dict["data_list"] = res_dict.get("data_list", [])

        return ret_dict

    def send_pf_demand_order(self, phone, shop_id, order_id, demand_date, demand_list):
        """ 向批发系统发起订货请求 """
        shop_id = PfSimpleEncrypt.encrypt(shop_id)
        url = "{}/oauth/caigou/demand/{}".format(PF_ROOT_HOST_NAME, shop_id)

        phone = PfSimpleEncrypt.encrypt(phone)
        parameters = {
            'passport_id': self.encrypted_passport_id,
            'auth_token': self.auth_token,
            'phone': phone,
            'external_demand_id': order_id,
            'expect_receive_date': TimeFunc.time_to_str(demand_date, "date"),
            'demand_list': demand_list,
        }

        result = requests.post(url, json=parameters, verify=False)

        ret_dict = {}
        err_dict = {"success": False, "msg": "批发系统接口异常"}
        res_dict = result.json() if result else err_dict

        ret_dict["success"] = res_dict.get('success', False)
        ret_dict["msg"] = res_dict.get('msg', '')

        return ret_dict

    def get_pf_demand_order(self, phone, shop_id, order_id):
        """ 批发订货单详情 """
        shop_id = PfSimpleEncrypt.encrypt(shop_id)
        url = "{}/oauth/caigou/demand/{}".format(PF_ROOT_HOST_NAME, shop_id)

        phone = PfSimpleEncrypt.encrypt(phone)
        parameters = {
            'passport_id': self.encrypted_passport_id,
            'auth_token': self.auth_token,
            'phone': phone,
            'external_demand_id': order_id,
        }

        result = requests.get(url, params=parameters, verify=False)

        ret_dict = {}
        err_dict = {"success": False, "msg": "批发系统接口异常"}
        res_dict = result.json() if result else err_dict

        ret_dict["success"] = res_dict.get('success', False)
        ret_dict["msg"] = res_dict.get('msg', '')
        ret_dict["data"] = {}

        if ret_dict["success"]:
            ret_dict["data"] = res_dict.get("data", {})

        return ret_dict

    def confirm_pf_demand_order(self, phone, shop_id, order_id):
        """ 确认收货 """
        shop_id = PfSimpleEncrypt.encrypt(shop_id)
        url = "{}/oauth/caigou/demand/{}".format(PF_ROOT_HOST_NAME, shop_id)

        phone = PfSimpleEncrypt.encrypt(phone)
        parameters = {
            'passport_id': self.encrypted_passport_id,
            'auth_token': self.auth_token,
            'phone': phone,
            'external_demand_id': order_id,
        }

        result = requests.put(url, json=parameters, verify=False)

        ret_dict = {}
        err_dict = {"success": False, "msg": "批发系统接口异常"}
        res_dict = result.json() if result else err_dict

        ret_dict["success"] = res_dict.get('success', False)
        ret_dict["msg"] = res_dict.get('msg', '')

        return ret_dict
