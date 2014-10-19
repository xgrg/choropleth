from alftavatn.model import *
def show_vk():
    u['player'].now_sees(['vk','room_on'], nothing_else=False)
    u['player'].no_longer_sees('room_off')
    u['vk'].start()

def hide_vk():
    u['vk'].stop()
    u['player'].no_longer_sees('vk')
    u['player'].no_longer_sees('room_on')
    u['player'].now_sees(['room_off'], nothing_else=False)
    #u['messenger'].show_brice()
    u['bricetimer'].start()


class Internal(Object):
   def __init__(self, **kwargs):
      Object.__init__(self, **kwargs)

   def __increment__(self):
      self['uptime'] += 1


def is_vk_visible(value):
   def res():
      if 'vk' in u['player']['visible'] and 'room_on' in u['player']['visible']:
         if value:
            print 'vk visible'
            u.pending_print('vk visible')
            return True
      elif not 'vk' in u['player']['visible'] and 'room_off' in u['player']['visible']:
         if not value:
            print 'vk not visible'
            u.pending_print('vk not visible')
            return True
      return False
   return res


def create_and_show_brice():
      index = u['internal']['uptime']
      print "brice number", index
      import random
      x = random.randrange(0,700)
      y = random.randrange(0,269)
      Visual(name='brice%s'%index, image=random.choice(['brice', 'lumiere']), zorder = 1,
            position = [x, y, 98,30])
      u['player'].now_sees('brice%s'%index, nothing_else= False)

def uptime(value):
  def res():
      return u['internal']['uptime']==value
  return res

def reset():
   u['player'].now_sees('room_off', nothing_else=True)
   u['bricetimer'].stop()

def create_world():

    r_on = Visual(name = 'room_on', image = 'room', zorder=0, position =  [0,0,900,300])
    r_off = Visual(name = 'room_off', image = 'room', zorder=0, position =  [0,0,900,300])
    reset = Visual(name = 'reset', image='reset', zorder =1, position=[849,269,50,30])
    reset.click = Action(True, Consequence(reset))
    i = Internal(name='internal', properties={'uptime':0})
    i.increment = Action(True, Consequence(i.__increment__))
    u.apply_changes()
    v = Animated(name ='vk', image='vincent', zorder=1, position = [300,30], framecount=40, fps=20)
    #v = Animated(name='explode', image='explode', zorder=1, position = [0,0], frame = 6, framecount=13)
    p = Player(name = 'player')
    u.apply_changes()
    u['player']['visible'] = ['room_off']
    r_on.click = Action(Condition(is_vk_visible(True)), Consequence(hide_vk))
    r_off.click = Action(Condition(is_vk_visible(False)), Consequence(show_vk))

    m = Object(name='messenger')
    t = Timer(name='bricetimer', interval=2, periodic=True)
    t.tick = Action(True, Consequence(i.increment))
    t.tick = Action(True, Consequence(create_and_show_brice))
    b = Visual(name='brice', image='brice', zorder=1, position= [150,150,78,30])
