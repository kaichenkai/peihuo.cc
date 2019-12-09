import calendar
import datetime
import hashlib
import json
import re
import time
import urllib.parse

import requests

from celerywork.prompt import send_frozen_account_dingtalk_msg, send_frozen_account_known_notify
from handlers.base.pub_log import log_msg_dict
from dal import models
from dal.db_configs import auth_redis, redis
# 时间
from settings import AUTH_HOST_NAME, AUTH_API_SECRETKEY


class TimeFunc():
    @classmethod
    def get_date_split(cls,choose_datetime):
        t_year = choose_datetime.year
        t_month = choose_datetime.month
        t_day = choose_datetime.day
        t_week = int(choose_datetime.strftime('%W'))
        return t_year,t_month,t_day,t_week

    @classmethod
    def get_date(cls,choose_datetime):
        return choose_datetime.strftime('%Y%m%d')

    @classmethod
    def get_time(cls,choose_datetime):
        return choose_datetime.strftime('%H:%M:%S')

    # 将时间类型换为时间字符串
    @classmethod
    def time_to_str(self, time, _type="all"):
        if _type == "all":
            fromat = "%Y-%m-%d %H:%M:%S"
        elif _type == "date":
            fromat = "%Y-%m-%d"
        elif _type == "hour":
            fromat = "%H:%M"
        elif _type == "month":
            fromat = "%m-%d"
        elif _type == "year":
            fromat = "%Y-%m"
        elif _type == "year_only":
            fromat = "%Y"
        elif _type == "full":
            fromat = "%Y%m%d%H%M"
        elif _type =="no_year":
            fromat = "%m-%d %H:%M:%S"
        elif _type =="time":
            fromat = "%H:%M:%S"
        else:
            fromat = "%Y-%m-%d %H:%M"
        try:
            time_res = time.strftime(fromat)
        except:
            time_res = ""
        return time_res

    #根据参数时间所在周的开始时间
    def getweekfirstday(current_date):
        yearnum=current_date.year
        weeknum=int(current_date.strftime("%W"))
        daynum=int(current_date.weekday())+1

        yearstart = datetime.datetime(yearnum,1,1)
        yearstartweekday = int(yearstart.weekday())+1
        if yearstartweekday < int (daynum):
            daydelat = (7-int(yearstartweekday))+(int(weeknum))*7
        else:
            daydelat = (7-int(yearstartweekday))+(int(weeknum)-1)*7
        a = yearstart+datetime.timedelta(days=daydelat+1)
        return a

    #获取当天的开始时间
    @classmethod
    def get_day_start_time(cls):
        now_time = datetime.datetime.now()
        start_time = datetime.datetime(now_time.year,now_time.month,now_time.day)
        return start_time

    #获取XX天的日期
    @classmethod
    def get_date_list(cls,date_range=7,date_type="day"):
        date_now=datetime.datetime.now()
        date_list = []
        current_month_first_day = 0
        for i in range(date_range):
            if date_type == "day":
                date = date_now-datetime.timedelta(days=i)
                date = date.date()
            else:
                date = cls.get_date_month(date_now,i)
            date_list.append(date)
        date_list.reverse()
        return date_list

    #获取XX月的月份
    @classmethod
    def get_date_month(cls,date,range_num):
        year = date.year
        month = date.month
        if month - range_num<= 0:
            res_month = 12+(month - range_num)
            res_year = year-1
        else:
            res_month = month-range_num
            res_year = year
        date = "%d-%d"%(res_year,res_month)
        return date

    #获取xx天的日期
    @classmethod
    def get_assign_date(cls,days=0):
        now_date = datetime.datetime.now()
        assign_date = datetime.datetime(now_date.year,now_date.month,now_date.day)-datetime.timedelta(days=days)
        return assign_date

    #拼接时间字符串
    @classmethod
    def splice_time(cls,year,month,day,time):
        time = "{year}-{month}-{day} {time}".format(year=year,month=month,day=day,time=cls.time_to_str(time,"time"))
        return time

    #获取今天的date类型
    @classmethod
    def get_today_date(cls):
        return datetime.date.today()

    # 获取今天的datetime类型
    @classmethod
    def get_today_datetime(cls):
        return datetime.datetime.combine(datetime.datetime.now(), datetime.time.min)

    # 获取两个日期之间的周数差，计算方式为 date2 - date1
    @staticmethod
    def week_difference(date1, date2):
        monday1 = (date1 - datetime.timedelta(date1.weekday()))
        monday2 = (date2 - datetime.timedelta(date2.weekday()))
        return (monday2 - monday1).days / 7

    # 获取两个日期之间的月数差，计算方式为 date2 - date1
    @staticmethod
    def month_difference(date1, date2):
        return (date2.year - date1.year) * 12 + date2.month - date1.month

    # 根据日历星期数获取周开始时间和结束时间
    @classmethod
    def get_week_by_weeknum(cls, year, weeknum, tzinfo=None):
        # 组装1月4日的日期
        day_jan_4th = datetime.date(year, 1, 4)
        # 今年第一个日历星期的开始日期
        first_week_start = day_jan_4th - datetime.timedelta(days=day_jan_4th.isoweekday()-1)
        # 所求星期的开始时间
        week_start = datetime.datetime.combine(
            first_week_start + datetime.timedelta(weeks=weeknum-1),
            datetime.time(),
        )
        week_end = week_start + datetime.timedelta(weeks=1)
        return week_start, week_end

    @staticmethod
    def add_months(source_date, months):
        month = source_date.month - 1 + months
        year = source_date.year + month // 12
        month = month % 12 + 1
        day = min(source_date.day, calendar.monthrange(year, month)[1])
        return datetime.date(year, month, day)


#字符
class CharFunc():
    # 检查是否包含汉字
    @classmethod
    def check_contain_chinese(cls,check_str):
        for ch in check_str:
            if '\u4e00' <= ch <= '\u9fff':
                return True
        return False

    #检查汉字字符个数
    @classmethod
    def get_contain_chinese_number(cls,check_str):
        number = 0
        for ch in check_str:
            if '\u4e00' <= ch <= '\u9fff' or ch=="：":
                number += 1
        return number


