import json

rulesfp = '/home/pi/alftavatn/rules.json'

j = json.load(open(rulesfp))

output = ''
for conditions, implications in j:
   output += '('
   for obj, prop, val in conditions:
      output += obj + '-' + prop + '-' + str(val) + ', '
   output = output[:-1] + ') => ('
   for obj, prop, val in implications:
      output += obj + '-' + prop + '-' + str(val) + ', '
   output = output[:-1] + ') \n '

print output

