# -*- coding:utf-8 -*-

import datetime
from collections import defaultdict
from sqlalchemy import func
from dal import models
from handlers.base.pub_func import TimeFunc, check_int, check_float
from handlers.base.pub_web import StationBaseHandler, ShopBaseHandler
from handlers.base.webbase import BaseHandler


# 意向单
class WishOrderMixin:
    def get(self, order_id):
        order = models.WishOrder.get_by_id(self.session, order_id, station_id=self.current_station.id)

        if not order:
            return self.send_fail("没有找到指定的意向单")

        order_goods_list = self.session.query(models.WishOrderGoods, models.Goods) \
            .join(models.Goods, models.Goods.id == models.WishOrderGoods.goods_id) \
            .filter(models.WishOrderGoods.wish_order_id == order_id,
                    models.WishOrderGoods.status >= 0) \
            .order_by(models.WishOrderGoods.priority.asc()) \
            .all()

        # 默认采购员信息
        goods_ids = {goods.id for _, goods in order_goods_list}
        default_purchasers = self.session.query(models.StaffGoods) \
            .filter(models.StaffGoods.goods_id.in_(goods_ids)) \
            .all()
        purchaser_ids = {purchaser.staff_id for purchaser in default_purchasers}
        purchaser_accounts = self.session.query(models.Staff, models.AccountInfo) \
            .join(models.AccountInfo, models.AccountInfo.id == models.Staff.account_id) \
            .filter(models.Staff.id.in_(purchaser_ids)) \
            .all()
        purchaser_account_dict = {item[0].id: item for item in purchaser_accounts}
        default_purchaser_dict = {item.goods_id: purchaser_account_dict.get(item.staff_id) for item in default_purchasers}

        order_goods_data = defaultdict(list)
        for order_goods, goods in order_goods_list:
            default_purchaser = default_purchaser_dict.get(goods.id)
            purchaser_id = default_purchaser[0].id if default_purchaser else 0
            purchaser_name = default_purchaser[0].remarks or default_purchaser[1].username if default_purchaser else ""

            # 仓库库存以提交时的为准
            goods_storage = goods.stock if order.status == 1 else order_goods.confirmed_storage
            order_goods_data[order_goods.status].append({
                "id": order_goods.id,
                "wish_order_id": order_goods.wish_order_id,
                "goods_id": goods.id,
                "serial_number": goods.serial_number,
                "order_goods_name": order_goods.goods_name,
                "order_goods_name_modified": order_goods.goods_name_modified,
                "goods_name": goods.name,
                "goods_code": goods.code,
                "goods_storage": check_float(goods_storage / 100),
                "create_time": TimeFunc.time_to_str(order_goods.create_time),
                "tag": order_goods.tag,
                "remarks": order_goods.remarks,
                "status": order_goods.status,
                "purchaser_id": purchaser_id,
                "purchaser_name": purchaser_name,
            })

        order_data = {
            "id": order.id,
            "station_id": order.station_id,
            "create_time": TimeFunc.time_to_str(order.create_time),
            "creator_id": order.creator_id,
            "wish_date": TimeFunc.time_to_str(order.wish_date, "date"),
            "status": order.status,
            "goods_data": order_goods_data,
        }
        return self.send_success(order_data=order_data)


