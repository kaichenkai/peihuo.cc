#coding:utf-8
# 支付宝的当面付
from settings import *
import time
import datetime
import requests

from Crypto.Hash import SHA as SHA
from Crypto.Signature import PKCS1_v1_5 as pk
from Crypto.PublicKey import RSA

import base64
import urllib
import math
from dal.db_configs import redis
from handlers.base.pub_func import NumFunc
check_float = NumFunc.check_float


class AliF2FPay(object):
    # 0.获取小果服务商下面的ali_app_auth_token
    @classmethod
    def getAppauthToken(cls,admin_id=None):
        if admin_id:
            ali_app_auth_token = "ali_app_auth_token:%s" % admin_id
            ali_app_refresh_token = "ali_app_refresh_token:%s" % admin_id
        else:
            ali_app_auth_token = "ali_app_auth_token_senguo"
            ali_app_refresh_token = "ali_app_refresh_token_senguo"
        if redis.get(ali_app_auth_token) and redis.ttl(ali_app_auth_token)>3600*24*30:
            ali_auth_token=redis.get(ali_app_auth_token).decode('utf-8')
        elif redis.get(ali_app_refresh_token):
            ali_refresh_token=redis.get(ali_app_refresh_token).decode('utf-8')
            if_success,ret_dict=cls.get_ali_auth_token("refresh_token",ali_refresh_token)
            if if_success:
                ali_auth_token=ret_dict["app_auth_token"]
                redis.set(ali_app_auth_token,ali_auth_token,ret_dict["expires_in"])
                redis.set(ali_app_refresh_token,ret_dict["app_refresh_token"],ret_dict["re_expires_in"])
            else:
                ali_auth_token=None
        else:
            ali_auth_token=None
        return ali_auth_token

    @classmethod
    def get_ali_auth_token(cls,grant_type,code_or_refreshtoken):
        ret_dict={}
        alif2fpay = AliF2FPay()
        parameters = {}
        parameters['method']='alipay.open.auth.token.app'
        alif2fpay.getPublicParas(parameters)
        parameters['app_id']=ALIPAY_KF_APPID
        parameters['version']='1.0'
        if grant_type=="authorization_code":
            parameters['biz_content']="{'grant_type': '"+grant_type+"', 'code': '"+code_or_refreshtoken+"'}"
        else:
            parameters['biz_content']="{'grant_type': '"+grant_type+"', 'refresh_token': '"+code_or_refreshtoken+"'}"
        strForSign = alif2fpay.formatBizQueryParaMap(parameters,False)
        h=SHA.new(strForSign.encode(encoding=ALIPAY_PUBLIC_CHARSET))
        key=RSA.importKey(ALIPAY_KF_RAS_PRIVATE_KEY_WITHLINEBREAK)
        signer = pk.new(key)
        signn=signer.sign(h)
        parameters['sign']=base64.b64encode(signn)
        r = requests.post('https://openapi.alipay.com/gateway.do?charset='+ALIPAY_PUBLIC_CHARSET, data=parameters,verify=False)
        retStrOfAli = r.text
        dictRetStr=eval(retStrOfAli)
        dicInfo = dictRetStr['alipay_open_auth_token_app_response']
        if (dicInfo['code']!='10000'):
            ret_msg=dicInfo.get('sub_msg','')
            if not ret_msg:
                ret_msg=dicInfo['msg']
            ret_dict["error_txt"] = ret_msg
            return False,ret_dict
        else:
            ret_dict["ali_merchant_id"]=dicInfo["user_id"]
            ret_dict["ali_auth_appid"]=dicInfo["auth_app_id"]
            ret_dict["app_auth_token"]=dicInfo["app_auth_token"]
            ret_dict["expires_in"]=dicInfo["expires_in"]
            ret_dict["app_refresh_token"]=dicInfo["app_refresh_token"]
            ret_dict["re_expires_in"]=dicInfo["re_expires_in"]
            return True,ret_dict

    # 1.0 获取公共参数
    def getPublicParas(self,parameters):
        parameters['app_id']=ALIPAY_SCAN_APPID
        parameters['charset']=ALIPAY_PUBLIC_CHARSET
        parameters['sign_type']='RSA'
        parameters['sign']=''
        parameters['timestamp']=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 1.1 二维码支付下单参数
    def getPayParas(self,order,fruits):
        parameters = {}
        parameters['method']='alipay.trade.precreate'
        # parameters['notify_url']=ALIPAY_HANDLE_HOST + "/cashierQrAliCallBack"
        # 需要设置回调地址
        raise NotImplementedError
        parameters['version']='1.0'
        self.getPublicParas(parameters)
        shop_name=order.shop.shop_name
        totalAmount = order.new_totalprice
        out_trade_no=order.num
        goods_detail=''
        for k,v in fruits.items():
            price = fruits[k]['price']
            num = fruits[k]['num']
            cashier_benefit = fruits[k]['cashier_benefit']
            fruit_name = fruits[k]['fruit_name']
            charge = fruits[k]['charge']
            unit= fruits[k]['unit']
            sub_total = check_float(price * num - cashier_benefit)
            fruit_name += '\r\n[%s*%.2f%s]'%(charge,num,unit)
            if cashier_benefit:
                fruit_name +='\r\n(单品优惠:%.2f元)'%(cashier_benefit)
            goods_detail+="{'goods_id': '"+str(k)+"', 'price': '"+str(sub_total)+"', 'quantity': '1','goods_name': '"+fruit_name+"'},"
        goods_detail="["+goods_detail[:len(goods_detail)-1]+"]"
        subject='到店二维码付-'+shop_name+'-单号：'+out_trade_no
        parameters['biz_content']="{'subject': '"+subject+"','out_trade_no': '"+out_trade_no+"', 'goods_detail': "+goods_detail+",\
             'total_amount': '"+str(totalAmount)+"', 'discountable_amount': '0'}"
        return parameters

    # 1.2 条码支付参数
    def getBarcodeParas(self,order,auth_code,fruits):
        parameters = {}
        parameters['method']='alipay.trade.pay'
        # parameters['notify_url'] = ALIPAY_HANDLE_HOST + "/cashierBarAliCallBack"
        # 需要设置回调地址
        raise NotImplementedError
        parameters['version']='1.0'
        self.getPublicParas(parameters)
        shop_name=order.shop.shop_name
        totalAmount = order.new_totalprice
        out_trade_no=order.num
        goods_detail=''
        for k,v in fruits.items():
            price = fruits[k]['price']
            num = fruits[k]['num']
            cashier_benefit = fruits[k]['cashier_benefit']
            fruit_name = fruits[k]['fruit_name']
            charge = fruits[k]['charge']
            unit= fruits[k]['unit']
            sub_total = check_float(price * num - cashier_benefit)
            fruit_name += '\r\n[%s*%.2f%s]'%(charge,num,unit)
            if cashier_benefit:
                fruit_name +='\r\n(单品优惠:%.2f元)'%(cashier_benefit)
            goods_detail+="{'goods_id': '"+str(k)+"', 'price': '"+str(sub_total)+"', 'quantity': '1','goods_name': '"+fruit_name+"'},"
        goods_detail="["+goods_detail[:len(goods_detail)-1]+"]"
        scene='bar_code'
        auth_code=auth_code
        subject='到店条码付-'+shop_name+'-单号：'+out_trade_no
        parameters['biz_content']="{'subject': '"+subject+"', 'discountable_amount': '0',\
            'scene': '"+scene+"', 'auth_code': '"+str(auth_code)+"', \
            'out_trade_no': '"+out_trade_no+"', 'goods_detail': "+goods_detail+", 'total_amount': '"+str(totalAmount)+"'}"
        return parameters

    # 1.3 退款参数
    def getRefundParas(self,trade_no,apply_money,refund_reason,out_refund_no):
        parameters = {}
        parameters['method']='alipay.trade.refund'
        parameters['version']='1.0'
        self.getPublicParas(parameters)
        parameters['biz_content']='{"trade_no": "'+str(trade_no)+'","refund_reason": "'+refund_reason+'", "refund_amount": '+str(apply_money)+',"out_request_no":"'+ out_refund_no +'"}'
        return parameters

    # 1.4 查询参数
    def getQueryParas(self,out_trade_no):
        parameters = {}
        parameters['method']='alipay.trade.query'
        self.getPublicParas(parameters)
        parameters['biz_content']='{"out_trade_no": "'+str(out_trade_no)+'"}'
        return parameters

    # 1.4.1 查询参数:用transaction_id
    def getQueryParas2(self,trade_no):
        parameters = {}
        parameters['method']='alipay.trade.query'
        self.getPublicParas(parameters)
        parameters['biz_content']='{"trade_no": "'+str(trade_no)+'"}'
        return parameters

    # 1.5 撤销参数
    def getCancelParas(self,out_trade_no):
        parameters = {}
        parameters['method']='alipay.trade.cancel'
        self.getPublicParas(parameters)
        parameters['biz_content']='{"out_trade_no": "'+str(out_trade_no)+'"}'
        return parameters

    # 1.6 关单参数
    def getCloseParas(self,out_trade_no):
        parameters = {}
        parameters['method']='alipay.trade.close'
        parameters['version']='1.0'
        self.getPublicParas(parameters)
        parameters['biz_content']='{"out_trade_no": "'+str(out_trade_no)+'"}'
        return parameters

    # 1.7 在线支付参数
    def getWapPayParas(self, db_record, biz_body):
        parameters = {}
        parameters['method']='alipay.trade.wap.pay'
        out_trade_no=db_record['out_trade_no']
        parameters['return_url']=db_record['return_url']
        parameters['notify_url']=db_record['notify_url']
        totalAmount=db_record['totalAmount']
        subject=db_record['subject']
        parameters['version']='1.0'
        parameters['format']="JSON"
        self.getPublicParas(parameters)
        parameters['biz_content']="{'body':'"+biz_body+"','subject':'"+subject+"','out_trade_no':'"+out_trade_no+"','total_amount':'" + str(totalAmount)+"','product_code':'QUICK_WAP_PAY','goods_type':'1'}"
        return parameters

    # 1.8 退款查询参数
    def getRefundQueryParas(self,out_request_no,trade_no):
        parameters = {}
        parameters['method']='alipay.trade.fastpay.refund.query'
        parameters['version']='1.0'
        self.getPublicParas(parameters)
        parameters['biz_content']='{"trade_no": "'+str(trade_no)+'","out_request_no":"'+str(out_request_no)+'"}'
        return parameters

    # 1.9 当面付有返佣，加上返佣需要的参数；手机网站虽然说没有，但还是加上
    def getCommisionParas(self,parameters):
        parameters['extend_params']="{'sys_service_provider_id': '"+ALIPAY_KF_PID+"'}"
        parameters['biz_content'] = parameters['biz_content'][:-1]+", 'extend_params': {'sys_service_provider_id': '"+ALIPAY_KF_PID+"'}}"
        return parameters

    # 2.参数重排
    def formatBizQueryParaMap(self, paraMap, urlencode):
        # """格式化参数，签名过程需要使用"""
        slist = sorted(paraMap)
        buff = []
        for k in slist:
            v = urllib.parse.quote(paraMap[k]) if urlencode else paraMap[k]
            if k != 'sign':
                buff.append("{0}={1}".format(k, v))
        return "&".join(buff)

    # 3.RSA签名
    # @param signdata: 需要签名的字符串
    def sign(self,signdata,rsa_key=ALIPAY_SCAN_SENGUO_RAS_PRIVATE_KEY_WITHLINEBREAK):
        h=SHA.new(signdata.encode(encoding=ALIPAY_PUBLIC_CHARSET))
        key=RSA.importKey(rsa_key)
        signer = pk.new(key)
        signn=signer.sign(h)
        signn=base64.b64encode(signn)
        return signn

    # 4.获得支付宝返回的字符串中待签名的部分
    # eg:{"alipay_trade_precreate_response":{"code":"10000","msg":"Success","out_trade_no":"1992000004","qr_code":"https:\/\/qr.alipay.com\/bar3yfck39znjfcrd4"},
    #     "sign":"g5znKhL3ZFTAFE2Tv4+LW35JtoxkNHiwXSJgYeJw4+02/6oea7auqjz5KzkGA86Yp/wpsJs5q7HDGYq4IUITGbhzNTwrZc8xrcPHr9dydPnW02NvhywryCWAP2Sd4Bo9lu7GQvJpTvsh0ncl0O/1OXRNTzsonijIMGh9OGSPdsU="}
    # or: {"alipay_trade_precreate_response":{"code":"40002","msg":"Invalid Arguments","sub_code":"isv.invalid-signature","sub_msg":"无效签名"},
    #     "sign":"aUududgICSy+Wr5NppUHX3FedZeQJCZ+L+xYy7q/TwwXLT5PEkF1PGlbG8hohV0kLZO9iFkWt7mhJeozz5GAp9cqVCnvEdiOT1ausq1EdBXIWF4kPb8C2ssoq6OpgBoHgd+cPbpaekbwbyHxWIHvfZopDUCG+G8aTUxJjLrTVsY="}

    # 4.1 获取支付宝扫码支付链接结果返回解析
    def getStrForSignOfRet(self,retStrOfAli):
        indexOfSign=retStrOfAli.find('"sign"')
        indexOfResponse=retStrOfAli.find('"alipay_trade_precreate_response"')
        indexOfError=retStrOfAli.find('error_response')
        response=''
        if indexOfResponse >0 and indexOfSign > 0:
            iReBegin=indexOfResponse+len('"alipay_trade_precreate_response"')+1
            iReEnd=indexOfSign-1
            response=retStrOfAli[iReBegin:iReEnd]
        elif indexOfError > 0 and indexOfSign > 0:
            iReBegin=indexOfResponse+len('"alipay_trade_precreate_response"')+1
            iReEnd=indexOfSign-1
            response=retStrOfAli[iReBegin:iReEnd]
        return response

    # 4.2 获取撤销支付宝支付订单返回结果解析
    def getStrForSignOfCancelRet(self,retStrOfAli):
        indexOfSign=retStrOfAli.find('"sign"')
        indexOfResponse=retStrOfAli.find('"alipay_trade_cancel_response"')
        response=''
        if indexOfResponse >0 and indexOfSign >0:
            iReBegin=indexOfResponse+len('"alipay_trade_cancel_response"')+1
            iReEnd=indexOfSign-1
            response=retStrOfAli[iReBegin:iReEnd]
        return response

    # 4.3 获取查询支付宝订单返回结果解析
    def getStrForSignOfQueryRet(self,retStrOfAli):
        indexOfSign=retStrOfAli.find('"sign"')
        indexOfResponse=retStrOfAli.find('"alipay_trade_query_response"')
        response=''
        if indexOfResponse >0 and indexOfSign >0:
            iReBegin=indexOfResponse+len('"alipay_trade_query_response"')+1
            iReEnd=indexOfSign-1
            response=retStrOfAli[iReBegin:iReEnd]
        return response

    # 4.4 获取支付宝退款返回结果解析
    def getStrForSignOfRefundRet(self,retStrOfAli):
        indexOfSign=retStrOfAli.find('"sign"')
        indexOfResponse=retStrOfAli.find('"alipay_trade_refund_response"')
        indexOfError=retStrOfAli.find('msg')
        response=''
        if indexOfResponse > 0 and indexOfSign > 0:
            iReBegin=indexOfResponse+len('"alipay_trade_refund_response"')+1
            iReEnd=indexOfSign-1
            response=retStrOfAli[iReBegin:iReEnd]
        elif indexOfError > 0 and indexOfSign > 0:
            iReBegin=indexOfResponse+len('"alipay_trade_refund_response"')+1
            iReEnd=indexOfSign-1
            response=retStrOfAli[iReBegin:iReEnd]
        return response

    # 4.5 获取支付宝条码支付结果解析
    def getStrForSignOfBarcodeRet(self,retStrOfAli):
        indexOfSign=retStrOfAli.find('"sign"')
        indexOfResponse=retStrOfAli.find('"alipay_trade_pay_response"')
        indexOfError=retStrOfAli.find('msg')
        response=''
        if indexOfResponse >0 and indexOfSign >0:
            iReBegin=indexOfResponse+len('"alipay_trade_pay_response"')+1
            iReEnd=indexOfSign-1
            response=retStrOfAli[iReBegin:iReEnd]
        elif indexOfError > 0 and indexOfSign >0:
            iReBegin=indexOfResponse+len('"alipay_trade_pay_response"')+1
            iReEnd=indexOfSign-1
            response=retStrOfAli[iReBegin:iReEnd]
        return response

    # 5.支付宝-扫码支付-RSA验签
    def checkSign(self,sign,signdata):
        signn=base64.b64decode(sign)
        key_withlinebreak=self.completeAlipayPublicKey(ALIPAY_PUBLIC_KEY)
        key=RSA.importKey(key_withlinebreak)
        h=SHA.new(signdata.encode(encoding=ALIPAY_PUBLIC_CHARSET))
        verifier = pk.new(key)
        if verifier.verify(h, signn):
            return True
        else:
            h=SHA.new(signdata.replace('\\','').encode(encoding=ALIPAY_PUBLIC_CHARSET))
            return verifier.verify(h, signn)

    # 6.给支付宝提供的没有换行的密钥换行
    def completeAlipayPublicKey(self,strPublicKey):
        nPublicKeyLen = len(strPublicKey);
        nMinus64=math.floor(nPublicKeyLen/64)
        listForPublicKey=list(strPublicKey)
        for i in range(nMinus64,0,-1):
            if strPublicKey[i*64] !='\n':
                listForPublicKey.insert(i*64,'\n')
        listForPublicKey.insert(0,'-----BEGIN PUBLIC KEY-----\n')
        listForPublicKey.append('\n-----END PUBLIC KEY-----\n')
        return ''.join(listForPublicKey)

    # 7.测试一下，用自己的公钥来解密自己的私钥加密的东西，测试验签方法
    def checkIfCheckSignWork(self,parameters,rsa_pub_key=ALIPAY_SCAN_SENGUO_RAS_PUBLIC_KEY):
        sign=parameters['sign']
        signn=base64.b64decode(sign)
        key_withlinebreak=self.completeAlipayPublicKey(rsa_pub_key)
        key=RSA.importKey(key_withlinebreak)
        signdata=self.formatBizQueryParaMap(parameters,False)
        h=SHA.new(signdata.encode(encoding=ALIPAY_PUBLIC_CHARSET))
        verifier = pk.new(key)
        if verifier.verify(h, signn):
            return True
        else:
            h=SHA.new(signdata.replace('\\','').encode(encoding=ALIPAY_PUBLIC_CHARSET))
            return verifier.verify(h, signn)
