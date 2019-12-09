#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from collections import defaultdict
from dal import models, constants
from sqlalchemy import or_, func
from handlers.base.pub_web import BaseHandler, PurchaseBaseHandler
from handlers.base.pub_web import StationBaseHandler
from celerywork.log_async_work import firm_log
import re


# 供货商操作记录
class FirmOperationRecord(StationBaseHandler):
    @BaseHandler.check_arguments("page?:int", "limit?:int")
    def get(self):
        page = self.args.get("page", 0)
        limit = self.args.get("limit", constants.PAGE_SIZE)
        if limit > constants.PAGE_MAX_LIMIT:
            limit = constants.PAGE_SIZE
        station_id = self.current_station.id
        operation_record_objects = self.session.query(models.OperationLog)\
                                               .filter(models.OperationLog.log_type == 2,
                                                       models.OperationLog.station_id == station_id)\
                                               .order_by(models.OperationLog.create_time.desc())\
                                               .offset(page * limit)\
                                               .limit(limit)\
                                               .all()
        operation_record_list = list()
        for operation_record in operation_record_objects:
            data = operation_record.to_dict()
            operation_record_list.append(data)
        has_more = len(operation_record_objects) >= limit
        return self.send_success(operation_record_list=operation_record_list, has_more=has_more)


# 供货商的货品列表
class FirmGoodsList(StationBaseHandler):
    @BaseHandler.check_arguments("page?:int", "limit?:int", "search?:str")
    def get(self, firm_id):
        page = self.args.get("page", 0)
        limit = self.args.get("limit", constants.PAGE_SIZE)
        if limit > constants.PAGE_MAX_LIMIT:
            limit = constants.PAGE_SIZE
        search = self.args.get("search", "").strip()
        station_id = self.current_station.id
        firm = models.Firm.get_by_firm_id(self.session, firm_id, station_id=station_id)
        if not firm:
            return self.send_fail("供货商不存在")
        filters = list()
        if search:
            filters.append(or_(models.Goods.name.like("%{0}%".format(search)),
                               models.Goods.name_acronym.like("%{0}%".format(search))
                               ))
        firm_goods_list = self.session.query(models.Goods)\
                                      .join(models.FirmGoods, models.Goods.id == models.FirmGoods.goods_id)\
                                      .filter(*filters,
                                              models.FirmGoods.firm_id == firm_id,
                                              models.FirmGoods.status == 0,
                                              models.Goods.station_id == station_id,
                                              models.Goods.status == 0)\
                                      .offset(page * limit)\
                                      .limit(limit)\
                                      .all()
        # 采购次数
        purchase_goods_list = self.session.query(models.PurchaseOrderGoods.goods_id,
                                                 func.count(models.PurchaseOrderGoods.goods_id))\
                                          .filter(models.PurchaseOrderGoods.firm_id == firm_id,
                                                  models.PurchaseOrderGoods.status >= 0)\
                                          .group_by(models.PurchaseOrderGoods.goods_id)\
                                          .all()
        purchase_goods_dict = {goods_id: count for goods_id, count in purchase_goods_list}

        goods_list = list()
        for goods in firm_goods_list:
            data = {"id": goods.id, "name": goods.name}
            data["purchase_times"] = purchase_goods_dict.get(goods.id, 0)
            goods_list.append(data)
        has_more = len(firm_goods_list) >= limit
        return self.send_success(goods_list=goods_list, has_more=has_more)


# 供货商列表mixin,用于在小程序或平台上获取供货商列表数据
class FirmListMixin:
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
            filters.append(or_(models.Firm.name.like("%{0}%".format(search)),
                               models.Firm.phone.like("%{0}%".format(search)),
                               models.Firm.name_acronym.like("%{0}%".format(search))
                               ))
        firms = self.session.query(models.Firm) \
            .filter(*filters,
                    models.Firm.station_id == station.id,
                    models.Firm.status == 0) \
            .offset(page * limit) \
            .limit(limit) \
            .all()
        firm_ids = {firm.id for firm in firms}
        firm_goods_list = self.session.query(models.FirmGoods) \
            .filter(models.FirmGoods.firm_id.in_(firm_ids),
                    models.FirmGoods.status == 0) \
            .all()
        firm_goods_dict = defaultdict(list)
        [firm_goods_dict[firm_goods.firm_id].append(firm_goods.goods_id) for firm_goods in firm_goods_list]
        firm_list = []
        for firm in firms:
            data = firm.to_dict()
            goods_ids = firm_goods_dict.get(firm.id, [])
            data["goods_ids"] = list(set(goods_ids))
            firm_list.append(data)
        has_more = len(firms) >= limit
        return self.send_success(firm_list=firm_list, has_more=has_more)


