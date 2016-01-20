#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

def initialize_database(fn = 'pluricent.db', datasource = 'pluricent/'):
    ''' Initializes a sqlite database with empty tables e.g. Action, Study, Subject, Center, Scanner, T1Image '''
    import os.path as osp
    import os
    assert(osp.exists(datasource) and len(os.listdir(datasource)) == 0)

    from sqlalchemy import create_engine, Table
    engine = create_engine('sqlite:///%s'%fn, encoding='utf-8')
    Base = declarative_base()
    Base.metadata.bind = engine
    Base.metadata.reflect()
    Base.metadata.drop_all()
    Base = declarative_base()
    Base.metadata.bind = engine

    class General(Base):
        __tablename__ = 'general'
        id = Column(Integer, primary_key=True)
        key = Column(String(25), nullable=False, unique=True)
        value = Column(String(100), nullable=False, unique=True)

    class Study(Base):
        __tablename__ = 'study'
        id = Column(Integer, primary_key=True)
        name = Column(String(25), nullable=False, unique=True)
        directory = Column(String(100), nullable=False, unique=True)

    class Subject(Base):
        __tablename__ = 'subject'
        id = Column(Integer, primary_key=True)
        identifier = Column(String(25), nullable=False)
        study_id = Column(Integer, ForeignKey('study.id'), nullable=False)
        birth_date = Column(String(10))
        sex = Column(String(1))
        study = relationship(Study)

    class Action(Base):
        __tablename__ = 'action'
        id = Column(Integer, primary_key=True)
        action = Column(String(250), nullable=False)
        timestamp = Column(String(19), nullable=False)

    class Center(Base):
        __tablename__ = 'center'
        id = Column(Integer, primary_key=True)
        name = Column(String(25), nullable=False)
        location = Column(String(50))

    class Scanner(Base):
        __tablename__ = 'scanner'
        id = Column(Integer, primary_key=True)
        intensity_field = Column(Float)
        manufacturer = Column(String(25))
        center_id = Column(Integer, ForeignKey('center.id'))
        service_starting_date = Column(String(10), doc="Date when the system was up and running.")
        center = relationship(Center)

    class T1Image(Base):
        __tablename__ = 't1image'
        id = Column(Integer, primary_key=True)
        subject_id = Column(Integer, ForeignKey('subject.id'), nullable=False)
        acquisition_date = Column(String(10))
        scanner_id = Column(Integer, ForeignKey('scanner.id'))
        quality_report = Column(String(25))
        quality_score = Column(Integer, doc="General quality score summarizing all various aspects of the image")
        subject = relationship(Subject)
        scanner = relationship(Scanner)
        path = Column(String(100), nullable=False, unique=True)

    Base.metadata.create_all()
    from sqlalchemy.orm import sessionmaker
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    new_general = General(key='datasource', value=datasource)
    session.add(new_general)
    session.commit()
    return engine


def create_engine(fn = 'pluricent.db'):
    #FIXME check that fn is a filename and it exists
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///%s'%fn, encoding='utf-8')
    return engine

def create_session(fn = 'pluricent.db'):
    engine = create_engine(fn)
    Base = declarative_base()
    Base.metadata.bind = engine
    Base.metadata.reflect()
    from sqlalchemy.orm import sessionmaker
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session


def add_study(session, name):
    import os.path as osp
    import os
    from pluricent.models import Study
    ds = datasource(session)
    assert(osp.isdir(ds))
    s = studies(session)
    directory = 'ds%05d'%(len(s)+1)
    assert(not osp.exists(osp.join(ds, directory)))
    os.mkdir(osp.join(ds, directory))

    new_study = Study(id=(len(s)+1), name=name, directory=directory)

    session.add(new_study)
    session.commit()

def add_subjects(session, subjects, study):
    import os.path as osp
    import os
    from pluricent.models import Study, Subject
    ds = datasource(session) 
    study_id = study_id(session, study)
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


def subject_id(session, study_name, identifier):
    from models import Subject
    return session.query(Subject.id).filter(Subject.identifier==identifier).one()[0]
    

def add_center(session, name, location=None):
    #FIXME check if location is provided
    new_center = Center(name=name, location=location)
    session.add(new_center)
    session.commit()

def studies(session):
    from pluricent.models import Study
    return [each.name for each in session.query(Study).all()]

def datasource(session):
    from pluricent.models import General
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






