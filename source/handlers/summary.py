# -*- coding:utf-8 -*-
from collections import defaultdict
from functools import reduce
from sqlalchemy import func
from dal import models
from dal.db_configs import redis
from dal.redis_keys import KEY_DEMAND_ORDER_UPDATE_NOTIFICATIONS, KEY_PURCHASING_DYNAMICS_NOTIFICATIONS
from handlers.base.pub_func import check_float, is_int, is_number, check_int, TimeFunc
from handlers.base.pub_web import StationBaseHandler
from handlers.base.webbase import BaseHandler


# 汇总单
class SummaryTable(StationBaseHandler):
    @BaseHandler.check_arguments("wish_order_id:int", "goods_ids?:str")
    def get(self):
        wish_order_id = self.args["wish_order_id"]
        goods_ids_filter = self.args.get("goods_ids")
        if goods_ids_filter is not None:
            goods_ids_filter = list(map(lambda i: check_int(i), goods_ids_filter.split("|")))

        wish_order = models.WishOrder.get_by_id(self.session, wish_order_id, self.current_station.id)
        if not wish_order:
            return self.send_fail("没有找到指定的意向单")
        if wish_order.status <= 1:
            return self.send_fail("意向单还未提交")

        all_wish_goods = self.session.query(models.WishOrderGoods)\
            .filter(models.WishOrderGoods.wish_order_id == wish_order_id,
                    models.WishOrderGoods.status >= 0)\
            .all()
        wish_goods_dict = {wish_goods.goods_id: wish_goods for wish_goods in all_wish_goods}

        all_demand_goods = self.session.query(models.DemandOrderGoods) \
            .join(models.DemandOrder, models.DemandOrder.id == models.DemandOrderGoods.demand_order_id) \
            .filter(models.DemandOrder.status == 2,
                    models.DemandOrderGoods.status == 0,
                    models.DemandOrder.wish_order_id == wish_order_id) \
            .all()

        # 订货总量
        demand_amount_dict = defaultdict(int)
        for demand_goods in all_demand_goods:
            demand_amount_dict["demand_amount{0}".format(demand_goods.goods_id)] += demand_goods.demand_amount
            if demand_goods.modified_demand_amount is not None:
                demand_amount_dict["modified_demand_amount{0}".format(demand_goods.goods_id)] \
                    += demand_goods.modified_demand_amount
                demand_amount_dict["modify_status{0}".format(demand_goods.goods_id)] = 1  # 订单量修改状态
            else:
                demand_amount_dict["modified_demand_amount{0}".format(demand_goods.goods_id)] \
                    += demand_goods.demand_amount
        # 所有采购单货品
        purchase_query_set = self.session.query(models.PurchaseOrderGoods)\
            .join(models.PurchaseOrder, models.PurchaseOrder.id == models.PurchaseOrderGoods.purchase_order_id)\
            .filter(models.PurchaseOrder.wish_order_id == wish_order_id,
                    models.PurchaseOrder.status >= 0,
                    models.PurchaseOrderGoods.status >= 0)
        purchase_goods_list = purchase_query_set.all()
        # 采购单ID(未完成汇总之前采购单不存在)
        purchase_order_id = None
        if wish_order.status >= 3:
            purchase_order_id = purchase_query_set.with_entities(models.PurchaseOrder.id).distinct().scalar()

        purchase_goods_dict = defaultdict(list)
        [purchase_goods_dict[goods.goods_id].append(goods) for goods in purchase_goods_list]

        # 汇总单仓库库存
        goods_storage_list = self.session.query(models.WishOrderGoods.goods_id,
                                                models.WishOrderGoods.confirmed_storage) \
            .filter(models.WishOrderGoods.wish_order_id == wish_order_id,
                    models.WishOrderGoods.status >= 0) \
            .all()
        goods_storage_dict = {goods_id: storage for goods_id, storage in goods_storage_list}

        # 所有调货记录
        stock_out_records = self.session.query(models.StockOutInGoods) \
            .filter(models.StockOutInGoods.station_id == self.current_station.id,
                    models.StockOutInGoods.wish_order_id == wish_order_id,
                    models.StockOutInGoods.status.in_([2, 3, 4])) \
            .all()
        stock_out_record_dict = defaultdict(list)
        [stock_out_record_dict[record.goods_id].append(record) for record in stock_out_records]

        # 所有已确认的分车记录
        allocation_goods_orders = self.session.query(models.AllocationOrderGoods, models.AllocationOrder) \
            .join(models.AllocationOrder, models.AllocationOrder.id == models.AllocationOrderGoods.order_id) \
            .filter(models.AllocationOrder.wish_order_id == wish_order_id,
                    models.AllocationOrder.status == 1) \
            .all()
        allocation_sum_dict = defaultdict(int)
        allocation_orders_dict = defaultdict(set)
        purchase_allocation_dict = defaultdict(list)
        stock_out_allocation_dict = defaultdict(list)
        for allocation_goods, allocation_order in allocation_goods_orders:
            # 实配量
            allocation_sum_dict[allocation_order.goods_id] += allocation_goods.actual_allocated_amount
            # 分车次数
            allocation_orders_dict[allocation_order.goods_id].add(allocation_order.id)
            # 采购分车记录
            if allocation_order.purchase_order_goods_id:
                purchase_allocation_dict[allocation_order.purchase_order_goods_id].append((allocation_goods, allocation_order))
            # 出库分车记录
            if allocation_order.stock_out_record_id:
                stock_out_allocation_dict[allocation_order.stock_out_record_id].append((allocation_goods, allocation_order))

        # 货品种类
        goods_ids = set([goods.goods_id for goods in all_demand_goods]
                        + [goods.goods_id for goods in purchase_goods_list]
                        + [record.goods_id for record in stock_out_records])
        goods_list = models.Goods.get_by_ids(self.session, goods_ids, self.current_station.id)

        # 商品对应采购员的默认设置
        goods_purchaser_configs = self.session.query(models.StaffGoods) \
            .filter(models.StaffGoods.goods_id.in_(goods_ids)) \
            .all()
        goods_purchaser_dict = {item.goods_id: item.staff_id for item in goods_purchaser_configs}
        purchaser_ids = {item.staff_id for item in goods_purchaser_configs}
        goods_purchasers = self.session.query(models.Staff) \
            .filter(models.Staff.id.in_(purchaser_ids),
                    models.Staff.status == 0,
                    models.Staff.station_id == self.current_station.id) \
            .all()
        available_purchaser_ids = {purchaser.id for purchaser in goods_purchasers}

        summary_data = []
        for goods in goods_list:
            goods_id = goods.id
            serial_number = goods.serial_number
            wish_goods = wish_goods_dict.get(goods_id)
            goods_name = wish_goods.goods_name if wish_goods else goods.name
            goods_name_modified = wish_goods.goods_name_modified if wish_goods else 0
            # 仓库库存，以结束汇总开始备货时的库存为最终库存
            if wish_order.status >= 4:
                storage = goods_storage_dict.get(goods_id, 0)
            else:
                storage = goods.stock
            demand_amount = demand_amount_dict.get("demand_amount{0}".format(goods.id), 0)  # 订货总量
            modified_demand_amount = demand_amount_dict.get("modified_demand_amount{0}".format(goods.id), 0)  # 修改后的订货总量
            modify_status = demand_amount_dict.get("modify_status{0}".format(goods.id), 0)  # 订货量修改状态
            purchasing_amount = max(modified_demand_amount - storage, 0)  # 待采购量，库存充足则为 0
            allocating_amount = min(storage, demand_amount)  # 待调出量，库存充足则为订货总量

            purchaser = None

            # 采购信息
            purchase_goods_list = purchase_goods_dict.get(goods.id, [])
            purchase_tag = purchase_goods_list[0].tag if purchase_goods_list else 0  # 采购商品标签
            is_purchase = purchase_goods_list[0].is_purchase if purchase_goods_list else 0  # 采购商品是否不采了
            purchase_data = []
            total_amount = 0
            total_payoff = 0
            for purchase_goods in purchase_goods_list:
                # 应当是同一个采购员
                purchaser = purchase_goods.purchaser
                purchased_amount = purchase_goods.actual_amount
                total_amount += purchased_amount
                price = purchase_goods.price
                subtotal = purchase_goods.subtotal
                total_payoff += subtotal
                payment = purchase_goods.payment

                remarks = purchase_goods.remarks
                firm = purchase_goods.firm
                firm_id = firm.id if firm else 0
                firm_name = firm.name if firm else ""

                # 计算已配货量
                allocation_records = purchase_allocation_dict.get(purchase_goods.id, [])
                allocated_amount = reduce(lambda s, g: s + g[0].actual_allocated_amount, allocation_records, 0)

                purchase_data.append({
                    "purchase_goods_id": purchase_goods.id,  # 采购单商品 ID
                    "purchased_amount": check_float(purchased_amount / 100),  # 实采量
                    "allocated_amount": check_float(allocated_amount / 100),  # 实配量
                    "price": check_float(price / 100),
                    "subtotal": check_float(subtotal / 100),  # 总金额
                    "payment": payment,
                    "remarks": remarks,  # 采购备注
                    "firm_id": firm_id,  # 供货商 ID
                    "firm_name": firm_name,  # 供货商名称
                })

            # 采购均价
            purchase_price = check_float(total_payoff / total_amount) if total_amount > 0 else 0

            # 调货信息
            stock_out_record_list = stock_out_record_dict.get(goods.id, [])
            stock_out_data = []
            for stock_out_record in stock_out_record_list:
                # 计算已配货量
                allocation_records = stock_out_allocation_dict.get(stock_out_record.id, [])
                allocated_amount = reduce(lambda s, g: s + g[0].actual_allocated_amount, allocation_records, 0)

                stock_out_data.append({
                    "record_id": stock_out_record.id,
                    "amount": check_float(stock_out_record.amount / 100),  # 出库量
                    "allocated_amount": check_float(allocated_amount / 100),  # 实配量
                })

            purchaser_id = purchaser.id if purchaser else 0
            # 没有采购员就用以前设置过的采购员
            if not purchaser_id:
                default_purchaser_id = goods_purchaser_dict.get(goods_id)
                if default_purchaser_id in available_purchaser_ids:
                    purchaser_id = default_purchaser_id
                default_staff = models.Staff.get_by_id(self.session, purchaser_id, self.current_station.id)
                if default_staff and default_staff.purchaser_status == 1:
                    purchaser = default_staff
            purchaser_name = purchaser.remarks or purchaser.account.username if purchaser else ""

            if goods_ids_filter is None or goods_id in goods_ids_filter:
                priority = (wish_goods.priority if wish_goods else (10000 + serial_number)) + is_purchase * 100000
                summary_data.append({
                    "goods_id": goods_id,
                    "serial_number": serial_number,
                    "goods_name": goods_name,
                    "goods_name_modified": goods_name_modified,  # 货品名是否被修改过
                    "storage": check_float(storage / 100),  # 仓库库存
                    "demand_amount": check_float(demand_amount / 100),  # 订货总量
                    "modified_demand_amount": check_float(modified_demand_amount / 100),  # 修改后的订货总量
                    "modify_status": modify_status,  # 订货量修改状态
                    "purchasing_amount": check_float(purchasing_amount / 100),  # 待采购
                    "allocating_amount": check_float(allocating_amount / 100),  # 待调出
                    "purchaser_id": purchaser_id,  # 采购员 ID,
                    "purchaser_name": purchaser_name,  # 采购员姓名
                    "purchaser_tag": purchase_tag,  # 采购商品标签
                    "is_purchase": is_purchase,  # 采购商品是否不采了
                    "purchase_price": purchase_price,  # 采购进货价
                    "purchase_data": purchase_data,  # 采购信息
                    "stock_out_data": stock_out_data,  # 调货信息
                    "allocated_amount": check_float(allocation_sum_dict.get(goods_id, 0) / 100),  # 实配量
                    "allocated_times": len(allocation_orders_dict.get(goods_id, set())),  # 已分车次数
                    "priority": priority,  # 优先按「不采了」状态排序，然后按意向单顺序排序，最后按商品序列号
                })

        summary_data = sorted(summary_data, key=lambda x: x["priority"])

        return self.send_success(summary_data=summary_data, wish_order_status=wish_order.status,
                                 purchase_order_id=purchase_order_id)


