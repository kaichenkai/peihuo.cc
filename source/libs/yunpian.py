import requests
import json

#服务地址
sms_host = "sms.yunpian.com"
voice_host = "voice.yunpian.com"
#版本号
version = "v2"

#模板短信接口的URI
sms_tpl_send_uri = "/" + version + "/sms/tpl_single_send.json"

system_apikey = "41c25362696fcfec80028d870a744cf9"      # 系统短信通道
market_apikey = "3c66536dd3e27b7712794836aa3e7378"      # 营销短信通道


def tpl_send_sms(apikey, tpl_id, tpl_value, mobile):
    """
    模板接口发短信
    """
    params = {'apikey': apikey, 'tpl_id':tpl_id, 'tpl_value': tpl_value, 'mobile':mobile}
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    res = requests.post("http://" + sms_host+sms_tpl_send_uri,data=params)
    response_str = res.text
    response = json.loads(response_str)
    code = response.get('code',1)
    if code == 0:
        return True
    else:
        return response.get('detail','验证码发送失败，请稍后再试')


def send_yunpian_verify_code(mobile, code, use):
    """
    发送短信验证码

    【森果配货系统】您的验证码是#code#。此验证码用于#use#，5分钟内有效
    """
    tpl_id = 2617734
    tpl_value = "#code#={}&#use#={}".format(code, use)
    return tpl_send_sms(system_apikey, tpl_id, tpl_value, mobile)


def send_firm_settlement(phone, time, station_name, money):
    """
    供货商结算通知

    【森果配货系统】您于#time#在「#station_name#」结算货款#money#元，请及时确认
    """
    tpl_id = 2617736
    tpl_value = "#time#={}&#station_name#={}&#money#={}".format(time, station_name, money)
    return tpl_send_sms(system_apikey, tpl_id, tpl_value, phone)
