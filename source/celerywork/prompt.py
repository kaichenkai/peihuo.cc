#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os,sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

import datetime
import json

from celery import Celery
import requests

from settings import CELERY_BROKER, DINGTALK_WEBHOOK
from dal.db_configs import DBSession
from libs import yunpian


PromptWork = Celery('cg_prompt', broker=CELERY_BROKER, backend='')
PromptWork.conf.CELERY_TIMEZONE = 'Asia/Shanghai'           # 时区
PromptWork.conf.CELERYD_CONCURRENCY = 1                     # 任务并发数
PromptWork.conf.CELERYD_TASK_SOFT_TIME_LIMIT = 300          # 任务超时时间
PromptWork.conf.CELERY_DISABLE_RATE_LIMITS = True           # 任务频率限制开关
PromptWork.conf.CELERY_ROUTES = {                           # 任务调度队列
    "send_dingtalk_msg": {"queue": "cg_prompt_queue"},
    "send_frozen_account_dingtalk_msg": {"queue": "cg_prompt_queue"},
    "send_frozen_account_known_notify": {"queue": "cg_prompt_queue"},
    "send_frozen_account_done_notify": {"queue": "cg_prompt_queue"},
}


@PromptWork.task(bind=True, name="send_dingtalk_msg")
def send_dingtalk_msg(self, data):
    """发送钉钉通知"""
    try:
        resp= requests.post(DINGTALK_WEBHOOK, json=data).json()
        if resp["errcode"] != 0:
            print("Send dingtalk message failed, {}".format(resp["errmsg"]))
        else:
            print("Send dingtalk message success.")
    except Exception as e:
        print("Send dingtalk message error, {}".format(e))
        raise self.retry(exc=e)

@PromptWork.task(bind=True, name="send_frozen_account_dingtalk_msg")
def send_frozen_account_dingtalk_msg(self, phone):
    title = "被冻结账户注册通知"
    msg = "> 手机号码：" + phone
    now = datetime.datetime.now().strftime("%c")
    text = "\n\n".join(["#### {}".format(title), msg, "###### {}".format(now)])
    data = {
        "msgtype": "markdown",
        "markdown": {"title": title, "text": text},
        "at": {'atMobiles': [], 'isAtAll': False},
    }
    send_dingtalk_msg.delay(data)

@PromptWork.task(bind=True, name="send_frozen_account_known_notify")
def send_frozen_account_known_notify(self, phone):
    status = yunpian.send_frozen_account_known_notify(phone)
    print(status)

@PromptWork.task(bind=True, name="send_frozen_account_done_notify")
def send_frozen_account_done_notify(self, phone):
    status = yunpian.send_frozen_account_done_notify(phone)
    print(status)
