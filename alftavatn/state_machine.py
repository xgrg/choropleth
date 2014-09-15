#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, json
from alftavatn import *
from sig import Signal

timers = {}

class Model(dict):
    def __init__(self, jsonfile):
        self.update(json.load(jsonfile))
        self.sig = Signal()

    def initialize(self):
        self.changes = -1
        self.has_changed = False
        self.iter_nb = 0
        self.processed_rules = {}
        self.print_buffer = []

#        # Stopping timers
#        for timer in [e for e in self if 'timer' in self[e].get('types', [])]:
#            if self[timer]['running'] == 'True':
#                self.apply_change(timer, 'running', 'False')
#        if self.changes != -1:
#            print 'stopped %s timers'%(self.changes + 1)
#            self.changes = -1

        # Initializing field-of-views
        viewers = [e for e in self if 'viewer' in self[e].get('types',[])]
        self.fov = dict( [(i, self[i].get('visible', [])) for i in viewers])
        self.update_fov = False

    def get_canvas_cards(self):
       viewers = [e for e in self if 'viewer' in self[e].get('types',[])]
       fov = dict( [(i, self[i].get('visible',[])) for i in viewers])
       d = {}
       for v in fov:
         for each in fov[v]:
            if 'image' in self[each]:
               d.setdefault(v, []).append('%s.%s'%(each, self[each]['image']))
       print d
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

    def apply_change(self, obj, prop, val, verbose=True):
        self.changes = self.changes + 1
        if verbose:
            print '    => apply change to %s.%s'%(obj, prop), '(', self[obj][prop], '->', val, ')'
        self[obj][prop] = val
        self.has_changed = True

    def iterate(self, rules, action):

        def tick(obj, model):
           print '*** Thread just ended for object', model[obj], 'with timer', timers[obj]
           os.system('echo "%s,%s" >> %s'%(obj, "TICK", actionsfile))
           if model[obj]['periodic'] == 'False':
               print '   this is not a periodic one, sending STOP action and popping out timer', timers[obj]
               assert(model[obj]['running'] == 'True')
               os.system('echo "%s,STOP" >> %s'%(obj, actionsfile))
               timers.pop(obj)


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
                      for each in [o for o in self if 'types' in self[o] and t in self[o]['types']]:
                          if self[each][prop] == val:
                              objects_satisfying.append(each)
                      if len(objects_satisfying) == 0:
                          conditionsAreSatisfied = False

                  elif obj.startswith('ALL '):
                      t = obj[4:]
                      for each in [o for o in self if 'types' in self[o] and t in self[o]['types']]:
                          if self[each][prop] != val:
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
                   if 'timer' in self[obj].get('types',[]):
                       if action[1] == 'START' :
                         if self[action[0]]['running'] == 'False' :
                            self.apply_change(action[0], 'running', 'True')

                       if (action[1] == 'TICK' and self[action[0]]['running'] == 'True' and self[action[0]]['periodic'] == 'True') or action[1] == 'START':
                           import threading
                           if (action[1] == 'START' and not action[0] in timers) or (action[1] == 'TICK' and not timers[action[0]].is_alive()):
                               print "  Running a thread (either START or periodic TICK) with action", action
                               timers[action[0]] = threading.Timer(self[action[0]]['interval'], tick, args=[action[0], self])
                               timers[action[0]].start()
                               print '     timers are', timers
                           else:
                               print '     not running another thread for action', action
                               # second pass due to has_changed = True -> ignore it
                               pass

                       elif action[1] == 'STOP':
                           if self[action[0]]['running'] == 'True' :
                               self.apply_change(action[0], 'running', 'False')
                           if action[0] in timers:
                               timers[action[0]].cancel()
                               timers.pop(action[0])
                           else:
                               print '(timer', action[0], 'not found in', timers, ')'



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
                          self.print_buffer.append(val)
                      else :
                         if not isinstance(self[obj][prop], type(val)):
                            print 'Rule "%s" is changing property "%s" from type "%s" to "%s" on object "%s"'%(i, prop, type(self[obj][prop]), type(val), obj)

                         if self[obj][prop] != val :
                             self.apply_change(obj, prop, val)
                             print self[obj].get('types', []), obj
                             if 'viewer' in self[obj].get('types', []) and prop == 'visible':
                                self.fov.update({obj : self[obj]['visible']})
                                self.update_fov = True

                   elif len(i) == 2:
                      (obj, act) = i
                      assert(act.isupper())
                      if i != list(action):
                         #os.system('echo "%s,%s" >> %s'%(obj, act, actionsfile))
                         self.sig("%s,%s"%(obj, act))

                   else:
                      raise Exception('Implication should have 2 or 3 items (%s given)'%len(i))