# 门店订货状态列表
class ShopDemandingList(StationBaseHandler):
    @BaseHandler.check_arguments("wish_order_id:int")
    def get(self):
        wish_order_id = self.args["wish_order_id"]

        wish_order = models.WishOrder.get_by_id(self.session, wish_order_id, self.current_station.id)
        if not wish_order:
            return self.send_fail("没有找到此意向单")

        shops = models.Shop.get_by_station_id(self.session, self.current_station.id)

        demand_orders = models.DemandOrder.get_all_by_wish_order_id(self.session, wish_order_id)
        demand_order_dict = {order.shop_id: order for order in demand_orders}
        demand_status_dict = {order.shop_id: order.negative_order for order in demand_orders}

        demand_order_ids = {order.id for order in demand_orders}

        demand_goods_objects = self.session.query(models.DemandOrderGoods, models.WishOrderGoods, models.Goods)\
            .join(models.WishOrderGoods)\
            .join(models.Goods)\
            .filter(models.DemandOrderGoods.demand_order_id.in_(demand_order_ids),
                    models.DemandOrderGoods.status == 0)\
            .all()
        # 订货数量、预采数量、预采体积、预采重量
        demand_amount_dict = defaultdict(int)
        purchasing_amount_dict = defaultdict(int)
        purchasing_volume_dict = defaultdict(int)
        purchasing_weight_dict = defaultdict(int)
        for demand_goods, wish_goods, goods in demand_goods_objects:
            if demand_goods.modified_demand_amount is not None:
                demand_amount = demand_goods.modified_demand_amount
            else:
                demand_amount = demand_goods.demand_amount
            demand_amount_dict[demand_goods.demand_order_id] += demand_amount
            if wish_goods.status == 0:
                standards_volume = float(goods.standards_volume)
                standards_weight = goods.standards_weight
                # 对应的意向商品状态为可要货的前提下才有预采量
                purchasing_amount_dict[demand_goods.demand_order_id] += demand_amount
                purchasing_volume_dict[demand_goods.demand_order_id] += \
                    float(demand_amount) * standards_volume
                purchasing_weight_dict[demand_goods.demand_order_id] += \
                    demand_amount * standards_weight

        # 所有已确认的分车记录
        allocated_amount = self.session.query(models.AllocationOrderGoods.shop_id,
                                              func.sum(models.AllocationOrderGoods.actual_allocated_amount)) \
            .join(models.AllocationOrder, models.AllocationOrder.id == models.AllocationOrderGoods.order_id) \
            .filter(models.AllocationOrder.wish_order_id == wish_order.id,
                    models.AllocationOrder.status == 1) \
            .group_by(models.AllocationOrderGoods.shop_id) \
            .all()
        allocated_amount_dict = {data[0]: data[1] for data in allocated_amount}

        # 店铺实配金额
        allocated_goods_list = self.session.query(models.AllocationOrderGoods.shop_id,
                                                  models.AllocationOrder.goods_id,
                                                  func.sum(models.AllocationOrderGoods.actual_allocated_amount)) \
            .join(models.AllocationOrder, models.AllocationOrder.id == models.AllocationOrderGoods.order_id) \
            .filter(models.AllocationOrderGoods.destination == 0,
                    models.AllocationOrder.wish_order_id == wish_order_id,
                    models.AllocationOrder.status == 1,
                    models.AllocationOrder.station_id == self.current_station.id) \
            .group_by(models.AllocationOrderGoods.shop_id, models.AllocationOrder.goods_id) \
            .all()
        allocated_goods_dict = {"{0}|{1}".format(allocated_goods[0], allocated_goods[1]): allocated_goods[2]
                                for allocated_goods in allocated_goods_list}

        packing_price_list = self.session.query(models.ShopPackingPrice, models.Goods) \
            .join(models.Goods, models.Goods.id == models.ShopPackingPrice.goods_id) \
            .filter(models.ShopPackingPrice.station_id == self.current_station.id,
                    models.ShopPackingPrice.wish_order_id == wish_order_id) \
            .all()

        allocation_subtotal_dict = defaultdict(int)
        allocation_volume_dict = defaultdict(int)
        allocation_weight_dict = defaultdict(int)
        for packing_price, goods in packing_price_list:
            # 商品的规格体积、重量
            standards_volume = float(goods.standards_volume)
            standards_weight = goods.standards_weight
            allocated_amount = allocated_goods_dict.get("{0}|{1}".format(packing_price.shop_id, packing_price.goods_id), 0)
            # 实配金额
            allocation_subtotal_dict[packing_price.shop_id] += allocated_amount * packing_price.price
            # 实配体积
            allocation_volume_dict[packing_price.shop_id] += float(allocated_amount) * standards_volume
            # 实配重量
            allocation_weight_dict[packing_price.shop_id] += allocated_amount * standards_weight

        data_list = []
        demand_amount_sum = 0
        purchasing_amount_sum = 0
        purchasing_volume_sum = 0
        purchasing_weight_sum = 0
        allocated_subtotal_sum = 0
        allocated_amount_sum = 0
        allocated_volume_sum = 0
        allocated_weight_sum = 0
        for shop in shops:
            demand_order = demand_order_dict.get(shop.id)
            negative_order = demand_status_dict.get(shop.id, 0)
            demand_amount = demand_amount_dict.get(demand_order.id, 0) if demand_order else 0
            purchasing_amount = purchasing_amount_dict.get(demand_order.id, 0) if demand_order else 0
            purchasing_volume = purchasing_volume_dict.get(demand_order.id, 0) if demand_order else 0
            purchasing_weight = purchasing_weight_dict.get(demand_order.id, 0) if demand_order else 0
            allocated_subtotal = allocation_subtotal_dict.get(shop.id, 0)
            allocated_amount = allocated_amount_dict.get(shop.id, 0)
            allocated_volume = allocation_volume_dict.get(shop.id, 0)
            allocated_weight = allocation_weight_dict.get(shop.id, 0)

            data_list.append({
                "demand_order_id": demand_order.id if demand_order else 0,
                "shop_id": shop.id,
                "shop_name": shop.name,
                "shop_abbr": shop.abbreviation,
                "demand_amount": check_float(demand_amount / 100),
                "purchasing_amount": check_float(purchasing_amount / 100),
                "purchasing_volume": check_float(purchasing_volume / 100),
                "purchasing_weight": check_float(purchasing_weight / 100 / 100),
                "allocated_amount": check_float(allocated_amount / 100),
                "allocation_subtotal": check_float(allocated_subtotal / 100 / 100),
                "allocation_volume": check_float(allocated_volume / 100),
                "allocation_weight": check_float(allocated_weight / 100 / 100),
                "create_time": TimeFunc.time_to_str(demand_order.create_time) if demand_order else "",
                "status": demand_order.status if demand_order else -1,
                "negative_order": negative_order
            })

            demand_amount_sum += demand_amount
            # 预采数量、预采体积、预采重量
            purchasing_amount_sum += purchasing_amount
            purchasing_volume_sum += purchasing_volume
            purchasing_weight_sum += purchasing_weight
            # 实配金额、实采数量、实采体积、实采重量
            allocated_subtotal_sum += allocated_subtotal
            allocated_amount_sum += allocated_amount
            allocated_volume_sum += allocated_volume
            allocated_weight_sum += allocated_weight

        data_list = sorted(
            data_list,
            key=lambda data: int(data["status"] == 2)*4 + int(data["status"] in [-1, 0])*2 + int(data["status"] == 1),
            reverse=True,
        )

        data_sum = {
            "demand_amount": check_float(demand_amount_sum / 100),
            "purchasing_amount": check_float(purchasing_amount_sum / 100),
            "purchasing_volume": check_float(purchasing_volume_sum / 100 / 100),
            "purchasing_weight": check_float(purchasing_weight_sum / 100 / 100),
            "allocation_subtotal": check_float(allocated_subtotal_sum / 100 / 100),
            "allocated_amount": check_float(allocated_amount_sum / 100),
            "allocated_volume": check_float(allocated_volume_sum / 100 / 100),
            "allocated_weight": check_float(allocated_weight_sum / 100 / 100)
        }

        return self.send_success(data_list=data_list, data_sum=data_sum)


