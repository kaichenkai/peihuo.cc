#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import func
from handlers.base.pub_func import TimeFunc, check_float, check_int
from handlers.base.pub_web import StationBaseHandler
from handlers.base.pub_web import BaseHandler
from dal import models, constants
from collections import defaultdict


# 汇总单-仓库出入库统计列表
class StockOutInStatisticsList(StationBaseHandler):
    @BaseHandler.check_arguments("wish_order_id:int", "sort_by?:str", "reverse?:int")
    def get(self):
        wish_order_id = self.args["wish_order_id"]
        sort_by = self.args.get("sort_by", "stock").strip()
        # 默认倒序
        reverse = self.args.get("reverse", 1)
        wish_order = models.WishOrder.get_by_id(self.session, wish_order_id, self.current_station.id)
        if not wish_order:
            return self.send_fail("没有找到指定的意向单")
        if wish_order.status <= 1:
            return self.send_fail("意向单还未提交")
        # 取到意向单中商品的id
        wish_goods_list = self.session.query(models.WishOrderGoods)\
                                      .filter(models.WishOrderGoods.wish_order_id == wish_order_id,
                                              models.WishOrderGoods.status >= 0)\
                                      .all()
        goods_ids = [wish_goods.goods_id for wish_goods in wish_goods_list]

        # 获取意向单中的商品
        goods_object_list = self.session.query(models.Goods)\
                                        .filter(models.Goods.station_id == self.current_station.id,
                                                models.Goods.status == 0,
                                                models.Goods.id.in_(goods_ids))\
                                        .all()
        total_stock = sum(goods.stock for goods in goods_object_list)
        # 待出库记录
        wait_stock_out_record = self.session.query(models.StockOutInGoods.goods_id,
                                                   func.sum(models.StockOutInGoods.amount))\
                                            .filter(models.StockOutInGoods.status == 2,
                                                    models.StockOutInGoods.wish_order_id == wish_order_id)\
                                            .group_by(models.StockOutInGoods.goods_id)\
                                            .all()
        wait_stock_out_record_dict = {record[0]: record[1] for record in wait_stock_out_record}
        wait_stock_out_total_amount = sum(record[1] for record in wait_stock_out_record)

        # 已入库记录
        stock_in_record = self.session.query(models.StockOutInGoods.goods_id,
                                             func.sum(models.StockOutInGoods.amount))\
                                      .filter(models.StockOutInGoods.status == 1,
                                              models.StockOutInGoods.wish_order_id == wish_order_id)\
                                      .group_by(models.StockOutInGoods.goods_id)\
                                      .all()
        stock_in_record_dict = {record[0]: record[1] for record in stock_in_record}
        stock_in_total_amount = sum(record[1] for record in stock_in_record)

        goods_list = list()
        for goods in goods_object_list:
            data = goods.to_dict()
            data["stock"] = check_float(goods.stock / 100)
            data["wait_stock_out_amount"] = check_float(wait_stock_out_record_dict.get(goods.id, 0) / 100)
            data["stock_in_amount"] = check_float(stock_in_record_dict.get(goods.id, 0) / 100)
            # 如果商品的库存、待出库、已入库的数量都是0，则不返回
            if sum([data["stock"], data["wait_stock_out_amount"], data["stock_in_amount"]]) == 0:
                continue
            goods_list.append(data)
        if sort_by not in ["stock", "wait_stock_out_amount", "stock_in_amount"]:
            return self.send_fail("无效的排序参数")
        goods_list = sorted(goods_list, key=lambda x: x[sort_by], reverse=bool(reverse))

        total_data_dict = dict()
        total_data_dict["total_stock"] = check_float(total_stock / 100)
        total_data_dict["wait_stock_out_total_amount"] = check_float(wait_stock_out_total_amount / 100)
        total_data_dict["stock_in_total_amount"] = check_float(stock_in_total_amount / 100)
        return self.send_success(goods_list=goods_list, total_data_dict=total_data_dict)


