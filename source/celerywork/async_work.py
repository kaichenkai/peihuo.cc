#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from dal.db_configs import DBSession, statistic_DBSession

import datetime

from celery import Celery

from handlers.base import pub_statistic
from settings import CELERY_BROKER

AsyncWork = Celery('ph_async_work', broker=CELERY_BROKER, backend='')
AsyncWork.conf.CELERY_TIMEZONE = 'Asia/Shanghai'           # 时区
AsyncWork.conf.CELERYD_CONCURRENCY = 1                     # 任务并发数
AsyncWork.conf.CELERYD_TASK_SOFT_TIME_LIMIT = 300          # 任务超时时间
AsyncWork.conf.CELERY_DISABLE_RATE_LIMITS = True           # 任务频率限制开关
AsyncWork.conf.CELERY_ROUTES = {                           # 任务调度队列
    "run_statistics": {"queue": "ph_async_work_queue"},
}


@AsyncWork.task(bind=True, name="run_statistics")
def run_statistics(self, user_id, shop_id, chain_shop_id, for_dates):
    """
    为指定日期运行采购统计

    :param for_dates iterable %Y-%m-%d s
    """

    session = DBSession()
    statistic_session = statistic_DBSession()

    for date in for_dates:
        try:
            date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("invalid date format: {}".format(date))

        date_delta = (datetime.date.today() - date).days
        pub_statistic.purchase_order_goods_firm(session, statistic_session,
                                                user_id, shop_id, chain_shop_id,
                                                date_delta)

    session.close()
    statistic_session.close()
