# -*- coding: utf-8 -*-
import datetime
import sqlalchemy

from sqlalchemy import func, and_, or_, distinct
from handlers.base.pub_func import TimeFunc, check_float, check_int
from handlers.base.pub_receipt import ReceiptPrinter
from handlers.base.pub_statistic import update_shop_financial_statistics, update_station_fee_statistics
from handlers.base.pub_web import DemandBaseHandler, StationBaseHandler
from handlers.base.pub_web import BaseHandler
from dal import models, models_statistics
from collections import defaultdict


# 费用
class Fee(StationBaseHandler):
    @BaseHandler.check_arguments("date:date", "fee_list:list")
    def post(self):
        date = self.args["date"]
        fee_list = self.args["fee_list"]

        valid, message = self.validate_fee_list(fee_list)
        if not valid:
            return self.send_fail(message)

        for fee in fee_list:
            type = check_int(fee["type"])
            money = check_float(fee["money"])
            remarks = fee.get("remarks", "")

            new_fee = models.Fee(
                date=date,
                type=type,
                money=check_int(money * 100),
                remarks=remarks,
                station_id=self.current_station.id,
                creator_id=self.current_user.id,
            )
            self.session.add(new_fee)

        self.session.commit()
        return self.send_success()

    def validate_fee_list(self, fee_list):
        """验证费用列表参数"""

        if not isinstance(fee_list, list):
            return False, "费用列表参数格式有误"

        for fee in fee_list:
            if not isinstance(fee, dict):
                return False, "费用列表参数项格式有误"

            if "type" not in fee:
                return False, "参数缺失：type"
            elif check_int(fee["type"]) not in (1, 2):
                return False, "参数无效：type == {}".format(fee["type"])
            if "money" not in fee:
                return False, "参数缺失：money"
            elif check_float(fee["money"]) > 21474836:
                return False, "金额过大"
            if "remarks" in fee and len(fee["remarks"]) > 128:
                return False, "备注不能超过 128 个字符"

        return True, ""


# 费用列表
class FeeList(StationBaseHandler):
    @BaseHandler.check_arguments("types?:list", "date?:date", "from_date?:date", "before_date?:date", "page?:int", "limit?:int")
    def get(self):
        fee_types = self.args.get("types")
        date = self.args.get("date")
        from_date = self.args.get("from_date")
        before_date = self.args.get("before_date")
        page = self.args.get("page", 0)
        limit = self.args.get("limit", 20)

        fees = self.session.query(models.Fee) \
            .filter(models.Fee.station_id == self.current_station.id)

        if fee_types is not None:
            fees = fees.filter(models.Fee.type.in_(fee_types))
        if date is not None:
            fees = fees.filter(models.Fee.date == date)
        if from_date is not None:
            fees = fees.filter(models.Fee.date >= from_date)
        if before_date is not None:
            fees = fees.filter(models.Fee.date < before_date)

        fee_sum = fees.with_entities(func.sum(models.Fee.money)).scalar() or 0
        fee_sum = check_float(fee_sum / 100)

        fees = fees.order_by(models.Fee.date.desc()).offset(page * limit).limit(limit).all()

        fee_list = []
        for fee in fees:
            creator = fee.creator
            fee_list.append({
                "id": fee.id,
                "date": TimeFunc.time_to_str(fee.date, "date"),
                "type": fee.type,
                "money": check_float(fee.money / 100),
                "remarks": fee.remarks,
                "creator_id": creator.id,
                "creator_name": creator.username,
                "create_time": TimeFunc.time_to_str(fee.create_time),
            })

        has_more = len(fee_list) >= limit
        return self.send_success(fee_sum=fee_sum, fees=fee_list, has_more=has_more)


