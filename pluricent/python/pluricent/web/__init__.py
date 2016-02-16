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
        import pluricent as pl
        import os.path as osp
        fn = osp.abspath(pl.global_settings()['database'])
        ds = osp.dirname(fn)
        args = {'danger':'', 'datasource':'', 'database':fn}
        if osp.isfile(fn):
           args.update({'datasource': ds, 'database': fn})
        else:
           args['danger'] = 'The database %s is missing'%fn
        self.render("html/index.html", username = username, **args)

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
        p = pl.Pluricent(pl.global_settings()['database'])
        studies = p.studies()

        if 'study' in self.request.arguments:
           # Study selected: displaying more info
           study = self.get_argument('study')
           if study in studies:
              images = p.t1images(study)
              print study, images
              d = []
              for each in images:
                 d.append({'subject': each.subject.identifier,
                     'path': each.path,
                     'id': each.id})
              self.render("html/explore_study.html", username = username, study_name = study, warning = warning, images=d)
              return
           else:
              warning = 'invalid study'
              default = True

        if default:
           # Welcome page for study selection
           studies = json.dumps(studies)
           self.render("html/explore.html", username = username, studies = studies, warning = warning)


def __collect_tests__():
    import inspect, os, importlib, os.path as osp
    from pluricent.web import settings
    d = osp.join(osp.abspath(settings.DIRNAME), 'bin')
    print d
    os.chdir(d)
    m = importlib.import_module('tests')
    test_functions = [e for e in inspect.getmembers(m, inspect.isfunction) if e[0].startswith('test')]
    return test_functions

class SysDiagHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        username = self.current_user[1:-1]
        import json
        import os.path as osp
        from datetime import datetime
        import dateutil.parser
        j = osp.join(settings.STATIC_PATH, 'json', 'sysdiag.json')

        if osp.isfile(j):
           # === sysdiag.json exists ===
           results = json.load(open(j))
           d = dateutil.parser.parse(results['last_checked'])
           results['last_checked'] = d.strftime('%Y-%m-%d %H:%M:%S')
           results['error'] = ''
           for k,v in results.items():
               if not v in [False, True, None]: continue
               results[k] = {False: "danger", True: "success", None:''}[v]
           print results

        else:
           # === sysdiag.json missing ===
           results = {}
           # brand new results
           f = __collect_tests__()
           for fname, _ in f:
              results[fname] = False
           results['error'] = 'json missing'
           results['last_checked'] = ''
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
