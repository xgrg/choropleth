from state_machine import AnimSignal, ChangeSignal, FovSignal, Signal
from Queue import Queue

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

class Universe(dict):

   def __init__(self):
      self.changes = {}
      self.is_running = False
      self.fov = {}
      self.actions = Queue()
      self.model_changed = ChangeSignal()
      self.fov_changed = FovSignal()
      self.pending_print = Signal()
      self.apply_prints = Signal()
      self.animstate_changed = AnimSignal()

   def get_objects(self):
       '''Returns a list of objects existing in the current model.'''
       objects = set()
       for name, obj in self.items():
         for k, att in obj.__dict__.items():
             if isinstance(att, Action):
                 for cond, cons in att:
                     if cond:
                         objects.add(name)
       return objects

   def get_actions(self, obj):
       '''Returns a list of objects existing in the current model.'''
       actions = set()
       for k, att in self[obj].__dict__.items():
             if isinstance(att, Action):
                 for cond, cons in att:
                     if cond:
                         actions.add(k)
       return actions

   def add_action(self, action):
      self.actions.put(action)
      if not self.is_running:
         self.update_model()

   def __setitem__(self, key, value):
      assert(key not in self)
      print 'added object'
      self.changes.setdefault(key, {}).update({'@added': None})
      if isinstance(value, Viewer):
          self.fov[key] = value.get('visible', [])
      super(Universe, self).__setitem__(key, value)

   def __get_sprites_infos__(self, visible):
       ''' Returns image, position and zorder of a given sprite to be \
        sent to client '''
       item = {}
       for each in visible:
           image = self[each]['image']
           pos =  self[each]['position']
           z = self[each]['zorder']
           item[each] = {'image': image, 'x': pos[0], 'y': pos[1], 'z':z }
           if len(pos) == 4:
               print 'image', image
               item[each].update({'w':pos[2], 'h':pos[3]})
           if isinstance(self[each], Animated):
               f = self[each]['frame']
               running = self[each]['running']
               fps = self[each]['fps']
               framecount = self[each]['framecount']
               item[each].update({'frame':f, 'running':running, 'fps': fps, 'framecount': framecount})
       return item

   def apply_changes(self):
       import json
       for k,v in self.changes.items():
           if isinstance(self[k], Timer) and 'running' in v:
               if v['running'][0] is None:
                   continue
               if v['running'][1]:
                   self[k].thread.start()
               else:
                   self[k].thread.cancel()
           elif isinstance(self[k], Viewer) and 'visible' in v:
                 fovadded = {}
                 fovremoved = {}
                 print 'visible change'
                 visible = v['visible'][1]
                 item = self.__get_sprites_infos__(visible)

                 res = __diff_json__(self.fov[k], item)
                 fovadded[k], fovremoved[k] = res
                 self.fov[k] = item
                 self.fov_changed(json.dumps([fovadded, fovremoved]))

           elif isinstance(self[k], Visual) and \
                ('position' in v or 'image' in v):
               print 'visual change'
               fovadded = {}
               fovremoved = {}
               for viewer, fov in self.fov.items():
                   if k in fov:
                       visible = self[viewer]['visible']
                       item = self.__get_sprites_infos__(visible)
                       res = __diff_json__(self.fov[obj], item)
                       fovadded[viewer], fovremoved[viewer] = res
                       self.fov[viewer] = item
               print fovadded, fovremoved
               self.fov_changed(json.dumps([fovadded, fovremoved]))


       self.apply_prints()
       self.changes = {}

   def update_model(self, verbose=True):
      self.is_running = True
      while not self.actions.empty():
         item = self.actions.get()
         if verbose:
            print 'Firing action', item
         obj, act = item.split(',')
         getattr(self[obj], act).__call__()
         self.apply_changes()
      self.is_running = False



u = Universe()

class Condition:
   def __init__(self, rule):
      self.check = rule

   def __bool__(self):
      return self.check()
   __nonzero__ = __bool__

