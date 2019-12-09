# -*- coding:utf-8 -*-

import math
from PIL import Image, ImageOps


class ConvertImage(object):
    """
    Load images in, and output ESC/POS formats.
    The class is designed to efficiently delegate image processing to
    PIL, rather than spend CPU cycles looping over pixels.
    """

    def __init__(self, img_source):
        """
        Load in an image
        :param img_source: PIL.Image, or filename to load one from.
        """
        if isinstance(img_source, Image.Image):
            img_original = img_source
        else:
            img_original = Image.open(img_source)

        # store image for eventual further processing (splitting)
        self.img_original = img_original

        # Convert to white RGB background, paste over white background
        # to strip alpha.
        img_original = img_original.convert('RGBA')
        im = Image.new("RGB", img_original.size, (255, 255, 255))
        im.paste(img_original, mask=img_original.split()[3])
        # Convert down to greyscale
        im = im.convert("L")
        # Invert: Only works on 'L' images
        im = ImageOps.invert(im)
        # Pure black and white
        self._im = im.convert("1")

    @property
    def width(self):
        """
        Width of image in pixels
        """
        width_pixels, _ = self._im.size
        return width_pixels

    @property
    def width_bytes(self):
        """
        Width of image if you use 8 pixels per byte and 0-pad at the end.
        """
        return (self.width + 7) >> 3

    @property
    def height(self):
        """
        Height of image in pixels
        """
        _, height_pixels = self._im.size
        return height_pixels

    def to_column_format(self, high_density_vertical=True):
        """
        Extract slices of an image as equal-sized blobs of column-format data.
        :param high_density_vertical: Printed line height in dots
        """
        im = self._im.transpose(Image.ROTATE_270).transpose(Image.FLIP_LEFT_RIGHT)
        line_height = 24 if high_density_vertical else 8
        width_pixels, height_pixels = im.size
        top = 0
        left = 0
        while left < width_pixels:
            box = (left, top, left + line_height, top + height_pixels)
            im_slice = im.transform((line_height, height_pixels), Image.EXTENT, box)
            im_bytes = im_slice.tobytes()
            yield(im_bytes)
            left += line_height

    def to_raster_format(self):
        """
        Convert image to raster-format binary
        """
        return self._im.tobytes()

    def split(self, fragment_height):
        """
        Split an image into multiple fragments after fragment_height pixels
        :param fragment_height: height of fragment
        :return: list of PIL objects
        """
        passes = int(math.ceil(self.height/fragment_height))
        fragments = []
        for n in range(0, passes):
            left = 0
            right = self.width
            upper = n * fragment_height
            lower = min((n + 1) * fragment_height, self.height)
            box = (left, upper, right, lower)
            fragments.append(self.img_original.crop(box))
        return fragments

    def center(self, max_width=560):
        """In-place image centering
        :param: Maximum width in order to deduce x offset for centering
        :return: None
        """
        old_width, height = self._im.size
        new_size = (max_width, height)

        new_im = Image.new("1", new_size)
        paste_x = int((max_width - old_width) / 2)

        new_im.paste(self._im, (paste_x, 0))

        self._im = new_im

    def resize_img(self,dst_w=200, dst_h=0, qua=85):
        """
        只给了宽或者高，或者两个都给了，然后取比例合适的
        如果图片比给要压缩的尺寸都要小，则不进行压缩
        """
        ori_w, ori_h =  self._im.size
        ratio = 1

        # 如果当前图片尺寸小不放大
        if ori_w <= dst_w and ori_h <= dst_h:
            return

        width_ratio = dst_w / ori_w
        height_ratio = dst_h / ori_h

        if width_ratio and height_ratio:
            ratio = min(width_ratio, height_ratio)
        elif height_ratio:
            ratio = height_ratio
        elif width_ratio:
            ratio = width_ratio
        else:
            raise ValueError("dst_w 和 dst_h 不能同时为0")

        new_width = int(ori_w * ratio)
        new_height = int(ori_h * ratio)

        self._im = self._im.resize((new_width, new_height), Image.BICUBIC)


class ConvertSignature(ConvertImage):
    """电子写字板签名图片，需要裁剪边缘，并固定高度进行缩小和放大"""
    def __init__(self, img_source):
        super().__init__(img_source)
        # 裁剪边缘
        im = self._im
        im = im.crop(im.getbbox())
        self._im = im

    def resize_img(self, dst_h=100, qua=85):
        """忽略宽度，定高缩放"""
        dst_w = 0
        ori_w, ori_h = self._im.size
        # 如果图片需要缩小，直接调用ConvertImage的方法就好
        if ori_h > dst_h:
            super().resize_img(dst_w, dst_h, qua)
        # 如果图片需要放大
        else:
            ratio = dst_h / ori_h
            new_width = int(ori_w * ratio)
            new_height = int(ori_h * ratio)
            self._im = self._im.resize((new_width, new_height), Image.BICUBIC)