# 费用汇总 注释掉的GET方法是原直接查询，新写的GET方法通过统计表拿数据
class FeeSummaryList(StationBaseHandler):
    # @BaseHandler.check_arguments("scope:int", "page?:int", "limit?:int",
    #                              "from_date?:date", "to_date?:date")
    # def get(self):
    #     scope = self.args["scope"]
    #     page = self.args.get("page", 0)
    #     limit = self.args.get("limit", 20)
    #
    #     # 先拿到所有的日期对象，以limit为
    #     if scope == 0:
    #         fee_dates = self.session.query(models.Fee.date) \
    #             .filter(models.Fee.station_id == self.current_station.id) \
    #             .order_by(models.Fee.date.desc())
    #         voucher_dates = self.session.query(func.DATE(models.FirmSettlementVoucher.create_time)) \
    #             .filter(models.FirmSettlementVoucher.station_id == self.current_station.id) \
    #             .order_by(models.FirmSettlementVoucher.create_time.desc())
    #         dates = fee_dates.union(voucher_dates) \
    #             .distinct() \
    #             .offset(page * limit) \
    #             .limit(limit) \
    #             .all()
    #     else:
    #         # TODO 月年的因为数据量不会多于 20 条，暂时不分页
    #         fee_dates = self.session.query(models.Fee.date) \
    #             .filter(models.Fee.station_id == self.current_station.id)
    #         voucher_dates = self.session.query(func.DATE(models.FirmSettlementVoucher.create_time)) \
    #             .filter(models.FirmSettlementVoucher.station_id == self.current_station.id)
    #         dates = fee_dates.union(voucher_dates) \
    #             .distinct() \
    #             .all()
    #
    #     from_date = datetime.date.today()
    #     to_date = datetime.date.today()
    #     dates = [date[0] for date in dates]
    #     for date in dates:
    #         if date < from_date:
    #             from_date = date
    #         if date > to_date:
    #             to_date = date
    #
    #     # 上面都可以不用改，作为传参就可以了，上面确定了具体的from_date以及to_Date
    #     # 可以根据具体的
    #     fee_sums = self.session.query(models.Fee.date,
    #                                   func.sum(func.IF(models.Fee.type == 1, models.Fee.money, 0)).label("delivery"),
    #                                   func.sum(func.IF(models.Fee.type == 2, models.Fee.money, 0)).label("routine")) \
    #         .filter(models.Fee.station_id == self.current_station.id,
    #                 models.Fee.date >= from_date,
    #                 models.Fee.date <= to_date) \
    #         .group_by(models.Fee.date) \
    #         .all()
    #     print(fee_sums)
    #     # god somebody help me with this plz
    #     vouchers = self.session.query(models.FirmSettlementVoucher,
    #                                   models.AllocationOrder,
    #                                   models.PurchaseOrderGoods) \
    #         .join(models.AllocationOrder, models.AllocationOrder.id == models.FirmSettlementVoucher.allocation_order_id) \
    #         .join(models.PurchaseOrderGoods, models.PurchaseOrderGoods.id == models.AllocationOrder.purchase_order_goods_id) \
    #         .filter(models.FirmSettlementVoucher.station_id == self.current_station.id,
    #                 func.DATE(models.FirmSettlementVoucher.create_time) >= from_date,
    #                 func.DATE(models.FirmSettlementVoucher.create_time) <= to_date) \
    #         .all()
    #
    #     # 计算结算件数
    #     allocation_order_ids = {order.id for _, order, _ in vouchers}
    #     allocated_amount_sums = self.session.query(models.AllocationOrderGoods.order_id,
    #                                                func.sum(models.AllocationOrderGoods.allocated_amount)) \
    #         .filter(models.AllocationOrderGoods.order_id.in_(allocation_order_ids)) \
    #         .group_by(models.AllocationOrderGoods.order_id) \
    #         .all()
    #     allocated_amount_sum_dict = {data[0]: data[1] for data in allocated_amount_sums}
    #
    #     def scoped_date(date):
    #         if scope == 0:
    #             date = TimeFunc.time_to_str(date, "date")
    #         elif scope == 1:
    #             date = TimeFunc.time_to_str(date, "year")
    #         else:
    #             date = TimeFunc.time_to_str(date, "year_only")
    #         return date
    #
    #     # 待结算单总金额
    #     voucher_sum_dict = defaultdict(int)
    #     for voucher, allocation, purchase_goods in vouchers:
    #         amount = allocated_amount_sum_dict.get(allocation.id, 0)
    #         # 采购价，按件数比例计算，实配件数/采购件数*小计
    #         total_money = check_float(amount / purchase_goods.actual_amount * purchase_goods.subtotal)
    #         date = scoped_date(voucher.create_time)
    #         voucher_sum_dict[date] += total_money
    #
    #     # 按指定范围求和
    #     fee_summary_dict = {}
    #     for date, delivery, routine in fee_sums:
    #         date = scoped_date(date)
    #         if date not in fee_summary_dict:
    #             fee_summary_dict[date] = {
    #                 "delivery_sum": 0,
    #                 "routine_sum": 0,
    #             }
    #         fee_summary_dict[date]["delivery_sum"] += delivery or 0
    #         fee_summary_dict[date]["routine_sum"] += routine or 0
    #     print(fee_summary_dict)
    #
    #     # 结果列表日期去重
    #     print(dates)
    #     result_dates = {scoped_date(date) for date in dates}
    #     print(result_dates)
    #
    #     # 汇总列表
    #     summarys = []
    #     for date in result_dates:
    #         voucher_sum = voucher_sum_dict.get(date, 0)
    #         fee_summary = fee_summary_dict.get(date)
    #
    #         summarys.append({
    #             "date": date,
    #             "voucher_sum": check_float(voucher_sum / 100),
    #             "delivery_sum": check_float(fee_summary["delivery_sum"] / 100) if fee_summary else 0,
    #             "routine_sum": check_float(fee_summary["routine_sum"] / 100) if fee_summary else 0,
    #         })
    #
    #     summarys = sorted(summarys, key=lambda i: i["date"], reverse=True)
    #
    #     has_more = len(summarys) >= limit
    #     return self.send_success(summarys=summarys, has_more=has_more)

    @BaseHandler.check_arguments("scope:int", "page?:int", "limit?:int",
                                 "from_date?:date", "to_date?:date")
    def get(self):
        scope = self.args.get("scope", 0)
        page = self.args.get("page", 0)
        limit = self.args.get("limit", 20)
        from_date = self.args.get("from_date")
        to_date = self.args.get("to_date")
        if scope not in [0, 1, 2]:
            return self.send_fail("scope invalid")
        # 更新一下统计表信息
        update_station_fee_statistics(self.session, self.statistic_session,
                                      station_id=self.current_station.id)
        date_query = None
        if scope == 0:
            date_query = \
                func.DATE(models_statistics.StatisticsStationFee.statistics_date).label("data_date")
        elif scope == 1:
            date_query = \
                func.date_format(models_statistics.StatisticsStationFee.statistics_date, "%Y-%m").label("data_date")
        elif scope == 2:
            date_query = \
                func.date_format(models_statistics.StatisticsStationFee.statistics_date, "%Y").label("data_date")
        packing_sums = \
            self.statistic_session.query(
                date_query, models_statistics.StatisticsStationFee.station_id,
                func.sum(models_statistics.StatisticsStationFee.voucher_sum).label("voucher_sum"),
                func.sum(models_statistics.StatisticsStationFee.delivery_sum).label("delivery_sum"),
                func.sum(models_statistics.StatisticsStationFee.routine_sum).label("routine_sum")
            ).filter(models_statistics.StatisticsStationFee.station_id == self.current_station.id,
                     models_statistics.StatisticsStationFee.statistics_type == 0)
        # 指定日期段筛选，为日后可能做准备
        if from_date:
            packing_sums = packing_sums.filter(models_statistics.StatisticsStationFee.statistics_date >= from_date)
        if to_date:
            packing_sums = packing_sums.filter(models_statistics.StatisticsStationFee.statistics_date <= to_date)
        # 默认排序一下
        packing_sums = packing_sums.order_by(models_statistics.StatisticsStationFee.statistics_date.desc())
        packing_sums = packing_sums.group_by("data_date", models_statistics.StatisticsStationFee.station_id) \
            .offset(page * limit).limit(limit).all()
        summarys = []
        for packing_data in packing_sums:
            voucher_sum = check_float(packing_data.voucher_sum / 100)
            delivery_sum = check_float(packing_data.delivery_sum / 100)
            routine_sum = check_float(packing_data.routine_sum / 100)
            if scope == 0:
                date = TimeFunc.time_to_str(packing_data.data_date, "date")
            else:
                date = packing_data.data_date

            summarys.append({
                "date": date,
                "voucher_sum": voucher_sum,
                "delivery_sum": delivery_sum,
                "routine_sum": routine_sum
            })
        summarys = sorted(summarys, key=lambda i: i["date"], reverse=True)
        has_more = len(summarys) >= limit
        return self.send_success(summarys=summarys, has_more=has_more)

