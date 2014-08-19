import json

modelfp = '/home/pi/alftavatn/model.json'

j = json.load(open(modelfp))

output = ''
for name, o in j.items():
    output += name + ':\n'
    for propname, p in o.items():
       if propname not in ['geometry', 'position']:
          output += '&nbsp;&nbsp;&nbsp;&nbsp;' + propname + ' [' + ','.join(p[0]) + '] = ' + str(p[1]) + '\n'
       else:
          output += '&nbsp;&nbsp;&nbsp;&nbsp;' + propname + ' ' + str(p) + ' \n'
    output += '\n'

print output

