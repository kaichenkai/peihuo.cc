# -*- coding:utf-8 -*-
import datetime
from collections import defaultdict

from sqlalchemy import func

from dal import models
from handlers.base.pub_func import TimeFunc, check_float, check_int
from handlers.base.pub_receipt import ReceiptPrinter
from handlers.base.pub_web import StationBaseHandler
from handlers.base.webbase import BaseHandler


# 打印机
class Printer(StationBaseHandler):
    @BaseHandler.check_arguments("printer_num:str", "printer_key?:str", "remarks:str")
    def post(self):
        printer_num = self.args["printer_num"]
        printer_key = self.args.get("printer_key", "")
        remarks = self.args["remarks"]

        if not printer_num:
            return self.send_fail("终端号不能为空")
        if len(printer_num) > 20:
            return self.send_fail("终端号不能超过 20 个字符")
        if len(printer_key) > 20:
            return self.send_fail("终端密钥不能超过 20 个字符")
        if not remarks:
            return self.send_fail("备注不能为空")
        if len(remarks) > 20:
            return self.send_fail("备注不能超过 20 个字符")

        new_printer = models.Printer(
            remarks=remarks,
            wireless_print_num=printer_num,
            wireless_print_key=printer_key,
            station_id=self.current_station.id,
            creator_id=self.current_user.id,
        )
        self.session.add(new_printer)
        self.session.commit()

        return self.send_success()

    @BaseHandler.check_arguments("printer_num:str", "printer_key?:str", "remarks:str")
    def put(self, printer_id):
        printer_num = self.args["printer_num"]
        printer_key = self.args.get("printer_key", "")
        remarks = self.args["remarks"]

        if not printer_num:
            return self.send_fail("终端号不能为空")
        if len(printer_num) > 20:
            return self.send_fail("终端号不能超过 20 个字符")
        if len(printer_key) > 20:
            return self.send_fail("终端密钥不能超过 20 个字符")
        if len(remarks) > 20:
            return self.send_fail("备注不能超过 20 个字符")

        printer = models.Printer.get_by_id(self.session, printer_id, self.current_station.id)
        if not printer:
            return self.send_fail("没有找到对应的打印机")

        printer.wireless_print_num = printer_num
        printer.printer_key = printer_key
        printer.remarks = remarks
        self.session.commit()

        return self.send_success()

    def delete(self, printer_id):
        printer = models.Printer.get_by_id(self.session, printer_id, self.current_station.id)
        if not printer:
            return self.send_fail("没有找到对应的打印机")

        printer.status = -1
        self.session.commit()

        return self.send_success()


# 打印机列表
class PrinterList(StationBaseHandler):
    def get(self):
        printers = models.Printer.get_by_station_id(self.session, self.current_station.id)

        printer_list = [{
            "id": printer.id,
            "printer_num": printer.wireless_print_num,
            "printer_key": printer.wireless_print_key,
            "remarks": printer.remarks,
            "status": printer.status,
        } for printer in printers]

        return self.send_success(printer_list=printer_list)


# 打印测试
class TestPrint(StationBaseHandler):
    @BaseHandler.check_arguments("printer_id:int")
    def post(self):
        printer_id = self.args["printer_id"]
        printer = models.Printer.get_by_id(self.session, printer_id, self.current_station.id)
        if not printer:
            return self.send_fail("选择了无效的打印机")

        receipt_printer = ReceiptPrinter(printer.wireless_print_num, printer.wireless_print_key)
        receipt_content = receipt_printer.test_order_template(
            printer_remarks=printer.remarks,
            printer_num=printer.wireless_print_num,
            printer_key=printer.wireless_print_key,
            operator_name=self.current_user.username,
            create_time=TimeFunc.time_to_str(datetime.datetime.now()),
        )
        success, error_msg = receipt_printer.print(receipt_content)
        if not success:
            return self.send_fail(error_msg)

        return self.send_success()


# 出库单打印
class StockOutPrint(StationBaseHandler):
    @BaseHandler.check_arguments("record_id:int", "printer_id:int")
    def post(self):
        record_id = self.args["record_id"]
        printer_id = self.args["printer_id"]

        record = models.StockOutInGoods.get_by_id(self.session, record_id,
                                                  self.current_station.id, status_list=[2, 3, 4])
        if not record:
            return self.send_fail("没有找到指定的出库单")

        printer = models.Printer.get_by_id(self.session, printer_id, self.current_station.id)
        if not printer:
            return self.send_fail("选择了无效的打印机")

        number_map = self.session.query(models.SerialNumberMap) \
            .filter(models.SerialNumberMap.order_type == 2,
                    models.SerialNumberMap.order_id == record.id) \
            .first()
        if not number_map:
            return self.send_fail("该出库单没有有效的出库单号")

        receipt_printer = ReceiptPrinter(printer.wireless_print_num, printer.wireless_print_key)
        receipt_content = receipt_printer.stock_out_order_template(
            goods_name=record.goods.name,
            order_no=number_map.order_no,
            amount=check_float(record.amount / 100),
            operator_name=record.operator.username,
            create_time=TimeFunc.time_to_str(record.create_time),
        )

        success, error_msg = receipt_printer.print(receipt_content)
        if not success:
            return self.send_fail(error_msg)

        return self.send_success()