class WishOrder(WishOrderMixin, StationBaseHandler):
    @BaseHandler.check_arguments("wish_date:date", "goods_list:list", "commit?:bool")
    def post(self):
        wish_date = self.args["wish_date"]
        goods_list = self.args["goods_list"]
        commit = self.args.get("commit", False)

        valid, message = self.validate_goods_list(goods_list)
        if not valid:
            return self.send_fail(message)

        existed_order_today = self.session.query(models.WishOrder) \
            .filter(models.WishOrder.status > 0,
                    models.WishOrder.station_id == self.current_station.id,
                    models.WishOrder.wish_date == wish_date) \
            .first()
        if existed_order_today:
            return self.send_fail("今天已经创建过意向单了")

        new_order = models.WishOrder(
            station_id=self.current_station.id,
            creator_id=self.current_user.id,
            wish_date=wish_date,
        )
        self.session.add(new_order)
        self.session.flush()

        # 商品库存
        goods_ids = [goods["goods_id"] for goods in goods_list]
        goods_storage_list = self.session.query(models.Goods.id, models.Goods.stock) \
            .filter(models.Goods.id.in_(goods_ids)) \
            .all()
        goods_storage_dict = {goods.id: goods.stock for goods in goods_storage_list}

        # 上一个意向单中的货品名
        last_order = self.session.query(models.WishOrder) \
            .filter(models.WishOrder.station_id == self.current_station.id,
                    models.WishOrder.create_time < new_order.create_time) \
            .order_by(models.WishOrder.create_time.desc()) \
            .limit(1) \
            .first()
        last_order_goods_name_dict = {}
        if last_order:
            last_order_goods_list = self.session.query(models.WishOrderGoods.id, models.WishOrderGoods.goods_name) \
                .filter(models.WishOrderGoods.wish_order_id == last_order.id,
                        models.WishOrderGoods.status >= 0) \
                .all()
            last_order_goods_name_dict = {goods.id: goods.goods_name for goods in last_order_goods_list}

        # 添加意向单商品
        i = 0
        for goods in goods_list:
            goods_id = goods["goods_id"]
            order_goods_name = goods["order_goods_name"]
            status = goods["status"]
            tag = goods.get("tag", "")
            remarks = goods.get("remarks", "")
            storage = goods_storage_dict.get(goods_id, 0)
            last_goods_name = last_order_goods_name_dict.get(goods_id)
            goods_name_modified = 1 if last_goods_name and last_goods_name != order_goods_name else 0

            new_goods = models.WishOrderGoods(
                wish_order_id=new_order.id,
                goods_id=goods_id,
                goods_name=order_goods_name,
                goods_name_modified=goods_name_modified,
                confirmed_storage=storage,
                tag=tag,
                remarks=remarks,
                status=status,
                priority=i,
            )
            self.session.add(new_goods)
            i += 1

        # 默认保存为草稿
        if commit:
            new_order.status = 2
        else:
            new_order.status = 1

        self.session.commit()

        return self.send_success(order_id=new_order.id)

    def validate_goods_list(self, goods_list):
        """验证商品列表参数"""

        if not isinstance(goods_list, list):
            return False, "商品列表参数格式有误"

        for goods in goods_list:
            if not isinstance(goods, dict):
                return False, "商品列表参数项格式有误"

            if "goods_id" not in goods:
                return False, "参数缺失：goods_id"
            if "order_goods_name" not in goods:
                return False, "参数缺失：order_goods_name"
            elif len(goods["order_goods_name"]) > 128:
                return False, "商品名过长：{}".format(goods["order_goods_name"])
            if "status" not in goods:
                return False, "参数缺失：status"
            elif goods["status"] not in (0, 1, 2):
                return False, "参数无效：status == {}".format(goods["status"])

        # 检验商品名称是否重复
        name_list = [goods["order_goods_name"] for goods in goods_list]
        for name in name_list:
            if name_list.count(name) > 1:
                return False, "「{0}」商品名称重复".format(name)
        # 检验goods_id有效性
        goods_ids = {check_int(goods["goods_id"]) for goods in goods_list}
        valid_goods_list = models.Goods.get_by_ids(self.session, goods_ids, self.current_station.id)
        valid_goods_ids = {goods.id for goods in valid_goods_list}
        if goods_ids != valid_goods_ids:
            return False, "提交了无效的商品"

        return True, ""

    @BaseHandler.check_arguments("goods_list:list", "commit?:bool")
    def put(self, order_id):
        goods_list = self.args["goods_list"]
        commit = self.args.get("commit", False)

        valid, message = self.validate_goods_list(goods_list)
        if not valid:
            return self.send_fail(message)

        order = models.WishOrder.get_by_id(self.session, order_id, self.current_station.id)
        if not order:
            return self.send_fail("没有找到指定的意向单")
        if order.status >= 3:
            return self.send_fail("意向单已完成汇总")
        if order.create_time.date() < datetime.date.today():
            return self.send_fail("只能修改当天的意向单")

        order_goods_list = models.WishOrderGoods.get_by_order_id(self.session, order_id)
        order_goods_dict = {order_goods.goods_id: order_goods for order_goods in order_goods_list}

        # 商品库存
        goods_ids = [goods["goods_id"] for goods in goods_list]
        goods_storage_list = self.session.query(models.Goods.id, models.Goods.stock) \
            .filter(models.Goods.id.in_(goods_ids)) \
            .all()
        goods_storage_dict = {goods.id: goods.stock for goods in goods_storage_list}

        # 上一个意向单中的货品名
        last_order = self.session.query(models.WishOrder) \
            .filter(models.WishOrder.station_id == self.current_station.id,
                    models.WishOrder.create_time < order.create_time) \
            .order_by(models.WishOrder.create_time.desc()) \
            .limit(1) \
            .first()
        last_order_goods_name_dict = {}
        if last_order:
            last_order_goods_list = self.session.query(models.WishOrderGoods.goods_id, models.WishOrderGoods.goods_name) \
                .filter(models.WishOrderGoods.wish_order_id == last_order.id,
                        models.WishOrderGoods.status >= 0) \
                .all()
            last_order_goods_name_dict = {goods.goods_id: goods.goods_name for goods in last_order_goods_list}

        # 添加意向单商品
        i = 0
        for goods in goods_list:
            goods_id = goods["goods_id"]
            order_goods_name = goods["order_goods_name"]
            status = goods["status"]
            tag = goods.get("tag", "")
            remarks = goods.get("remarks", "")
            storage = goods_storage_dict.get(goods_id, 0)
            last_goods_name = last_order_goods_name_dict.get(goods_id)
            goods_name_modified = 1 if last_goods_name and last_goods_name != order_goods_name else 0

            order_goods = order_goods_dict.pop(goods_id, None)
            if not order_goods:
                order_goods = models.WishOrderGoods(
                    wish_order_id=order_id,
                    goods_id=goods_id,
                )
                self.session.add(order_goods)
                self.session.flush()

            order_goods.goods_name = order_goods_name
            order_goods.goods_name_modified = goods_name_modified
            order_goods.confirmed_storage = storage
            order_goods.tag = tag
            order_goods.remarks = remarks
            order_goods.status = status
            order_goods.priority = i
            i += 1
        # 删除前端已删除的意向单商品
        for deleted_order_goods in order_goods_dict.values():
            deleted_order_goods.status = -1

        self.session.flush()

        # 更新所有店铺的订货单
        demand_order_list = models.DemandOrder.get_all_by_wish_order_id(self.session, order_id)
        for demand_order in demand_order_list:
            wish_order_goods_list = models.WishOrderGoods.get_by_order_id(self.session, order_id)
            demand_order_goods_list = models.DemandOrderGoods.get_by_order_id(self.session, demand_order.id)
            demand_order_goods_dict = {goods.wish_order_goods_id: goods for goods in demand_order_goods_list}

            for wish_goods in wish_order_goods_list:
                # pop 以检查多余的订货单商品
                demand_goods = demand_order_goods_dict.pop(wish_goods.id, None)

                # 没有则创建新的订货单商品
                if not demand_goods:
                    demand_goods = models.DemandOrderGoods(
                        goods_id=wish_goods.goods_id,
                        demand_order_id=demand_order.id,
                        wish_order_goods_id=wish_goods.id
                    )
                    self.session.add(demand_goods)

            # 删除「没有对应的意向单商品」的订货单商品
            for deprecated_demand_goods in demand_order_goods_dict.values():
                deprecated_demand_goods.status = -1

        # 默认保存为草稿
        if commit:
            order.status = 2
        else:
            order.status = 1

        self.session.commit()

        return self.send_success()


