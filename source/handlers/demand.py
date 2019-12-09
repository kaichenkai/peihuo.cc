# -*- coding:utf-8 -*-
from collections import defaultdict

from sqlalchemy import func
from tornado.web import Finish

import dal.models as models
from dal.db_configs import redis
from dal.redis_keys import KEY_DEMAND_ORDER_UPDATE_NOTIFICATIONS
from handlers.base.pub_func import TimeFunc, check_int, check_float, AuthFunc
from handlers.base.pub_web import ShopBaseHandler, DemandBaseHandler, StationBaseHandler
from handlers.base.webbase import BaseHandler
from handlers.wish_order import WishOrderMixin
from handlers.wish_order import CurrentWishOrderMixin
from handlers.call_pifa import GetPifaData
from libs.senguo_encrypt import PfSimpleEncrypt


# TODO 订货端取意向单，临时使用，为规避权限问题，权限系统设计完成后删除此类
class WishOrder(WishOrderMixin, ShopBaseHandler):
    pass


# 订货单详情Mixin, 用于在「通过链接访问」或「平台上」获取订货单数据
class DemandOrderMixin:
    def get(self, order_id):
        demand_order = models.DemandOrder.get_by_id(self.session, order_id)

        if not demand_order:
            return self.send_fail("没有找到此订货单")
        negative_order = demand_order.negative_order
        wish_order = models.WishOrder.get_by_id(self.session, demand_order.wish_order_id)

        if not wish_order:
            return self.send_fail("没有找到对应的意向单")

        order_goods_list = self.session.query(models.DemandOrderGoods) \
            .filter(models.DemandOrderGoods.demand_order_id == order_id,
                    models.DemandOrderGoods.status == 0) \
            .all()

        # 所有已确认的分车记录
        allocated_amount = self.session.query(models.AllocationOrder.goods_id,
                                              func.sum(models.AllocationOrderGoods.actual_allocated_amount),
                                              func.sum(models.PurchaseOrderGoods.subtotal),
                                              func.sum(models.PurchaseOrderGoods.actual_amount)) \
            .join(models.AllocationOrderGoods, models.AllocationOrder.id == models.AllocationOrderGoods.order_id) \
            .outerjoin(models.PurchaseOrderGoods, models.PurchaseOrderGoods.id == models.AllocationOrder.purchase_order_goods_id) \
            .filter(models.AllocationOrder.wish_order_id == wish_order.id,
                    models.AllocationOrder.status == 1,
                    models.AllocationOrderGoods.shop_id == demand_order.shop_id) \
            .group_by(models.AllocationOrder.goods_id) \
            .all()
        allocated_amount_dict = {data[0]: data[1] for data in allocated_amount}
        purchase_price_dict = {data[0]: (data[2] or 0) / (data[3] or 1) for data in allocated_amount}

        # 配货价
        packing_prices = self.session.query(models.ShopPackingPrice) \
            .filter(models.ShopPackingPrice.station_id == wish_order.station_id,
                    models.ShopPackingPrice.wish_order_id == wish_order.id,
                    models.ShopPackingPrice.shop_id == demand_order.shop_id) \
            .all()
        packing_price_dict = {price.goods_id: price for price in packing_prices}

        order_goods_data = []
        for order_goods in order_goods_list:
            current_storage = check_float(order_goods.current_storage / 100)
            # 订货备注
            demand_remarks = order_goods.remarks
            # 商品的规格体积、重量
            standards_volume = float(order_goods.goods.standards_volume)
            standards_weight = check_float(order_goods.goods.standards_weight / 100)

            # 订货数量、订货体积、订货重量
            demand_amount = check_float(order_goods.demand_amount / 100)
            if order_goods.modified_demand_amount is not None:
                demand_amount = check_float(order_goods.modified_demand_amount / 100)
            goods_volume = standards_volume
            goods_weight = standards_weight

            # 实配数量、实配体积、实配重量
            packed_amount = check_float(allocated_amount_dict.get(order_goods.goods_id, 0) / 100)
            packed_volume = check_float(packed_amount * standards_volume)
            packed_weight = check_float(packed_amount * standards_weight)
            # 采购价
            purchase_price = check_float(purchase_price_dict.get(order_goods.goods_id, 0))
            # 配货价
            packing_price_model = packing_price_dict.get(order_goods.goods_id)
            allocation_price = check_float(packing_price_model.price / 100) if packing_price_model else 0
            allocation_subtotal = check_float(packed_amount * allocation_price)

            if self.current_staff:
                if 9 not in self.current_staff.admin_permission_list and self.current_staff.super_admin_status == 0:
                    purchase_price = 0
                    allocation_price = 0
                    allocation_subtotal = 0

            wish_order_goods = order_goods.wish_order_goods
            order_goods_data.append({
                "id": order_goods.id,
                "wish_order_goods_id": order_goods.wish_order_goods_id,
                "goods_id": order_goods.goods_id,
                "goods_name": wish_order_goods.goods_name if wish_order_goods else order_goods.goods.name,
                "goods_name_modified": wish_order_goods.goods_name_modified if wish_order_goods else 0,
                "current_storage": current_storage,
                "goods_volume": goods_volume,
                "goods_weight": goods_weight,
                "demand_amount": demand_amount,
                "packed_amount": packed_amount,
                "packed_volume": packed_volume,
                "packed_weight": packed_weight,
                "purchase_price": purchase_price,
                "allocation_price": allocation_price,
                "allocation_subtotal": allocation_subtotal,
                "remarks": demand_remarks,
                "status": order_goods.status,
            })

        creator = demand_order.creator
        order_data = {
            "id": demand_order.id,
            "wish_order_id": demand_order.wish_order_id,
            "wish_order_status": wish_order.status,
            "shop_id": demand_order.shop_id,
            "create_time": TimeFunc.time_to_str(demand_order.create_time),
            "update_time": TimeFunc.time_to_str(demand_order.update_time),
            "creator_name": creator.username,
            "creator_avatar": creator.headimgurl,
            "status": demand_order.status,
            "goods_data": order_goods_data,
            "negative_order": negative_order
        }

        return self.send_success(order_data=order_data)

    @BaseHandler.check_arguments("negative_order:int")
    def update_dorder_negative_status(self, order_id):
        demand_order = models.DemandOrder.get_by_id(self.session, order_id)
        if not demand_order:
            return self.send_fail("无效的order_id订单参数")
        negative_order = self.args.get("negative_order", 0)
        if negative_order not in {0, 1}:
            return self.send_fail("请检查negative_order传入参数")
        demand_order.negative_order = negative_order
        # 根据订货单的“今日不订”状态改变不同，针对性的修改订货单的状态
        if negative_order == 1 and demand_order.status == 2:
            demand_order.status = 1
        if negative_order == 0 and demand_order.status == 1:
            demand_order.status = 2
        self.session.commit()
        return self.send_success()

    @BaseHandler.check_arguments("goods_list?:list", "status?:int", "action:?str")
    def put(self, order_id):
        status = self.args.get("status")
        goods_list = self.args.get("goods_list")
        action = self.args.get("action", "")

        demand_order = models.DemandOrder.get_by_id(self.session, order_id)
        if not demand_order:
            return self.send_fail("没有找到此订货单")
        if action == "update_dorder_negative_status":
            return self.update_dorder_negative_status(order_id)

        if status is not None:
            self.update_status(demand_order, status)

        if goods_list is not None:
            # 检验cookie中门店和订货单门店是否相同
            if demand_order.shop_id != self.current_shop.id:
                return self.send_fail("订货单和门店不匹配, 请刷新重试")

            self.update_goods_list(demand_order, goods_list)

            # 发送更新提醒
            redis.incr(KEY_DEMAND_ORDER_UPDATE_NOTIFICATIONS.format(demand_order.wish_order_id, self.current_shop.station_id))

        self.session.commit()
        return self.send_success()

    def update_status(self, demand_order, status):
        """更新订货单状态"""

        wish_order = models.WishOrder.get_by_id(self.session, demand_order.wish_order_id)
        if not wish_order:
            self.send_fail("没有找到对应的意向单")
            raise Finish()
        if wish_order.status >= 3:
            self.send_fail("意向单已截止订货")
            raise Finish()

        # 不能回到初始状态
        if status == 0 and demand_order.status > 0:
            self.send_fail("状态无效")
            raise Finish()

        demand_order.status = status

    def update_goods_list(self, demand_order, goods_list):
        """更新订货单货品列表"""
        valid, message = self.validate_goods_list(goods_list)
        if not valid:
            self.send_fail(message)
            raise Finish()

        wish_order = models.WishOrder.get_by_id(self.session, demand_order.wish_order_id)
        if not wish_order:
            self.send_fail("没有找到对应的意向单")
            raise Finish()
        if wish_order.status >= 3:
            self.send_fail("意向单已截止订货")
            raise Finish()

        demand_order_goods_list = models.DemandOrderGoods.get_by_order_id(self.session, demand_order.id)
        demand_order_goods_dict = {goods.id: goods for goods in demand_order_goods_list}

        for goods in goods_list:
            demand_goods_id = check_int(goods["id"])
            current_storage = round(check_float(goods.get("current_storage", 0)) * 100)
            demand_amount = round(check_float(goods.get("demand_amount", 0)) * 100)
            demand_remarks = goods.get("demand_remarks", "")

            demand_order_goods = demand_order_goods_dict[demand_goods_id]

            demand_order_goods.current_storage = current_storage
            demand_order_goods.demand_amount = demand_amount
            demand_order_goods.remarks = demand_remarks

        # 初次提交
        if demand_order.status == 0:
            demand_order.status = 2

    def validate_goods_list(self, goods_list):
        """校验商品列表参数"""
        if not isinstance(goods_list, list):
            return False, "商品列表参数格式有误"

        for goods in goods_list:
            if not isinstance(goods, dict):
                return False, "商品列表参数项格式有误"

            if "id" not in goods:
                return False, "参数缺失：id"

        # 有没有无效的订货单货品 ID
        demand_order_goods_ids = {check_int(goods["id"]) for goods in goods_list if "id" in goods and goods["id"]}
        valid_goods_list = models.DemandOrderGoods.get_by_ids(self.session, demand_order_goods_ids)
        valid_goods_ids = {goods.id for goods in valid_goods_list}
        if demand_order_goods_ids != valid_goods_ids:
            return False, "存在无效的订货单商品"

        return True, ""


