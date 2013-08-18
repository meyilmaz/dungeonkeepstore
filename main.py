#!/usr/bin/env python
import os.path
import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options
from tornado import template

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if user_json != None:
            user = tornado.escape.json_decode(user_json)
        else: 
            user = None
        return user

    def get_menu(self):
        user = self.get_current_user()
        categories = main_menu
        if user:
            categories = auth_menu
            categories[-1]["link_name"] = user[u'email']
            categories[-1]["dropdown"] = ({"link_name":"Logout","href":"/logout"},)
            categories[-1]["class"]= "active dropdown"
        else:
            categories = main_menu
        return categories
    
class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "public","templates"),
            static_path=os.path.join(os.path.dirname(__file__), "public","static"),
            debug=True,
            cookie_secret="32oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            login_url="/login",
            xsrf_cookies = True,
            autoescape=None
            )
        handlers = [
            (r"/login",GoogleLoginHandler),
            (r"/home",HomeHandler),
            (r"/logout",LogoutHandler),
            (r"/", MainHandler),
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': settings.get('static_path')}),
        ]
        
        tornado.web.Application.__init__(self, handlers, **settings)

main_menu = ({"link_name":"Login","auth_required":False,"href":"/login"},)
auth_menu = ({"link_name":"b","auth_required":True,"in":"pull-left"},{"link_name":"c","class":"stage-right","in":"pull-left"},{"link_name":"Login","auth_required":False,"href":"/login"})
class GoogleLoginHandler(BaseHandler,
                         tornado.auth.GoogleMixin):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("openid.mode", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.authenticate_redirect()
            
    def _on_auth(self, user):
        if not user:
            self.send_error(500)
        self.set_secure_cookie("user", tornado.escape.json_encode(user))
        self.redirect("/home")

class MainHandler(BaseHandler):
    def get(self):
        self.set_header("Cache-control", "no-cache")
        self.render(
          "index.htm",
          menulinks = self.get_menu(),
          auth = self.get_current_user()
        )

   

class HomeHandler(BaseHandler):
    def get(self):
        self.render(
          "home.htm",
          menulinks = self.get_menu(),
          auth = self.get_current_user()
        )
    
class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", "/"))
    
    
def main():
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
	main()
