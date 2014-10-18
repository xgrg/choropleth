from alftavatn.model import *

class Title(Visual):
   def __init__(self, **kwargs):
      Visual.__init__(self, **kwargs)

class Room(Visual):
   def __init__(self, **kwargs):
      Visual.__init__(self, **kwargs)

class Internal(Object):
   def __init__(self, **kwargs):
      Object.__init__(self, **kwargs)

def toggle_explode():
    if u['explode']['running']:
        u['explode'].stop()
    else:
        u['explode'].start()

def create_world():


    t = Title(name = 'title', image = 'title', zorder=0, position =  [0,0,900,300])
    exp = Animated(name='explode', image='explode', zorder=1, position = [0,0], frame = 6, framecount=13)
    exp.click = Action(True, toggle_explode)

    r = Room(name = 'room', image = 'room', zorder=0, position =  [0,0])#,900,300])

    def is_title():
       return 'title' in u['player']['visible']

    def is_room():
       return 'room' in u['player']['visible']

    def switch_to_room():
       u['player']['visible'] = ['room']
       u['timer'].start()

    def purr():
       print 'rrrRRrrrRRR...'
       if 'ronron' not in u['player']['visible']:
           u['player'].now_sees('ronron', nothing_else=False)
       else:
           u['player'].no_longer_sees('ronron')
       u.apply_changes()

    def print_internal_uptime():
        u['internal']['uptime'] += 1
        u.pending_print('%s'%u['internal']['uptime'])

    # can be useful to define a function to add an action
    # so that previously defined click() are not overwritten
    t.click = Action(Condition(is_title), switch_to_room)
    r.click = Action(Condition(is_room), purr)

    t = Timer(name = 'timer', interval=1, periodic=True)
    t.tick = Action(True, Consequence(print_internal_uptime))

    Visual(name = 'cat', image = 'cat', zorder=2,position = [200,110,151,174])
    Visual(name = 'pouf', image = 'pouf',  position = [10,170,160,99])
    Visual(name = 'lampe', image = 'lamp', position = [0,0,79,79])
    Visual(name = 'porte', image = 'door1', position = [700,60,177,233])
    Visual(name = 'fenetre', image = 'window', position = [470,30,223,150])
    Visual(name = 'ventilateur', image = 'fan', position = [350,130,119,148])
    Visual(name = 'ronron', image = 'ronron', zorder=1, position = [220,110,122,30])

    Object(name = 'internal', properties={'uptime':0})

    def uptime(value):
        def res():
            return u['internal']['uptime']==value
        return res

    def show(item):
        def res():
            u['player'].now_sees(item, nothing_else=False)
            u.apply_changes()
        return res



    t.tick = Action(Condition(uptime(2)), show('cat'))
    t.tick = Action(Condition(uptime(4)), show('ventilateur'))
    t.tick = Action(Condition(uptime(6)), show('pouf'))
    t.tick = Action(Condition(uptime(8)), show('lampe'))
    t.tick = Action(Condition(uptime(10)), show(['porte', 'fenetre']))


    p = Player(name = 'player')
    p = Player(name = 'player1')
    p['location'] = 'home'
    u.apply_changes()
    u['player']['visible'] = ['explode','title']






if __name__ == '__main__':
    create_world()
