# models.py
import datetime
import random
from sqlalchemy import func, ForeignKey, Column, Index, event, Date, UniqueConstraint, SMALLINT
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Query, relationship, backref
from sqlalchemy.types import String, Integer, DateTime, DECIMAL
from dal.db_configs import MapBase, redis
from settings import QINIU_IMG_HOST, AUTH_UPDATE_INTERVAL, DB_NAME
from handlers.base.pub_func import check_float, TimeFunc, check_int


class _CommonApi:
    def save(self, session):
        s = session
        s.add(self)
        s.commit()

    def update(self, session, **kwargs):
        for key in kwargs.keys():
            setattr(self, key, kwargs[key])
        self.save(session)

    @classmethod
    def get_or_create_instance(cls, session, **kwargs):
        the_instance = session.query(cls).filter_by(**kwargs).first()
        if not the_instance:
            the_instance = cls(**kwargs)
            session.add(the_instance)
            session.flush()
            if_add = True
        else:
            if_add = False
        return if_add, the_instance


class _AccountApi(_CommonApi):

    @classmethod
    def get_by_id(cls, session, id):
        s = session
        try:
            u = s.query(cls).filter_by(id=id).one()
        except:
            u = None
        return u

    @classmethod
    def get_pwd_token(cls, session, id):
        user_pwd_token_key='user_pwd_token:%d'%id
        if redis.get(user_pwd_token_key):
            token = redis.get(user_pwd_token_key).decode()
        else:
            try:
                token = session.query(AccountInfo.password).filter_by(id=id).scalar()[24:48]
            except:
                token = ""
        return token

    @classmethod
    def get_by_passport_id(cls, session, passport_id):
        try:
            u = session.query(cls).filter_by(passport_id=passport_id).one()
        except:
            u = None
        return u

    @classmethod
    def calc_passport_hash(cls, passport_id):
        """计算passport hash"""
        from hashlib import md5
        from handlers.base.pub_func import AuthFunc
        columns = ("id", "phone", "wx_unionid", "qq_account", "email", "can_login")
        data = AuthFunc.get_passportinfo(passport_id)
        data["id"] = passport_id
        hash_str = "".join([str(data[c] or "") for c in columns])
        return md5(hash_str.encode()).hexdigest()


# 拼接图片域名
class AddImgDomain():
    @classmethod
    def add_domain(cls,img):
        """给图片添加图床域名"""
        if img and img[:1]!="/" and img[:5]!="https":
            return QINIU_IMG_HOST + img
        else:
            return img

    @classmethod
    def add_domain_muti(cls,imgs):
        """传入一个iterable对象，同时给多张图片添加图床域名"""
        imgs_list = []
        if imgs:
            for img in imgs:
                img = cls.add_domain(img)
                imgs_list.append(img)
        return imgs_list

    @classmethod
    def add_domain_headimg(cls,img):
        """为头像添加图床域名，返回 480x480 尺寸的头像"""
        if not img:
            return "/static/common/img/person.png"
        elif img[-4:]=="/132":
            return img[:-3] + "0"
        elif img[-2:]=="/0":
            return img
        else:
            return QINIU_IMG_HOST + img + "?imageView2/1/w/480/h/480"

    @classmethod
    def add_domain_headimgsmall(cls,img):
        """为头像添加图床域名，返回 100x100 尺寸的头像"""
        if not img:
            return "/static/common/img/person.png"
        elif img[-2:]=="/0":
            return img[:-1] + "132"
        elif img[-4:]=="/132":
            return img
        else:
            return QINIU_IMG_HOST + img + "?imageView2/1/w/100/h/100"

    @classmethod
    def add_domain_shop(cls,img):
        """为店铺图片添加图床域名"""
        return cls.add_domain(img) or "/static/images/shop_picture.png"


# 验证码用途
class VerifyCodeUse:
    # 非登录状态获取验证码用途
    login_verify_code_use = {
        'login': '登录森果采购配货系统账户',
        'bind': '森果采购配货系统账户绑定手机号',
        'station_register': '注册中转站',
    }
    # 登录用户获取验证码用途
    operation_verify_code_use = {
        'modify_password': '修改账户密码',
        'shopauth': '申请店铺认证',
        'ownpayment': '申请在线支付渠道',
    }

    @classmethod
    def get_use_text(cls, key, t='all'):
        """获取验证码用途文本

        输入参数
        key 验证码用途标志
        t 验证码用途类别，默认为'all'表示所有，可以取'login'和'operation'

        返回值
        验证码类别文本或None
        """
        if t == 'all':
            all_verify_code_use = cls.login_verify_code_use.copy()
            all_verify_code_use.update(cls.operation_verify_code_use)
            return all_verify_code_use.get(key)
        elif t == 'login':
            return cls.login_verify_code_use.get(key)
        elif t == 'operation':
            return cls.operation_verify_code_use.get(key)
        else:
            return None


class TimeBaseModel(object):
    """模型基类，为模型补充创建时间与更新时间"""
    create_time = Column(DateTime, nullable=False, default=func.now())  # 记录的创建时间
    update_time = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())  # 记录的更新时间


class AccountInfo(MapBase, _AccountApi):
    """用户的基本信息表
    """
    __tablename__ = "account_info"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    phone = Column(String(32), unique=True, default=None)               # 手机号
    sex = Column(TINYINT, nullable=False, default=0)                    # 用户性别 0:未知 1:男 2:女
    nickname = Column(String(64), default="")                           # 用户昵称
    realname = Column(String(128))                                      # 用户真实姓名
    headimgurl = Column(String(1024))                                   # 用户头像
    birthday = Column(Integer)                                          # 用户生日
    wx_country = Column(String(32))                                     # 用户所在国家
    wx_province = Column(String(32))                                    # 用户所在省份
    wx_city = Column(String(32))                                        # 用户所在城市
    wx_unionid = Column(String(64), unique = True)                      # 微信unionid
    wx_openid  = Column(String(64))                                     # 微信openid
    create_time = Column(DateTime, nullable=False, default=func.now())  # 创建时间
    passport_id = Column(Integer, unique=True, index=True)              # 森果通行证ID
    alipay_acctid = Column(String(50), nullable=False, default="")      # 支付宝账号
    alipay_acctname = Column(String(50), nullable=False, default="")    # 支付宝账号真实姓名

    @property
    def head_imgurl(self):
        return AddImgDomain.add_domain_headimg(self.headimgurl)

    @property
    def head_imgurl_small(self):
        return AddImgDomain.add_domain_headimgsmall(self.headimgurl)

    @property
    def username(self):
        return self.realname or self.nickname or ""

    @staticmethod
    def get_by_ids(session, account_ids):
        if not account_ids:
            return []
        account_list = session.query(AccountInfo) \
            .filter(AccountInfo.id.in_(account_ids)) \
            .all()
        return account_list


# 中转站
class TransferStation(MapBase):
    __tablename__ = "transfer_station"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False, default="")  # 中转站名称
    province = Column(Integer, nullable=False, default=0, index=True)  # 省份
    city = Column(Integer, nullable=False, default=0, index=True)  # 城市
    address = Column(String(100), nullable=False, default='')  # 店铺地址
    create_time = Column(DateTime, nullable=False, default=func.now())  # 创建时间
    status = Column(TINYINT, nullable=False, default=0)  # 状态 -1-已删除 0-正常

    creator_id = Column(Integer, ForeignKey(AccountInfo.id), nullable=False)  # 创建人 ID
    creator = relationship("AccountInfo", foreign_keys="TransferStation.creator_id")

    @staticmethod
    def get_by_id(session, station_id):
        station = session.query(TransferStation) \
            .filter(TransferStation.id == station_id,
                    TransferStation.status == 0) \
            .first()
        return station


# 日志
class OperationLog(TimeBaseModel, MapBase):
    __tablename__ = "operation_log"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    log_type = Column(TINYINT, nullable=False, default=0)  # 1：员工 2：供货商
    operation_object = Column(String(64), nullable=False, default="")  # 操作对象
    detail = Column(String(512), nullable=False, default="")  # 操作详情

    creator_id = Column(Integer, ForeignKey(AccountInfo.id), nullable=False)  # 创建人 ID
    creator = relationship("AccountInfo", foreign_keys="OperationLog.creator_id")

    station_id = Column(Integer, ForeignKey(TransferStation.id), nullable=False)  # 中转站 ID
    station = relationship("TransferStation", foreign_keys="OperationLog.station_id")

    def to_dict(self):
        reps_dict = {
            "id": self.id,
            "datetime": TimeFunc.time_to_str(self.create_time),
            "creator_name": self.creator.nickname,
            "operation_object": self.operation_object,
            "detail": self.detail
        }
        return reps_dict


