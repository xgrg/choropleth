#!/usr/bin/env python
import os,json
modelfp = '/home/pi/alftavatn/model.json'
actionsfp = '/home/pi/alftavatn/actions.txt'

j = json.load(open(modelfp))
if (j['porte']['openstate'][1] == 0):
  os.system('echo "player,FERMER,porte" > %s'%actionsfp);
elif (j['porte']['openstate'][1] == 1):
  os.system('echo "player,OUVRIR,porte" > %s'%actionsfp);

