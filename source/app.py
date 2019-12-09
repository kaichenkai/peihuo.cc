#! /usr/bin/env python3
import time
import signal
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.wsgi
from tornado.options import options, define
import os,sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../")))

import dal.models as models
import dal.models_statistics as models_statistics
from urls import handlers
from settings import COOKIE_SECRET

define("debug", default=0, help="debug mode: 1 to open, 0 to close")
define("port", default=8989, help="port, defualt: 8989")

settings = {
    "cookie_secret": COOKIE_SECRET,
    "xsrf_cookies": False,
    "template_path": os.path.join(os.path.dirname(__file__), 'template'),
}

class Application(tornado.web.Application):
    def __init__(self):
        settings["debug"] = bool(options.debug)
        super().__init__(handlers, **settings)


def sig_handler(sig, frame):
    """信号处理函数
    """
    print('\nReceived interrupt signal: %s' % sig)
    tornado.ioloop.IOLoop.instance().add_callback(shutdown)


def shutdown():
    """进程关闭处理
    """
    print('Stopping http server, please wait...')
    # 停止接受Client连接
    application.stop()

    io_loop = tornado.ioloop.IOLoop.instance()
    # 设置最长等待强制结束时间
    deadline = time.time() + 5

    def stop_loop():
        now = time.time()
        if now < deadline:
            io_loop.add_timeout(now + 1, stop_loop)
        else:
            io_loop.stop()
    stop_loop()


if __name__ == "__main__":
    # 等待supervisor发送进程结束信号
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    models.init_db_data()
    models_statistics.init_db_data()
    tornado.options.parse_command_line()
    app = Application()
    application = tornado.httpserver.HTTPServer(app, xheaders=True)
    application.listen(options.port)
    if options.debug==1:
        debug_str = "in debug mode"
    elif options.debug==2:
        print("run test success, exiting...")
        sys.exit(0)
    else:
        debug_str = "in production mode"
    print("running peihuo.senguo.cc {0} @ {1}...".format(debug_str,options.port))
    tornado.ioloop.IOLoop.instance().start()