# 订货截止
class DemandCutoff(StationBaseHandler):
    @BaseHandler.check_arguments("wish_order_id:int", "goods_list:list")
    def post(self):
        wish_order_id = self.args["wish_order_id"]
        goods_list = self.args["goods_list"]

        wish_order = models.WishOrder.get_by_id(self.session, wish_order_id, self.current_station.id)
        if not wish_order:
            return self.send_fail("没有找到指定的意向单")

        # 截止意向单订货
        if wish_order.status > 2:
            return self.send_fail("意向单已截止订货")
        elif wish_order.status < 2:
            return self.send_fail("意向单未提交")

        valid, message = self.validate_goods_list(goods_list)
        if not valid:
            return self.send_fail(message)
        goods_dict = {goods["goods_id"]: goods for goods in goods_list}

        # 意向单下的所有订货单货品
        all_demand_goods = self.session.query(models.DemandOrderGoods) \
            .join(models.DemandOrder, models.DemandOrder.id == models.DemandOrderGoods.demand_order_id) \
            .filter(models.DemandOrderGoods.status == 0,
                    models.DemandOrder.status == 2,
                    models.DemandOrder.wish_order_id == wish_order_id) \
            .all()
        # 后台订货总量
        demand_amount_dict = defaultdict(int)
        for demand_goods in all_demand_goods:
            if demand_goods.modified_demand_amount is not None:
                demand_amount_dict[demand_goods.goods_id] += demand_goods.modified_demand_amount
            else:
                demand_amount_dict[demand_goods.goods_id] += demand_goods.demand_amount

        # 所有货品
        goods_ids = {goods.goods_id for goods in all_demand_goods}
        goods_list = self.session.query(models.Goods) \
            .filter(models.Goods.status == 0,
                    models.Goods.station_id == self.current_station.id,
                    models.Goods.id.in_(goods_ids)) \
            .all()

        # 所有意向单货品
        wish_order_goods_list = self.session.query(models.WishOrderGoods) \
            .filter(models.WishOrderGoods.wish_order_id == wish_order_id) \
            .all()
        wish_order_goods_dict = {goods.goods_id: goods for goods in wish_order_goods_list}

        # 创建采购单
        new_purchase_order = models.PurchaseOrder(
            station_id=self.current_station.id,
            wish_order_id=wish_order_id,
        )
        self.session.add(new_purchase_order)
        self.session.flush()

        for goods in goods_list:
            goods_arg = goods_dict.get(goods.id)
            if not goods_arg:
                # 加了新的订货单，前端没有提交上来
                return self.send_fail("订货单发生变动，请刷新重试")

            goods_name = goods_arg["goods_name"]

            # 创建出库请求
            storage = goods.stock
            demand_amount = demand_amount_dict.get(goods.id, 0)
            allocating_amount = min(max(storage, 0), demand_amount)  # 待调出量，库存充足则为订货总量，库存为负时计 0 库存

            # 锁定汇总单商品库存
            wish_order_goods = wish_order_goods_dict.get(goods.id)
            if wish_order_goods:
                wish_order_goods.confirmed_storage = storage

            # 二次检查
            if goods_arg["storage"] != check_float(storage / 100):
                return self.send_fail("{} 的库存量发生变动，请刷新重试".format(goods_name))
            if goods_arg["modified_demand_amount"] is not None:
                if goods_arg["modified_demand_amount"] != check_float(demand_amount / 100):
                    return self.send_fail("{} 的修改后的订货量发生变动，请刷新重试".format(goods_name))
            else:
                if goods_arg["demand_amount"] != check_float(demand_amount / 100):
                    return self.send_fail("{} 的订货量发生变动，请刷新重试".format(goods_name))

            if allocating_amount:
                new_record = models.StockOutInGoods(
                    station_id=self.current_station.id,
                    wish_order_id=wish_order_id,
                    creator_id=self.current_user.id,
                    operator_id=self.current_user.id,
                    goods_id=goods.id,
                    amount=allocating_amount,
                    type=0,
                    status=2,
                )
                self.session.add(new_record)
                self.session.flush()

                models.SerialNumberMap.generate(self.session, 2, new_record.id, self.current_station.id)

            # 收集采购单数据
            purchasing_amount = max(demand_amount - max(storage, 0), 0)  # 待采购量，库存充足则为 0，库存为负时计 0 库存
            new_purchase_goods = models.PurchaseOrderGoods(
                purchaser_id=goods_arg["purchaser_id"] if goods_arg["purchaser_id"] else None,
                estimated_amount=purchasing_amount,
                purchase_order_id=new_purchase_order.id,
                goods_id=goods.id,
                wish_order_goods_id=wish_order_goods.id
            )
            self.session.add(new_purchase_goods)

        wish_order.status = 4

        self.session.commit()
        return self.send_success()

    def validate_goods_list(self, goods_list):
        """
        [
            {
                "goods_id": 1,
                "goods_name": "商品名",
                "purchaser_id": 123,
                "demand_amount": 333,
                "storage": 666
            },
        ]
        """
        if not isinstance(goods_list, list):
            return False, "商品列表参数格式有误"

        for goods in goods_list:
            if not isinstance(goods, dict):
                return False, "商品列表参数项格式有误"

            if "goods_id" not in goods:
                return False, "参数缺失：goods_id"
            elif not is_int(goods["goods_id"]):
                return False, "参数 goods_id 应为整数类型"
            if "goods_name" not in goods:
                return False, "参数缺失：goods_name"
            if goods["purchaser_id"] and not is_int(goods["purchaser_id"]):
                return False, "参数 purchaser_id 应为整数类型"
            if "demand_amount" not in goods:
                return False, "参数缺失：demand_amount"
            elif not is_number(goods["demand_amount"]):
                return False, "参数 demand_amount 应为数字类型"
            if "storage" not in goods:
                return False, "参数缺失：storage"
            elif not is_number(goods["storage"]):
                return False, "参数 storage 应为数字类型"

        goods_ids = {check_int(goods["goods_id"]) for goods in goods_list}
        valid_goods_list = models.Goods.get_by_ids(self.session, goods_ids, self.current_station.id)
        valid_goods_ids = {goods.id for goods in valid_goods_list}
        if goods_ids != valid_goods_ids:
            return False, "提交了无效的商品"

        purchaser_ids = {check_int(goods["purchaser_id"]) for goods in goods_list} - {0}
        valid_purchaser_list = self.session.query(models.Staff.id) \
            .filter(models.Staff.id.in_(purchaser_ids),
                    models.Staff.purchaser_status == 1,
                    models.Staff.status == 0) \
            .all()
        valid_purchaser_ids = {staff.id for staff in valid_purchaser_list}
        if purchaser_ids != valid_purchaser_ids:
            return False, "选择了无效的采购员"

        return True, ""