# 出库商品清单
class StockOutList(StationBaseHandler):
    @BaseHandler.check_arguments("record_date?:date", "goods_ids?:str", "page?:int", "limit?:int")
    def get(self):
        record_date = self.args.get("record_date")
        goods_ids = self.args.get("goods_ids")
        if goods_ids is not None:
            goods_ids = set(map(lambda i: check_int(i), goods_ids.split("|")))
        page = self.args.get("page", 0)
        limit = self.args.get("limit", constants.PAGE_SIZE)
        if limit > constants.PAGE_MAX_LIMIT:
            limit = constants.PAGE_SIZE

        station = self.current_station
        records = self.session.query(models.StockOutInGoods)\
                              .filter(models.StockOutInGoods.station_id == station.id,
                                      models.StockOutInGoods.status == 2)
        if record_date:
            records = records.filter(func.DATE(models.StockOutInGoods.create_time) == record_date)
        if goods_ids is not None:
            records = records.filter(models.StockOutInGoods.goods_id.in_(goods_ids))

        all_goods_ids = records.with_entities(models.StockOutInGoods.goods_id).all()
        all_goods_ids = {i[0] for i in all_goods_ids}
        all_goods = self.session.query(models.Goods) \
            .filter(models.Goods.id.in_(all_goods_ids)) \
            .all()

        records = records.order_by(models.StockOutInGoods.id.desc())\
            .offset(page * limit)\
            .limit(limit)\
            .all()

        record_list = list()
        for record in records:
            data = record.to_dict()
            record_list.append(data)

        goods_data = [{
            "id": goods.id,
            "name": goods.name,
        } for goods in all_goods]

        has_more = len(record_list) >= limit
        return self.send_success(record_list=record_list, goods_data=goods_data, has_more=has_more)


# 入库单
class StockInRecord(StationBaseHandler):
    @BaseHandler.check_arguments("allocation_order_id:int", "stock_in_amount?:float")
    def post(self):
        allocation_order_id = self.args["allocation_order_id"]
        stock_in_amount = self.args.get("stock_in_amount")

        allocation_order = models.AllocationOrder.get_by_id(self.session, allocation_order_id, self.current_station.id)
        if not allocation_order:
            return self.send_fail("没有找到对应的分车单")
        elif not allocation_order.purchase_order_goods_id:
            return self.send_fail("没有找到有效的供货商分车单")

        existed_record = self.session.query(models.StockOutInGoods) \
            .filter(models.StockOutInGoods.type == 1,
                    models.StockOutInGoods.allocation_order_id == allocation_order.id,
                    models.StockOutInGoods.status >= 0) \
            .first()
        if existed_record:
            return self.send_fail("已经创建过此采购单商品的入库单了")

        if stock_in_amount is not None:
            # 修改过的分车量
            allocated_amount = check_int(stock_in_amount * 100)
        else:
            # 所有送到仓库的分车量
            allocated_amount = self.session.query(func.sum(models.AllocationOrderGoods.actual_allocated_amount)) \
                .filter(models.AllocationOrderGoods.order_id == allocation_order.id,
                        models.AllocationOrderGoods.destination == 1) \
                .first()
            allocated_amount = allocated_amount[0] or 0 if allocated_amount else 0

        # 采购分到仓库
        if allocation_order.purchase_order_goods_id:
            purchase_goods = models.PurchaseOrderGoods.get_by_id(self.session, allocation_order.purchase_order_goods_id,
                                                                 self.current_station.id)
            if not purchase_goods:
                return self.send_fail("没有找到对应的采购单商品")

            goods = purchase_goods.goods
            goods_id = goods.id
            # 库存采购均价 = (原有库存的实际成本 + 本次进货的实际成本) / (原有库存数量 + 本次进货数量)
            if goods.stock_average_price:
                goods.stock_average_price = check_float(
                    (goods.stock_cost + purchase_goods.subtotal/purchase_goods.actual_amount
                     * allocated_amount / 100)
                    / (goods.stock + allocated_amount) * 100)
            else:
                goods.stock_average_price = purchase_goods.price
            # 库存成本（数据库中存储时都 * 100，所以再做乘法处理时需要 / 100）
            goods.stock_cost += check_float(purchase_goods.subtotal/purchase_goods.actual_amount
                                            * allocated_amount / 100)
        elif allocation_order.stock_out_record_id:
            stock_out_record = models.StockOutInGoods.get_by_id(self.session,
                                                                allocation_order.stock_out_record_id,
                                                                self.current_station,
                                                                [3, 4])
            if not stock_out_record:
                return self.send_fail("没有找到对应的出库记录")

            goods = stock_out_record.goods
            goods_id = goods.id
            # 库存成本（数据库中存储时都 * 100，所以再做乘法处理时需要 / 100）
            goods.stock_cost += check_float(goods.stock_average_price * allocated_amount / 100)
        else:
            return self.send_fail("分车单类型未知")

        # 创建入库单
        new_stock_in_record = models.StockOutInGoods(
            type=1,
            status=1,
            amount=allocated_amount,
            allocation_order_id=allocation_order_id,
            goods_id=goods_id,
            wish_order_id=allocation_order.wish_order_id,
            station_id=self.current_station.id,
            creator_id=self.current_user.id,
            operator_id=self.current_user.id,
        )
        self.session.add(new_stock_in_record)
        self.session.flush()

        # 增加库存
        new_stock_in_record.goods.stock += new_stock_in_record.amount
        self.session.flush()

        # 生成单号
        models.SerialNumberMap.generate(self.session, 1, new_stock_in_record.id, self.current_station.id)

        # 确认分车单
        allocation_order.status = 1

        self.session.commit()
        return self.send_success()


