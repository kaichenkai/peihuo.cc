import os

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (sessionmaker)
from sqlalchemy import create_engine
import redis as redis_db

import settings
from settings import (MYSQL_SERVER, MYSQL_DRIVER, DB_NAME, DB_STATISTIC_NAME,
                      DB_CHARSET, AUTH_REDIS_SERVER, AUTH_REDIS_PORT, AUTH_REDIS_PASSWORD)
from settings import (REDIS_SERVER, REDIS_PORT, REDIS_PASSWORD)

MYSQL_USERNAME = os.getenv('MYSQL_USER') or settings.MYSQL_USERNAME
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD') or settings.MYSQL_PASSWORD

# 数据库
engine = create_engine("mysql+{driver}://{username}:{password}@{server}/{database}?charset={charset}"
                       .format(driver=MYSQL_DRIVER,
                               username=MYSQL_USERNAME,
                               password=MYSQL_PASSWORD,
                               server=MYSQL_SERVER,
                               database=DB_NAME,
                               charset=DB_CHARSET),
                       pool_size=20,
                       max_overflow=100,
                       pool_recycle=7200,
                       echo=False)
engine.execute("SET NAMES {charset};".format(charset=DB_CHARSET))
MapBase = declarative_base(bind=engine)
DBSession = sessionmaker(bind=engine)

# 数据统计数据库
statistic_engine = create_engine("mysql+{driver}://{username}:{password}@{server}/{database}?charset={charset}"
                                 .format(driver=MYSQL_DRIVER,
                                         username=MYSQL_USERNAME,
                                         password=MYSQL_PASSWORD,
                                         server=MYSQL_SERVER,
                                         database=DB_STATISTIC_NAME,
                                         charset=DB_CHARSET),
                                 pool_size=20,
                                 max_overflow=100,
                                 pool_recycle=7200,
                                 echo=False)
statistic_engine.execute("SET NAMES {charset};".format(charset=DB_CHARSET))
statistic_DBSession = sessionmaker(bind=statistic_engine, expire_on_commit=False)
Statistic_MapBase = declarative_base(bind=statistic_engine)

# Redis缓存数据库
pool_db = redis_db.ConnectionPool(host=REDIS_SERVER, port=REDIS_PORT, password=REDIS_PASSWORD, db=4)
redis = redis_db.StrictRedis(connection_pool=pool_db)

# Redis缓存数据库
pool_db_pf = redis_db.ConnectionPool(host="172.16.0.1", port=6379, password="wHi#fg)65_er$2Yd", db=0)
pf_redis = redis_db.StrictRedis(connection_pool=pool_db_pf)

# passport.senguo.cc redis
auth_pool_db0 = redis_db.ConnectionPool(host=AUTH_REDIS_SERVER,
                                        port=AUTH_REDIS_PORT, password=AUTH_REDIS_PASSWORD, db=0)
auth_redis = redis_db.StrictRedis(connection_pool=auth_pool_db0)
