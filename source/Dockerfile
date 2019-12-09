FROM python:3.5-alpine
MAINTAINER Chihane <chihane@yeah.net>

LABEL name="senguoph"
LABEL description="森果采购配货系统后端基础镜像"
LABEL maintainer="chihane@yeah.net"

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories
RUN apk add --no-cache --virtual .build-dependencies build-base libjpeg jpeg-dev zlib-dev libressl-dev libffi-dev tzdata

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./docker/conf/wait-for.sh /usr/local/bin/wait-for.sh
RUN chmod +x /usr/local/bin/wait-for.sh

RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

RUN apk del .build-dependencies
