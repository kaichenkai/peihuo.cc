# -*- coding:utf-8 -*-
import datetime
import sqlalchemy
from collections import defaultdict

from sqlalchemy import func, and_

from dal import models
from handlers.base.pub_func import check_int, TimeFunc, check_float
from handlers.base.pub_receipt import ReceiptPrinter
from handlers.base.pub_web import StationBaseHandler
from handlers.base.webbase import BaseHandler


# 分车单
class AllocationOrder(StationBaseHandler):
    def get(self, order_id):
        allocation_order = models.AllocationOrder.get_by_id(self.session, order_id, self.current_station.id)
        if not allocation_order:
            return self.send_fail("没有找到对应的分车单")
        elif not allocation_order.purchase_order_goods_id:
            return self.send_fail("没有找到有效的供货商分车单")
        elif allocation_order.status != 1:
            return self.send_fail("对应的分车单还未被确认")

        allocated_amount = self.session.query(func.sum(models.AllocationOrderGoods.actual_allocated_amount)) \
            .filter(models.AllocationOrderGoods.order_id == allocation_order.id) \
            .first()
        allocated_amount = allocated_amount[0] or 0 if allocated_amount else 0

        # 采购分车记录
        if allocation_order.purchase_order_goods_id:
            purchase_goods = models.PurchaseOrderGoods.get_by_id(self.session, allocation_order.purchase_order_goods_id,
                                                                 self.current_station.id)
            if not purchase_goods:
                return self.send_fail("没有找到对应的采购单商品")

            goods_name = purchase_goods.goods.name
            firm_name = purchase_goods.firm.name
        # 仓库分车记录
        elif allocation_order.stock_out_record_id:
            stock_out_record = models.StockOutInGoods.get_by_id(self.session,
                                                                allocation_order.stock_out_record_id,
                                                                self.current_station,
                                                                [3, 4])
            if not stock_out_record:
                return self.send_fail("没有找到对应的出库记录")
            goods_name = stock_out_record.goods.name
            firm_name = "仓库"
        else:
            return self.send_fail("分车单类型未知")

        data = {
            "id": allocation_order.id,
            "goods_name": goods_name,
            "firm_name": firm_name,
            "order_no": allocation_order.order_no,
            "amount": check_float(allocated_amount / 100),
        }
        return self.send_success(data=data)

    def validate_allocation_list(self, allocation_list):
        """校验分车列表参数"""
        if not isinstance(allocation_list, list):
            return False, "分车列表参数格式有误"

        for allocation in allocation_list:
            if not isinstance(allocation, dict):
                return False, "商品列表参数项格式有误"

            if "shop_id" not in allocation:
                return False, "参数缺失：shop_id"
            if "shop_name" not in allocation:
                return False, "参数缺失：shop_name"
            if "destination" not in allocation:
                return False, "参数缺失：destination"
            elif check_int(allocation["destination"]) not in {0, 1, 2}:
                return False, "参数无效：destination == {}".format(allocation["destination"])
            allocating_amount = allocation.get("allocating_amount")
            if allocating_amount:
                try:
                    allocating_amount = float(allocating_amount)
                except:
                    return self.send_fail("allocating_amount 格式有误: {}".format(allocating_amount))

        return True, ""

    @BaseHandler.check_arguments("firm_name:str",
                                 "purchase_goods_id?:int", "stock_out_record_id?:int",
                                 "allocate_list:list")
    def post(self):
        firm_name = self.args["firm_name"]
        purchase_goods_id = self.args.get("purchase_goods_id")
        stock_out_record_id = self.args.get("stock_out_record_id")
        allocation_list = self.args["allocate_list"]

        valid, message = self.validate_allocation_list(allocation_list)
        if not valid:
            return self.send_fail(message)

        config = models.Config.get_by_station_id(self.session, self.current_station.id)
        printer_id = config.allocation_printer_id
        copies = config.allocation_print_copies

        printer = models.Printer.get_by_id(self.session, printer_id, self.current_station.id)
        if not printer:
            return self.send_fail("分车单打印机设置无效，请在中转站设置中配置")

        # 采购分车单
        if purchase_goods_id:
            purchase_goods = models.PurchaseOrderGoods.get_by_id(self.session, purchase_goods_id, self.current_station.id)
            if not purchase_goods:
                return self.send_fail("没有找到 {} 的对应采购单商品".format(firm_name))

            goods = purchase_goods.goods
            goods_id = goods.id
            goods_name = goods.name
            firm_name = purchase_goods.firm.name
            number_map = models.SerialNumberMap.generate(self.session, 5, purchase_goods.id, self.current_station.id)
            wish_order_id = purchase_goods.order.wish_order_id

        # 出库分车单
        elif stock_out_record_id:
            stock_out_record = models.StockOutInGoods.get_by_id(self.session, stock_out_record_id, self.current_station.id)
            if not stock_out_record:
                return self.send_fail("没有找到 {} 的对应出库记录".format(firm_name))
            elif stock_out_record.status < 3:
                return self.send_fail("{} 的商品还没有确认出库".format(firm_name))

            goods = stock_out_record.goods
            goods_id = goods.id
            goods_name = goods.name
            firm_name = "仓库"
            number_map = models.SerialNumberMap.generate(self.session, 6, stock_out_record.id, self.current_station.id)
            wish_order_id = stock_out_record.wish_order_id

        else:
            return self.send_fail("参数错误：purchase_goods_id 和 stock_out_record_id 必选其一")

        # 创建分车订单
        new_allocation_order = models.AllocationOrder(
            wish_order_id=wish_order_id,
            purchase_order_goods_id=purchase_goods_id,
            stock_out_record_id=stock_out_record_id,
            order_no=number_map.order_no,
            creator_id=self.current_user.id,
            station_id=self.current_station.id,
            goods_id=goods_id,
        )
        self.session.add(new_allocation_order)
        self.session.flush()
        # 配送部分
        total_amount = 0
        for allocate_item in allocation_list:
            shop_id = allocate_item["shop_id"]
            shop_name = allocate_item["shop_name"]
            destination = allocate_item["destination"]
            allocated_amount = check_float(allocate_item.get("allocating_amount", 0))
            total_amount += allocated_amount

            if allocated_amount:
                allocated_amount = check_int(allocated_amount * 100)
                new_allocation_goods = models.AllocationOrderGoods(
                    order_id=new_allocation_order.id,
                    shop_id=shop_id or None,
                    destination=destination,
                    allocated_amount=allocated_amount,
                    actual_allocated_amount=allocated_amount,
                )
                self.session.add(new_allocation_goods)

        self.session.commit()

        # 打印分车单据
        receipt_printer = ReceiptPrinter(printer.wireless_print_num, printer.wireless_print_key)
        receipt_content = receipt_printer.allocation_order_template(
            goods_name=goods_name,
            firm_name=firm_name,
            order_no=number_map.order_no,
            total_amount=total_amount,
            allocation_list=allocation_list,
            operator_name=self.current_user.username,
            create_time=TimeFunc.time_to_str(datetime.datetime.now()),
        )
        for i in range(copies):
            success, error_msg = receipt_printer.print(receipt_content)
            if not success:
                return self.send_fail(error_msg)

        return self.send_success()

    @BaseHandler.check_arguments("action:str")
    def put(self, order_id):
        action = self.args["action"]

        if action == "confirm":
            return self.confirm(order_id)
        elif action == "update_goods_list":
            return self.update_goods_list(order_id)
        elif action == "update_remarks":
            return self.update_remarks(order_id)
        else:
            return self.send_fail("action invalid")

    @BaseHandler.check_arguments("remarks:str")
    def update_remarks(self, order_id):
        remarks = self.args["remarks"]

        order = models.AllocationOrder.get_by_id(self.session, order_id, self.current_station.id)
        if not order:
            return self.send_fail("没有找到该分车单")

        order.remarks = remarks
        self.session.commit()
        return self.send_success()

    @BaseHandler.check_arguments("goods_list:list", "amount_other_dest?:float", "amount_stock_in?:float")
    def update_goods_list(self, order_id):
        """ 更新分车单货品列表 """
        goods_list = self.args["goods_list"]
        amount_other_dest = self.args.get("amount_other_dest")
        amount_stock_in = self.args.get("amount_stock_in")

        valid, message = self.validate_goods_list(goods_list)
        if not valid:
            return self.send_fail(message)

        order = models.AllocationOrder.get_by_id(self.session, order_id, self.current_station.id)
        if not order:
            return self.send_fail("没有找到该分车单")

        order_goods_list = order.goods_list.all()
        order_goods_dict = {}
        order_goods_other = None
        order_goods_stock_in = None
        for goods in order_goods_list:
            # 目前入库分车单货品和其他目标分车单货品只能有一个
            if goods.destination == 0:
                order_goods_dict[goods.id] = goods
            elif goods.destination == 1:
                order_goods_stock_in = goods
            elif goods.destination == 2:
                order_goods_other = goods

        # 更新已有的分车单货品
        for goods_param in goods_list:
            order_goods_id = check_int(goods_param["id"])
            allocated_amount = check_float(goods_param["allocated_amount"])
            order_goods = order_goods_dict[order_goods_id]
            order_goods.actual_allocated_amount = check_int(allocated_amount * 100)

        # 其他目标的分车单货品
        if amount_other_dest is not None:
            amount_other_dest = check_int(amount_other_dest * 100)
            if not order_goods_other:
                order_goods_other = models.AllocationOrderGoods(
                    destination=2,
                    allocated_amount=amount_other_dest,
                    order_id=order.id,
                )
                self.session.add(order_goods_other)
            order_goods_other.actual_allocated_amount = amount_other_dest

        # 入库的分车单货品
        if amount_stock_in is not None:
            amount_stock_in = check_int(amount_stock_in * 100)
            if not order_goods_stock_in:
                order_goods_stock_in = models.AllocationOrderGoods(
                    destination=1,
                    allocated_amount=amount_stock_in,
                    order_id=order.id,
                )
                self.session.add(order_goods_stock_in)
            order_goods_stock_in.actual_allocated_amount = amount_stock_in

        self.session.commit()
        return self.send_success()

    def validate_goods_list(self, goods_list):
        """验证商品列表参数"""

        if not isinstance(goods_list, list):
            return False, "商品列表参数格式有误"

        for goods in goods_list:
            if not isinstance(goods, dict):
                return False, "商品列表参数项格式有误"

            if "id" not in goods:
                return False, "参数缺失：id"
            if "allocated_amount" not in goods:
                return False, "参数缺失：allocated_amount"
            elif check_float(goods["allocated_amount"]) >= 2147483600:
                return False, "实配量过大：{}".format(goods["allocated_amount"])

        # 有没有无效的分车单货品 ID
        order_goods_ids = {check_int(goods["id"]) for goods in goods_list}
        valid_goods_list = models.AllocationOrderGoods.get_by_ids(self.session, order_goods_ids)
        valid_goods_ids = {goods.id for goods in valid_goods_list}
        if order_goods_ids != valid_goods_ids:
            return False, "存在无效的分车单货品"

        return True, ""

    @BaseHandler.check_arguments("remarks?:str")
    def confirm(self, order_id):
        """ 确认分车 """
        remarks = self.args.get("remarks", "")

        order = models.AllocationOrder.get_by_id(self.session, order_id, self.current_station.id)
        if not order:
            return self.send_fail("没有找到该分车单")
        elif order.status == 1:
            return self.send_fail("该分车单已经被确认过了")

        order.status = 1
        order.remarks = remarks
        self.session.flush()

        # 采购分车单确认后更新门店配货价
        self.update_shop_packing_price(order)

        self.session.commit()
        return self.send_success()

    def update_shop_packing_price(self, order):
        """更新分车目标门店的商品配货价"""
        if order.purchase_order_goods_id:
            # 分车目标门店
            allocated_shops = self.session.query(models.AllocationOrderGoods.shop_id) \
                .filter(models.AllocationOrderGoods.destination == 0,
                        models.AllocationOrderGoods.order_id == order.id) \
                .all()
            allocated_shops = {shop[0] for shop in allocated_shops}

            # 重新计算各门店的采购价
            purchase_data = self.session.query(models.AllocationOrderGoods.shop_id,
                                               func.sum(models.AllocationOrderGoods.actual_allocated_amount).label("allocated_amount"),
                                               func.sum(models.PurchaseOrderGoods.subtotal).label("subtotal"),
                                               func.sum(models.PurchaseOrderGoods.actual_amount).label("actual_amount")) \
                .join(models.AllocationOrder) \
                .outerjoin(models.PurchaseOrderGoods, models.PurchaseOrderGoods.id == models.AllocationOrder.purchase_order_goods_id) \
                .filter(models.AllocationOrder.wish_order_id == order.wish_order_id,
                        models.AllocationOrder.status == 1,
                        models.AllocationOrder.goods_id == order.goods_id,
                        models.AllocationOrderGoods.shop_id.in_(allocated_shops)) \
                .group_by(models.AllocationOrderGoods.shop_id) \
                .all()
            purchase_price_dict = {data.shop_id: (data.subtotal or 0) / (data.actual_amount or 1)
                                   for data in purchase_data}
            allocated_amount_dict = {data.shop_id: data.allocated_amount for data in purchase_data}

            # 已有的配货价数据
            packing_price_list = self.session.query(models.ShopPackingPrice) \
                .filter(models.ShopPackingPrice.goods_id == order.goods_id,
                        models.ShopPackingPrice.station_id == self.current_station.id,
                        models.ShopPackingPrice.wish_order_id == order.wish_order_id,
                        models.ShopPackingPrice.shop_id.in_(allocated_shops)) \
                .all()
            packing_price_dict = {packing_price.shop_id: packing_price for packing_price in packing_price_list}

            # 更新各门店配货价
            for shop_id in allocated_shops:
                packing_price = packing_price_dict.get(shop_id)
                if not packing_price:
                    packing_price = models.ShopPackingPrice(
                        station_id=self.current_station.id,
                        creator_id=self.current_user.id,
                        wish_order_id=order.wish_order_id,
                        shop_id=shop_id,
                        goods_id=order.goods_id,
                    )
                    self.session.add(packing_price)
                # 直接覆盖为采购价
                purchase_price = purchase_price_dict.get(shop_id, 0)
                packing_price.price = check_int(purchase_price * 100)
                # 更新总配货量
                allocated_amount = allocated_amount_dict.get(shop_id, 0)
                packing_price.allocated_amount = allocated_amount


