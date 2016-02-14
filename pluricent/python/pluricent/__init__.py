#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base, inspect
from models import create_database, create_session


def add_study(session, name, description_file=None, readme_file=None):
    import os.path as osp
    import os, models
    ds = datasource(session)
    assert(osp.isdir(ds))
    s = studies(session)
    directory = 'ds%05d'%(len(s)+1)
    assert(not osp.exists(osp.join(ds, directory)))
    os.mkdir(osp.join(ds, directory))

    new_study = models.Study(id=(len(s)+1), name=name, directory=directory, \
        description_file=description_file, readme_file=readme_file)

    session.add(new_study)
    session.commit()

def study_id(session, study):
    from models import Study
    return session.query(Study.id).filter(Study.name==study).one()[0]

def study_dir(session, study):
    from models import Study
    return session.query(Study.directory).filter(Study.name==study).one()[0]

def study_from_dir(session, studydir):
    from models import Study
    return session.query(Study.name).filter(Study.directory==studydir).one()[0]

def subject_id(session, study_name, identifier):
    from models import Subject
    return session.query(Subject.id).filter(Subject.identifier==identifier).one()[0]

def studies(session):
    import models
    return [each.name for each in session.query(models.Study).all()]

def subjects(session, study):
    import models
    import pluricent as pl
    study_id = pl.study_id(session, study)
    return [each.identifier for each in session.query(models.Subject).filter(models.Subject.study_id==study_id).all()]

def t1images(session, study=None, subject=None):
    import models
    import pluricent as pl
    if not study is None:
       study_id = pl.study_id(session, study)
       if subject is None:
          return session.query(models.T1Image).join(models.Subject).join(models.Study).filter(models.Study.id==study_id).all()
       else:
          return session.query(models.T1Image).join(models.Subject).join(models.Study).filter(models.Study.id==study_id).filter(models.Subject.identifier == subject).all()
    else:
       return session.query(models.T1Image).all()


def t1image_from_path(session, path):
    import models
    return session.query(models.T1Image).filter(models.T1Image.path==path).one()[0]

def datasource(session):
    import models
    General = models.General
    return session.query(General.value).filter(General.key=='datasource').one()[0]

def add_center(session, name, location=None):
    #FIXME check if location is provided
    new_center = Center(name=name, location=location)
    session.add(new_center)
    session.commit()

def add_subjects(session, subjects, study):
    import os.path as osp
    import os
    import pluricent as pl
    from pluricent.models import Study, Subject
    ds = datasource(session)
    study_id = pl.study_id(session, study)
    studydir = session.query(Study.directory).filter(Study.id==study_id).one()[0]
    assert(osp.isdir(osp.join(ds, studydir)))
    for s in subjects:
        assert(not osp.exists(osp.join(ds, studydir, s)))
        os.mkdir(osp.join(ds, studydir, s))
        new_subject = Subject(identifier=s, study_id=study_id)
        session.add(new_subject)
    session.commit()

def add_t1image(session, path, study, subject):
    from pluricent.models import T1Image
    try:
       subj_id = subject_id(session, study, subject)
    except Exception as e:
       raise Exception('Problem searching for %s in %s'%(subject, study))
    try:
       stud_id = study_id(session, study)
    except Exception as e:
       raise Exception('Problem searching for study %s'%study)

    new_t1image = T1Image(subject_id=subj_id, path=path)
    session.add(new_t1image)
    session.commit()

def add_action(session, action):
    from time import gmtime, strftime
    from models import Action
    timestamp = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    new_action = Action(action=str(action), timestamp=timestamp)
    session.add(new_action)
    session.commit()


def make_actions(session, actions):
    from pluricent.models import Action

    print '%s actions to perform'%len(actions)
    for i, a in enumerate(actions):
        print 'action %s/%s'%(i, len(actions)), a
        add_action(session, a)

        if a[0] == 'add_study':
            add_study(session, a[1])

        elif a[0] == 'add_subject':
           add_subjects(session, [a[1]], a[2])

        elif a[0] == 'add_t1image':
            add_t1image(session, a[1], a[2], a[3])


def populate_from_directory(directory, fn = 'pluricent.db'):
    unknown = []
    import os
    import os.path as osp
    from pluricent import checkbase as cb
    cl = cb.CloudyCheckbase(directory)
    actions = []

    for root, dirs, files in os.walk(directory):
        for each in dirs:
            d = osp.join(root, each)
#            cb.parsefilepath(







