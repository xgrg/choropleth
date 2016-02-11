#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

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
  description_file = Column(String(100))
  readme_file = Column(String(100))

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
  timepoint = Column(String(10))
  scanner_id = Column(Integer, ForeignKey('scanner.id'))
  quality_report = Column(String(25))
  quality_score = Column(Integer, doc="General quality score summarizing all various aspects of the image")
  subject = relationship(Subject)
  scanner = relationship(Scanner)
  comments = Column(String(100))
  path = Column(String(100), nullable=False, unique=True)


def create_engine(fn = 'pluricent.db'):
    #FIXME check that fn is a filename and it exists
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///%s'%fn, encoding='utf-8')
    return engine

def create_session(fn = 'pluricent.db'):
    engine = create_engine(fn)
    Base.metadata.bind = engine
    Base.metadata.reflect()
    from sqlalchemy.orm import sessionmaker
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session

def create_database(fn = 'pluricent.db', datasource = 'pluricent/'):
    ''' Initializes a sqlite database with empty tables e.g. Action, Study, Subject, Center, Scanner, T1Image '''
    import os.path as osp
    import os
    from sqlalchemy import create_engine, Table, Column, Integer, String
    from sqlalchemy.orm import sessionmaker

    assert(osp.exists(datasource) and len(os.listdir(datasource)) == 0)

    if osp.isfile(fn):
       print 'deleting all contents from %s'%fn
    else:
       print 'creating %s'%fn

    engine = create_engine('sqlite:///%s'%fn, encoding='utf-8')
    Base.metadata.bind = engine
    Base.metadata.reflect()
    print '  0', Base.metadata.tables
    Base.metadata.drop_all()
    Base.metadata.clear()

    print '  1', Base.metadata.tables

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
        description_file = Column(String(100))
        readme_file = Column(String(100))

    class Subject(Base):
        __tablename__ = 'subject'
        id = Column(Integer, primary_key=True)
        identifier = Column(String(25), nullable=False)
        study_id = Column(Integer, ForeignKey('study.id'), nullable=False)
        study_name = Column(Integer, ForeignKey('study.name'), nullable=False)
        birth_date = Column(String(10))
        sex = Column(String(1))
        study1 = relationship(Study, foreign_keys=study_id)
        study2 = relationship(Study, foreign_keys=study_name)

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
        timepoint = Column(String(10))
        quality_report = Column(String(25))
        quality_score = Column(Integer, doc="General quality score summarizing all various aspects of the image")
        subject = relationship(Subject)
        scanner = relationship(Scanner)
        comments = Column(String(100))
        path = Column(String(100), nullable=False, unique=True)

    Base.metadata.create_all()
    print '  2', Base.metadata.tables

    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    new_general = General(key='datasource', value=datasource)
    session.add(new_general)
    session.commit()
    return engine