# 采购小程序获取供货商列表
class PurchaseFirmList(FirmListMixin, PurchaseBaseHandler):
    pass


# 中转站获取供货商列表
class StationFirmList(FirmListMixin, StationBaseHandler):
    pass


# 编辑供货商
class Firm(PurchaseBaseHandler):
    # TODO 只有采购员权限的员工应该能新增/修改供货商
    def get(self, firm_id):
        station_id = self.current_station.id
        firm = models.Firm.get_by_firm_id(self.session, firm_id, station_id=station_id)
        if not firm:
            return self.send_fail("供货商不存在")
        firm_dict = {
            "id": firm.id,
            "name": firm.name,
            "phone": firm.phone,
            "remarks": firm.remarks
        }
        return self.send_success(firm_dict=firm_dict)

    @BaseHandler.check_arguments("name:str", "phone?:str", "remarks?:str")
    def post(self):
        user = self.current_user
        station = self.current_station
        name = self.args["name"].strip()
        phone = self.args.get("phone", "").strip()
        remarks = self.args.get("remarks", "").strip()
        valid, message = self.validate_name_and_phone(name, phone, remarks)
        if not valid:
            return self.send_fail(message)
        new_firm = models.Firm(
            name=name,
            phone=phone,
            remarks=remarks,
            creator_id=user.id,
            station_id=station.id
        )
        self.session.add(new_firm)
        self.session.commit()
        firm_dict = new_firm.to_dict()
        # 添加日志
        firm_log.delay(user.id, station.id, 1, new_firm.name)
        return self.send_success(firm_dict=firm_dict)

    @BaseHandler.check_arguments("action:str", "name?:str", "phone?:str", "remarks?:str", "goods_id_list?:list")
    def put(self, firm_id):
        action = self.args["action"].strip()
        station_id = self.current_station.id
        firm = models.Firm.get_by_firm_id(self.session, firm_id, station_id=station_id)
        if not firm:
            return self.send_fail("供货商不存在")
        if action == "edit_firminfo":
            return self.edit_firminfo(firm)
        elif action == "update_goods":
            return self.update_goods(firm)
        else:
            return self.send_fail("不支持的操作类型")

    def edit_firminfo(self, firm):
        name = self.args.get("name", "").strip()
        phone = self.args.get("phone", "").strip()
        remarks = self.args.get("remarks", "").strip()
        valid, message = self.validate_name_and_phone(name, phone, remarks, firm_id=firm.id)
        if not valid:
            return self.send_fail(message)
        # 添加日志(在修改之前记录)
        self.add_modify_log(firm, name, phone, remarks)
        firm.name = name
        firm.phone = phone
        firm.remarks = remarks
        self.session.commit()
        return self.send_success()

    def add_modify_log(self, firm, name, phone, remarks):
        user = self.current_user
        station = self.current_station
        modify_content = str()
        if name != firm.name:
            modify_content += "姓名更改({0}→{1}),".format(firm.name, name)
        if phone != firm.phone:
            modify_content += "手机号更改({0}→{1}),".format(firm.phone, phone)
        if remarks != firm.remarks:
            modify_content += "备注更改({0}→{1})".format(firm.remarks, remarks)
        if modify_content:
            firm_log.delay(user.id, station.id, 3, firm.name, modify_content=modify_content)

    def update_goods(self, firm):
        user = self.current_user
        station = self.current_station
        goods_id_list = self.args.get("goods_id_list", list())
        valid, message, goods_list = self.validate_goods_id_list(goods_id_list)
        if not valid:
            return self.send_fail(message)
        firm_goods_list = self.session.query(models.FirmGoods, models.Goods.name)\
                                      .join(models.Goods, models.Goods.id == models.FirmGoods.goods_id)\
                                      .filter(models.FirmGoods.firm_id == firm.id,
                                              models.FirmGoods.status == 0,
                                              models.Goods.status == 0)\
                                      .all()
        # 删除当前供货商的商品
        for firm_goods, goods_name in firm_goods_list:
            firm_goods.status = -1
        # 添加新的供应货品
        for goods_id in goods_id_list:
            firm_goods = models.FirmGoods(
                goods_id=goods_id,
                firm_id=firm.id
            )
            self.session.add(firm_goods)
        # 添加日志
        last_goods_name = [goods_name for firm_goods, goods_name in firm_goods_list]
        goods_name = [goods.name for goods in goods_list]
        modify_content = str()
        if goods_name != last_goods_name:
            modify_content += "修改供应货品({0}→{1})".format(last_goods_name, goods_name)
        if modify_content:
            firm_log.delay(user.id, station.id, 3, firm.name, modify_content)
        self.session.commit()
        return self.send_success()

    def validate_name_and_phone(self, name, phone, remarks, firm_id=None):
        if not name:
            return False, "请输入供货商名称"
        if len(name) > constants.FIRM_NAME_LEN:
            return False, "供货商名称过长"
        if not phone:
            return False, "请输入手机号"
        if not re.match(r"^1[34578]\d{9}$", phone):
            return False, "请输入正确的手机号"
        if len(remarks) > constants.REMARKS_LEN:
            return False, "备注长度超过128位"
        filters = list()
        if firm_id:
            filters.append(models.Firm.id != firm_id)
        name_phone_list = self.session.query(models.Firm.name, models.Firm.phone)\
                                      .filter(*filters,
                                              or_(models.Firm.name == name, models.Firm.phone == phone),
                                              models.Firm.station_id == self.current_station.id,
                                              models.Firm.status == 0)\
                                      .all()
        name_phone_dict = {name: phone for name, phone in name_phone_list}
        if name in name_phone_dict.keys():
            return False, "供货商名称重复"
        if phone and phone in name_phone_dict.values():
            return False, "手机号重复"
        return True, ""

    def validate_goods_id_list(self, goods_id_list):
        if not isinstance(goods_id_list, list):
            return False, "商品列表参数格式有误"
        goods_list = models.Goods.get_by_ids(self.session, goods_id_list)
        goods_ids = [goods.id for goods in goods_list]
        if set(goods_ids) != set(goods_id_list):
            return False, "提交了无效的商品", []
        return True, "", goods_list

    def delete(self, firm_id):
        user = self.current_user
        station = self.current_station
        firm = models.Firm.get_by_firm_id(self.session, firm_id, station_id=station.id)
        if not firm:
            return self.send_fail("供货商不存在")
        firm.status = -1
        # 把商品的供货商也进行逻辑删除
        firm_goods_list = self.session.query(models.FirmGoods)\
                                      .join(models.Firm, models.FirmGoods.firm_id == models.Firm.id)\
                                      .filter(models.Firm.id == firm_id,
                                              models.FirmGoods.status == 0)\
                                      .all()
        for firm_goods in firm_goods_list:
            firm_goods.status = -1
        self.session.commit()
        # 添加日志
        firm_log.delay(user.id, station.id, 2, firm.name)
        return self.send_success()