# 汇总单更新提醒
class SummaryNotifications(StationBaseHandler):
    @BaseHandler.check_arguments("purchase_order_id?:int")
    def get(self):
        purchase_order_id = self.args.get("purchase_order_id")

        demand_order_update_total, demand_order_update_dict = self.demand_order_updates()

        data = {
            "demand_order_update": {
                "total": demand_order_update_total,
                "order_update_dict": demand_order_update_dict
            }
        }

        if purchase_order_id:
            purchase_order = models.PurchaseOrder.get_by_id(self.session, purchase_order_id)
            if not purchase_order:
                return self.send_fail("没有找到对应的采购单")
            purchasing_dynamics_status = self.purchasing_dynamics_update(purchase_order_id)

            purchasing_dynamics_dict = {"purchasing_dynamics_update": purchasing_dynamics_status}
            data.update(purchasing_dynamics_dict)

        return self.send_success(data=data)

    def demand_order_updates(self):
        # 所有意向单的更新信息
        keys_demand_order_updates = redis.keys(KEY_DEMAND_ORDER_UPDATE_NOTIFICATIONS.format("*",
                                                                                            self.current_station.id))
        # 所有有更新的意向单 ID
        wish_order_ids = []
        for key_demand_order_updates in keys_demand_order_updates:
            key_demand_order_updates = key_demand_order_updates.decode('utf-8')
            key_demand_order_updates_parts = key_demand_order_updates.split(":")
            if len(key_demand_order_updates_parts) != 3:
                continue
            wish_order_id = check_int(key_demand_order_updates_parts[1])
            wish_order_ids.append(wish_order_id)

        wish_order_ids = list(set(wish_order_ids))

        # 计算各意向单更新数及总更新数
        demand_order_update_dict = {}
        demand_order_update_total = 0
        for wish_order_id in wish_order_ids:
            update_number = redis.get(KEY_DEMAND_ORDER_UPDATE_NOTIFICATIONS.format(wish_order_id,
                                                                                   self.current_station.id))
            update_number = check_int(update_number.decode('utf-8')) if update_number else 0
            demand_order_update_dict[wish_order_id] = update_number
            demand_order_update_total += update_number

        return demand_order_update_total, demand_order_update_dict

    def purchasing_dynamics_update(self, purchase_order_id):
        # 采购动态是否有更新
        key_purchasing_dynamics_update = redis.get(KEY_PURCHASING_DYNAMICS_NOTIFICATIONS
                                                   .format(purchase_order_id, self.current_staff.id, self.current_station.id))

        purchasing_dynamics_status = 1 if key_purchasing_dynamics_update else 0

        return purchasing_dynamics_status

    @BaseHandler.check_arguments("notification_type:str", "wish_order_id?:int", "purchase_order_id?:int")
    def delete(self):
        notification_type = self.args["notification_type"]

        # 订货单更新数清零
        if notification_type == "demand_order_update":
            wish_order_id = self.args.get("wish_order_id")
            wish_order_id = wish_order_id or "*"
            redis.delete(KEY_DEMAND_ORDER_UPDATE_NOTIFICATIONS.format(wish_order_id, self.current_station.id))

        # 清除采购动态提示
        elif notification_type == "purchasing_dynamics":
            purchase_order_id = self.args.get("purchase_order_id")

            purchase_order = models.PurchaseOrder.get_by_id(self.session, purchase_order_id)
            if purchase_order:
                redis.delete(KEY_PURCHASING_DYNAMICS_NOTIFICATIONS
                             .format(purchase_order.id, self.current_staff.id, self.current_station.id))

        return self.send_success()


