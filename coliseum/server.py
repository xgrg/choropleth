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

class TestHandler(tornado.websocket.WebSocketHandler):
  def initialize(self):
    self.clients = []
    self.pot = 0
    self.pot2 = 3

  def _decay(self):
     self.pot = self.pot * 0.95
     self.pot2 = self.pot2 * 0.75

  def do_every (self, interval, worker_func, iterations = 0):
     if iterations != 1:
       threading.Timer (
         interval,
         self.do_every, [interval, worker_func, 0 if iterations == 0 else iterations-1]
       ).start ()

     worker_func ()


  def open(self, *args):
    print("open", "WebSocketChatHandler")
    self.clients.append(self)

  def on_message(self, message):
     print message
     res = message.split('@')
     if res[0] == 'DIALOG':
        self.pot = len(res[1])
        self.pot2 = len(res[1].split(' '))
        self.write(message)
        self.do_every(0.25, self._decay)
     elif res[0] == 'SENSE':
        print 'SENSE', res[1], res[2], getattr(self, res[2])
        self.write('SENSE@%s@%s'%(res[1], getattr(self, res[2])))

  def on_close(self):
     self.clients.remove(self)

  def write(self, data):
      for each in self.clients:
          self.write_message(data)


