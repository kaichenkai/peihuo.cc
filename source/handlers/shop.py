# -*- coding:utf-8 -*-
from collections import defaultdict

from dal import models
from handlers.base.pub_func import TimeFunc
from handlers.base.pub_web import StationBaseHandler
from handlers.base.webbase import BaseHandler


# 店铺
class Shop(StationBaseHandler):
    def get(self, shop_id):
        shop = models.Shop.get_by_id(self.session, shop_id, self.current_station.id)

        if not shop:
            return self.send_fail("没有找到此店铺")

        contacts = models.ShopContact.get_by_shop_id(self.session, shop.id)

        # 店铺订货人对应的用户信息
        contact_account_ids = {contact.account_id for contact in contacts}
        accounts = models.AccountInfo.get_by_ids(self.session, contact_account_ids)
        account_dict = {account.id: account for account in accounts}

        contacts_data = []
        for contact in contacts:
            account = account_dict.get(contact.account_id)

            contacts_data.append({
                "id": contact.id,
                "account_id": contact.account_id,
                "shop_id": contact.shop_id,
                "phone": contact.phone,
                "name": contact.name,
                "avatar": account.headimgurl if account else "",
                "status": contact.status,
            })

        shop_data = {
            "id": shop.id,
            "name": shop.name,
            "station_id": shop.station_id,
            "creator_id": shop.creator_id,
            "create_time": TimeFunc.time_to_str(shop.create_time),
            "abbreviation": shop.abbreviation,
            "address": shop.address,
            "status": shop.status,
            "contacts": contacts_data,
        }
        return self.send_success(shop=shop_data)

    @BaseHandler.check_arguments("abbreviation?:str", "name?:str", "address?:str", "contacts?:list")
    def put(self, shop_id):
        abbreviation = self.args.get("abbreviation").strip()
        name = self.args.get("name").strip()
        address = self.args.get("address").strip()
        contacts = self.args.get("contacts")

        if not contacts:
            return self.send_fail("至少有一个店铺订货人")
        valid, message = self.validate_contacts(contacts)
        if not valid:
            return self.send_fail(message)

        shop = models.Shop.get_by_id(self.session, shop_id, self.current_station.id)

        if not shop:
            return self.send_fail("没有找到此店铺")

        if abbreviation is not None:
            abbr_duplicated = self.session.query(models.Shop) \
                .filter(models.Shop.abbreviation == abbreviation,
                        models.Shop.station_id == self.current_station.id,
                        models.Shop.status == 0,
                        models.Shop.id != shop_id) \
                .first()
            if abbr_duplicated and abbr_duplicated.id != shop.id:
                return self.send_fail("该店铺简称已存在")

            if not abbreviation:
                return self.send_fail("店铺简称不能为空")
            elif len(abbreviation) > 4:
                return self.send_fail("店铺简称不能超过 4 个字符")

            shop.abbreviation = abbreviation

        if name is not None:
            shop.name = name

        if address is not None:
            shop.address = address

        # 删除旧订货人
        legacy_contacts = models.ShopContact.get_by_shop_id(self.session, shop.id)
        for legacy_contact in legacy_contacts:
            legacy_contact.status = -1

        # 添加新订货人
        phones = {contact["phone"] for contact in contacts}

        # 绑定到已有用户
        registered_users = self.session.query(models.AccountInfo) \
            .filter(models.AccountInfo.phone.in_(phones)) \
            .all()
        user_dict = {user.phone: user for user in registered_users}

        for new_contact in contacts:
            phone = new_contact["phone"]
            name = new_contact.get("name", phone)
            user = user_dict.get(phone)
            new_contact = models.ShopContact(
                shop_id=shop.id,
                account_id=user.id if user else 0,
                phone=phone,
                name=name,
            )
            self.session.add(new_contact)

        self.session.commit()

        return self.send_success()

    @BaseHandler.check_arguments("abbreviation:str", "name?:str", "address?:str", "contacts?:list")
    def post(self):
        abbreviation = self.args["abbreviation"].strip()
        name = self.args.get("name", "").strip()
        address = self.args.get("address", "").strip()
        contacts = self.args.get("contacts")
        if not contacts:
            return self.send_fail("至少有一个店铺订货人")

        valid, message = self.validate_contacts(contacts)
        if not valid:
            return self.send_fail(message)

        abbr_duplicated = self.session.query(models.Shop.id) \
            .filter(models.Shop.abbreviation == abbreviation, models.Shop.station_id == self.current_station.id, models.Shop.status == 0) \
            .scalar()
        if abbr_duplicated:
            return self.send_fail("该店铺简称已存在")

        if not abbreviation:
            return self.send_fail("店铺简称不能为空")
        elif len(abbreviation) > 4:
            return self.send_fail("店铺简称不能超过 4 个字符")

        new_shop = models.Shop(
            name=name,
            abbreviation=abbreviation,
            address=address,
            station_id=self.current_station.id,
            creator_id=self.current_user.id
        )
        self.session.add(new_shop)
        self.session.flush()

        # 添加门店订货人
        if contacts:
            phones = {contact["phone"] for contact in contacts}

            # 绑定到已有用户
            registered_users = self.session.query(models.AccountInfo) \
                .filter(models.AccountInfo.phone.in_(phones)) \
                .all()
            user_dict = {user.phone: user for user in registered_users}

            for contact in contacts:
                phone = contact["phone"]
                name = contact.get("name", phone)
                user = user_dict.get(phone)
                new_contact = models.ShopContact(
                    shop_id=new_shop.id,
                    account_id=user.id if user else 0,
                    phone=phone,
                    name=name,
                )
                self.session.add(new_contact)

        self.session.commit()

        return self.send_success()

    def validate_contacts(self, contacts):
        """门店联系人参数验证"""

        if not isinstance(contacts, list):
            return False, "联系人参数格式有误"

        phones = []
        for contact in contacts:
            if not isinstance(contact, dict):
                return False, "联系人参数项格式有误"

            if "phone" not in contact:
                return False, "参数缺失：phone"
            phone = contact["phone"]
            if not phone or len(phone) != 11:
                return False, "手机号码无效"
            if phone in phones:
                return False, "手机号码重复"
            else:
                phones.append(phone)

        return True, ""

    def delete(self, shop_id):
        shop = models.Shop.get_by_id(self.session, shop_id, self.current_station.id)

        if not shop:
            return self.send_fail("没有找到此店铺")

        shop.status = -1

        contacts = models.ShopContact.get_by_shop_id(self.session, shop.id)
        for contact in contacts:
            contact.status = -1

        self.session.commit()

        return self.send_success()


