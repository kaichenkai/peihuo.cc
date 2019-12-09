#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from dal.db_configs import DBSession
from dal import models
from celery import Celery
from settings import CELERY_BROKER
from handlers.base.pub_func import check_int

AsyncWork = Celery('ph_async_work', broker=CELERY_BROKER, backend='')
AsyncWork.conf.CELERY_TIMEZONE = 'Asia/Shanghai'           # 时区
AsyncWork.conf.CELERYD_CONCURRENCY = 1                     # 任务并发数
AsyncWork.conf.CELERYD_TASK_SOFT_TIME_LIMIT = 300          # 任务超时时间
AsyncWork.conf.CELERY_DISABLE_RATE_LIMITS = True           # 任务频率限制开关
AsyncWork.conf.CELERY_ROUTES = {                           # 任务调度队列
    "firm_log": {"queue": "ph_log_work_queue"},
    "staff_log": {"queue": "ph_log_work_queue"},
    "purchasing_dynamics": {"queue": "ph_log_work_queue"}
}


@AsyncWork.task(bind=True, name="firm_log")
def firm_log(self, operator_id, station_id, type, firm_name, modify_content=None):
    """
    为供货商模块的数据操作记录日志
    :param self: 任务本身
    :param operator_id: 操作人id
    :param station_id: 中转站id
    :param type: 操作类型，1：添加，2.删除，3.编辑
    :param firm_name: 操作对象名称
    :param modify_content: 编辑内容
    :return:
    """

    session = DBSession()

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
    session.add(log)
    session.commit()
    session.close()
    return "success"


@AsyncWork.task(bind=True, name="staff_log")
def staff_log(self, operator_id, station_id, type, staff_name, modify_content=None):
    """
    为员工模块的数据操作记录日志
    :param self: 任务本身
    :param operator_id: 操作人id
    :param station_id: 中转站id
    :param type: 操作类型，1：添加，2.删除，3.编辑
    :param staff_name: 操作对象名称
    :param modify_content: 编辑内容
    :return:
    """

    session = DBSession()
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
    session.add(log)
    session.commit()
    session.close()
    return "success"


@AsyncWork.task(bind=True, name="purchasing_dynamics")
def purchasing_dynamics(self, record_type, purchase_goods_dict):
    """
    给采购小程序记录采购动态
    """

    record_type = record_type  # 记录类型
    goods_id = purchase_goods_dict["goods_id"]  # 商品 ID
    purchaser_id = purchase_goods_dict["purchaser_id"]  # 采购员 ID，不安排采购时为空
    creator_id = purchase_goods_dict["creator_id"]  # 操作用户 ID

    goods_name = purchase_goods_dict["goods_name"]  # 商品名称
    last_goods_name = purchase_goods_dict["last_goods_name"]  # 上次的商品名称
    last_goods_name = last_goods_name if last_goods_name else goods_name

    actual_amount = check_int(purchase_goods_dict["actual_amount"] * 100)  # 实际采购件数
    last_actual_amount = purchase_goods_dict["last_actual_amount"]  # 上次的采购件数
    last_actual_amount = last_actual_amount if last_actual_amount else actual_amount

    actual_weight = check_int(purchase_goods_dict["actual_weight"] * 100)  # 实际采购重量
    last_actual_weight = purchase_goods_dict["last_actual_weight"]  # 上次的采购重量
    last_actual_weight = last_actual_weight if last_actual_weight else actual_weight

    actual_unit = purchase_goods_dict["actual_unit"]  # 实际采购单位 0: 件  1: 斤

    price = check_int(purchase_goods_dict["price"] * 100)  # 采购单价
    last_price = purchase_goods_dict["last_price"]  # 上次的采购单价
    last_price = last_price if last_price else price

    subtotal = check_int(purchase_goods_dict["subtotal"] * 100)  # 小计
    last_subtotal = purchase_goods_dict["last_subtotal"]  # 上次的采购小计
    last_subtotal = last_subtotal if last_subtotal else subtotal

    firm_id = purchase_goods_dict["firm_id"]  # 供货商id
    last_firm_id = purchase_goods_dict["last_firm_id"]  # 上次的供货商id
    last_firm_id = last_firm_id if last_firm_id else firm_id

    payment = purchase_goods_dict["payment"]  # 支付方式 0: 现金 1: 银行卡 2: 微信 3: 支付宝 4: 赊账 5: 其他
    is_purchase = purchase_goods_dict["is_purchase"]  # 0: 正常 1: 不采了
    tag = purchase_goods_dict["tag"]  # 商品标签 0: 正常 1：采购员手动添加
    remarks = purchase_goods_dict["remarks"]  # 采购备注
    purchase_order_goods_id = purchase_goods_dict["id"]  # 采购单商品 ID
    purchase_order_id = purchase_goods_dict["purchase_order_id"]  # 采购单 ID
    wish_order_goods_id = purchase_goods_dict["wish_order_goods_id"]  # 意向单商品 ID, 手动添加的采购商品，没有对应的意向单id

    session = DBSession()
    new_dynamic = models.PurchasingDynamics(
        record_type=record_type,
        goods_id=goods_id,
        purchaser_id=purchaser_id,
        creator_id=creator_id,
        goods_name=goods_name,
        last_goods_name=last_goods_name,
        actual_amount=actual_amount,
        last_actual_amount=last_actual_amount,
        actual_weight=actual_weight,
        last_actual_weight=last_actual_weight,
        actual_unit=actual_unit,
        price=price,
        last_price=last_price,
        subtotal=subtotal,
        last_subtotal=last_subtotal,
        firm_id=firm_id,
        last_firm_id=last_firm_id,
        payment=payment,
        is_purchase=is_purchase,
        tag=tag,
        remarks=remarks,
        purchase_order_goods_id=purchase_order_goods_id,
        purchase_order_id=purchase_order_id,
        wish_order_goods_id=wish_order_goods_id
    )
    session.add(new_dynamic)
    session.commit()
    session.close()
    return "success"