# 同意向单下已提交的订货单
class WishOrderDemandInfo(ShopBaseHandler):
    def get(self, order_id):
        order = models.WishOrder.get_by_id(self.session, order_id)

        if not order:
            return self.send_fail("没有找到指定的意向单")
        wish_order_id = order_id
        # 统计已提交及汇总的订货单
        demand_orders = self.session.query(models.DemandOrder, models.AccountInfo) \
            .join(models.AccountInfo, models.DemandOrder.creator_id == models.AccountInfo.id) \
            .filter(models.DemandOrder.wish_order_id == wish_order_id,
                    models.DemandOrder.status != 0).all()
        shop_id_list = [u.shop_id for u, _ in demand_orders]
        shop_contact_list = self.session.query(models.ShopContact) \
            .filter(models.ShopContact.shop_id.in_(shop_id_list)).all()
        shop_contact_dict = {}
        for shop_contact in shop_contact_list:
            shop_contact_dict[shop_contact.phone] = shop_contact.name
        shops = self.session.query(models.Shop).filter(models.Shop.id.in_(shop_id_list))
        shop_name_dict = {}
        for shop in shops:
            shop_name_dict[shop.id] = shop.abbreviation
        demand_order_data = []
        for demand_order, account_info in demand_orders:
            demand_order_data.append(
                {"creator": shop_contact_dict.get(account_info.phone, "") or account_info.username,
                 "creator_id": account_info.id,
                 "shop_id": demand_order.shop_id,
                 "shop": shop_name_dict[demand_order.shop_id],
                 "create_time": TimeFunc.time_to_str(demand_order.create_time),
                 "headimgurl": account_info.headimgurl})
        return self.send_success(demand_order_data=demand_order_data)


