#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from handlers.base.pub_func import is_int, check_int, check_float
from handlers.base.pub_web import StationBaseHandler, PurchaseBaseHandler
from handlers.base.pub_web import BaseHandler
from dal import models, constants
from sqlalchemy import func, or_
from collections import defaultdict
from sqlalchemy.sql.functions import count


# 商品的供货商列表
class GoodsFirmList(StationBaseHandler):
    @BaseHandler.check_arguments("page?:int", "limit?:int", "search?:str")
    def get(self, goods_id):
        page = self.args.get("page", 0)
        limit = self.args.get("limit", constants.PAGE_SIZE)
        if limit > constants.PAGE_MAX_LIMIT:
            limit = constants.PAGE_SIZE
        search = self.args.get("search", "").strip()
        station_id = self.current_station.id
        goods = models.Goods.get_by_goods_id(self.session, goods_id, station_id=station_id)
        if not goods:
            return self.send_fail("此商品不存在")

        filters = list()
        if search:
            filters.append(or_(models.Firm.name.like("%{0}%".format(search)),
                               models.Firm.phone.like("%{0}%".format(search)),
                               models.Firm.name_acronym.like("%{0}%".format(search))
                               ))
        firm_goods_objs = self.session.query(models.Firm, models.FirmGoods)\
            .join(models.FirmGoods, models.FirmGoods.firm_id == models.Firm.id)\
            .filter(*filters,
                    models.Firm.station_id == self.current_station.id,
                    models.Firm.status == 0,
                    models.FirmGoods.goods_id == goods_id,
                    models.FirmGoods.status == 0)\
            .offset(page * limit)\
            .limit(limit)\
            .all()
        firm_ids = [firm.id for firm, _ in firm_goods_objs]

        firm_purchase_count_list = self.session.query(models.Firm.id, count(models.Firm.id))\
            .join(models.PurchaseOrderGoods, models.PurchaseOrderGoods.firm_id == models.Firm.id)\
            .filter(models.Firm.id.in_(firm_ids),
                    models.Firm.station_id == self.current_station.id,
                    models.Firm.status == 0,
                    models.PurchaseOrderGoods.goods_id == goods_id,
                    models.PurchaseOrderGoods.status >= 0)\
            .order_by(count(models.Firm.id).desc())\
            .group_by(models.Firm.id)\
            .all()
        purchase_count_dict = {firm_id: purchase_count for firm_id, purchase_count in firm_purchase_count_list}

        firm_list = list()
        for firm, firm_goods in firm_goods_objs:
            data = firm.to_dict()
            purchase_count = purchase_count_dict.get(firm.id, 0)

            data["purchase_times"] = purchase_count
            data["recommend"] = firm_goods.is_recommend
            data["recommend_remarks"] = firm_goods.remarks
            data["priority"] = 999999 + purchase_count if firm_goods.is_recommend else purchase_count
            firm_list.append(data)
            firm_list = sorted(firm_list, key=lambda x: x["priority"], reverse=True)
        has_more = len(firm_goods_objs) >= limit
        return self.send_success(firm_list=firm_list, has_more=has_more)