# 供货商收款账户
class FirmPaymentAccount(StationBaseHandler):
    @BaseHandler.check_arguments("account_type:int", "account_name:str", "account_num:str", "branch_bank_no?:str")
    def post(self, firm_id):
        user = self.current_user
        station = self.current_station
        account_type = self.args["account_type"]
        account_name = self.args["account_name"]
        account_num = self.args["account_num"]
        branch_bank_no = self.args.get("branch_bank_no", "")

        if not account_num:
            return self.send_fail("支付账号不能为空")
        if not account_name:
            return self.send_fail("账户名不能为空")
        if account_type in [2, 3]:
            if not branch_bank_no:
                return self.send_fail("请选择开户银行")

        firm = models.Firm.get_by_firm_id(self.session, firm_id, self.current_station.id)
        if not firm:
            return self.send_fail("没有找到对应的供货商")

        accounts_count = self.session.query(func.count(models.FirmPaymentAccount.id)) \
            .filter(models.FirmPaymentAccount.firm_id == firm_id,
                    models.FirmPaymentAccount.status == 0) \
            .scalar()
        if accounts_count >= 4:
            return self.send_fail("每个供货商最多添加 4 个支付账号")

        account = models.FirmPaymentAccount(
            firm_id=firm_id,
            account_type=account_type,
            account_name=account_name,
            account_num=account_num,
            branch_bank_no=branch_bank_no,
            station_id=station.id,
            creator_id=user.id,
        )
        self.session.add(account)
        self.session.commit()
        # 添加日志
        account_type_dict = {0: "未知", 1: "支付宝账户", 2: "对公账户", 3: "私人账户"}
        account_type = account_type_dict.get(account.account_type, "未知")
        modify_content = "添加{0}({1})".format(account_type, account.account_num)
        firm_log.delay(user.id, station.id, 3, firm.name, modify_content)
        return self.send_success()

    @BaseHandler.check_arguments("account_type:int", "account_name:str", "account_num:str", "branch_bank_no?:str")
    def put(self, firm_id, account_id):
        account_type = self.args["account_type"]
        account_name = self.args["account_name"]
        account_num = self.args["account_num"]
        branch_bank_no = self.args.get("branch_bank_no", "")

        if not account_num:
            return self.send_fail("支付账号不能为空")
        if not account_name:
            return self.send_fail("账户名不能为空")
        if account_type in [2, 3]:
            if not branch_bank_no:
                return self.send_fail("请选择开户银行")

        firm = models.Firm.get_by_firm_id(self.session, firm_id, self.current_station.id)
        if not firm:
            return self.send_fail("没有找到对应的供货商")

        account = models.FirmPaymentAccount.get_by_id(self.session, account_id, self.current_station.id)
        if not account or account.status != 0:
            return self.send_fail("没有找到对应的供货商支付账号")

        # 添加日志（在修改之前）
        self.add_modify_account_log(account, account_type, account_name, account_num, firm.name)

        # 直接删了旧的重建，以便保留旧账户在其他地方的引用信息
        account.status = -1
        new_account = models.FirmPaymentAccount(
            firm_id=firm_id,
            account_type=account_type,
            account_name=account_name,
            account_num=account_num,
            branch_bank_no=branch_bank_no,
            station_id=self.current_station.id,
            creator_id=self.current_user.id,
        )
        self.session.add(new_account)
        self.session.commit()
        return self.send_success()

    def add_modify_account_log(self, account, account_type, account_name, account_num, firm_name):
        account_type_dict = {0: "未知", 1: "支付宝账户", 2: "对公账户", 3: "私人账户"}
        account_type = account_type_dict.get(account_type, "未知")
        modify_content = "{0}({1}),".format(account_type, account.account_num)
        if account_name != account.account_name:
            modify_content += "名称更改({0}→{1}),".format(account.account_name, account_name)
        if account_num != account.account_num:
            modify_content += "账号更改({0}→{1})".format(account.account_num, account_num)
        if modify_content != "{0}({1}),".format(account_type, account.account_num):
            firm_log.delay(self.current_user.id, self.current_station.id, 3, firm_name, modify_content)

    def delete(self, firm_id, account_id):
        firm = models.Firm.get_by_firm_id(self.session, firm_id, self.current_station.id)
        if not firm:
            return self.send_fail("没有找到对应的供货商")
        account = models.FirmPaymentAccount.get_by_id(self.session, account_id)
        if not account or account.status != 0:
            return self.send_fail("没有找到对应的供货商支付账号")

        account.status = -1
        self.session.commit()
        # 添加日志
        account_type_dict = {0: "未知", 1: "支付宝账户", 2: "对公账户", 3: "私人账户"}
        account_type = account_type_dict.get(account.account_type, "未知")
        modify_content = "删除{0}({1})".format(account_type, account.account_num)
        firm_log.delay(self.current_user.id, self.current_station.id, 3, firm.name, modify_content)
        return self.send_success()


