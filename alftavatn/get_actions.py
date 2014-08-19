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

if len(args)==2:
   s = args[0]
   o = args[1]
   actions = set()
   for (conditions, implications) in rules:
      satisfied = True
      for (obj, prop, val) in conditions:
         if not prop.isupper() and model[obj][prop][1] != val:
            satisfied = False
            break
         elif obj == s and prop.isupper() and val == o:
            actions.add(prop)

   print ','.join(actions)

