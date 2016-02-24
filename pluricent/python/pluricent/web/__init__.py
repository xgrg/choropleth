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

class AnalyzeHandler(BaseHandler):
    @tornado.web.authenticated

    def post(self):
        import pluricent as pl
        import numpy as np
        import json
        from sqlalchemy import distinct
        structure = self.get_argument('id')
        print structure
        args = {}
        p = pl.Pluricent(pl.global_settings()['database'])

        structures = [str(e[0]) for e in p.session.query(distinct(pl.models.Measurement.structure)).all()]
        measurements = dict(p.session.query(pl.models.Subject.identifier, pl.models.Measurement.value)\
                       .join(pl.models.T1Image).join(pl.models.Measurement).filter(pl.models.Measurement.structure == structure).all())
        args['data'], args['labels'] = np.histogram(measurements.values())
        args = dict([(k, json.dumps([int(e) for e in v.tolist()])) for k,v in args.items()])
        args['structure'] = structure
        args['structures'] = structures
        args['measurements'] = measurements
        res = json.dumps(args)
        self.write(res)
        return None

    def get(self):
        username = self.current_user[1:-1]
        import pluricent as pl
        from sqlalchemy import distinct
        args = {}
        p = pl.Pluricent(pl.global_settings()['database'])
        structures = [str(e[0]) for e in p.session.query(distinct(pl.models.Measurement.structure)).all()]
        args['structures'] = structures
        self.render("html/analyze.html", username = username, **args)

class ExploreHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        import pluricent as pl
        from sqlalchemy import func, distinct
        import numpy as np
        import json
        args = {}
        p = pl.Pluricent(pl.global_settings()['database'])
        datatypes = [e[0] for e in p.session.query(distinct(pl.models.Processing.datatype)).all()]

        table = []
        headers = ['subject', 't1image']
        q = []
        q.append(dict(p.session.query(pl.models.Subject.identifier, func.count(pl.models.T1Image.path)).filter(pl.models.T1Image.subject_id == pl.models.Subject.id).group_by(pl.models.Subject.identifier).all()))
        for each in datatypes:
            headers.append(each)
            res = p.session.query(pl.models.Subject.identifier, func.count(pl.models.Processing.path)).join(pl.models.T1Image).filter(pl.models.Processing.input_id == pl.models.T1Image.id).filter(pl.models.T1Image.subject_id == pl.models.Subject.id).filter(pl.models.Processing.datatype==each).group_by(pl.models.Subject.identifier).all()
            q.append(dict(res))

        subjects = [e[0] for e in p.session.query(pl.models.Subject.identifier).all()]
        table.append(headers)
        for s in subjects:
            table.append([s])
            table[-1].extend([each.get(s, 0) for each in q])

        #print t1images
        args['images'] = table

        res = json.dumps(args)
        self.write(res)

        return None

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
            (r"/analyze/", AnalyzeHandler),
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