# 门店其他支出
class ShopPayout(StationBaseHandler):
    @BaseHandler.check_arguments("type?:str", "money:float", "remarks?:str")
    def update_payout(self, payout):
        payout_type = self.args.get("type", "")
        money = self.args["money"]
        remarks = self.args.get("remarks", "")
        payout.type = payout_type
        payout.money = check_int(money * 100)
        payout.remarks = remarks

    @BaseHandler.check_arguments("shop_id:int", "date?:date")
    def post(self):
        shop_id = self.args["shop_id"]
        date = self.args.get("date", datetime.date.today())

        shop = models.Shop.get_by_id(self.session, shop_id, self.current_station.id)
        if not shop:
            return self.send_fail("没有找到对应的店铺")

        new_payout = models.ShopPayout(
            station_id=self.current_station.id,
            creator_id=self.current_user.id,
            shop_id=shop_id,
            date=date,
        )
        self.session.add(new_payout)

        self.update_payout(new_payout)

        self.session.commit()
        return self.send_success()

    @BaseHandler.check_arguments()
    def put(self, payout_id):
        payout = models.ShopPayout.get_by_id(self.session, payout_id, self.current_station.id)
        if not payout:
            return self.send_fail("没有找到对应的记录")

        self.update_payout(payout)

        self.session.commit()
        return self.send_success()

    def delete(self, payout_id):
        payout = models.ShopPayout.get_by_id(self.session, payout_id, self.current_station.id)
        if not payout:
            return self.send_fail("没有找到对应的记录")

        payout.status = -1

        self.session.commit()
        return self.send_success()


