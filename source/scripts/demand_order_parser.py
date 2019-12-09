import os
import re
import sys

from openpyxl import load_workbook

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from dal.db_configs import DBSession
import dal.models as models


# TODO 先把这部分填了！
WISH_ORDER_ID = 114  # 意向单 ID，意向单需要先手动创建


if __name__ == '__main__':
    if not WISH_ORDER_ID:
        raise Exception('先把代码里的常量填了！')

    session = DBSession()

    filename = '2018.12.4西青道店意向单.xlsx'
    wb = load_workbook(filename)
    sheet = wb.active

    # 从文件名里匹配门店名
    matcher = re.search('\d([^\d]+)店', filename)
    if matcher:
        shop_name = matcher.group(1)
    else:
        raise Exception('{} 文件里没找到有效店名')

    # 把意向单拿出来
    wish_order = models.WishOrder.get_by_id(session, WISH_ORDER_ID)
    if not wish_order:
        raise Exception('先建个意向单')
    station_id = wish_order.station_id
    creator_id = wish_order.creator_id

    # 从文件名里找一个 Shop，没有就建一个
    shop = session.query(models.Shop) \
        .filter(models.Shop.abbreviation == shop_name,
                models.Shop.station_id == station_id,
                models.Shop.status == 0) \
        .first()
    if not shop:
        print('-------------- {} 店还没有，建一个 --------------'.format(shop_name))
        shop = models.Shop(
            abbreviation=shop_name,
            station_id=station_id,
            creator_id=creator_id,
        )
        session.add(shop)
        session.flush()

    # 建一个订货单
    demand_order = session.query(models.DemandOrder) \
        .filter(models.DemandOrder.wish_order_id == WISH_ORDER_ID,
                models.DemandOrder.shop_id == shop.id) \
        .first()
    if not demand_order:
        print('-------------- {} 店还没订货，建一个订货单 --------------'.format(shop_name))
        demand_order = models.DemandOrder(
            wish_order_id=WISH_ORDER_ID,
            shop_id=shop.id,
            creator_id=creator_id,
            status=2,  # 直接加进汇总单里
        )
        session.add(demand_order)
        session.flush()

    # 每次直接把之前的订货单商品全删了重建
    session.query(models.DemandOrderGoods) \
        .filter(models.DemandOrderGoods.demand_order_id == demand_order.id) \
        .update({"status": -1})
    session.flush()

    # 把意向单商品都取出来
    wish_goods_list = session.query(models.WishOrderGoods) \
        .join(models.WishOrder, models.WishOrder.id == models.WishOrderGoods.wish_order_id) \
        .filter(models.WishOrder.id == WISH_ORDER_ID,
                models.WishOrderGoods.status >= 0) \
        .all()
    wish_goods_dict = {goods.goods_id: goods for goods in wish_goods_list}

    for i in range(4, 999999):
        # 取出表里一行的数据
        no = sheet["A{}".format(i)].value
        code = sheet["B{}".format(i)].value
        name = sheet["C{}".format(i)].value
        purchaser = sheet["D{}".format(i)].value
        storage = sheet["E{}".format(i)].value
        demand_amount = sheet["F{}".format(i)].value

        if not no:
            break
        if name == '下方产品不保证有货':
            continue

        print('{} {} {} {} {} {}'.format(no, code, name, purchaser, storage, demand_amount))
        if storage and not isinstance(storage, float) and not isinstance(storage, int):
            raise Exception('{} 的库存量 {} 不是纯数字，手动改改'.format(name, storage))
        if demand_amount and not isinstance(demand_amount, float) and not isinstance(demand_amount, int):
            raise Exception('{} 的订货量 {} 不是纯数字，手动改改'.format(name, demand_amount))

        # 用名字把商品查出来
        goods = session.query(models.Goods) \
            .filter(models.Goods.name == name,
                    models.Goods.station_id == station_id) \
            .first()
        if not goods:
            raise Exception('没找到 {}，先手动建好加到意向单里吧'.format(name))

        wish_goods = wish_goods_dict.get(goods.id)
        if not wish_goods:
            raise Exception('意向单里没有 {}，先去手动加到意向单里'.format(name))

        # 拿本行数据建一个订货单商品
        demand_goods = models.DemandOrderGoods(
            current_storage=round(storage * 100) if storage else 0,
            demand_amount=round(demand_amount * 100) if demand_amount else 0,
            goods_id=goods.id,
            demand_order_id=demand_order.id,
            wish_order_goods_id=wish_goods.id,
        )
        session.add(demand_goods)
        session.flush()

    session.commit()
