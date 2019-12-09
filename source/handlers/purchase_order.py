#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
from datetime import timedelta
from handlers.call_pifa import GetPifaData
from handlers.base.pub_func import TimeFunc, check_float, check_int, is_int, is_number, AuthFunc
from handlers.base.pub_web import PurchaseBaseHandler
from handlers.base.pub_web import BaseHandler
from handlers.summary import PurchasingDynamicsMixin
from dal import constants, models
from sqlalchemy import func, or_


# 扫码录入采购数据
class ScanCodeEntry(PurchaseBaseHandler):
    @BaseHandler.check_arguments("action:str")
    def get(self):
        action = self.args["action"]
        if action == "single_entry":
            # 单品扫码录入(获取批发的采购数据)
            return self.single_enter()
        elif action == "multi_entry":
            # 多品扫码录入
            return self.multi_entry()
        else:
            return self.send_fail("不支持的操作类型")

    @BaseHandler.check_arguments("receipt_id:int")
    def single_enter(self):
        receipt_id = self.args["receipt_id"]
        token = AuthFunc.gen_token()
        ret_dict = GetPifaData(self.current_user.passport_id, token).get_sales_record(receipt_id)
        if ret_dict["result_status"] != "Success":
            return self.send_fail(ret_dict.get("msg", ""))

        sales_records = ret_dict["records"]
        multi = ret_dict["multi"]
        if multi:
            return self.send_fail("单据中包含多条采购数据，请选择「多品扫码」")

        record = sales_records[0]
        record_dict = ScanCodeEntry.to_record_dict(record)

        return self.send_success(record_dict=record_dict)

    @BaseHandler.check_arguments("receipt_id:int")
    def multi_entry(self):
        receipt_id = self.args["receipt_id"]
        token = AuthFunc.gen_token()
        ret_dict = GetPifaData(self.current_user.passport_id, token).get_sales_record(receipt_id)
        if ret_dict["result_status"] != "Success":
            return self.send_fail(ret_dict.get("msg", ""))

        sales_records = ret_dict["records"]
        multi = ret_dict["multi"]
        if not multi:
            return self.send_fail("单据中只包含单条采购数据，请选择商品「扫码录入」")

        record_list = list()
        for record in sales_records:
            record_dict = ScanCodeEntry.to_record_dict(record)
            record_list.append(record_dict)

        return self.send_success(record_list=record_list)

    @staticmethod
    def to_record_dict(record):
        record_dict = {
            "goods_name": record["goods_name"],
            # 默认是现金支付
            "payment": models.PurchaseOrderGoods.pf_payment_map_dict.get(record["payment"], 0),
            "actual_amount": record["amount"],
            "actual_weight": record["weight"],
            "actual_unit": models.PurchaseOrderGoods.pf_unit_map_dict.get(record["unit"], 0),
            "price": check_float(record["price"] / 100),
            "commission": check_float(record["commission"] / 100),
            "deposit": check_float(record["deposit"] / 100),
            "subtotal": check_float(record["subtotal"] / 100),

            "num": record["num"],
            "status": record["status"],
            "bill_time": record["bill_time"],
            "printer_num": record["printer_num"],
            "printer_remark": record["printer_remark"],
            "salesman": record["salesman"],
            "accountant": record["accountant"],
            "order_time": record["order_time"],
        }
        return record_dict


# 采购单商品设置采购员
class SetPurchaser(PurchaseBaseHandler):
    @BaseHandler.check_arguments("wish_order_id?:int", "goods_id:int", "purchaser_id:int")
    def put(self):
        wish_order_id = self.args.get("wish_order_id")
        goods_id = self.args["goods_id"]
        purchaser_id = self.args["purchaser_id"]
        if purchaser_id:
            valid_purchaser = models.Staff.get_by_id(self.session, purchaser_id, station_id=self.current_station.id)
            if not valid_purchaser:
                return self.send_fail("选择了无效的采购员")
            # 存储商品默认的采购员
            staff_goods_list = self.session.query(models.StaffGoods)\
                                           .filter(models.StaffGoods.goods_id == goods_id)\
                                           .all()
            for staff_goods in staff_goods_list:
                self.session.delete(staff_goods)
            new_staff_goods = models.StaffGoods(
                goods_id=goods_id,
                staff_id=purchaser_id
            )
            self.session.add(new_staff_goods)
            # 如果意向单已制作完成
            if wish_order_id:
                wish_order = models.WishOrder.get_by_id(self.session, wish_order_id, self.current_station.id)
                if not wish_order:
                    return self.send_fail("没有找到指定的意向单")
                if wish_order.status <= 1:
                    return self.send_fail("意向单还未提交")
                # 如果意向单已汇总
                if wish_order.status >= 3:
                    # 判断采购员有没有这个采购商品，如果没有，需要添加给该采购员
                    valid_purchase_goods_list = self.session.query(models.PurchaseOrderGoods)\
                        .join(models.PurchaseOrder, models.PurchaseOrder.id == models.PurchaseOrderGoods.purchase_order_id)\
                        .filter(models.PurchaseOrder.wish_order_id == wish_order_id,
                                models.PurchaseOrderGoods.goods_id == goods_id,
                                models.PurchaseOrder.status >= 0,
                                models.PurchaseOrderGoods.status >= 0)\
                        .all()
                    purchaser_ids = {purchase_goods.purchaser_id for purchase_goods in valid_purchase_goods_list}
                    if purchaser_id not in purchaser_ids:
                        # 取一个任意采购商品
                        purchase_goods = valid_purchase_goods_list[0]
                        new_purchase_goods = models.PurchaseOrderGoods(
                            estimated_amount=purchase_goods.estimated_amount,
                            tag=purchase_goods.tag,
                            wish_order_goods_id=purchase_goods.wish_order_goods_id,
                            goods_id=purchase_goods.goods_id,
                            purchaser_id=purchaser_id,
                            purchase_order_id=purchase_goods.purchase_order_id
                        )
                        self.session.add(new_purchase_goods)
        else:
            # 清除商品和采购员的对应关系
            staff_goods_list = self.session.query(models.StaffGoods)\
                                           .filter(models.StaffGoods.goods_id == goods_id)\
                                           .all()
            for staff_goods in staff_goods_list:
                self.session.delete(staff_goods)
        self.session.commit()
        return self.send_success()