#数字
class NumFunc():
    @staticmethod
    def is_number(number):
        try:
            float(number)
            return True
        except:
            pass
        return False

    @staticmethod
    def is_int(number):
        try:
            int(number)
            return True
        except:
            pass
        return False

    # 处理金额小数位数（1.00处理为1; 1.10处理为1.1; 1.111处理为1.11; 非数字返回0）
    @staticmethod
    def check_float(number,place=2):
        try:
            num = round(float(number),place)
        except:
            num = 0
        if num == int(num):
            num = int(num)
        return num

    # 将数字处理为整数（非数字返回0）
    @staticmethod
    def check_int(number):
        try:
            num = int(number)
        except:
            num = 0
        return num

    # 将阿拉伯数字转为中文大写
    @classmethod
    def upcase_number(cls,n):
        units = ['', '万', '亿']
        nums = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
        decimal_label = ['角', '分']
        small_int_label = ['', '拾', '佰', '仟']
        int_part, decimal_part = str(int(n)), str(cls.check_float(n - int(n)))[2:]  # 分离整数和小数部分
        res = []
        if decimal_part:
            decimal_tmp = ''.join([nums[int(x)] + y for x, y in list(zip(decimal_part, decimal_label))])
            decimal_tmp=decimal_tmp.replace('零角', '零').replace('零分', '')
            res.append(decimal_tmp)

        if not decimal_part:
            res.append('整')

        if int_part != '0':
            res.append('圆')
            while int_part:
                small_int_part, int_part = int_part[-4:], int_part[:-4]
                tmp = ''.join([nums[int(x)] + (y if x != '0' else '') for x, y in list(zip(small_int_part[::-1], small_int_label))[::-1]])
                tmp = tmp.rstrip('零').replace('零零零', '零').replace('零零', '零')
                unit = units.pop(0)
                if tmp:
                    tmp += unit
                    res.append(tmp)
        if int_part == '0' and not decimal_part:
            res.append('零圆')
        return ''.join(res[::-1])

    # 按精度设置规则对金额进行处理
    # precision:精度设置 1:到分 2:到角 3:到元
    # precision_type:精度方式 1:四舍五入 2:抹掉尾数 3:进一法
    @classmethod
    def handle_precision(cls,in_money,precision,precision_type):
        in_money_cent = int(round(in_money*100))
        if precision==1:
            return in_money_cent
        else:
            # 整数部分
            int_part = cls.check_int(str(in_money_cent)[:-2])
            # 十分位
            tenths_digit_part = cls.check_int(str(in_money_cent)[-2:-1])
            # 百分位
            percentile_part = cls.check_int(str(in_money_cent)[-1:])
            if precision==2:
                # (四舍五入并且百分位大于等于5)或者(进一法并且百分位大于等于1)
                if (precision_type == 1 and percentile_part>=5) or (precision_type == 3 and percentile_part>=1):
                    return int_part*100+(tenths_digit_part+1)*10
                else:
                    return int_part*100+(tenths_digit_part)*10
            else:
                # (四舍五入并且十分位大于等于5)或者(进一法并且十分位大于等于1)
                if (precision_type == 1 and tenths_digit_part>=5) or (precision_type == 3 and tenths_digit_part>=1):
                    return (int_part+1)*100
                else:
                    return int_part*100


is_number = NumFunc.is_number
is_int = NumFunc.is_int
check_float = NumFunc.check_float
check_int = NumFunc.check_int


#转换数据格式
class DataFormatFunc():

    @classmethod
    def format_str_to_int_inlist(cls,data_list):
        res_list = []
        for data in data_list:
            try:
                data = int(data)
            except:
                continue
            res_list.append(data)
        return res_list

    @classmethod
    def format_int_to_str_inlist(cls,data_list):
        res_list = []
        for data in data_list:
            try:
                data = int(data)
            except:
                continue
            data = str(data)
            res_list.append(data)
        return res_list

    @classmethod
    def split_str(cls,string,symbol=","):
        return string.split(symbol)

    @classmethod
    def join_str(cls,string,symbol=","):
        return symbol.join(string)


#特殊字符
class Emoji():
    @classmethod
    def filter_emoji(cls,keyword):
        keyword=re.compile(u'[\U00010000-\U0010ffff]').sub(u'',keyword)
        return keyword

    @classmethod
    def check_emoji(cls,keyword):
        reg_emoji = re.compile(u'[\U00010000-\U0010ffff]')
        has_emoji = re.search(reg_emoji,keyword)
        if has_emoji:
            return True
        else:
            return False


#省份城市转换
class ProvinceCityFunc():
    @classmethod
    def city_to_province(cls, code):
        from dal.dis_dict import dis_dict
        province_code = int(code / 10000) * 10000
        if dis_dict.get(province_code, None):
            return province_code
        else:
            return None

    @classmethod
    def county_to_province(cls,code):
        from dal.dis_dict import dis_dict
        province_code = int(code/10000)*10000
        if dis_dict.get(province_code,None):
            return province_code
        else:
            return None

    @classmethod
    def get_city(cls,code):
        from dal.dis_dict import dis_dict
        try:
            if "city" in dis_dict[int(code/10000)*10000].keys():
                text = dis_dict[int(code/10000)*10000]["city"][code]["name"]
            else:
                text = ""
        except:
            text = ""
        return text

    @classmethod
    def get_province(cls,code):
        from dal.dis_dict import dis_dict
        try:
            text = dis_dict.get(int(code),{}).get("name",'')
        except:
            text = ""
        return text