# 上一个意向单
class LastWishOrder(StationBaseHandler):
    def get(self):
        today_start = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        order = self.session.query(models.WishOrder) \
            .filter(models.WishOrder.station_id == self.current_station.id,
                    models.WishOrder.create_time < today_start) \
            .order_by(models.WishOrder.create_time.desc()) \
            .limit(1) \
            .first()

        # fails silently
        if not order:
            return self.send_success(order_data={})

        order_goods_list = self.session.query(models.WishOrderGoods, models.Goods) \
            .join(models.Goods, models.Goods.id == models.WishOrderGoods.goods_id) \
            .filter(models.WishOrderGoods.wish_order_id == order.id,
                    models.WishOrderGoods.status >= 0) \
            .order_by(models.WishOrderGoods.priority.asc()) \
            .all()

        # 默认采购员信息
        goods_ids = {goods.id for _, goods in order_goods_list}
        default_purchasers = self.session.query(models.StaffGoods) \
            .filter(models.StaffGoods.goods_id.in_(goods_ids)) \
            .all()
        purchaser_ids = {purchaser.staff_id for purchaser in default_purchasers}
        purchaser_accounts = self.session.query(models.Staff, models.AccountInfo) \
            .join(models.AccountInfo, models.AccountInfo.id == models.Staff.account_id) \
            .filter(models.Staff.id.in_(purchaser_ids)) \
            .all()
        purchaser_account_dict = {item[0].id: item for item in purchaser_accounts}
        default_purchaser_dict = {item.goods_id: purchaser_account_dict.get(item.staff_id) for item in default_purchasers}

        order_goods_data = defaultdict(list)
        for order_goods, goods in order_goods_list:
            default_purchaser = default_purchaser_dict.get(goods.id)
            purchaser_id = default_purchaser[0].id if default_purchaser else 0
            purchaser_name = default_purchaser[0].remarks or default_purchaser[1].username if default_purchaser else ""

            # 仓库库存以提交时的为准
            order_goods_data[order_goods.status].append({
                "id": order_goods.id,
                "wish_order_id": order_goods.wish_order_id,
                "goods_id": goods.id,
                "serial_number": goods.serial_number,
                "goods_name": goods.name,
                "goods_code": goods.code,
                "goods_storage": check_float(goods.stock / 100),
                "create_time": TimeFunc.time_to_str(order_goods.create_time),
                "tag": order_goods.tag,
                "remarks": order_goods.remarks,
                "status": order_goods.status,
                "purchaser_id": purchaser_id,
                "purchaser_name": purchaser_name,
            })

        order_data = {
            "id": order.id,
            "station_id": order.station_id,
            "create_time": TimeFunc.time_to_str(order.create_time),
            "creator_id": order.creator_id,
            "wish_date": TimeFunc.time_to_str(order.wish_date, "date"),
            "status": order.status,
            "goods_data": order_goods_data,
        }
        return self.send_success(order_data=order_data)