# 采购单商品退货
class GoodsReturn(PurchaseBaseHandler):
    @BaseHandler.check_arguments("wish_order_id:int", "goods_id:int")
    def get(self):
        wish_order_id = self.args["wish_order_id"]
        goods_id = self.args["goods_id"]
        wish_order = models.WishOrder.get_by_id(self.session, wish_order_id, self.current_station.id)
        if not wish_order:
            return self.send_fail("没有找到指定的意向单")
        if wish_order.status <= 1:
            return self.send_fail("意向单还未提交")
        purchase_goods_list = self.session.query(models.PurchaseOrderGoods) \
                                          .join(models.PurchaseOrder,
                                                models.PurchaseOrder.id == models.PurchaseOrderGoods.purchase_order_id)\
                                          .filter(models.PurchaseOrder.wish_order_id == wish_order_id,
                                                  models.PurchaseOrderGoods.goods_id == goods_id,
                                                  models.PurchaseOrderGoods.actual_amount > 0,
                                                  models.PurchaseOrder.status >= 0,
                                                  models.PurchaseOrderGoods.status >= 0) \
                                          .all()
        if not purchase_goods_list:
            return self.send_fail("尚未采购该商品")
        goods_list = list()
        for purchase_goods in purchase_goods_list:
            data = {
                "id": purchase_goods.id,
                "goods_id": purchase_goods.goods_id,
                "firm_id": purchase_goods.firm_id,
                "firm_name": purchase_goods.firm.name,
                "actual_amount": check_float(purchase_goods.actual_amount / 100)
            }
            goods_list.append(data)
        return self.send_success(goods_list=goods_list)

    @BaseHandler.check_arguments("wish_order_id:int", "goods_id:int", "firm_id:int")
    def put(self):
        wish_order_id = self.args["wish_order_id"]
        goods_id = self.args["goods_id"]
        firm_id = self.args["firm_id"]
        wish_order = models.WishOrder.get_by_id(self.session, wish_order_id, self.current_station.id)
        if not wish_order:
            return self.send_fail("没有找到指定的意向单")
        if wish_order.status <= 1:
            return self.send_fail("意向单还未提交")
        firm = models.Firm.get_by_firm_id(self.session, firm_id, self.current_station.id)
        if not firm:
            return self.send_fail("无效的供货商")
        purchase_goods = self.session.query(models.PurchaseOrderGoods)\
                                     .join(models.PurchaseOrder,
                                           models.PurchaseOrder.id == models.PurchaseOrderGoods.purchase_order_id)\
                                     .filter(models.PurchaseOrder.wish_order_id == wish_order_id,
                                             models.PurchaseOrderGoods.id == goods_id,
                                             models.PurchaseOrderGoods.firm_id == firm_id,
                                             models.PurchaseOrder.status >= 0,
                                             models.PurchaseOrderGoods.status >= 0) \
                                     .first()
        if not purchase_goods:
            return self.send_fail("提供了无效的采购单商品")
        if purchase_goods.actual_amount == 0:
            return self.send_fail("尚未采购该商品")
        # 已经分车的商品不允许退货
        allocation_order = self.session.query(models.AllocationOrder)\
                                       .filter(models.AllocationOrder.purchase_order_goods_id == purchase_goods.id,
                                               models.AllocationOrder.status == 1)\
                                       .first()
        if allocation_order:
            return self.send_fail("采购单商品已有成功分车的记录，不能退货")
        purchase_goods.status = -2
        self.session.flush()
        # 如果该采购单商品都退货了，需要将采购单商品恢复到采购单中
        valid_purchase_goods = self.session.query(models.PurchaseOrderGoods)\
                                           .join(models.PurchaseOrder,
                                                 models.PurchaseOrder.id == models.PurchaseOrderGoods.purchase_order_id)\
                                           .filter(models.PurchaseOrder.wish_order_id == wish_order_id,
                                                   models.PurchaseOrderGoods.goods_id == purchase_goods.goods_id,
                                                   models.PurchaseOrderGoods.actual_amount > 0,
                                                   models.PurchaseOrder.status >= 0,
                                                   models.PurchaseOrderGoods.status >= 0) \
                                           .first()
        if not valid_purchase_goods:
            # 恢复一个初始的采购单商品
            origin_purchase_goods = models.PurchaseOrderGoods(
                estimated_amount=purchase_goods.estimated_amount,
                tag=purchase_goods.tag,
                goods_id=purchase_goods.goods_id,
                purchaser_id=purchase_goods.purchaser_id,
                purchase_order_id=purchase_goods.purchase_order_id,
                wish_order_goods_id=purchase_goods.wish_order_goods_id
            )
            self.session.add(origin_purchase_goods)
        self.session.commit()
        return self.send_success()


# 采购单列表
class PurchaseOrderList(PurchaseBaseHandler):
    @BaseHandler.check_arguments("page?:int", "limit?:int")
    def get(self):
        page = self.args.get("page", 0)
        limit = self.args.get("limit", constants.PAGE_SIZE)
        if limit > constants.PAGE_MAX_LIMIT:
            limit = constants.PAGE_SIZE
        query_set = self.session.query(models.PurchaseOrder)\
                                .filter(models.PurchaseOrder.station_id == self.current_station.id,
                                        models.PurchaseOrder.status >= 0)

        purchase_order_objects = query_set.order_by(models.PurchaseOrder.status,
                                                    models.PurchaseOrder.create_time.desc())\
                                          .offset(page * limit)\
                                          .limit(limit)\
                                          .all()
        # 采购单数量(使用with_entities()来改变query内容而不需要重写查询条件)
        purchase_order_num = query_set.with_entities(func.count(models.PurchaseOrder.id)).first()

        purchase_order_ids = [purchase_order.id for purchase_order in purchase_order_objects]

        purchase_order_goods_objects = self.session.query(models.PurchaseOrderGoods)\
            .join(models.PurchaseOrder, models.PurchaseOrder.id == models.PurchaseOrderGoods.purchase_order_id)\
            .filter(or_(models.PurchaseOrderGoods.purchaser_id == self.current_staff.id,
                        models.PurchaseOrderGoods.purchaser_id == None),
                    models.PurchaseOrderGoods.purchase_order_id.in_(purchase_order_ids),
                    models.PurchaseOrderGoods.status >= 0)\
            .all()
        purchase_order_goods_dict = defaultdict(list)
        for purchase_goods in purchase_order_goods_objects:
            purchase_order_goods_dict[purchase_goods.purchase_order_id].append(purchase_goods)
        purchase_order_list = list()
        for purchase_order in purchase_order_objects:
            purchase_order_goods_list = purchase_order_goods_dict.get(purchase_order.id, list())
            # 如果该采购员在采购单中没有采购商品，也返回该采购单
            data = purchase_order.to_dict()
            # 货品数
            data["goods_num"] = len({purchase_goods.goods_id for purchase_goods in purchase_order_goods_list})
            # 总件数
            data["total_amount"] = check_float(sum(purchase_goods.actual_amount
                                                   for purchase_goods in purchase_order_goods_list) / 100)
            # 总支出
            data["subtotal"] = check_float(sum(purchase_goods.subtotal
                                               for purchase_goods in purchase_order_goods_list) / 100)
            purchase_order_list.append(data)

        has_more = len(purchase_order_objects) >= limit
        return self.send_success(purchase_order_list=purchase_order_list,
                                 purchase_order_num=purchase_order_num,
                                 has_more=has_more)