# 出库单
class StockOutRecord(StationBaseHandler):
    @BaseHandler.check_arguments("goods_id:int", "amount?:float")
    def post(self):
        goods_id = self.args["goods_id"]
        amount = check_int(self.args.get("amount", 0) * 100)

        # 以意向日期最新的一个意向单为准
        wish_order = self.session.query(models.WishOrder) \
            .filter(models.WishOrder.station_id == self.current_station.id,
                    models.WishOrder.status >= 2) \
            .order_by(models.WishOrder.wish_date.desc()) \
            .first()
        if not wish_order:
            return self.send_fail("没有找到已提交的意向单")

        goods = models.Goods.get_by_goods_id(self.session, goods_id, self.current_station.id)
        if not goods:
            return self.send_fail("没有找到对应的商品")

        new_record = models.StockOutInGoods(
            station_id=self.current_station.id,
            wish_order_id=wish_order.id,
            creator_id=self.current_user.id,
            operator_id=self.current_user.id,
            goods_id=goods_id,
            amount=amount,
            type=0,
            status=2,
        )
        self.session.add(new_record)
        self.session.flush()

        models.SerialNumberMap.generate(self.session, 2, new_record.id, self.current_station.id)

        self.session.commit()
        return self.send_success()

    def delete(self, stock_outin_record_id):
        stockout_record = models.StockOutInGoods.get_by_id(self.session, stock_outin_record_id, self.current_station.id)
        if not stockout_record or stockout_record.type != 0:
            return self.send_fail("没有找到对应的出库单")
        elif stockout_record.status > 2:
            return self.send_fail("该出库单已经出库，无法删除")

        stockout_record.status = -1
        self.session.commit()

        return self.send_success()

    @BaseHandler.check_arguments("action:str", "amount?:float")
    def put(self, stock_outin_record_id):
        action = self.args["action"]
        amount = self.args.get("amount")
        if amount and amount >= 2147483600:
            return self.send_fail("出库数量过大")
        if amount and amount < 0:
            return self.send_fail("出库数量不能为负数")

        stock_outin_record = models.StockOutInGoods.get_by_id(self.session, stock_outin_record_id, self.current_station.id)
        if not stock_outin_record:
            return self.send_fail("出库记录不存在")
        if stock_outin_record.status != 2:
            return self.send_fail("出库记录状态有误")

        staff = models.Staff.get_by_account_id(self.session, self.current_user.id, self.current_station.id)
        if not staff:
            return self.send_fail("您不是当前中转站的员工")
        # 不是超管且没有仓库权限
        if staff.super_admin_status != 1 and (staff.admin_status != 1 or 4 not in staff.admin_permission_list):
            return self.send_fail("无权操作出入库记录")

        if action == "modify_stock_out_amount":
            stock_outin_record.amount = check_int(amount * 100)
            self.session.commit()
            return self.send_success()
        elif action == "stockout_affirm":
            return self.stockout_affirm(stock_outin_record)
        else:
            return self.send_fail("不支持的操作类型")

    def stockout_affirm(self, stock_outin_record):
        goods = stock_outin_record.goods
        # 减少库存量
        goods.stock -= stock_outin_record.amount
        # 减少库存成本（数据库中存储时 * 100，所以再做乘法处理时需要 / 100）
        goods.stock_cost -= check_float(goods.stock_average_price * stock_outin_record.amount / 100)
        stock_outin_record.operator_id = self.current_user.id
        stock_outin_record.status = 3
        self.session.commit()
        return self.send_success()


