#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import json
import traceback

import requests
from dal.db_configs import redis
from handlers.base.pub_func import UrlShorten
from handlers.base.pub_web import GlobalBaseHandler
from settings import DINGTALK_WEBHOOK


# 服务器出现 500 错误时发送告警
class ServerAlarm:
    @staticmethod
    def send_server_error(request_uri, **kwargs):
        # 获取错误消息
        server_error_messsage = traceback.format_exception(*kwargs["exc_info"])
        error_type = server_error_messsage[-1].strip()
        server_error_messsage = json.dumps(server_error_messsage)

        # 存入 Redis
        error_key = UrlShorten.get_hex(server_error_messsage)
        server_error = "Ph_Server_Error:%s" % error_key
        server_error_times = "Ph_Server_Error_Times:%s" % error_key

        # 报错已存在，增加报错计数
        if redis.exists(server_error):
            redis.incr(server_error_times)
        else:
            redis.set(server_error, server_error_messsage, 72 * 60 * 60)
            redis.set(server_error_times, 1, 72 * 60 * 60)

            try:
                ServerAlarm.send_dingtalk_msg(
                    request_uri,
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    error_key,
                    error_type,
                )
            except:
                pass

    @staticmethod
    def send_dingtalk_msg(request_uri, happen_time, error_key, error_type):
        detail_url = "https://ph.senguo.cc/api/servererror/{}?verify=senguoph".format(error_key)
        data = {
            "actionCard": {
                "title": "森果配货 500 错误",
                "text": "出错地址：{request_uri}\n\n"
                        "出错时间：{happen_time}\n\n"
                        "错误类型：{error_type}\n\n"
                        "[>>>查看详情]({detail_url})\n\n".format(**locals()),
                "hideAvatar": "0",
                "btnOrientation": "0",
                "btns": [],
            },
            "msgtype": "actionCard",
        }
        try:
            resp = requests.post(DINGTALK_WEBHOOK, json=data, timeout=2).json()
            if resp["errcode"] != 0:
                print("Send server error failed, {}".format(resp["errmsg"]))
        except Exception as e:
            print("Send server error failed, {}".format(e))
        print("Send server error successfully.")


# 服务器错误详情
class ServerErrorDetail(GlobalBaseHandler):
    @GlobalBaseHandler.check_arguments("verify?:str")
    def get(self, error_key):
        if self.args.get("verify") != "senguoph":
            return self.write("<h1>HTTP 403</h1>")

        # 错误信息
        server_error = "Ph_Server_Error:%s" % error_key
        if redis.exists(server_error):
            try:
                error_msg = json.loads(redis.get(server_error).decode("utf-8"))
            except:
                error_msg = redis.get(redis.get(server_error))
        else:
            error_msg = '错误信息已失效'

        # 剩余时间
        try:
            time_left = int(redis.ttl(server_error) / (60 * 60))
        except:
            time_left = 0

        # 出错次数
        server_error_times = "Ph_Server_Error_Times:%s" % error_key
        try:
            times = redis.get(server_error_times) or 1
        except:
            times = 1

        # 封面
        error_cover_img = redis.get("Ph_Server_Error_Cover")
        if not error_cover_img:
            error_cover_img = "https://picsum.photos/500/300/?random"

        return self.render("server_error.html", error_msg=error_msg,
                           time_left=time_left, times=times, error_cover_img=error_cover_img)
