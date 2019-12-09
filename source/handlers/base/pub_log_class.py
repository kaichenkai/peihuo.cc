#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dal import models
from handlers.base.pub_web import GlobalBaseHandler


# 日志
# 此日志已在异步任务中处理
class OperationLog(GlobalBaseHandler):
    def __init__(self):
        pass

    def firm_log(self, operator_id, station_id, type, firm_name, modify_content=None):
        if type == 1:
            detail = "添加供货商({0})".format(firm_name)
        elif type == 2:
            detail = "删除供货商({0})".format(firm_name)
        elif type == 3:
            detail = "{0}".format(modify_content)
        else:
            return "参数有误"
        log = models.OperationLog(
            log_type=2,  # 1：员工 2：供货商
            operation_object=firm_name,
            detail=detail,
            creator_id=operator_id,  # 创建人 ID
            station_id=station_id  # 中转站 ID
        )
        self.session.add(log)
        self.session.commit()
        return "success"

    def staff_log(self, operator_id, station_id, type, staff_name, modify_content=None):
        if type == 1:
            detail = "添加员工({0})".format(staff_name)
        elif type == 2:
            detail = "删除员工({0})".format(staff_name)
        elif type == 3:
            detail = "{0}".format(modify_content)
        else:
            return "参数有误"
        log = models.OperationLog(
            log_type=1,  # 1：员工 2：供货商
            operation_object=staff_name,
            detail=detail,
            creator_id=operator_id,  # 创建人 ID
            station_id=station_id  # 中转站 ID
        )
        self.session.add(log)
        self.session.commit()
        return "success"
