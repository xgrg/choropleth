from tornado import web, ioloop, websocket
from server import IndexHandler, LongPollingHandler, TokenHandler, TestHandler
import os, json
from Queue import Queue


class TornadoServer(web.Application):
   def __init__(self):
      pass

   def start_thread(self):
      web.Application.__init__(self, handlers = [web.url(r'/', IndexHandler, kwargs={}),
                                             web.url(r'/list_tokens', TokenHandler, kwargs={}),
                                             web.url(r'/websocket', TestHandler, name='ws', kwargs={})],
                                             static_path = os.path.dirname(os.path.abspath(__file__)),
                                             autoescape = None)
      self.listen(8000)
      ioloop.IOLoop.instance().start()

if __name__ == '__main__':
   server = TornadoServer()
   server.start_thread()
