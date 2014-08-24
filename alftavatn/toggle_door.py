#!/usr/bin/env python
import os,json
modelfp = '/home/pi/alftavatn/model.json'
actionsfp = '/home/pi/alftavatn/actions.txt'

j = json.load(open(modelfp))
if (j['porte']['openstate'] == 'open'):
  os.system('echo "porte,FERMER" > %s'%actionsfp);
elif (j['porte']['openstate'] == 'close'):
  os.system('echo "porte,OUVRIR" > %s'%actionsfp);

