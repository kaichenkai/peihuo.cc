# -*- coding:utf-8 -*-
import datetime
from collections import defaultdict

from dal import models
from handlers.base.pub_func import TimeFunc, check_float, check_int
from handlers.base.pub_receipt import ReceiptPrinter
from handlers.base.pub_web import StationBaseHandler
from handlers.base.webbase import BaseHandler


# 设置
class Configuration(StationBaseHandler):
    def get(self):
        config = models.Config.get_by_station_id(self.session, self.current_station.id)
        if not config:
            absent_config = models.Config(id=self.current_station.id)
            self.session.add(absent_config)
            self.session.commit()

        settlement_print_config = config.get_settlement_receipt_types()

        config_data = {
            "allocation_printer_id": config.allocation_printer_id,
            "allocation_print_copies": config.allocation_print_copies,
            "settlement_printer_id": config.settlement_printer_id,
            "print_accountant_receipt": settlement_print_config["print_accountant_receipt"],
            "print_customer_receipt": settlement_print_config["print_customer_receipt"],
            "purchase_type": config.purchase_type,
        }
        return self.send_success(config=config_data)

    @BaseHandler.check_arguments("action:str")
    def put(self):
        action = self.args["action"]

        if action == "allocation_printer":
            return self.allocation_printer()
        elif action == "settlement_printer":
            return self.settlement_printer()
        elif action == "purchase_type":
            return self.purchase_type()
        elif action == "shop_demand_amount_type":
            return self.shop_demand_amount_type()
        else:
            return self.send_fail("invalid action")

    @BaseHandler.check_arguments("printer_id:int", "copies:int")
    def allocation_printer(self):
        """ 分车单打印设置 """
        printer_id = self.args["printer_id"]  # 使用的打印机
        copies = self.args["copies"]  # 打印的份数

        config = models.Config.get_by_station_id(self.session, self.current_station.id)

        printer = models.Printer.get_by_id(self.session, printer_id, self.current_station.id)
        if not printer:
            return self.send_fail("打印机无效")

        if copies < 0:
            return self.send_fail("打印份数无效")
        elif copies > 10:
            return self.send_fail("打印份数过大")

        config.allocation_printer_id = printer_id
        config.allocation_print_copies = copies

        self.session.commit()
        return self.send_success()

    @BaseHandler.check_arguments("printer_id:int", "print_accountant_receipt:bool", "print_customer_receipt:bool")
    def settlement_printer(self):
        """ 待结算单打印设置 """
        printer_id = self.args["printer_id"]  # 使用的打印机
        print_accountant_receipt = self.args["print_accountant_receipt"]  #  打印会计联
        print_customer_receipt = self.args["print_customer_receipt"]  #  打印客户联

        config = models.Config.get_by_station_id(self.session, self.current_station.id)

        printer = models.Printer.get_by_id(self.session, printer_id, self.current_station.id)
        if not printer:
            return self.send_fail("打印机无效")

        config.settlement_printer_id = printer_id
        config.set_settlement_receipt_types(print_accountant_receipt, print_customer_receipt)

        self.session.commit()
        return self.send_success()

    @BaseHandler.check_arguments("new_type:int")
    def purchase_type(self):
        """ 采购方式设置 """
        new_type = self.args["new_type"]  # 新采购方式

        config = models.Config.get_by_station_id(self.session, self.current_station.id)

        config.purchase_type = new_type

        self.session.commit()
        return self.send_success()

    @BaseHandler.check_arguments("new_type:int")
    def shop_demand_amount_type(self):
        """ 门店订货总量计算方式设置 """
        new_type = self.args["new_type"]  # 新计算方式

        config = models.Config.get_by_station_id(self.session, self.current_station.id)

        config.shop_demand_amount_type = new_type

        self.session.commit()
        return self.send_success()