# 单品分车记录列表
class GoodsAllocationList(StationBaseHandler):
    @BaseHandler.check_arguments("wish_order_id:int", "goods_id:int")
    def get(self):
        wish_order_id = self.args["wish_order_id"]
        goods_id = self.args["goods_id"]

        wish_order = models.WishOrder.get_by_id(self.session, wish_order_id, self.current_station.id)
        if not wish_order:
            return self.send_fail("没有找到对应的意向单")

        wish_goods = wish_order.goods_list \
            .filter(models.WishOrderGoods.status >= 0,
                    models.WishOrderGoods.goods_id == goods_id) \
            .first()

        demand_goods_order = self.session.query(models.DemandOrderGoods, models.DemandOrder) \
            .join(models.DemandOrder, models.DemandOrder.id == models.DemandOrderGoods.demand_order_id) \
            .filter(models.DemandOrder.wish_order_id == wish_order_id,
                    models.DemandOrderGoods.goods_id == goods_id,
                    models.DemandOrderGoods.status == 0) \
            .all()
        demand_goods_dict = {order.shop_id: goods for goods, order in demand_goods_order}
        demand_status_dict = {order.shop_id: order.negative_order for _, order in demand_goods_order}

        allocation_goods_list = self.session.query(models.AllocationOrderGoods) \
            .join(models.AllocationOrder, models.AllocationOrder.id == models.AllocationOrderGoods.order_id) \
            .filter(models.AllocationOrder.wish_order_id == wish_order_id,
                    models.AllocationOrder.goods_id == goods_id) \
            .all()
        # 计算各店铺配货总量
        allocation_sum_dict = defaultdict(int)
        stock_in_sum = 0
        other_sum = 0
        for allocation_goods in allocation_goods_list:
            if allocation_goods.destination == 0:
                allocation_sum_dict[allocation_goods.shop_id] += allocation_goods.actual_allocated_amount
            elif allocation_goods.destination == 1:
                stock_in_sum += allocation_goods.actual_allocated_amount
            elif allocation_goods.destination == 2:
                other_sum += allocation_goods.actual_allocated_amount

        shops = models.Shop.get_by_station_id(self.session, self.current_station.id)
        data_list = []
        storage_sum = 0
        demand_amount_sum = 0
        allocated_amount_sum = 0
        for shop in shops:
            # 订货信息
            demand_goods = demand_goods_dict.get(shop.id)
            negative_order = demand_status_dict.get(shop.id, 0)
            current_storage = check_float(demand_goods.current_storage / 100) if demand_goods else 0  # TODO 这次没订货的应该要取上一次订货的库存量
            if demand_goods and demand_goods.modified_demand_amount is not None:
                demand_amount = check_float(demand_goods.modified_demand_amount / 100)
            elif demand_goods:
                demand_amount = check_float(demand_goods.demand_amount / 100)
            else:
                demand_amount = None
            # 配货信息
            allocated_amount = check_float(allocation_sum_dict.get(shop.id, 0) / 100)
            # 排序优先级，有订货的门店按 ID 升序靠前，未订货的按 ID 升序排在 0 以下
            priority = shop.id if shop.id in demand_goods_dict else shop.id - 99999
            # 累计值
            storage_sum += current_storage
            demand_amount_sum += demand_amount if demand_amount else 0
            allocated_amount_sum += allocated_amount

            data = {
                "shop_id": shop.id,
                "shop_name": shop.abbreviation,
                "destination": 0,
                "current_storage": current_storage,
                "demand_amount": demand_amount,
                "allocated_amount": allocated_amount,
                "priority": priority,
                "negative_order": negative_order
            }
            data_list.append(data)

        # 仓库分车信息
        warehouse_storage = check_float(wish_goods.confirmed_storage / 100) if wish_goods else 0
        warehousing_amount = check_float(stock_in_sum / 100)
        storage_sum += warehouse_storage
        allocated_amount_sum += warehousing_amount
        data_list.append({
            "shop_id": 0,
            "shop_name": "仓库",
            "destination": 1,
            "current_storage": warehouse_storage,
            "demand_amount": 0,
            "allocated_amount": warehousing_amount,
            "priority": -1,
            "negative_order": 0
        })

        # 其他分车信息
        other_allocated_amount = check_float(other_sum / 100)
        allocated_amount_sum += other_allocated_amount
        if other_allocated_amount:
            data_list.append({
                "shop_id": 0,
                "shop_name": "其他",
                "destination": 2,
                "current_storage": 0,
                "demand_amount": 0,
                "allocated_amount": other_allocated_amount,
                "priority": 0,
                "negative_order": 0
            })

        # 按优先级排序
        data_list = sorted(data_list, key=lambda d: d["priority"], reverse=True)

        shop_order = {"仓库": -999, "总部": 1, "刘园": 2, "侯台": 3,
                      "咸水沽": 4, "华明": 5,
                      "大港": 6, "杨村": 7, "新立": 8, "大寺": 9, "汉沽": 10,
                      "沧州": 11, "静海": 13, "芦台": 14, "工农村": 15, "唐山": 16, "廊坊": 17,
                      "哈尔滨": 18, "西青道": 19, "双鸭山": 20, "承德": 21,
                      "张胖子": 22, "固安": 23, "燕郊": 24, "胜芳": 25, "蓟县": 26, }
        data_list = sorted(data_list, key=lambda d: shop_order.get(d["shop_name"], 999))

        sum_data = {
            "total_storage": check_float(storage_sum),
            "total_demand_amount": check_float(demand_amount_sum),
            "total_allocated_amount": check_float(allocated_amount_sum),
        }

        return self.send_success(sum_data=sum_data, data_list=data_list)


