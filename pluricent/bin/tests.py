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

def __collect_tests__():
    import inspect, os, importlib, os.path as osp
    from pluricent.web import settings
    d = osp.dirname(osp.abspath(settings.STATIC_PATH))
    os.chdir(d)
    m = importlib.import_module('tests')
    test_functions = [e for e in inspect.getmembers(m, inspect.isfunction) if e[0].startswith('test')]
    return test_functions

#================
# Basic tests

def test_database_exists():
    ''' Returns False if the database as defined in pluricent.settings
    is missing'''
    import os.path as osp
    from pluricent.web import settings
    import pluricent as pl
    db = settings.DATABASE
    return osp.isfile(db)

def test_datasource_exists():
    ''' Returns False if the datasource as defined in the database
    is missing'''
    import os.path as osp
    from pluricent.web import settings
    import pluricent as pl
    db = settings.DATABASE
    s = pl.create_session(db)
    ds = pl.datasource(s)
    return osp.isdir(ds)


#================
# Web-based tests

def test_login_logout():
   ''' Performs 3 tests in a row :
   - login with wrong credentials
   - login with correct credentials
   - logout
   Returns True if the 3 tests are successful'''
   import requests
   print 'Check the server is running'
   url = baseurl + 'auth/login/'
   data = {'username': 'toto', 'password':'admin'}
   try:
       r = requests.post(url, data=data)
       res = r.url == baseurl + 'auth/login/?error=Login+incorrect'
       print res

       data = credentials
       r = requests.post(url, data=data)
       res = res and '<a id="logout"' in r.text
       print r.text, res

       url = baseurl + 'auth/logout/'
       r = requests.get(url)
       res = res and baseurl + 'auth/login/' in r.url
       print res
   except Exception as e:
       res = False
       print e

   return res

def test_invalid_study():
   ''' Logs in and acts as if just asked for a non-existing study.
   Returns True if successfully redirected with an information message'''
   import requests
   url = baseurl + 'auth/login/'
   s = requests.Session()
   r = s.post(url, data=credentials)
   url = baseurl + 'explore/?study=toto'
   print url
   r = s.get(url)
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


#===============================
# Database-based tests (on dummy)

def test_create_database():
    '''Creates a dummy database and repository in /tmp'''
    import pluricent as p
    import os

    dummydb, dummydir = __new_dummy__()

    os.mkdir(dummydir)
    e = p.create_database(dummydb, dummydir)
    return True


def test_create_study():
    ''' Creates a study in the last dummy database created'''
    import pluricent as p

    dummydb, dummydir = __last_dummy__()
    print 'Reading %s (%s)'%(dummydb, dummydir)

    s = p.create_session(dummydb)
    p.add_study(s, 'study01')
    studies = p.studies(s)
    print 'studies', studies
    return True

def test_create_subjects():
    ''' Adds subjects to the first study of the last dummy
    database created'''
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


#================================
# Database-based tests (on prod)

def test_studies():
    ''' Compares studies between the repository and the database '''
    from pluricent.web import settings
    import pluricent as pl
    import os, os.path as osp
    db = settings.DATABASE
    s = pl.create_session(db)
    ds = pl.datasource(s)
    studies_db = list(set([pl.study_dir(s, e) for e in pl.studies(s)]))
    studies_ds = list(set([e for e in os.listdir(ds) \
            if osp.isdir(osp.join(ds,e)) and not e in ['.','..']]))
    print studies_db, studies_ds
    return studies_db == studies_ds

def run_tests(results):
    test_functions = __collect_tests__()
    for fname, func in test_functions:
        results[fname] = func()
    return results

def run_test(test):
    test_functions = dict(__collect_tests__())
    test_functions[test]()

if __name__ == '__main__':
    # ==== brand new results ====
    results = {}
    f = __collect_tests__()
    for fname, _ in f:
        results[fname] = False

    # ==== argparse ====
    import argparse, inspect
    parser = argparse.ArgumentParser(description='Runs unit tests (to date: %s)'%', '.join(results.keys()))
    parser.add_argument("--debug", help="Debug mode: raise exceptions (default: skips errors\
            until the end, writes the output in json file)", action="store_true")
    parser.add_argument("-t", dest='test_name', type=str, help="Run specific test (in debug mode)", required=False)
    args = parser.parse_args()

    # ==== run specific test ? ====
    if args.test_name:
        if not args.test_name in results.keys():
            raise Exception('%s should refer to an existing test (%s)'%(args.test_name, results.keys()))
        run_test(args.test_name)
        import sys
        sys.exit(0)

    # ==== run tests ====
    from datetime import datetime
    results['last_checked'] = datetime.now().isoformat()

    if args.debug:
        results = run_tests(results)
    else:
        try:
            results = run_tests(results)
        except Exception as e:
            print e


    import json
    import pluricent as pl
    import os.path as osp
    print '===================================================================================================='
    fp = osp.abspath(osp.join(osp.dirname(pl.__file__), '..', '..', 'web', 'json', 'sysdiag.json'))
    print 'Writing json... %s'%fp
    json.dump(results, open(fp, 'w'), indent=2)

