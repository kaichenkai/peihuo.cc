import json
import random
import urllib.request

import requests

from dal.db_configs import redis, pf_redis
from settings import *


# 所有需要微信授权调用的东西，模版消息等
class WxOauth2(object):
    client_access_token_url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential" \
                              "&appid={appid}&secret={appsecret}".format(appid=MP_APPID, appsecret=MP_APPSECRET)
    userinfo_url = "https://api.weixin.qq.com/sns/userinfo?access_token={access_token}&openid={openid}&lang=zh_CN"
    token_url = "https://api.weixin.qq.com/sns/oauth2/access_token?appid={appid}" \
                "&secret={appsecret}&code={code}&grant_type=authorization_code"

    # 微信接口调用所需要的 AccessToken，不需要用户授权
    @staticmethod
    def get_client_access_token():
        access_token = pf_redis.get('pf_access_token')
        if access_token:
            return access_token.decode('utf-8')

        data = json.loads(urllib.request.urlopen(WxOauth2.client_access_token_url).read().decode("utf-8"))
        if 'access_token' in data:
            access_token = data['access_token']
            pf_redis.set("pf_access_token", access_token, 3600)
            return access_token
        else:
            return None

    # 获取用户微信 OpenID
    # AccessToken 接口调用有次数上限，最好全局变量缓存
    # 这是需要用户授权才能获取的 AccessToken
    @staticmethod
    def get_access_token_openid(code, mode):
        # 需要改成异步请求
        token_url = WxOauth2.token_url.format(code=code, appid=MP_APPID, appsecret=MP_APPSECRET)
        # 获取 AccessToken
        try:
            data = json.loads(urllib.request.urlopen(token_url).read().decode("utf-8"))
        except Exception as e:
            print("[WxOauth2]get_access_token_openid: Oauth2 Error, get access token failed")
            return None
        if "access_token" not in data:
            return None
        return data["access_token"], data["openid"]

    # 获取用户微信资料（需用户授权）
    @staticmethod
    def get_userinfo(code, mode):
        data = WxOauth2.get_access_token_openid(code, mode)
        if not data:
            return None
        access_token, openid = data
        userinfo_url = WxOauth2.userinfo_url.format(access_token=access_token, openid=openid)
        try:
            data = json.loads(urllib.request.urlopen(userinfo_url).read().decode("utf-8"))
        except Exception as e:
            return None
        if "errcode" in data:
            return None
        return data


# 生成公众号带参数的二维码
class WxTicketUrl(object):
    @staticmethod
    def get_ticket_url(source="login"):
        """
            9 位留给用户登录
            8 位留给微信绑定
        """
        access_token = WxOauth2.get_client_access_token()
        if source == "login":
            scene_id = WxTicketUrl.make_scene_id_len9()
        elif source == "bind":
            scene_id = WxTicketUrl.make_scene_id_len8()
        else:
            return

        url = 'https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token={0}'.format(access_token)
        data = {"action_name": "QR_SCENE",
                "expire_seconds": 60 * 60,
                "action_info": {"scene": {"scene_id": scene_id}}}
        r = requests.post(url, data=json.dumps(data))
        result = json.loads(r.text)
        ticket_url = result.get('url', '')
        return ticket_url, scene_id

    # 生成随机 scene_id，用于扫码登录时识别用户
    @staticmethod
    def make_scene_id_len9():
        """9 位随机数"""
        while 1:
            scene_id = random.randint(100000000, 999999999)
            if not pf_redis.get('pf_scene_openid:%s' % scene_id):
                break
        return scene_id

    @staticmethod
    def make_scene_id_len8():
        """8 位随机数"""
        while 1:
            scene_id = random.randint(10000000, 99999999)
            if not pf_redis.get('pf_scene_openid:%s' % scene_id):
                break
        return scene_id
