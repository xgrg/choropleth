#!/usr/bin/env python
# -*- coding: utf-8 -*-

def test_login_logout():
   import requests
   print 'Check the server is running'
   url = 'http://localhost:8888/auth/login/'
   data = {'username': 'toto', 'password':'admin'}
   r = requests.post(url, data=data)
   res = r.url == 'http://localhost:8888/auth/login/?error=Login+incorrect'

   data = {'username': 'admin', 'password':'admin'}
   r = requests.post(url, data=data)
   res = res and '<a id="logout"' in r.text

   url = 'http://localhost:8888/auth/logout/' 
   r = requests.get(url)
   res = res and 'http://localhost:8888/auth/login/' in r.url

   return res
   

