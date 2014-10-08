#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, json
from alftavatn import *
from sig import Signal


class ChangeSignal(Signal):
    def __call__(self, data):
       Signal.__call__(self, 'change@' + data)

class FovSignal(Signal):
    def __call__(self, data):
       Signal.__call__(self, 'fov@' + data)

class Object(dict):
    def __init__(self, name, d):
       dict.__init__(self, d)
       self.name = name
       self.pending_changes = {}

    def add_pending_change(self, prop, val, verbose=True):
       '''Returns False if the change has already been marked at a previous
       round, True if it is a new change '''
       if verbose:
          print '\n~~~~ object %s has pending change (%s -> %s) ~~~~'%(self.name, prop, val)
          print '(pending changes so far for object %s : '%self.name, self.pending_changes, ')'
       assert(prop not in self.pending_changes or self.pending_changes[prop] == val)
       if prop in self.pending_changes and val == self.pending_changes[prop]:
          return False
       else:
          self.pending_changes[prop] = val
          return True

    def apply_change(self, prop, val):
       assert(prop in self.pending_changes)
       assert(val == self.pending_changes[prop])
       self[prop] = val
       self.pending_changes.pop(prop)

    def get_property(self, prop):
       return self.pending_changes.get(prop, self[prop])

    def get(self, prop, default):
       if prop in self or prop in self.pending_changes:
          return self.get_property(prop)
       else:
          return default


