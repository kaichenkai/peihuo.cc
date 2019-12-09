import redis as _redis

_r = _redis.StrictRedis(
    host="r-bp16b4b9b1bf3854744.redis.rds.aliyuncs.com",
    port="6379",
    password="WRfnzrQTc813CUiG",
    db=100,
    decode_responses=True)

_settings_dict = _r.hgetall("settings_ph_production")

for _key, _value in _settings_dict.items():
    exec("%s = '''%s'''" % (_key, _value))
