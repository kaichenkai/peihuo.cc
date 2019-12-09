#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import binascii

from Crypto.Cipher import DES, AES


class EncryptBase():
    '''
        调用示例
        加密:SimpleEncrypt.encrypt('10930')
            返回:'41c836605df56a81'
        解密:SimpleEncrypt.decrypt('41c836605df56a81')
            返回:'10930'
    '''
    @classmethod
    def pad(cls, text):
        '''
            length需和key长度相等
        '''
        while len(text) % cls.crypt_len != 0:
            text += " "
        return text

    @classmethod
    def encrypt(cls, text):
        '''
            参数: text-待加密字符串
                  key-DES需要的秘钥
        '''
        if not isinstance(text,str):
            text = str(text)
        des = DES.new(cls.crypt_key.encode("utf-8"), DES.MODE_ECB)
        padded_text = cls.pad(text)
        encrypted_text = des.encrypt(padded_text.encode("utf-8"))
        return binascii.hexlify(encrypted_text).decode()

    @classmethod
    def decrypt(cls, text):
        if not isinstance(text,str):
            text = str(text)
        try:
            encrypted_text = binascii.unhexlify(text)
        except:
            return "0"
        des = DES.new(cls.crypt_key.encode("utf-8"), DES.MODE_ECB)
        return des.decrypt(encrypted_text).decode().strip()

    @classmethod
    def decrypt_to_int(cls,text):
        try:
            text = int(cls.decrypt(text))
        except:
            text = 0
        return text


class SimpleEncrypt(EncryptBase):
    """
        用于配货系统数据加密
    """
    crypt_key = "3y4@B@W8"
    crypt_len = 8


class SgSimpleEncrypt(EncryptBase):
    """
        用于与零售系统进行数据交互
    """
    crypt_key = "s0&Kp#HF"
    crypt_len = 8


class PfSimpleEncrypt(EncryptBase):
    """
        用于与批发系统进行数据交互
    """
    crypt_key = "a#No0UD^"
    crypt_len = 8


class CgSimpleEncrypt(EncryptBase):
    """
        用于采购系统数据加密
    """
    crypt_key = "CGkiedbs"
    crypt_len = 8



# AES加密，支持中文
class AESCryptoBase(object):
    """AES加密算法，支持中文，右侧使用\0补齐。

    - 密钥key长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度。
    - 初始向量iv长度必须为16 Bytes 长度。
    - 被加密字符串长度必须为16 Bytes 的整数倍。
    """
    @classmethod
    def encrypt(cls, text):
        text = text.encode()
        pad_count = len(cls.key) - (len(text) % len(cls.key))
        padded_text = text + b"\0" * pad_count
        cryptor = AES.new(cls.key, cls.mode, cls.iv)
        return binascii.b2a_hex(cryptor.encrypt(padded_text)).decode()

    @classmethod
    def decrypt(cls, text):
        cryptor = AES.new(cls.key, cls.mode, cls.iv)
        try:
            content = binascii.a2b_hex(text.encode())
        except binascii.Error:
            content = ""
        try:
            result = cryptor.decrypt(content)
        except ValueError:
            result = b""
        return result.rstrip(b"\0").decode()


class QRCodeCrypto(AESCryptoBase):
    """
    用于个人中心二维码加解密，AES-128算法。
    """
    key = "U6i['85Qxw%=ox6R"
    mode = AES.MODE_CBC
    iv = "`V(x0[wJn08f+L6t"