# 门店通过链接访问订货单
class ShopDemandOrder(DemandOrderMixin, ShopBaseHandler):
    pass


# 平台上获取订货单数据
class StationDemandOrder(DemandOrderMixin, StationBaseHandler):
    pass


# 订货单列表
class DemandOrderList(ShopBaseHandler):
    @BaseHandler.check_arguments("wish_order_id:int")
    def get(self):
        wish_order_id = self.args["wish_order_id"]

        demand_orders = models.DemandOrder.get_all_by_wish_order_id(self.session, wish_order_id)

        order_ids = [order.id for order in demand_orders]
        order_goods_list = self.session.query(models.DemandOrderGoods) \
            .filter(models.DemandOrderGoods.demand_order_id.in_(order_ids),
                    models.DemandOrderGoods.status == 0) \
            .all()

        goods_ids = {goods.goods_id for goods in order_goods_list}
        goods_list = models.Goods.get_by_ids(self.session, goods_ids)
        goods_dict = {goods.id: goods for goods in goods_list}

        # 订货单商品数据
        order_goods_dict = defaultdict(list)
        for order_goods in order_goods_list:
            current_storage = check_float(order_goods.current_storage / 100)
            demand_amount = check_float(order_goods.demand_amount / 100)
            demand_remarks = order_goods.remarks

            goods = goods_dict.get(order_goods.goods_id)

            order_goods_dict[order_goods.demand_order_id].append({
                "id": order_goods.id,
                "wish_order_goods_id": order_goods.wish_order_goods_id,
                "goods_id": order_goods.goods_id,
                "goods_name": goods.name if goods else "",
                "current_storage": current_storage,
                "demand_amount": demand_amount,
                "remarks": demand_remarks,
                "status": order_goods.status,
            })

        shop_ids = {order.shop_id for order in demand_orders}
        shops = models.Shop.get_by_ids(self.session, shop_ids)
        shop_dict = {shop.id: shop for shop in shops}

        order_list = []
        for order in demand_orders:
            order_goods_data = order_goods_dict.get(order.id, [])
            shop = shop_dict.get(order.shop_id)

            order_data = {
                "id": order.id,
                "wish_order_id": order.wish_order_id,
                "shop_id": order.shop_id,
                "shop_name": shop.abbreviation if shop else "",
                "create_time": TimeFunc.time_to_str(order.create_time),
                "status": order.status,
                "goods_data": order_goods_data,
            }
            order_list.append(order_data)

        return self.send_success(order_list=order_list)