# 商品列表mixin,用于在小程序或平台上获取商品库数据
class GoodsListMixin:
    @BaseHandler.check_arguments("page?:int", "limit?:int", "search?:str")
    def get(self):
        page = self.args.get("page", 0)
        limit = self.args.get("limit", constants.PAGE_SIZE)
        if limit > constants.PAGE_MAX_LIMIT:
            limit = constants.PAGE_SIZE
        search = self.args.get("search", "").strip()
        station = self.current_station
        filters = list()
        if search:
            filters.append(or_(models.Goods.name.like("%{0}%".format(search)),
                               models.Goods.name_acronym.like("%{0}%".format(search))
                               ))
        goods_objects = self.session.query(models.Goods) \
            .filter(*filters,
                    models.Goods.station_id == station.id,
                    models.Goods.status == 0) \
            .offset(page * limit) \
            .limit(limit) \
            .all()
        goods_ids = [goods.id for goods in goods_objects]

        # 供货商信息
        firm_goods_objs = self.session.query(models.Firm, models.FirmGoods) \
            .join(models.FirmGoods, models.Firm.id == models.FirmGoods.firm_id) \
            .filter(models.FirmGoods.goods_id.in_(goods_ids),
                    models.FirmGoods.status == 0,
                    models.Firm.station_id == station.id,
                    models.Firm.status == 0) \
            .all()
        firm_dict = defaultdict(list)
        recommend_firm_dict = defaultdict(list)
        for firm, firm_goods in firm_goods_objs:
            # 商品的供货商
            firm_dict[firm_goods.goods_id].append(firm_goods.firm_id)
            # 商品的推荐供货商
            if firm_goods.is_recommend == 1:
                data = firm.to_dict()
                data["recommend_remarks"] = firm_goods.remarks
                recommend_firm_dict[firm_goods.goods_id].append(data)

        # 默认采购员信息
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

        goods_list = list()
        for goods in goods_objects:
            data = goods.to_stock_dict()
            # 商品的供货商数量
            firm_ids = firm_dict.get(goods.id, [])
            data["firm_amount"] = len(firm_ids)
            # 商品的推荐供货商数据
            data["recommend_firm"] = recommend_firm_dict.get(goods.id, [])

            default_purchaser = default_purchaser_dict.get(goods.id)
            purchaser_id = default_purchaser[0].id if default_purchaser else 0
            purchaser_name = default_purchaser[0].remarks or default_purchaser[1].username if default_purchaser else ""
            data["purchaser_id"] = purchaser_id,
            data["purchaser_name"] = purchaser_name

            goods_list.append(data)
        has_more = len(goods_objects) >= limit
        return self.send_success(goods_list=goods_list, has_more=has_more)


# 中转站获取商品库列表
class StationGoodsList(GoodsListMixin, StationBaseHandler):
    pass


# 采购小程序上获取商品库列表
class PurchaseGoodsList(GoodsListMixin, PurchaseBaseHandler):
    pass


