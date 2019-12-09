# -*- coding:utf-8 -*-

import datetime
from collections import defaultdict
from sqlalchemy import or_, func
from dal import models, constants
from handlers.base.pub_func import TimeFunc, check_int, check_float
from handlers.base.pub_web import StationBaseHandler, PurchaseBaseHandler
from handlers.base.webbase import BaseHandler
from celerywork.log_async_work import staff_log


# 员工
class Staff(StationBaseHandler):
    @BaseHandler.check_arguments("action:str")
    def get(self, staff_id):
        action = self.args["action"]
        staff_info = self.session.query(models.Staff, models.AccountInfo) \
            .join(models.AccountInfo, models.AccountInfo.id == models.Staff.account_id) \
            .filter(models.Staff.station_id == self.current_station.id,
                    models.Staff.status == 0,
                    models.Staff.id == staff_id) \
            .first()
        if not staff_info:
            return self.send_fail("找不到该员工")
        staff, account = staff_info

        if action == "staff_info":
            staff_data = {
                "account_id": account.id,
                "staff_id": staff.id,
                "avatar": account.headimgurl,
                "nickname": account.nickname,
                "realname": account.realname,
                "phone": account.phone,
                "position": staff.position,
                "birthday": TimeFunc.time_to_str(staff.birthday, "date"),
                "date_onboarding": TimeFunc.time_to_str(staff.date_onboarding, "date"),
                "remarks": staff.remarks,
                "admin_status": staff.admin_status,
                "purchaser_status": staff.purchaser_status,
                "admin_permissions": staff.admin_permission_list,
                "purchaser_permissions": staff.purchaser_permission_list,
                "status": staff.status,
            }
            return self.send_success(staff_data=staff_data)
        elif action == "day_summary_record":
            return self.day_summary_record(staff)
        elif action == "month_summary_record":
            return self.month_summary_record(staff)
        elif action == "with_goods_summary":
            return self.with_goods_summary(staff)
        elif action == "with_firm_summary":
            return self.with_firm_summary(staff)
        elif action == "day_summary_detail":
            return self.day_summary_detail(staff)
        elif action == "month_summary_detail":
            return self.month_summary_detail(staff)
        elif action == "goods_summary_detail":
            return self.goods_summary_detail(staff)
        elif action == "firm_summary_detail":
            return self.firm_summary_detail(staff)
        else:
            return self.send_fail("不支持的操作类型")

    @BaseHandler.check_arguments("page:int", "limit:int")
    def day_summary_record(self, staff):
        page = self.args.get("page", 0)
        limit = self.args.get("limit", constants.PAGE_SIZE)
        if limit > constants.PAGE_MAX_LIMIT:
            limit = constants.PAGE_SIZE

        purchase_dates = self.session.query(func.DATE(models.PurchaseOrderGoods.create_time))\
            .filter(models.PurchaseOrderGoods.purchaser_id == staff.id,
                    models.PurchaseOrderGoods.firm_id >= 0,
                    models.PurchaseOrderGoods.status >= 0)\
            .distinct()\
            .offset(page * limit)\
            .limit(limit)\
            .all()

        # 获取分页数据中最大时间和最小时间
        from_date = datetime.date.today()
        to_date = datetime.date.today()
        dates = [date[0] for date in purchase_dates]
        for date in dates:
            if date < from_date:
                from_date = date
            if date > to_date:
                to_date = date

        purchase_goods_objs = self.session.query(models.PurchaseOrderGoods)\
            .filter(models.PurchaseOrderGoods.purchaser_id == staff.id,
                    models.PurchaseOrderGoods.firm_id >= 0,
                    models.PurchaseOrderGoods.status >= 0,
                    func.DATE(models.PurchaseOrderGoods.create_time) >= from_date,
                    func.DATE(models.PurchaseOrderGoods.create_time) <= to_date)\
            .all()

        day_purchase_dict = defaultdict(list)
        for purchase_goods in purchase_goods_objs:
            purchase_date = TimeFunc.time_to_str(purchase_goods.create_time, _type="date")
            day_purchase_dict[purchase_date].append(purchase_goods.to_dict())

        purchase_goods_data_list = list()
        for date, purchase_goods_info in day_purchase_dict.items():
            data = dict()
            data["date"] = date
            # 货品数(区分日期)
            data["goods_num"] = 0
            data["goods_num"] += len({purchase_goods["goods_id"] for purchase_goods in purchase_goods_info})
            # 总件数
            data["goods_amount"] = check_float(sum(purchase_goods["actual_amount"] for purchase_goods in purchase_goods_info))
            # 总支出
            data["goods_subtotal"] = check_float(sum(purchase_goods["subtotal"] for purchase_goods in purchase_goods_info))
            purchase_goods_data_list.append(data)
        # 排序
        purchase_goods_data_list = sorted(purchase_goods_data_list, key=lambda x: x["date"], reverse=True)
        has_more = len(purchase_goods_objs) >= limit
        return self.send_success(purchase_goods_data_list=purchase_goods_data_list, has_more=has_more)

    def month_summary_record(self, staff):
        # TODO 月年的因为数据量不会多于 20 条，暂时不分页
        purchase_goods_objs = self.session.query(models.PurchaseOrderGoods)\
            .filter(models.PurchaseOrderGoods.purchaser_id == staff.id,
                    models.PurchaseOrderGoods.firm_id >= 0,
                    models.PurchaseOrderGoods.status >= 0)\
            .all()

        month_purchase_dict = defaultdict(list)
        for purchase_goods in purchase_goods_objs:
            purchase_date = TimeFunc.time_to_str(purchase_goods.create_time, _type="year")
            month_purchase_dict[purchase_date].append(purchase_goods.to_dict())

        purchase_goods_data_list = list()
        for year, purchase_goods_info in month_purchase_dict.items():
            data = dict()
            data["year"] = year
            # 货品数(区分日期)
            data["goods_num"] = 0
            data["goods_num"] += len({purchase_goods["goods_id"] for purchase_goods in purchase_goods_info})
            # 总件数
            data["goods_amount"] = check_float(sum(purchase_goods["actual_amount"] for purchase_goods in purchase_goods_info))
            # 总支出
            data["goods_subtotal"] = check_float(sum(purchase_goods["subtotal"] for purchase_goods in purchase_goods_info))
            purchase_goods_data_list.append(data)

        # 排序
        purchase_goods_data_list = sorted(purchase_goods_data_list, key=lambda x: x["year"], reverse=True)
        return self.send_success(purchase_goods_data_list=purchase_goods_data_list)

    @BaseHandler.check_arguments("start_date:date", "end_date:date", "page:int", "limit:int")
    def with_goods_summary(self, staff):
        start_date = self.args["start_date"]
        end_date = self.args["end_date"]
        page = self.args["page"]
        limit = self.args["limit"]
        if limit > constants.PAGE_MAX_LIMIT:
            limit = constants.PAGE_SIZE
        goods_id_tuple = self.session.query(models.PurchaseOrderGoods.goods_id)\
            .filter(models.PurchaseOrderGoods.purchaser_id == staff.id,
                    models.PurchaseOrderGoods.firm_id >= 0,
                    models.PurchaseOrderGoods.status >= 0)\
            .distinct()\
            .offset(page * limit)\
            .limit(limit)\
            .all()
        goods_ids = [goods_id[0] for goods_id in goods_id_tuple] or [0]

        purchase_goods_objs = self.session.query(models.PurchaseOrderGoods)\
            .filter(models.PurchaseOrderGoods.goods_id.in_(goods_ids),
                    func.DATE(models.PurchaseOrderGoods.create_time) >= start_date,
                    func.DATE(models.PurchaseOrderGoods.create_time) < end_date,
                    models.PurchaseOrderGoods.purchaser_id == staff.id,
                    models.PurchaseOrderGoods.firm_id >= 0,
                    models.PurchaseOrderGoods.status >= 0)\
            .all()

        purchase_goods_dict = defaultdict(list)
        for purchase_goods in purchase_goods_objs:
            purchase_goods_dict[purchase_goods.goods_id].append(purchase_goods.to_dict())

        purchase_goods_data_list = list()
        for goods_id, purchase_goods_info in purchase_goods_dict.items():
            data = dict()
            data["goods_id"] = purchase_goods_info[0]["goods_id"]
            data["goods_name"] = purchase_goods_info[0]["goods_name"]
            # 采购次数
            data["purchase_count"] = len([purchase_goods["firm_id"] for purchase_goods in purchase_goods_info])
            # 总件数
            data["goods_amount"] = check_float(sum(purchase_goods["actual_amount"] for purchase_goods in purchase_goods_info))
            # 总支出
            data["goods_subtotal"] = check_float(sum(purchase_goods["subtotal"] for purchase_goods in purchase_goods_info))
            # 供货商名称列表
            data["firm_name_list"] = list({purchase_goods["firm_name"] for purchase_goods in purchase_goods_info})
            purchase_goods_data_list.append(data)

        has_more = len(goods_ids) >= limit
        return self.send_success(purchase_goods_data_list=purchase_goods_data_list, has_more=has_more)

    @BaseHandler.check_arguments("start_date:date", "end_date:date", "page:int", "limit:int")
    def with_firm_summary(self, staff):
        start_date = self.args["start_date"]
        end_date = self.args["end_date"]
        page = self.args["page"]
        limit = self.args["limit"]
        if limit > constants.PAGE_MAX_LIMIT:
            limit = constants.PAGE_SIZE

        firm_id_tuple = self.session.query(models.PurchaseOrderGoods.firm_id)\
            .filter(models.PurchaseOrderGoods.purchaser_id == staff.id,
                    models.PurchaseOrderGoods.firm_id >= 0,
                    models.PurchaseOrderGoods.status >= 0)\
            .distinct()\
            .offset(page * limit)\
            .limit(limit)\
            .all()
        firm_ids = [firm_id[0] for firm_id in firm_id_tuple] or [0]

        purchase_goods_objs = self.session.query(models.PurchaseOrderGoods)\
            .filter(models.PurchaseOrderGoods.firm_id.in_(firm_ids),
                    func.DATE(models.PurchaseOrderGoods.create_time) >= start_date,
                    func.DATE(models.PurchaseOrderGoods.create_time) < end_date,
                    models.PurchaseOrderGoods.purchaser_id == staff.id,
                    models.PurchaseOrderGoods.firm_id >= 0,
                    models.PurchaseOrderGoods.status >= 0)\
            .all()

        purchase_goods_dict = defaultdict(list)
        for purchase_goods in purchase_goods_objs:
            purchase_goods_dict[purchase_goods.firm_id].append(purchase_goods.to_dict())

        purchase_goods_data_list = list()
        for firm, purchase_goods_info in purchase_goods_dict.items():
            data = dict()
            data["firm_id"] = purchase_goods_info[0]["firm_id"]
            data["firm_name"] = purchase_goods_info[0]["firm_name"]
            # 采购次数(供货商id存在为已录入数据的采购商品)
            data["purchase_count"] = len([purchase_goods["firm_id"] for purchase_goods in purchase_goods_info])
            # 总支出/元
            data["goods_subtotal"] = check_float(sum(purchase_goods["subtotal"] for purchase_goods in purchase_goods_info))
            # 商品名称列表
            data["goods_name_list"] = list({purchase_goods["goods_name"] for purchase_goods in purchase_goods_info})
            purchase_goods_data_list.append(data)

        has_more = len(purchase_goods_objs) >= limit
        return self.send_success(purchase_goods_data_list=purchase_goods_data_list, has_more=has_more)

    @BaseHandler.check_arguments("date:date")
    def day_summary_detail(self, staff):
        date = self.args["date"]
        purchase_goods_objs = self.session.query(models.PurchaseOrderGoods) \
            .filter(func.DATE(models.PurchaseOrderGoods.create_time) == date,
                    models.PurchaseOrderGoods.purchaser_id == staff.id,
                    models.PurchaseOrderGoods.firm_id >= 0,
                    models.PurchaseOrderGoods.status >= 0) \
            .all()

        purchase_goods_dict = defaultdict(list)
        for purchase_goods in purchase_goods_objs:
            purchase_goods_dict[purchase_goods.goods_id].append(purchase_goods.to_dict())

        purchase_goods_data_list = list()
        day_summary_data = defaultdict(int)
        total_actual_amount = 0
        total_spending = 0
        for goods_id, purchase_goods_info in purchase_goods_dict.items():
            data = dict()
            data["goods_name"] = purchase_goods_info[0]["goods_name"]
            # 采购件数
            data["goods_amount"] = check_float(sum(purchase_goods["actual_amount"] for purchase_goods in purchase_goods_info))
            # 总支出/元
            data["goods_subtotal"] = check_float(sum(purchase_goods["subtotal"] for purchase_goods in purchase_goods_info))
            # 供货商采购记录
            data["firm_purchase_record"] = list()
            for purchase_goods in purchase_goods_info:
                data["firm_purchase_record"].append(purchase_goods)
            purchase_goods_data_list.append(data)
            total_actual_amount += data["goods_amount"]
            total_spending += data["goods_subtotal"]
        # 日汇总数据
        day_summary_data["total_actual_amount"] += check_float(total_actual_amount)
        day_summary_data["total_spending"] += check_float(total_spending)

        return self.send_success(purchase_goods_data_list=purchase_goods_data_list, day_summary_data=day_summary_data)

    @BaseHandler.check_arguments("start_date:date", "end_date:date")
    def month_summary_detail(self, staff):
        start_date = self.args["start_date"]
        end_date = self.args["end_date"]
        purchase_goods_objs = self.session.query(models.PurchaseOrderGoods) \
            .filter(func.DATE(models.PurchaseOrderGoods.create_time) >= start_date,
                    func.DATE(models.PurchaseOrderGoods.create_time) < end_date,
                    models.PurchaseOrderGoods.purchaser_id == staff.id,
                    models.PurchaseOrderGoods.firm_id >= 0,
                    models.PurchaseOrderGoods.status >= 0) \
            .all()

        purchase_goods_dict = defaultdict(list)
        for purchase_goods in purchase_goods_objs:
            purchase_goods_dict[purchase_goods.goods_id].append(purchase_goods.to_dict())

        purchase_goods_data_list = list()
        month_summary_data = defaultdict(int)
        total_actual_amount = 0
        total_spending = 0
        for goods_id, purchase_goods_info in purchase_goods_dict.items():
            data = dict()
            data["goods_name"] = purchase_goods_info[0]["goods_name"]
            # 采购件数
            data["goods_amount"] = check_float(sum(purchase_goods["actual_amount"] for purchase_goods in purchase_goods_info))
            # 总支出/元
            data["goods_subtotal"] = check_float(sum(purchase_goods["subtotal"] for purchase_goods in purchase_goods_info))
            # 供货商采购记录
            data["firm_purchase_record"] = list()
            for purchase_goods in purchase_goods_info:
                data["firm_purchase_record"].append(purchase_goods)
            purchase_goods_data_list.append(data)
            # 月汇总数据
            total_actual_amount += data["goods_amount"]
            total_spending += data["goods_subtotal"]
        month_summary_data["total_actual_amount"] = check_float(total_actual_amount)
        month_summary_data["total_spending"] = check_float(total_spending)

        return self.send_success(purchase_goods_data_list=purchase_goods_data_list, month_summary_data=month_summary_data)

    @BaseHandler.check_arguments("goods_id:int", "start_date:date", "end_date:date")
    def goods_summary_detail(self, staff):
        goods_id = self.args["goods_id"]
        start_date = self.args["start_date"]
        end_date = self.args["end_date"]

        purchase_goods_objs = self.session.query(models.PurchaseOrderGoods)\
            .filter(func.DATE(models.PurchaseOrderGoods.create_time) >= start_date,
                    func.DATE(models.PurchaseOrderGoods.create_time) < end_date,
                    models.PurchaseOrderGoods.goods_id == goods_id,
                    models.PurchaseOrderGoods.purchaser_id == staff.id,
                    models.PurchaseOrderGoods.firm_id >= 0,
                    models.PurchaseOrderGoods.status >= 0)\
            .all()

        day_purchase_dict = defaultdict(list)
        for purchase_goods in purchase_goods_objs:
            purchase_date = TimeFunc.time_to_str(purchase_goods.create_time, _type="date")
            day_purchase_dict[purchase_date].append(purchase_goods.to_dict())

        purchase_goods_data_list = list()
        goods_summary_data = defaultdict(int)
        total_actual_amount = 0
        total_spending = 0
        for date, purchase_goods_info in day_purchase_dict.items():
            data = dict()
            data["date"] = date
            # 供货商列表
            data["firm_name_list"] = list({purchase_goods["firm_name"] for purchase_goods in purchase_goods_info})
            # 总件数
            data["goods_amount"] = check_float(sum(purchase_goods["actual_amount"] for purchase_goods in purchase_goods_info))
            # 总支出
            data["goods_subtotal"] = check_float(sum(purchase_goods["subtotal"] for purchase_goods in purchase_goods_info))
            # 单价/元
            data["price"] = check_float(data["goods_subtotal"] / data["goods_amount"])
            purchase_goods_data_list.append(data)
            total_actual_amount += data["goods_amount"]
            total_spending += data["goods_subtotal"]
        # 按商品汇总数据
        goods_summary_data["total_actual_amount"] += check_float(total_actual_amount)
        goods_summary_data["total_spending"] += check_float(total_spending)

        # 排序
        purchase_goods_data_list = sorted(purchase_goods_data_list, key=lambda x: x["date"], reverse=True)
        return self.send_success(purchase_goods_data_list=purchase_goods_data_list, goods_summary_data=goods_summary_data)

    @BaseHandler.check_arguments("firm_id:int", "start_date:date", "end_date:date")
    def firm_summary_detail(self, staff):
        firm_id = self.args["firm_id"]
        start_date = self.args["start_date"]
        end_date = self.args["end_date"]

        purchase_goods_objs = self.session.query(models.PurchaseOrderGoods)\
            .filter(func.DATE(models.PurchaseOrderGoods.create_time) >= start_date,
                    func.DATE(models.PurchaseOrderGoods.create_time) < end_date,
                    models.PurchaseOrderGoods.firm_id == firm_id,
                    models.PurchaseOrderGoods.purchaser_id == staff.id,
                    models.PurchaseOrderGoods.firm_id >= 0,
                    models.PurchaseOrderGoods.status >= 0)\
            .all()

        purchase_goods_dict = defaultdict(list)
        for purchase_goods in purchase_goods_objs:
            purchase_goods_dict[purchase_goods.goods_id].append(purchase_goods.to_dict())

        purchase_goods_data_list = list()
        firm_summary_data = defaultdict(int)
        total_actual_amount = 0
        total_spending = 0
        for firm_name, purchase_goods_info in purchase_goods_dict.items():
            data = dict()
            data["goods_name"] = purchase_goods_info[0]["goods_name"]
            # 采购次数
            data["purchase_count"] = len([purchase_goods["firm_id"] for purchase_goods in purchase_goods_info])
            # 总件数
            data["goods_amount"] = check_float(sum(purchase_goods["actual_amount"] for purchase_goods in purchase_goods_info))
            # 总支出
            data["goods_subtotal"] = check_float(sum(purchase_goods["subtotal"] for purchase_goods in purchase_goods_info))
            # 单价/元
            data["price"] = check_float(data["goods_subtotal"] / data["goods_amount"])
            purchase_goods_data_list.append(data)
            total_actual_amount += data["goods_amount"]
            total_spending += data["goods_subtotal"]
        # 按供货商汇总数据
        firm_summary_data["total_actual_amount"] += total_actual_amount
        firm_summary_data["total_spending"] += total_spending

        return self.send_success(purchase_goods_data_list=purchase_goods_data_list, firm_summay_data=firm_summary_data)

    @BaseHandler.check_arguments("account_id:int")
    def post(self):
        account_id = self.args["account_id"]
        user = self.current_user
        station = self.current_station
        staff = models.Staff.get_by_account_id(self.session, account_id, station_id=self.current_station.id)
        if staff:
            return self.send_fail("该用户已经是员工了")

        staff = models.Staff(
            station_id=self.current_station.id,
            account_id=account_id,
        )
        self.session.add(staff)
        self.session.flush()

        self.update_staff(staff)

        self.session.commit()

        # 添加日志
        staff_log.delay(user.id, station.id, 1, staff.account.nickname)

        return self.send_success()

    def put(self, staff_id):
        staff = models.Staff.get_by_id(self.session, staff_id, self.current_station.id)

        if not staff:
            return self.send_fail("没有找到此员工")

        self.update_staff(staff)

        self.session.commit()

        return self.send_success()

    @BaseHandler.check_arguments("admin_status:int", "purchaser_status:int",
                                 "admin_permissions:list", "purchaser_permissions:list",
                                 "position?:str", "birthday?:date", "date_onboarding?:date", "remarks?:str",
                                 "realname?:str")
    def update_staff(self, staff):
        """更新员工信息"""
        admin_status = self.args["admin_status"]
        purchaser_status = self.args["purchaser_status"]
        admin_permissions = self.args["admin_permissions"]
        purchaser_permissions = self.args["purchaser_permissions"]
        position = self.args.get("position", "")
        birthday = self.args.get("birthday")
        date_onboarding = self.args.get("date_onboarding")
        remarks = self.args.get("remarks", "")
        realname = self.args.get("realname", "")
        # 添加日志
        self.add_modify_log(admin_status, purchaser_status, staff, admin_permissions, purchaser_permissions)

        staff.admin_status = admin_status
        staff.purchaser_status = purchaser_status

        admin_permissions = {check_int(permission) for permission in admin_permissions} - {0}
        staff.set_admin_permissions(admin_permissions)
        purchaser_permissions = {check_int(permission) for permission in purchaser_permissions} - {0}
        staff.set_purchaser_permissions(purchaser_permissions)

        staff.position = position
        staff.remarks = remarks

        staff.account.realname = realname

        if birthday:
            staff.birthday = birthday
        if date_onboarding:
            staff.date_onboarding = date_onboarding

    def add_modify_log(self, admin_status, purchaser_status, staff, admin_permissions, purchaser_permissions):
        modify_content = str()
        if admin_status != staff.admin_status and admin_status == 0:
            modify_content += "管理员状态更改为(关闭)|"
        if admin_status != staff.admin_status and admin_status == 1:
            modify_content += "管理员状态更改为(打开)|"
        if purchaser_status != staff.purchaser_status and purchaser_status == 0:
            modify_content += "采购员状态更改为(关闭)|"
        if purchaser_status != staff.purchaser_status and purchaser_status == 1:
            modify_content += "采购员状态更改为(打开)|"
        last_admin_permission_list = staff.admin_permission_list
        if set(last_admin_permission_list) - {0} != set(admin_permissions):
            # 管理员原有权限
            admin_permission_text = staff.admin_permission_text
            modify_content += "管理员原有权限:("
            for admin_permission in last_admin_permission_list:
                if admin_permission in admin_permission_text:
                    modify_content += "{0},".format(admin_permission_text.get(admin_permission, ""))
            modify_content += ")|"
            # 管理员当前权限
            modify_content += "管理员当前权限:("
            for admin_permission in admin_permissions:
                if admin_permission in admin_permission_text:
                    modify_content += "{0},".format(admin_permission_text.get(admin_permission, ""))
            modify_content += ")|"
        last_purchaser_permissions_list = staff.purchaser_permission_list
        if set(last_purchaser_permissions_list) - {0} != set(purchaser_permissions) - {0}:
            # 采购员原有权限
            purchaser_permission_text = staff.purchaser_permission_text
            modify_content += "采购员原有权限:("
            for purchaser_permission in last_purchaser_permissions_list:
                if purchaser_permission in purchaser_permission_text:
                    modify_content += "{0},".format(purchaser_permission_text.get(purchaser_permission, ""))
            modify_content += ")|"
            # 采购员当前权限
            modify_content += "采购员当前权限:("
            for purchaser_permission in purchaser_permissions:
                if purchaser_permission in purchaser_permission_text:
                    modify_content += "{0},".format(purchaser_permission_text.get(purchaser_permission, ""))
            modify_content += ")"
        if modify_content:
            staff_log.delay(self.current_user.id, self.current_station.id, 3, staff.account.nickname, modify_content)

    def delete(self, staff_id):
        user = self.current_user
        station = self.current_station
        staff = models.Staff.get_by_id(self.session, staff_id, self.current_station.id)

        if not staff:
            return self.send_fail("没有找到此员工")

        if self.current_staff.super_admin_status == 0 and self.current_staff.admin_status == 0:
            return self.send_fail("没有删除员工的权限")

        if staff.super_admin_status == 1:
            return self.send_fail("超级管理员不能被删除")

        staff.status = -1

        self.session.commit()

        # 添加日志
        staff_log.delay(user.id, station.id, 2, staff.account.nickname)

        return self.send_success()