# 分车记录列表
class AllocationRecordList(StationBaseHandler):
    @BaseHandler.check_arguments("wish_order_id:int", "goods_id:int")
    def get(self):
        wish_order_id = self.args["wish_order_id"]
        goods_id = self.args["goods_id"]

        wish_order = models.WishOrder.get_by_id(self.session, wish_order_id, self.current_station.id)
        if not wish_order:
            return self.send_fail("没有找到对应的意向单")

        orders = self.session.query(models.AllocationOrder, models.PurchaseOrderGoods) \
            .outerjoin(models.PurchaseOrderGoods, models.PurchaseOrderGoods.id == models.AllocationOrder.purchase_order_goods_id) \
            .filter(models.AllocationOrder.station_id == self.current_station.id,
                    models.AllocationOrder.wish_order_id == wish_order_id,
                    models.AllocationOrder.goods_id == goods_id) \
            .order_by(models.AllocationOrder.create_time.desc()) \
            .all()

        order_ids = {order.id for order, _ in orders}
        order_goods_list = self.session.query(models.AllocationOrderGoods) \
            .filter(models.AllocationOrderGoods.order_id.in_(order_ids)) \
            .all()

        demand_goods_order = self.session.query(models.DemandOrderGoods, models.DemandOrder) \
            .join(models.DemandOrder, models.DemandOrder.id == models.DemandOrderGoods.demand_order_id) \
            .filter(models.DemandOrder.wish_order_id == wish_order_id,
                    models.DemandOrderGoods.goods_id == goods_id,
                    models.DemandOrderGoods.status == 0) \
            .all()
        demand_goods_dict = {order.shop_id: goods for goods, order in demand_goods_order}

        shop_ids = {goods.shop_id for goods in order_goods_list}
        shops = models.Shop.get_by_ids(self.session, shop_ids, self.current_station.id)
        shop_dict = {shop.id: shop for shop in shops}

        order_goods_dict = defaultdict(list)
        order_goods_sum_dict = {}
        for order_goods in order_goods_list:
            demand_goods = demand_goods_dict.get(order_goods.shop_id)
            demand_amount = (demand_goods.modified_demand_amount or demand_goods.demand_amount) if demand_goods else 0
            current_storage = demand_goods.current_storage if demand_goods else 0

            if order_goods.destination == 0:
                shop_name = shop_dict.get(order_goods.shop_id).abbreviation
            elif order_goods.destination == 1:
                shop_name = "仓库"
            else:
                shop_name = "其他"
            order_goods_dict[order_goods.order_id].append({
                "shop_name": shop_name,
                "storage": check_float(current_storage / 100),
                "demand_amount": check_float(demand_amount / 100),
                "allocated_amount": check_float(order_goods.actual_allocated_amount / 100),
            })

            if order_goods.order_id not in order_goods_sum_dict:
                order_goods_sum_dict[order_goods.order_id] = {
                    "storage": 0,
                    "demand_amount": 0,
                    "allocated_amount": 0,
                }
            order_goods_sum_dict[order_goods.order_id]["storage"] += current_storage
            order_goods_sum_dict[order_goods.order_id]["demand_amount"] += demand_amount
            order_goods_sum_dict[order_goods.order_id]["allocated_amount"] += order_goods.actual_allocated_amount

        data_list = []
        for order, purchase_order_goods in orders:
            order_goods_sum = order_goods_sum_dict.get(order.id, {})
            data_list.append({
                "order_id": order.id,
                "create_time": TimeFunc.time_to_str(order.create_time),
                "order_no": order.order_no,
                "source": purchase_order_goods.firm.name if purchase_order_goods else "仓库",
                "storage": check_float(order_goods_sum.get("storage", 0) / 100),
                "demand_amount": check_float(order_goods_sum.get("demand_amount", 0) / 100),
                "allocated_amount": check_float(order_goods_sum.get("allocated_amount", 0) / 100),
                "status": order.status,
                "order_goods_list": order_goods_dict.get(order.id, []),
            })

        return self.send_success(data_list=data_list)


