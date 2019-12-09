#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys
import tornado
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../")))
import multiprocessing
from dal.db_configs import DBSession
from dal import models
from tornado.options import options, define


define("action", default="", help="")


# 生成中文汉字首字母
def generating_acronym():

    session = DBSession()

    firm_list = session.query(models.Firm)\
                       .filter(models.Firm.status == 0)\
                       .all()
    goods_list = session.query(models.Goods)\
                        .filter(models.Goods.status == 0)\
                        .all()
    for firm in firm_list:
        firm.name = firm.name
    for goods in goods_list:
        goods.name = goods.name

    session.commit()
    session.close()
    return "success"


db_dict_action = {
    'generating_acronym': generating_acronym,
}


def main():
    tornado.options.parse_command_line()
    action = options.action
    g = multiprocessing.Process(name=action, target=db_dict_action[action])
    g.start()
    g.join()


if __name__ == "__main__":
    main()
