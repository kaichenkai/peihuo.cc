# -*- coding: utf-8 -*-
import datetime

from sqlalchemy import func, and_, or_, distinct
from handlers.base.pub_func import TimeFunc, check_float, check_int
from handlers.base.pub_receipt import ReceiptPrinter
from handlers.base.pub_web import StationBaseHandler
from handlers.base.pub_web import BaseHandler
from handlers.base.pub_statistic import update_firm_payment_statistics
from dal import models, constants, models_statistics
from collections import defaultdict


# 待结算单列表
class FirmSettlementVoucherList(StationBaseHandler):
    @BaseHandler.check_arguments("order_id?:int",
                                 "status?:int", "order_by?:str", "asc?:bool",
                                 "keyword?:str", "from_date?:date", "before_date?:date", "date?:date",
                                 "settled_from_date?:date", "settled_before_date?:date", "settled_date?:date",
                                 "page?:int", "limit?:int")
    def get(self):
        order_id = self.args.get("order_id")
        keyword = self.args.get("keyword")
        status = self.args.get("status")
        order_by = self.args.get("order_by")
        asc = self.args.get("asc", False)
        from_date = self.args.get("from_date")
        before_date = self.args.get("before_date")
        date = self.args.get("date")
        settled_from_date = self.args.get("settled_from_date")
        settled_before_date = self.args.get("settled_before_date")
        settled_date = self.args.get("settled_date")
        page = self.args.get("page", 0)
        limit = self.args.get("limit", 20)

        vouchers = self.session.query(models.FirmSettlementVoucher,
                                      models.FirmSettlementOrder,
                                      models.AllocationOrder,
                                      models.PurchaseOrderGoods,
                                      models.WishOrderGoods,
                                      models.Firm,
                                      models.Staff,
                                      models.AccountInfo) \
            .join(models.AllocationOrder, models.AllocationOrder.id == models.FirmSettlementVoucher.allocation_order_id) \
            .outerjoin(models.FirmSettlementOrder, models.FirmSettlementOrder.id == models.FirmSettlementVoucher.settlement_order_id) \
            .join(models.PurchaseOrderGoods, models.PurchaseOrderGoods.id == models.AllocationOrder.purchase_order_goods_id) \
            .join(models.WishOrderGoods, and_(models.WishOrderGoods.goods_id == models.PurchaseOrderGoods.goods_id,
                                              models.WishOrderGoods.wish_order_id == models.AllocationOrder.wish_order_id)) \
            .join(models.Firm, models.Firm.id == models.FirmSettlementVoucher.firm_id) \
            .outerjoin(models.Staff, models.Staff.id == models.PurchaseOrderGoods.purchaser_id) \
            .outerjoin(models.AccountInfo, models.AccountInfo.id == models.Staff.account_id) \
            .filter(models.FirmSettlementVoucher.station_id == self.current_station.id,
                    models.WishOrderGoods.status >= 0)

        if order_id:
            vouchers = vouchers.filter(models.FirmSettlementVoucher.settlement_order_id == order_id)

        if keyword:
            vouchers = vouchers.filter(or_(models.WishOrderGoods.goods_name.like("%{}%".format(keyword)),
                                       models.Firm.name.like("%{}%".format(keyword))))
        if status is not None:
            vouchers = vouchers.filter(models.FirmSettlementVoucher.status == status)

        # 结算时间过滤
        if settled_from_date or settled_before_date or settled_date:
            if settled_from_date:
                vouchers = vouchers.filter(func.DATE(models.FirmSettlementOrder.create_time) >= settled_from_date)
            if settled_before_date:
                vouchers = vouchers.filter(func.DATE(models.FirmSettlementOrder.create_time) < settled_before_date)
            if settled_date:
                vouchers = vouchers.filter(func.DATE(models.FirmSettlementOrder.create_time) == settled_date)

        # 开票时间过滤
        if from_date:
            vouchers = vouchers.filter(func.DATE(models.FirmSettlementVoucher.create_time) >= from_date)
        if before_date:
            vouchers = vouchers.filter(func.DATE(models.FirmSettlementVoucher.create_time) < before_date)
        if date:
            vouchers = vouchers.filter(func.DATE(models.FirmSettlementVoucher.create_time) == date)

        if order_by == "date":
            if asc:
                vouchers = vouchers.order_by(models.FirmSettlementVoucher.create_time.asc())
            else:
                vouchers = vouchers.order_by(models.FirmSettlementVoucher.create_time.desc())
        elif order_by == "goods_name":
            if asc:
                vouchers = vouchers.order_by(models.WishOrderGoods.name_acronym.asc())
            else:
                vouchers = vouchers.order_by(models.WishOrderGoods.name_acronym.desc())
        elif order_by == "firm_name":
            if asc:
                vouchers = vouchers.order_by(models.Firm.name_acronym.asc())
            else:
                vouchers = vouchers.order_by(models.Firm.name_acronym.desc())

        data_count = vouchers.count()
        vouchers = vouchers.offset(page * limit).limit(limit).all()

        # 计算结算件数（不含分车入库部分）
        allocation_order_ids = {order.id for _, _, order, _, _, _, _, _ in vouchers}
        allocated_amount_sums = self.session.query(models.AllocationOrderGoods.order_id,
                                                   func.sum(models.AllocationOrderGoods.actual_allocated_amount)) \
            .filter(models.AllocationOrderGoods.order_id.in_(allocation_order_ids),
                    models.AllocationOrderGoods.destination != 1) \
            .group_by(models.AllocationOrderGoods.order_id) \
            .all()
        allocated_amount_sum_dict = {data[0]: data[1] for data in allocated_amount_sums}

        # 分车入库记录（用于计算实际入库件数）
        stock_in_records = self.session.query(models.StockOutInGoods.allocation_order_id,
                                              models.StockOutInGoods.amount) \
            .filter(models.StockOutInGoods.allocation_order_id.in_(allocation_order_ids),
                    models.StockOutInGoods.type == 1,
                    models.StockOutInGoods.status == 1) \
            .all()
        stock_in_amount_dict = {record[0]: record[1] for record in stock_in_records}

        order_list = []
        for voucher, settlement_order, allocation, purchase_goods, wish_goods, firm, purchaser, purchaser_account in vouchers:
            amount = check_float(allocated_amount_sum_dict.get(allocation.id, 0) / 100)
            stock_in_amount = check_float(stock_in_amount_dict.get(allocation.id, 0) / 100)
            # 应结量 = 非入库部分分车量 + 实际入库量
            amount += stock_in_amount

            # 应结金额，按件数比例计算，实配件数/采购件数*小计
            total_money = check_float(amount / purchase_goods.actual_amount * purchase_goods.subtotal)
            # 采购价
            price = check_float(total_money / amount)

            order_list.append({
                "id": voucher.id,
                "order_no": voucher.order_no,
                "settlement_order_id": voucher.settlement_order_id,
                "amount": amount,
                "price": price,
                "total_money": total_money,
                "settled_amount": check_float((voucher.settled_amount or 0) / 100),
                "settled_price": check_float((voucher.settled_price or 0) / 100),
                "settled_time": TimeFunc.time_to_str(settlement_order.create_time) if settlement_order else "",
                "date": TimeFunc.time_to_str(voucher.create_time, "date"),
                "create_time": TimeFunc.time_to_str(voucher.create_time),
                "creator_name": voucher.creator.username,
                "goods_id": wish_goods.goods_id,
                "goods_name": wish_goods.goods_name,
                "firm_id": firm.id,
                "firm_name": firm.name,
                "remarks": voucher.remarks,
                "purchaser_name": (purchaser.remarks or purchaser_account.username) if purchaser and purchaser_account else "",
                "status": voucher.status,
            })

        has_more = len(order_list) >= limit
        return self.send_success(order_list=order_list, data_count=data_count, has_more=has_more)