# 汇总单-修改订货量
class DemandAmount(StationBaseHandler):
    @BaseHandler.check_arguments("wish_order_id:int", "goods_id:int")
    def get(self):
        wish_order_id = self.args["wish_order_id"]
        goods_id = self.args["goods_id"]
        wish_order = models.WishOrder.get_by_id(self.session, wish_order_id, self.current_station.id)
        if not wish_order:
            return self.send_fail("没有找到指定的意向单")
        if wish_order.status <= 1:
            return self.send_fail("意向单还未提交")
        demand_order_goods_objects = self.session.query(models.DemandOrderGoods)\
            .join(models.DemandOrder, models.DemandOrder.id == models.DemandOrderGoods.demand_order_id)\
            .filter(models.DemandOrder.wish_order_id == wish_order_id,
                    models.DemandOrderGoods.goods_id == goods_id,
                    models.DemandOrder.status >= 0,
                    models.DemandOrderGoods.status >= 0)\
            .all()
        shop_demand_dict = {demand_goods.order.shop_id: demand_goods for demand_goods in demand_order_goods_objects}
        shop_list = self.session.query(models.Shop)\
                                .filter(models.Shop.station_id == self.current_station.id,
                                        models.Shop.status == 0)\
                                .all()

        shop_order = {"仓库": -999, "总部": 1, "刘园": 2, "侯台": 3,
                      "咸水沽": 4, "华明": 5,
                      "大港": 6, "杨村": 7, "新立": 8, "大寺": 9, "汉沽": 10,
                      "沧州": 11, "静海": 13, "芦台": 14, "工农村": 15, "唐山": 16, "廊坊": 17,
                      "哈尔滨": 18, "西青道": 19, "双鸭山": 20, "承德": 21,
                      "张胖子": 22, "固安": 23, "燕郊": 24, "胜芳": 25, "蓟县": 26, }
        shop_list = sorted(shop_list, key=lambda d: shop_order.get(d.abbreviation, 999))

        demand_goods_list = list()
        total_data_dict = dict()
        total_data_dict["total_stock"] = 0
        total_data_dict["total_demand_amount"] = 0
        total_data_dict["total_modified_demand_amount"] = 0
        for shop in shop_list:
            demand_goods = shop_demand_dict.get(shop.id, None)
            if demand_goods:
                data = demand_goods.to_dict()
                total_data_dict["total_stock"] += check_float(demand_goods.current_storage / 100)
                total_data_dict["total_demand_amount"] += check_float(demand_goods.demand_amount / 100)
                if demand_goods.modified_demand_amount is None:
                    total_data_dict["total_modified_demand_amount"] += check_float(demand_goods.demand_amount / 100)
                else:
                    total_data_dict["total_modified_demand_amount"] += check_float(demand_goods.modified_demand_amount / 100)
            else:
                data = {
                    "id": None,
                    "shop_id": shop.id,
                    "shop_name": shop.abbreviation,
                    "current_storage": None,
                    "demand_amount": None,
                    "modified_demand_amount": None
                }
            demand_goods_list.append(data)
        return self.send_success(demand_goods_list=demand_goods_list, total_data_dict=total_data_dict)

    @BaseHandler.check_arguments("wish_order_id:int", "goods_id:int", "goods_demand_list:list")
    def put(self):
        wish_order_id = self.args["wish_order_id"]
        goods_id = self.args["goods_id"]
        goods_demand_list = self.args["goods_demand_list"]
        wish_order = models.WishOrder.get_by_id(self.session, wish_order_id, self.current_station.id)
        if not wish_order:
            return self.send_fail("没有找到指定的意向单")
        if wish_order.status <= 1:
            return self.send_fail("意向单还未提交")
        valid, message = self.validate_goods_demand_list(goods_demand_list)
        if not valid:
            return self.send_fail(message)
        # 查询店铺的订货单商品是否存在
        goods_ids = [goods_demand["demand_order_goods_id"] for goods_demand in goods_demand_list]
        demand_order_goods_list = models.DemandOrderGoods.get_by_ids(self.session, goods_ids)
        demand_order_goods_dict = {demand_goods.id: demand_goods for demand_goods in demand_order_goods_list}

        for goods_demand in goods_demand_list:
            # 如果店铺的订货单商品存在
            if goods_demand["demand_order_goods_id"] in demand_order_goods_dict:
                demand_goods = demand_order_goods_dict[goods_demand["demand_order_goods_id"]]
                demand_goods.modified_demand_amount = check_float(goods_demand["modified_demand_amount"] * 100)
            else:
                demand_order = self.session.query(models.DemandOrder) \
                    .filter(models.DemandOrder.wish_order_id == wish_order_id,
                            models.DemandOrder.shop_id == goods_demand["shop_id"],
                            models.DemandOrder.status >= 0) \
                    .first()
                # 如果当前店铺没有提交订货单，则先生成订货单(状态：已加入汇总单)
                if not demand_order:
                    demand_order = models.DemandOrder(
                        wish_order_id=wish_order_id,
                        shop_id=goods_demand["shop_id"],
                        creator_id=self.current_user.id,
                        status=2
                    )
                    self.session.add(demand_order)
                    self.session.flush()

                wish_order_goods_list = models.WishOrderGoods.get_by_order_id(self.session, wish_order_id)
                wish_order_goods_dict = {wish_order_goods.goods_id: wish_order_goods
                                         for wish_order_goods in wish_order_goods_list}
                # 判读是否是手动添加的采购商品(手动添加的采购商品没有对应的意向商品)
                if not wish_order_goods_dict.get(goods_id):
                    demand_goods = models.DemandOrderGoods(
                        goods_id=goods_id,
                        demand_order_id=demand_order.id,
                        modified_demand_amount=check_float(goods_demand["modified_demand_amount"] * 100)
                    )
                    self.session.add(demand_goods)
                    self.session.flush()
                else:
                    for wish_goods in wish_order_goods_list:
                        # 创建新的订货单商品
                        demand_goods = models.DemandOrderGoods(
                            goods_id=wish_goods.goods_id,
                            demand_order_id=demand_order.id,
                            wish_order_goods_id=wish_goods.id
                        )
                        self.session.add(demand_goods)
                        self.session.flush()
                        # 修改订货单商品的订货量
                        if demand_goods.goods_id == goods_id:
                            demand_goods.modified_demand_amount = check_float(goods_demand["modified_demand_amount"] * 100)
        # 判断意向单是否已汇总，如果已汇总，需要更新采购单商品的待采购量
        if wish_order.status >= 3:
            # 获取商品的修改后的订货总量
            demand_goods_objects = self.session.query(models.DemandOrderGoods)\
                .join(models.DemandOrder, models.DemandOrder.id == models.DemandOrderGoods.demand_order_id)\
                .filter(models.DemandOrder.wish_order_id == wish_order_id,
                        models.DemandOrderGoods.goods_id == goods_id,
                        models.DemandOrderGoods.status >= 0,
                        models.DemandOrder.status >= 0)\
                .all()
            total_modified_demand_amount = int()
            for demand_goods in demand_goods_objects:
                if demand_goods.modified_demand_amount is not None:
                    total_modified_demand_amount += demand_goods.modified_demand_amount
                else:
                    total_modified_demand_amount += demand_goods.demand_amount
            # 商品库存，以结束汇总开始备货时的库存为最终库存
            goods_storage = self.session.query(models.WishOrderGoods.confirmed_storage)\
                .filter(models.WishOrderGoods.wish_order_id == wish_order_id,
                        models.WishOrderGoods.goods_id == goods_id,
                        models.WishOrderGoods.status >= 0) \
                .first()
            goods_storage = goods_storage[0] if goods_storage else 0
            purchasing_amount = max(total_modified_demand_amount - goods_storage, 0)  # 待采购量，库存充足则为 0
            # 更新采购商品的待采购量
            purchase_order_goods_objects = self.session.query(models.PurchaseOrderGoods)\
                .join(models.PurchaseOrder, models.PurchaseOrder.id == models.PurchaseOrderGoods.purchase_order_id)\
                .filter(models.PurchaseOrder.wish_order_id == wish_order_id,
                        models.PurchaseOrderGoods.goods_id == goods_id,
                        models.PurchaseOrder.status >= 0)\
                .all()
            for purchase_goods in purchase_order_goods_objects:
                purchase_goods.estimated_amount = purchasing_amount
        self.session.commit()
        return self.send_success()

    def validate_goods_demand_list(self, goods_demand_list):
        """
        [
            {
                "shop_id": 1
                "demand_order_goods_id": 1
                "modified_demand_amount": 200
            },
            ...
        ]
        """
        if not isinstance(goods_demand_list, list):
            return False, "商品订货列表参数格式有误"
        for goods_demand in goods_demand_list:
            if not isinstance(goods_demand, dict):
                return False, "商品订货列表参数格式有误"

            if "shop_id" not in goods_demand:
                return False, "参数缺失：shop_id"
            elif not is_int(goods_demand["shop_id"]):
                return False, "参数 shop_id 应为整数类型"

            if "demand_order_goods_id" not in goods_demand:
                return False, "参数缺失：demand_order_goods_id"
            elif not is_int(goods_demand["demand_order_goods_id"]):
                return False, "参数 demand_order_goods_id 应为整数类型"

            if "modified_demand_amount" not in goods_demand:
                return False, "参数缺失：modified_demand_amount"
            elif not is_number(goods_demand["modified_demand_amount"]):
                return False, "参数 modified_demand_amount 应为数字类型"
            elif goods_demand["modified_demand_amount"] < 0:
                return False, "参数 modified_demand_amount 不能是负数"
            elif goods_demand["modified_demand_amount"] >= 2147483600:
                return False, "订货量的值过大"

        shop_ids = {check_int(goods_demand["shop_id"]) for goods_demand in goods_demand_list}
        valid_shop_list = models.Shop.get_by_ids(self.session, shop_ids, station_id=self.current_station.id)
        valid_shop_ids = {goods.id for goods in valid_shop_list}
        if shop_ids != valid_shop_ids:
            return False, "提交了无效的店铺"

        goods_ids = {check_int(goods_demand["demand_order_goods_id"]) for goods_demand in goods_demand_list} - {0}
        valid_goods_list = models.DemandOrderGoods.get_by_ids(self.session, goods_ids)
        valid_goods_ids = {goods.id for goods in valid_goods_list}
        if goods_ids != valid_goods_ids:
            return False, "提交了无效的订货单商品"

        return True, ""


