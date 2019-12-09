# Copyright 2017 Sunmh
#
# some base log function for senguo
# 之后的就先用这个新的log文件
import os
import sys
import datetime

# 记录日志
# filename中有/，表示要创建文件夹。
# 日志的粒度,format_date----'%Y-%m-%d'
def log_msg(file, content, format_date=""):
    try:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "/opt/logs/peihuo/others"))
        if format_date:
            file = "%s/%s_%s.log" % (base_path, file, datetime.datetime.now().strftime(format_date))
        else:
            file = "%s/%s.log" % (base_path, file)
        file_path = os.path.dirname(file)
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        with open(file, "a") as f:
            f.write(content)
            f.write('\n')
    except:
        pass

# dict型日志形式解析
def log_msg_dict(file, content, format_date=""):
    msg_txt=""
    for key in content:
        msg_txt += str(key)+':'+str(content[key])+'\n'
    log_msg(file, msg_txt, format_date)
