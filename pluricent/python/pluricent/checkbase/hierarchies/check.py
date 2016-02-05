# -*- coding: utf-8 -*-


def perform_checks_hierarchy(directory, hierarchy_type = 'Morphologist'):
    ''' Runs a series of tests on a given dictionary returned from
    checkbase.detect_hierarchies. These tests are performed according to the
    type of the hierarchy.
    - lists key steps of the production pipeline associated to the hierarchy
    - lists subjects (or just directories at the subject level) detected in the hierarchy
    - sorts out subjects whose ID appear multiple times (in distinct groups e.g)
    - identifies all existing files in the hierarchy and collects the unidentified ones.
    - lists subjects with complete datasets according to the previous key items
    - lists subjects with no identified items (possibly mistaken folders)
    All the results are returned as a dictionary.
      checks['all_subjects'] : {'/neurospin/cati/Users/dubois/' : ['toto', 'tata', ...], ...}
      checks['existing_files'] :
         {'/neurospin/cati/Memento/' : ( {'toto' : {'subject': toto,
                                                    'group': 'temoins',
                                                    'acquisition': 'default',
                                                    'modality' : 't1mri',
                                                    'extension' : 'nii'}, ...},
                                         {'tata' : ['i_am_an_unidentified_file.xxx', ...], ...} ), ...}
      checks['complete_subjects']
      checks['multiple_subjects']
      checks['empty_subjects']
      checks['checkbase']

    '''
    from pluricent.checkbase.hierarchies import morphologist as morpho
    from pluricent.checkbase.hierarchies import freesurfer as free
    from pluricent.checkbase.hierarchies import snapshots as snap

    if hierarchy_type == 'morphologist':
        m = morpho.MorphologistCheckbase(directory)
        m.perform_checks()
    elif hierarchy_type == 'freesurfer':
        m = free.FreeSurferCheckbase(directory)
        m.perform_checks()
    elif hierarchy_type == 'snapshots':
        m = snap.SnapshotsCheckbase(directory)
        m.perform_checks()


    return m

def _check_directories(rootdirectory, dirlist, verbose = True):
   from pluricent import checkbase as c
   import os
   checks = {}
   hierarchies = {}

   for eachdir in dirlist:
       # process each directory
       if verbose: print eachdir, 'in progress'
       db_dir = os.path.join(rootdirectory, eachdir)
       h = c.detect_hierarchies(db_dir, maxdepth=3)
       assert(not hierarchies.has_key(eachdir))
       hierarchies[eachdir] = h
       dir_checks = perform_checks_hierarchy(h)

       # update big directory
       for each in dir_checks.keys():
          checks.setdefault(each, {})
          for db, res in dir_checks[each].items():
             checks[each].setdefault(db, {})
          checks[each].update(dir_checks[each])
   return checks, hierarchies