class Model(dict):
    def __init__(self, jsonfile):
        self.timers = {}

        j = json.load(jsonfile)
        for each in j:
           self[each] = Object(each, j[each])

        self.action_added = Signal()
        self.model_changed = ChangeSignal()
        self.fov_changed = FovSignal()
        self.pending_print = Signal()
        #self.initialize()

    def reset_pending_changes(self, verbose=True):
        if verbose:
           print 'Pending changes reset...'
        for each in getattr(self, 'pending_changes', {}):
           self[each].pending_changes = {}
        self.pending_changes = {}

    def initialize(self):
        self.changes = -1
        self.reset_pending_changes()
        self.has_changed = False
        self.iter_nb = 0
        self.processed_rules = {}

        # Initializing field-of-views
        if not hasattr(self, 'fov'):
           viewers = [e for e in self if 'viewer' in self[e].get('types',[])]
           self.fov = dict( [(i, self[i].get('visible', [])) for i in viewers])
           self.fov_changed(json.dumps([self.fov, {}]))
           print 'fov_changed', self.fov

    def get_canvas_cards(self):
       viewers = [e for e in self if 'viewer' in self[e].get('types',[])]
       fov = dict( [(i, self[i].get('visible',[])) for i in viewers])
       d = {}
       for v in fov:
         for each in fov[v]:
            if 'image' in self[each]:
               d.setdefault(v, []).append('%s.%s'%(each, self[each]['image']))
       fov = d.get('player', [])
       output1 = ''
       for each in fov:
           k = each.split('.')
           item = '<b>' + k[0] + '</b><br>'
           item = item + '<img src="static/data/%s.png" /><br>'%k[1]
           output1 = output1 + '<div class="item"><div class="tweet-wrapper"><span class="text">' + item + '</span></div></div>'
       return output1

    def get_model_cards(self):
       output = ''
       for k, obj in self.items():
           item = '<b>' + k + '</b><br>'
           for p in obj:
               if not p in ['geometry', 'position']:
                   item = item + ' &nbsp;&nbsp;&nbsp;' + p + ' = ' + str(obj[p]) + '<br>'
           output = output + '<div class="item"><div class="tweet-wrapper"><span class="text">' + item + '</span></div></div>'
       return output

    def add_pending_change(self, obj, prop, val):
        print ' (all pendings changes so far before adding %s.%s -> %s :'%(obj, prop, val), self.pending_changes,
        assert(obj not in self.pending_changes \
              or (prop in self.pending_changes[obj] and val == self.pending_changes[obj][prop]) \
              or prop not in self.pending_changes)
        self.pending_changes.setdefault(obj, {})
        self.pending_changes[obj].setdefault(prop, {})
        self.pending_changes[obj][prop] = val

        if self[obj].add_pending_change(prop, val):
           self.changes = self.changes + 1

    def apply_change(self, obj, prop, val, verbose=True):
        #self.changes = self.changes + 1
        if verbose:
            print '    => apply change to %s.%s'%(obj, prop), '(', self[obj][prop], '->', val, ')'
        self[obj].apply_change(prop, val)

        self.has_changed = True
        self.model_changed(json.dumps(self))

    def iterate(self, rules, action):

        def tick(obj, model):
           print '*** Thread just ended for object', model[obj], 'with timer', self.timers[obj]
           print self.timers[obj][0].is_alive()
           self.timers[obj][1] = False
           self.action_added('%s,TICK'%obj)
           if model[obj].get_property('periodic') == 'False':
               print '   this is not a periodic one, sending STOP action and popping out timer', self.timers[obj]
               assert(model[obj].get_property('running') == 'True')
               self.timers.pop(obj)
               self.action_added('%s,STOP'%obj)


        self.iter_nb = self.iter_nb + 1
        self.changes = 0

        for conditions, implications in rules :
            conditionsAreSatisfied = True

            for c in conditions:
               if len(c) == 3:
                  (obj, prop, val) = c
                  if obj.startswith('ANY '):
                      t = obj[4:]
                      objects_satisfying = []
                      for each in [o for o in self if 'types' in self[o] and t in self[o].get_property('types')]:
                          if self[each].get_property(prop) == val:
                              objects_satisfying.append(each)
                      if len(objects_satisfying) == 0:
                          conditionsAreSatisfied = False

                  elif obj.startswith('ALL '):
                      t = obj[4:]
                      for each in [o for o in self if 'types' in self[o] and t in self[o].get_property('types')]:
                          if self[each].get_property(prop) != val:
                              conditionsAreSatisfied = False

                  elif self[obj][prop] != val:
                     conditionsAreSatisfied = False

               elif len(c) == 2:
                  (obj, act) = c
                  assert(act.isupper())
                  if not action is None:
                    if (obj, act) != action :
                        conditionsAreSatisfied = False
                  else:
                    conditionsAreSatisfied = False

               else:
                  raise Exception('Condition should have 2 or 3 items (%s given)'%len(i))

            if conditionsAreSatisfied :
                print '* Conditions', conditions,'are satisfied... with action', action

                # If some action provided
                if not action is None :
                   if 'timer' in self[obj].get('types', []):
                       if action[1] == 'START' :
                         if self[action[0]].get_property('running') == 'False' :
                            self.add_pending_change(action[0], 'running', 'True')

                       if (action[1] == 'TICK' and self[action[0]].get_property('running') == 'True' \
                             and self[action[0]].get_property('periodic') == 'True') or action[1] == 'START':
                           import threading
                           if (action[1] == 'START' and not action[0] in self.timers) or (action[1] == 'TICK' and not self.timers[action[0]][1]):
                               print "  Running a thread (either START or periodic TICK) with action", action
                               self.timers[action[0]] = [threading.Timer(self[action[0]]['interval'], tick, args=[action[0], self]), True]
                               self.timers[action[0]][0].start()
                               print '     timers are', self.timers
                           else:
                               print "is alive", self.timers[action[0]][1]
                               print '     not running another thread for action', action
                               # second pass due to has_changed = True -> ignore it
                               pass

                       elif action[1] == 'STOP':
                           if self[action[0]]['running'] == 'True' :
                               self.add_pending_change(action[0], 'running', 'False')
                           if action[0] in self.timers:
                               self.timers[action[0]][0].cancel()
                               self.timers.pop(action[0])
                           else:
                               print '(timer', action[0], 'not found in', self.timers, ')'



                for i in implications :

                   if len(i) == 3:
                      (obj, prop, val) = i
                      if isinstance(val, basestring):
                          if val[0] == '@':
                             if val in self.processed_rules:
                                 continue
                             f = val
                             operations = parse_function(val)
                             val = solve_function(operations, self)
                             self.processed_rules[f] = val

                      if prop == 'PRINT':
                          self.pending_print(val)
                      else :
                         if not isinstance(self[obj].get_property(prop), type(val)):
                            print 'Rule "%s" is changing property "%s" from type "%s" to "%s" on object "%s"'%(i, prop, type(self[obj].get_property(prop)), type(val), obj)

                         if self[obj].get_property(prop) != val :
                             self.add_pending_change(obj, prop, val)

                   elif len(i) == 2:
                      (obj, act) = i
                      assert(act.isupper())
                      if i != list(action):
                         self.action_added("%s,%s"%(obj, act))

                   else:
                      raise Exception('Implication should have 2 or 3 items (%s given)'%len(i))


