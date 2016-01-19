#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

def initialize_database(fn = 'pluricent.db'):
    ''' Initializes a sqlite database with empty tables e.g. Action, Study, Subject, Center, Scanner, T1Image '''

    from sqlalchemy import create_engine, Table
    engine = create_engine('sqlite:///%s'%fn, encoding='utf-8')
    Base = declarative_base()
    Base.metadata.bind = engine
    Base.metadata.reflect()
    Base.metadata.drop_all()
    Base = declarative_base()
    Base.metadata.bind = engine

    class Study(Base):
        __tablename__ = 'study'
        id = Column(Integer, primary_key=True)
        name = Column(String(25), nullable=False, unique=True)

    class Subject(Base):
        __tablename__ = 'subject'
        id = Column(Integer, primary_key=True)
        identifier = Column(String(25), nullable=False)
        study_id = Column(Integer, ForeignKey('study.id'))
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
        subject_id = Column(Integer, ForeignKey('subject.id'))
        acquisition_date = Column(String(10))
        scanner_id = Column(Integer, ForeignKey('scanner.id'))
        quality_report = Column(String(25))
        quality_score = Column(Integer, doc="General quality score summarizing all various aspects of the image")
        subject = relationship(Subject)
        scanner = relationship(Scanner)


    Base.metadata.create_all()
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
    from pluricent.models import Study
    new_study = Study(name=name)
    session.add(new_study)
    session.commit()


def add_center(session, name, location=None):
    #FIXME check if location is provided
    new_center = Center(name=name, location=location)
    session.add(new_center)
    session.commit()

def studies(session):
    from pluricent.models import Study
    return [each.name for each in session.query(Study).all()]

def populate_study(studydir, fn = 'pluricent.db'):
    import os.path as osp

    session = create_session(fn)

    # checks if study already exists in the database
    s = studies(session)

    dirname = osp.split(studydir)[-1]
    actions = []
    if not dirname in s:
        actions.append(('add_study', dirname))

    make_actions(session, actions)

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






