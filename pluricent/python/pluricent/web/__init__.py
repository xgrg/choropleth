import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import settings

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        username = self.current_user[1:-1]
        self.render("html/index.html", username = username)

class ExploreHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        username = self.current_user[1:-1]
        import pluricent as pl
        import os.path as osp
        import json
        warning = ''
        default = True

        # Retrieving studies from the database
        fn = osp.join(osp.dirname(pl.__file__), '..', '..', 'pluricent.db')
        assert(osp.isfile(fn))
        s = pl.create_session(fn)
        studies = pl.studies(s)

        if 'study' in self.request.arguments:
           # Study selected: displaying more info
           study = self.get_argument('study')
           if study in studies:

              self.write('hey')
              return
           else:
              warning = 'invalid study'
              default = True

        if default:
           # Welcome page for study selection
           studies = json.dumps(studies)
           self.render("html/explore.html", username = username, studies = studies, warning = warning)


class SysDiagHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        username = self.current_user[1:-1]
        import json
        import os.path as osp
        from datetime import datetime
        import dateutil.parser
        results = json.load(open(osp.join(settings.STATIC_PATH, 'json', 'sysdiag.json')))
        d = dateutil.parser.parse(results['last_checked'])
        results['last_checked'] = d.strftime('%Y-%m-%d %H:%M:%S')
        for k,v in results.items():
            if not v in [False, True]: continue
            results[k] = {False: "danger", True: "success"}[v]
        print results
        self.render("html/sysdiag.html", username = username, **results)

class AuthLoginHandler(BaseHandler):
    def get(self):
        try:
            errormessage = self.get_argument("error")
        except:
            errormessage = ""
        self.render("html/login.html", errormessage = errormessage)

    def check_permission(self, password, username):
        if username == "admin" and password == "admin":
            return True
        return False

    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        auth = self.check_permission(password, username)
        if auth:
            self.set_current_user(username)
            self.redirect(self.get_argument("next", u"/"))
        else:
            error_msg = u"?error=" + tornado.escape.url_escape("Login incorrect")
            self.redirect(u"/auth/login/" + error_msg)

    def set_current_user(self, user):
        if user:
            self.set_secure_cookie("user", tornado.escape.json_encode(user))
        else:
            self.clear_cookie("user")

class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", "/"))

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/auth/login/", AuthLoginHandler),
            (r"/auth/logout/", AuthLogoutHandler),
            (r"/sysdiag/", SysDiagHandler),
            (r"/explore/", ExploreHandler),
        ]
        s = {
            "template_path":settings.TEMPLATE_PATH,
            "static_path":settings.STATIC_PATH,
            "debug":settings.DEBUG,
            "cookie_secret": settings.COOKIE_SECRET,
            "login_url": "/auth/login/"
        }
        tornado.web.Application.__init__(self, handlers, autoescape=None, **s)

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