# 门店配货价
class ShopPackingPrice(StationBaseHandler):
    @BaseHandler.check_arguments("wish_order_id:int", "shop_id:int", "price_list:list")
    def put(self):
        wish_order_id = self.args["wish_order_id"]
        shop_id = self.args["shop_id"]
        price_list = self.args["price_list"]

        if 9 not in self.current_staff.admin_permission_list and self.current_staff.super_admin_status == 0:
            return self.send_fail("没有编辑配货价的权限")

        wish_order = models.WishOrder.get_by_id(self.session, wish_order_id, self.current_station.id)
        if not wish_order:
            return self.send_fail("没有找到指定的意向单")
        if wish_order.status <= 1:
            return self.send_fail("意向单还未提交")

        shop = models.Shop.get_by_id(self.session, shop_id, self.current_station.id)
        if not shop:
            return self.send_fail("没有找到对应店铺")

        valid, message = self.validate_price_list(price_list)
        if not valid:
            return self.send_fail(message)

        goods_ids = {check_int(price_data["goods_id"]) for price_data in price_list}
        price_models = self.session.query(models.ShopPackingPrice) \
            .filter(models.ShopPackingPrice.station_id == self.current_station.id,
                    models.ShopPackingPrice.wish_order_id == wish_order.id,
                    models.ShopPackingPrice.shop_id == shop.id,
                    models.ShopPackingPrice.goods_id.in_(goods_ids)) \
            .all()
        price_model_dict = {price.goods_id: price for price in price_models}

        for price_data in price_list:
            goods_id = check_int(price_data["goods_id"])
            packing_price = check_int(price_data["packing_price"])

            price_model = price_model_dict.get(goods_id)
            if not price_model:
                price_model = models.ShopPackingPrice(
                    station_id=self.current_station.id,
                    creator_id=self.current_user.id,
                    wish_order_id=wish_order.id,
                    shop_id=shop.id,
                    goods_id=goods_id,
                )
                self.session.add(price_model)

            price_model.price = check_int(packing_price * 100)

        self.session.commit()
        return self.send_success()

    def validate_price_list(self, price_list):
        """
        检查配货价格列表
        [
            {
                "goods_id": 1
                "packing_price": 2.4
            },
            ...
        ]
        """
        if not isinstance(price_list, list):
            return False, "配货价格列表参数格式有误"
        for price_data in price_list:
            if not isinstance(price_data, dict):
                return False, "配货价格列表参数格式有误"

            if "goods_id" not in price_data:
                return False, "参数缺失：goods_id"
            elif not is_int(price_data["goods_id"]):
                return False, "参数 goods_id 应为整数类型"

            if "packing_price" not in price_data:
                return False, "参数缺失：packing_price"
            elif not is_number(price_data["packing_price"]):
                return False, "参数 packing_price 应为数字类型"
            elif check_int(price_data["packing_price"]) >= 2147483600:
                return False, "配货价格的值过大"

        goods_ids = {check_int(price_data["goods_id"]) for price_data in price_list}
        valid_goods_list = models.Goods.get_by_ids(self.session, goods_ids, station_id=self.current_station.id)
        valid_goods_ids = {goods.id for goods in valid_goods_list}
        if goods_ids != valid_goods_ids:
            return False, "提交了无效的商品"

        return True, ""