# 采购单
class PurchaseOrder(PurchaseBaseHandler):
    @BaseHandler.check_arguments("action:str", "sort_by?:str", "reverse?:int")
    def get(self, order_id):
        action = self.args["action"]
        sort_by = self.args.get("sort_by")
        # 默认升序
        reverse = self.args.get("reverse", 0)
        purchase_order = models.PurchaseOrder.get_by_id(self.session, order_id, status_list=[0, 1])
        if not purchase_order:
            return self.send_fail("采购单不存在")
        if action == "get_purchase_goods_list":
            return self.get_purchase_goods_list(order_id, purchase_order, sort_by, reverse)
        # 获取历史供货商
        elif action == "get_history_firms":
            return self.get_history_firms(order_id)
        else:
            return self.send_fail("不支持的操作类型")

    def get_purchase_goods_list(self, order_id, purchase_order, sort_by, reverse):
        # 取当前采购员和未设置采购员的采购商品
        purchase_goods_list = self.session.query(models.PurchaseOrderGoods)\
                                          .filter(models.PurchaseOrderGoods.purchase_order_id == order_id,
                                                  or_(models.PurchaseOrderGoods.purchaser_id == self.current_staff.id,
                                                      models.PurchaseOrderGoods.purchaser_id == None),
                                                  models.PurchaseOrderGoods.status >= 0)\
                                          .all()
        wish_order_goods_ids = {goods.wish_order_goods_id for goods in purchase_goods_list}
        wish_order_goods_list = self.session.query(models.WishOrderGoods)\
                                            .filter(models.WishOrderGoods.id.in_(wish_order_goods_ids))\
                                            .all()
        wish_order_goods_dict = {goods.id: goods for goods in wish_order_goods_list}
        goods_dict = defaultdict(list)
        for purchase_goods in purchase_goods_list:
            # 商品名称可能会重复，这里用goods_id进行区分
            goods_id = purchase_goods.goods_id
            data = purchase_goods.to_dict()
            # 获取采购商品对应的意向商品
            wish_goods = wish_order_goods_dict.get(purchase_goods.wish_order_goods_id)
            # 采购商品对应的商品规格信息(用于在采购小程序上修改商品规格)
            goods = purchase_goods.goods
            data["length"] = check_float(goods.length / 100)
            data["width"] = check_float(goods.width / 100)
            data["height"] = check_float(goods.height / 100)
            data["standards_volume"] = float(goods.standards_volume)
            data["standards_weight"] = check_float(goods.standards_weight / 100)
            data["goods_name"] = wish_goods.goods_name if wish_goods else goods.name
            data["goods_name_modified"] = wish_goods.goods_name_modified if wish_goods else 0
            data["wish_goods_status"] = wish_goods.status if wish_goods else 0
            # 默认与意向单商品的排序保持一致，手动添加的商品排在前面
            data["priority"] = wish_goods.priority if wish_goods else goods.serial_number - 1000
            # 已录入采购数据的商品，自动弹到下面
            if purchase_goods.actual_amount > 0:
                data["priority"] += 10000
            # 未设置采购员，排到倒数第二
            if purchase_goods.purchaser_id == None:
                data["priority"] += 100000
            # 设置为不采了，直接排到最底下
            if purchase_goods.is_purchase == 1:
                data["priority"] += 1000000
            goods_dict[goods_id].append(data)
        goods_list = list()
        for goods_id, goods_info_list in goods_dict.items():
            data = dict()
            data["goods_info_list"] = goods_info_list
            data["name"] = goods_info_list[0]["goods_name"]
            data["priority"] = 0
            if sort_by == "estimated_amount":
                data["priority"] += goods_info_list[0]["estimated_amount"]
            elif sort_by == "actual_amount":
                data["priority"] += sum(goods_info["actual_amount"] for goods_info in goods_info_list)
            elif sort_by == "price":
                data["priority"] += check_float(sum(goods_info["price"] for goods_info in goods_info_list) / len(goods_info_list))
            else:
                data["priority"] = goods_info_list[0]["priority"]
            goods_list.append(data)
        # 排序
        goods_list = sorted(goods_list, key=lambda x: x["priority"], reverse=bool(reverse))
        # 统计单个订单的总件数和总支出
        amount_data = self.session.query(func.sum(models.PurchaseOrderGoods.actual_amount),
                                         func.sum(models.PurchaseOrderGoods.subtotal))\
                                  .filter(models.PurchaseOrderGoods.purchase_order_id == order_id,
                                          models.PurchaseOrderGoods.purchaser_id == self.current_staff.id,
                                          models.PurchaseOrderGoods.status >= 0)\
                                  .group_by(models.PurchaseOrderGoods.purchase_order_id)\
                                  .first()
        order_actual_amount, order_subtotal = amount_data if amount_data else (0, 0)
        # 采购单日期(取意向单的意向日期)
        date = TimeFunc.time_to_str(purchase_order.wish_order.wish_date, _type="date")
        return self.send_success(goods_list=goods_list,
                                 date=date,
                                 order_actual_amount=check_float(order_actual_amount / 100),
                                 order_subtotal=check_float(order_subtotal / 100))

    # 获取采购单的历史供货商
    def get_history_firms(self, order_id):
        firms = self.session.query(models.Firm)\
                            .join(models.PurchaseOrderGoods, models.PurchaseOrderGoods.firm_id == models.Firm.id)\
                            .filter(models.PurchaseOrderGoods.purchase_order_id == order_id,
                                    models.PurchaseOrderGoods.status >= 0)\
                            .order_by(models.PurchaseOrderGoods.update_time.desc())\
                            .distinct()\
                            .limit(constants.HISTORY_FIRM_NUM)\
                            .all()
        firm_list = list()
        for firm in firms:
            data = firm.to_dict()
            firm_list.append(data)
        return self.send_success(firm_list=firm_list)