# 员工列表
class StaffList(StationBaseHandler):
    @BaseHandler.check_arguments("role?:str", "search?:str", "page?:int", "limit?:int")
    def get(self):
        role = self.args.get("role")
        search = self.args.get("search", "").strip()
        page = self.args.get("page", 0)
        limit = self.args.get("limit", 20)

        staff_infos = self.session.query(models.Staff, models.AccountInfo) \
            .join(models.AccountInfo, models.AccountInfo.id == models.Staff.account_id) \
            .filter(models.Staff.station_id == self.current_station.id,
                    models.Staff.status == 0)

        if role == "purchaser":
            staff_infos = staff_infos.filter(models.Staff.purchaser_status == 1)
        elif role == "admin":
            staff_infos = staff_infos.filter(models.Staff.admin_status == 1)

        # 根据员工姓名或手机号查询(2018-12-11 by chenkai)
        if search:
            staff_infos = staff_infos.filter(or_(models.AccountInfo.realname.like('%{}%'.format(search)),
                                                 models.AccountInfo.nickname.like('%{}%'.format(search)),
                                                 models.AccountInfo.phone.like('%{}%'.format(search))))

        staff_infos = staff_infos.offset(page * limit) \
            .limit(limit) \
            .all()

        staff_list = []
        for staff, account in staff_infos:
            staff_list.append({
                "account_id": account.id,
                "staff_id": staff.id,
                "avatar": account.headimgurl,
                "name": account.username,
                "real_name": account.realname,
                "nick_name": account.nickname,
                "phone": account.phone,
                "super_admin_status": staff.super_admin_status,
                "admin_status": staff.admin_status,
                "purchaser_status": staff.purchaser_status,
                "remarks": staff.remarks,
            })

        has_more = len(staff_infos) >= limit
        return self.send_success(staff_list=staff_list, has_more=has_more)