class Consequence:
    def __init__(self, f):
        self.f = f

    def __call__(self):
        self.f()

class Action(list):
   def __init__(self, cond, cons):
      self.append((cond, cons))

   def __call__(self):

      last_changes = u.changes
      while True:
        for conditions, consequences in self:
           print 'Checking conditions', conditions
           if conditions:
               print '* Conditions', conditions,'are satisfied...'
               consequences()

        first_iter = False

        last_changes = __diff_json__(last_changes, u.changes )[0]
        if len(last_changes) != 0:
            print 'looping again', u.changes
        else:
            break

      u.apply_changes()



class Object(dict):
   def __init__(self, name, properties={}):
      assert(name not in u)
      self.name = name
      for i,j in properties.items():
         self[i] = j
      u[name] = self

   def __getitem__(self, key):
       return super(Object, self).__getitem__(key)

   def __setitem__(self, key, value):
       if self.get(key, None) != value and key not in u.changes.get(self.name, {}):
           print 'change', self.name, key, value
           u.changes.setdefault(self.name, {}).update({key : (self.get(key), value)})
           super(Object, self).__setitem__(key, value)

class Viewer(Object):
   def __init__(self, name, properties={}):
      Object.__init__(self, name, properties)
      self['visible'] = []

   def set_field_of_view(self, fov):
      self['visible'] = fov

   def no_longer_sees(self, fov):
      if fov in self['visible']:
          oldfov = self['visible']
          self['visible'].remove(fov)
          u.changes.setdefault(self.name, {}).update({'visible': (oldfov, self['visible'])})

   def now_sees(self, fov, nothing_else=True):
      if nothing_else:
          self['visible'] = fov
      else:
          changed = False
          oldfov = self['visible']
          if isinstance(fov, list):
              l = [e for e in fov if e not in self['visible']]
              if len(l) != 0:
                  changed = True
              self['visible'].extend(l)
          elif isinstance(fov, str) and fov not in self['visible']:
              changed = True
              self['visible'].append(fov)
          if changed:
              u.changes.setdefault(self.name, {}).update({'visible': (oldfov, self['visible'])})

class Visual(Object):
   def __init__(self, name, image, position=[0,0,0,0], zorder=1, properties={}):
      import os
      fn = os.path.join(os.path.dirname(__file__), 'data', '%s.png'%image)
      assert(os.path.isfile(fn))
      properties['image'] = image
      properties['position'] = position
      properties['zorder'] = zorder
      Object.__init__(self, name, properties)

class Animated(Visual):
    def __init__(self, frame=0, framecount=1, fps=5, **kwargs):
      kwargs.setdefault('properties', {})
      kwargs['properties']['frame'] = frame
      kwargs['properties']['running'] = False
      kwargs['properties']['framecount'] = framecount
      kwargs['properties']['fps'] = fps
      Visual.__init__(self, **kwargs )
      self.state_changed = Signal()
      self.state_changed.connect(u.animstate_changed)

    def start(self):
      self['running'] = True
      self.state_changed('%s,true'%self.name)

    def stop(self):
      self['running'] = False
      self.state_changed('%s,false'%self.name)


class Player(Viewer):
   def __init__(self, name, properties={}):
      Viewer.__init__(self, name, properties)