# 域名缩短
class UrlShorten():
    code_map = (
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
        'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
        'q', 'r', 's', 't', 'u', 'v', 'w', 'x',
        'y', 'z', '0', '1', '2', '3', '4', '5',
        '6', '7', '8', '9', 'A', 'B', 'C', 'D',
        'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
        'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
        'U', 'V', 'W', 'X', 'Y', 'Z'
    )

    @classmethod
    def get_md5(self,longurl):
        longurl = longurl.encode('utf8') if isinstance(longurl,str) else longurl
        m = hashlib.md5()
        m.update(longurl)
        return m.hexdigest()

    @classmethod
    def get_hex(self,key):
        hkeys = []
        hex   =  self.get_md5(key)
        for i in range(0,1):
            n = int(hex[i*8:(i+1)*8],16)
            v = []
            e = 0
            for j in range(0,8):
                x = 0x0000003D & n
                e |= ((0x00000002 & n ) >> 1) << j
                v.insert(0,self.code_map[x])
                n = n >> 6
            e |= n << 5
            v.insert(0,self.code_map[e & 0x0000003D])
            hkeys.append("".join(v))
        return hkeys[0]

    @classmethod
    def get_short_url(self,long_url):
        url = self.session.query(models.ShortUrl).filter_by(long_url = long_url).first()
        if url:
            short_url = url.short_url
            self.session.commit()
            return short_url
        else:
            hkeys = []
            hex   =  self.get_md5(long_url)
            for i in range(0,1):
                n = int(hex[i*8:(i+1)*8],16)
                v = []
                e = 0
                for j in range(0,8):
                    x = 0x0000003D & n
                    e |= ((0x00000002 & n ) >> 1) << j
                    v.insert(0,self.code_map[x])
                    n = n >> 6
                e |= n << 5
                v.insert(0,self.code_map[e & 0x0000003D])
                hkeys.append("".join(v))
            url = models.ShortUrl(short_url = hkeys[0],long_url = long_url)
            self.session.add(url)
            self.session.commit()
            return hkeys[0]

    @classmethod
    def get_long_url(self,short_url):
        url = self.session.query(models.ShortUrl).filter_by(short_url = short_url).first()
        if not url:
            self.session.close()
            return False
        long_url = url.long_url
        self.session.commit()
        return long_url


#账户
class AccountFunc():

    #根据手机号获取账户
    @classmethod
    def get_account_by_phone(self,session,phone):
        AccountInfo = models.AccountInfo
        account = session.query(AccountInfo).filter_by(phone=phone).first()
        return account

    #根据id列表获取账户基本信息
    @classmethod
    def get_account_through_id_list(cls,session,account_id_list):
        if account_id_list:
            AccountInfo = models.AccountInfo
            account = session.query(AccountInfo)\
                            .filter(AccountInfo.id.in_(account_id_list))\
                            .all()
            account_dict = {x.id:x for x in account}
        else:
            account_dict = {}
        return account_dict

    #根据ID列表获取用户实际姓名
    @classmethod
    def get_account_name_through_id_list(cls,session,account_id_list):
        if account_id_list:
            AccountInfo = models.AccountInfo
            account = session.query(AccountInfo.id,AccountInfo.realname,AccountInfo.nickname)\
                            .filter(AccountInfo.id.in_(account_id_list))\
                            .all()
            account_dict = {x.id:x.realname or x.nickname for x in account}
        else:
            account_dict = {}
        return account_dict

    # 根据ID列表获取推荐人ID
    @classmethod
    def get_base_info_through_id_list(cls, session, account_id_list):
        if not account_id_list:
            return {}
        AccountInfo = models.AccountInfo
        accounts = session.query(AccountInfo.id,
                                AccountInfo.passport_id,
                                AccountInfo.realname,
                                AccountInfo.nickname) \
                        .filter(AccountInfo.id.in_(account_id_list)) \
                        .all()
        base_info_dict = {}
        for id_, passport_id, realname, nickname in accounts:
            data = dict(
                name=realname or nickname,
                passport_id=passport_id,
            )
            base_info_dict[id_] = data
        return base_info_dict

    #根据id获取账户
    @classmethod
    def get_account_through_id(cls,session,account_id):
        AccountInfo = models.AccountInfo
        account = session.query(AccountInfo).filter_by(id=account_id).first()
        return account

    # 根据 passport_id 获取账户
    @classmethod
    def get_account_through_passport_id(cls, session, passport_id):
        AccountInfo = models.AccountInfo
        account = session.query(AccountInfo) \
                        .filter_by(passport_id=passport_id) \
                        .one_or_none()
        return account

    #获取账户真实姓名
    @classmethod
    def get_account_realname(cls,session,account_id):
        AccountInfo = models.AccountInfo
        realname = session.query(AccountInfo.realname).filter_by(id=account_id).scalar() or ""
        return realname

    #获取账户手机号
    @classmethod
    def get_account_phone(cls,session,account_id):
        AccountInfo = models.AccountInfo
        phone = session.query(AccountInfo.phone).filter_by(id=account_id).scalar() or ""
        return phone

    @classmethod
    def get_account_info(cls,account):
        user_info= {}
        user_info["id"] = account.id
        user_info["passport_id"] = account.passport_id
        user_info["nickname"] = account.nickname or account.realname
        user_info["imgurl"] = account.head_imgurl_small or ""
        user_info["phone"] = account.phone or ""
        return user_info