# 订货单意向单同步
class DemandOrderSyncronization(ShopBaseHandler):
    @BaseHandler.check_arguments("wish_order_id:int")
    def put(self):
        shop_id = self.current_shop.id
        wish_order_id = self.args["wish_order_id"]

        shop = models.Shop.get_by_id(self.session, shop_id)
        if not shop:
            return self.send_fail("没有找到对应的门店")
        wish_order = models.WishOrder.get_by_id(self.session, wish_order_id)
        if not wish_order:
            return self.send_fail("没有找到此意向单")

        # 检验店铺和意向单的中转站是否相同
        if shop.station_id != wish_order.station_id:
            return self.send_fail("意向单和订货门店不匹配,请刷新重试")

        # 获取或创建订货单
        demand_order = models.DemandOrder.get_by_wish_order_id(self.session, wish_order_id, shop_id)
        if not demand_order:
            demand_order = models.DemandOrder(
                wish_order_id=wish_order_id,
                shop_id=shop_id,
                creator_id=self.current_user.id,
            )
            self.session.add(demand_order)
            self.session.flush()

        wish_order_goods_list = models.WishOrderGoods.get_by_order_id(self.session, wish_order.id)
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
                    wish_order_goods_id=wish_goods.id,
                )
                self.session.add(demand_goods)
                self.session.flush()

        # 删除「没有对应的意向单商品」的订货单商品
        for deprecated_demand_goods in demand_order_goods_dict.values():
            deprecated_demand_goods.status = -1

        self.session.commit()
        return self.send_success(demand_order_id=demand_order.id)


