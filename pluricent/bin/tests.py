#!/usr/bin/env python
# -*- coding: utf-8 -*-
baseurl = 'http://localhost:8888/'
credentials = {'username': 'admin', 'password':'admin'}

def __new_dummy__():
    import os.path as osp
    a = 0
    dummydir = '/tmp/dummydb_%s'
    dummydb = '/tmp/dummydb_%s.db'
    while osp.isdir(dummydir%a) or osp.isfile(dummydb%a):
        a += 1

    # Careful : dummydir becomes dummydir%a
    dummydir = dummydir%a
    dummydb = dummydb%a
    return dummydb, dummydir

def __last_dummy__():
    import os.path as osp
    a = 100
    dummydir = '/tmp/dummydb_%s'
    dummydb = '/tmp/dummydb_%s.db'

    while not osp.isdir(dummydir%a) or not osp.isfile(dummydb%a):
        a -= 1

    # Careful : dummydir becomes dummydir%a
    dummydir = dummydir%a
    dummydb = dummydb%a
    return dummydb, dummydir

# Web-based tests

def test_login_logout():
   import requests
   print 'Check the server is running'
   url = baseurl + 'auth/login/'
   data = {'username': 'toto', 'password':'admin'}
   try:
       r = requests.post(url, data=data)
       res = r.url == baseurl + 'auth/login/?error=Login+incorrect'

       data = credentials
       r = requests.post(url, data=data)
       res = res and '<a id="logout"' in r.text

       url = baseurl + 'auth/logout/'
       r = requests.get(url)
       res = res and baseurl + 'auth/login/' in r.url
   except Exception as e:
       res = False
       print e

   return res

def test_invalid_study():
   import requests
   url = baseurl + 'auth/login/'
   r = requests.post(url, data=credentials)
   url = baseurl + 'explore/?study=toto'
   print url
   r = requests.get(url)
   print r.text
   res = 'invalid study' in r.text
   return res

def test_valid_study():
#FIXME
   import requests
   import pluricent as pl
   url = baseurl + 'auth/login/'
   r = requests.post(url, data=credentials)
   url = baseurl + 'explore/?study=study01'

   r = requests.get(url)
   res = 'invalid study' in r.text
   return res

# Database-based tests

def test_create_database():
    import pluricent as p
    import os

    dummydb, dummydir = __new_dummy__()

    os.mkdir(dummydir)
    e = p.create_database(dummydb, dummydir)
    return True


def test_create_study():
    import pluricent as p

    dummydb, dummydir = __last_dummy__()
    print 'Reading %s (%s)'%(dummydb, dummydir)

    s = p.create_session(dummydb)
    p.add_study(s, 'study01')
    studies = p.studies(s)
    print 'studies', studies
    return True

def test_create_subjects():
    import pluricent as p

    dummydb, dummydir = __last_dummy__()
    print 'Reading %s (%s)'%(dummydb, dummydir)

    s = p.create_session(dummydb)

    studies = p.studies(s)
    print 'adding subjects in %s'%studies[0]
    subjects = ['subj01','subj02']
    p.add_subjects(s, subjects, studies[0])
    subjects = p.subjects(s, studies[0])
    print 'subjects', subjects
    return True



if __name__ == '__main__':
    results = {}
    from datetime import datetime
    results['last_checked'] = datetime.now().isoformat()
    results['test_login_logout'] = test_login_logout()
    results['test_invalid_study'] = results['test_login_logout'] and test_invalid_study()
    results['test_create_database'] = test_create_database()
    results['test_create_study'] = test_create_study()
    results['test_create_subjects'] = test_create_subjects()

    import json
    import pluricent as pl
    import os.path as osp
    fp = osp.join(osp.dirname(pl.__file__), '..', '..', 'web', 'json', 'sysdiag.json')
    json.dump(results, open(fp, 'w'), indent=2)

