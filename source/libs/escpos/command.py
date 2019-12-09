# -*- coding:utf-8 -*-

import base64
import struct
from io import BytesIO

from PIL import Image

from libs.escpos.convert_image import ConvertImage, ConvertSignature


class Commander:
    @staticmethod
    def reset():
        return [0x1B, 0x40]

    @staticmethod
    def text(text):
        return bytearray(text, 'utf-8')

    @staticmethod
    def bold(apply):
        return [0x1B, 0x45, apply and 1 or 0]

    @staticmethod
    def font_multiplies(width, height):
        return [0x1D, 0x21, (width - 1) * 16 + (height - 1)]

    @staticmethod
    def alignment(alignment):
        return [0x1B, 0x61, alignment]

    @staticmethod
    def barcode(content):
        cmd = bytearray()
        # 设置居中
        # cmd.extend([0x1B, 0x61, 1])
        # 条码高度
        cmd.extend([0x1D, 0x68, 100])
        # 条码宽度
        cmd.extend([0x1D, 0x77, 2])
        # 不打印 HRI 字符
        cmd.extend([0x1D, 0x48, 0])
        # 打印
        cmd.extend([0x1D, 0x6B, 0x49, len(content)])
        cmd.extend(bytearray(content, 'utf-8'))
        # 还原居中
        # cmd.extend([0x1B, 0x61, 0])
        return cmd

    @staticmethod
    def qrcode(content):
        cmd = bytearray()
        # 设置居中
        # cmd.extend([0x1B, 0x61, 1])
        # 设置单元大小
        cmd.extend([0x1D, 0x28, 0x6B, 0x03, 0x00, 0x31, 0x43, 8])
        # 设置二维码纠错等级 - 15 %
        cmd.extend([0x1D, 0x28, 0x6B, 0x03, 0x00, 0x31, 0x45, 48])
        # 传输数据到编码缓存
        length = len(content) + 3
        pL = length % 256
        cmd.extend([0x1D, 0x28, 0x6B, pL, 0x00, 0x31, 0x50, 0x30])
        # 二维码内容
        cmd.extend(bytearray(content, 'utf-8'))
        # 打印
        cmd.extend([0x1D, 0x28, 0x6B, 0x03, 0x00, 0x31, 0x51, 0x30])
        # 还原居中
        # cmd.extend([0x1B, 0x61, 0])
        return cmd

    @staticmethod
    def receipt_id(receipt_id):
        """ 单据号 """
        cmd = bytearray()
        # 数据包主题
        cmd.extend([0x03, 0x00])
        # 单据号
        cmd.extend(bytearray(receipt_id, 'utf-8'))
        # 单据号结束
        cmd.extend([0x00])
        return cmd

    @staticmethod
    def print_and_feed(distance=96):
        return [0x1B, 0x4A, distance]

    @staticmethod
    def cut_paper():
        return [0x1D, 0x56, 65, 20]

    @staticmethod
    def image(img_base64):
        # 测试图片，待修改 add by yy 2018-3-20
        content = base64.b64decode(img_base64)
        img_source = Image.open(BytesIO(content))

        # 将图片进行去透明、反色处理
        im = ConvertImage(img_source)
        # 图片压缩
        im.resize_img()
        # 图片居中
        im.center()
        # 计算图片宽度
        width_bytes = struct.pack('2B', int(im.width / 8 % 256), int(im.width / 8 / 256))
        # 计算图片高度
        height_bytes = struct.pack('2B', int(im.height % 256), int(im.height / 256))
        # 图片内容
        image_data = im.to_raster_format()

        cmd = bytearray()
        # 设置格式
        cmd.extend([0x1D, 0x76, 0x30, 0x00])
        # 设置图片宽度
        cmd.extend(width_bytes)
        # 设置图片高度
        cmd.extend(height_bytes)
        # 写入图片信息
        cmd.extend(image_data)

        return cmd

    @staticmethod
    def signature(img_base64):
        """处理电子手写板用户签名"""
        content = base64.b64decode(img_base64)
        img_source = Image.open(BytesIO(content))

        # 将图片进行去透明、反色、裁切白边处理
        sig = ConvertSignature(img_source)
        # 图片压缩
        sig.resize_img()
        # 图片居中
        sig.center()
        # 计算图片宽度
        width_bytes = struct.pack('2B', int(sig.width / 8 % 256), int(sig.width / 8 / 256))
        # 计算图片高度
        height_bytes = struct.pack('2B', int(sig.height % 256), int(sig.height / 256))
        # 图片内容
        image_data = sig.to_raster_format()

        cmd = bytearray()
        # 设置格式
        cmd.extend([0x1D, 0x76, 0x30, 0x00])
        # 设置图片宽度
        cmd.extend(width_bytes)
        # 设置图片高度
        cmd.extend(height_bytes)
        # 写入图片信息
        cmd.extend(image_data)

        return cmd