# 出入库记录
class StockOutInRecord(StationBaseHandler):
    @BaseHandler.check_arguments("page?:int", "limit?:int", "goods_ids?:str")
    def get(self):
        page = self.args.get("page", 0)
        limit = self.args.get("limit", constants.PAGE_SIZE)
        goods_ids = self.args.get("goods_ids")
        if limit > constants.PAGE_MAX_LIMIT:
            limit = constants.PAGE_SIZE
        station = self.current_station
        query_set = self.session.query(models.StockOutInGoods)

        if goods_ids:
            goods_ids = [check_int(goods_id)for goods_id in goods_ids.split("|")]
            query_set = query_set.filter(models.StockOutInGoods.goods_id.in_(goods_ids))

        stock_outin_record_objects = query_set.filter(models.StockOutInGoods.station_id == station.id,
                                                      models.StockOutInGoods.status.in_([1, 3, 4]))\
                                              .order_by(models.StockOutInGoods.create_time.desc())\
                                              .offset(page * limit)\
                                              .limit(limit)\
                                              .all()
        stock_outin_record_list = list()
        for stock_outin_record in stock_outin_record_objects:
            data = stock_outin_record.to_dict()
            stock_outin_record_list.append(data)

        # 出入库记录商品信息(搜索使用)
        goods_ids = [stock_outin_record.goods_id for stock_outin_record in stock_outin_record_objects]
        goods_list = []
        if len(goods_ids) > 0:
            goods_objects = self.session.query(models.Goods) \
                .filter(models.Goods.id.in_(goods_ids),
                        models.Goods.station_id == self.current_station.id,
                        models.Goods.status == 0) \
                .all()
            goods_list = [{"goods_id": goods.id, "goods_name": goods.name} for goods in goods_objects]

        has_more = len(stock_outin_record_objects) >= limit
        return self.send_success(stock_outin_record_list=stock_outin_record_list, goods_list=goods_list, has_more=has_more)


# 仓库库存列表
class WarehouseStockList(StationBaseHandler):
    @BaseHandler.check_arguments("page?:int", "limit?:int", "search?:str", "goods_ids?:str",
                                 "order_by?:str", "asc?:bool")
    def get(self):
        page = self.args.get("page", 0)
        limit = self.args.get("limit", constants.PAGE_SIZE)
        if limit > constants.PAGE_MAX_LIMIT:
            limit = constants.PAGE_SIZE
        search = self.args.get("search", "").strip()
        goods_ids = self.args.get("goods_ids")
        order_by = self.args.get("order_by")
        asc = self.args.get("asc", False)

        station = self.current_station
        query_set = self.session.query(models.Goods)\
            .filter(models.Goods.station_id == station.id,
                    models.Goods.status == 0)
        if search:
            query_set = query_set.filter(models.Goods.code == search)
        if goods_ids:
            goods_ids = [check_int(goods_id)for goods_id in goods_ids.split("|")]
            query_set = query_set.filter(models.Goods.id.in_(goods_ids))

        if order_by == "code":
            if asc:
                query_set = query_set.order_by(models.Goods.code.asc())
            else:
                query_set = query_set.order_by(models.Goods.code.desc())
        elif order_by == "stock":
            if asc:
                query_set = query_set.order_by(models.Goods.stock.asc())
            else:
                query_set = query_set.order_by(models.Goods.stock.desc())
        elif order_by == "stock_average_price":
            if asc:
                query_set = query_set.order_by(models.Goods.stock_average_price.asc())
            else:
                query_set = query_set.order_by(models.Goods.stock_average_price.desc())
        elif order_by == "stock_cost":
            if asc:
                query_set = query_set.order_by(models.Goods.stock_cost.asc())
            else:
                query_set = query_set.order_by(models.Goods.stock_cost.desc())

        stock_goods_objects = query_set.offset(page * limit)\
                                       .limit(limit)\
                                       .all()
        stock_goods_list = list()
        for stock_goods in stock_goods_objects:
            data = stock_goods.to_stock_dict()
            # 根据权限查看仓库库存均价和采购成本
            staff_permission_list = self.current_staff.admin_permission_list
            is_permission = 10 in staff_permission_list
            if not ((self.current_staff.super_admin_status or self.current_staff.admin_status) and is_permission):
                data["stock_average_price"] = 0
                data["stock_cost"] = 0
            stock_goods_list.append(data)
        # 所有商品信息(搜索使用)
        goods_objects = self.session.query(models.Goods)\
                            .filter(models.Goods.station_id == self.current_station.id,
                                    models.Goods.status == 0)\
                            .all()
        goods_list = [{"goods_id": goods.id, "goods_name": goods.name} for goods in goods_objects]
        has_more = len(stock_goods_objects) >= limit
        return self.send_success(stock_goods_list=stock_goods_list, goods_list=goods_list, has_more=has_more)