class PurchasingDynamicsMixin:
    @BaseHandler.check_arguments("wish_order_id:int")
    def get(self):
        wish_order_id = self.args["wish_order_id"]
        wish_order = models.WishOrder.get_by_id(self.session, wish_order_id, self.current_station.id)
        if not wish_order:
            return self.send_fail("没有找到指定的意向单")
        if wish_order.status <= 1:
            return self.send_fail("意向单还未提交")

        # 根据意向单拿采购商品
        purchasing_record_objs = self.session.query(models.PurchasingDynamics)\
            .join(models.PurchaseOrder, models.PurchaseOrder.id == models.PurchasingDynamics.purchase_order_id)\
            .filter(models.PurchaseOrder.wish_order_id == wish_order_id)\
            .order_by(models.PurchasingDynamics.update_time.desc())\
            .all()

        purchasing_dynamic_dict = defaultdict(list)
        for purchasing_dynamic in purchasing_record_objs:
            data = purchasing_dynamic.to_dict()

            # 根据权限查看采购单价与小计
            admin_permission_list = self.current_staff.admin_permissions_available
            purchaser_permission_list = self.current_staff.purchaser_permissions_available
            is_permission = 9 in admin_permission_list or 4 in purchaser_permission_list
            if not is_permission:
                data["price"] = 0
                data["subtotal"] = 0

            purchasing_dynamic_dict[TimeFunc.time_to_str(purchasing_dynamic.update_time)].append(data)

        purchasing_dynamic_list = []
        for date_time, purchasing_dynamic_info in purchasing_dynamic_dict.items():
            data = dict()
            data["date_time"] = date_time
            data["purchasing_dynamic_info"] = purchasing_dynamic_info

            purchasing_dynamic_list.append(data)

        # 排序
        purchasing_dynamic_list = sorted(purchasing_dynamic_list, key=lambda x: x["date_time"], reverse=True)

        return self.send_success(purchasing_dynamic_list=purchasing_dynamic_list)


# 平台上获取采购动态数据
class StationPurchasingDynamics(PurchasingDynamicsMixin, StationBaseHandler):
    pass
