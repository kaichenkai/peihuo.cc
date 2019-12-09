# 统计专用数据模块
from sqlalchemy import create_engine, func, ForeignKey, Column, Index
from sqlalchemy.orm import relationship
from sqlalchemy.types import String, Integer, Boolean, Float, Date, BigInteger, DateTime, Time, SMALLINT, REAL, Text
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, YEAR
from dal.db_configs import Statistic_MapBase, statistic_DBSession
from dal.models import _CommonApi, TransferStation, Shop


class TimeBaseModel(object):
    create_time = Column(DateTime, nullable=False, default=func.now())  # 记录的创建时间
    update_time = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())  # 记录的更新时间


# 门店对账
class StatisticsShopFinancial(Statistic_MapBase, TimeBaseModel):
    __tablename__ = "statistics_shop_financial"

    id = Column(Integer, primary_key=True, autoincrement=True)
    statistics_date = Column(Date, nullable=False)  # 统计日期
    statistics_type = Column(TINYINT, nullable=False, default=1)  # 统计类型 0-天 1-月

    station_id = Column(Integer, nullable=False, default=0)  # 中转站 ID

    shop_id = Column(Integer, nullable=False, default=0)  # 门店 ID

    shop_payout_money = Column(Integer, nullable=False, default=0)  # 其他支出
    shop_payout_count = Column(Integer, nullable=False, default=0)  # 其他支出次数

    allocation_money = Column(Integer, nullable=False, default=0)  # 实配金额
    allocation_count = Column(Integer, nullable=False, default=0)  # 实配次数


# 中转站费用对账
class StatisticsStationFee(Statistic_MapBase, TimeBaseModel):
    __tablename__ = "statistics_station_fee"

    id = Column(Integer, primary_key=True, autoincrement=True)
    statistics_date = Column(Date, nullable=False)  # 统计日期
    statistics_type = Column(TINYINT, nullable=False, default=1)  # 统计类型 0-天 1-月
    station_id = Column(Integer, nullable=False, default=0)  # 中转站ID
    voucher_sum = Column(Integer, nullable=False, default=0)  # 货品采购费用
    delivery_sum = Column(Integer, nullable=False, default=0)  # 运杂费
    routine_sum = Column(Integer, nullable=False, default=0)  # 日常杂费


# 供货商结算款汇总
class StatisticsFirmPayment(Statistic_MapBase, TimeBaseModel):
    __tablename__ = "statistics_firm_payment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    statistics_date = Column(Date, nullable=False)   # 统计日期
    statistics_type = Column(TINYINT, nullable=False, default=1)   # 统计类型 0-天 1-月
    station_id = Column(Integer, nullable=False, default=0)   # 中转站ID
    firm_id = Column(Integer, nullable=False, default=0)    # 供货商ID
    settle_times = Column(Integer, nullable=False, default=0)   # 结算次数，默认为0
    settle_nums = Column(Integer, nullable=False, default=0)    # 结算票数
    settle_money = Column(BigInteger, nullable=False, default=0)   # 结算金额


# 数据库初始化
def init_db_data():
    Statistic_MapBase.metadata.create_all()
    return True
