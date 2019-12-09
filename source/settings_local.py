# cookie域名
ROOT_HOST_NAME = "ph.senguo.cc"
COOKIE_SECRET = "local"

# 授权回调域名
APP_OAUTH_CALLBACK_URL = "https://peihuo.senguo.cc"

CELERY_BROKER = "amqp://guest@127.0.0.1:5672//"  # 本地celery配置

# mysql数据库相关
MYSQL_SERVER = "localhost:3306"  # 本地数据库配置
MYSQL_DRIVER        = "pymysql"
MYSQL_USERNAME      = "username"
MYSQL_PASSWORD      = "password"
DB_NAME             = "senguoph"
DB_STATISTIC_NAME   = "senguoph_statistic"
DB_CHARSET          = "utf8"

#果蔬批发服务号
MP_APPID     = "000000"  # 请务必修改此常量，保证本地不会生成access_token致使线上access_token过期
MP_APPSECRET = "000000"  # 请务必修改此常量，保证本地不会生成access_token致使线上access_token过期

# 小程序
PURCHASE_APPLET_APPID = "local"
PURCHASE_APPLET_APPSECRET = "local"
DEMAND_APPLET_APPID = "local"
DEMAND_APPLET_APPSECRET = "local"

# redis数据库相关
REDIS_SERVER = "127.0.0.1"  # 本地redis配置
REDIS_PORT   = 6379
REDIS_PASSWORD = ""

# 七牛云的参数
QINIU_ACCESS_KEY = "Pm0tzHLClI6iHqxdkCbwlSwHWZycbQoRFQwdqEI_"
QINIU_SECRET_KEY = "gCjIMVE_lpW7d2bjI-AdMXDKQeE1bdtKxRInBRTH"
QINIU_BUCKET = "shopimg"
QINIU_IMG_HOST = "http://img.senguo.cc/"

# 钉钉机器人webhook地址，用于接收服务器报错
DINGTALK_WEBHOOK = ""

# 森果统一账号相关
AUTH_COOKIE_EXPIRE_DAYS = 7                 # cookie过期时间
AUTH_COOKIE_DOMAIN = "senguo.cc"
AUTH_API_SECRETKEY = "test"                # passport.senguo.cc 接口鉴权密钥
AUTH_HOST_NAME = "http://passporttest.senguo.cc"    # passport.senguo.cc域名
AUTH_REDIS_SERVER = "127.0.0.1"
AUTH_REDIS_PORT = 6379
AUTH_REDIS_PASSWORD = ""
AUTH_UPDATE_INTERVAL = 2                    # 更新accountinfo表的最小时间间隔，单位秒

# 批发域名
PF_ROOT_HOST_NAME = "http://pftest.senguo.cc"