# 采购单商品
class PurchaseOrderGoods(PurchaseBaseHandler):
    @BaseHandler.check_arguments("action:str", "purchase_order_id?:int")
    def get(self, goods_id):
        action = self.args["action"]
        purchase_order_id = self.args.get("purchase_order_id")
        purchase_goods = models.PurchaseOrderGoods.get_by_id(self.session, goods_id, station_id=self.current_station.id)
        if not purchase_goods:
            return self.send_fail("采购单商品不存在")
        if action == "get_purchase_goods":
            goods_dict = purchase_goods.to_dict()
            # 设置意向单商品的名称
            wish_goods = self.session.query(models.WishOrderGoods) \
                .filter(models.WishOrderGoods.id == purchase_goods.wish_order_goods_id,
                        models.WishOrderGoods.status >= 0) \
                .first()
            goods_dict["goods_name"] = wish_goods.goods_name if wish_goods else purchase_goods.goods.name
            goods_dict["goods_name_modified"] = wish_goods.goods_name_modified if wish_goods else None
            return self.send_success(goods_dict=goods_dict)
        # 获取采购商品的历史供货商
        elif action == "get_history_firms":
            firms = self.session.query(models.Firm)\
                                .join(models.PurchaseOrderGoods, models.PurchaseOrderGoods.firm_id == models.Firm.id)\
                                .filter(models.Firm.station_id == self.current_station.id,
                                        models.Firm.status == 0,
                                        models.PurchaseOrderGoods.id == goods_id,
                                        models.PurchaseOrderGoods.status >= 0)\
                                .order_by(models.PurchaseOrderGoods.update_time.desc())\
                                .distinct()\
                                .limit(constants.HISTORY_FIRM_NUM)\
                                .all()
            firm_list = list()
            for firm in firms:
                data = firm.to_dict()
                firm_list.append(data)
            return self.send_success(firm_list=firm_list)
        # 查看各门店要货
        elif action == "query_shop_demand":
            purchase_order = models.PurchaseOrder.get_by_id(self.session, purchase_order_id)
            if not purchase_order:
                return self.send_fail("采购单不存在")
            wish_order_id = self.session.query(models.WishOrder.id)\
                .join(models.PurchaseOrder, models.PurchaseOrder.wish_order_id == models.WishOrder.id)\
                .filter(models.PurchaseOrder.id == purchase_order_id,
                        models.WishOrder.status >= 0,
                        models.PurchaseOrder.status >= 0)\
                .scalar()
            demand_order_goods_objects = self.session.query(models.DemandOrderGoods)\
                .join(models.DemandOrder, models.DemandOrder.id == models.DemandOrderGoods.demand_order_id)\
                .filter(models.DemandOrder.wish_order_id == wish_order_id,
                        models.DemandOrderGoods.goods_id == purchase_goods.goods_id,
                        models.DemandOrderGoods.status >= 0,
                        models.DemandOrder.status >= 0)\
                .all()
            # 不显示没有提交订货单的商铺
            demand_goods_list = list()
            for demand_goods in demand_order_goods_objects:
                data = demand_goods.to_dict()
                demand_goods_list.append(data)
            return self.send_success(demand_goods_list=demand_goods_list)
        # 一周采购记录
        elif action == "week_purchase_record":
            now_date_time = TimeFunc.get_today_datetime() + timedelta(days=1)
            end_date_time = now_date_time - timedelta(days=7)
            purchase_order_goods_objs = self.session.query(models.PurchaseOrderGoods)\
                .join(models.Firm, models.Firm.id == models.PurchaseOrderGoods.firm_id)\
                .filter(models.Firm.station_id == self.current_station.id,
                        models.Firm.status == 0,
                        models.PurchaseOrderGoods.goods_id == purchase_goods.goods_id,
                        models.PurchaseOrderGoods.create_time >= end_date_time,
                        models.PurchaseOrderGoods.create_time <= now_date_time,
                        models.PurchaseOrderGoods.status >= 0)\
                .order_by(models.PurchaseOrderGoods.create_time.desc())\
                .all()
            purchase_goods_list = list()
            for purchase_goods in purchase_order_goods_objs:
                data = purchase_goods.to_dict()
                purchase_goods_list.append(data)
            return self.send_success(purchase_goods_list=purchase_goods_list)

        else:
            return self.send_fail("不支持的操作类型")

    @BaseHandler.check_arguments("order_id:int", "goods_ids:list")
    def post(self):
        order_id = self.args["order_id"]
        goods_ids = self.args["goods_ids"]
        purchase_order = models.PurchaseOrder.get_by_id(self.session, order_id)
        if not purchase_order:
            return self.send_fail("采购单不存在")
        valid, message = self.validate_goods_ids(goods_ids)
        if not valid:
            return self.send_fail(message)
        # 判断采购单商品是否存在
        purchase_order_goods_objects = self.session.query(models.PurchaseOrderGoods)\
            .filter(models.PurchaseOrderGoods.purchase_order_id == order_id,
                    models.PurchaseOrderGoods.purchaser_id == self.current_staff.id,
                    models.PurchaseOrderGoods.goods_id.in_(goods_ids),
                    models.PurchaseOrderGoods.status >= -1)\
            .all()
        purchase_order_goods_dict = defaultdict(list)
        estimated_amount = 0
        for purchase_goods in purchase_order_goods_objects:
            if purchase_goods.status == 0:
                purchase_order_goods_dict[purchase_goods.goods_id].append(purchase_goods)
            # 获取采购商品的待采购量
            estimated_amount = purchase_goods.estimated_amount
        for goods_id in goods_ids:
            # 如果采购商品不存在，则生成采购商品
            purchase_goods_list = purchase_order_goods_dict.get(goods_id)
            if not purchase_goods_list:
                new_purchase_goods = models.PurchaseOrderGoods(
                    tag=1,
                    goods_id=goods_id,
                    estimated_amount=estimated_amount,
                    purchase_order_id=order_id,
                    purchaser_id=self.current_staff.id
                )
                self.session.add(new_purchase_goods)
                self.session.flush()

                # 记录采购动态(如果采购商品的采购量=0，则是录入数据，否则是修改数据)
                self.record_purchasing_dynamics(5, new_purchase_goods)

        self.session.commit()
        return self.send_success()

    def validate_goods_ids(self, goods_ids):
        if not goods_ids:
            return False, "商品id列表不能为空"
        if not isinstance(goods_ids, list):
            return False, "商品列表参数格式有误"
        for goods_id in goods_ids:
            if not isinstance(goods_id, int):
                return False, "商品id参数有误"
        valid_goods_list = models.Goods.get_by_ids(self.session, goods_ids, self.current_station.id)
        valid_goods_ids = {goods.id for goods in valid_goods_list}
        if set(goods_ids) != valid_goods_ids:
            return False, "提交了无效的商品"
        return True, ""

    @BaseHandler.check_arguments("action:str")
    def put(self, goods_id):
        action = self.args["action"]
        purchase_goods = models.PurchaseOrderGoods.get_by_id(self.session, goods_id)
        if not purchase_goods:
            return self.send_fail("采购商品不存在")
        if action == "manually_entering":
            return self.manually_entering(purchase_goods)
        elif action == "again_entering":
            return self.again_entering(purchase_goods)
        elif action == "modify_purchase_goods_name":
            return self.modify_purchase_goods_name(purchase_goods)
        elif action == "purchase_remarks":
            return self.purchase_remarks(purchase_goods)
        elif action == "batch_entering":
            return self.batch_entering()
        elif action == "small_program_batch_entering":
            return self.small_program_batch_entering()
        elif action == "dont_purchase":
            return self.dont_purchase(purchase_goods)
        else:
            return self.send_fail("不支持的操作类型")

    @BaseHandler.check_arguments("firm_id:int", "actual_amount:float",
                                 "actual_weight:float", "fee:float", "deposit:float",
                                 "price:float", "actual_unit:int", "subtotal:float", "payment:int")
    def manually_entering(self, purchase_goods):
        firm_id = self.args["firm_id"]
        actual_amount = self.args["actual_amount"]
        actual_weight = self.args["actual_weight"]
        fee = self.args["fee"]
        deposit = self.args["deposit"]
        price = self.args["price"]
        actual_unit = self.args["actual_unit"]
        subtotal = self.args["subtotal"]
        payment = self.args["payment"]
        # 校验商品和供货商，建立商品和供货商之间的关系
        models.FirmGoods.add_firm_goods(self.session, purchase_goods.goods_id, firm_id, self.current_station.id)
        # 后端也要计算下统计数据
        # 按件计价
        amount_result = (price + fee + deposit) * actual_amount
        # 按斤计价: 重量 * 价格 + （行费 + 押金）* 件数
        weight_result = actual_weight * price + (fee + deposit) * actual_amount
        if actual_unit == 0 and check_float(amount_result) != subtotal:
            return self.send_fail("按件计价数据统计错误")
        if actual_unit == 1 and check_float(weight_result) != subtotal:
            return self.send_fail("按斤计价数据统计错误")
        # 判断商品是否已分车结算
        firm_settlement_voucher = self.session.query(models.FirmSettlementVoucher) \
            .join(models.AllocationOrder, models.AllocationOrder.id == models.FirmSettlementVoucher.allocation_order_id) \
            .filter(models.AllocationOrder.purchase_order_goods_id == purchase_goods.id,
                    models.FirmSettlementVoucher.status == 1,
                    models.AllocationOrder.status == 1) \
            .first()
        if firm_settlement_voucher:
            return self.send_fail("该采购商品已分车结算完成")

        # 判断是添加还是修改(0: 录入 1: 修改)
        record_type = 0 if purchase_goods.actual_amount == 0 else 1
        # 获取上一次的采购单价、采购件数、采购重量、采购小计
        last_data_dict = dict()
        if record_type == 1:
            if check_float(purchase_goods.price / 100) != price:
                last_data_dict["last_price"] = purchase_goods.price
            if check_float(purchase_goods.actual_amount / 100) != actual_amount:
                last_data_dict["last_actual_amount"] = purchase_goods.actual_amount
            if check_float(purchase_goods.actual_weight / 100) != actual_weight:
                last_data_dict["last_actual_weight"] = purchase_goods.actual_weight
            if check_float(purchase_goods.subtotal / 100) != subtotal:
                last_data_dict["last_subtotal"] = purchase_goods.subtotal
            if purchase_goods.firm_id != firm_id:
                last_data_dict["last_firm_id"] = purchase_goods.firm_id

        purchase_goods.firm_id = firm_id
        purchase_goods.actual_amount = check_int(actual_amount * 100)
        purchase_goods.actual_weight = check_int(actual_weight * 100)
        purchase_goods.fee = check_int(fee * 100)
        purchase_goods.deposit = check_int(deposit * 100)
        purchase_goods.price = check_int(price * 100)
        purchase_goods.actual_unit = actual_unit
        purchase_goods.subtotal = check_int(subtotal * 100)
        purchase_goods.payment = payment
        # 恢复商品「不采了」的状态
        if purchase_goods.is_purchase == 1:
            purchase_goods.is_purchase = 0

        # 记录采购动态
        self.record_purchasing_dynamics(record_type, purchase_goods, **last_data_dict)

        self.session.commit()
        return self.send_success()

    # 一品多供货商
    @BaseHandler.check_arguments("firm_id:int", "actual_amount:float",
                                 "actual_weight:float", "fee:float", "deposit:float",
                                 "price:float", "actual_unit:int", "subtotal:float", "payment:int")
    def again_entering(self, purchase_goods):
        firm_id = self.args["firm_id"]
        actual_amount = self.args["actual_amount"]
        actual_weight = self.args["actual_weight"]
        fee = self.args["fee"]
        deposit = self.args["deposit"]
        price = self.args["price"]
        actual_unit = self.args["actual_unit"]
        subtotal = self.args["subtotal"]
        payment = self.args["payment"]
        # 校验商品和供货商，建立商品和供货商之间的关系
        models.FirmGoods.add_firm_goods(self.session, purchase_goods.goods_id, firm_id, self.current_station.id)
        # 后端也要计算下统计数据
        # 按件计价
        amount_result = (price + fee + deposit) * actual_amount
        # 按斤计价: 重量 * 价格 + （行费 + 押金）* 件数
        weight_result = actual_weight * price + (fee + deposit) * actual_amount
        if actual_unit == 0 and check_float(amount_result) != subtotal:
            return self.send_fail("按件计价数据统计错误")
        if actual_unit == 1 and check_float(weight_result) != subtotal:
            return self.send_fail("按斤计价数据统计错误")

        new_goods = models.PurchaseOrderGoods(
            estimated_amount=purchase_goods.estimated_amount,  # 预采购量
            actual_amount=check_int(actual_amount * 100),  # 实采件数
            actual_weight=check_int(actual_weight * 100),  # 实采重量
            fee=check_int(fee * 100),
            deposit=check_int(deposit * 100),
            price=check_int(price * 100),
            actual_unit=actual_unit,
            subtotal=check_int(subtotal * 100),
            payment=payment,
            tag=purchase_goods.tag,
            purchase_order_id=purchase_goods.purchase_order_id,
            goods_id=purchase_goods.goods_id,
            firm_id=firm_id,
            purchaser_id=purchase_goods.purchaser_id,
            wish_order_goods_id=purchase_goods.wish_order_goods_id
        )
        self.session.add(new_goods)
        self.session.commit()

        # 记录采购动态
        self.record_purchasing_dynamics(0, purchase_goods)

        return self.send_success()

    # 平台批量录入采购数据
    @BaseHandler.check_arguments("purchase_goods_list:list")
    def batch_entering(self):
        purchase_goods_list = self.args["purchase_goods_list"]
        valid, message, already_exist_goods_list = self.validate_purchase_goods_list(purchase_goods_list)
        if not valid:
            return self.send_fail(message)
        # 取任意一个已存在的采购商品
        temp_purchase_goods = already_exist_goods_list[0]
        already_exist_goods_dict = {purchase_goods.id: purchase_goods for purchase_goods in already_exist_goods_list}
        for purchase_goods in purchase_goods_list:
            already_exist_goods = already_exist_goods_dict.get(purchase_goods["id"])
            # 后端也要计算下统计数据
            subtotal = purchase_goods["subtotal"]
            price = purchase_goods["price"]
            actual_amount = purchase_goods["actual_amount"]
            payment = purchase_goods["payment"]
            firm_id = purchase_goods["firm_id"]
            if subtotal != price * actual_amount:
                return self.send_fail("按件计价数据统计错误")
            if not already_exist_goods:
                new_purchase_goods = models.PurchaseOrderGoods(
                    estimated_amount=temp_purchase_goods.estimated_amount,
                    actual_amount=check_int(actual_amount * 100),
                    price=check_int(price * 100),
                    subtotal=check_int(subtotal * 100),
                    payment=payment,
                    tag=temp_purchase_goods.tag,
                    wish_order_goods_id=temp_purchase_goods.wish_order_goods_id,
                    firm_id=firm_id,
                    goods_id=temp_purchase_goods.goods_id,
                    purchaser_id=self.current_staff.id,
                    purchase_order_id=temp_purchase_goods.purchase_order_id
                )
                self.session.add(new_purchase_goods)
                self.session.flush()
                # 建立商品和供货商之间的关系
                models.FirmGoods.add_firm_goods(self.session, new_purchase_goods.goods_id, firm_id, self.current_station.id)
            else:
                already_exist_goods.price = check_int(price * 100)
                already_exist_goods.actual_amount = check_int(actual_amount * 100)
                already_exist_goods.payment = payment
                already_exist_goods.subtotal = check_int(subtotal * 100)
                already_exist_goods.firm_id = firm_id
                already_exist_goods.purchaser_id = self.current_staff.id
        self.session.commit()
        return self.send_success()

    def validate_purchase_goods_list(self, purchase_goods_list):
        """验证采购数据列表参数
        [
            {
                "id": 采购商品id,
                "firm_id": 供货商id
                "price": 单价,
                "actual_amount": 件数,
                "payment": 支付方式
                "subtotal": 小计
            },
            ...
        ]
        """
        if not isinstance(purchase_goods_list, list):
            return False, "采购数据列表参数格式有误", None

        for purchase_goods in purchase_goods_list:
            if not isinstance(purchase_goods, dict):
                return False, "采购数据参数项格式有误", None

            if "id" not in purchase_goods:
                return False, "参数缺失：采购商品id", None
            elif not is_int(purchase_goods["id"]):
                return False, "采购商品id 应为整数类型", None

            if "firm_id" not in purchase_goods:
                return False, "参数缺失：firm_id", None
            elif not is_int(purchase_goods["firm_id"]):
                return False, "firm_id 应为整数类型", None

            if "price" not in purchase_goods:
                return False, "参数缺失：price", None
            elif not is_number(purchase_goods["price"]):
                return False, "price 应为数字类型", None
            elif purchase_goods["price"] < 0:
                return False, "单价不能是负数", None
            elif purchase_goods["price"] >= 2147483600:
                return False, "单价的值过大", None

            if "actual_amount" not in purchase_goods:
                return False, "参数缺失：actual_amount", None
            elif not is_number(purchase_goods["actual_amount"]):
                return False, "actual_amount 应为数字类型", None
            elif purchase_goods["price"] < 0:
                return False, "件数不能是负数", None
            elif purchase_goods["price"] >= 2147483600:
                return False, "件数的值过大", None

            if "payment" not in purchase_goods:
                return False, "参数缺失：payment", None
            elif not is_int(purchase_goods["payment"]):
                return False, "payment 应为整数类型", None
            elif purchase_goods["payment"] not in models.PurchaseOrderGoods.payment_list:
                return False, "参数无效：payment = {0}".format(purchase_goods["payment"]), None

        goods_ids = [check_int(purchase_goods["id"]) for purchase_goods in purchase_goods_list]
        # 检验采购商品id是否重复
        for goods_id in goods_ids:
            if goods_id != 0 and goods_ids.count(goods_id) > 1:
                return False, "采购商品id重复", None
        # 检验采购商品id有效性
        already_exist_goods_list = self.session.query(models.PurchaseOrderGoods)\
            .filter(models.PurchaseOrderGoods.id.in_(goods_ids),
                    models.PurchaseOrderGoods.status >= 0)\
            .all()
        if not already_exist_goods_list:
            return False, "缺少有效的采购商品id", None
        valid_goods_ids = {purchase_goods.id for purchase_goods in already_exist_goods_list}
        if set(goods_ids) - {0} != valid_goods_ids:
            return False, "提交了无效的采购商品", None

        firm_ids = [check_int(purchase_goods["firm_id"]) for purchase_goods in purchase_goods_list]
        # 检验供货商id有效性
        firms = models.Firm.get_by_ids(self.session, firm_ids, station_id=self.current_station.id)
        valid_firm_ids = {firm.id for firm in firms}
        if set(firm_ids) != valid_firm_ids:
            return False, "选择了无效的供货商", None
        # 检验供货商id是否重复(不允许在同一家供货商录入多次数据)
        firm_dict = {firm.id: firm.name for firm in firms}
        for firm_id in firm_ids:
            if firm_ids.count(firm_id) > 1:
                firm_name = firm_dict.get(firm_id)
                return False, "不可以在「{0}」供货商处重复录入采购数据噢".format(firm_name), None

        return True, "", already_exist_goods_list

    # 小程序批量录入采购数据
    @BaseHandler.check_arguments("purchase_goods_list:list")
    def small_program_batch_entering(self):
        purchase_goods_list = self.args["purchase_goods_list"]
        valid, message, already_exist_goods_list = self.small_program_validate_goods_list(purchase_goods_list)
        if not valid:
            return self.send_fail(message)

        already_exist_goods_dict = {purchase_goods.id: purchase_goods for purchase_goods in already_exist_goods_list}
        for purchase_goods_info in purchase_goods_list:
            purchase_goods = already_exist_goods_dict.get(purchase_goods_info["id"])
            # 后端也要计算下统计数据
            firm_id = purchase_goods_info["firm_id"]
            actual_amount = purchase_goods_info["actual_amount"]
            actual_weight = purchase_goods_info["actual_weight"]
            fee = purchase_goods_info["fee"]
            deposit = purchase_goods_info["deposit"]
            price = purchase_goods_info["price"]
            actual_unit = purchase_goods_info["actual_unit"]
            subtotal = purchase_goods_info["subtotal"]
            payment = purchase_goods_info["payment"]

            # 校验商品和供货商，建立商品和供货商之间的关系
            models.FirmGoods.add_firm_goods(self.session, purchase_goods.goods_id, firm_id, self.current_station.id)
            # 后端也要计算下统计数据
            # 按件计价
            amount_result = (price + fee + deposit) * actual_amount
            # 按斤计价: 重量 * 价格 + （行费 + 押金）* 件数
            weight_result = actual_weight * price + (fee + deposit) * actual_amount
            if actual_unit == 0 and check_float(amount_result) != subtotal:
                return self.send_fail("按件计价数据统计错误")
            if actual_unit == 1 and check_float(weight_result) != subtotal:
                return self.send_fail("按斤计价数据统计错误")

            # 如果是首次录入数据
            if purchase_goods.actual_amount == 0 and purchase_goods.actual_weight == 0:
                purchase_goods.firm_id = firm_id
                purchase_goods.actual_amount = check_int(actual_amount * 100)
                purchase_goods.actual_weight = check_int(actual_weight * 100)
                purchase_goods.fee = check_int(fee * 100)
                purchase_goods.deposit = check_int(deposit * 100)
                purchase_goods.price = check_int(price * 100)
                purchase_goods.actual_unit = actual_unit
                purchase_goods.subtotal = check_int(subtotal * 100)
                purchase_goods.payment = payment
                purchase_goods.purchaser_id = self.current_staff.id
                # 判断商品的状态是否是不采了
                if purchase_goods.is_purchase == 1:
                    purchase_goods.is_purchase = 0
            # 否则是一品多供货商
            else:
                purchase_goods = models.PurchaseOrderGoods(
                    estimated_amount=purchase_goods.estimated_amount,
                    actual_amount=check_int(actual_amount * 100),
                    actual_weight=check_int(actual_weight * 100),
                    actual_unit=actual_unit,
                    fee=check_int(fee * 100),
                    deposit=check_int(deposit * 100),
                    price=check_int(price * 100),
                    subtotal=check_int(subtotal * 100),
                    payment=payment,
                    tag=purchase_goods.tag,
                    wish_order_goods_id=purchase_goods.wish_order_goods_id,
                    firm_id=firm_id,
                    goods_id=purchase_goods.goods_id,
                    purchaser_id=self.current_staff.id,
                    purchase_order_id=purchase_goods.purchase_order_id
                )
                self.session.add(purchase_goods)
                self.session.flush()

            # 记录采购动态
            self.record_purchasing_dynamics(0, purchase_goods)

        self.session.commit()
        return self.send_success()

    def small_program_validate_goods_list(self, purchase_goods_list):
        """验证采购数据列表参数
            [
                {
                    "id": 采购商品id,
                    "firm_id": 供货商id
                    "price": 单价,
                    "actual_amount": 件数,
                    "actual_weight": 重量,
                    "actual_unit": 实际采购单位,
                    "fee": 行费,
                    "deposit": 押金,
                    "payment": 支付方式
                    "subtotal": 小计
                },
                ...
            ]
        """
        if not isinstance(purchase_goods_list, list):
            return False, "采购数据列表参数格式有误", None

        for purchase_goods in purchase_goods_list:
            if not isinstance(purchase_goods, dict):
                return False, "采购数据参数项格式有误", None

            if "id" not in purchase_goods:
                return False, "参数缺失：采购商品id", None
            elif not is_int(purchase_goods["id"]):
                return False, "采购商品id 应为整数类型", None

            if "firm_id" not in purchase_goods:
                return False, "参数缺失：firm_id", None
            elif not is_int(purchase_goods["firm_id"]):
                return False, "firm_id 应为整数类型", None

            if "price" not in purchase_goods:
                return False, "参数缺失：price", None
            elif not is_number(purchase_goods["price"]):
                return False, "price 应为数字类型", None
            elif purchase_goods["price"] < 0:
                return False, "单价不能是负数", None
            elif purchase_goods["price"] >= 2147483600:
                return False, "单价的值过大", None

            if "actual_amount" not in purchase_goods:
                return False, "参数缺失：actual_amount", None
            elif not is_number(purchase_goods["actual_amount"]):
                return False, "actual_amount 应为数字类型", None
            elif purchase_goods["price"] < 0:
                return False, "件数不能是负数", None
            elif purchase_goods["price"] >= 2147483600:
                return False, "件数的值过大", None

            if "actual_weight" not in purchase_goods:
                return False, "参数缺失：actual_weight", None
            elif not is_number(purchase_goods["actual_weight"]):
                return False, "actual_weight 应为数字类型", None
            elif purchase_goods["actual_weight"] < 0:
                return False, "重量不能是负数", None
            elif purchase_goods["actual_weight"] >= 2147483600:
                return False, "重量的值过大", None

            if "fee" not in purchase_goods:
                return False, "参数缺失：fee", None
            elif not is_number(purchase_goods["fee"]):
                return False, "fee 应为数字类型", None
            elif purchase_goods["fee"] < 0:
                return False, "行费不能是负数", None
            elif purchase_goods["fee"] >= 2147483600:
                return False, "行费的值过大", None

            if "deposit" not in purchase_goods:
                return False, "参数缺失：deposit", None
            elif not is_number(purchase_goods["deposit"]):
                return False, "deposit 应为数字类型", None
            elif purchase_goods["deposit"] < 0:
                return False, "押金不能是负数", None
            elif purchase_goods["deposit"] >= 2147483600:
                return False, "押金的值过大", None

            if "payment" not in purchase_goods:
                return False, "参数缺失：payment", None
            elif not is_int(purchase_goods["payment"]):
                return False, "payment 应为整数类型", None
            elif purchase_goods["payment"] not in models.PurchaseOrderGoods.payment_list:
                return False, "参数无效：payment = {0}".format(purchase_goods["payment"]), None

        goods_ids = [check_int(purchase_goods["id"]) for purchase_goods in purchase_goods_list]
        # 检验采购商品id是否重复
        for goods_id in goods_ids:
            if goods_id != 0 and goods_ids.count(goods_id) > 1:
                return False, "采购商品id重复", None
        # 检验采购商品id有效性
        already_exist_goods_list = self.session.query(models.PurchaseOrderGoods) \
            .filter(models.PurchaseOrderGoods.id.in_(goods_ids),
                    models.PurchaseOrderGoods.status >= 0) \
            .all()
        if not already_exist_goods_list:
            return False, "缺少有效的采购商品id", None
        valid_goods_ids = {purchase_goods.id for purchase_goods in already_exist_goods_list}
        if set(goods_ids) != valid_goods_ids:
            return False, "提交了无效的采购商品", None

        firm_ids = {check_int(purchase_goods["firm_id"]) for purchase_goods in purchase_goods_list}
        # 检验供货商id单一性
        if not firm_ids:
            return False, "请选择供货商", None
        if len(firm_ids) > 1:
            return False, "选择了多个供货商", None
        # 检验供货商id有效性
        firm_id = next(iter(firm_ids))
        firm = models.Firm.get_by_firm_id(self.session, firm_id, station_id=self.current_station.id)
        if not firm:
            return False, "选择了无效的供货商", None

        return True, "", already_exist_goods_list

    @BaseHandler.check_arguments("goods_name:str")
    def modify_purchase_goods_name(self, purchase_goods):
        goods_name = self.args["goods_name"]
        valid, message = self.validate_goods_name(goods_name, purchase_goods)
        if not valid:
            return self.send_fail(message)
        # 如果是采购员手动添加的商品(手动添加的采购商品没有对应的意向商品)，则直接修改商品name
        if not purchase_goods.wish_order_goods_id:
            last_goods_name = purchase_goods.goods.name
            purchase_goods.goods.name = goods_name

        else:
            wish_goods = purchase_goods.wish_order_goods
            last_goods_name = wish_goods.goods_name
            wish_goods.goods_name = goods_name

            # 更新意向商品修改状态
            wish_goods.goods_name_modified = 1

        self.session.commit()

        if last_goods_name != goods_name:
            # 记录修改名称动态
            last_data_dict = {"last_goods_name": last_goods_name}
            self.record_purchasing_dynamics(4, purchase_goods, **last_data_dict)

        return self.send_success()

    def validate_goods_name(self, name, purchase_goods):
        if not name:
            return False, "请填写采购商品名称"
        if len(name) > constants.GOODS_NAME_LEN:
            return False, "采购商品名称过长"
        # 采购商品name不允许重复
        purchase_order_goods_objects = self.session.query(models.PurchaseOrderGoods)\
            .filter(models.PurchaseOrderGoods.purchase_order_id == purchase_goods.purchase_order_id,
                    models.PurchaseOrderGoods.purchaser_id == self.current_staff.id,
                    models.PurchaseOrderGoods.goods_id != purchase_goods.goods_id,
                    models.PurchaseOrderGoods.status >= 0)\
            .all()
        goods_name_list = list()
        for purchase_goods in purchase_order_goods_objects:
            wish_goods = purchase_goods.wish_order_goods
            goods = purchase_goods.goods
            goods_name = wish_goods.goods_name if wish_goods else goods.name
            goods_name_list.append(goods_name)
        if name in goods_name_list:
            return False, "采购商品名称重复"
        return True, ""

    @BaseHandler.check_arguments("remarks:str")
    def purchase_remarks(self, purchase_goods):
        remarks = self.args["remarks"]
        if len(remarks) > 128:
            return self.send_fail("备注内容过长")
        purchase_goods.remarks = remarks

        # 记录采购动态
        self.record_purchasing_dynamics(3, purchase_goods)

        self.session.commit()
        return self.send_success()

    # 将商品设置为不采了
    def dont_purchase(self, purchase_goods):
        if purchase_goods.actual_amount:
            return self.send_fail("该商品已录入采购数据")
        if not purchase_goods.purchaser_id:
            return self.send_fail("该商品未分配采购员")
        if purchase_goods.is_purchase == 0:
            purchase_goods.is_purchase = 1
            self.session.commit()

        # 记录采购动态
        self.record_purchasing_dynamics(2, purchase_goods)

        return self.send_success()

    def delete(self, goods_id):
        # 逻辑删除当前采购员的采购商品
        purchase_goods = self.session.query(models.PurchaseOrderGoods)\
                                     .filter(models.PurchaseOrderGoods.id == goods_id,
                                             models.PurchaseOrderGoods.purchaser_id == self.current_staff.id,
                                             models.PurchaseOrderGoods.status >= 0)\
                                     .first()
        if not purchase_goods:
            return self.send_fail("采购单商品不存在")
        # 查询采购商品（也包括一品多供货商的采购数据）
        purchase_goods_objects = self.session.query(models.PurchaseOrderGoods)\
            .filter(models.PurchaseOrderGoods.purchase_order_id == purchase_goods.purchase_order_id,
                    models.PurchaseOrderGoods.goods_id == purchase_goods.goods_id,
                    models.PurchaseOrderGoods.purchaser_id == self.current_staff.id,
                    models.PurchaseOrderGoods.status >= 0)\
            .all()
        for purchase_goods in purchase_goods_objects:
            purchase_goods.status = -1
        self.session.commit()

        for purchase_goods in purchase_goods_objects:
            # 记录采购动态
            self.record_purchasing_dynamics(6, purchase_goods)

        return self.send_success()


# 采购小程序获取采购动态数据
class PurchasingDynamics(PurchasingDynamicsMixin, PurchaseBaseHandler):
    pass
