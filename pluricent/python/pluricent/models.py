#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship
from pluricent import Base

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
