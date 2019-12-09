from sqlalchemy import func

from handlers.base.pub_func import check_float, TimeFunc
from handlers.base.pub_web import StationBaseHandler

from dal import models


# 单号搜索
class OrderSearch(StationBaseHandler):
    def get(self, order_no):
        number_map = models.SerialNumberMap.get_by_order_no(self.session, order_no)
        if not number_map:
            return self.send_fail("没有找到指定的单号")

        if number_map.order_type == 2:
            return self.stock_out_order(number_map)
        elif number_map.order_type in [5, 6]:
            return self.allocation_order(number_map)
        elif number_map.order_type == 4:
            return self.settlement_voucher(number_map)
        else:
            return self.send_fail("暂不支持此种订单的搜索")

    def stock_out_order(self, number_map):
        """ 出库单搜索 """
        record = self.session.query(models.StockOutInGoods) \
            .filter(models.StockOutInGoods.id == number_map.order_id,
                    models.StockOutInGoods.station_id == self.current_station.id,
                    models.StockOutInGoods.type == 0,
                    models.StockOutInGoods.status.in_([2, 3, 4])) \
            .first()
        if not record:
            return self.send_fail("没有找到对应的出库单")

        goods = record.goods
        data = {
            "order_type": number_map.order_type,
            "order_no": number_map.order_no,
            "id": record.id,
            "amount": check_float(record.amount / 100),
            "goods_id": goods.id,
            "goods_name": goods.name,
            "status": record.status,
        }
        return self.send_success(data=data)

    def allocation_order(self, number_map):
        """ 分车单搜索 """
        allocation_order = self.session.query(models.AllocationOrder) \
            .filter(models.AllocationOrder.order_no == number_map.order_no,
                    models.AllocationOrder.station_id == self.current_station.id) \
            .first()
        if not allocation_order:
            return self.send_fail("没有找到指定的分车单")

        firm_name = ""
        # 采购分车单
        if number_map.order_type == 5:
            purchase_goods = models.PurchaseOrderGoods.get_by_id(self.session, number_map.order_id, self.current_station.id)
            if not purchase_goods:
                return self.send_fail("分车单对应的采购货品无效")

            firm = purchase_goods.firm
            firm_name = firm.name if firm else ""
        # 仓库分车单
        elif number_map.order_type == 6:
            stock_out_record = models.StockOutInGoods.get_by_id(self.session,
                                                                allocation_order.stock_out_record_id,
                                                                self.current_station.id,
                                                                [3, 4])
            if not stock_out_record:
                return self.send_fail("没有找到对应的出库记录")
        else:
            return self.send_fail("分车单类型未知")

        allocation_goods_list = allocation_order.goods_list \
            .order_by(models.AllocationOrderGoods.id.asc()) \
            .all()
        # 配货去向
        allocation_list = []
        # 总配货量
        allocated_amount = 0
        # 入库总量
        stock_in_amount = 0
        for allocation_goods in allocation_goods_list:
            if allocation_goods.destination == 0:
                shop = allocation_goods.shop
                shop_id = shop.id if shop else 0
                shop_name = shop.abbreviation if shop else "未知店铺"
            elif allocation_goods.destination == 1:
                shop_id = 0
                shop_name = "仓库"
            elif allocation_goods.destination == 2:
                shop_id = 0
                shop_name = "其他"
            else:
                raise Exception("未知分车目标")

            allocation_list.append({
                "id": allocation_goods.id,
                "destination": allocation_goods.destination,
                "shop_id": shop_id,
                "shop_name": shop_name,
                "allocated_amount": check_float(allocation_goods.actual_allocated_amount / 100),
            })
            allocated_amount += allocation_goods.actual_allocated_amount
            stock_in_amount += allocation_goods.actual_allocated_amount if allocation_goods.destination == 1 else 0

        actual_stock_in_amount = self.session.query(func.sum(models.StockOutInGoods.amount)) \
            .filter(models.StockOutInGoods.type == 1,
                    models.StockOutInGoods.status == 1,
                    models.StockOutInGoods.allocation_order_id == allocation_order.id) \
            .first()

        wish_goods_name = self.session.query(models.WishOrderGoods.goods_name) \
            .filter(models.WishOrderGoods.wish_order_id == allocation_order.wish_order_id,
                    models.WishOrderGoods.goods_id == allocation_order.goods_id,
                    models.WishOrderGoods.status >= 0) \
            .first()
        goods_name = wish_goods_name.goods_name if wish_goods_name else "" or allocation_order.goods.name

        data = {
            "order_type": number_map.order_type,
            "order_no": number_map.order_no,
            "allocation_order_id": allocation_order.id,
            "allocation_status": allocation_order.status,
            "allocation_remarks": allocation_order.remarks,
            "goods_name": goods_name,
            "firm_name": firm_name,
            "allocated_amount": check_float(allocated_amount / 100),
            "stock_in_amount": check_float(stock_in_amount / 100),
            "actual_stock_in_amount": check_float((actual_stock_in_amount[0] or 0) / 100) if actual_stock_in_amount else 0,
            "allocation_list": allocation_list,
        }
        return self.send_success(data=data)

    def settlement_voucher(self, number_map):
        """ 待结算单搜索 """
        settlement_voucher = self.session.query(models.FirmSettlementVoucher) \
            .filter(models.FirmSettlementVoucher.order_no == number_map.order_no,
                    models.FirmSettlementVoucher.station_id == self.current_station.id) \
            .first()
        if not settlement_voucher:
            return self.send_fail("没有找到指定的待结算单")

        allocation_order = settlement_voucher.allocation_order
        purchase_goods = allocation_order.purchase_order_goods
        wish_order = allocation_order.wish_order

        # 优先用意向单商品名
        goods_id = allocation_order.goods_id
        wish_goods_name = self.session.query(models.WishOrderGoods.goods_name) \
            .filter(models.WishOrderGoods.wish_order_id == wish_order.id,
                    models.WishOrderGoods.goods_id == goods_id,
                    models.WishOrderGoods.status >= 0) \
            .first()
        goods_name = wish_goods_name.goods_name if wish_goods_name else "" or allocation_order.goods.name

        firm = settlement_voucher.firm

        # 除入库外已分车量
        amount = self.session.query(func.sum(models.AllocationOrderGoods.actual_allocated_amount)) \
            .filter(models.AllocationOrderGoods.order_id == allocation_order.id,
                    models.AllocationOrderGoods.destination != 1) \
            .first()
        amount = amount[0] or 0 if amount else 0
        # 分车入库记录
        stock_in_record = self.session.query(models.StockOutInGoods) \
            .filter(models.StockOutInGoods.allocation_order_id == allocation_order.id,
                    models.StockOutInGoods.type == 1,
                    models.StockOutInGoods.status == 1) \
            .first()
        amount += stock_in_record.amount if stock_in_record else 0
        amount = check_float(amount / 100)

        # 应结金额，按件数比例计算，实配件数/采购件数*小计
        total_money = check_float(amount / purchase_goods.actual_amount * purchase_goods.subtotal)
        # 采购价
        price = check_float(total_money / amount)

        data = {
            "order_type": number_map.order_type,
            "order_no": number_map.order_no,
            "settlement_voucher_id": settlement_voucher.id,
            "settlement_status": settlement_voucher.status,
            "create_time": TimeFunc.time_to_str(settlement_voucher.create_time),
            "goods_id": goods_id,
            "goods_name": goods_name,
            "firm_id": firm.id,
            "firm_name": firm.name,
            "remarks": settlement_voucher.remarks,
            "amount": amount,
            "price": price,
            "total_money": total_money,
        }
        return self.send_success(data=data)