# 打印机
class Printer(MapBase, TimeBaseModel):
    __tablename__ = "printer"

    id = Column(Integer, primary_key=True, autoincrement=True)
    wireless_print_num = Column(String(20), nullable=False, default="")  # 云打印机终端号
    wireless_print_key = Column(String(20), nullable=False, default="")  # 云打印机密钥
    remarks = Column(String(20), nullable=False, default="")  # 备注
    status = Column(TINYINT, nullable=False, default=0)  # 状态 -1-已删除 0-正常

    station_id = Column(Integer, ForeignKey(TransferStation.id), nullable=False)  # 中转站 ID
    station = relationship("TransferStation", foreign_keys="Printer.station_id")

    creator_id = Column(Integer, ForeignKey(AccountInfo.id), nullable=False)  # 创建人 ID
    creator = relationship("AccountInfo", foreign_keys="Printer.creator_id")

    @staticmethod
    def get_by_id(session, printer_id, station_id):
        printer = session.query(Printer) \
            .filter(Printer.id == printer_id,
                    Printer.station_id == station_id,
                    Printer.status == 0) \
            .first()
        return printer

    @staticmethod
    def get_by_station_id(session, station_id):
        printers = session.query(Printer) \
            .filter(Printer.station_id == station_id,
                    Printer.status == 0) \
            .all()
        return printers


# 员工
class Staff(MapBase):
    __tablename__ = "staff"

    admin_permissions_available = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    purchaser_permissions_available = [1, 2, 3, 4]

    id = Column(Integer, primary_key=True, autoincrement=True)
    super_admin_status = Column(TINYINT, nullable=False, default=0)  # 超级管理员状态 0-非管理员 1-有效
    admin_status = Column(TINYINT, nullable=False, default=0)  # 管理员状态 0-非管理员 1-有效
    purchaser_status = Column(TINYINT, nullable=False, default=0)  # 采购员状态 0-非采购员 1-有效
    admin_permissions = Column(String(512), nullable=False, default="")  # 管理员权限，由|分隔 1: 对账中心 2: 采购单 3: 商品库
    #  4: 仓库 5: 供货商 6: 店铺 7: 员工 8: 设置 9: 查看汇总单里的货品采购价 # 10: 查看仓库采购均价和采购成本
    purchaser_permissions = Column(String(512), nullable=False, default="")  # 采购员权限，由|分隔 1: 接受分店要货请求
    # 2: 查看全局采购汇总 3: 新建采购单 4: 查看货品采购价
    remarks = Column(String(50), nullable=False, default="")  # 员工备注
    position = Column(String(32), nullable=False, default="")  # 员工职位
    date_onboarding = Column(Date)  # 入职日期
    birthday = Column(Date)  # 生日
    status = Column(TINYINT, nullable=False, default=0)  # 状态 -1-已删除 0-正常

    station_id = Column(Integer, ForeignKey(TransferStation.id), nullable=False)  # 中转站 ID
    station = relationship("TransferStation", foreign_keys="Staff.station_id")

    account_id = Column(Integer, ForeignKey(AccountInfo.id))  # 用户 ID
    account = relationship("AccountInfo", foreign_keys="Staff.account_id")

    def is_admin(self):
        return self.super_admin_status == 1 or self.admin_status == 1

    @property
    def admin_permission_list(self):
        return list(map(lambda p: check_int(p), self.admin_permissions.split("|")))

    @property
    def purchaser_permission_list(self):
        return list(map(lambda p: check_int(p), self.purchaser_permissions.split("|")))

    def set_admin_permissions(self, admin_permission_list, grant_all=False):
        if grant_all:
            admin_permission_list = Staff.admin_permissions_available
        self.admin_permissions = "|".join({str(permission) for permission in admin_permission_list})

    def set_purchaser_permissions(self, purchaser_permission_list, grant_all=False):
        if grant_all:
            purchaser_permission_list = Staff.purchaser_permissions_available
        self.purchaser_permissions = "|".join({str(permission) for permission in purchaser_permission_list})

    @property
    def admin_permission_text(self):
        text_dict = {1: "对账中心", 2: "采购单", 3: "商品库", 4: "仓库",
                     5: "供货商", 6: "店铺", 7: "员工", 8: "设置", 9: "查看汇总单里的货品采购价"}
        return text_dict

    @property
    def purchaser_permission_text(self):
        text_dict = {1: "接受分店要货请求", 2: "查看全局采购汇总", 3: "新建采购单"}
        return text_dict

    @staticmethod
    def get_by_id(session, staff_id, station_id):
        staff = session.query(Staff) \
            .filter(Staff.id == staff_id,
                    Staff.station_id == station_id,
                    Staff.status == 0) \
            .first()
        return staff

    @staticmethod
    def get_by_account_id(session, account_id, station_id=None):
        staff = session.query(Staff) \
            .filter(Staff.account_id == account_id,
                    Staff.status == 0)

        if station_id is not None:
            staff = staff.filter(Staff.station_id == station_id)

        staff = staff.first()
        return staff

    @staticmethod
    def get_by_station_id(session, station_id):
        staff_list = session.query(Staff) \
            .filter(Staff.station_id == station_id) \
            .all()
        return staff_list


# 门店
class Shop(MapBase):
    __tablename__ = "shop"

    id = Column(Integer, primary_key=True, autoincrement=True)
    serial_number = Column(Integer, nullable=False)  # 店铺序列号
    name = Column(String(64), nullable=False, default="")  # 店铺名称
    create_time = Column(DateTime, nullable=False, default=func.now())  # 创建时间
    abbreviation = Column(String(8), nullable=False, default="")  # 店铺简称
    address = Column(String(256), nullable=False, default="")  # 店铺地址
    status = Column(TINYINT, nullable=False, default=0)  # 状态 -1-已删除 0-正常

    station_id = Column(Integer, ForeignKey(TransferStation.id), nullable=False)  # 中转站 ID
    station = relationship("TransferStation", foreign_keys="Shop.station_id")

    creator_id = Column(Integer, ForeignKey(AccountInfo.id), nullable=False)  # 创建人 ID
    creator = relationship("AccountInfo", foreign_keys="Shop.creator_id")

    contacts = relationship("ShopContact", back_populates="shop", lazy="dynamic")  # 门店订货人

    @staticmethod
    def get_by_id(session, shop_id, station_id=None):
        shop = session.query(Shop) \
            .filter(Shop.id == shop_id,
                    Shop.status == 0)

        if station_id:
            shop = shop.filter(Shop.station_id == station_id)

        shop = shop.first()
        return shop

    @staticmethod
    def get_by_ids(session, shop_ids, station_id=None):
        if not shop_ids:
            return []
        shop_list = session.query(Shop) \
            .filter(Shop.id.in_(shop_ids),
                    Shop.status == 0) \

        if station_id:
            shop_list = shop_list.filter(Shop.station_id == station_id)

        shop_list = shop_list.all()
        return shop_list

    @staticmethod
    def get_by_station_id(session, station_id):
        shops = session.query(Shop) \
            .filter(Shop.station_id == station_id,
                    Shop.status == 0) \
            .all()
        return shops


# 门店联系人
class ShopContact(MapBase):
    __tablename__ = "shop_contact"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer)  # 用户 ID，非系统用户时为空
    phone = Column(String(32), nullable=False, default="")  # 联系人手机号码
    name = Column(String(64), nullable=False, default="")  #  联系人姓名
    status = Column(TINYINT, nullable=False, default=0)  # 状态 -1-已删除 0-正常

    shop_id = Column(Integer, ForeignKey(Shop.id))  # 门店 ID
    shop = relationship("Shop", back_populates="contacts")

    @staticmethod
    def get_by_id(session, contact_id):
        contact = session.query(ShopContact) \
            .filter(ShopContact.id == contact_id,
                    ShopContact.status == 0) \
            .first()
        return contact

    @staticmethod
    def get_by_account_id(session, account_id):
        contact = session.query(ShopContact) \
            .filter(ShopContact.account_id == account_id,
                    ShopContact.status == 0) \
            .first()
        return contact

    @staticmethod
    def get_by_shop_id(session, shop_id):
        contacts = session.query(ShopContact) \
            .filter(ShopContact.shop_id == shop_id,
                    ShopContact.status == 0) \
            .all()
        return contacts

    @staticmethod
    def get_by_shop_ids(session, shop_ids):
        contacts = session.query(ShopContact) \
            .filter(ShopContact.shop_id.in_(shop_ids),
                    ShopContact.status == 0) \
            .all()
        return contacts


