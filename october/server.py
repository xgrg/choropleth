import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado import gen

class IndexHandler(tornado.web.RequestHandler):
  def initialize(self):
    pass

  def get(self):
    self.render("index.html")

  def post(self):
    pass



class TokenHandler(tornado.web.RequestHandler):
    def initialize(self):
        pass

    def get(self):
       pass




class LongPollingHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self):
       pass


class TestHandler(tornado.websocket.WebSocketHandler):
  def initialize(self):
    self.clients = []

  def open(self, *args):
    print("open", "WebSocketChatHandler")
    self.clients.append(self)

  def on_message(self, message):
      self.write('ok')

  def on_close(self):
     self.clients.remove(self)

  def write(self, data):
      for each in self.clients:
          self.write(data)
