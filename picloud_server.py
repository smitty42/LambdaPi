import os
import time
import json
import base64

import cloud

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options

port = 8888
os.system('''kill -9 `netstat -nap tcp |
            grep %s |
            awk '{{split ($7, a, "/"); print a[1]}}'`'''%port)
define("port", default=port, help="run on the given port", type=int)

class PycloudMiddleman(tornado.web.RequestHandler):
    def get(s):
        sub = s.get_argument('substring')
        sub = base64.b64decode(str(sub))
        return s.write(str(sub))

def read_picloud_file():
    start = time.time()
    picloud_file = cloud.bucket.getf('pi_parts000', prefix='classB')
    pi = picloud_file.read()
    end = time.time()
    return end - start

def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/search", PycloudMiddleman),
        ],
    )
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
