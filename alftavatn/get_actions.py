#!/usr/bin/env python
import sys, json
args = sys.argv[1:]

rulesfp = '/home/pi/alftavatn/rules.json'
modelfp = '/home/pi/alftavatn/model.json'

rules = None
model = None
while (rules is None or model is None):
   try:
      rules = json.load(open(rulesfp))
      model = json.load(open(modelfp))
   except:
      pass

if len(args)==1:
   o = args[0]
   actions = set()
   for (conditions, implications) in rules:
      satisfied = True
      for c in conditions:
         if len(c) == 3:
            (obj, prop, val) = c
            if obj.startswith('ANY '):
                      t = obj[4:]
                      objects_satisfying = []
                      for each in [o for o in model if 'types' in model[o] and t in model[o]['types']]:
                          if model[each][prop] == val:
                              objects_satisfying.append(each)
                      if len(objects_satisfying) == 0:
                          satisfied = False
            elif obj.startswith('ALL '):
                      t = obj[4:]
                      for each in [o for o in model if 'types' in model[o] and t in model[o]['types']]:
                          if model[each][prop] != val:
                              satisfied = False
            elif model[obj][prop] != val:
               satisfied = False
               break
         elif len(c) == 2:
            (obj, action) = c
            assert(action.isupper())
            if obj != o:
               satisfied = False
               break
      if satisfied:
         actions.add(action)

   print ','.join(actions)

