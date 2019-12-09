import copy
import datetime
import os
import sys
import time
from multiprocessing import Process

from sqlalchemy import func, and_

from handlers.base.pub_func import check_int

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../../")))

from sqlalchemy import func, and_, or_, distinct
from tornado.options import options, define
from handlers.base.pub_func import TimeFunc, check_float, check_int
from collections import defaultdict
import dal.models_statistics as models_statistics
import dal.models as models
from dal.db_configs import DBSession,statistic_DBSession


def update_firm_payment_statistics(session, statistics_session, specific_date=None,
                                   station_id=None, scope=0):
    # specific_date应该为一个Date对象
    firm_statistics = statistics_session.query(models_statistics.StatisticsFirmPayment) \
        .filter_by(statistics_type=0)
    if station_id:
        firm_statistics = firm_statistics.filter_by(station_id=station_id)
    if specific_date:
        firm_statistics = firm_statistics.filter_by(statistics_date=specific_date)
    firm_statistics_list = firm_statistics.all()
    firm_sta_dict = {"{}:{}:{}".format(
        s.statistics_date, s.station_id, s.firm_id): s for s in firm_statistics_list}
    # 更新数据
    vouchers = session.query(models.FirmSettlementVoucher, models.FirmSettlementOrder) \
        .join(models.FirmSettlementOrder,
              models.FirmSettlementOrder.id == models.FirmSettlementVoucher.settlement_order_id) \
        .filter(models.FirmSettlementVoucher.status == 1)
    if specific_date:
        vouchers = vouchers.filter(models.FirmSettlementOrder.statistics_date == specific_date)
    if station_id:
        vouchers = vouchers.filter_by(station_id=station_id)
    # 待筛选的所有供货商 ID
    all_firm_ids = vouchers.with_entities(models.FirmSettlementVoucher.firm_id).all()
    all_firm_ids = {i.firm_id for i in all_firm_ids}
    vouchers = vouchers.all()
    all_firms = session.query(models.Firm) \
        .filter(models.Firm.id.in_(all_firm_ids)) \
        .all()
    firm_dict = {firm.id: firm for firm in all_firms}
    summary_dict = {}
    #  改走统计表的形式，依据统计表的数据结构，需要保证firm_id与date的组合为唯一
    for voucher, voucher_order in vouchers:
        key_date = TimeFunc.time_to_str(voucher_order.create_time, "date")
        if voucher.firm_id not in summary_dict:
            summary_dict[voucher.firm_id] = {}
            summary_dict[voucher.firm_id][key_date] = {
                "order_ids": set(),
                "voucher_count": 0,  # 结算次数
                "total_money": 0,   # 总价钱
            }
        elif not summary_dict.get(voucher.firm_id, {}).get(key_date):
            summary_dict[voucher.firm_id][key_date] = {
                "order_ids": set(),
                "voucher_count": 0,  # 结算次数
                "total_money": 0,   # 总价钱
            }
        summary_dict[voucher.firm_id][key_date]["order_ids"].add(voucher.settlement_order_id)
        summary_dict[voucher.firm_id][key_date]["voucher_count"] += 1
        summary_dict[voucher.firm_id][key_date]["total_money"] += voucher.settled_price * voucher.settled_amount
        summary_dict[voucher.firm_id][key_date]["date"] = func.DATE(voucher_order.create_time)
        summary_dict[voucher.firm_id][key_date]["station_id"] = voucher_order.station_id

    for firm_id, date_summary_dict in summary_dict.items():
        firm = firm_dict.get(firm_id)
        for key_date, summary in date_summary_dict.items():
            date = summary["date"]
            station_id = summary["station_id"]
            firm_id = firm.id if firm else 0
            key = "{}:{}:{}".format(key_date, station_id, firm_id)
            settle_times = len(summary["order_ids"])
            settle_nums = summary["voucher_count"]
            settle_money = summary["total_money"]
            firm_sta = firm_sta_dict.get(key)
            if not firm_sta:
                new_statistics_firm_payment = \
                    models_statistics.StatisticsFirmPayment(statistics_date=date,
                                                            statistics_type=0,
                                                            station_id=station_id,
                                                            firm_id=firm_id,
                                                            settle_times=settle_times,
                                                            settle_nums=settle_nums,
                                                            settle_money=settle_money)
                statistics_session.add(new_statistics_firm_payment)
                statistics_session.flush()
            else:
                firm_sta.settle_times = settle_times
                firm_sta.settle_nums = settle_nums
                firm.settle_money = settle_money
    statistics_session.commit()