# 订货门店列表
class DemandShopList(ShopBaseHandler):
    def get(self):
        # TODO 临时方案，之后需要检查用户身份
        if not self.current_shop:
            return self.send_fail("当前用户不是任何店铺的订货人")

        # 当前用户作为员工的所有店铺
        shops = self.session.query(models.Shop)\
            .join(models.ShopContact, models.ShopContact.shop_id == models.Shop.id)\
            .filter(models.Shop.status == 0,
                    models.ShopContact.status == 0,
                    models.Shop.station_id == self.current_station.id,
                    models.ShopContact.account_id == self.current_user.id)\
            .all()
        shop_list = []
        for shop in shops:
            shop_list.append({
                "id": shop.id,
                "name": shop.name,
                "abbreviation": shop.abbreviation,
                "address": shop.address,
                "station_name": shop.station.name
            })

        return self.send_success(shop_list=shop_list)


# 当前用户登录的门店
class CurrentShop(ShopBaseHandler):
    def get(self):
        shop = self.current_shop
        data = {}
        if shop:
            data = {
                "id": shop.id,
                "name": shop.name,
                "abbreviation": shop.abbreviation,
                "address": shop.address,
                "create_time": TimeFunc.time_to_str(shop.create_time),
                "status": shop.status,
                "station_name": shop.station.name
            }
        return self.send_success(data=data)

    @BaseHandler.check_arguments("shop_id:int")
    def put(self):
        shop_id = self.args["shop_id"]
        change_shop = self.session.query(models.Shop)\
            .join(models.ShopContact, models.ShopContact.shop_id == models.Shop.id)\
            .filter(models.Shop.id == shop_id,
                    models.ShopContact.account_id == self.current_user.id,
                    models.Shop.status == 0,
                    models.ShopContact.status == 0)\
            .first()
        if not change_shop:
            return self.send_fail("店铺切换失败")
        # 设置门店cookie
        self.set_current_shop_cookie(change_shop.id, domain=self._ARG_DEFAULT)
        # 设置门店中转站cookie
        demand_station_id = change_shop.station_id
        self.set_demand_station_cookie(demand_station_id, domain=self._ARG_DEFAULT)
        return self.send_success()


class DemandOrderStationCookie(ShopBaseHandler):
    @BaseHandler.check_arguments("station_id:int")
    def get(self):
        station_id = self.args["station_id"]
        # 访问订货单时设置门店中转站cookie
        self.set_demand_station_cookie(station_id, domain=self._ARG_DEFAULT)
        # 清除当前店铺cookie
        self.clear_current_shop_cookie()
        return self.send_success()