class CurrentWishOrderMixin:
    def get_current_wish_order(self, station):
        now = datetime.datetime.now()
        today = now.date()

        # 以每天下午三点为界
        if now.hour >= 15:
            from_time = datetime.datetime.combine(today, datetime.time(15))
            to_time = from_time + datetime.timedelta(days=1)
        else:
            to_time = datetime.datetime.combine(today, datetime.time(15))
            from_time = to_time - datetime.timedelta(days=1)

        # 最新的意向单
        order = self.session.query(models.WishOrder) \
            .filter(models.WishOrder.station_id == station.id,
                    models.WishOrder.create_time >= from_time,
                    models.WishOrder.create_time <= to_time) \
            .first()

        order_goods_list = []

        if not order:
            # 下午三点前创建今天的意向单，下午三点后创建第二天的意向单
            if now.hour >= 15:
                wish_date = today + datetime.timedelta(days=1)
            else:
                wish_date = today
            order = models.WishOrder(
                create_time=now,
                wish_date=wish_date,
                status=2,
                station_id=station.id,
                creator_id=self.current_user.id,
            )
            self.session.add(order)
            self.session.flush()

            # 上一个意向单
            last_order = self.session.query(models.WishOrder) \
                .filter(models.WishOrder.station_id == station.id,
                        models.WishOrder.create_time < from_time) \
                .order_by(models.WishOrder.create_time.desc()) \
                .limit(1) \
                .first()

            # 复制上一个意向单的内容
            if last_order:
                last_order_goods_list = self.session.query(models.WishOrderGoods, models.Goods) \
                    .join(models.Goods) \
                    .filter(models.WishOrderGoods.wish_order_id == last_order.id,
                            models.WishOrderGoods.status >= 0) \
                    .all()
                for order_goods, goods in last_order_goods_list:
                    new_order_goods = models.WishOrderGoods(
                        goods_name=order_goods.goods_name,
                        goods_name_modified=0,
                        tag=order_goods.tag,
                        remarks=order_goods.remarks,
                        status=order_goods.status,
                        priority=order_goods.priority,
                        goods_id=order_goods.goods_id,
                        wish_order_id=order.id,
                    )
                    self.session.add(new_order_goods)
                    self.session.flush()

                    order_goods_list.append((new_order_goods, goods))

            self.session.commit()
        else:
            order_goods_list = self.session.query(models.WishOrderGoods, models.Goods) \
                .join(models.Goods) \
                .filter(models.WishOrderGoods.status >= 0,
                        models.WishOrderGoods.wish_order_id == order.id) \
                .order_by(models.WishOrderGoods.priority.asc()) \
                .all()

        # 默认采购员信息
        goods_ids = {goods.id for _, goods in order_goods_list}
        default_purchasers = self.session.query(models.StaffGoods) \
            .filter(models.StaffGoods.goods_id.in_(goods_ids)) \
            .all()
        purchaser_ids = {purchaser.staff_id for purchaser in default_purchasers}
        purchaser_accounts = self.session.query(models.Staff, models.AccountInfo) \
            .join(models.AccountInfo, models.AccountInfo.id == models.Staff.account_id) \
            .filter(models.Staff.id.in_(purchaser_ids)) \
            .all()
        purchaser_account_dict = {item[0].id: item for item in purchaser_accounts}
        default_purchaser_dict = {item.goods_id: purchaser_account_dict.get(item.staff_id) for item in
                                  default_purchasers}

        order_goods_data = defaultdict(list)
        for order_goods, goods in order_goods_list:
            default_purchaser = default_purchaser_dict.get(goods.id)
            purchaser_id = default_purchaser[0].id if default_purchaser else 0
            purchaser_name = default_purchaser[0].remarks or default_purchaser[1].username if default_purchaser else ""

            # 仓库库存以提交时的为准
            order_goods_data[order_goods.status].append({
                "id": order_goods.id,
                "wish_order_id": order_goods.wish_order_id,
                "goods_id": goods.id,
                "serial_number": goods.serial_number,
                "goods_name": goods.name,
                "goods_code": goods.code,
                "goods_storage": check_float(goods.stock / 100),
                "create_time": TimeFunc.time_to_str(order_goods.create_time),
                "tag": order_goods.tag,
                "remarks": order_goods.remarks,
                "status": order_goods.status,
                "purchaser_id": purchaser_id,
                "purchaser_name": purchaser_name,
            })

        order_data = {
            "id": order.id,
            "station_id": order.station_id,
            "create_time": TimeFunc.time_to_str(order.create_time),
            "creator_id": order.creator_id,
            "wish_date": TimeFunc.time_to_str(order.wish_date, "date"),
            "status": order.status,
            "goods_data": order_goods_data,
        }
        return order_data