# 商品Mixin
class GoodsMixin:
    def get(self, goods_id):
        station_id = self.current_station.id
        goods = models.Goods.get_by_goods_id(self.session, goods_id, station_id=station_id)
        if not goods:
            return self.send_fail("该商品不存在")
        goods_dict = {
            "name": goods.name,
            "code": goods.code,
            "length": check_float(goods.length / 100),
            "width": check_float(goods.width / 100),
            "height": check_float(goods.height / 100),
            "standards_volume": float(goods.standards_volume),
            "standards_weight": check_float(goods.standards_weight / 100)
        }
        return self.send_success(goods_dict=goods_dict)

    @BaseHandler.check_arguments("name:str", "code:str", "length?:float", "width?:float", "height?:float",
                                 "standards_weight?:float")
    def post(self):
        name = self.args["name"].strip()
        code = self.args["code"].strip()
        length = self.args.get("length", 0)
        width = self.args.get("width", 0)
        height = self.args.get("height", 0)
        standards_weight = self.args.get("standards_weight", 0)
        user = self.current_user
        station = self.current_station
        valid, message = self.validate_name_and_code(name, code, length, width, height, standards_weight)
        if not valid:
            return self.send_fail(message)
        new_goods = models.Goods(
            name=name,
            code=code,
            length=check_int(length * 100),
            width=check_int(width * 100),
            height=check_int(height * 100),
            standards_weight=check_int(standards_weight * 100),
            creator_id=user.id,
            station_id=station.id,
        )
        self.session.add(new_goods)
        self.session.commit()
        goods_dict = new_goods.to_dict()
        return self.send_success(goods_dict=goods_dict)

    @BaseHandler.check_arguments("action:str", "name?:str", "code?:str", "length?:float", "width?:float", "height?:float",
                                 "standards_weight?:float", "firm_id_list?:list", "firm_id?:int", "firm_list?:list")
    def put(self, goods_id):
        action = self.args["action"]
        station_id = self.current_station.id
        goods = models.Goods.get_by_goods_id(self.session, goods_id, station_id=station_id)
        if not goods:
            return self.send_fail("此商品不存在")
        if action == "edit_goodsinfo":
            name = self.args.get("name")
            code = self.args.get("code")
            length = self.args.get("length", 0)
            width = self.args.get("width", 0)
            height = self.args.get("height", 0)
            standards_weight = self.args.get("standards_weight", 0)

            valid, message = self.validate_name_and_code(name, code, length, width, height, standards_weight, goods_id=goods_id)
            if not valid:
                return self.send_fail(message)
            goods.name = name if name else goods.name
            goods.code = code if code else goods.code
            goods.length = check_int(length * 100)
            goods.width = check_int(width * 100)
            goods.height = check_int(height * 100)
            goods.standards_weight = check_int(standards_weight * 100)
            self.session.commit()
            return self.send_success()
        elif action == "update_firm":
            firm_id_list = self.args.get("firm_id_list", list())
            valid, message = self.validate_firm_id_list(firm_id_list)
            if not valid:
                return self.send_fail(message)
            goods_firm_list = self.session.query(models.FirmGoods) \
                .filter(models.FirmGoods.goods_id == goods_id,
                        models.FirmGoods.status == 0) \
                .all()
            goods_firm_dict = {goods_firm.firm_id: goods_firm for goods_firm in goods_firm_list}

            for firm_id in firm_id_list:
                goods_firm = goods_firm_dict.pop(firm_id, None)
                if not goods_firm:
                    goods_firm = models.FirmGoods(
                        goods_id=goods_id,
                        firm_id=firm_id
                    )
                    self.session.add(goods_firm)
                    self.session.flush()
            # 删除前端已删除的供货商
            for delete_goods_firm in goods_firm_dict.values():
                delete_goods_firm.status = -1
            self.session.commit()
            return self.send_success()
        elif action == "add_firm":
            # 给商品增加一个新的供货商
            firm_id = self.args.get("firm_id")
            result, message = models.FirmGoods.add_firm_goods(self.session, goods_id, firm_id, station_id)
            if not result:
                return self.send_fail(message)
            return self.send_success()
        elif action == "set_recommend_firm":
            firm_list = self.args.get("firm_list", list())
            valid, message = self.validate_firm_list(firm_list)
            if not valid:
                return self.send_fail(message)
            goods_firm_list = self.session.query(models.FirmGoods) \
                .filter(models.FirmGoods.goods_id == goods_id,
                        models.FirmGoods.status == 0) \
                .all()
            goods_firm_dict = {goods_firm.firm_id: goods_firm for goods_firm in goods_firm_list}
            for firm in firm_list:
                firm_id = firm["firm_id"]
                remarks = firm["remarks"]
                goods_firm = goods_firm_dict.pop(firm_id, None)
                if not goods_firm:
                    # 设置新的推荐供货商
                    goods_firm = models.FirmGoods(
                        goods_id=goods_id,
                        firm_id=firm_id,
                        is_recommend=1,
                        remarks=remarks
                    )
                    self.session.add(goods_firm)
                    self.session.flush()
                else:
                    goods_firm.is_recommend = 1
                    goods_firm.remarks = remarks
            for delete_goods_firm in goods_firm_dict.values():
                # 取消推荐供货商，但仍然是供货商
                if delete_goods_firm.is_recommend == 1:
                    delete_goods_firm.is_recommend = 0
            self.session.commit()
            return self.send_success()

        else:
            return self.send_fail("不支持的操作类型")

    def validate_name_and_code(self, name, code, length, width, height, standards_weight, goods_id=None):
        if name == "":
            return False, "请填写商品名称"
        if name and len(name) > constants.GOODS_NAME_LEN:
            return False, "商品名称过长"
        if code and not re.match(r"^[A-Za-z0-9_]+$", code):
            return False, "编码格式不正确"
        if code and len(code) > constants.GOODS_CODE_LEN:
            return False, "编码长度超过32位"
        if length < 0:
            return False, "长度不能是负数"
        if width < 0:
            return False, "宽度不能是负数"
        if height < 0:
            return False, "高度不能是负数"
        if standards_weight < 0:
            return False, "重量不能是负数"
        if length >= 21474836:
            return False, "长度的值过大"
        if width >= 21474836:
            return False, "宽度的值过大"
        if height >= 21474836:
            return False, "高度的值过大"
        if standards_weight >= 21474836:
            return False, "重量的值过大"

        # 商品名和编码不可以同时重复
        filters = list()
        if goods_id:
            filters.append(models.Goods.id != goods_id)
        name_code_list = self.session.query(models.Goods.name, models.Goods.code) \
            .filter(*filters,
                    models.Goods.name == name,
                    models.Goods.code == code,
                    models.Goods.station_id == self.current_station.id,
                    models.Goods.status == 0) \
            .all()
        name_code_tuple = [(name, code) for name, code in name_code_list]
        if (name, code) in name_code_tuple:
            return False, "商品重复"
        return True, ""

    def validate_firm_id_list(self, firm_id_list):
        if not isinstance(firm_id_list, list):
            return False, "供货商ID列表参数格式有误"
        if len(set(firm_id_list)) != len(firm_id_list):
            return False, "供货商ID参数重复"
        firm_list = models.Firm.get_by_ids(self.session, firm_id_list, station_id=self.current_station.id)
        firm_ids = [firm.id for firm in firm_list]
        if set(firm_ids) != set(firm_id_list):
            return False, "提交了无效的供货商"
        return True, ""

    def validate_firm_list(self, firm_list):
        """
        [
            {
                "firm_id": 1,
                "remarks": "备注"
            },
            ...
        ]
        """
        if not isinstance(firm_list, list):
            return False, "供货商列表参数格式有误"

        for firm in firm_list:
            if not isinstance(firm, dict):
                return False, "供货商字典参数格式有误"
            if "firm_id" not in firm:
                return False, "参数缺失：firm_id"
            elif not is_int(firm["firm_id"]):
                return False, "参数 firm_id 应为整数类型"
            if "remarks" not in firm:
                return False, "参数缺失：remarks"
            elif len(firm["remarks"]) > constants.REMARKS_LEN:
                return False, "备注长度超过128位"

        firm_id_set = {check_int(firm["firm_id"]) for firm in firm_list}
        firm_id_list = [check_int(firm["firm_id"]) for firm in firm_list]
        if len(firm_id_list) != len(firm_id_set):
            return False, "供货商ID重复"
        valid_firm_list = models.Firm.get_by_ids(self.session, firm_id_set, self.current_station.id)
        valid_firm_ids = {firm.id for firm in valid_firm_list}
        if firm_id_set != valid_firm_ids:
            return False, "提交了无效的供货商"

        return True, ""

    def delete(self, goods_id):
        station_id = self.current_station.id
        goods = models.Goods.get_by_goods_id(self.session, goods_id, station_id=station_id)
        if not goods:
            return self.send_fail("此商品不存在")
        goods.status = -1
        # 把供货商的供应货品也进行逻辑删除
        firm_goods_list = self.session.query(models.FirmGoods) \
            .join(models.Goods, models.FirmGoods.goods_id == models.Goods.id) \
            .filter(models.Goods.id == goods_id,
                    models.FirmGoods.status == 0) \
            .all()
        for firm_goods in firm_goods_list:
            firm_goods.status = -1
        self.session.commit()
        return self.send_success()


# 采购小程序商品处理
class PurchaseGoods(GoodsMixin, PurchaseBaseHandler):
    pass


# 中转站下商品处理
class StationGoods(GoodsMixin, StationBaseHandler):
    pass
