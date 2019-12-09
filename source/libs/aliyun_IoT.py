# 阿里云物联网相关
from aliyunsdkcore import client
from aliyunsdkiot.request.v20170420 import PubRequest

_accessKeyId = 'LTAIrHRiv3K322Hz'
_accessKeySecret = '4ns1IofAr0DXnkaepD2xAS0AoJj1PF'

IoTClient = client.AcsClient(_accessKeyId, _accessKeySecret, 'cn-shanghai')