def update_station_fee_statistics(session, statistics_session, specific_date=None,
                                  station_id=None, scope=0):
    # 先拿到所有的日期对象
    if station_id:
        if scope == 0:
            fee_dates = session.query(models.Fee.date) \
                .filter(models.Fee.station_id == station_id).order_by(models.Fee.date.desc())
            voucher_dates = session.query(func.DATE(models.FirmSettlementVoucher.create_time)) \
                .filter(models.FirmSettlementVoucher.station_id == station_id) \
                .order_by(models.FirmSettlementVoucher.create_time.desc())
            dates = fee_dates.union(voucher_dates).distinct().all()
        else:
            fee_dates = session.query(models.Fee.date) \
                .filter(models.Fee.station_id == station_id)
            voucher_dates = session.query(func.DATE(models.FirmSettlementVoucher.create_time)) \
                .filter(models.FirmSettlementVoucher.station_id == station_id)
            dates = fee_dates.union(voucher_dates).distinct().all()
    else:
        if scope == 0:
            fee_dates = session.query(models.Fee.date).order_by(models.Fee.date.desc())
            voucher_dates = session.query(func.DATE(models.FirmSettlementVoucher.create_time)) \
                .order_by(models.FirmSettlementVoucher.create_time.desc())
            dates = fee_dates.union(voucher_dates).distinct().all()
        else:
            fee_dates = session.query(models.Fee.date)
            voucher_dates = session.query(func.DATE(models.FirmSettlementVoucher.create_time))
            dates = fee_dates.union(voucher_dates).distinct().all()
    dates = [date[0] for date in dates]
    fee_statistics = statistics_session.query(models_statistics.StatisticsStationFee) \
        .filter_by(statistics_type=0)
    if station_id:
        fee_statistics = fee_statistics.filter_by(station_id=station_id)
    if specific_date:
        fee_statistics = fee_statistics.filter_by(statistics_date=specific_date)
    fee_statistics_list = fee_statistics.all()
    # 先拿到当前已有的全部统计表
    fee_sta_dict = {"{}:{}".format(s.statistics_date, s.station_id): s for s in fee_statistics_list}

    # 对费用统计表，需要取到三个值，分别是采购费用，运杂费，日常杂费
    # 对financial里实时更新的方法进行修改放到公共方法里
    fee_sums = session.query(models.Fee.date,
                             func.sum(func.IF(models.Fee.type == 1,
                                              models.Fee.money, 0)).label("delivery"),
                             func.sum(func.IF(models.Fee.type == 2,
                                              models.Fee.money, 0)).label("routine"),
                             models.Fee.station_id)

    if station_id:
        fee_sums = fee_sums.filter(models.Fee.station_id == station_id)
    if specific_date:
        fee_sums = fee_sums.filter(models.Fee.date == specific_date)
    fee_sums = fee_sums.group_by(models.Fee.date).all()

    vouchers = session.query(models.FirmSettlementVoucher,
                             models.AllocationOrder,
                             models.PurchaseOrderGoods) \
        .join(models.AllocationOrder,
              models.AllocationOrder.id == models.FirmSettlementVoucher.allocation_order_id) \
        .join(models.PurchaseOrderGoods,
              models.PurchaseOrderGoods.id == models.AllocationOrder.purchase_order_goods_id)
    if station_id:
        vouchers = vouchers.filter(models.FirmSettlementVoucher.station_id == station_id)
    if specific_date:
        vouchers = vouchers.filter(func.DATE(models.FirmSettlementVoucher.create_time) == specific_date)
    vouchers = vouchers.all()

    # 计算结算件数
    allocation_order_ids = {order.id for _, order, _ in vouchers}
    allocated_amount_sums = session.query(models.AllocationOrderGoods.order_id,
                                          func.sum(models.AllocationOrderGoods.allocated_amount)) \
        .filter(models.AllocationOrderGoods.order_id.in_(allocation_order_ids)) \
        .group_by(models.AllocationOrderGoods.order_id) \
        .all()
    allocated_amount_sum_dict = {data[0]: data[1] for data in allocated_amount_sums}

    def scoped_date(date_param):
        if scope == 0:
            str_result = TimeFunc.time_to_str(date_param, "date")
        elif scope == 1:
            str_result = TimeFunc.time_to_str(date_param, "year")
        else:
            str_result = TimeFunc.time_to_str(date_param, "year_only")
        return str_result

    # 待结算单总金额
    voucher_sum_dict = defaultdict(int)
    voucher_station_dict = {}
    for voucher, allocation, purchase_goods in vouchers:
        amount = allocated_amount_sum_dict.get(allocation.id, 0)
        # 采购价，按件数比例计算，实配件数/采购件数*小计
        total_money = check_float(amount / purchase_goods.actual_amount * purchase_goods.subtotal)
        date = scoped_date(voucher.create_time)
        voucher_sum_dict[date] += total_money
        voucher_station_dict[date] = voucher.station_id
    # 按指定范围求和
    fee_summary_dict = {}
    for date, delivery, routine, station_id in fee_sums:
        date = scoped_date(date)
        if date not in fee_summary_dict:
            fee_summary_dict[date] = {
                "delivery_sum": 0,
                "routine_sum": 0,
                "station_id": station_id
            }
        fee_summary_dict[date]["delivery_sum"] += delivery or 0
        fee_summary_dict[date]["routine_sum"] += routine or 0
    result_dates = {scoped_date(date) for date in dates}
    for date in result_dates:
        voucher_sum = voucher_sum_dict.get(date, 0)
        fee_summary = fee_summary_dict.get(date)
        # 包含当日有采购和未采购但有其他费用的情况
        station_id = voucher_station_dict.get(date) or fee_summary["station_id"]
        delivery_sum = check_float(fee_summary["delivery_sum"]) if fee_summary else 0
        routine_sum = check_float(fee_summary["routine_sum"]) if fee_summary else 0
        key = "{}:{}".format(date, station_id)
        statistics = fee_sta_dict.get(key)
        if not statistics:
            new_fee_statistic = models_statistics.StatisticsStationFee(
                statistics_date=date, statistics_type=0,
                station_id=station_id, voucher_sum=voucher_sum,
                delivery_sum=delivery_sum, routine_sum=routine_sum)
            statistics_session.add(new_fee_statistic)
            statistics_session.flush()
            fee_sta_dict[key] = new_fee_statistic
        else:
            statistics.routine_sum = routine_sum
            statistics.delivery_sum = delivery_sum
            statistics.voucher_sum = voucher_sum_dict.get(date, 0)
    statistics_session.commit()