# 供货商-商品（多对多关系表）
class FirmGoods(TimeBaseModel, MapBase):
    __tablename__ = "firm_goods"

    id = Column(Integer, primary_key=True, autoincrement=True)
    goods_id = Column(Integer, ForeignKey("goods.id"))  # 商品id
    firm_id = Column(Integer, ForeignKey("firm.id"))  # 供货商id
    is_recommend = Column(TINYINT, nullable=False, default=0)  # 是否推荐 0:不推荐 1:推荐
    remarks = Column(String(128), nullable=False, default="")  # 推荐备注
    status = Column(TINYINT, nullable=False, default=0)  # 状态 0:正常 -1:已删除

    goods = relationship("Goods", back_populates="firms")
    firm = relationship("Firm", back_populates="goods_list")

    # 添加一条商品和供货商之间的对应关系
    @staticmethod
    def add_firm_goods(session, goods_id, firm_id, station_id):
        firm = Firm.get_by_firm_id(session, firm_id, station_id)
        if not firm:
            return True, "没有找到对应的供货商"
        goods = Goods.get_by_goods_id(session, goods_id, station_id)
        if not goods:
            return True, "没有找到采购商品对应的商品"
        firm_goods = session.query(FirmGoods)\
                            .filter(FirmGoods.goods_id == goods_id,
                                    FirmGoods.firm_id == firm_id,
                                    FirmGoods.status == 0)\
                            .all()
        if firm_goods:
            return True, "商品已绑定该供货商"
        firm_goods = FirmGoods(
            firm_id=firm_id,
            goods_id=goods_id
        )
        session.add(firm_goods)
        session.commit()
        return True, ""


# 商品的默认采购员
class StaffGoods(TimeBaseModel, MapBase):
    __tablename__ = "staff_goods"

    id = Column(Integer, primary_key=True, autoincrement=True)
    goods_id = Column(Integer, nullable=False)  # 商品 ID，Goods 表
    staff_id = Column(Integer, nullable=False)  # 采购员 ID，Staff 表


# 采购商户
class Firm(TimeBaseModel, MapBase):
    __tablename__ = "firm"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False, default="")               # 供货商名称
    name_acronym = Column(String(64), nullable=False, default="")            # 供货商中文名称首字母
    company_name = Column(String(64), nullable=False, default="")       # 企业全称
    type = Column(TINYINT, nullable=False, default=0)                   # 工商类型 0:个体 1:企业
    phone = Column(String(32), nullable=False, default="")               # 手机号
    remarks = Column(String(128), nullable=False, default="")           # 备注
    # long_supply_goods =                                               # 长期供应货品
    # legal_representative =                                            # 法人代表
    status = Column(TINYINT, nullable=False, default=0)                 # 状态 0:正常 -1:已删除

    station_id = Column(Integer, ForeignKey(TransferStation.id), nullable=False)  # 中转站id
    station = relationship("TransferStation", foreign_keys="Firm.station_id")

    creator_id = Column(Integer, ForeignKey(AccountInfo.id), nullable=False)  # 创建人ID
    creator = relationship("AccountInfo", foreign_keys="Firm.creator_id")

    goods_list = relationship("FirmGoods", back_populates="firm", lazy="dynamic")

    @staticmethod
    def get_by_firm_id(session, firm_id, station_id=None):
        firm = session.query(Firm).filter(Firm.id == firm_id, Firm.status == 0)
        if station_id:
            firm = firm.filter(Firm.station_id == station_id)
        firm = firm.first()
        return firm

    @staticmethod
    def get_by_ids(session, firm_ids, station_id=None):
        firm_list = session.query(Firm) \
            .filter(Firm.id.in_(firm_ids), Firm.status == 0)

        if station_id:
            firm_list = firm_list.filter(Firm.station_id == station_id)

        firm_list = firm_list.all()
        return firm_list

    def to_dict(self):
        reps_dict = {
            "id": self.id,
            "name": self.name,
            "company_name": self.company_name,
            "type": self.type,
            "phone": self.phone,
            "remarks": self.remarks
        }
        return reps_dict


# 利楚省市区县信息表
# 当前最长省 内蒙古自治区 6
# 当前最长市 中沙群岛的岛礁及其海域 11
# 当前最长区县 积石山保安族东乡族撒拉族自治县 15
class LcAreaCode(MapBase):
    __tablename__ = "lc_areacode"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    province_code = Column(String(3), nullable=False, default='', index=True)   # 省编码
    province_text = Column(String(32), nullable=False, default='')              # 省名称
    city_code     = Column(String(4), nullable=False, default='', index=True)   # 市编码
    city_text     = Column(String(64), nullable=False, default='')              # 市名称
    county_code   = Column(String(4), nullable=False, default='', index=True)   # 区县编码
    county_text   = Column(String(64), nullable=False, default='')              # 区县名称


# 利楚父级银行信息表
class LcParentBank(MapBase):
    __tablename__ = 'lc_parent_bank'

    parent_bank_no = Column(SMALLINT, primary_key=True)                 # 父级银行编码
    parent_bank_name = Column(String(64), nullable=False, default='')   # 父级银行名称


# 利楚支行信息表
class LcBank(MapBase):
    __tablename__ = "lc_bank"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    city_code = Column(String(4), nullable=False)                               # 城市编码
    parent_bank_no = Column(SMALLINT, ForeignKey(LcParentBank.parent_bank_no), nullable=False)  # 父级银行编码
    bank_no   = Column(String(32), nullable=False)                              # 支行编码
    bank_name = Column(String(64), nullable=False, default='')                  # 支行名称


# 商户收款账户
class FirmPaymentAccount(MapBase, TimeBaseModel):
    __tablename__ = "firm_payment_account"

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    account_type = Column(TINYINT, nullable=False, default=0)  # 提现账户类型 0-未知 1-支付宝 2-对公账户 3-私人账户
    account_name = Column(String(32), nullable=False, default="")  # 支付宝/银行账户名/公司全称
    account_num = Column(String(32), nullable=False, default="")  # 支付宝/银行账户帐号
    branch_bank_no = Column(String(32), nullable=False, default="")  # 开户支行编码（仅银行账户）
    status = Column(TINYINT, nullable=False, default=0)  # 状态 -1-删除 0-正常

    station_id = Column(Integer, ForeignKey(TransferStation.id), nullable=False)  # 中转站 ID
    station = relationship("TransferStation", foreign_keys="FirmPaymentAccount.station_id")

    firm_id = Column(Integer, ForeignKey(Firm.id), nullable=False)  # 商户 ID
    firm = relationship("Firm", foreign_keys="FirmPaymentAccount.firm_id")

    creator_id = Column(Integer, ForeignKey(AccountInfo.id), nullable=False)  # 创建人 ID
    creator = relationship("AccountInfo", foreign_keys="FirmPaymentAccount.creator_id")

    @staticmethod
    def get_by_id(session, account_id, station_id=None):
        account = session.query(FirmPaymentAccount) \
            .filter(FirmPaymentAccount.id == account_id,
                    FirmPaymentAccount.status == 0)

        if station_id:
            account = account.filter(FirmPaymentAccount.station_id == station_id)

        account = account.first()
        return account


# 商品
class Goods(TimeBaseModel, MapBase):
    __tablename__ = "goods"

    id = Column(Integer, primary_key=True, autoincrement=True)
    serial_number = Column(Integer, nullable=False)  # 商品序列号
    name = Column(String(128), nullable=False, default="")              # 商品名称
    name_acronym = Column(String(64), nullable=False, default="")           # 商品中文名称首字母
    code = Column(String(32), nullable=False, default="")               # 商品编码
    status = Column(TINYINT, nullable=False, default=0)                 # 状态 0:正常 -1:已删除
    stock = Column(Integer, nullable=False, default=0)                  # 库存
    stock_average_price = Column(Integer, nullable=False, default=0)    # 库存均价
    stock_cost = Column(Integer, nullable=False, default=0)             # 库存成本
    length = Column(Integer, nullable=False, default=0)  # 整件长度
    width = Column(Integer, nullable=False, default=0)  # 整件宽度
    height = Column(DECIMAL(14, 6), nullable=False, default=0)  # 整件高度
    standards_volume = Column(Integer, nullable=False, default=0)  # 体积
    standards_weight = Column(Integer, nullable=False, default=0)  # 重量

    station_id = Column(Integer, ForeignKey(TransferStation.id), nullable=False)  # 中转站id
    station = relationship("TransferStation", foreign_keys="Goods.station_id")

    creator_id = Column(Integer, ForeignKey(AccountInfo.id), nullable=False)  # 创建人 ID
    creator = relationship("AccountInfo", foreign_keys="Goods.creator_id")

    firms = relationship("FirmGoods", back_populates="goods", lazy="dynamic")

    @staticmethod
    def get_by_ids(session, goods_ids, station_id=None):
        goods_list = session.query(Goods) \
            .filter(Goods.id.in_(goods_ids), Goods.status == 0)

        if station_id is not None:
            goods_list = goods_list.filter(Goods.station_id == station_id)

        goods_list = goods_list.all()
        return goods_list

    @staticmethod
    def get_by_goods_id(session, goods_id, station_id=None):
        goods = session.query(Goods).filter(Goods.id == goods_id, Goods.status == 0)
        if station_id:
            goods = goods.filter(Goods.station_id == station_id)
        goods = goods.first()
        return goods

    def to_dict(self):
        reps_dict = {
            "id": self.id,
            "serial_number": self.serial_number,
            "name": self.name,
            "code": self.code,
        }
        return reps_dict

    def to_stock_dict(self):
        reps_dict = {
            "id": self.id,
            "serial_number": self.serial_number,
            "name": self.name,
            "code": self.code,
            "stock": check_float(self.stock / 100),
            "stock_average_price": check_float(self.stock_average_price / 100),
            "stock_cost": check_float(self.stock_cost / 100)
        }
        return reps_dict


