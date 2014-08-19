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
      for (obj, prop, val) in conditions:
         if obj == o and not prop.isupper() and model[obj][prop][1] != val:
            satisfied = False
            break
         elif obj == o and prop.isupper():
            candidate = val
      if satisfied:
         actions.add(candidate)

   print ','.join(actions)



