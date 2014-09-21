
from tornado import web, ioloop, websocket
from server import IndexHandler, LongPollingHandler, TokenHandler, TestHandler
import os, json
from Queue import Queue
from sig import Signal

import state_machine as sm


class TornadoServer(web.Application):
   def __init__(self, engine=None):
      self.engine = Engine()

   def start_thread(self):
      web.Application.__init__(self, handlers = [web.url(r'/', IndexHandler, kwargs={'engine':self.engine}),
                                             web.url(r'/list_tokens', TokenHandler, kwargs={'engine':self.engine}),
                                             web.url(r'/websocket', TestHandler, name='ws', kwargs={'engine':self.engine})],
                                             static_path = os.path.dirname(os.path.abspath(__file__)),
                                             autoescape = None)
      self.listen(8000)
      ioloop.IOLoop.instance().start()

class DialogSignal(Signal):
   def __call__(self, data=''):
      Signal.__call__(self, 'dialog@' + data)

class Engine():
   def __init__(self):
      self.actions = Queue()
      self.print_buffer = DialogSignal()
      self.is_running = False
      self.pending_prints = set()

   def load_model(self, fp):
      self.model = sm.Model(open(fp))
      self.model.action_added.connect(self.add_action)
      self.model.pending_print.connect(self.add_pending_print)

   def load_rules(self, fp):
      self.rules = json.load(open(fp))

   def add_action(self, action):
      self.actions.put(action)
      if not self.is_running:
         self.update_model()

   def add_pending_print(self, data):
      self.pending_prints.add(data)

   def update_model(self, verbose=True):
      self.is_running = True
      while not self.actions.empty():
         item = self.actions.get()
         if verbose:
            print 'Firing action', item
         obj, act = item.split(',')
         self.apply_rules((obj, act))
         self.apply_changes()
         self.apply_prints()
      self.is_running = False

   def apply_prints(self):
      while self.pending_prints:
         item = self.pending_prints.pop()
         self.print_buffer(str(item))

   def apply_changes(self, verbose=True):
      changes = 0
      if verbose:
         print '(applying following changes :', self.model.pending_changes,')'
      for obj, v in self.model.pending_changes.items():
         for prop, val in v.items():
            self.model.apply_change(obj, prop, val)
            changes = changes + 1
            if 'viewer' in self.model[obj].get('types', []) and prop == 'visible':
              item = {}
              for each in self.model[obj].get_property('visible'):
                 print each, self.model[each]
                 image = self.model[each].get_property('image')
                 pos =  self.model[each].get_property('position')
                 item[each] = {'image': image, 'x': pos[0], 'y': pos[1], 'w': pos[2], 'h': pos[3]}
              self.model.fov[obj] = item
              self.model.fov_changed(json.dumps(self.model.fov))
              if verbose:
                 print 'FOV CHANGED', self.model.fov
      if verbose:
         print '%s changes'%changes


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
   server = TornadoServer()
   server.engine.load_model('/tmp/model.json')
   server.engine.load_rules('/tmp/rules.json')
   server.engine.apply_rules()
   server.start_thread()
