#!/usr/bin/env python
import os.path

import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options
from tornado import template

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "public","templates"),
            static_path=os.path.join(os.path.dirname(__file__), "public","static"),
            debug=True,
            autoescape=None
            )
        handlers = [
            (r"/", MainHandler),
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': settings.get('static_path')}),
        ]
        
        tornado.web.Application.__init__(self, handlers, **settings)

main_menu = ({"link_name":"Home"},{"link_name":"b"},{"link_name":"c"})
        
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        categories = main_menu
        categories[0]["active"]=True
        self.render(
            "index.htm",
            menulinks = categories,
            header_text = "Welcome to the Dungeon Keep!",
            footer_text = "For more information, please email us at <a href=\"mailto:mehmety@gmail.com\">mehmety@gmail.com</a>.",
        )


def main():
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
	main()