# 门店对账统计
def update_shop_financial_statistics(session, statistics_session, update_packing=True, update_shop_payout=True,
                                     date=None, station_id=None, shop_ids=None):

    statistics_list = statistics_session.query(models_statistics.StatisticsShopFinancial) \
        .filter(models_statistics.StatisticsShopFinancial.statistics_type == 0)
    if date is not None:
        statistics_list = statistics_list.filter(models_statistics.StatisticsShopFinancial.statistics_date == date)
    if station_id is not None:
        statistics_list = statistics_list.filter(models_statistics.StatisticsShopFinancial.station_id == station_id)
    if shop_ids is not None:
        statistics_list = statistics_list.filter(models_statistics.StatisticsShopFinancial.shop_id.in_(shop_ids))
    statistics_list = statistics_list.all()
    statistics_dict = {"{}:{}".format(s.statistics_date, s.shop_id): s for s in statistics_list}

    if update_packing:
        packing_sums = session.query(func.DATE(models.AllocationOrderGoods.create_time).label("create_date"),
                                     models.AllocationOrderGoods.shop_id,
                                     models.Shop,
                                     func.count(models.AllocationOrder.id).label("allocated_count"),
                                     func.sum(models.ShopPackingPrice.price
                                              * models.AllocationOrderGoods.actual_allocated_amount).label("allocated_sum")) \
            .join(models.Shop, models.Shop.id == models.AllocationOrderGoods.shop_id) \
            .join(models.AllocationOrder, models.AllocationOrder.id == models.AllocationOrderGoods.order_id) \
            .join(models.ShopPackingPrice, and_(models.ShopPackingPrice.shop_id == models.AllocationOrderGoods.shop_id,
                                                models.ShopPackingPrice.wish_order_id == models.AllocationOrder.wish_order_id,
                                                models.ShopPackingPrice.goods_id == models.AllocationOrder.goods_id)) \
            .filter(models.AllocationOrder.status == 1)

        if date is not None:
            packing_sums = packing_sums.filter(func.DATE(models.AllocationOrderGoods.create_time) == date)
        if station_id is not None:
            packing_sums = packing_sums.filter(models.AllocationOrder.station_id == station_id)
        if shop_ids is not None:
            packing_sums = packing_sums.filter(models.AllocationOrderGoods.shop_id.in_(shop_ids))

        packing_sums = packing_sums.group_by(func.DATE(models.AllocationOrderGoods.create_time),
                                             models.AllocationOrderGoods.shop_id).all()

        for packing_sum in packing_sums:
            key = "{}:{}".format(packing_sum.create_date, packing_sum.shop_id)
            statistics = statistics_dict.get(key)
            if not statistics:
                statistics = models_statistics.StatisticsShopFinancial(
                    statistics_date=packing_sum.create_date,
                    statistics_type=0,
                    station_id=packing_sum.Shop.station_id,
                    shop_id=packing_sum.shop_id,
                )
                statistics_session.add(statistics)
                statistics_session.flush()
                statistics_dict[key] = statistics

            statistics.allocation_count = packing_sum.allocated_count or 0
            statistics.allocation_money = check_int((packing_sum.allocated_sum or 0) / 100)

    if update_shop_payout:
        payouts = session.query(models.ShopPayout.date,
                                models.ShopPayout.shop_id,
                                models.ShopPayout.station_id,
                                func.count(models.ShopPayout.id).label("payout_count"),
                                func.sum(models.ShopPayout.money).label("payout_sum"))

        if date is not None:
            payouts = payouts.filter(models.ShopPayout.date == date)
        if station_id is not None:
            payouts = payouts.filter(models.ShopPayout.station_id == station_id)
        if shop_ids is not None:
            payouts = payouts.filter(models.ShopPayout.shop_id.in_(shop_ids))

        payouts = payouts.group_by(models.ShopPayout.date, models.ShopPayout.shop_id) \
            .all()

        for payout in payouts:
            key = "{}:{}".format(payout.date, payout.shop_id)
            statistics = statistics_dict.get(key)
            if not statistics:
                statistics = models_statistics.StatisticsShopFinancial(
                    statistics_date=payout.date,
                    statistics_type=0,
                    station_id=payout.station_id,
                    shop_id=payout.shop_id,
                )
                statistics_session.add(statistics)
                statistics_session.flush()
                statistics_dict[key] = statistics

            statistics.shop_payout_count = payout.payout_count or 0
            statistics.shop_payout_money = payout.payout_sum or 0

    statistics_session.commit()