# 供货商待结算单
class FirmSettlementVoucher(StationBaseHandler):
    @BaseHandler.check_arguments("allocation_order_id:int", "remarks?:str")
    def post(self):
        allocation_order_id = self.args["allocation_order_id"]
        remarks = self.args.get("remarks", "")

        allocation_order = models.AllocationOrder.get_by_id(self.session, allocation_order_id, self.current_station.id)
        if not allocation_order:
            return self.send_fail("没有找到对应的分车单")
        elif not allocation_order.purchase_order_goods_id:
            return self.send_fail("没有找到有效的供货商分车单")
        elif allocation_order.status != 1:
            return self.send_fail("对应的分车单还未被确认")

        # 已配置的打印机
        config = models.Config.get_by_station_id(self.session, self.current_station.id)
        printer_id = config.settlement_printer_id
        printer = models.Printer.get_by_id(self.session, printer_id, self.current_station.id)
        if not printer:
            return self.send_fail("待结算单打印机设置无效，请在中转站设置中配置")

        # 除入库外已分车量
        allocated_amount = self.session.query(func.sum(models.AllocationOrderGoods.actual_allocated_amount)) \
            .filter(models.AllocationOrderGoods.order_id == allocation_order.id,
                    models.AllocationOrderGoods.destination != 1) \
            .first()
        allocated_amount = allocated_amount[0] or 0 if allocated_amount else 0

        # 分车入库记录
        stock_in_record = self.session.query(models.StockOutInGoods) \
            .filter(models.StockOutInGoods.allocation_order_id == allocation_order.id,
                    models.StockOutInGoods.type == 1,
                    models.StockOutInGoods.status == 1) \
            .first()
        allocated_amount += stock_in_record.amount if stock_in_record else 0

        purchase_goods = models.PurchaseOrderGoods.get_by_id(self.session, allocation_order.purchase_order_goods_id)
        if not purchase_goods:
            return self.send_fail("没有找到对应的采购单商品")
        elif not purchase_goods.firm_id:
            return self.send_fail("没有可结算的供货商")

        # 已有的待结算单
        settlement_voucher = self.session.query(models.FirmSettlementVoucher) \
            .filter(models.FirmSettlementVoucher.station_id == self.current_station.id,
                    models.FirmSettlementVoucher.allocation_order_id == allocation_order.id) \
            .first()
        if not settlement_voucher:
            # 生成待结算单号
            number_map = models.SerialNumberMap.generate(self.session, 4, allocation_order.id, self.current_station.id)
            # 创建新的待结算单
            settlement_voucher = models.FirmSettlementVoucher(
                station_id=self.current_station.id,
                creator_id=self.current_user.id,
                allocation_order_id=allocation_order_id,
                firm_id=purchase_goods.firm_id,
                order_no=number_map.order_no,
                remarks=remarks,
            )
            self.session.add(settlement_voucher)
            self.session.flush()

        # 打印待结算单
        receipt_printer = ReceiptPrinter(printer.wireless_print_num, printer.wireless_print_key)
        order = purchase_goods.order
        receipt_types = config.get_settlement_receipt_types()
        receipt_content = ""
        # 打印会计联
        if receipt_types["print_accountant_receipt"]:
            receipt_content += receipt_printer.firm_settlement_voucher_template(
                receipt_type=0,
                goods_name=purchase_goods.goods.name,
                firm_name=purchase_goods.firm.name,
                order_no=settlement_voucher.order_no,
                amount=check_float(allocated_amount / 100),
                remarks=settlement_voucher.remarks,
                operator_name=self.current_user.username,
                create_time=TimeFunc.time_to_str(datetime.datetime.now()),
                should_cut=receipt_types["print_customer_receipt"],  # XXX ugly workaround，需要打印客户联时才切纸
            )
        # 打印客户联
        if receipt_types["print_customer_receipt"]:
            receipt_content += receipt_printer.firm_settlement_voucher_template(
                receipt_type=1,
                goods_name=purchase_goods.goods.name,
                firm_name=purchase_goods.firm.name,
                order_no=settlement_voucher.order_no,
                amount=check_float(allocated_amount / 100),
                remarks=settlement_voucher.remarks,
                operator_name=self.current_user.username,
                create_time=TimeFunc.time_to_str(datetime.datetime.now()),
            )
        if receipt_content:
            success, error_msg = receipt_printer.print(receipt_content)
            if not success:
                return self.send_fail(error_msg)

        self.session.commit()
        return self.send_success()