# 用户搜索
class AccountSearch(StationBaseHandler):
    def get(self, keyword):
        account_info = self.session.query(models.AccountInfo) \
            .filter(or_(models.AccountInfo.id == check_int(keyword),
                        models.AccountInfo.phone == keyword)) \
            .first()

        account_data = {}
        if account_info:
            account_data = {
                "id": account_info.id,
                "avatar": account_info.headimgurl,
                "name": account_info.nickname,
                "phone": account_info.phone,
            }

        return self.send_success(account_data=account_data)


# 当前用户的员工身份
class CurrentStaffMixin:
    def should_check_identity(self):
        return False

    def get(self):
        staff = self.current_staff
        data = {}
        if staff:
            data = {
                "id": staff.id,
                "station_id": staff.station_id,
                "account_id": staff.account_id,
                "super_admin_status": staff.super_admin_status,
                "admin_status": staff.admin_status,
                "purchaser_status": staff.purchaser_status,
                "admin_permissions": staff.admin_permission_list,
                "purchaser_permissions": staff.purchaser_permission_list,
                "remarks": staff.remarks,
                "position": staff.position,
                "date_onboarding": TimeFunc.time_to_str(staff.date_onboarding, "date"),
                "birthday": TimeFunc.time_to_str(staff.birthday, "date"),
                "status": staff.status,
            }
        return self.send_success(data=data)


# 小程序获取当前用户信息
class PurchaseCurrentStaff(CurrentStaffMixin, PurchaseBaseHandler):
    pass


# 中转站获取当前用户信息
class StationCurrentStaff(CurrentStaffMixin, StationBaseHandler):
    pass


# 员工操作记录
class StaffOperationRecord(StationBaseHandler):
    @BaseHandler.check_arguments("page?:int", "limit?:int")
    def get(self):
        page = self.args.get("page", 0)
        limit = self.args.get("limit", constants.PAGE_SIZE)
        if limit > constants.PAGE_MAX_LIMIT:
            limit = constants.PAGE_SIZE
        station_id = self.current_station.id
        operation_record_objects = self.session.query(models.OperationLog)\
                                               .filter(models.OperationLog.log_type == 1,
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
