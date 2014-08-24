import json

rulesfp = '/home/pi/alftavatn/rules.json'
modelfp = '/home/pi/alftavatn/model.json'

j = json.load(open(rulesfp))
m = json.load(open(modelfp))
import state_machine as s

output = ''
for conditions, implications in j:
   output += '('
   for c in conditions:
      try:
         (obj, prop, val) = c
#         if val[0] == '@':
#            val = s.solve_function(s.parse_function(val), m)
         output += obj + '-' + prop + '-' + str(val) + ', '
      except ValueError:
         (obj, act) = c
         output += obj + '-' + act + ', '

   output = output[:-1] + ') => ('

   for i in implications:
      try:
         (obj, prop, val) = i
#         if val[0] == '@':
#            val = s.solve_function(s.parse_function(val), m)
         output += obj + '-' + prop + '-' + str(val) + ', '
      except ValueError:
         (obj, act) = i
         output += obj + '-' + act + ', '
   output = output[:-1] + ') \n '

print output

