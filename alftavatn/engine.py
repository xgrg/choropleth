
from tornado import web, ioloop, websocket
from server import IndexHandler, LongPollingHandler, TokenHandler, TestHandler
import os

import state_machine as sm


class TornadoServer(web.Application):
   def __init__(self, start=True, engine=None):
      web.Application.__init__(self, handlers = [web.url(r'/', IndexHandler),
                                             web.url(r'/poll', LongPollingHandler),
                                             web.url(r'/list_tokens', TokenHandler),
                                             web.url(r'/websocket', TestHandler, name='ws', kwargs={'engine':engine})],
                                             static_path = os.path.dirname(os.path.abspath(__file__)),
                                             autoescape = None)
      if start:
         self.start_thread()

   def start_thread(self):
      self.listen(8000)
      import threading, time
      # The tornado IO loop doesn't need to be started in the main thread
      # so let's start it in another thread:
      self.thread = threading.Thread(target=ioloop.IOLoop.instance().start)
      self.thread.daemon = True
      self.thread.start()


class Engine():
   def __init__(self):
      from Queue import Queue
      self.actions = Queue()

   def load_model(self, fp):
      self.model = sm.Model(open(fp))

   def load_rules(self, fp):
      import json
      self.rules = json.load(open(fp))

   def start_tornado(self):
      self.server = TornadoServer(start=True, engine=self)

   def get_server_signal(self, data):
      self.actions.put(data)

   def apply_rules (self, action = None) :

       self.model.initialize()
       prevchanges = False

       while self.model.changes != 0:
           self.model.iterate(self.rules, action)
           if self.model.changes != 0:
               print '(model has met %s changes during last iteration, going for another round)\n'%self.model.changes
               prevchanges = True
           elif prevchanges:
               print '(model has met 0 changes during last iteration, exiting loop)\n'

       if self.model.update_fov:
          d = {}
          for v in self.model.fov:
             for each in self.model.fov[v]:
                if 'image' in self.model[each]:
                   d.setdefault(v, []).append('%s.%s'%(each, self.model[each]['image']))

       for each in self.model.print_buffer:
         for client in self.clients:
            client.write_message(each)


def create_files():
   ''' A simple function that makes the files needed for running everything.

   Make copies of model and rules in /tmp in case they do not exist.'''

   homedir = os.path.dirname(os.path.abspath(__file__))
   modelfile = os.path.join(homedir, 'data', 'model.json')
   rulesfile = os.path.join(homedir, 'data', 'rules.json')

   for fp, source in zip(['/tmp/model.json', '/tmp/rules.json'], [modelfile, rulesfile]):
      if not os.path.exists(fp):
         os.system('cp %s %s'%(source, fp))


if __name__ == '__main__':
   # Make files (model, rules) ready for execution
   create_files()

   # Where everything begins
   e = Engine()
   e.load_model('/tmp/model.json')
   e.load_rules('/tmp/rules.json')
   e.start_tornado()

   while(True):
      if not e.actions.empty():
         item = e.actions.get()
         print 'ACTION', item
         obj, act = item.split(',')
         e.apply_rules((obj, act))
      else:
         e.apply_rules()
