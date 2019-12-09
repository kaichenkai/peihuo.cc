import argparse
import datetime
import json
import os
import re
import sys
from collections import defaultdict

from openpyxl import load_workbook
from sqlalchemy import or_

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from dal.db_configs import DBSession
import dal.models as models


# TODO 先把这部分填了！
WISH_DATE = datetime.date(2018, 12, 31)
STATION_ID = 11  # 中转站 ID，先去数据库里查出来直接设置好
CREATOR_ID = 24  # 记录创建人的 ID，就用中转站的超管吧
PURCHASER_MAP = {  # 采购员映射，直接把几个采购员在数据库里的 ID 拿来建好查找表
    "八哥": 32,
    "大鹏": 62,
    "王哥": 61,
    "郭树": 72,
    "二胖": 80,
    "库房": 85,
    "八哥小号": 32,
    "树℡": 72,
    "朱会勇": 80,
    "仓库": 85,
}


if __name__ == '__main__':
    if not STATION_ID:
        raise Exception('先把代码里的常量填了！')

    session = DBSession()

    filename = '2018-12-30各店意向单(1).xlsx'
    wb = load_workbook(filename)
    sheet = wb.active

    # 先搞个意向单
    wish_order = session.query(models.WishOrder) \
        .filter(models.WishOrder.wish_date == WISH_DATE,
                models.WishOrder.station_id == STATION_ID) \
        .first()
    if not wish_order:
        wish_order = models.WishOrder(
            wish_date=WISH_DATE,
            status=2,  # 直接是提交状态，要改再说
            station_id=STATION_ID,
            creator_id=CREATOR_ID,
        )
        session.add(wish_order)
        session.flush()

    # 每次直接把之前的意向单商品全删了重建
    session.query(models.WishOrderGoods) \
        .filter(models.WishOrderGoods.wish_order_id == wish_order.id) \
        .update({"status": -1})
    session.flush()

    goods_status = 0  # 0-有货 1-缺货 2-没货
    for i in range(4, 999999):
        # 取出表里一行的数据
        no = sheet["A{}".format(i)].value
        code = sheet["B{}".format(i)].value
        name = sheet["C{}".format(i)].value
        purchaser = sheet["D{}".format(i)].value
        remarks = sheet["G{}".format(i)].value

        if not no:
            break
        if name == '下方产品不保证有货':
            goods_status = 1
            continue
        if remarks and '没有了' in remarks:
            goods_status = 2

        print('{} {} {} {} {}'.format(no, code, name, purchaser, remarks))

        # 用名字把商品查出来，没有就建一个
        goods = session.query(models.Goods) \
            .filter(models.Goods.name == name,
                    models.Goods.station_id == STATION_ID,
                    models.Goods.status == 0) \
            .first()
        if not goods:
            print('-------------- {} 还没有，建一个 --------------'.format(name))
            goods = models.Goods(
                name=name,
                station_id=STATION_ID,
                creator_id=CREATOR_ID,
            )
            session.add(goods)
            session.flush()
        goods.code = code

        # 拿本行数据建一个意向单商品
        wish_goods = models.WishOrderGoods(
            remarks=remarks,
            status=goods_status,
            goods_id=goods.id,
            wish_order_id=wish_order.id,
            goods_name=goods.name,
            priority=i,
        )
        session.add(wish_goods)
        session.flush()

        if purchaser:
            purchaser_id = PURCHASER_MAP.get(purchaser)

            if not purchaser_id:
                raise Exception("{} 没有对应的采购员".format(purchaser))

            default_purchaser = session.query(models.StaffGoods) \
                .filter(models.StaffGoods.goods_id == goods.id) \
                .first()
            if not default_purchaser:
                default_purchaser = models.StaffGoods(
                    goods_id=goods.id,
                    staff_id=purchaser_id,
                )
                session.add(default_purchaser)
                session.flush()
            else:
                default_purchaser.staff_id = purchaser_id
                session.flush()

    session.commit()
