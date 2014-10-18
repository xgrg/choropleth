import tornado.ioloop
import tornado.web
import tornado.websocket
import threading, os, string, json, time
from tornado import gen

class IndexHandler(tornado.web.RequestHandler):
  def initialize(self, engine=None):
    self.engine = engine
    self.model = engine.model

  def get(self):
    error = False
    if 'id' in self.request.arguments:
       self.player_id = self.get_argument('id')
       if self.player_id not in self.model.fov:
          error = True
    else:
       error = True

    if error:
       self.write('Please define a correct id')
    else:
       self.render("index2.html", player_id = self.player_id) #, canvas = self.model.get_canvas_cards())

  def post(self):
      print self.request.arguments
      if 'send_action' in self.request.arguments:
          obj = self.get_argument('object')
          act = self.get_argument('action')
          self.model.add_action("%s,%s"%(obj, act))
      elif 'get_objects' in self.request.arguments:
           from alftavatn import get_objects
           objects = self.model.get_objects() #(self.model, self.rules)
           self.write(','.join(objects))
      elif 'get_actions' in self.request.arguments:
           from alftavatn import get_actions
           obj = self.get_argument('object')
           actions = self.model.get_actions(obj)
           self.write(','.join(actions))
      elif 'fov' in self.request.arguments:
          res = json.dumps(self.model.fov[self.get_argument('player_name')])
          print 'fov return', res
          self.write(res)
      elif 'get_image_path' in self.request.arguments:
          self.write('static/data/' + self.model[self.get_argument('get_image_path')]['image'] + '.png')



class TokenHandler(tornado.web.RequestHandler):
    def initialize(self, engine=None):
        self.engine = engine
        self.model = engine.model
        self.rules = engine.rules

    def get(self):
        if 'q' in self.request.arguments:
            model = self.model
            q = string.replace(self.get_argument('q'),' ', '')
            i = 1
            keys = model.keys()
            keys.sort()
            keys_starting_with_q = [v for v in keys if (q in v.lower() and v.lower().index(q) == 0)]

            arr = []
            for v in keys_starting_with_q:
               p = {"id" : i, "name" : v, "type" : "object"}
               p["image"] = 'static/data/' + model[v]["image"] + '.png' if "image" in model[v] else ""
               arr.append(p)
               i = i + 1

            json_response = tornado.web.escape.json_encode(arr)
            self.write(json_response)
        elif 'qa' in self.request.arguments:
            obj = self.get_argument('object')
            print obj
            model = self.model
            rules = self.rules
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

class TestHandler(tornado.websocket.WebSocketHandler):
  def initialize(self, engine):
    self.engine = engine
    self.clients = []
    self.engine.print_buffer.connect(self.write)
    self.engine.model.model_changed.connect(self.write)
    self.engine.model.fov_changed.connect(self.write)
    self.engine.model.animstate_changed.connect(self.write)

  def open(self, *args):
    print("open", "WebSocketChatHandler")
    self.clients.append(self)

  def on_message(self, message):
     print message
     action, params = message.split('@')
     if action == 'DIALOG':
         # This Dialog action can only be fired from a client,
         # not by the state machine, this is why the response
         # is sent only to self (and not to every client as in
         # write(self, data)
         self.write_message('dialog@' + params)
     elif action == 'ACTION':
         self.engine.model.action_added(params)
     elif action == 'TOGGLEDOOR':
         j = self.engine.model
         if (j['porte']['openstate'] == 'open'):
           self.engine.model.action_added("porte,FERMER")
         elif (j['porte']['openstate'] == 'close'):
           self.engine.model.action_added("porte,OUVRIR")

  def on_close(self):
     self.clients.remove(self)

  def write(self, data):
      for each in self.clients:
          self.write_message(data)

if __name__ == '__main__':
    app = tornado.web.Application(handlers = [(r'/', IndexHandler), (r'/poll', LongPollingHandler), (r'/list_tokens', TokenHandler)],
            static_path = homedir, autoescape = None)

    app.listen(8000)
    tornado.ioloop.IOLoop.instance().start()