# 供货商结算单
class FirmSettlementOrder(StationBaseHandler):
    def get(self, order_id):
        order = self.session.query(models.FirmSettlementOrder) \
            .filter(models.FirmSettlementOrder.id == order_id,
                    models.FirmSettlementOrder.station_id == self.current_station.id) \
            .first()
        if not order:
            return self.send_fail("没有找到该结算单")

        # 结算账号信息
        payment_account = order.payment_account
        if payment_account:
            parent_bank = None
            if payment_account.account_type in [2, 3]:
                parent_bank = self.session.query(models.LcParentBank) \
                    .filter(models.LcParentBank.parent_bank_no == payment_account.branch_bank_no) \
                    .first()
            payment_firm = payment_account.firm
            payment_account_info = {
                "id": payment_account.id,
                "account_type": payment_account.account_type,
                "account_name": payment_account.account_name,
                "account_num": payment_account.account_num,
                "bank_name": parent_bank.parent_bank_name if parent_bank else "",
                "firm_id": payment_firm.id,
                "firm_name": payment_firm.name,
                "status": payment_account.status,
            }
        else:
            payment_account_info = {}

        # 供货商信息
        firms = self.session.query(models.Firm.id,
                                   models.Firm.name,
                                   func.sum(models.FirmSettlementVoucher.settled_amount
                                            * models.FirmSettlementVoucher.settled_price).label("settled_money")) \
            .join(models.FirmSettlementVoucher, models.FirmSettlementVoucher.firm_id == models.Firm.id) \
            .filter(models.FirmSettlementVoucher.settlement_order_id == order_id,
                    models.FirmSettlementVoucher.status == 1) \
            .group_by(models.FirmSettlementVoucher.firm_id) \
            .all()
        firms = [{
            "id": firm.id,
            "name": firm.name,
            "settled_money": check_float(firm.settled_money / 10000),
        } for firm in firms]

        creator = order.creator
        order_info = {
            "id": order.id,
            "agent_name": order.agent_name,
            "agent_phone": order.agent_phone,
            "payment": order.payment,
            "total_money": check_float(order.total_money / 100),
            "remarks": order.remarks,
            "create_time": TimeFunc.time_to_str(order.create_time),
            "creator_id": creator.id,
            "creator_name": creator.username,
            "payment_account": payment_account_info,
            "firms": firms,
        }

        return self.send_success(order_info=order_info)

    @BaseHandler.check_arguments("vouchers:list",
                                 "agent_name:str", "agent_phone:str", "total_money_sum:float",
                                 "payment_account_id:int", "remarks?:str",
                                 "send_sms?:bool")
    def post(self):
        vouchers = self.args["vouchers"]
        agent_name = self.args["agent_name"]
        agent_phone = self.args["agent_phone"]
        total_money_sum = self.args["total_money_sum"]
        payment_account_id = self.args["payment_account_id"] or None
        remarks = self.args.get("remarks", "")
        send_sms = self.args.get("send_sms", False)

        valid, message = self.validate_goods_list(vouchers)
        if not valid:
            return self.send_fail(message)

        voucher_ids = {check_int(voucher["id"]) for voucher in vouchers}
        valid_vouchers = self.session.query(models.FirmSettlementVoucher) \
            .filter(models.FirmSettlementVoucher.id.in_(voucher_ids),
                    models.FirmSettlementVoucher.status == 0) \
            .all()
        if {voucher.id for voucher in valid_vouchers} != voucher_ids:
            return self.send_fail("提交了无效的或已结算过的记录")
        valid_vouchers_dict = {voucher.id: voucher for voucher in valid_vouchers}

        payment = 0
        if payment_account_id:
            payment_account = models.FirmPaymentAccount.get_by_id(self.session, payment_account_id, self.current_station.id)
            if not payment_account:
                return self.send_fail("没有找到指定的供货商收款账号")
            payment = 2 if payment_account.account_type == 1 else 1

        settlement_order = models.FirmSettlementOrder(
            agent_name=agent_name,
            agent_phone=agent_phone,
            payment=payment,
            payment_account_id=payment_account_id,
            total_money=check_int(total_money_sum * 100),
            remarks=remarks,
            station_id=self.current_station.id,
            creator_id=self.current_user.id
        )
        self.session.add(settlement_order)
        self.session.flush()

        voucher_money_sum = 0
        for voucher_arg in vouchers:
            voucher_id = check_int(voucher_arg["id"])
            amount = check_float(voucher_arg["amount"])
            price = check_float(voucher_arg["price"])
            total_money = check_float(voucher_arg["total_money"])
            voucher = valid_vouchers_dict[voucher_id]

            voucher.settlement_order_id = settlement_order.id
            voucher.settled_amount = check_int(amount * 100)
            voucher.settled_price = check_int(price * 100)
            voucher.status = 1

            voucher_money_sum += total_money

        if total_money_sum != voucher_money_sum:
            return self.send_fail("结算总金额计算有误，应为 {}".format(voucher_money_sum))

        self.session.commit()

        if send_sms:
            from libs import yunpian
            yunpian.send_firm_settlement(agent_phone,
                                         TimeFunc.time_to_str(datetime.datetime.now()),
                                         self.current_station.name,
                                         total_money_sum)

        return self.send_success()

    def validate_goods_list(self, vouchers):
        """验证待结算单列表参数"""

        if not isinstance(vouchers, list):
            return False, "待结算单列表参数格式有误"

        for i in range(len(vouchers)):
            voucher = vouchers[i]
            if not isinstance(voucher, dict):
                return False, "待结算单列表参数项格式有误"

            if "id" not in voucher:
                return False, "参数缺失：id"
            if "amount" not in voucher:
                return False, "参数缺失：amount"
            if "price" not in voucher:
                return False, "参数缺失：price"
            if "total_money" not in voucher:
                return False, "参数缺失：total_money"

            amount = voucher["amount"]
            price = voucher["price"]
            total_money = voucher["total_money"]

            if check_float(amount * price) != total_money:
                return False, "第 {} 项应结金额计算有误，应为{}".format(i, check_float(amount * price))

        return True, ""