# 店铺配货单打印
class ShopPackingPrint(StationBaseHandler):
    @BaseHandler.check_arguments("wish_order_id:int", "shop_id:int", "printer_id:int")
    def post(self):
        wish_order_id = self.args["wish_order_id"]
        shop_id = self.args["shop_id"]
        printer_id = self.args["printer_id"]

        wish_order = models.WishOrder.get_by_id(self.session, wish_order_id, self.current_station.id)
        if not wish_order:
            return self.send_fail("对应的意向单无效")

        shop = models.Shop.get_by_id(self.session, shop_id, self.current_station.id)
        if not shop:
            return self.send_fail("没有找到对应的店铺")

        printer = models.Printer.get_by_id(self.session, printer_id, self.current_station.id)
        if not printer:
            return self.send_fail("选择了无效的打印机")

        allocation_goods_list = self.session.query(models.AllocationOrderGoods, models.AllocationOrder) \
            .join(models.AllocationOrder, models.AllocationOrder.id == models.AllocationOrderGoods.order_id) \
            .filter(models.AllocationOrderGoods.shop_id == shop_id,
                    models.AllocationOrder.wish_order_id == wish_order_id,
                    models.AllocationOrder.station_id == self.current_station.id,
                    models.AllocationOrder.status == 1) \
            .all()

        goods_ids = []
        # 各商品的总实配量
        allocation_dict = defaultdict(int)
        for allocation_goods, allocation_order in allocation_goods_list:
            allocation_dict[allocation_order.goods_id] += allocation_goods.actual_allocated_amount
            goods_ids.append(allocation_order.goods_id)
        goods_ids = set(goods_ids)

        wish_goods_list = self.session.query(models.WishOrderGoods) \
            .filter(models.WishOrderGoods.status >= 0,
                    models.WishOrderGoods.wish_order_id == wish_order_id,
                    models.WishOrderGoods.goods_id.in_(goods_ids)) \
            .all()
        wish_goods_dict = {goods.goods_id: goods for goods in wish_goods_list}

        demand_goods_list = self.session.query(models.DemandOrderGoods) \
            .join(models.DemandOrder, models.DemandOrder.id == models.DemandOrderGoods.demand_order_id) \
            .filter(models.DemandOrder.shop_id == shop_id,
                    models.DemandOrder.wish_order_id == wish_order_id,
                    models.DemandOrderGoods.goods_id.in_(goods_ids)) \
            .all()
        demand_goods_dict = {goods.goods_id: goods for goods in demand_goods_list}

        goods_list = self.session.query(models.Goods) \
            .filter(models.Goods.station_id == self.current_station.id,
                    models.Goods.id.in_(goods_ids)) \
            .all()
        goods_dict = {goods.id: goods for goods in goods_list}

        packing_list = []
        for goods_id in goods_ids:
            goods = goods_dict.get(goods_id)
            wish_goods = wish_goods_dict.get(goods_id)
            demand_goods = demand_goods_dict.get(goods_id)
            allocated_amount = allocation_dict.get(goods_id, 0)

            packing_list.append({
                "goods_name": wish_goods.goods_name if wish_goods else goods.name if goods else "",
                "demand_amount": check_float(demand_goods.demand_amount / 100) if demand_goods else 0,
                "allocated_amount": check_float(allocated_amount / 100),
            })

        printer = models.Printer.get_by_id(self.session, printer_id, self.current_station.id)
        if not printer:
            return self.send_fail("选择了无效的打印机")

        number_map = models.SerialNumberMap.generate(self.session, 3, 0, self.current_station.id)

        receipt_printer = ReceiptPrinter(printer.wireless_print_num, printer.wireless_print_key)
        receipt_content = receipt_printer.packing_order_template(
            shop_name=shop.name,
            order_no=number_map.order_no,
            goods_list=packing_list,
            operator_name=self.current_user.username,
            create_time=TimeFunc.time_to_str(datetime.datetime.now()),
        )

        success, error_msg = receipt_printer.print(receipt_content)
        if not success:
            return self.send_fail(error_msg)

        return self.send_success()


# 店铺配货单打印
class AllocationOrderReprint(StationBaseHandler):
    @BaseHandler.check_arguments("allocation_order_id:int")
    def post(self):
        allocation_order_id = self.args["allocation_order_id"]

        order = models.AllocationOrder.get_by_id(self.session, allocation_order_id, self.current_station.id)

        config = models.Config.get_by_station_id(self.session, self.current_station.id)
        printer_id = config.allocation_printer_id
        copies = config.allocation_print_copies

        printer = models.Printer.get_by_id(self.session, printer_id, self.current_station.id)
        if not printer:
            return self.send_fail("分车单打印机设置无效，请在中转站设置中配置")

        goods = order.goods
        purchase_order_goods = order.purchase_order_goods

        goods_list = order.goods_list
        total_amount = 0
        allocation_list = []
        for order_goods in goods_list:
            total_amount += order_goods.actual_allocated_amount
            if order_goods.destination == 0:
                shop = order_goods.shop
                shop_name = shop.abbreviation if shop else "未知店铺"
            elif order_goods.destination == 1:
                shop_name = "仓库"
            elif order_goods.destination == 2:
                shop_name = "其他"
            else:
                shop_name = ""
            allocation_list.append({
                "shop_name": shop_name,
                "allocating_amount": check_float(order_goods.actual_allocated_amount / 100)
            })

        # 打印分车单据
        receipt_printer = ReceiptPrinter(printer.wireless_print_num, printer.wireless_print_key)
        receipt_content = receipt_printer.allocation_order_template(
            goods_name=goods.name,
            firm_name=purchase_order_goods.firm.name if purchase_order_goods else "仓库",
            order_no=order.order_no,
            total_amount=check_float(total_amount / 100),
            allocation_list=allocation_list,
            operator_name=self.current_user.username,
            create_time=TimeFunc.time_to_str(datetime.datetime.now()),
        )
        for i in range(copies):
            success, error_msg = receipt_printer.print(receipt_content)
            if not success:
                return self.send_fail(error_msg)

        return self.send_success()
