# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../")))

from celery import Celery
from celery.schedules import crontab

from settings import CELERY_BROKER
import celerywork.platform_statistic as platform_statistic


AutoWork = Celery('ph_cron_work', broker=CELERY_BROKER, backend='')
AutoWork.conf.CELERY_TIMEZONE = 'Asia/Shanghai'         # 时区
AutoWork.conf.CELERYD_CONCURRENCY = 1                   # 任务并发数
AutoWork.conf.CELERYD_TASK_SOFT_TIME_LIMIT = 300        # 任务超时时间
AutoWork.conf.CELERY_DISABLE_RATE_LIMITS = True         # 任务频率限制开关

AutoWork.conf.CELERYBEAT_SCHEDULE = {
    'run_platform_statistic': {
        'task': 'run_platform_statistic',
        'schedule': crontab(hour=0, minute=0),
        # 'schedule': crontab(hour="*", minute="*"),
        'options': {
            'queue': 'ph_cron_work'
        }
    },
    'run_platform_statistic_weekly': {
        'task': 'run_platform_statistic_weekly',
        # 先让当天的日统计跑完
        'schedule': crontab(day_of_week="monday", hour=0, minute=5),
        # 'schedule': crontab(hour="*", minute="*"),
        'options': {
            'queue': 'ph_cron_work'
        }
    },
    'run_platform_statistic_monthly': {
        'task': 'run_platform_statistic_monthly',
        # 先让当天的日统计跑完
        'schedule': crontab(day_of_month='1', hour=0, minute=5),
        # 'schedule': crontab(hour="*", minute="*"),
        'options': {
            'queue': 'ph_cron_work'
        }
    },
}


# 平台统计数据 - 用户店铺类型、日总计、日增量
@AutoWork.task(bind=True, name="run_platform_statistic")
def run_platform_statistic(self):
    platform_statistic.query_user_identity.delay()
    platform_statistic.run_platform_total.apply_async(countdown=60)
    platform_statistic.run_platform_increment.apply_async(countdown=120)

# 平台统计数据 - 周增量
@AutoWork.task(bind=True, name="run_platform_statistic_weekly")
def run_platform_statistic_weekly(self):
    platform_statistic.run_platform_increment_week.delay()

# 平台统计数据 - 月增量
@AutoWork.task(bind=True, name="run_platform_statistic_monthly")
def run_platform_statistic_monthly(self):
    platform_statistic.run_platform_increment_month.delay()