# 分车单商品列表
class AllocationOrderGoodsList(StationBaseHandler):
    @BaseHandler.check_arguments("shop_id?:int", "from_date?:date", "to_date?:date", "before_date?:date", "order_status?:int",
                                 "order_by?:str", "asc?:bool",
                                 "page?:int", "limit?:int")
    def get(self):
        shop_id = self.args.get("shop_id")
        from_date = self.args.get("from_date")
        to_date = self.args.get("to_date")
        before_date = self.args.get("before_date")
        order_status = self.args.get("order_status")
        order_by = self.args.get("order_by")
        asc = self.args.get("asc", False)
        page = self.args.get("page", 0)
        limit = self.args.get("limit", 20)

        goods_list = self.session.query(models.AllocationOrderGoods, models.Goods, models.AllocationOrder, models.ShopPackingPrice) \
            .join(models.AllocationOrder) \
            .join(models.Goods, models.Goods.id == models.AllocationOrder.goods_id) \
            .outerjoin(models.ShopPackingPrice, and_(models.ShopPackingPrice.wish_order_id == models.AllocationOrder.wish_order_id,
                                                     models.ShopPackingPrice.goods_id == models.AllocationOrder.goods_id,
                                                     models.ShopPackingPrice.shop_id == models.AllocationOrderGoods.shop_id)) \
            .filter(models.AllocationOrder.station_id == self.current_station.id)

        if shop_id is not None:
            goods_list = goods_list.filter(models.AllocationOrderGoods.shop_id == shop_id)

        if order_status is not None:
            goods_list = goods_list.filter(models.AllocationOrder.status == order_status)

        if from_date:
            goods_list = goods_list.filter(func.DATE(models.AllocationOrderGoods.create_time) >= from_date)
        if to_date:
            goods_list = goods_list.filter(func.DATE(models.AllocationOrderGoods.create_time) <= to_date)
        if before_date:
            goods_list = goods_list.filter(func.DATE(models.AllocationOrderGoods.create_time) < before_date)

        sum_data = goods_list.with_entities(func.sum(models.AllocationOrderGoods.actual_allocated_amount).label("allocated_amount"),
                                            func.sum(models.AllocationOrderGoods.actual_allocated_amount
                                                     * models.ShopPackingPrice.price).label("packing_money"),
                                            func.sum(models.Goods.standards_volume
                                                     * models.AllocationOrderGoods.actual_allocated_amount).label("volume"),
                                            func.sum(models.Goods.standards_weight
                                                     * models.AllocationOrderGoods.actual_allocated_amount).label("weight")) \
            .first()

        if order_by == "allocated_amount":
            if asc:
                goods_list = goods_list.order_by(models.AllocationOrderGoods.actual_allocated_amount.asc())
            else:
                goods_list = goods_list.order_by(models.AllocationOrderGoods.actual_allocated_amount.desc())
        elif order_by == "packing_price":
            if asc:
                goods_list = goods_list.order_by(models.ShopPackingPrice.price.asc())
            else:
                goods_list = goods_list.order_by(models.ShopPackingPrice.price.desc())
        elif order_by == "packing_money":
            if asc:
                goods_list = goods_list.order_by(sqlalchemy.asc(models.AllocationOrderGoods.actual_allocated_amount
                                                                * models.ShopPackingPrice.price))
            else:
                goods_list = goods_list.order_by(sqlalchemy.desc(models.AllocationOrderGoods.actual_allocated_amount
                                                                 * models.ShopPackingPrice.price))
        elif order_by == "goods_volume":
            if asc:
                goods_list = goods_list.order_by(models.Goods.standards_volume.asc())
            else:
                goods_list = goods_list.order_by(models.Goods.standards_volume.desc())
        elif order_by == "goods_weight":
            if asc:
                goods_list = goods_list.order_by(models.Goods.standards_weight.asc())
            else:
                goods_list = goods_list.order_by(models.Goods.standards_weight.desc())

        goods_list = goods_list.offset(page * limit) \
            .limit(limit) \
            .all()

        data_list = []
        for order_goods, goods, order, packing_price in goods_list:
            data_list.append({
                "id": order_goods.id,
                "goods_name": goods.name,
                "allocated_amount": check_float(order_goods.actual_allocated_amount / 100),
                "packing_price": check_float(packing_price.price / 100) if packing_price else 0,
                "packing_money": check_float(packing_price.price * order_goods.actual_allocated_amount / 10000) if packing_price else 0,
                "goods_volume": check_float(goods.standards_volume * order_goods.actual_allocated_amount / 10000),
                "goods_weight": check_float(goods.standards_weight * order_goods.actual_allocated_amount / 10000),
            })

        sum_data = {
            "allocated_amount": check_float((sum_data.allocated_amount or 0) / 100) if sum_data else 0,
            "packing_money": check_float((sum_data.packing_money or 0) / 10000) if sum_data else 0,
            "goods_volume": check_float((sum_data.volume or 0) / 10000) if sum_data else 0,
            "goods_weight": check_float((sum_data.weight or 0) / 10000) if sum_data else 0,
        }

        has_more = len(data_list) >= limit
        return self.send_success(data_list=data_list, sum_data=sum_data, has_more=has_more)