# 意向单
class WishOrder(MapBase):
    __tablename__ = "wish_order"

    id = Column(Integer, primary_key=True, autoincrement=True)
    create_time = Column(DateTime, nullable=False, default=func.now())
    wish_date = Column(Date, nullable=False, default=func.curdate())  # 意向日期
    status = Column(TINYINT, nullable=False, default=1)  # 状态 1-草稿 2-已提交 3-已截止订货 4-已确认完成
    quotation_status = Column(TINYINT, nullable=False, default=1)  # 状态 1-草稿 2-制作完成

    station_id = Column(Integer, ForeignKey(TransferStation.id), nullable=False)  # 中转站 ID
    station = relationship("TransferStation", foreign_keys="WishOrder.station_id")

    creator_id = Column(Integer, ForeignKey(AccountInfo.id), nullable=False)  # 创建人 ID
    creator = relationship("AccountInfo", foreign_keys="WishOrder.creator_id")

    goods_list = relationship("WishOrderGoods", back_populates="order", lazy="dynamic")  # 意向单商品列表

    @staticmethod
    def get_by_id(session, order_id, station_id=None, status_list=None):
        if status_list is None:
            status_list = [1, 2, 3, 4]

        if not status_list:
            return None

        order = session.query(WishOrder) \
            .filter(WishOrder.id == order_id,
                    WishOrder.status.in_(status_list))

        if station_id:
            order = order.filter(WishOrder.station_id == station_id)

        order = order.first()
        return order


# 意向单商品
class WishOrderGoods(MapBase):
    __tablename__ = "wish_order_goods"

    id = Column(Integer, primary_key=True, autoincrement=True)
    create_time = Column(DateTime, nullable=False, default=func.now())
    goods_name = Column(String(128), nullable=False, default="")  # 货品名，可能和 goods.name 不同
    name_acronym = Column(String(128), nullable=False, default="")  # 货品名首字母
    goods_name_modified = Column(TINYINT, nullable=False, default=0)  # 货品名被修改过，0-否 1-是
    tag = Column(String(8), nullable=False, default="")  # 标签
    remarks = Column(String(128), nullable=False, default="")  # 说明
    today_price = Column(Integer, nullable=False, default=0)  # 今日报价
    confirmed_storage = Column(Integer, nullable=False, default=0)  # 意向单完成时的库存
    status = Column(TINYINT, nullable=False, default=1)  # 状态 -1-已删除 0-可订货 1-可能缺货 2-不可要货
    priority = Column(Integer, nullable=False, default=0)  # 排序优先级，0 为最前

    goods_id = Column(Integer, ForeignKey(Goods.id), nullable=False)  # 商品 ID
    goods = relationship("Goods", foreign_keys="WishOrderGoods.goods_id")

    wish_order_id = Column(Integer, ForeignKey(WishOrder.id), nullable=False)  # 意向单 ID
    order = relationship("WishOrder", back_populates="goods_list")

    @staticmethod
    def get_by_order_id(session, order_id):
        order_goods_list = session.query(WishOrderGoods) \
            .filter(WishOrderGoods.wish_order_id == order_id,
                    WishOrderGoods.status >= 0) \
            .all()
        return order_goods_list

    @staticmethod
    def get_by_ids(session, goods_ids):
        goods_list = session.query(WishOrderGoods) \
            .filter(WishOrderGoods.id.in_(goods_ids)) \
            .all()
        return goods_list

    def to_dict(self):
        reps_dict = {
            "id": self.id,
            "name": self.goods.name,
            "tag": self.tag,
            "remarks": self.remarks,
            "today_price": check_float(self.today_price / 100)
        }
        return reps_dict


# 订货单
class DemandOrder(MapBase, _CommonApi, TimeBaseModel):
    __tablename__ = "demand_order"

    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(TINYINT, nullable=False, default=0)  # 状态 0-已创建 1-已提交 2-已加入汇总单

    wish_order_id = Column(Integer, ForeignKey(WishOrder.id), nullable=False)  # 意向单 ID
    wish_order = relationship("WishOrder", foreign_keys="DemandOrder.wish_order_id")

    shop_id = Column(Integer, ForeignKey(Shop.id), nullable=False)  # 店铺 ID
    shop = relationship("Shop", foreign_keys="DemandOrder.shop_id")

    creator_id = Column(Integer, ForeignKey(AccountInfo.id), nullable=False)  # 创建人 ID
    creator = relationship("AccountInfo", foreign_keys="DemandOrder.creator_id")

    goods_list = relationship("DemandOrderGoods", back_populates="order", lazy="dynamic")  # 订货单商品列表
    negative_order = Column(TINYINT, nullable=False, default=0)     # 是否标记为"今日不订"订单，1为“今日不订”，0为正常订单

    @staticmethod
    def get_by_id(session, order_id, shop_id=None):
        order = session.query(DemandOrder) \
            .filter(DemandOrder.id == order_id)

        if shop_id:
            order = order.filter(DemandOrder.shop_id == shop_id)

        order = order.first()
        return order

    @staticmethod
    def get_all_by_wish_order_id(session, wish_order_id):
        orders = session.query(DemandOrder) \
            .filter(DemandOrder.wish_order_id == wish_order_id) \
            .all()
        return orders

    @staticmethod
    def get_by_wish_order_id(session, wish_order_id, shop_id):
        order = session.query(DemandOrder) \
            .filter(DemandOrder.wish_order_id == wish_order_id,
                    DemandOrder.shop_id == shop_id) \
            .first()
        return order


# 订货单商品
class DemandOrderGoods(MapBase):
    __tablename__ = "demand_order_goods"

    id = Column(Integer, primary_key=True, autoincrement=True)
    create_time = Column(DateTime, nullable=False, default=func.now())
    current_storage = Column(Integer, nullable=False, default=0)  # 当前库存
    demand_amount = Column(Integer, nullable=False, default=0)  # 要货量
    modified_demand_amount = Column(Integer)  # 修改后的要货量, 默认为None
    remarks = Column(String(128), nullable=False, default="")  # 要货备注
    status = Column(TINYINT, nullable=False, default=0)  # 状态 0:正常 -1:已删除

    goods_id = Column(Integer, ForeignKey(Goods.id), nullable=False)  # 商品 ID
    goods = relationship("Goods", foreign_keys="DemandOrderGoods.goods_id")

    demand_order_id = Column(Integer, ForeignKey(DemandOrder.id), nullable=False)  # 订货单 ID
    order = relationship("DemandOrder", back_populates="goods_list")

    wish_order_goods_id = Column(Integer, ForeignKey(WishOrderGoods.id))  # 意向单商品 ID, 将手动添加的采购商品添加为订货商品，没有对应的意向单id
    wish_order_goods = relationship("WishOrderGoods", foreign_keys="DemandOrderGoods.wish_order_goods_id")

    @staticmethod
    def get_by_order_id(session, order_id):
        order_goods_list = session.query(DemandOrderGoods) \
            .filter(DemandOrderGoods.demand_order_id == order_id,
                    DemandOrderGoods.status == 0) \
            .all()
        return order_goods_list

    @staticmethod
    def get_by_ids(session, goods_ids):
        goods_list = session.query(DemandOrderGoods) \
            .filter(DemandOrderGoods.id.in_(goods_ids),
                    DemandOrderGoods.status == 0) \
            .all()
        return goods_list

    def to_dict(self):
        reps_dict = {
            "id": self.id,
            "shop_id": self.order.shop_id,
            "shop_name": self.order.shop.abbreviation,
            "current_storage": check_float(self.current_storage / 100),
            "demand_amount": check_float(self.demand_amount / 100),
            "modified_demand_amount": check_float(self.modified_demand_amount / 100)
            if self.modified_demand_amount is not None else None
        }
        return reps_dict


