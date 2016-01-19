#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web
import json
import os.path as osp
import pluricent

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        fp = osp.join(osp.split(__file__)[0], 'stats.json')
        session = pluricent.create_session('/tmp/example.db')
        studies = pluricent.studies(session)
        j = json.load(open(fp))
        self.write('''<html><head></head>
         <body>
         Total disk usage : %s<br>
         Studies : %s (%s)<br>

         </body></html>'''%(j['total_diskusage'], str(studies), len(studies)))

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8889)
    tornado.ioloop.IOLoop.current().start()