class Timer(Object):
   def _start_(self):
       self['running'] = True
       self._tick_()

   def _stop_(self):
       self['running'] = False

   def _tick_(self, verbose=True):
       import threading
       u.changes.setdefault(self.name, {}).update({'running': (True, True)})
       self.thread = threading.Timer(self['interval'], self.tick)

       print "  Running a thread (either START or periodic TICK) with action"
       print '     timer is', self.thread
       if not self['periodic']:
           if verbose:
               print '   this is not a periodic one, sending \
                       STOP action and popping out timer', self.timers[obj]
           assert(self['running'])
           del self.thread
           delattr(self, 'thread')
           u.action_added('%s,stop'%self.name)

   def __init__(self, name, interval=1, periodic=False, properties={}):
      properties['running'] = False
      properties['interval'] = interval
      properties['periodic'] = periodic
      self.start = Action(True, self._start_)
      self.stop = Action(True, self._stop_)
      self.tick = Action(True, self._tick_)
      Object.__init__(self, name, properties)

   def __setattr__(self, attr, value):
      if isinstance(value, Action):
          old = getattr(self, attr, None)
          if not old is None:
              old.extend(value)
              object.__setattr__(self, attr, old)
          else:
              object.__setattr__(self, attr, value)
      else:
          object.__setattr__(self, attr, value)




class Title(Visual):
   def __init__(self, **kwargs):
      Visual.__init__(self, **kwargs)

class Room(Visual):
   def __init__(self, **kwargs):
      Visual.__init__(self, **kwargs)

class Internal(Object):
   def __init__(self, **kwargs):
      Object.__init__(self, **kwargs)

def toggle_explode():
    if u['explode']['running']:
        u['explode'].stop()
    else:
        u['explode'].start()

def create_world():


    t = Title(name = 'title', image = 'title', zorder=0, position =  [0,0,900,300])
    exp = Animated(name='explode', image='explode', zorder=1, position = [0,0], frame = 6, framecount=13)
    exp.click = Action(True, toggle_explode)

    r = Room(name = 'room', image = 'room', zorder=0, position =  [0,0])#,900,300])

    def is_title():
       return u['player']['visible'] == ['title']

    def is_room():
       return 'room' in u['player']['visible']

    def switch_to_room():
       u['player']['visible'] = ['room']
       u['timer'].start()

    def purr():
       print 'rrrRRrrrRRR...'
       if 'ronron' not in u['player']['visible']:
           u['player'].now_sees('ronron', nothing_else=False)
       else:
           u['player'].no_longer_sees('ronron')
       u.apply_changes()

    def print_internal_uptime():
        u['internal']['uptime'] += 1
        u.pending_print('%s'%u['internal']['uptime'])

    # can be useful to define a function to add an action
    # so that previously defined click() are not overwritten
    t.click = Action(Condition(is_title), switch_to_room)
    r.click = Action(Condition(is_room), purr)

    t = Timer(name = 'timer', interval=1, periodic=True)
    t.tick = Action(True, Consequence(print_internal_uptime))

    Visual(name = 'cat', image = 'cat', zorder=2,position = [200,110]) #,151,174])
    Visual(name = 'pouf', image = 'pouf',  position = [10,170]) #,160,99])
    Visual(name = 'lampe', image = 'lamp', position = [0,0]) #,79,79])
    Visual(name = 'porte', image = 'door1', position = [700,60,177,233])
    Visual(name = 'fenetre', image = 'window', position = [470,30,223,150])
    Visual(name = 'ventilateur', image = 'fan', position = [350,130,119,148])
    Visual(name = 'ronron', image = 'ronron', zorder=1, position = [220,110,122,30])

    Object(name = 'internal', properties={'uptime':0})

    def uptime(value):
        def res():
            return u['internal']['uptime']==value
        return res

    def show(item):
        def res():
            u['player'].now_sees(item, nothing_else=False)
            u.apply_changes()
        return res



    t.tick = Action(Condition(uptime(2)), show('cat'))
    t.tick = Action(Condition(uptime(4)), show('ventilateur'))
    t.tick = Action(Condition(uptime(6)), show('pouf'))
    t.tick = Action(Condition(uptime(8)), show('lampe'))
    t.tick = Action(Condition(uptime(10)), show(['porte', 'fenetre']))


    p = Player(name = 'player')
    p['location'] = 'home'
    u.apply_changes()
    u['player']['visible'] = ['explode','title']






if __name__ == '__main__':
    create_world()
