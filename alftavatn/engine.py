
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
      print 'apply prints'
      while self.pending_prints:
         item = self.pending_prints.pop()
         self.print_buffer(str(item))

   def apply_changes(self, verbose=True):
      def __diff_json__(j1, j2):
         added = []
         removed = []
         for k in j2:
            if not k in j1:
               added.append(k)
            elif j1[k] != j2[k]:
               removed.append(k)
               added.append(k)
         for k in j1:
            if not k in j2:
               removed.append(k)
         return added, removed


      changes = 0
      if verbose:
         print '(applying following changes :', self.model.pending_changes,')'

      fovadded = {}
      fovremoved = {}

      for obj, v in self.model.pending_changes.items():
         for prop, val in v.items():
            self.model.apply_change(obj, prop, val)
            changes = changes + 1
            if ('viewer' in self.model[obj].get('types', []) and prop == 'visible') or prop == 'position':
              if prop == 'position':
                 viewers = []
                 for v in self.model.fov:
                    if obj in self.model.fov[v]:
                       viewers.append(v)

                 for viewer in viewers:
                    item = {}
                    visible = self.model[viewer].get_property('visible')
                    for each in visible:
                       print each, self.model[each]
                       image = self.model[each].get_property('image')
                       pos =  self.model[each].get_property('position')
                       item[each] = {'image': image, 'x': pos[0], 'y': pos[1], 'w': pos[2], 'h': pos[3]}
                    res = __diff_json__(self.model.fov[viewer], item)
                    fovadded[viewer] = res[0]
                    fovremoved[viewer] = res[1]
                    self.model.fov[viewer] = item
              else:
                 visible = self.model[obj].get_property('visible')
                 item = {}
                 for each in visible:
                    print each, self.model[each]
                    image = self.model[each].get_property('image')
                    pos =  self.model[each].get_property('position')
                    item[each] = {'image': image, 'x': pos[0], 'y': pos[1], 'w': pos[2], 'h': pos[3]}

                 res = __diff_json__(self.model.fov[obj], item)
                 fovadded[obj] = res[0]
                 fovremoved[obj] = res[1]
                 self.model.fov[obj] = item

              self.model.fov_changed(json.dumps([fovadded, fovremoved]))
              if verbose:
                 print 'FOV CHANGED', 'added', fovadded, 'removed', fovremoved
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

def create_files(modelfile, rulesfile):
   ''' A simple function that makes the files needed for running everything.

   Make copies of model and rules in /tmp in case they do not exist.'''

   for fp, source in zip(['/tmp/model.json', '/tmp/rules.json'], [modelfile, rulesfile]):
      if not os.path.exists(fp):
         print 'Copying', source, 'to', fp
         os.system('cp %s %s'%(source, fp))

if __name__ == '__main__':
   #import argparse
   #parser = argparse.ArgumentParser(description='Alftavatn engine')
   #parser.add_argument('-m','--model', help='Model file', required=True)
   #parser.add_argument('-r','--rules', help='Rules file', required=True)
   #args = vars(parser.parse_args())
   # Make files (model, rules) ready for execution
   #create_files(args['model'], args['rules'])

   # Where everything begins
   server = TornadoServer()
   #server.engine.load_model('/tmp/model.json')
   #server.engine.load_rules('/tmp/rules.json')
   #server.engine.apply_rules()
   import model
   model.create_world()
   server.engine.model = model.u
   server.engine.model.pending_print.connect(server.engine.add_pending_print)
   server.engine.model.apply_prints.connect(server.engine.apply_prints)
   server.engine.model.apply_changes()
   server.start_thread()
