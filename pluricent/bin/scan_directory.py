#!/usr/bin/env python
# -*- coding: utf-8 -*-
''' Contains code supposed to parse directories and identify files
that will populate the clean database. Mostly ad-hoc scripts
performing quick and dirty operations

*** scandir_BVdatabase : to run on BVddatabase directories
(make use of brainvisa.checkbase)
'''

def size_to_human(full_size):
  size = full_size
  if size >= 1024:
    unit = 'KiB'
    size /= 1024.0
    if size >= 1024:
      unit = 'MiB'
      size /= 1024.0
      if size >= 1024:
        unit = 'GiB'
        size /= 1024.0
        if size >= 1024:
          unit = 'TiB'
          size /= 1024.0
    s = '%.2f' % (size,)
    if s.endswith( '.00' ): s = s[:-3]
    elif s[-1] == '0': s = s[:-1]
    return s + ' ' + unit + ' (' + str(full_size) + ')'
  else:
    return str(size)

stat_attributes = ('st_atime', 'st_ctime', 'st_gid', 'st_mode', 'st_mtime',
               'st_nlink', 'st_size', 'st_uid', 'st_blksize', 'st_blocks',
               'st_dev','st_rdev', 'st_ino')


def scandir_BVdatabase(studydir):
    '''Objectif: trouver sujets, centres et images T1 nifti'''
    ''' Strategie : BVdatabase '''
    import os.path as osp
    import os

    actions = []
    assert(osp.isdir(studydir))
    studydir = studydir.rstrip('/')
    assert(osp.split(studydir)[-1] == 'BVdatabase')

    from brainvisa import checkbase as cb
    m = cb.MorphologistCheckbase(studydir)

    subjects = m.get_flat_subjects()

    actions.extend([('add_subject', s) for s in subjects])

    for subject in subjects:
      files = m.get_subject_hierarchy_files(subject)

      for k,v in files.items():
        for each in v:
           fp = cb.getfilepath(k, each)
           if osp.isfile(fp):
              if k in ['raw', 'nobias'] :
                 print fp, 'identified as', k
                 actions.append(('add_image', subject, k, fp, each))
    return actions


    # estimating directory size
    cumulative_size = 0
    for root, dirs, files in os.walk(studydir):
        for f in files:
            cumulative_size += os.stat(osp.join(root,f)).st_size

    print size_to_human(cumulative_size)


def move_to_cloud_hierarchy(actions, destdir):
    import os.path as osp
    import os, shutil
    from brainvisa import checkbase as cb

    cl = cb.CloudyCheckbase(destdir)

    assert(osp.exists(destdir))

    for a in actions:
        k, v = a[0], a[1:]
        if k=='add_image':
            subject, datatype, fp, att = v
            d = osp.join(destdir, subject, 'anatomy')
            #os.makedirs(d)
            #os.system('cp %s %s'%(fp, ))
            att.update({'database': destdir, 'number': '001'})
            d2 = cb.getfilepath('t1raw', att, patterns=cl.patterns)
            print 'cp %s %s'%(fp, d2)