# 供货商结算记录列表
class FirmSettlementOrderList(StationBaseHandler):
    @BaseHandler.check_arguments("from_date?:date", "to_date?:date", "firm_ids?:str", "page?:int", "limit?:int")
    def get(self):
        today = datetime.date.today()
        from_date = self.args.get("from_date", today - datetime.timedelta(days=30))
        to_date = self.args.get("to_date", today)
        firm_ids = self.args.get("firm_ids")
        firm_ids = set(map(lambda i: check_int(i), firm_ids.split("|"))) if firm_ids else None
        page = self.args.get("page", 0)
        limit = self.args.get("limit", 20)

        # 预先对结算单分页
        order_ids_base = self.session.query(models.FirmSettlementOrder.id) \
            .join(models.FirmSettlementVoucher,
                  models.FirmSettlementVoucher.settlement_order_id == models.FirmSettlementOrder.id) \
            .filter(models.FirmSettlementOrder.station_id == self.current_station.id,
                    func.DATE(models.FirmSettlementOrder.create_time) >= from_date,
                    func.DATE(models.FirmSettlementOrder.create_time) <= to_date) \
            .order_by(models.FirmSettlementOrder.create_time.desc())
        # 未筛选的所有结算单
        unfiltered_order_ids = order_ids_base.all()
        unfiltered_order_ids = [o.id for o in unfiltered_order_ids]
        if firm_ids is not None:
            order_ids_base = order_ids_base.filter(models.FirmSettlementVoucher.firm_id.in_(firm_ids))
        order_ids = order_ids_base.distinct() \
            .offset(page * limit).limit(limit).all()

        # 本页所有结算单
        order_ids = {o.id for o in order_ids}
        orders = self.session.query(models.FirmSettlementOrder) \
            .filter(models.FirmSettlementOrder.id.in_(order_ids)) \
            .order_by(models.FirmSettlementOrder.create_time.desc()) \
            .all()
        # 对应的所有待结算单
        vouchers_firms = self.session.query(models.FirmSettlementVoucher, models.Firm) \
            .join(models.Firm, models.Firm.id == models.FirmSettlementVoucher.firm_id) \
            .filter(models.FirmSettlementVoucher.settlement_order_id.in_(order_ids)) \
            .all()
        firms_dict = defaultdict(set)
        [firms_dict[voucher.settlement_order_id].add(firm) for voucher, firm in vouchers_firms]

        firm_account_ids = {order.payment_account_id for order in orders}
        accounts = self.session.query(models.FirmPaymentAccount) \
            .filter(models.FirmPaymentAccount.id.in_(firm_account_ids)) \
            .all()
        account_dict = {account.id: account for account in accounts}

        order_list = []
        for order in orders:
            creator = order.creator
            settlement_account = account_dict.get(order.payment_account_id)

            firms = firms_dict.get(order.id, [])
            firms = [{
                "id": firm.id,
                "name": firm.name,
            } for firm in firms]

            order_list.append({
                "id": order.id,
                "creator_id": creator.id,
                "creator_name": creator.username,
                "create_time": TimeFunc.time_to_str(order.create_time),
                "agent_name": order.agent_name,
                "agent_phone": order.agent_phone,
                "payment": order.payment,
                "firms": firms,
                "settlement_account_id": settlement_account.id if settlement_account else 0,
                "settlement_account_num": settlement_account.account_num if settlement_account else "现金",
                "total_money": check_float(order.total_money / 100),
                "remarks": order.remarks,
            })

        all_firms = self.session.query(models.Firm) \
            .join(models.FirmSettlementVoucher, models.FirmSettlementVoucher.firm_id == models.Firm.id) \
            .filter(models.FirmSettlementVoucher.settlement_order_id.in_(unfiltered_order_ids)) \
            .distinct() \
            .all()
        all_firms = [{
            "id": firm.id,
            "name": firm.name,
        } for firm in all_firms]

        has_more = len(orders) >= limit
        return self.send_success(orders=order_list, all_firms=all_firms, has_more=has_more)