# 门店其他支出列表
class ShopPayoutList(StationBaseHandler):
    @BaseHandler.check_arguments("from_date?:date", "to_date?:date", "before_date?:date", "shop_id:int", "order_by?:str", "asc?:bool")
    def get(self):
        shop_id = self.args["shop_id"]
        from_date = self.args.get("from_date")
        to_date = self.args.get("to_date")
        before_date = self.args.get("before_date")
        order_by = self.args.get("order_by")
        asc = self.args.get("asc", False)
        page = self.args.get("page", 0)
        limit = self.args.get("limit", 20)

        payouts = self.session.query(models.ShopPayout, models.AccountInfo) \
            .join(models.AccountInfo) \
            .filter(models.ShopPayout.station_id == self.current_station.id,
                    models.ShopPayout.shop_id == shop_id)

        if from_date:
            payouts = payouts.filter(models.ShopPayout.date >= from_date)
        if to_date:
            payouts = payouts.filter(models.ShopPayout.date <= to_date)
        if before_date:
            payouts = payouts.filter(models.ShopPayout.date < before_date)

        payout_sum = payouts.with_entities(func.sum(models.ShopPayout.money)).first()

        if order_by == "money":
            if asc:
                payouts = payouts.order_by(models.ShopPayout.money.asc())
            else:
                payouts = payouts.order_by(models.ShopPayout.money.desc())

        payouts = payouts.offset(page * limit).limit(limit).all()

        data_list = []
        for payout, creator in payouts:
            data_list.append({
                "id": payout.id,
                "creator": creator.username,
                "create_time": TimeFunc.time_to_str(payout.create_time),
                "type": payout.type,
                "money": check_float(payout.money / 100),
                "remarks": payout.remarks,
            })

        sum_data = {
            "money": check_float((payout_sum[0] or 0) / 100) if payout_sum else 0,
        }

        has_more = len(data_list) >= limit
        return self.send_success(data_list=data_list, sum_data=sum_data, has_more=has_more)


