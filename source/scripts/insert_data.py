import datetime
import json
import os,sys
import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../")))
import multiprocessing
from multiprocessing import Process
from sqlalchemy import or_
import tornado.web
from tornado.options import options, define
import dal.models as models
from dal.db_configs import DBSession, statistic_DBSession, redis
from handlers.base.pub_func import TimeFunc

define("action", default="", help="")
define("p2", default="", help="")

session = DBSession()


def set_latest_version(param):
    info = {
        "Android": {
            "verCode": "1801220947",
            "verName": "1.0.9",
            "verDate": "2018-01-23",
            "url": "http://d.senguo.cc/android/SenguoSecretary-V1.0.9-1801220947-release.apk",
            "log": "增加老板直接开票功能"
        }
    }

    redis.set("cgapp_update_info", json.dumps(info))


def add_test_data(data):
    object_list = list()
    user = models.AccountInfo(
        phone='18627765247',
        sex=2,
        nickname='kai',
        realname="chenkai",
        headimgurl='https://thirdwx.qlogo.cn/mmopen/vi_32/DYAIOgq83eq4GRIvU1EfTcicfRHlrpibKnSPjDtoGHWiccXP8lbF0XR5uDzjbJlREwAOVZiaFxkDlqm5CWsMaJe6PQ/132',
        birthday=2018,
        wx_country='中国',
        wx_province='江西',
        wx_city='九江',
        wx_unionid='oxkR_jlY3xj-BdzsPGggDTslqK5',
        wx_openid='oMvaL1i3oOJkI8hRjCSfQ8rXLVlw',
        create_time='2018-03-23 12:10:06.000',
        passport_id=194726,
        alipay_acctid='',
        alipay_acctname=''
    )
    object_list.append(user)
    station = models.TransferStation(
        name="测试中转站",
        province=1,
        city=1,
        address="光谷",
        create_time=datetime.datetime.now(),
        status=0,
        creator_id=1
    )
    object_list.append(station)

    staff = models.Staff(
        remarks="测试员工",
        date_onboarding=datetime.date.today(),
        birthday=datetime.date.today(),
        status=0,
        station_id=1,
        account_id=1
    )
    object_list.append(staff)

    firm_1 = models.Firm(
        name="甲",
        station_id=1,
        creator_id=1
    )
    object_list.append(firm_1)
    firm_2 = models.Firm(
        name="乙",
        station_id=1,
        creator_id=1
    )
    object_list.append(firm_2)
    firm_3 = models.Firm(
        name="丙",
        station_id=1,
        creator_id=1
    )
    object_list.append(firm_3)

    goods_1 = models.Goods(
        name="苹果",
        station_id=1
    )
    object_list.append(goods_1)
    goods_2 = models.Goods(
        name="脆梨",
        station_id=1
    )
    object_list.append(goods_2)
    goods_3 = models.Goods(
        name="柚子",
        station_id=1
    )
    object_list.append(goods_3)

    firm_goods_1 = models.FirmGoods(
        goods_id=1,
        firm_id=1,
    )
    object_list.append(firm_goods_1)
    firm_goods_2 = models.FirmGoods(
        goods_id=1,
        firm_id=2,
    )
    object_list.append(firm_goods_2)
    firm_goods_3 = models.FirmGoods(
        goods_id=2,
        firm_id=1,
    )
    object_list.append(firm_goods_3)

    wish_order = models.WishOrder(
        wish_date=datetime.date.today(),
        station_id =1,
        creator_id=1
    )
    object_list.append(wish_order)

    purchase_order = models.PurchaseOrder(
        station_id=1,
        purchaser_id=1,
        wish_order_id=1
    )
    object_list.append(purchase_order)

    purchase_order_goods_1 = models.PurchaseOrderGoods(
        firm_id=1,
        goods_id=1,
        purchase_order_id=1
    )
    object_list.append(purchase_order_goods_1)
    purchase_order_goods_2 = models.PurchaseOrderGoods(
        firm_id=2,
        goods_id=1,
        purchase_order_id=1
    )
    object_list.append(purchase_order_goods_2)
    purchase_order_goods_3 = models.PurchaseOrderGoods(
        firm_id=1,
        goods_id=2,
        purchase_order_id=1
    )
    object_list.append(purchase_order_goods_3)
    session.add_all(object_list)
    session.commit()


db_dict_action = {
    'set_latest_version': set_latest_version,
    'add_test_data': add_test_data
}


def main():
    tornado.options.parse_command_line()
    action=options.action
    p2=options.p2
    g = multiprocessing.Process(name=action,target=db_dict_action[action](p2))
    g.start()
    g.join()
    session.close()


if __name__ == "__main__":
    main()
