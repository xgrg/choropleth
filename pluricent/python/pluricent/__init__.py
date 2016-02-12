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

def study_id(session, study):
    from models import Study
    return session.query(Study.id).filter(Study.name==study).one()[0]

def study_dir(session, study):
    from models import Study
    return session.query(Study.directory).filter(Study.name==study).one()[0]

def subject_id(session, study_name, identifier):
    from models import Subject
    return session.query(Subject.id).filter(Subject.identifier==identifier).one()[0]


def add_center(session, name, location=None):
    #FIXME check if location is provided
    new_center = Center(name=name, location=location)
    session.add(new_center)
    session.commit()

def studies(session):
    import models
    return [each.name for each in session.query(models.Study).all()]

def subjects(session, study):
    import models
    import pluricent as pl
    study_id = pl.study_id(session, study)
    return [each.identifier for each in session.query(models.Subject).filter(models.Subject.study_id==study_id).all()]

def datasource(session):
    import models
    General = models.General
    return session.query(General.value).filter(General.key=='datasource').one()[0]

def add_t1image(session, path, study, subject):
    from pluricent.models import T1Image

    new_t1image = T1Image(subject_id=subject_id(session, study, subject), study_id=study_id(session, study), path=path)
    session.add(new_t1image)
    session.commit()

def make_actions(session, actions):
    from time import gmtime, strftime
    from pluricent.models import Action

    print '%s actions to perform'%len(actions)
    for i, a in enumerate(actions):
        print 'action %s/%s'%(i, len(actions)), a
        timestamp = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        new_action = Action(action=str(a), timestamp=timestamp)
        session.add(new_action)
        session.commit()

        if a[0] == 'add_study':
            add_study(session, a[1])


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