# 采购单
class PurchaseOrder(TimeBaseModel, MapBase):
    __tablename__ = "purchase_order"

    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(TINYINT, nullable=False, default=0)  # 采购单状态 0: 待采购 1: 采购完成 -1：已删除

    station_id = Column(Integer, ForeignKey(TransferStation.id), nullable=False)  # 中转站 ID
    station = relationship("TransferStation", foreign_keys="PurchaseOrder.station_id")

    wish_order_id = Column(Integer, ForeignKey(WishOrder.id), nullable=False)  # 意向单 ID
    wish_order = relationship("WishOrder", foreign_keys="PurchaseOrder.wish_order_id")

    goods_list = relationship("PurchaseOrderGoods", back_populates="order", lazy="dynamic")  # 采购单商品列表

    @staticmethod
    def get_by_id(session, order_id, status_list=None):
        if status_list is None:
            status_list = [0, 1]

        if not status_list:
            return None

        order = session.query(PurchaseOrder).filter(PurchaseOrder.id == order_id,
                                                    PurchaseOrder.status.in_(status_list))
        order = order.first()
        return order

    def to_dict(self):
        reps_dict = {
            "id": self.id,
            "date": TimeFunc.time_to_str(self.wish_order.wish_date, _type="date"),
            "wish_order_id": self.wish_order_id
        }
        return reps_dict


# 采购单商品
class PurchaseOrderGoods(TimeBaseModel, MapBase):
    __tablename__ = "purchase_order_goods"
    payment_list = [0, 1, 2, 3, 4, 5]

    # 批发的支付方式：0: "所有支付方式", 1: "现金", 2: "pos刷卡", 3: "条码收款|微信", 4: "条码收款|支付宝", 7: "客户扫码付|微信", 8: "客户扫码付|支付宝",
    # 9: "赊账", 10: "组合支付", 11: "支票", 12: "汇款转账", 13: "余额支付"
    pf_payment_map_dict = {0: 5, 1: 0, 2: 1, 3: 2, 4: 3, 7: 2, 8: 3, 9: 4, 10: 5, 11: 5, 12: 5, 13: 5}

    # 批发的计价方式: 0: "按斤", 1: "按件"
    pf_unit_map_dict = {0: 1, 1: 0}

    id = Column(Integer, primary_key=True, autoincrement=True)
    estimated_amount = Column(Integer, nullable=False, default=0)               # 预采购量
    actual_amount = Column(Integer, nullable=False, default=0)  # 实际采购件数
    actual_weight = Column(Integer, nullable=False, default=0)  # 实际采购重量
    actual_unit = Column(TINYINT, nullable=False, default=0)  # 实际采购单位 0: 件  1: 斤
    fee = Column(Integer, nullable=False, default=0)  # 行费
    deposit = Column(Integer, nullable=False, default=0)  # 押金
    price = Column(Integer, nullable=False, default=0)  # 采购单价
    subtotal = Column(Integer, nullable=False, default=0)  # 小计
    payment = Column(TINYINT, nullable=False, default=0)  # 支付方式 0: 现金 1: 银行卡 2: 微信 3: 支付宝 4: 赊账 5: 其他
    is_purchase = Column(TINYINT, nullable=False, default=0)  # 0: 正常 1: 不采了
    status = Column(TINYINT, nullable=False, default=0)  # 货品状态 -3：初始备份(已弃用) -2: 已退货 -1：已删除 0: 正常
    tag = Column(TINYINT, nullable=False, default=0)  # 商品标签 0: 正常 1：采购员手动添加
    remarks = Column(String(128), nullable=False, default="")  # 采购备注

    wish_order_goods_id = Column(Integer, ForeignKey(WishOrderGoods.id))  # 意向单商品 ID, 手动添加的采购商品，没有对应的意向单id
    wish_order_goods = relationship("WishOrderGoods", foreign_keys="PurchaseOrderGoods.wish_order_goods_id")

    firm_id = Column(Integer, ForeignKey(Firm.id))  # 供货商id
    firm = relationship("Firm", foreign_keys="PurchaseOrderGoods.firm_id")

    goods_id = Column(Integer, ForeignKey(Goods.id), nullable=False)  # 商品 ID
    goods = relationship("Goods", foreign_keys="PurchaseOrderGoods.goods_id")

    purchaser_id = Column(Integer, ForeignKey(Staff.id))  # 采购员 ID，不安排采购时为空
    purchaser = relationship("Staff", foreign_keys="PurchaseOrderGoods.purchaser_id")

    purchase_order_id = Column(Integer, ForeignKey(PurchaseOrder.id))  # 采购单 ID  # 采购单id为空时，认为不采购
    order = relationship("PurchaseOrder", back_populates="goods_list")

    def __str__(self):
        return 'order_id:{0}'.format(self.id)

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "goods_id": self.goods_id,
            "goods_name": self.wish_order_goods.goods_name if self.wish_order_goods_id else self.goods.name,
            "wish_order_goods_id": self.wish_order_goods_id,
            "purchase_order_id": self.purchase_order_id,
            "is_purchase": self.is_purchase,
            "status": self.status,
            "tag": self.tag,
            "remarks": self.remarks,
            "estimated_amount": check_float(self.estimated_amount / 100),
            "actual_amount": check_float(self.actual_amount / 100),
            "actual_weight": check_float(self.actual_weight / 100),
            "actual_unit": self.actual_unit,
            "fee": check_float(self.fee / 100),
            "deposit": check_float(self.deposit / 100),
            "price": check_float(self.price / 100),
            "subtotal": check_float(self.subtotal / 100),
            "payment": self.payment,
            "firm_id": self.firm_id,
            "firm_name": self.firm.name if self.firm_id else "",
            "purchaser_id": self.purchaser_id,
            "stock": check_float(self.goods.stock / 100),
            "date": TimeFunc.time_to_str(self.create_time, _type="date")  # 创建日期
        }
        return resp_dict

    @staticmethod
    def get_by_id(session, goods_id, station_id=None):
        goods = session.query(PurchaseOrderGoods).filter(PurchaseOrderGoods.id == goods_id,
                                                         PurchaseOrderGoods.status >= 0)

        if station_id:
            goods = goods.join(PurchaseOrder, PurchaseOrder.id == PurchaseOrderGoods.purchase_order_id) \
                .filter(PurchaseOrder.station_id == station_id)

        goods = goods.first()
        return goods


# 采购动态
class PurchasingDynamics(TimeBaseModel, MapBase):
    __tablename__ = "purchasing_dynamics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_type = Column(TINYINT, nullable=False, default=0)  # 动态类型 0: 采购数据录入 1:采购数据修改 2: 不采了 3: 添加采购备注
    # 4: 修改商品名称  5: 新增采购商品 6: 移除商品

    goods_name = Column(String(128), nullable=False, default="")  # 商品名称
    last_goods_name = Column(String(128), nullable=False, default="")  # 上一次商品名称

    actual_amount = Column(Integer, nullable=False, default=0)  # 实际采购件数
    last_actual_amount = Column(Integer, nullable=False, default=0)  # 上一次实际采购件数

    actual_weight = Column(Integer, nullable=False, default=0)  # 实际采购重量
    last_actual_weight = Column(Integer, nullable=False, default=0)  # 上一次实际采购重量

    price = Column(Integer, nullable=False, default=0)  # 采购单价
    last_price = Column(Integer, nullable=False, default=0)  # 上次的采购单价

    actual_unit = Column(TINYINT, nullable=False, default=0)  # 实际采购单位 0: 件  1: 斤

    subtotal = Column(Integer, nullable=False, default=0)  # 小计
    last_subtotal = Column(Integer, nullable=False, default=0)  # 上一次的小计

    payment = Column(TINYINT, nullable=False, default=0)  # 支付方式 0: 现金 1: 银行卡 2: 微信 3: 支付宝 4: 赊账 5: 其他
    is_purchase = Column(TINYINT, nullable=False, default=0)  # 0: 正常 1: 不采了
    tag = Column(TINYINT, nullable=False, default=0)  # 商品标签 0: 正常 1：采购员手动添加
    remarks = Column(String(128), nullable=False, default="")  # 采购备注

    purchase_order_goods_id = Column(Integer, ForeignKey(PurchaseOrderGoods.id), nullable=False)  # 采购单商品 ID
    purchase_order_goods = relationship("PurchaseOrderGoods", foreign_keys="PurchasingDynamics.purchase_order_goods_id")

    purchase_order_id = Column(Integer, ForeignKey(PurchaseOrder.id), nullable=False)  # 采购单 ID
    purchase_order = relationship("PurchaseOrder", foreign_keys="PurchasingDynamics.purchase_order_id")

    wish_order_goods_id = Column(Integer, ForeignKey(WishOrderGoods.id))  # 意向单商品 ID, 手动添加的采购商品，没有对应的意向单id
    wish_order_goods = relationship("WishOrderGoods", foreign_keys="PurchasingDynamics.wish_order_goods_id")

    firm_id = Column(Integer, ForeignKey(Firm.id))  # 供货商id
    firm = relationship("Firm", foreign_keys="PurchasingDynamics.firm_id")

    last_firm_id = Column(Integer, ForeignKey(Firm.id))  # 供货商id
    last_firm = relationship("Firm", foreign_keys="PurchasingDynamics.last_firm_id")

    goods_id = Column(Integer, ForeignKey(Goods.id), nullable=False)  # 商品 ID
    goods = relationship("Goods", foreign_keys="PurchasingDynamics.goods_id")

    purchaser_id = Column(Integer, ForeignKey(Staff.id))  # 采购员 ID，不安排采购时为空
    purchaser = relationship("Staff", foreign_keys="PurchasingDynamics.purchaser_id")

    creator_id = Column(Integer, ForeignKey(AccountInfo.id), nullable=False)  # 操作人 ID
    creator = relationship("AccountInfo", foreign_keys="PurchasingDynamics.creator_id")

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "record_type": self.record_type,
            "goods_id": self.goods_id,
            "goods_name": [self.last_goods_name, self.goods_name],
            "is_purchase": self.is_purchase,
            "tag": self.tag,
            "remarks": self.remarks,
            "actual_amount": [check_float(self.last_actual_amount / 100), check_float(self.actual_amount / 100)],
            "actual_weight": [check_float(self.last_actual_weight / 100), check_float(self.actual_weight / 100)],
            "actual_unit": self.actual_unit,
            "price": [check_float(self.last_price / 100), check_float(self.price / 100)],
            "subtotal": [check_float(self.last_subtotal / 100), check_float(self.subtotal / 100)],
            "payment": self.payment,
            "firm_name": [self.last_firm.name if self.last_firm_id else "", self.firm.name if self.firm_id else ""],
            "purchaser_id": self.purchaser_id,
            "purchaser_name": self.purchaser.account.username if self.purchaser_id else "",
            "creator_id": self.creator_id,
            "creator_name": self.creator.username,
            "headimgurl": self.creator.headimgurl
        }
        return resp_dict


