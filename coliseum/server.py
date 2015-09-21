import tornado.ioloop
import tornado.web
import tornado.websocket
import threading, os, string, json, time
from tornado import gen
import time
from threading import Thread, Timer

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


from model import Model

class TestHandler(tornado.websocket.WebSocketHandler):
  def initialize(self):
    self.clients = []
    self.model = Model()
    self.model.run()

  def open(self, *args):
    print("open", "WebSocketChatHandler")
    self.clients.append(self)

  def on_message(self, message):
     print message
     res = message.split('@')
     if res[0] == 'DIALOG':
         self.model.perceive(res[1])
         self.write(message)
     elif res[0] == 'SENSE':
        print 'SENSE', res[1], res[2], self.model.sense(res[2])
        self.write('SENSE@%s@%s'%(res[1], self.model.sense(res[2])))
     elif res[0] == 'CHECKMEM':
        self.write('CHECKMEM@%s'%str(self.model.mem.memory))

  def on_close(self):
     self.clients.remove(self)

  def write(self, data):
      for each in self.clients:
          self.write_message(data)