# 门店列表
class ShopList(StationBaseHandler):
    @BaseHandler.check_arguments("page?:int", "limit?:int")
    def get(self):
        page = self.args.get("page", 0)
        limit = self.args.get("limit", 20)

        shops = self.session.query(models.Shop) \
            .filter(models.Shop.station_id == self.current_station.id,
                    models.Shop.status == 0) \
            .offset(page * limit) \
            .limit(limit) \
            .all()

        shop_ids = [shop.id for shop in shops]

        contacts = models.ShopContact.get_by_shop_ids(self.session, shop_ids)
        contacts_dict = defaultdict(list)
        [contacts_dict[contact.shop_id].append(contact) for contact in contacts]

        # 店铺订货人对应的用户信息
        contact_account_ids = {contact.account_id for contact in contacts}
        accounts = models.AccountInfo.get_by_ids(self.session, contact_account_ids)
        account_dict = {account.id: account for account in accounts}

        shop_list = []
        for shop in shops:
            contacts = contacts_dict.get(shop.id, [])

            contacts_data = []
            for contact in contacts:
                account = account_dict.get(contact.account_id)

                contacts_data.append({
                    "id": contact.id,
                    "account_id": contact.account_id,
                    "shop_id": contact.shop_id,
                    "name": contact.name,
                    "phone": contact.phone,
                    "avatar": account.headimgurl if account else "",
                    "status": contact.status,
                })

            shop_data = {
                "id": shop.id,
                "serial_number": shop.serial_number,
                "name": shop.name,
                "station_id": shop.station_id,
                "creator_id": shop.creator_id,
                "create_time": TimeFunc.time_to_str(shop.create_time),
                "abbreviation": shop.abbreviation,
                "address": shop.address,
                "status": shop.status,
                "contacts": contacts_data,
            }
            shop_list.append(shop_data)

        has_more = len(shops) >= limit
        return self.send_success(shop_list=shop_list, has_more=has_more)