# 账号统一
class AuthFunc:
    """用于简单接口鉴权"""
    @classmethod
    def _calc_token(cls, timestr):
        """token计算方式"""
        s = AUTH_API_SECRETKEY + timestr
        return hashlib.md5(s.encode("utf-8")).hexdigest()

    @classmethod
    def gen_token(cls):
        """生成token"""
        timestr = datetime.datetime.now().strftime("%Y%m%d%H")
        return cls._calc_token(timestr)

    @classmethod
    def verify_token(cls, token):
        """验证token"""
        # 上一小时的token在这一小时的前5分钟内仍然有效
        token_expire_delay = 5
        now = datetime.datetime.now()
        tokens = {now}
        if now.minute <= token_expire_delay:
            tokens.add(now - datetime.timedelta(hours=1))
        tokens = map(lambda x: x.strftime("%Y%m%d%H"), tokens)
        tokens = map(lambda x: cls._calc_token(x), tokens)
        return token in tokens

    @classmethod
    def get_passportinfo(cls, passport_id):
        """根据passport表id获取passport信息"""
        url = urllib.parse.urljoin(AUTH_HOST_NAME, "/passport/get")
        headers = {"Authorization": cls.gen_token()}
        resp = requests.post(url, json=dict(id=passport_id), headers=headers)
        if resp.status_code != 200:
            raise Exception(resp.text)
        return resp.json()["data"]

    @classmethod
    def update_passportinfo(cls, passport_id, type_, value):
        """更新passport表信息"""
        assert type_ in ("phone", "wx_unionid")
        url = urllib.parse.urljoin(AUTH_HOST_NAME, "/passport/update")
        data = dict(
            id=passport_id,
            type=type_,
            value=value,
        )
        headers = {"Authorization": cls.gen_token()}
        resp = requests.post(url, json=data, headers=headers)
        if resp.status_code != 200:
            raise Exception(resp.text)
        resp = resp.json()
        if not resp["success"]:
            return False, resp["error_text"]
        return True, ""

    @classmethod
    def verify_passportinfo(cls, type_, value, force_create=False):
        """验证passport信息"""
        assert type_ in ("phone", "wx_unionid")
        url = urllib.parse.urljoin(AUTH_HOST_NAME, "/passport/verify")
        data = dict(
            source="peihuo",
            type=type_,
            value=value,
            force_create=bool(force_create),
        )
        headers = {"Authorization": cls.gen_token()}
        resp = requests.post(url, json=data, headers=headers)
        if resp.status_code != 200:
            raise Exception(resp.text)
        resp = resp.json()
        return resp

    @classmethod
    def merge_passport(cls, session, passport_id, phone):
        url = urllib.parse.urljoin(AUTH_HOST_NAME, "/passport/merge")
        data = dict(
            passport_id=passport_id,
            phone=phone,
            source="peihuo",
        )
        headers = {"Authorization": cls.gen_token()}
        resp = requests.post(url, json=data, headers=headers)
        if resp.status_code != 200:
            raise Exception(resp.text)
        resp = resp.json()
        if not resp["success"]:
            errmsg = resp["error_text"]
            if errmsg == "NOT EXIST":
                return False, "请先使用微信登录"
            elif errmsg == "USE UPDATE":
                return False, "USE UPDATE"
            elif errmsg == "SAME PASSPORT":
                return False, "您已绑定该手机号"
            elif errmsg == "CANT MERGE 3":
                return False, "该手机号已绑定其他微信"
            elif errmsg == "CANT MERGE 4":
                return False, "该手机号已被冻结，请更换手机号"
            elif errmsg == "CANT MERGE 5":
                return False, "请使用微信扫码登录"
            elif errmsg == "CANT MERGE 6":
                return False, "您已绑定手机号，请前往个人中心进行修改"
            else:
                return False, "绑定失败，请联系森果客服 400-027-0135"

        source_passport_id = resp["source_passport_id"]
        target_passport_id = resp["target_passport_id"]

        merge_key = "passport_merge:{}|{}:ph".format(source_passport_id, target_passport_id)
        if auth_redis.exists(merge_key):
            if auth_redis.get(merge_key) == 2:
                return True, ""
            auth_redis.set(merge_key, 2)
            cls.update_single_accountinfo(
                source_passport_id,
                cls.get_passportinfo(source_passport_id),
                session,
            )
            cls.update_single_accountinfo(
                target_passport_id,
                cls.get_passportinfo(target_passport_id),
                session,
            )
            auth_redis.delete(merge_key)
        return True, ""

    @classmethod
    def update_single_accountinfo(cls, passport_id, data, session, force_create=False):
        """更新当前系统的accountinfo表的单条记录"""
        AccountInfo = models.AccountInfo

        user = session.query(AccountInfo) \
                        .filter_by(passport_id=passport_id) \
                        .first()
        if not user:
            if force_create:
                user = AccountInfo(passport_id=passport_id)
                session.add(user)
                session.flush()
            else:
                return None
        else:
            user = session.query(AccountInfo) \
                        .filter_by(id=user.id) \
                        .with_lockmode("update") \
                        .first()

        for k, v in data.items():
            if hasattr(user, k) and k in ("phone", "wx_unionid"):
                setattr(user, k, v)
        session.commit()
        return user

    @classmethod
    def update_accountinfo(cls, session):
        """根据redis更新accountinfo"""
        cls.update_merge_accountinfo(session)

        keystr = "passport_update:{}:ph"
        keys = auth_redis.keys(keystr.format("*"))
        keys = {int(i.decode().split(":")[1]) for i in keys}

        for i in keys:
            this_key = keystr.format(i)
            status = int(auth_redis.get(this_key) or 0)
            # 值为2表示正在处理中，跳过
            if status==2:
                continue
            # 开始处理时设置值为2
            auth_redis.set(this_key, 2)
            data = cls.get_passportinfo(i)
            cls.update_single_accountinfo(i, data, session)
            # 处理完成后删除
            auth_redis.delete(this_key)

    @classmethod
    def update_merge_accountinfo(cls, session):
        keystr = "passport_merge:{}|{}:ph"
        keys = auth_redis.keys(keystr.format("*", "*"))
        keys = {i.decode().split(":")[1] for i in keys}

        for i in keys:
            source, target = map(int, i.split("|"))
            this_key = keystr.format(source, target)
            status = int(auth_redis.get(this_key) or "2")
            if status == 2:
                continue
            auth_redis.set(this_key, 2)
            cls.update_single_accountinfo(
                source,
                cls.get_passportinfo(source),
                session,
            )
            cls.update_single_accountinfo(
                target,
                cls.get_passportinfo(target),
                session,
            )
            auth_redis.delete(this_key)

    @classmethod
    def login_by_wx(cls, session, wx_userinfo):
        """微信登录"""
        wx_unionid = wx_userinfo["unionid"]
        resp = cls.verify_passportinfo("wx_unionid", wx_unionid, force_create=True)
        # 错误处理
        if not resp["success"]:
            errmsg = resp["error_text"]
            if errmsg == "LOCKED":
                return False, "该账户已被冻结，请联系森果客服 400-027-0135"
            else:
                return False, "无法登录，请联系森果客服 400-027-0135"

        data = resp["data"]
        user = session.query(models.AccountInfo).filter_by(passport_id=data["id"]).first()
        if not user:
            passport_id = data.pop("id")
            user = cls.update_single_accountinfo(passport_id, data, session, force_create=True)
        return True, user

    @classmethod
    def login_by_phone_password(cls, session, phone, password):
        """手机号+密码 登录"""
        resp = cls.verify_passportinfo("phone", phone)
        # 错误处理
        if not resp["success"]:
            errmsg = resp["error_text"]
            if errmsg == "LOCKED":
                cls.prompt_frozen_account(phone)
                return False, "该账户已被冻结，请联系森果客服 400-027-0135"
            else:
                return False, "用户名或密码错误"
        data = resp["data"]
        user = session.query(models.AccountInfo).filter_by(passport_id=data["id"]).first()
        if not user:
            passport_id = data.pop("id")
            user = cls.update_single_accountinfo(passport_id, data, session, force_create=True)
        if user.password != password or user.password is None:
            return False, "用户名或密码错误"
        return True, user

    @classmethod
    def login_by_phone_code(cls, session, phone):
        """手机号登录"""
        resp = cls.verify_passportinfo("phone", phone, force_create=True)
        # 错误处理
        if not resp["success"]:
            errmsg = resp["error_text"]
            if errmsg == "LOCKED":
                cls.prompt_frozen_account(phone)
                return False, "该账户已被冻结，请联系森果客服 400-027-0135"
            elif errmsg == "NOT EXIST":
                return False, "您还不是系统用户"
            else:
                return False, "登录失败，请联系森果客服 400-027-0135"
        data = resp["data"]
        user = session.query(models.AccountInfo).filter_by(passport_id=data["id"]).first()
        if not user:
            passport_id = data.pop("id")
            user = cls.update_single_accountinfo(passport_id, data, session, force_create=True)
        return True, user

    @classmethod
    def update_through_wx(cls, session, wx_userinfo, account, action="update"):
        """通过微信更新用户资料"""
        headimgurl = wx_userinfo.get("headimgurl", None)
        if headimgurl:
            headimgurl = headimgurl.replace("http://", "https://")
        if action == "bind":
            account.wx_unionid = wx_userinfo.get("unionid", None)
        if action in ["bind", "update_all"]:
            # now_openid = account.wx_openid or ""
            # if not now_openid.startswith("oA") \
            #         and wx_userinfo.get("openid", "").startswith("oA"):
            account.wx_openid = wx_userinfo.get("openid", None)
        account.wx_country = wx_userinfo.get("country", None)
        account.wx_province = wx_userinfo.get("province", None)
        account.wx_city = wx_userinfo.get("city", None)
        account.sex = wx_userinfo.get("sex", None)
        account.headimgurl = headimgurl
        account.nickname = wx_userinfo.get("nickname", None)
        session.add(account)
        session.commit()

    @classmethod
    def prompt_frozen_account(cls, phone):
        redis_key = "frozen_account:{}".format(phone)
        if redis.exists(redis_key):
            return
        redis.set(redis_key, 1, 3*24*3600)
        send_frozen_account_dingtalk_msg.delay(phone)
        send_frozen_account_known_notify.delay(phone)