# 供货商收款账户列表
class FirmPaymentAccountList(StationBaseHandler):
    @BaseHandler.check_arguments("firm_ids:str")
    def get(self):
        firm_ids = self.args["firm_ids"]
        firm_ids = firm_ids.split("|")
        accounts = self.session.query(models.FirmPaymentAccount) \
            .filter(models.FirmPaymentAccount.station_id == self.current_station.id,
                    models.FirmPaymentAccount.firm_id.in_(firm_ids),
                    models.FirmPaymentAccount.status == 0) \
            .all()

        branch_bank_nos = {account.branch_bank_no for account in accounts if account.branch_bank_no}
        banks = self.session.query(models.LcBank, models.LcParentBank, models.LcAreaCode) \
            .join(models.LcParentBank, models.LcParentBank.parent_bank_no == models.LcBank.parent_bank_no) \
            .join(models.LcAreaCode, models.LcAreaCode.city_code == models.LcBank.city_code) \
            .filter(models.LcBank.bank_no.in_(branch_bank_nos)) \
            .all()
        bank_dict = {bank[0].bank_no: bank for bank in banks}

        account_list = []
        for account in accounts:
            bank = bank_dict.get(account.branch_bank_no)
            firm = account.firm

            account_list.append({
                "id": account.id,
                "firm_id": firm.id,
                "firm_name": firm.name,
                "account_type": account.account_type,
                "account_name": account.account_name,
                "account_num": account.account_num,
                "branch_bank_no": account.branch_bank_no,
                "branch_bank_name": bank[0].bank_name if bank else "",
                "bank_no": bank[1].parent_bank_no if bank else 0,
                "bank_name": bank[1].parent_bank_name if bank else "",
                "bank_province_code": bank[2].province_code if bank else "",
                "bank_province_text": bank[2].province_text if bank else "",
                "bank_city_code": bank[2].city_code if bank else "",
                "bank_city_text": bank[2].city_text if bank else "",
            })

        return self.send_success(accounts=account_list)
