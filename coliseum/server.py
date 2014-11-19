import tornado.ioloop
import tornado.web
import tornado.websocket
import threading, os, string, json, time
from tornado import gen

class IndexHandler(tornado.web.RequestHandler):
  def initialize(self):
    pass

  def get(self):
    self.render("index.html")

  def post(self):
    pass



class TokenHandler(tornado.web.RequestHandler):
    def initialize(self, engine=None):
        pass

    def get(self):
       pass




class LongPollingHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self):
       pass

class TestHandler(tornado.websocket.WebSocketHandler):
  def initialize(self, engine):
    self.clients = []

  def open(self, *args):
    print("open", "WebSocketChatHandler")
    self.clients.append(self)

  def on_message(self, message):
     print message

  def on_close(self):
     self.clients.remove(self)

  def write(self, data):
      for each in self.clients:
          self.write_message(data)

if __name__ == '__main__':
    app = tornado.web.Application(handlers = [(r'/', IndexHandler), (r'/poll', LongPollingHandler), (r'/list_tokens', TokenHandler)],
            static_path = homedir, autoescape = None)

    app.listen(8000)
    tornado.ioloop.IOLoop.instance().start()

