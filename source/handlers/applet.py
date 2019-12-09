import random
import string
import time
import datetime
import codecs
import base64
import json
try:
    from Crypto.Cipher import AES
except:
    pass

import tornado.web
import tornado.escape

codecs.register(lambda name: codecs.lookup('utf8') if name == 'utf8mb4' else None)


class GetSessionKey(object):
    def __init__(self,appid,appsecret,code):
        self.appid = appid
        self.appsecret = appsecret
        self.code = code

    def get_session_key(self):
        '''
            获取session_key
            code:用户登录凭证，由前端调起登录函数从而获取获取微信返回的code传入后台
            appid:小程序appid
            appsecret:小程序appsecret

        '''
        appid = self.appid
        appsecret = self.appsecret
        code = self.code
        userinfo_data = {}
        try:
            import requests
            session_key_url = "https://api.weixin.qq.com/sns/jscode2session?appid=%s&secret=%s&js_code=%s&grant_type=authorization_code"%(appid,appsecret,code)
            data = json.loads(requests.get(session_key_url).content.decode('utf-8'))
            if data.get("errcode",None):
                openid  = ""
                session_key = ""
                errmsg = data.get("errmsg","")
            else:
                openid  = data['openid']
                session_key = data['session_key']
                errmsg = ""
        except:
            openid  = ""
            session_key = ""
            errmsg = ""
        userinfo_data["openid"] = openid
        userinfo_data["session_key"] = session_key
        userinfo_data["errmsg"] = errmsg
        return userinfo_data


# 微信消息解密
class WXBizDataCrypt(object):
    def __init__(self, appId, sessionKey):
        self.appId = appId
        self.sessionKey = sessionKey

    def decryptData(self, encryptedData, iv):
        # base64 decode
        sessionKey = base64.b64decode(self.sessionKey)
        encryptedData = base64.b64decode(encryptedData)
        iv = base64.b64decode(iv)

        cipher = AES.new(sessionKey, AES.MODE_CBC, iv)

        decrypted = json.loads(self._unpad(cipher.decrypt(encryptedData).decode("utf-8")))

        if decrypted['watermark']['appid'] != self.appId:
            raise Exception('Invalid Buffer')

        return decrypted

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]


class CreateToken(object):
    def __init__(self,openid,session_key):
        self.openid = openid
        self.session_key = session_key

    def token(self):
        nonceStr = self.create_nonce_str()
        timestamp = self.create_timestamp()

    # 随机字符串
    def create_nonce_str(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

    # 时间戳
    def create_timestamp(self):
        return int(time.time())


class CreateSignature(object):
    def __init__(self,rawData,sessionKey):
        self.rawData = rawData
        self.sessionKey = sessionKey

    def get_signature(self):
        import hashlib
        sha1 = hashlib.sha1()
        sha_str = self.rawData+self.sessionKey
        sha_str = sha_str.encode("utf-8")
        sha1.update(sha_str)
        signature = sha1.hexdigest()
        return signature



class ResolveData(object):

    def resolve(self,args):

        code = args["code"].strip()
        userInfo = args["userInfo"]
        rawData = args["rawData"].strip()
        signature = args["signature"].strip()
        encryptedData = args["encryptedData"].strip()
        iv = args["iv"]
        keys_list = ("code","userInfo","rawData","signature","encryptedData","iv")
        if any(args.get(key,"") in ("",[],"[]")for key in keys_list):
            return False,"请填写完整参数"

        if not userInfo:
            return False,"未获取到用户信息"

        from settings import PURCHASE_APPLET_APPID, PURCHASE_APPLET_APPSECRET, DEMAND_APPLET_APPID, DEMAND_APPLET_APPSECRET

        # 获取openid及session_key
        source = args.get("source")
        if source == "purchase":
            session_key_info = GetSessionKey(PURCHASE_APPLET_APPID, PURCHASE_APPLET_APPSECRET, code).get_session_key()
        elif source == "demand":
            session_key_info = GetSessionKey(DEMAND_APPLET_APPID, DEMAND_APPLET_APPSECRET, code).get_session_key()
        else:
            session_key_info = GetSessionKey(PURCHASE_APPLET_APPID, PURCHASE_APPLET_APPSECRET, code).get_session_key()

        if session_key_info["errmsg"]:
            return False,session_key_info["errmsg"]

        openid  = session_key_info['openid']
        session_key = session_key_info['session_key']

        # 验签
        signature_for_check = CreateSignature(rawData,session_key).get_signature()
        if signature != signature_for_check:
            return False,"签名错误"

        # 校验appid
        if source == "purchase":
            pc = WXBizDataCrypt(PURCHASE_APPLET_APPID, session_key)
        elif source == "demand":
            pc = WXBizDataCrypt(DEMAND_APPLET_APPID, session_key)
        else:
            pc = WXBizDataCrypt(PURCHASE_APPLET_APPID, session_key)
        decrypted_data = pc.decryptData(encryptedData, iv)
        unionId = decrypted_data.get("unionId","")

        # unionId为空的情况：小程序未绑定开放平台
        if not unionId:
            return False,"无法获取用户的unionid"

        userInfo["unionid"] = unionId
        userInfo["headimgurl"] = userInfo.get("avatarUrl")
        userInfo["nickname"] = userInfo.get("nickName")
        userInfo["sex"] = userInfo.get("gender")
        return True,userInfo