#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from sqlalchemy import func
from handlers.base.pub_func import check_int, check_float
from handlers.base.pub_web import StationBaseHandler
from handlers.base.pub_web import BaseHandler
from dal import models
from collections import defaultdict


# 报价单
class QuotationOrder(StationBaseHandler):
    @BaseHandler.check_arguments("action:str")
    def get(self, order_id):
        station = self.current_station
        action = self.args.get("action", "").strip()
        wish_order = models.WishOrder.get_by_id(self.session, order_id,
                                                station_id=station.id)
        if not wish_order:
            return self.send_fail("报价单不存在")
        if action == "get_purchase_quotation":
            return self.get_purchase_quotation(station, wish_order)
        elif action == "get_goods_quotation":
            return self.get_goods_quotation(order_id)
        else:
            return self.send_fail("不支持的操作类型")

    # 采购报价单
    def get_purchase_quotation(self, station, wish_order):
        goods_objects = self.session.query(models.WishOrderGoods)\
                                    .filter(models.WishOrderGoods.wish_order_id == wish_order.id,
                                            models.WishOrderGoods.status != -1)\
                                    .order_by(models.WishOrderGoods.create_time.desc())\
                                    .all()
        # 昨日意向单
        yesterday_date = wish_order.wish_date - timedelta(days=1)
        yesterday_wish_order = self.session.query(models.WishOrder)\
                                           .filter(models.WishOrder.wish_date == yesterday_date,
                                                   models.WishOrder.station_id == station.id)\
                                           .first()
        # 获取昨日商品报价,可能没有昨日报价
        yesterday_goods_dict = dict()
        if yesterday_wish_order:
            yesterday_goods_objects = self.session.query(models.WishOrderGoods)\
                                                  .filter(models.WishOrderGoods.wish_order_id == yesterday_wish_order.id,
                                                          models.WishOrderGoods.status != -1)\
                                                  .all()
            yesterday_goods_dict = {yesterday_goods.goods_id: yesterday_goods.today_price for yesterday_goods in yesterday_goods_objects}
        # 采购均价
        purchase_goods_info = self.session.query(models.PurchaseOrderGoods.goods_id,
                                                 func.sum(models.PurchaseOrderGoods.subtotal),
                                                 func.sum(models.PurchaseOrderGoods.actual_amount))\
                                          .join(models.PurchaseOrder, models.PurchaseOrder.id == models.PurchaseOrderGoods.purchase_order_id)\
                                          .filter(models.PurchaseOrder.wish_order_id == wish_order.id,
                                                  models.PurchaseOrder.status == 0,
                                                  models.PurchaseOrderGoods.status >= 0)\
                                          .group_by(models.PurchaseOrderGoods.goods_id)\
                                          .all()
        # 按斤/件进行处理
        # purchase_goods_dict = defaultdict(list)
        # for purchase_goods in purchase_goods_info:
        #     goods_id = purchase_goods[0]
        #     if purchase_goods[4] == 0:  # (件)
        #         purchase_goods_dict["amount_{}".format(goods_id)].append(check_int(purchase_goods[3] / 100))
        #     if purchase_goods[4] == 1:  # (斤)
        #         purchase_goods_dict["weight_{}".format(goods_id)].append(check_int(purchase_goods[3] / 100))
        # # 采购均价(件)
        # amount_dict = {goods_id: sum(price) / len(price) for goods_id, price in purchase_goods_dict.items()}
        # # 采购均价(斤)
        # weight_dict = {goods_id: sum(price) / len(price) for goods_id, price in purchase_goods_dict.items()}
        purchase_goods_dict = defaultdict()
        for goods_id, subtotal, actual_amount in purchase_goods_info:
            purchase_goods_dict[goods_id] = subtotal / actual_amount if actual_amount > 0 else 0

        # 排序调整，已配货的商品显示在前边
        allocation_order_goods_ids = self.session.query(models.AllocationOrder.goods_id)\
                                                 .filter(models.AllocationOrder.wish_order_id == wish_order.id,
                                                         models.AllocationOrder.station_id == self.current_station.id,
                                                         models.AllocationOrder.status == 1)\
                                                 .distinct()\
                                                 .all()
        goods_id_set = {goods_id[0] for goods_id in allocation_order_goods_ids}

        wish_goods_list = list()
        for wish_goods in goods_objects:
            data = wish_goods.to_dict()
            # 昨日报价
            yesterday_price = yesterday_goods_dict.get(wish_goods.goods_id, 0)
            data["yesterday_price"] = check_float(yesterday_price / 100)
            # 采购均价
            purchase_price = purchase_goods_dict.get(wish_goods.goods_id, 0)
            data["purchase_price"] = check_float(purchase_price)
            wish_goods_list.append(data)
            # 添加排序键值对
            data["priority"] = wish_goods.goods_id
            is_allocation = wish_goods.goods_id in goods_id_set
            if is_allocation:
                data["priority"] -= 9999
        # 调整排序
        wish_goods_list = sorted(wish_goods_list, key=lambda x: x["priority"])

        # 报价单状态
        status = wish_order.quotation_status
        return self.send_success(wish_goods_list=wish_goods_list, status=status)

    # 商品报价单
    def get_goods_quotation(self, order_id):
        goods_objects = self.session.query(models.WishOrderGoods)\
                                         .filter(models.WishOrderGoods.wish_order_id == order_id,
                                                 models.WishOrderGoods.status != -1)\
                                         .order_by(models.WishOrderGoods.create_time.desc())\
                                         .all()
        goods_list = list()
        for wish_goods in goods_objects:
            data = wish_goods.to_dict()
            goods_list.append(data)
        return self.send_success(goods_list=goods_list)

    @BaseHandler.check_arguments("action:str")
    def put(self, order_id):
        station = self.current_station
        action = self.args.get("action")
        wish_order = models.WishOrder.get_by_id(self.session, order_id,
                                                station_id=station.id)
        if not wish_order:
            return self.send_fail("报价单不存在")
        if wish_order.quotation_status == 2:
            return self.send_fail("报价单已制作完成")
        if action == "save_draft":
            return self.save_draft(order_id)
        elif action == "completed":
            if wish_order.status not in [3, 4]:
                return self.send_fail("订货单尚未汇总")
            # 报价单制作完成
            wish_order.quotation_status = 2
            return self.save_draft(order_id)
        else:
            return self.send_fail("不支持的操作类型")

    @BaseHandler.check_arguments("goods_today_price:dict")
    def save_draft(self, order_id):
        goods_today_price = self.args.get("goods_today_price")
        valid, message, goods_today_price = self.validate_goods_today_price(goods_today_price)
        if not valid:
            return self.send_fail(message)
        goods_ids = goods_today_price.keys()
        wish_goods_objects = self.session.query(models.WishOrderGoods) \
                                         .filter(models.WishOrderGoods.wish_order_id == order_id,
                                                 models.WishOrderGoods.id.in_(goods_ids),
                                                 models.WishOrderGoods.status != -1) \
                                         .all()
        for wish_goods in wish_goods_objects:
            wish_goods.today_price = check_float(goods_today_price.get(wish_goods.id, 0) * 100)
        self.session.commit()
        return self.send_success()

    def validate_goods_today_price(self, goods_today_price):
        """验证商品今日报价字典"""
        if not isinstance(goods_today_price, dict):
            return False, "商品报价字典参数格式有误", ""
        for goods_id, price in goods_today_price.items():
            try:
                int(goods_id)
                int(price)
            except:
                return False, "商品报价参数无效", ""
        # 将json数据中的key转换为int类型
        goods_today_price = {check_int(key): value for key, value in goods_today_price.items()}
        return True, "", goods_today_price