# 出/入库商品
class StockOutInGoods(TimeBaseModel, MapBase):
    __tablename__ = "stock_out_in_goods"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(TINYINT, nullable=False)                                  # 状态 0:出库 1:入库
    amount = Column(Integer, nullable=False, default=0)                     # 数量
    status = Column(TINYINT, nullable=False, default=0)                     # 状态 -1-已删除 0-待入库 1-已入库 2-待出库 3-已出库 4-出库已收货

    allocation_order_id = Column(Integer)  # 分车单 ID，分车入库的商品有此字段
    purchase_order_goods_id = Column(Integer)  # 采购单商品 ID，采购入库的记录有此字段  TODO 已经不需要，随时删除，删时同步删除线上数据库中的字段

    goods_id = Column(Integer, ForeignKey(Goods.id), nullable=False)  # 商品id
    goods = relationship("Goods", foreign_keys="StockOutInGoods.goods_id")

    wish_order_id = Column(Integer, ForeignKey(WishOrder.id), nullable=False)  # 意向单 ID
    wish_order = relationship("WishOrder", foreign_keys="StockOutInGoods.wish_order_id")

    station_id = Column(Integer, ForeignKey(TransferStation.id), nullable=False)  # 中转站 ID
    station = relationship("TransferStation", foreign_keys="StockOutInGoods.station_id")

    creator_id = Column(Integer, ForeignKey(AccountInfo.id), nullable=False)  # 创建人 ID
    creator = relationship("AccountInfo", foreign_keys="StockOutInGoods.creator_id")

    operator_id = Column(Integer, ForeignKey(AccountInfo.id), nullable=False)  # 操作人 ID
    operator = relationship("AccountInfo", foreign_keys="StockOutInGoods.operator_id")

    @staticmethod
    def get_by_id(session, record_id, station_id=None, status_list=None):
        if status_list is None:
            status_list = [0, 1, 2, 3, 4]

        if not status_list:
            return None

        record = session.query(StockOutInGoods) \
            .filter(StockOutInGoods.id == record_id,
                    StockOutInGoods.status.in_(status_list))

        if station_id:
            record = record.filter(StockOutInGoods.station_id == station_id)

        record = record.first()
        return record

    @staticmethod
    def generate_order_number():
        order_number = ["".join([str(random.randint(0, 9)) for _ in range(12)])]
        return order_number

    def to_dict(self):
        reps_dict = {
            "id": self.id,
            "goods_id": self.goods_id,
            "goods_name": self.goods.name,
            "creator_id": self.creator_id,
            "creator_name": self.creator.username,
            "operator_id": self.operator_id,
            "operator_name": self.operator.username,
            "record_datetime": TimeFunc.time_to_str(self.update_time),
            "type": self.type,
            "status": self.status,
            "amount": check_float(self.amount / 100),
            "wish_date": TimeFunc.time_to_str(self.wish_order.wish_date, _type="date"),
        }
        return reps_dict


# 库存操作记录
class StockOperationRecord(TimeBaseModel, MapBase):
    __tablename__ = "stock_operation_record"

    id = Column(Integer, primary_key=True, autoincrement=True)
    operation_detail = Column(String(256), nullable=False, default="")  # 操作详情
    remarks = Column(String(128), nullable=False, default="")  # 备注

    goods_id = Column(Integer, ForeignKey(Goods.id), nullable=False)  # 出入库商品 ID
    goods = relationship("Goods", foreign_keys="StockOperationRecord.goods_id")

    station_id = Column(Integer, ForeignKey(TransferStation.id), nullable=False)  # 中转站 ID
    station = relationship("TransferStation", foreign_keys="StockOperationRecord.station_id")

    creator_id = Column(Integer, ForeignKey(AccountInfo.id), nullable=False)  # 操作人 ID
    creator = relationship("AccountInfo", foreign_keys="StockOperationRecord.creator_id")

    def to_dict(self):
        reps_dict = {
            "id": self.id,
            "create_time": TimeFunc.time_to_str(self.create_time),
            "goods_name": self.goods.name,
            "goods_code": self.goods.code,
            "creator_name": self.creator.username,
            "operation_detail": self.operation_detail,
            "remarks": self.remarks
        }
        return reps_dict