# 门店对账列表
class ShopAccountingList(StationBaseHandler):
    @BaseHandler.check_arguments("from_date?:date", "to_date?:date", "before_date?:date", "shop_ids?:str", "scope?:int",
                                 "order_by?:str", "asc?:bool", "page?:int", "limit?:int")
    def get(self):
        from_date = self.args.get("from_date")
        to_date = self.args.get("to_date")
        before_date = self.args.get("before_date")
        shop_ids_filter = set(map(lambda x: check_int(x), self.args.get("shop_ids", "").split("|"))) - {0}
        scope = self.args.get("scope", 0)
        order_by = self.args.get("order_by")
        asc = self.args.get("asc", False)
        page = self.args.get("page", 0)
        limit = self.args.get("limit", 20)

        if scope not in [0, 1, 2]:
            return self.send_fail("scope invalid")

        update_shop_financial_statistics(self.session, self.statistic_session,
                                         station_id=self.current_station.id)

        date_query = None
        if scope == 0:
            date_query = func.DATE(models_statistics.StatisticsShopFinancial.statistics_date).label("data_date")
        elif scope == 1:
            date_query = func.date_format(models_statistics.StatisticsShopFinancial.statistics_date, "%Y-%m").label("data_date")
        elif scope == 2:
            date_query = func.date_format(models_statistics.StatisticsShopFinancial.statistics_date, "%Y").label("data_date")

        packing_sums = self.statistic_session.query(date_query,
                                                    models_statistics.StatisticsShopFinancial.shop_id,
                                                    func.sum(models_statistics.StatisticsShopFinancial.allocation_money).label("allocation_money"),
                                                    func.sum(models_statistics.StatisticsShopFinancial.shop_payout_money).label("shop_payout_money")) \
            .filter(models_statistics.StatisticsShopFinancial.station_id == self.current_station.id,
                    models_statistics.StatisticsShopFinancial.statistics_type == 0)

        # 待筛选的门店列表
        shop_ids = packing_sums.with_entities(models_statistics.StatisticsShopFinancial.shop_id).distinct().all()
        shop_ids = {i[0] for i in shop_ids}
        shops = self.session.query(models.Shop) \
            .filter(models.Shop.id.in_(shop_ids)) \
            .all()
        shop_dict = {s.id: s for s in shops}

        # 门店筛选
        if shop_ids_filter:
            packing_sums = packing_sums.filter(models_statistics.StatisticsShopFinancial.shop_id.in_(shop_ids_filter))

        if from_date:
            packing_sums = packing_sums.filter(models_statistics.StatisticsShopFinancial.statistics_date >= from_date)
        if to_date:
            packing_sums = packing_sums.filter(models_statistics.StatisticsShopFinancial.statistics_date <= to_date)
        if before_date:
            packing_sums = packing_sums.filter(models_statistics.StatisticsShopFinancial.statistics_date < before_date)

        if order_by == "other_payout":
            if asc:
                packing_sums = packing_sums.order_by(sqlalchemy.asc(models_statistics.StatisticsShopFinancial.shop_payout_money))
            else:
                packing_sums = packing_sums.order_by(sqlalchemy.desc(models_statistics.StatisticsShopFinancial.shop_payout_money))
        elif order_by == "packing_money":
            if asc:
                packing_sums = packing_sums.order_by(sqlalchemy.asc(models_statistics.StatisticsShopFinancial.allocation_money))
            else:
                packing_sums = packing_sums.order_by(sqlalchemy.desc(models_statistics.StatisticsShopFinancial.allocation_money))
        elif order_by == "payout_sum":
            if asc:
                packing_sums = packing_sums.order_by(sqlalchemy.asc(func.sum(models_statistics.StatisticsShopFinancial.allocation_money
                                                                             + models_statistics.StatisticsShopFinancial.shop_payout_money)))
            else:
                packing_sums = packing_sums.order_by(sqlalchemy.desc(func.sum(models_statistics.StatisticsShopFinancial.allocation_money
                                                                              + models_statistics.StatisticsShopFinancial.shop_payout_money)))
        else:
            packing_sums = packing_sums.order_by(models_statistics.StatisticsShopFinancial.statistics_date.desc())

        # 累计实配金额
        payout_money_sum = packing_sums.with_entities(func.sum(models_statistics.StatisticsShopFinancial.allocation_money),
                                                      func.sum(models_statistics.StatisticsShopFinancial.shop_payout_money)) \
            .first()

        packing_sums = packing_sums.group_by("data_date", models_statistics.StatisticsShopFinancial.shop_id) \
            .offset(page * limit) \
            .limit(limit) \
            .all()

        data_list = []
        for packing_data in packing_sums:
            packing_money = check_float(packing_data.allocation_money / 100)
            other_payout = check_float(packing_data.shop_payout_money / 100)
            if scope == 0:
                payout_date = TimeFunc.time_to_str(packing_data.data_date, "date")
            else:
                payout_date = packing_data.data_date

            shop = shop_dict.get(packing_data.shop_id)

            data_list.append({
                "date": payout_date,
                "shop_id": shop.id if shop else 0,
                "shop_name": shop.abbreviation if shop else "已删除",
                "packing_money": packing_money,
                "other_payout": other_payout,
                "payout_sum": check_float(packing_money + other_payout)
            })

        packing_money_sum = (payout_money_sum[0] or 0) if payout_money_sum else 0
        other_payout_sum = (payout_money_sum[1] or 0) if payout_money_sum else 0
        sum_data = {
            "shops": [{
                "id": shop.id,
                "name": shop.abbreviation,
            } for shop in shops],
            "packing_money": check_float(packing_money_sum / 100),
            "other_payout": check_float(other_payout_sum / 100),
            "payout_sum": check_float((packing_money_sum + other_payout_sum) / 100),
        }

        has_more = len(data_list) >= limit
        return self.send_success(data_list=data_list, sum_data=sum_data, has_more=has_more)