# 商品库存查询
class GoodsStocks(StationBaseHandler):
    @BaseHandler.check_arguments("goods_ids:str")
    def get(self):
        goods_ids = set(self.args["goods_ids"].split("|")) - {0} - {"0"}
        goods_list = models.Goods.get_by_ids(self.session, goods_ids, self.current_station.id)
        goods_stock_dict = {goods.id: check_float(goods.stock / 100) for goods in goods_list}
        return self.send_success(stock_data=goods_stock_dict)


# 仓库库存处理
class WarehouseStock(StationBaseHandler):
    @BaseHandler.check_arguments("stock:float", "remarks?:str")
    def put(self, goods_id):
        accountinfo = self.current_user
        station = self.current_station
        stock = self.args["stock"]
        remarks = self.args.get("remarks", "").strip()
        if stock >= 2147483600:
            return self.send_fail("库存值过大")
        if stock < 0:
            return self.send_fail("库存不能为负数")
        if len(remarks) > constants.REMARKS_LEN:
            return self.send_fail("备注长度超过128位")
        goods = models.Goods.get_by_goods_id(self.session, goods_id)
        if not goods:
            return self.send_fail("此商品不存在")

        # 生成修改记录
        stock_operation_record = models.StockOperationRecord(
            operation_detail="库存修改({0}→{1})".format(check_float(goods.stock / 100), check_float(stock)),
            remarks=remarks,
            goods_id=goods_id,
            creator_id=accountinfo.id,
            station_id=station.id
        )
        # 更新库存成本
        goods.stock_cost += check_float((stock * 100 - goods.stock) * goods.stock_average_price / 100)
        # 修改库存
        goods.stock = check_int(stock * 100)
        self.session.add(stock_operation_record)
        self.session.commit()
        return self.send_success()


# 库存操作记录
class StockOperationRecord(StationBaseHandler):
    @BaseHandler.check_arguments("page?:int", "limit?:int")
    def get(self):
        page = self.args.get("page", 0)
        limit = self.args.get("limit", constants.PAGE_SIZE)
        if limit > constants.PAGE_MAX_LIMIT:
            limit = constants.PAGE_SIZE
        station = self.current_station
        query_set = self.session.query(models.StockOperationRecord)\
                                .join(models.Goods, models.Goods.id == models.StockOperationRecord.goods_id)
        operation_record_objects = query_set.filter(models.StockOperationRecord.station_id == station.id)\
                                            .order_by(models.StockOperationRecord.create_time.desc())\
                                            .offset(page * limit)\
                                            .limit(limit)\
                                            .all()
        operation_record_list = list()
        for operation_record in operation_record_objects:
            data = operation_record.to_dict()
            operation_record_list.append(data)
        has_more = len(operation_record_objects) >= limit
        return self.send_success(operation_record_list=operation_record_list, has_more=has_more)