# 单号对应表
class SerialNumberMap(MapBase, TimeBaseModel):
    __tablename__ = "serial_number_map"
    __table_args__ = (UniqueConstraint('order_no', 'order_id', 'order_type'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 订单类型 1: 入库单(StockOutInGoods) 2: 出库单(StockOutInGoods) 3: 店铺配送单(DemandOrder) 4: 供货商待结算单(AllocationOrder)
    # 5: 采购分车单(PurchaseOrderGoods) 6: 仓库分车单(StockOutInGoods)
    order_type = Column(TINYINT, nullable=False, default=0)
    order_id = Column(Integer, nullable=False, default=0)  # 订单 ID
    order_no = Column(String(16), nullable=False, default="")  # 单号

    @staticmethod
    def newest_order_no(session, order_type, order_date):
        date_start = datetime.datetime.combine(order_date, datetime.time.min)
        date_end = datetime.datetime.combine(order_date, datetime.time.max)
        order = session.query(SerialNumberMap) \
            .filter(SerialNumberMap.order_type == order_type,
                    SerialNumberMap.create_time >= date_start,
                    SerialNumberMap.create_time <= date_end) \
            .first()
        return order.order_no if order else ''

    @staticmethod
    def get_by_order_no(session, order_no):
        return session.query(SerialNumberMap) \
            .filter(SerialNumberMap.order_no == order_no) \
            .first()

    @staticmethod
    def generate(session, order_type, data_id, station_id, order_date=None):
        section_platform = '4'
        section_order_type = str(order_type).rjust(2, '0')
        section_station_id = str(station_id).rjust(3, '0')
        order_date = order_date or datetime.date.today()
        section_date = order_date.strftime('%y%m%d')

        def serial_number_padding(number):
            return str(number).rjust(4, '0')

        def slice_serial_number(_order_no):
            if not _order_no or len(_order_no) < 4:
                return 1
            return int(_order_no[-4:])

        # 订单序列号
        redis_key = 'ph_order_number:{}:{}'.format(section_date, order_type)
        section_serial_number = redis.get(redis_key)
        if not section_serial_number:
            order_no = SerialNumberMap.newest_order_no(session, order_type, order_date)
            section_serial_number = slice_serial_number(order_no)
            redis.set(redis_key, section_serial_number, ex=86400)
        pipe = redis.pipeline()
        pipe.get(redis_key)
        pipe.incrby(redis_key, 1)
        # execute返回命令执行结果列表, 这里获取订单序列号
        section_serial_number = pipe.execute()[0]
        section_serial_number = serial_number_padding(section_serial_number.decode())

        order_no = "{}{}{}{}{}".format(section_platform, section_order_type,
                                       section_station_id, section_date, section_serial_number)
        new_number = SerialNumberMap(
            order_type=order_type,
            order_id=data_id,
            order_no=order_no,
        )
        session.add(new_number)
        session.flush()
        return new_number


# 分车单
class AllocationOrder(MapBase, TimeBaseModel):
    __tablename__ = "allocation_order"

    id = Column(Integer, primary_key=True, autoincrement=True)

    purchase_order_goods_id = Column(Integer, ForeignKey(PurchaseOrderGoods.id))  # 采购单商品 ID，货品来自仓库时为空
    purchase_order_goods = relationship("PurchaseOrderGoods", foreign_keys="AllocationOrder.purchase_order_goods_id")
    stock_out_record_id = Column(Integer, ForeignKey(StockOutInGoods.id))  # 出库单 ID，货品来自采购时为空
    stock_out_record = relationship("StockOutInGoods", foreign_keys="AllocationOrder.stock_out_record_id")

    remarks = Column(String(256), nullable=False, default="")  # 备注

    status = Column(TINYINT, nullable=False, default=0)  # 状态 0-正常 1-已确认

    wish_order_id = Column(Integer, ForeignKey(WishOrder.id), nullable=False)  # 意向单 ID
    wish_order = relationship("WishOrder", foreign_keys="AllocationOrder.wish_order_id")

    goods_id = Column(Integer, ForeignKey(Goods.id), nullable=False)  # 商品 ID
    goods = relationship("Goods", foreign_keys="AllocationOrder.goods_id")

    order_no = Column(String(16), nullable=False, default="")  # 分车单号

    station_id = Column(Integer, ForeignKey(TransferStation.id), nullable=False)  # 中转站 ID
    station = relationship("TransferStation", foreign_keys="AllocationOrder.station_id")

    creator_id = Column(Integer, ForeignKey(AccountInfo.id), nullable=False)  # 操作人 ID
    creator = relationship("AccountInfo", foreign_keys="AllocationOrder.creator_id")

    goods_list = relationship("AllocationOrderGoods", back_populates="order", lazy="dynamic")  # 分车单货品列表

    @staticmethod
    def get_by_id(session, order_id, station_id=None):
        order = session.query(AllocationOrder).filter(AllocationOrder.id == order_id,
                                                      AllocationOrder.status >= 0)
        if station_id:
            order = order.filter(AllocationOrder.station_id == station_id)
        order = order.first()
        return order


# 分车单货品
class AllocationOrderGoods(MapBase, TimeBaseModel):
    __tablename__ = "allocation_order_goods"

    id = Column(Integer, primary_key=True, autoincrement=True)

    destination = Column(TINYINT, nullable=False, default=0)  # 配送目标 0: 门店 1: 仓库 2: 其他
    allocated_amount = Column(Integer, nullable=False, default=0)  # 初始化配送量
    actual_allocated_amount = Column(Integer, nullable=False, default=0)  # 实际配送量

    order_id = Column(Integer, ForeignKey(AllocationOrder.id), nullable=False)  # 分车单 ID
    order = relationship("AllocationOrder", back_populates="goods_list")

    shop_id = Column(Integer, ForeignKey(Shop.id))  # 门店 ID，送往仓库时为空
    shop = relationship("Shop", foreign_keys="AllocationOrderGoods.shop_id")

    @staticmethod
    def get_by_ids(session, goods_ids):
        goods_list = session.query(AllocationOrderGoods) \
            .filter(AllocationOrderGoods.id.in_(goods_ids)) \
            .all()
        return goods_list


# 供货商结算单
class FirmSettlementOrder(MapBase, TimeBaseModel):
    __tablename__ = "firm_settlement_order"

    id = Column(Integer, primary_key=True, autoincrement=True)

    agent_name = Column(String(128), nullable=False, default="")  # 经办人姓名
    agent_phone = Column(String(32), nullable=False, default="")  # 经办人手机号
    payment = Column(TINYINT, nullable=False, default=0)  # 付款方式 0-现金 1-银行卡 2-支付宝
    total_money = Column(Integer, nullable=False, default=0)  # 结算总金额
    remarks = Column(String(256), nullable=False, default="")  # 备注

    station_id = Column(Integer, ForeignKey(TransferStation.id), nullable=False)  # 中转站 ID
    station = relationship("TransferStation", foreign_keys="FirmSettlementOrder.station_id")

    payment_account_id = Column(Integer, ForeignKey(FirmPaymentAccount.id))  # 付款方式 ID，非现金结算时有值
    payment_account = relationship("FirmPaymentAccount", foreign_keys="FirmSettlementOrder.payment_account_id")

    creator_id = Column(Integer, ForeignKey(AccountInfo.id), nullable=False)  # 操作人 ID
    creator = relationship("AccountInfo", foreign_keys="FirmSettlementOrder.creator_id")


# 供货商待结算单
class FirmSettlementVoucher(MapBase, TimeBaseModel):
    __tablename__ = "firm_settlement_voucher"

    id = Column(Integer, primary_key=True, autoincrement=True)

    station_id = Column(Integer, ForeignKey(TransferStation.id), nullable=False)  # 中转站 ID
    station = relationship("TransferStation", foreign_keys="FirmSettlementVoucher.station_id")

    creator_id = Column(Integer, ForeignKey(AccountInfo.id), nullable=False)  # 操作人 ID
    creator = relationship("AccountInfo", foreign_keys="FirmSettlementVoucher.creator_id")

    allocation_order_id = Column(Integer, ForeignKey(AllocationOrder.id), nullable=False)  # 分车单 ID
    allocation_order = relationship("AllocationOrder", foreign_keys="FirmSettlementVoucher.allocation_order_id")

    firm_id = Column(Integer, ForeignKey(Firm.id), nullable=False)  # 商户 ID
    firm = relationship("Firm", foreign_keys="FirmSettlementVoucher.firm_id")

    settlement_order_id = Column(Integer, ForeignKey(FirmSettlementOrder.id))  # 结算单 ID，结算后有值
    settlement_order = relationship("FirmSettlementOrder", foreign_keys="FirmSettlementVoucher.settlement_order_id")

    settled_amount = Column(Integer)  # 实际结算件数，结算后有值
    settled_price = Column(Integer)  # 实际结算采购价，结算后有值

    order_no = Column(String(16), nullable=False, default="")  # 待结算单号
    status = Column(TINYINT, nullable=False, default=0)  # 状态 0-正常 1-已结算
    remarks = Column(String(256), nullable=False, default="")  # 备注


# 设置
class Config(MapBase):
    __tablename__ = "config"

    id = Column(Integer, ForeignKey(TransferStation.id), primary_key=True, nullable=False)

    allocation_printer_id = Column(Integer, nullable=False, default=0)  # 分车单打印机 ID
    allocation_print_copies = Column(TINYINT, nullable=False, default=1)  # 分车单打印份数
    settlement_printer_id = Column(Integer, nullable=False, default=0)  #  结算单打印机 ID
    settlement_receipt_types = Column(TINYINT, nullable=False, default=3)  # 结算单打印票据类型，位掩码方式保存 0-客户联 1-会计联
    purchase_type = Column(TINYINT, nullable=True, default=0)  # 采购方式 0-采购助手 1-后台录入
    shop_demand_amount_type = Column(TINYINT, nullable=True, default=0)  # 门店订货总量计算方式 0-所有订货 1-只计算正常订货的商品

    @staticmethod
    def get_by_station_id(session, station_id):
        config = session.query(Config) \
            .filter(Config.id == station_id) \
            .first()
        return config

    def set_settlement_receipt_types(self, print_accountant_receipt, print_customer_receipt):
        self.settlement_receipt_types = int(print_accountant_receipt) << 1 | int(print_customer_receipt) << 0

    def get_settlement_receipt_types(self):
        return {
            "print_accountant_receipt": bool(self.settlement_receipt_types & (1 << 1)),
            "print_customer_receipt": bool(self.settlement_receipt_types & (1 << 0)),
        }


# 其他费用
class Fee(MapBase, TimeBaseModel):
    __tablename__ = "fee"

    id = Column(Integer, primary_key=True, autoincrement=True)

    date = Column(Date, nullable=False, default=func.curdate())  # 费用发生日期
    type = Column(TINYINT, nullable=False, default=0)  # 费用类型 0-未知 1-运杂费 2-日常杂费
    money = Column(Integer, nullable=False, default=0)  # 金额
    remarks = Column(String(128), nullable=False, default="")  # 备注

    station_id = Column(Integer, ForeignKey(TransferStation.id), nullable=False)  # 中转站 ID
    station = relationship("TransferStation", foreign_keys="Fee.station_id")

    creator_id = Column(Integer, ForeignKey(AccountInfo.id), nullable=False)  # 操作人 ID
    creator = relationship("AccountInfo", foreign_keys="Fee.creator_id")


# 店铺配货价格表
class ShopPackingPrice(MapBase, TimeBaseModel):
    __tablename__ = "shop_packing_price"

    id = Column(Integer, primary_key=True, autoincrement=True)

    station_id = Column(Integer, ForeignKey(TransferStation.id), nullable=False)  # 中转站 ID
    station = relationship("TransferStation", foreign_keys="ShopPackingPrice.station_id")

    creator_id = Column(Integer, ForeignKey(AccountInfo.id), nullable=False)  # 操作人 ID
    creator = relationship("AccountInfo", foreign_keys="ShopPackingPrice.creator_id")

    wish_order_id = Column(Integer, ForeignKey(WishOrder.id), nullable=False)  # 意向单 ID
    wish_order = relationship("WishOrder", foreign_keys="ShopPackingPrice.wish_order_id")

    shop_id = Column(Integer, ForeignKey(Shop.id), nullable=False)  # 门店 ID
    shop = relationship("Shop", foreign_keys="ShopPackingPrice.shop_id")

    goods_id = Column(Integer, ForeignKey(Goods.id), nullable=False)  # 商品 ID
    goods = relationship("Goods", foreign_keys="ShopPackingPrice.goods_id")

    price = Column(Integer, nullable=False, default=0)  # 配货价
    allocated_amount = Column(Integer, nullable=False, default=0)  # 配货量


# 店铺其他支出
class ShopPayout(MapBase, TimeBaseModel):
    __tablename__ = "shop_payout"

    id = Column(Integer, primary_key=True, autoincrement=True)

    station_id = Column(Integer, ForeignKey(TransferStation.id), nullable=False)  # 中转站 ID
    station = relationship("TransferStation", foreign_keys="ShopPayout.station_id")

    creator_id = Column(Integer, ForeignKey(AccountInfo.id), nullable=False)  # 操作人 ID
    creator = relationship("AccountInfo", foreign_keys="ShopPayout.creator_id")

    shop_id = Column(Integer, ForeignKey(Shop.id), nullable=False)  # 门店 ID
    shop = relationship("Shop", foreign_keys="ShopPayout.shop_id")

    status = Column(TINYINT, nullable=False, default=0)  # 状态 0-正常 -1-已删除

    date = Column(Date, nullable=False, default=func.curdate())  # 支出日期
    type = Column(String(16), nullable=False, default="")  # 类型
    money = Column(Integer, nullable=False, default=0)  # 金额
    remarks = Column(String(128), nullable=False, default="")  # 备注

    @staticmethod
    def get_by_id(session, data_id, station_id=None):
        data = session.query(ShopPayout).filter(ShopPayout.id == data_id,
                                                ShopPayout.status == 0)
        if station_id:
            data = data.filter(ShopPayout.station_id == station_id)
        data = data.first()
        return data


# 外部订货单
class ExternalDemandOrder(MapBase, TimeBaseModel):
    __tablename__ = "external_demand_order"

    id = Column(Integer, primary_key=True, autoincrement=True)

    creator_id = Column(Integer, ForeignKey(AccountInfo.id), nullable=False)  # 操作人 ID
    creator = relationship("AccountInfo", foreign_keys="ExternalDemandOrder.creator_id")

    target = Column(TINYINT, nullable=False, default=0)  # 订货目标 0-未知 1-批发
    object_id = Column(Integer, nullable=False, default=0)  # 订货对象 ID
    object_name = Column(String(32), nullable=False, default="")  # 订货对象名称
    demand_date = Column(Date, nullable=False, default=func.curdate())  # 期望到货时间
    status = Column(TINYINT, nullable=False, default=0)  # 订货单状态 0-待确认 1-待配货 2-配货中 3-送货中 4-已完成

    goods_list = relationship("ExternalDemandOrderGoods", back_populates="order", lazy="dynamic")  # 意向单商品列表

    @staticmethod
    def get_by_id(session, data_id):
        data = session.query(ExternalDemandOrder) \
            .filter(ExternalDemandOrder.id == data_id) \
            .first()
        return data


# 外部订货单商品
class ExternalDemandOrderGoods(MapBase, TimeBaseModel):
    __tablename__ = "external_demand_order_goods"

    id = Column(Integer, primary_key=True, autoincrement=True)

    creator_id = Column(Integer, ForeignKey(AccountInfo.id), nullable=False)  # 操作人 ID
    creator = relationship("AccountInfo", foreign_keys="ExternalDemandOrderGoods.creator_id")

    order_id = Column(Integer, ForeignKey(ExternalDemandOrder.id), nullable=False)  # 订货单 ID
    order = relationship("ExternalDemandOrder", back_populates="goods_list")

    goods_name = Column(String(128), nullable=False, default="")  # 货品名
    demand_amount = Column(Integer, nullable=False, default=0)  # 订货量
    demand_unit = Column(Integer, nullable=False, default=0)  # 订货单位 0-斤 1-件 2-kg 3-个 4-份 5-盒 6-只 7-包
    remarks = Column(String(128), nullable=False, default="")  # 备注

    confirmed_amount = Column(Integer, nullable=False, default=0)  # 实配量
    confirmed_unit = Column(Integer, nullable=False, default=0)  # 实配单位
    price = Column(Integer, nullable=False, default=0)  # 单价
    total_money = Column(Integer, nullable=False, default=0)  # 小计

    syncronized = Column(TINYINT, nullable=False, default=0)  # 已同步过 0-否 1-是


# 新增商品时，根据length、width、weight字段计算商品的规格体积
@event.listens_for(Goods, "before_insert")
def add_goods_update_standards_volume(mapper, connection, target):
    standards_volume = check_float((target.length or 0) / 100) \
                       * check_float((target.width or 0) / 100) \
                       * check_float((target.height or 0) / 100)
    # 体积的存储单位是立方米
    target.standards_volume = standards_volume / 1000000


# 修改商品信息时，length、width、weight字段改变时更新商品的规格体积
@event.listens_for(Goods, "before_update")
def on_changed_goods_update_standards_volume(mapper, connection, target):
    standards_volume = check_float((target.length or 0) / 100) \
                       * check_float((target.width or 0) / 100) \
                       * check_float((target.height or 0) / 100)
    # 体积的存储单位是立方米
    target.standards_volume = standards_volume / 1000000


# 数据库set事件，name字段改变时更新首字母缩写
@event.listens_for(Firm.name, "set")
@event.listens_for(Goods.name, "set")
@event.listens_for(WishOrderGoods.goods_name, "set")
def on_changed_name_set_name_acronym(target, value, oldvalue, initiator):
    from pypinyin import slug, Style
    target.name_acronym = slug(
        value,
        style=Style.FIRST_LETTER,
        separator='',
        errors='ignore',
        strict=False
    )


# 新增商品或店铺时生成序列号
@event.listens_for(Goods, "before_insert")
@event.listens_for(Shop, "before_insert")
def generate_serial_number(mapper, connection, target):
    # 新增商品
    if isinstance(target, Goods):
        get_serial_number = "select max(serial_number) from {0}.`goods` where station_id={1}".format(DB_NAME, target.station_id)
        # 获取序列号
        result = connection.execute(get_serial_number)
        serial_number = (next(iter(result))[0] or 0) + 1
        target.serial_number = serial_number

    # 新增店铺
    if isinstance(target, Shop):
        get_serial_number = "select max(serial_number) from {0}.`shop` where station_id={1}".format(DB_NAME, target.station_id)
        # 获取序列号
        result = connection.execute(get_serial_number)
        serial_number = (next(iter(result))[0] or 0) + 1
        target.serial_number = serial_number


# 监听查询事件，查询accountinfo时，进行更新
@event.listens_for(Query, "before_compile")
def update_accountinfo(query):
    # 判断是否查询accountinfo表
    for c in query.column_descriptions:
        if c["entity"]==AccountInfo \
                and c["name"] in ("AccountInfo", "phone", "wx_unionid"):
            break
    else:
        return
    # 检查并设置更新间隔
    if redis.exists("auth_passport_update"):
        return
    redis.set("auth_passport_update", 1, AUTH_UPDATE_INTERVAL)
    # 更新操作
    from handlers.base.pub_func import AuthFunc
    from dal.db_configs import DBSession
    session = DBSession()
    AuthFunc.update_accountinfo(session)
    session.close()


# 数据库初始化
def init_db_data():
    MapBase.metadata.create_all()
    print("init db success")
    return True
