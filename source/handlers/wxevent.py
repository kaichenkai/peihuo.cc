import time

from handlers.base.webbase import BaseHandler

try:
    import xml.etree.cElementTree as ET
except:
    import xml.etree.ElementTree as ET
import requests
import json

import tornado.gen

from dal.db_configs import redis, pf_redis
from handlers.base.pub_web import GlobalBaseHandler
from handlers.base.pub_wx_web import WxOauth2
from handlers.weixin.WXBizMsgCrypt import WXBizMsgCrypt


# 微信公众绑定到开放平台的下面三个类用到的一些公用方法
class WxmpBindToWxopenBaseHandler(GlobalBaseHandler):
    @classmethod
    def xmlToDic(self, xmlstr):
        if isinstance(xmlstr, bytes):
            xmlstr = xmlstr.decode('utf-8')
        else:
            xmlstr = xmlstr
        data = {}
        tree = ET.fromstring(xmlstr)
        for child in tree:
            data[child.tag] = child.text
        return data

    def check_xsrf_cookie(self):
        return True

    @classmethod
    def make_xml(self, ToUserName, FromUserName, CreateTime, MsgType, Content=None):
        root = ET.Element('xml')
        first = ET.Element('ToUserName')
        first.text = ToUserName
        second = ET.Element('FromUserName')
        second.text = FromUserName
        third = ET.Element('CreateTime')
        third.text = CreateTime
        forth = ET.Element('MsgType')
        forth.text = MsgType
        data = [first, second, third, forth]
        if Content:
            fifth = ET.Element('Content')
            fifth.text = Content
            data.append(fifth)
        data = tuple(data)
        root.extend(data)
        return root

    @classmethod
    def check_signature(self, signature, timestamp, nonce):
        import hashlib
        token = 'senguotest123'
        L = [timestamp, nonce, token]
        try:
            L.sort()
        except:
            print('L sort error')
        s = L[0] + L[1] + L[2]
        if isinstance(s, str):
            s = s.encode('utf-8')
        return hashlib.sha1(s).hexdigest() == signature


# 订货后台微信服务号服务器配置，启用开发开发者模式后，用户发给公众号的消息以及开发者所需要的事件推送，将被微信转发到该 URL 中
class WxMessage(WxmpBindToWxopenBaseHandler):
    @BaseHandler.check_arguments('signature?:str', 'timestamp?:str', 'nonce?:str', 'echostr:str')
    def get(self):
        signature = self.args.get('signature', '')
        timestamp = self.args.get('timestamp', '')
        nonce = self.args.get('nonce', '')
        echostr = self.args['echostr']
        if self.check_signature(signature, timestamp, nonce):
            return self.write(echostr)
        else:
            return self.write(echostr)

    @BaseHandler.check_arguments('timestamp?:str', 'signature?:str', 'nonce?:str',
                                 'encrypt_type?:str', 'msg_signature?:str')
    def post(self):
        # 解析返回数据
        encodingAESKey = "tRKv4W4QonuYAfuEck0N6xSPnrPuRVra438AUzYSrbf"  # 消息加密秘钥
        token          = "2w3e4r5t6ysxdcfvgbhnjmkjuliookij"             # token
        open_appid     = "wx554875345d7cbba4"                           # 服务号所在开放平台的appid（这里使用的是公众账号一栏）
        decrypt_test   = WXBizMsgCrypt(token,encodingAESKey,open_appid)
        raw_data       = self.request.body
        timestamp      = self.args.get('timestamp', None)
        signature      = self.args.get('signature', None)
        nonce          = self.args.get('nonce', None)
        encrypt_type   = self.args.get('encrypt_type', None)
        msg_signature  = self.args.get('msg_signature', None)
        ret, decryp_xml = decrypt_test.DecryptMsg(raw_data,msg_signature,timestamp,nonce)
        if isinstance(decryp_xml, bytes):
            decryp_xml = decryp_xml.decode('utf-8')
        start_index    = decryp_xml.find('<xml>')
        end_index      = decryp_xml.find('</xml>')
        decryp_xml     = decryp_xml[start_index:end_index+6]
        data           = self.xmlToDic(decryp_xml)
        event          = data.get('Event', "").upper()
        eventkey       = data.get('EventKey', None)
        MsgType        = data.get('MsgType', None)
        Content        = data.get('Content', None)
        ToUserName     = data.get('ToUserName', None)    # 开发者微信号
        FromUserName   = data.get('FromUserName', None)  # 发送方openid
        CreateTime     = data.get('CreateTime', None)    # 接受消息时间
        MsgId          = data.get('Content', None)
        CreateTime     = str(int(time.time()))
        openid         = FromUserName

        if event == "CLICK":
            if eventkey == 'photo':
                access_token = WxOauth2.get_client_access_token()
                url = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={0}'.format(access_token)
                pic_data = {
                    "touser": FromUserName,
                    "msgtype": "image",
                    "image": {
                        "media_id": "tUtWkxgHhnlhku5aTJ08z6wPJKuLi7-mNyW1QRi-6Bna-Og9OgS885Tm1EbtDEOs"
                    }
                }
                r = requests.post(url, data=json.dumps(pic_data))
                return self.write('')

        # 用户扫码进入森果商户通
        if event == 'SCAN':
            scene_id = int(eventkey) if eventkey and eventkey.isdigit() else 0

            # 扫码绑定
            if len(str(scene_id)) == 8 and openid:
                h = "pf_scene_openid:%s" % scene_id
                wx_userinfo = WxMessage.get_wx_user_info(openid)
                pf_redis.set(h, json.dumps(wx_userinfo), 300)
                self.kefu_auto_reply(openid, "扫码成功")

            # 扫码登录
            elif len(str(scene_id)) == 9 and openid:
                # 获取用户信息，存入redis
                h = "pf_scene_openid:%s" % scene_id
                wx_userinfo = WxMessage.get_wx_user_info(openid)
                pf_redis.set(h, json.dumps(wx_userinfo), 300)
                # 使用客服接口发送消息
                self.kefu_auto_reply(openid, "扫码成功")

            else:
                self.write('')

        elif event in ['TEMPLATESENDJOBFINISH', 'LOCATION']:
            return self.write('success')

        # 除了上面的事件推送之外的所有事件推送，都回复一个空串。
        else:
            return self.write('')

    @staticmethod
    def get_wx_user_info(openid):
        access_token = WxOauth2.get_client_access_token()
        url = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token={0}&openid={1}&lang=zh_CN' \
            .format(access_token, openid)
        r = requests.get(url)
        wx_userinfo = json.loads(r.content.decode("utf-8"))
        return wx_userinfo

    # 客服接口
    @tornado.gen.coroutine
    def kefu_auto_reply(self, ToUserName, content):
        access_token = WxOauth2.get_client_access_token()
        from tornado.httpclient import AsyncHTTPClient
        client = AsyncHTTPClient()
        url = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={0}'.format(access_token)
        data = {
            "touser": ToUserName,
            "msgtype": "text",
            "text": {
                "content": content,
            }
        }
        data = json.dumps(data, ensure_ascii=False)
        try:
            res = yield client.fetch(url, method="POST", body=data)
        except:
            return False
