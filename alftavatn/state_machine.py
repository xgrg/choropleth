#!/usr/bin/env python

import os, sys, json
actionsfile = '/home/pi/alftavatn/actions.txt'
modelfile = '/home/pi/alftavatn/model.json'
rulesfile = '/home/pi/alftavatn/rules.json'
dialogsfile = '/var/www/alftavatn/data.txt'

def process_rules ( model, rules, action ) :
    changes = -1
    iter_nb = 0
    has_changed = False

    while changes != 0:
        iter_nb = iter_nb + 1
        changes = 0
        for conditions, implications in rules :
            conditionsAreSatisfied = True
            for obj, prop, val in conditions:
                if prop.isupper() and not action is None:
                    #print rule[0][each], action
                    if (obj, prop, val) != action :
                        conditionsAreSatisfied = False
                elif prop.isupper() and action is None:
                    conditionsAreSatisfied = False
                elif not prop.isupper():
                    #print machine_states[each], rule[0][each]
                    if model[obj][prop][1] != val:
                        conditionsAreSatisfied = False
            if conditionsAreSatisfied :
                print 'ok'
                for obj, prop, val in implications :
                    if prop == 'PRINT':
                        os.system('echo "%s" >> %s'%(val, dialogsfile))
                    elif prop.isupper():
                       os.system('echo "%s,%s,%s" >> %s'%(obj, prop, val, actionsfile))
                    else :
                        if model[obj][prop][1] != val :
                            changes = changes + 1
                            print changes, obj, prop, model[obj][prop][0][model[obj][prop][1]], '->', val
                            model[obj][prop][1] = val
                            has_changed = True
            #else :
                #print 'not ok'
        #print "iteration :", iter_nb, "changes :", changes

    if has_changed:
     json.dump(model, open(modelfile, 'w'), indent=2)
    if not action is None:
      f = open(actionsfile, 'w')
      f.close()


try :
   os.system('echo "STATE MACHINE STARTED" > %s'%dialogsfile)
   while(True):
      actions = [e.rstrip('\n') for e in open(actionsfile).readlines()]
      model = json.load(open(modelfile))
      rules = json.load(open(rulesfile))
      if len(actions) != 0:
         for a in actions:
            src, act, obj = a.split(',')
            print obj, act
            process_rules(model, rules, (src, act, obj))
      else:
            process_rules(model, rules, None)

except:
   e = sys.exc_info()
   s = str(e)
   os.system('echo "STATE MACHINE STOPPED %s" >> %s'%(s, dialogsfile))
   raise