# 当前意向单 TODO 过渡用，在意向单汇总单重构完成后删除 ref: https://tower.im/teams/175903/todos/13413/24
class CurrentWishOrder(ShopBaseHandler, CurrentWishOrderMixin):
    def get(self):
        order_data = self.get_current_wish_order(self.current_shop.station)
        return self.send_success(order_data=order_data)


# 可订货的批发店铺列表
class PfShopList(DemandBaseHandler):
    def get(self):
        api = GetPifaData(self.current_user.passport_id, AuthFunc.gen_token())

        ret_dict = api.get_pf_shops(self.current_user.phone)
        if not ret_dict["success"]:
            return self.send_fail(ret_dict.get("msg", ""))

        data_list = []
        for data in ret_dict["data_list"]:
            data_list.append({
                "shop_id": check_int(PfSimpleEncrypt.decrypt(data.get("shop_id", 0))),
                "shop_name": data.get("shop_name", ""),
                "purchase_times": data.get("purchase_times", 0),
                "latest_order_time": data.get("latest_order_time", ""),
                "is_online_order_open": data.get("is_online_order_open", 0),
            })

        return self.send_success(data_list=data_list)


# 批发订货单
class PfDemandOrder(DemandBaseHandler):
    def get(self, order_id):
        order = self.session.query(models.ExternalDemandOrder) \
            .filter(models.ExternalDemandOrder.id == order_id,
                    models.ExternalDemandOrder.creator_id == self.current_user.id) \
            .first()
        if not order:
            return self.send_fail("没有找到该订货单")

        goods_list = order.goods_list.all()

        # 从批发获取订单详情
        api = GetPifaData(self.current_user.passport_id, AuthFunc.gen_token())
        ret_dict = api.get_pf_demand_order(self.current_user.phone, order.object_id, order.id)
        if not ret_dict["success"]:
            return self.send_fail(ret_dict.get("msg", ""))
        pf_order_data = ret_dict.get("data", {})
        pf_goods_dict = {goods_data.get("external_id"): goods_data for goods_data in pf_order_data.get("demand_lines", [])}

        demand_goods_list = []
        for goods in goods_list:
            # 同步批发订单信息
            pf_goods = pf_goods_dict.get(goods.id)
            if not goods.syncronized and pf_goods:
                sale_record_info = pf_goods.get("sale_record_info", {})
                goods.confirmed_amount = check_int(sale_record_info.get("amount", 0) * 100)
                goods.confirmed_unit = check_int(sale_record_info.get("unit", 0))
                goods.price = check_int(sale_record_info.get("unit_price", 0) * 100)
                goods.total_money = check_int(sale_record_info.get("sales_money", 0) * 100)
                # goods.syncronized = 1

            demand_goods_list.append({
                "id": goods.id,
                "goods_name": goods.goods_name,
                "demand_amount": check_float(goods.demand_amount / 100),
                "demand_unit": goods.demand_unit,
                "remarks": goods.remarks,
                "confirmed_amount": check_float(goods.confirmed_amount / 100),
                "confirmed_unit": goods.confirmed_unit,
                "price": check_float(goods.price / 100),
                "total_money": check_float(goods.total_money / 100),
            })

        data = {
            "shop_id": order.object_id,
            "shop_name": order.object_name,
            "demand_date": TimeFunc.time_to_str(order.demand_date, "date"),
            "create_time": TimeFunc.time_to_str(order.create_time),
            "status": order.status,
            "total_money": check_float(pf_order_data.get("order_money", 0) / 100),
            "goods_list": demand_goods_list,
        }

        self.session.commit()
        return self.send_success(data=data)

    @BaseHandler.check_arguments("action:str")
    def put(self, order_id):
        action = self.args["action"]

        order = self.session.query(models.ExternalDemandOrder) \
            .filter(models.ExternalDemandOrder.id == order_id,
                    models.ExternalDemandOrder.creator_id == self.current_user.id) \
            .first()
        if not order:
            return self.send_fail("没有找到该订货单")

        if action == "confirm":
            return self.confirm(order)
        else:
            return self.send_fail("action invalid")

    def confirm(self, order):
        api = GetPifaData(self.current_user.passport_id, AuthFunc.gen_token())
        ret_dict = api.confirm_pf_demand_order(self.current_user.phone, order.object_id, order.id)
        if not ret_dict["success"]:
            return self.send_fail(ret_dict.get("msg", ""))

        return self.send_success()

    @BaseHandler.check_arguments("pf_shop_id:int", "pf_shop_name:str", "demand_date:date", "goods_list:list")
    def post(self):
        pf_shop_id = self.args["pf_shop_id"]
        pf_shop_name = self.args["pf_shop_name"]
        demand_date = self.args["demand_date"]
        goods_list = self.args["goods_list"]

        valid, message = self.validate_goods_list(goods_list)
        if not valid:
            return self.send_fail(message)

        # 添加到本地数据库
        new_order = models.ExternalDemandOrder(
            creator_id=self.current_user.id,
            target=1,
            object_id=pf_shop_id,
            object_name=pf_shop_name,
            demand_date=demand_date,
        )
        self.session.add(new_order)
        self.session.flush()

        demand_list = []
        for goods_data in goods_list:
            goods_name = goods_data["goods_name"]
            demand_amount = check_float(goods_data["demand_amount"])
            demand_unit = check_int(goods_data["demand_unit"])
            remarks = goods_data.get("remarks", "")

            new_order_goods = models.ExternalDemandOrderGoods(
                creator_id=self.current_user.id,
                order_id=new_order.id,
                goods_name=goods_name,
                demand_amount=check_int(demand_amount * 100),
                demand_unit=demand_unit,
                remarks=remarks,
            )
            self.session.add(new_order_goods)
            self.session.flush()
            unit_map = {0: "斤",
                        1: "件",
                        2: "kg",
                        3: "个",
                        4: "份",
                        5: "盒",
                        6: "只",
                        7: "包"}
            demand_list.append({
                "external_line_id": new_order_goods.id,
                "name": goods_name,
                "amount": demand_amount,
                "unit_text": unit_map.get(demand_unit, "斤"),
                "remark": remarks,
            })

        api = GetPifaData(self.current_user.passport_id, AuthFunc.gen_token())

        ret_dict = api.send_pf_demand_order(self.current_user.phone, pf_shop_id,
                                            new_order.id, demand_date, demand_list)
        if not ret_dict["success"]:
            return self.send_fail(ret_dict.get("msg", ""))

        self.session.commit()
        return self.send_success()

    def validate_goods_list(self, goods_list):
        """验证商品列表参数"""

        if not isinstance(goods_list, list):
            return False, "商品列表参数格式有误"

        for goods in goods_list:
            if not isinstance(goods, dict):
                return False, "商品列表参数项格式有误"

            if "goods_name" not in goods:
                return False, "参数缺失：goods_name"
            elif len(goods["goods_name"]) > 128:
                return False, "商品名过长：{}".format(goods["goods_name"])
            if "demand_amount" not in goods:
                return False, "参数缺失：demand_amount"
            elif check_float(goods["demand_amount"]) >= 2147483600:
                return False, "订货量过大：{}".format(goods["demand_amount"])
            if "demand_unit" not in goods:
                return False, "参数缺失：demand_unit"
            elif goods["demand_unit"] not in (0, 1, 2, 3, 4, 5, 6, 7):
                return False, "参数无效：demand_unit == {}".format(goods["demand_unit"])

        return True, ""


# 批发订货单列表
class PfDemandOrderList(DemandBaseHandler):
    @BaseHandler.check_arguments("page?:int", "limit?:int")
    def get(self):
        page = self.args.get("page", 0)
        limit = self.args.get("limit", 20)

        orders = self.session.query(models.ExternalDemandOrder,
                                    models.ExternalDemandOrder.id,
                                    func.count(models.ExternalDemandOrderGoods.id)) \
            .join(models.ExternalDemandOrderGoods, models.ExternalDemandOrderGoods.order_id == models.ExternalDemandOrder.id) \
            .filter(models.ExternalDemandOrder.creator_id == self.current_user.id) \
            .group_by(models.ExternalDemandOrder.id) \
            .order_by(models.ExternalDemandOrder.id.desc()) \
            .offset(page * limit) \
            .limit(limit) \
            .all()

        data_list = []
        for order, order_id, goods_count in orders:
            data_list.append({
                "id": order.id,
                "demand_date": TimeFunc.time_to_str(order.demand_date, "date"),
                "shop_name": order.object_name,
                "goods_count": goods_count or 0,
                "status": order.status,
            })

        has_more = len(data_list) >= limit
        return self.send_success(data_list=data_list, has_more=has_more)