# 无线打印
class WirelessPrintFunc():
    def __init__(self, print_type, _paper_width=32):
        # 打印机类型
        print_type_dict = {1: "ylyprint", 2: "feprint", 3: "sgprint", 4: "80localprint"}
        self._type = print_type_dict.get(print_type, "sgprint")
        paper_width_dict = {1: 32, 2: 48, 3: 48, 4: 48}
        _paper_width = paper_width_dict.get(print_type, 32)

        # 纸宽
        self._paper_width = _paper_width

        # 会计联/客户联的间距
        customer_space_dict = {
            1: (_paper_width - 16) * " ",
            2: (_paper_width - 16) * " ",
            3: (_paper_width - 16) * " ",
            4: (_paper_width - 16) * " "
        }
        accountant_space_dict = {
            1: (_paper_width - 8) * " ",
            2: (_paper_width - 8) * " ",
            3: (_paper_width - 8) * " ",
            4: (_paper_width - 8) * " "
        }
        _customer_space = customer_space_dict.get(print_type, (_paper_width - 16) * " ")
        _accountant_space = accountant_space_dict.get(print_type, (_paper_width - 8) * " ")
        self.customer_space = _customer_space
        self.accountant_space = _accountant_space

        # 打印机默认字号
        if self._type in ["feprint", "sgprint"]:
            self.default_size = 0
        else:
            self.default_size = 1

        # 底部技术支持文字
        self.support_text = "技术支持：森果  服务热线：400-027-0135"

    def line_break(self, str_data):
        """换行"""
        _type = self._type
        if _type == "ylyprint":
            return "{}\r\n".format(str_data)
        elif _type == "feprint":
            return "{}<BR>".format(str_data)
        elif _type == "sgprint":
            return "{}\n".format(str_data)
        elif _type == "80localprint":
            if not str_data:
                return "</br>"
            if not re.search('<p', str_data):
                return "<p style='display:block;'>{}</p>".format(str_data)
            _, num = re.search('style=', str_data).span()
            str_data = "<p style='display:block;"+str_data[num+1:]
            return str_data

    def bottom_line_break(self):
        """横线"""
        _type = self._type
        if _type == "ylyprint":
            return "--------------------------------\r\n"
        elif _type == "feprint":
            return "------------------------------------------------<BR>"
        elif _type == "sgprint":
            return "------------------------------------------------\n"
        elif _type == "80localprint":
            return "<p style='overflow:hidden;width:100%;height: 20px;'>------------------------------------------------------------</p>"

    def float_middle(self, str_data, bytes_len=0):
        """居中"""
        _type = self._type
        _paper_width = self._paper_width
        if _type == "ylyprint":
            # 32字节
            left_len = (_paper_width - bytes_len) // 2
            right_len = (_paper_width - left_len - bytes_len)
            return left_len * ' ' + str_data + right_len * ' '
        elif _type == "feprint":
            return "<C>{}</C>".format(str_data)
        elif _type == "sgprint":
            return "<C>{}</C>".format(str_data)
        elif _type == "80localprint":
            if not re.search('<p', str_data):
                return "<p style='text-align:center;'>{}</p>".format(str_data)
            _, num = re.search('style=', str_data).span()
            str_data = "<p style='text-align:center;"+str_data[num+1:]
            return str_data

    def float_left(self, str_data, bytes_len=0):
        """居左"""
        _type = self._type
        _paper_width = self._paper_width
        if _type == "ylyprint":
            # 32字节
            left_len = 0
            right_len = (_paper_width - left_len - bytes_len)
            return left_len * ' ' + str_data + right_len * ' '
        elif _type == "feprint":
            return "<L>{}</L>".format(str_data)
        elif _type == "sgprint":
            return "<L>{}</L>".format(str_data)
        elif _type == "80localprint":
            if not re.search('<p', str_data):
                return "<p style='text-align:left;'>{}</p>".format(str_data)
            _, num = re.search('style=', str_data).span()
            str_data = "<p style='text-align:left;"+str_data[num+1:]
            return str_data

    def float_right(self, str_data, bytes_len=0):
        """右对齐"""
        _type = self._type
        _paper_width = self._paper_width
        if _type == "ylyprint":
            # 32个字节
            return (_paper_width - bytes_len) * ' ' + str_data
        elif _type == "feprint":
            return "<RIGHT>{}</RIGHT>".format(str_data)
        elif _type == "sgprint":
            return "<R>{}</R>".format(str_data)
        elif _type == "80localprint":
            if not re.search('<p', str_data):
                return "<p style='text-align:right;'>{}</p>".format(str_data)
            _, num = re.search('style=', str_data).span()
            str_data = "<p style='text-align:right;"+str_data[num+1:]
            return str_data

    def zoom_in(self, str_data, zoom_type=2):
        """字号缩放

        zoom_type:缩放类型:0.不缩放,1.宽度放大,2.高度放大,3.宽度和高度都放大
        """
        _type = self._type
        if _type == "ylyprint":
            return "@@2" + str_data
        elif _type == "feprint":
            if zoom_type == 1:
                return "<W>{}</W>".format(str_data)
            elif zoom_type == 2:
                return "<B>{}</B>".format(str_data)
            elif zoom_type == 3:
                return "<DB>{}</DB>".format(str_data)
            else:
                return str_data
        elif _type == "sgprint":
            if zoom_type == 1:
                return "<FS1>{}</FS1>".format(str_data)
            elif zoom_type == 2:
                return "<FS2>{}</FS2>".format(str_data)
            elif zoom_type == 3:
                return "<FS3>{}</FS3>".format(str_data)
            else:
                return str_data
        elif _type == "80localprint":
            if zoom_type == 1:
                return "<p style='font-size:8pt;'>{}</p>".format(str_data)
            elif zoom_type == 2:
                return "<p style='font-size:16pt;'>{}</p>".format(str_data)
            elif zoom_type == 3:
                return "<p style='font-size:24pt;'>{}</p>".format(str_data)
            else:
                return str_data

    def barcode(self, str_data, type=None, index=None):
        """条码"""
        _type = self._type
        if _type == "ylyprint":
            return "<b>{}</b>".format(str_data)
        elif _type == "feprint":
            length = len(str_data)
            b = [27, 100, 2, 29, 72, 50, 29, 104, 80, 29, 119, 2, 29, 107]
            b[5] = 48  # 48隐藏下方的号码,49展示上方的号码,50展示下方的号码
            b[8] = 120  # 调节条码高度,0x50~0x64,没有给固定的，应该想多少都差不多
            b.append(73)  # code128
            b.append(length + 2)
            b.append(123)
            b.append(66)
            i = 0
            while i < length:
                b.append(ord(str_data[i]))
                i += 1
            strcode = ''.join([chr(c) for c in b])
            return strcode
        elif _type == 'sgprint':
            return "\n<BR>{}</BR>".format(str_data)
        elif _type == "80localprint":
            return "<div id='order_{0}_barcode_{1}' style='font-size:16pt;text-align:center;margin:2px auto;'>{2}</div>".format(type, index, str_data)

    def fill_box(self, content, box_len, content_len=0, float_dir='right'):
        """指定字符串和盒子长度，以及对齐方式和字符串长度

        left:文字左对齐填充空格
        right:文字右对齐填充空格
        """
        if not content_len:
            content_len = len(content)
        if content_len >= box_len:
            return content
        else:
            left_len = 0
            right_len = 0
            if float_dir == 'right':
                left_len = box_len - content_len
            elif float_dir == 'left':
                right_len = box_len - content_len
            else:
                left_len = (box_len - content_len) // 2
                right_len = box_len - content_len - left_len
            return ' ' * left_len + content + ' ' * right_len

    def fill_box_to_float_right(self, left_content, box_len, right_content):
        """指定左边字符串和盒子长度，以及右边字符串长度　使得右边字符串靠右
        """
        left_len = len(left_content) + \
                   CharFunc.get_contain_chinese_number(left_content)
        right_len = len(right_content) + \
                    CharFunc.get_contain_chinese_number(right_content)
        if left_len % box_len + right_len <= box_len:
            # 同行
            space_count = box_len - (left_len % box_len + right_len)
        else:
            # 只能两行
            space_count = box_len * 2 - (left_len % box_len + right_len)
        if self._type == "80localprint":
            return "<p><span style='display:inline-block;width:75%;'>{}</span><span style='display:inline-block;width:25%;text-align:right;vertical-align:top;'>{}</span></p>".format(left_content, right_content)
        return left_content + ' ' * space_count + right_content

    def cut(self):
        """切刀"""
        _type = self._type
        if _type == "ylyprint":
            return 32 * "-"
        elif _type == "feprint":
            return self.line_break('') * 3 + "<CUT>"
        elif _type == "sgprint":
            return "<CUT>"
        else:
            return ""

    def qrcode(self, str_data):
        """二维码"""
        _type = self._type
        if _type == "ylyprint":
            return "<q>{}</q>".format(str_data)
        elif _type == "feprint":
            return "<QR>{}</QR>".format(str_data)
        elif _type == "sgprint":
            return "<QR>{}</QR>".format(str_data)
        else:
            return str_data

    def bold(self, str_data):
        """加粗"""
        _type = self._type
        if _type == "ylyprint":
            return str_data
        elif _type == "feprint":
            return "<BOLD>{}</BOLD>".format(str_data)
        elif _type == "sgprint":
            return "<FB>{}</FB>".format(str_data)
        elif _type == "80localprint":
            if not re.search('<p', str_data):
                return "<p style='font-weight:bold;'>{}</p>".format(str_data)
            _, num = re.search('style=', str_data).span()
            str_data = "<p style='font-weight:bold;"+str_data[num+1:]
            return str_data
        else:
            return str_data

    def img(self, img_base64):
        """图片"""
        _type = self._type
        if _type == "feprint":
            return "<LOGO>"
        elif _type == "sgprint":
            return "<IMG>{}</IMG>".format(img_base64)
        elif _type == "80localprint":
            return "<img src='{}' style=''>".format(img_base64)
        else:
            return img_base64

    def signature(self, img_base64):
        """签名"""
        _type = self._type
        if _type == "feprint":
            return "<LOGO>"
        elif _type == "sgprint":
            return "<SIG>{}</SIG>".format(img_base64)
        elif _type == "80localprint":
            return "<img src='{}' style=''>".format(img_base64)
        else:
            return img_base64

    def color_invert(self, str_data, cancel=False):
        """黑白反显

        为了不影响下一个字符串，在反显前后各加了一个取消
        """
        if self._type == "smposprint":
            return "::{}".format(str_data)
        elif self._type == "80localprint":
            if not re.search('<p', str_data):
                return "<p style='background-color:#000;-webkit-print-color-adjust: exact;color:#fff;'>{}</p>".format(str_data)
            _, num = re.search('style=', str_data).span()
            str_data = "<p style='background-color:#000;-webkit-print-color-adjust: exact;color:#fff;"+str_data[num+1:]
            return str_data
        else:
            length = len(str_data)
            b = [29, 66, 2]
            b += [29, 66, 1]
            i = 0
            while i < length:
                b.append(ord(str_data[i]))
                i += 1
            b += [29, 66, 2]
            str_data = ''.join([chr(c) for c in b])
            return str_data

    def inline_block(self,str_data):
        if not re.search('<p', str_data):
            return "<p style='display:inline-block;min-width: 40%;box-sizing:border-box;'>{}</p>".format(str_data)
        _, num = re.search('style=', str_data).span()
        str_data = "<p style='display:inline-block;min-width: 40%;box-sizing:border-box;" + str_data[num + 1:]
        return str_data

    def _ylyprint(self, content_body, machine_code, mkey):
        """易连云无线打印

        content_body:打印内容
        machine_code:打印机终端号
        mkey:打印机密钥
        """
        partner = '1693'  # 用户ID
        apikey = '664466347d04d1089a3d373ac3b6d985af65d78e'  # API密钥
        timenow = str(int(time.time()))  # 当前时间戳
        if machine_code and mkey:
            sign = apikey + 'machine_code' + machine_code + \
                   'partner' + partner + 'time' + timenow + mkey  # 生成的签名加密
            sign = hashlib.md5(sign.encode("utf-8")).hexdigest().upper()
        else:
            return False, "易联云打印失败，请检查打印机终端号是否正确设置"
        data = {
            "partner": partner,
            "machine_code": machine_code,
            "content": content_body,
            "time": timenow,
            "sign": sign}
        r = requests.post("http://open.10ss.net:8888", data=data)
        try:
            text = int(eval(r.text)["state"])
        except BaseException:
            return False, "易联云打印接口返回异常，请稍后重试"
        if text == 1:
            return True, ""
        elif text in [3, 4]:
            return False, "易联云打印失败，请在店铺设置中检查打印机终端号是否正确设置"
        else:
            return False, "易联云打印失败，错误代码：%d" % text

    def _feprint(self, content_body, machine_code):
        """飞鹅云无线打印

        content_body:打印内容
        machine_code:打印机终端号
        """
        URL = "http://api.feieyun.cn/Api/Open/"  # 不需要修改
        USER = "senguo@senguo.cc"
        UKEY = "WAhPxdfWIgLd3FYW"
        STIME = str(int(time.time()))
        signature = hashlib.sha1(
            (USER + UKEY + STIME).encode("utf-8")).hexdigest()
        data = {
            'user': USER,
            'sig': signature,
            'stime': STIME,
            'apiname': 'Open_printMsg',  # 固定值,不需要修改
            'sn': machine_code,
            'content': content_body,
            'times': '1'  # 打印联数
        }
        response = requests.post(URL, data=data, timeout=30)
        code = response.status_code  # 响应状态码
        if code == 200:
            ret_dict = json.loads(response.text)
            log_date = datetime.datetime.now().strftime('%Y%m%d')
            if ret_dict["ret"] != 0:
                log_msg_dict('fe_ret_error/%s' % log_date, ret_dict, False)
                return False, "FE云打印出错，接口返回--" + ret_dict["msg"]
            return True, ""
        else:
            return False, "FE云打印服务器出错，请联系森果客服人员"

    def _sgprint(self, content_body, machine_code):
        """森果云无线打印

        content_body:打印内容
        machine_code:打印机终端号
        """
        import base64
        from libs.aliyun_IoT import IoTClient, PubRequest
        from libs.escpos.parser import Parser
        # 附加单据号防止重复打印
        receipt_number = "<N>" + str(int(time.time() * 1000)) + "</N>"
        content_body = receipt_number + content_body + "<CUT>"
        content = base64.b64encode(Parser.parse(content_body)).decode()
        request = PubRequest.PubRequest()
        request.set_accept_format('json')
        request.set_ProductKey('9t2pDhYz0IS')
        request.set_TopicFullName('/9t2pDhYz0IS/%s/data' % machine_code)
        request.set_MessageContent(content)
        request.set_Qos(1)
        r = IoTClient.do_action_with_exception(request)

        return True, ""

    def sgbluetooth(self, content_body):
        import base64
        from libs.escpos.parser import Parser
        content = base64.b64encode(
            Parser.parse(
                content_body +
                "<CUT>")).decode()
        return content

    @classmethod
    def _fequery(cls, machine_code):
        """飞鹅云无线打印查询

        machine_code:打印机终端号
        """
        URL = "http://api.feieyun.cn/Api/Open/"  # 不需要修改
        USER = "senguo@senguo.cc"
        UKEY = "WAhPxdfWIgLd3FYW"
        STIME = str(int(time.time()))
        signature = hashlib.sha1(
            (USER + UKEY + STIME).encode("utf-8")).hexdigest()
        data = {
            'user': USER,
            'sig': signature,
            'stime': STIME,
            'apiname': 'Open_queryPrinterStatus',  # 固定值,不需要修改
            'sn': machine_code
        }
        response = requests.post(URL, data=data, timeout=30)
        code = response.status_code  # 响应状态码
        if code == 200:
            ret_dict = json.loads(response.text)
            if ret_dict["ret"] != 0:
                err_txt = ret_dict["data"] if ret_dict["data"] else ret_dict["msg"]
                return False, "FE打印机状态有误,接口返回--" + err_txt
            return True, ""
        else:
            return False, "FE云打印服务器出错,请联系森果客服人员"

    @classmethod
    def _feadd(cls, machine_code, mkey):
        """飞鹅云无线打印机添加

        machine_code:打印机终端号
        """
        URL = "http://api.feieyun.cn/Api/Open/"  # 不需要修改
        USER = "senguo@senguo.cc"
        UKEY = "WAhPxdfWIgLd3FYW"
        STIME = str(int(time.time()))
        signature = hashlib.sha1(
            (USER + UKEY + STIME).encode("utf-8")).hexdigest()
        params = {
            'user': USER,
            'sig': signature,
            'stime': STIME,
            'apiname': 'Open_printerAddlist',  # 固定值,不需要修改
            'printerContent': "%s#%s# # " % (machine_code, mkey)
        }
        response = requests.post(URL, data=params, timeout=30)
        code = response.status_code  # 响应状态码
        if code == 200:
            ret_dict = json.loads(response.text)
            if ret_dict["ret"] != 0:
                err_txt = ret_dict["data"] if ret_dict["data"] else ret_dict["msg"]
                return False, "FE打印机状态有误,接口返回--" + err_txt
            else:
                bind_ok = ret_dict["data"]["ok"]
                if bind_ok:
                    return True, ""
                else:
                    bind_no = ret_dict["data"]["no"][0]
                    if bind_no.find("错误：已被添加过") == -1:
                        return False, bind_no
                    else:
                        return True, ""
        else:
            return False, "FE云打印服务器出错,请联系森果客服人员"

    def send_print_request(
            self,
            content_body,
            wireless_print_num,
            wireless_print_key=""):
        """向各个打印平台发送打印请求
        """
        print_type = self._type
        if print_type == "ylyprint":
            if_print_success, error_txt = self._ylyprint(
                content_body, wireless_print_num, wireless_print_key)
        elif print_type == "feprint":
            if_print_success, error_txt = self._feprint(
                content_body, wireless_print_num)
        else:
            if_print_success, error_txt = self._sgprint(
                content_body, wireless_print_num)
        return if_print_success, error_txt

    def format_str_position_size(
            self,
            text,
            position,
            size,
            newline,
            last_newline=1):
        """格式化字符串大小及位置

        text:字符串内容
        position:对齐方式
        size:字号
        newline:是否换行
        last_newline:上一行文字是否换行
        action:条目名称
        """
        float_middle = self.float_middle
        float_right = self.float_right
        zoom_in = self.zoom_in
        line_break = self.line_break
        _type = self._type
        default_size = self.default_size
        fill_box = self.fill_box
        size = NumFunc.check_int(size)
        newline = NumFunc.check_int(newline)
        origin_text = text
        if size == 2:
            text = zoom_in(text, 2)
        elif size == 3:
            text = zoom_in(text, 3)
        else:
            text = zoom_in(text, default_size)
        if newline:
            if last_newline:
                if position == "center":
                    text = float_middle(text)
                elif position == "right":
                    text = float_right(text)
                else:
                    text = line_break(text)
            else:
                if _type == '80localprint':
                    text = self.inline_block(text)
                else:
                    text = line_break(text)
        else:
            if _type in ["feprint", "sgprint"]:
                if size == 1:
                    content_len = len(origin_text)
                else:
                    # 遇到不换行的保留一个最小长度以维持格式对齐
                    content_len = (
                                          len(origin_text) + CharFunc.get_contain_chinese_number(origin_text)) * 2
                text = fill_box(text, 20, content_len, float_dir="left")
            elif _type == '80localprint':
                text = self.inline_block(text)
            else:
                text += "  "
        return text

