import tornado.ioloop
import tornado.web
import tornado.websocket
import threading, os, string, json, time
from tornado import gen

s= ''
homedir = os.path.dirname(os.path.abspath(__file__))
modelfp = os.path.join(homedir, 'data', 'model.json')
rulesfp = os.path.join(homedir, 'data', 'rules.json')

#datafile = os.path.join('/tmp', 'data.txt')
#visiblefile = os.path.join('/tmp', 'visible.txt')
#actionsfp = os.path.join('/tmp', 'actions.txt')



def get_canvas_cards():
    model = json.load(open(modelfp))
    viewers = [e for e in model if 'viewer' in model[e].get('types',[])]
    fov = dict( [(i, model[i].get('visible',[])) for i in viewers])
    d = {}
    for v in fov:
      for each in fov[v]:
         if 'image' in model[each]:
            d.setdefault(v, []).append('%s.%s'%(each, model[each]['image']))
    print d
    fov = d.get('player', [])
    output1 = ''
    for each in fov:
        k = each.split('.')
        item = '<b>' + k[0] + '</b><br>'
        item = item + '<img src="static/data/%s.png" /><br>'%k[1]
        output1 = output1 + '<div class="item"><div class="tweet-wrapper"><span class="text">' + item + '</span></div></div>'
    return output1

def get_model_cards():
    model = json.load(open(modelfp))
    output = ''
    for k, obj in model.items():
        item = '<b>' + k + '</b><br>'
        for p in obj:
            if not p in ['geometry', 'position']:
                item = item + ' &nbsp;&nbsp;&nbsp;' + p + ' = ' + str(obj[p]) + '<br>'
        output = output + '<div class="item"><div class="tweet-wrapper"><span class="text">' + item + '</span></div></div>'
    return output

class IndexHandler(tornado.web.RequestHandler):
  def get(self):
    print self.settings
    model = tornado.web.escape.json_encode(json.load(open(modelfp)))
    rules = json.load(open(rulesfp))
    rules = ' <br/>'.join([tornado.web.escape.json_encode(e) for e in rules])
    print model
    self.render("index.html", model = model, rules = rules, canvas = get_canvas_cards())

  def post(self):
      print self.request.arguments
      if 'dialog' in self.request.arguments:
         dialog = self.get_argument('dialog')
         os.system('echo "%s" >> %s'%(dialog, datafile))
      elif 'clean_data' in self.request.arguments:
         os.system('> %s'%datafile)
      elif 'toggle_door' in self.request.arguments:

         j = json.load(open(modelfp))
         if (j['porte']['openstate'] == 'open'):
           os.system('echo "porte,FERMER" > %s'%actionsfp);
         elif (j['porte']['openstate'] == 'close'):
             os.system('echo "porte,OUVRIR" > %s'%actionsfp);
      elif 'send_action' in self.request.arguments:
          obj = self.get_argument('object')
          act = self.get_argument('action')
          #os.system('echo "%s,%s" >> %s'%(obj, act, actionsfp))
          self.actions.append("%s,%s"%(obj, act))
      elif 'get_objects' in self.request.arguments:
           from alftavatn import get_objects

           rules = None
           model = None

           while (rules is None or model is None):
              try:
                 rules = json.load(open(rulesfp))
                 model = json.load(open(modelfp))
              except:
                 pass
           objects = get_objects(model, rules)
           self.write(','.join(objects))

      elif 'get_actions' in self.request.arguments:
           from alftavatn import get_actions
           obj = self.get_argument('object')

           rules = None
           model = None

           while (rules is None or model is None):
              try:
                 rules = json.load(open(rulesfp))
                 model = json.load(open(modelfp))
              except:
                 pass
           actions = get_actions(obj, model, rules)
           self.write(','.join(actions))
      elif 'fov' in self.request.arguments:
          self.write(get_canvas_cards())
      elif 'refreshmodel' in self.request.arguments:
          self.write(get_model_cards())


class TokenHandler(tornado.web.RequestHandler):
    def get(self):
        if 'q' in self.request.arguments:
            model = json.load(open(modelfp))
            q = string.replace(self.get_argument('q'),' ', '')
            i = 1
            keys = model.keys()
            keys.sort()
            keys_starting_with_q = [v for v in keys if (q in v.lower() and v.lower().index(q) == 0)]

            arr = []
            for v in keys_starting_with_q:
               p = {"id" : i, "name" : v, "type" : "object"}
               p["image"] = 'static/data' + model[v]["image"] + '.png' if "image" in model[v] else ""
               arr.append(p)
               i = i + 1

            json_response = tornado.web.escape.json_encode(arr)
            self.write(json_response)
        elif 'qa' in self.request.arguments:
            obj = self.get_argument('object')
            print obj
            model = json.load(open(modelfp))
            rules = json.load(open(rulesfp))
            q = string.replace(self.get_argument('qa'),' ', '')
            arr = []

            for conditions, implications in rules:
                for c in conditions:
                    if len(c) == 2 and c[0] == obj:
                        arr.append(c[1])
            actions_starting_with_q = [v for v in arr if (q in v.lower() and v.lower().index(q) == 0)]
            i = 1

            arr = []
            for v in actions_starting_with_q:
               p = {"id" : i, "name" : v}
               arr.append(p)
               i = i + 1

            json_response = tornado.web.escape.json_encode(arr)
            self.write(json_response)




class LongPollingHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self):
         return
         mtime = os.stat(datafile)[8]
         last_ajax_call = self.get_argument('timestamp') if 'timestamp' in self.request.arguments else None
         if (last_ajax_call is None or mtime > last_ajax_call):
             data = open(datafile).read()
             visible = open(visiblefile).read()
             timestamp = mtime
             ans = {'data_from_file': data, 'visible_from_file': visible, 'timestamp': timestamp}
             self.write(tornado.web.escape.json_encode(ans))
         else:
             time.sleep(0.1)

from sig import Signal
class TestHandler(tornado.websocket.WebSocketHandler):
  def initialize(self, engine):
    self.engine = engine
    self.engine.clients = []
    self.sig = Signal()
    self.sig.connect(engine.get_server_signal)

  def open(self, *args):
    print("open", "WebSocketChatHandler")
    self.engine.clients.append(self)

  def on_message(self, message):
     print message
     action, params = message.split('@')
     if action == 'DIALOG':
         self.write_message(params)
     elif action == 'ACTION':
         self.sig(params)

  def on_close(self):
     self.engine.clients.remove(self)

if __name__ == '__main__':
    app = tornado.web.Application(handlers = [(r'/', IndexHandler), (r'/poll', LongPollingHandler), (r'/list_tokens', TokenHandler)],
            static_path = homedir, autoescape = None)

    app.listen(8000)
    tornado.ioloop.IOLoop.instance().start()