# 当前意向单 TODO 过渡用，在意向单汇总单重构完成后删除 ref: https://tower.im/teams/175903/todos/13413/24
class CurrentWishOrder(StationBaseHandler, CurrentWishOrderMixin):
    def get(self):
        order_data = self.get_current_wish_order(self.current_station)
        return self.send_success(order_data=order_data)


# 用意向日期取意向单 ID TODO 过渡用，在意向单汇总单重构完成后删除 ref: https://tower.im/teams/175903/todos/13413/24
class WishOrderIdByWishDate(StationBaseHandler):
    @BaseHandler.check_arguments("wish_date:date")
    def get(self):
        wish_date = self.args["wish_date"]
        order = self.session.query(models.WishOrder) \
            .filter(models.WishOrder.wish_date == wish_date,
                    models.WishOrder.station_id == self.current_station.id) \
            .first()
        if not order:
            return self.send_fail("{} 没有意向单".format(TimeFunc.time_to_str(wish_date, "date")))
        return self.send_success(order_id=order.id)


# 意向单列表
class WishOrderList(StationBaseHandler):
    @BaseHandler.check_arguments("page?:int", "limit?:int")
    def get(self):
        page = self.args.get("page", 0)
        limit = self.args.get("limit", 20)

        wish_orders = self.session.query(models.WishOrder) \
            .filter(models.WishOrder.station_id == self.current_station.id) \
            .order_by(models.WishOrder.wish_date.desc()) \
            .offset(page * limit) \
            .limit(limit) \
            .all()

        # 门店数
        shop_count = self.session.query(models.Shop.id) \
            .filter(models.Shop.status == 0,
                    models.Shop.station_id == self.current_station.id) \
            .count()

        wish_order_ids = {order.id for order in wish_orders}
        demand_order_count_list = self.session.query(models.DemandOrder.wish_order_id,
                                                     func.count(models.DemandOrder.id)) \
            .filter(models.DemandOrder.status >= 1,
                    models.DemandOrder.wish_order_id.in_(wish_order_ids)) \
            .group_by(models.DemandOrder.wish_order_id) \
            .all()
        demand_order_count_dict = {wish_order_id: count for wish_order_id, count in demand_order_count_list}

        order_list = []
        for order in wish_orders:
            order_list.append({
                "id": order.id,
                "station_id": order.station_id,
                "create_time": TimeFunc.time_to_str(order.create_time),
                "creator_id": order.creator_id,
                "demand_order_count": demand_order_count_dict.get(order.id, 0),
                "shop_count": shop_count,
                "wish_date": TimeFunc.time_to_str(order.wish_date, "date"),
                "status": order.status,
            })

        has_more = len(wish_orders) >= limit
        return self.send_success(order_list=order_list, has_more=has_more)
