#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base, inspect
import models

class Pluricent():
    def __init__(self, filepath, create_database=False):
        ''' filepath refers to the database file pluricent.db'''
        import os.path as osp
        if not osp.isfile(filepath) and not create_database:
            raise Exception('%s must be an existing file'%filepath)
        if create_database:
            models.create_database(filepath, from_existing_repository=True)
        self.filepath = osp.abspath(filepath)
        self.session = models.create_session(filepath)

    def datasource(self):
        import os.path as osp
        return osp.dirname(osp.abspath(self.filepath))


    def add_study(self, name, directory=None, description_file=None, readme_file=None, create_folder=True):
        import os.path as osp
        import os, models
        ds = self.datasource()
        assert(osp.isdir(ds))
        s = self.studies()

        if directory is None:
           directory = 'ds%05d'%(len(s)+1)
           print 'No directory provided. %s will be stored in %s'%(name, directory)

        if create_folder:
           assert(not osp.exists(osp.join(ds, directory)))
           os.mkdir(osp.join(ds, directory))

        new_study = models.Study(id=(len(s)+1), name=name, directory=directory, \
            description_file=description_file, readme_file=readme_file)

        self.session.add(new_study)
        self.session.commit()

    def study_id(self, study):
        from models import Study
        try:
           return self.session.query(Study.id).filter(Study.name==study).one()[0]
        except base.NoResultFound:
           raise base.NoResultFound('%s does not exist'%study)

    def study_dir(self, study):
        from models import Study
        return self.session.query(Study.directory).filter(Study.name==study).one()[0]

    def study_from_dir(self, studydir):
        from models import Study
        return self.session.query(Study.name).filter(Study.directory==studydir).one()[0]

    def subject_id(self, study_name, identifier):
        from models import Subject
        try:
           return self.session.query(Subject.id).filter(Subject.identifier==identifier).filter(models.Subject.study_id==self.study_id(study_name)).one()[0]
        except base.NoResultFound:
           raise base.NoResultFound('%s not found in %s'%(identifier, study_name))

    def subject_from_id(self, id):
        from models import Subject
        try:
           return self.session.query(Subject.identifier).filter(Subject.id==id).one()[0]
        except base.NoResultFound:
           raise base.NoResultFound('%s not found'%id)

    def studies(self):
        return [each.name for each in self.session.query(models.Study).all()]

    def subjects(self, study):
        study_id = self.study_id(study)
        return [each.identifier for each in self.session.query(models.Subject).filter(models.Subject.study_id==study_id).all()]

    def t1images(self, study=None, subject=None):
        if not study is None:
           study_id = self.study_id(study)
           if subject is None:
              return self.session.query(models.T1Image).join(models.Subject).join(models.Study).filter(models.Study.id==study_id).all()
           else:
              return self.session.query(models.T1Image).join(models.Subject).join(models.Study).filter(models.Study.id==study_id).filter(models.Subject.identifier == subject).all()
        else:
           return self.session.query(models.T1Image).all()


    def t1image_from_path(self, path):
        return self.session.query(models.T1Image).filter(models.T1Image.path==path).one()[0]

    def measurements(self):
        return self.session.query(models.Measurement).all()

    def actions(self):
        return self.session.query(models.Action).all()


    def add_center(self, name, location=None):
        #FIXME check if location is provided
        new_center = Center(name=name, location=location)
        self.session.add(new_center)
        self.session.commit()

    def add_subjects(self, subjects, study, create_folders=True):
        import os.path as osp
        import os
        from pluricent.models import Study, Subject
        ds = self.datasource()
        study_id = self.study_id(study)
        studydir = self.session.query(Study.directory).filter(Study.id==study_id).one()[0]
        assert(osp.isdir(osp.join(ds, studydir)))
        for s in subjects:
            if create_folders:
               assert(not osp.exists(osp.join(ds, studydir, s)))
               os.mkdir(osp.join(ds, studydir, s))
            new_subject = Subject(identifier=s, study_id=study_id)
            self.session.add(new_subject)
        self.session.commit()

    def add_t1image(self, path, study, subject):
        from pluricent.models import T1Image
        try:
           subj_id = self.subject_id(study, subject)
        except Exception as e:
           raise Exception('Problem searching for %s in %s'%(subject, study))
        try:
           stud_id = self.study_id(study)
        except Exception as e:
           raise Exception('Problem searching for study %s'%study)

        new_t1image = T1Image(subject_id=subj_id, path=path)
        self.session.add(new_t1image)
        self.session.commit()

    def add_measurement(self, image_id, structure, measurement, unit, value, side=None, software=None, comments=None):
        args = {'image_id':image_id,
                'structure':structure,
                'measurement':measurement,
                'unit':unit,
                'value':value}
        if side:
           args['side'] = side
        if software:
           args['software'] = software
        if comments:
           args['comments'] = comments
        new_measurement = models.Measurement(**args)
        self.session.add(new_measurement)
        self.session.commit()

    def add_action(self, action):
        from time import gmtime, strftime
        from models import Action
        import json
        timestamp = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        new_action = Action(action=json.dumps(action), timestamp=timestamp)
        self.session.add(new_action)
        self.session.commit()

    def add_actions(self, actions):
        from time import gmtime, strftime
        from models import Action
        import json
        for action in actions:
           timestamp = strftime("%Y-%m-%d %H:%M:%S", gmtime())
           new_action = Action(action=json.dumps(action), timestamp=timestamp)
           self.session.add(new_action)
        self.session.commit()

    def make_actions(self, actions):

        print '%s actions to perform'%len(actions)
        for i, a in enumerate(actions):
            print 'action %s/%s'%(i, len(actions)), a
            self.add_action(a)
            action_type, params = a
            if action_type == 'add_study':
                params['create_folder'] = False
                self.add_study(**params)

            elif action_type == 'add_subject':
                params['create_folders'] = False
                self.add_subjects(**params)

            elif action_type == 'add_image':
                self.add_t1image(**params)

            elif action_type == 'add_measurements':
                self.insert_from_csv(params['csvfile'])


    def populate_from_directory(self, rootdir):
        '''directory should be the root dir containing multiple studies'''
        unknown = []
        import os
        import os.path as osp
        from pluricent import checkbase as cb
        from pluricent import tests
        dirlist = [e for e in os.listdir(rootdir) if osp.isdir(osp.join(rootdir, e)) and not e in ['.', '..']]
        filelist = [e for e in os.listdir(rootdir) if osp.isfile(osp.join(rootdir, e))]
        assert(filelist == ['pluricent.db'])
        actions = []


        # Then, go for the browsing
        for each in dirlist:
           studydir = osp.join(rootdir, each)
           print 'processing %s'%studydir
           assert(tests.test_respect_hierarchy(studydir))
           cl = cb.CloudyCheckbase(studydir)

           # first look for dataset_description.json and add study
           fp = cb.getfilepath('dataset_description', {'database': studydir}, cl.patterns)
           if not osp.exists(fp):
              print fp, 'is missing'
           import json
           studyname = json.load(open(fp))['name']
           actions.append(['add_study', studyname, studydir[len(rootdir)+1:], fp[len(osp.dirname(fp))+1:] ])
           print 'study %s (%s)'%(studyname, studydir)

           for s in [e for e in os.listdir(studydir) if osp.isdir(osp.join(studydir, e))]:
              actions.append(['add_subject', s, studyname])

           for root, dirs, files in os.walk(studydir):
               for f in files:
                   fp = osp.join(root, f)
                   res = cb.parsefilepath(fp, cl.patterns)
                   if not res is None:
                       datatype, att = res
                       if datatype in  'raw':
                           actions.append(['add_image', fp[len(rootdir)+1:], studyname, att['subject']])

        print actions
        print len(actions), 'actions to make'
        ans = raw_input('proceed ? y/n')
        if ans == 'y':
            print 'warning: erasing database contents'
            ans = raw_input('proceed ? y/n')
            if ans == 'y':
               models.create_database(self.filepath, from_existing_repository=True)

            self.make_actions(actions)


def global_settings():
    ''' ==== load setting from json ===='''
    import os.path as osp
    import pluricent as pl
    import json
    print pl.__file__
    j = json.load(open(osp.join(osp.split(osp.split(osp.dirname(pl.__file__))[0])[0], '.pluricent_settings.json')))
    return j