# 供货商结算汇总 注释掉的方法为原计算方法，新方法为走统计获取数据的方法
class FirmSettlementSummary(StationBaseHandler):
    @BaseHandler.check_arguments("dimension:str")
    def get(self):
        dimension = self.args["dimension"]
        if dimension == "firm":
            return self.firm_summary()
        elif dimension == "time":
            return self.time_summary()
        else:
            return self.send_fail("action invalid")

    @BaseHandler.check_arguments("scope:int", "summary_date:date",
                                 "firm_ids:?str", "page?:int", "limit?:int")
    def firm_summary(self):
        """各供货商的结算汇总"""
        scope = self.args["scope"]
        summary_date = self.args["summary_date"]
        firm_ids = self.args.get("firm_ids")
        firm_ids = set(map(lambda i: check_int(i), firm_ids.split("|"))) if firm_ids else None
        page = self.args.get("page", 0)
        limit = self.args.get("limit", 20)
        # 更新一下统计表相关信息
        update_firm_payment_statistics(self.session, self.statistic_session,
                                       station_id=self.current_station.id)
        # 汇总日期范围
        if scope == 0:
            date_start = summary_date
            date_end = summary_date + datetime.timedelta(days=1)
        elif scope == 1:
            date_start = datetime.date(summary_date.year, summary_date.month, 1)
            # 当月最后一天
            date_end = TimeFunc.add_months(date_start, 1) - datetime.timedelta(days=1)
        elif scope == 2:
            date_start = datetime.date(summary_date.year, 1, 1)
            date_end = datetime.date(summary_date.year + 1, 1, 1)
        else:
            return self.send_fail("不支持的汇总范围")
        statistics = self.statistic_session.query(models_statistics.StatisticsFirmPayment) \
            .filter(models_statistics.StatisticsFirmPayment.station_id == self.current_station.id,
                    models_statistics.StatisticsFirmPayment.statistics_type == 0,
                    func.DATE(models_statistics.StatisticsFirmPayment.statistics_date) >= date_start,
                    func.DATE(models_statistics.StatisticsFirmPayment.statistics_date) < date_end)
        # 待筛选的所有供货商 ID
        all_firm_ids = statistics.with_entities(models_statistics.StatisticsFirmPayment.firm_id).all()
        all_firm_ids = {i.firm_id for i in all_firm_ids}
        # 累计数据
        total_sum = \
            statistics.with_entities(func.count(models_statistics.StatisticsFirmPayment.settle_times),
                                     func.count(models_statistics.StatisticsFirmPayment.settle_nums),
                                     func.sum(models_statistics.StatisticsFirmPayment.settle_money)) \
            .first()
        if firm_ids:
            statistics = statistics.filter(models_statistics.StatisticsFirmPayment.firm_id.in_(firm_ids))
        statistics = statistics.all()
        all_firms = self.session.query(models.Firm) \
            .filter(models.Firm.id.in_(all_firm_ids)).all()
        firm_dict = {firm.id: firm for firm in all_firms}
        # 待筛选的所有供货商
        firms = [{"id": firm.id, "name": firm.name} for firm in all_firms]
        summary_dict = {}
        for statics in statistics:
            if statics.firm_id not in summary_dict:
                summary_dict[statics.firm_id] = {
                    "settle_times": 0,  # 结算次数
                    "settle_nums": 0,   # 结算票数
                    "settle_money": 0,  # 结算总金额
                }
            summary_dict[statics.firm_id]["settle_times"] += statics.settle_times
            summary_dict[statics.firm_id]["settle_nums"] += statics.settle_nums
            summary_dict[statics.firm_id]["settle_money"] += statics.settle_money
        # 累计数据
        settle_times = total_sum[0] or 0 if total_sum else 0
        settle_nums = total_sum[1] or 0 if total_sum else 0
        total_money = check_float(total_sum[2] or 0 / 10000) if total_sum else 0
        sum_data = {
            "times": settle_times,
            "voucher_count": settle_nums,
            "total_money": total_money,
            "firms": firms
        }
        # 汇总列表
        summarys = []
        for firm_id, summary in summary_dict.items():
            firm = firm_dict.get(firm_id)
            summarys.append({
                "firm_id": firm.id if firm else 0,
                "firm_name": firm.name if firm else "",
                "times": summary["settle_times"],
                "voucher_count": summary["settle_nums"],
                "total_money": check_float(summary["settle_money"] / 10000),
            })
        # 暂时不分页
        nomore = True
        return self.send_success(sum_data=sum_data, summarys=summarys, nomore=nomore)

    @BaseHandler.check_arguments("firm_id:int", "size:int", "from_date:date", "before_date:date")
    def time_summary(self):
        firm_id = self.args["firm_id"]
        size = self.args["size"]  # 日期范围内的汇总粒度 0-每天的汇总 1-每月的汇总
        from_date = self.args["from_date"]
        before_date = self.args["before_date"]
        # 更新一下统计表相关信息
        update_firm_payment_statistics(self.session, self.statistic_session,
                                       station_id=self.current_station.id)
        statics_date = self.statistic_session.query(models_statistics.StatisticsFirmPayment) \
            .filter(models_statistics.StatisticsFirmPayment.firm_id == firm_id,
                    func.DATE(models_statistics.StatisticsFirmPayment.statistics_date) >= from_date,
                    func.DATE(models_statistics.StatisticsFirmPayment.statistics_date) <= before_date) \
            .group_by(func.DATE(models_statistics.StatisticsFirmPayment.statistics_date)).all()
        # 汇总计算
        summary_dict = {}
        for data in statics_date:
            order_count = data.settle_times
            voucher_count = data.settle_nums
            total_money = data.settle_money
            settlement_date = data.statistics_date

            if size == 1:
                date = TimeFunc.time_to_str(settlement_date, "year")
            elif size == 0:
                date = TimeFunc.time_to_str(settlement_date, "date")
            else:
                date = TimeFunc.time_to_str(settlement_date, "date")

            if date not in summary_dict:
                summary_dict[date] = {
                    "order_count": 0,
                    "voucher_count": 0,
                    "total_money": 0,
                }

            summary_dict[date]["order_count"] += order_count
            summary_dict[date]["voucher_count"] += voucher_count
            summary_dict[date]["total_money"] += total_money

        summarys = sorted([{
            "date": key,
            "order_count": value["order_count"],
            "voucher_count": value["voucher_count"],
            "total_money": check_float(value["total_money"] / 10000),
        } for key, value in summary_dict.items()], key=lambda i: i["date"], reverse=True)

        return self.send_success(summarys=summarys)


    # @BaseHandler.check_arguments("scope:int", "summary_date:date",
    #                              "firm_ids?:str", "page?:int", "limit?:int")
    # def firm_summary(self):
    #     """各供货商的结算汇总"""
    #     scope = self.args["scope"]
    #     summary_date = self.args["summary_date"]
    #     firm_ids = self.args.get("firm_ids")
    #     firm_ids = set(map(lambda i: check_int(i), firm_ids.split("|"))) if firm_ids else None
    #     page = self.args.get("page", 0)
    #     limit = self.args.get("limit", 20)
    #
    #     # 汇总日期范围
    #     if scope == 0:
    #         date_start = summary_date
    #         date_end = summary_date + datetime.timedelta(days=1)
    #     elif scope == 1:
    #         date_start = datetime.date(summary_date.year, summary_date.month, 1)
    #         # 当月最后一天
    #         date_end = TimeFunc.add_months(date_start, 1) - datetime.timedelta(days=1)
    #     elif scope == 2:
    #         date_start = datetime.date(summary_date.year, 1, 1)
    #         date_end = datetime.date(summary_date.year + 1, 1, 1)
    #     else:
    #         return self.send_fail("不支持的汇总范围")
    #
    #     vouchers = self.session.query(models.FirmSettlementVoucher) \
    #         .join(models.FirmSettlementOrder,
    #               models.FirmSettlementOrder.id == models.FirmSettlementVoucher.settlement_order_id) \
    #         .filter(models.FirmSettlementVoucher.station_id == self.current_station.id,
    #                 models.FirmSettlementVoucher.status == 1,
    #                 func.DATE(models.FirmSettlementOrder.create_time) >= date_start,
    #                 func.DATE(models.FirmSettlementOrder.create_time) < date_end)
    #
    #     # 待筛选的所有供货商 ID
    #     all_firm_ids = vouchers.with_entities(models.FirmSettlementVoucher.firm_id).all()
    #     all_firm_ids = {i.firm_id for i in all_firm_ids}
    #     # 累计数据
    #     total_sum = vouchers.with_entities(func.count(distinct(models.FirmSettlementVoucher.settlement_order_id)),
    #                                        func.count(models.FirmSettlementVoucher.id),
    #                                        func.sum(models.FirmSettlementVoucher.settled_amount
    #                                                 * models.FirmSettlementVoucher.settled_price)) \
    #         .first()
    #
    #     if firm_ids:
    #         vouchers = vouchers.filter(models.FirmSettlementVoucher.firm_id.in_(firm_ids))
    #
    #     vouchers = vouchers.all()
    #
    #     all_firms = self.session.query(models.Firm) \
    #         .filter(models.Firm.id.in_(all_firm_ids)) \
    #         .all()
    #     firm_dict = {firm.id: firm for firm in all_firms}
    #
    #     # 待筛选的所有供货商
    #     firms = [{
    #         "id": firm.id,
    #         "name": firm.name,
    #     } for firm in all_firms]
    #
    #     summary_dict = {}
    #     for voucher in vouchers:
    #         if voucher.firm_id not in summary_dict:
    #             summary_dict[voucher.firm_id] = {
    #                 "order_ids": set(),
    #                 "voucher_count": 0,
    #                 "total_money": 0,
    #             }
    #         summary_dict[voucher.firm_id]["order_ids"].add(voucher.settlement_order_id)
    #         summary_dict[voucher.firm_id]["voucher_count"] += 1
    #         summary_dict[voucher.firm_id]["total_money"] += voucher.settled_price * voucher.settled_amount
    #
    #     # 累计数据
    #     times = total_sum[0] or 0 if total_sum else 0
    #     voucher_count = total_sum[1] or 0 if total_sum else 0
    #     total_money = check_float(total_sum[2] or 0 / 10000) if total_sum else 0
    #     sum_data = {
    #         "times": times,
    #         "voucher_count": voucher_count,
    #         "total_money": total_money,
    #         "firms": firms
    #     }
    #
    #     # 汇总列表
    #     summarys = []
    #     for firm_id, summary in summary_dict.items():
    #         firm = firm_dict.get(firm_id)
    #         summarys.append({
    #             "firm_id": firm.id if firm else 0,
    #             "firm_name": firm.name if firm else "",
    #             "times": len(summary["order_ids"]),
    #             "voucher_count": summary["voucher_count"],
    #             "total_money": check_float(summary["total_money"] / 10000),
    #         })
    #
    #     # 暂时不分页
    #     nomore = True
    #     return self.send_success(sum_data=sum_data, summarys=summarys, nomore=nomore)
    #
    # @BaseHandler.check_arguments("firm_id:int", "size:int", "from_date:date", "before_date:date")
    # def time_summary(self):
    #     firm_id = self.args["firm_id"]
    #     size = self.args["size"]  # 日期范围内的汇总粒度 0-每天的汇总 1-每月的汇总
    #     from_date = self.args["from_date"]
    #     before_date = self.args["before_date"]
    #
    #     vouchers_data = self.session.query(func.count(distinct(models.FirmSettlementVoucher.settlement_order_id)),
    #                                        func.count(models.FirmSettlementVoucher.id),
    #                                        func.sum(models.FirmSettlementVoucher.settled_amount
    #                                                 * models.FirmSettlementVoucher.settled_price),
    #                                        models.FirmSettlementOrder.create_time) \
    #         .join(models.FirmSettlementOrder, models.FirmSettlementOrder.id == models.FirmSettlementVoucher.settlement_order_id) \
    #         .filter(func.DATE(models.FirmSettlementOrder.create_time) >= from_date,
    #                 func.DATE(models.FirmSettlementOrder.create_time) < before_date,
    #                 models.FirmSettlementVoucher.status == 1,
    #                 models.FirmSettlementVoucher.firm_id == firm_id) \
    #         .group_by(func.DATE(models.FirmSettlementOrder.create_time)) \
    #         .all()
    #
    #     # 汇总计算
    #     summary_dict = {}
    #     for data in vouchers_data:
    #         order_count = data[0]
    #         voucher_count = data[1]
    #         total_money = data[2]
    #         settlement_date = data[3]
    #
    #         if size == 1:
    #             date = TimeFunc.time_to_str(settlement_date, "year")
    #         elif size == 0:
    #             date = TimeFunc.time_to_str(settlement_date, "date")
    #         else:
    #             date = TimeFunc.time_to_str(settlement_date, "date")
    #
    #         if date not in summary_dict:
    #             summary_dict[date] = {
    #                 "order_count": 0,
    #                 "voucher_count": 0,
    #                 "total_money": 0,
    #             }
    #
    #         summary_dict[date]["order_count"] += order_count
    #         summary_dict[date]["voucher_count"] += voucher_count
    #         summary_dict[date]["total_money"] += total_money
    #
    #     summarys = sorted([{
    #         "date": key,
    #         "order_count": value["order_count"],
    #         "voucher_count": value["voucher_count"],
    #         "total_money": check_float(value["total_money"] / 10000),
    #     } for key, value in summary_dict.items()], key=lambda i: i["date"], reverse=True)
    #
    #     return self.send_success(summarys=summarys)
