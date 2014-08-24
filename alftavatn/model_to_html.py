import json

print 'obsolete'
#modelfp = '/home/pi/alftavatn/model.json'
#
#j = json.load(open(modelfp))
#
#template = '''
#      <div class="item" >
#         <div class="tweet-wrapper">
#         <span class="text">%s</span>
#      </div></div>\n'''
#
#output = ''
#for name, o in j.items():
#    s = name + ':\n'
#    for propname, p in o.items():
#       if propname not in ['geometry', 'position']:
#          s += '&nbsp;&nbsp;&nbsp;&nbsp;' + propname + ' [' + ','.join(p[0]) + '] = ' + str(p[1]) + '\n'
#       else:
#          s += '&nbsp;&nbsp;&nbsp;&nbsp;' + propname + ' ' + str(p) + ' \n'
#    output += template%s
#
#print '<div id="jstwitter" >' + output + '</div>'
#
