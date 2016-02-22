# -*- coding: utf-8 -*-
import os
from pluricent.checkbase.hierarchies import *
from pluricent.checkbase.hierarchies.checkbase import Checkbase

patterns = { 'raw': os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', '(?P<session>\d{3})', 'anatomy', '(?P=subject)_T1w.nii.gz$'),
             'left_greywhite': os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', '(?P<session>\d{3})', 'processing', 'morphologist','(?P=subject)_left_greywhite.nii.gz$'),
             'right_greywhite': os.path.join('(?P<database>[\w -/]+)','(?P<subject>\w+)', '(?P<session>\d{3})', 'processing', 'morphologist','(?P=subject)_right_greywhite.nii.gz$'),
             'nobias': os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', '(?P<session>\d{3})', 'processing', 'morphologist','(?P=subject)_nobias.nii.gz$'),
             'spm_nobias': os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', '(?P<session>\d{3})', 'processing', 'spm8','(?P=subject)_nobias.nii.gz$'),
             'split': os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', '(?P<session>\d{3})', 'processing', 'morphologist','(?P=subject)_split.nii.gz$'),
             'brainmask': os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', '(?P<session>\d{3})', 'processing', 'morphologist','(?P=subject)_brain.nii.gz$'),
             'left_white': os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', '(?P<session>\d{3})', 'processing', 'morphologist','(?P=subject)_(?P<side>[L]?)white.(?P<extension>%s)'%mesh_extensions),
             'right_white': os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', '(?P<session>\d{3})', 'processing', 'morphologist','(?P=subject)_(?P<side>[R]?)white.(?P<extension>%s)'%mesh_extensions),
             'left_hemi': os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', '(?P<session>\d{3})', 'processing', 'morphologist','(?P=subject)_(?P<side>[L]?)hemi.(?P<extension>%s)'%mesh_extensions),
             'right_hemi': os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', '(?P<session>\d{3})', 'processing', 'morphologist','(?P=subject)_(?P<side>[R]?)hemi.(?P<extension>%s)'%mesh_extensions),
             'left_sulci': os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)',  '(?P<session>\d{3})', 'processing', 'morphologist', '(?P=subject)_(?P<side>[L]?)folds.arg'),
             'right_sulci': os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', '(?P<session>\d{3})', 'processing', 'morphologist', '(?P=subject)_(?P<side>[R]?)folds.arg'),
             'spm_nobias': os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', '(?P<session>\d{3})', 'processing', 'spm8', '(?P=subject)_nobias.(?P<extension>%s)'%image_extensions),
             'spm_greymap': os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', '(?P<session>\d{3})', 'processing', 'spm8','(?P=subject)_nat_grey.(?P<extension>%s)'%image_extensions),
             'spm_whitemap': os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)',  '(?P<session>\d{3})', 'processing', 'spm8', '(?P=subject)_nat_white.(?P<extension>%s)'%image_extensions),
             'spm_csfmap': os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)',  '(?P<session>\d{3})', 'processing', 'spm8', '(?P=subject)_nat_csf.(?P<extension>%s)'%image_extensions),
             'spm_greymap_warped': os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)',  '(?P<session>\d{3})', 'processing', 'spm8', '(?P=subject)_nat_grey_warped.(?P<extension>%s)'%image_extensions),
             'spm_whitemap_warped': os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', '(?P<session>\d{3})', 'processing', 'spm8', '(?P=subject)_white_warped.(?P<extension>%s)'%image_extensions),
             'spm_csfmap_warped': os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', '(?P<session>\d{3})', 'processing', 'spm8',  '(?P=subject)_csf_warped.(?P<extension>%s)'%image_extensions),
             'spm_greymap_modulated': os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', '(?P<session>\d{3})', 'processing', 'spm8', '(?P=subject)_grey_modulated.(?P<extension>%s)'%image_extensions),
             'spm_whitemap_modulated': os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', '(?P<session>\d{3})', 'processing', 'spm8', '(?P=subject)_white_modulated.(?P<extension>%s)'%image_extensions),
             'spm_csfmap_modulated': os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', '(?P<session>\d{3})', 'processing', 'spm8','(?P=subject)_csf_modulated.(?P<extension>%s)'%image_extensions),
             'dataset_description': os.path.join('(?P<database>[\w -/]+)', 'dataset_description.json'),
             'readme': os.path.join('(?P<database>[\w -/]+)', 'README'),
             'measurements': os.path.join('(?P<database>[\w -/]+)', 'measurements_(?P<filename>\w+).csv'),
             #'subject' : os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)')
#             'snapshot_splitbrain': os.path.join('(?P<database>[\w -/]+)', 'ANALYSIS', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', 'snapshot_splitbrain_(?P=subject).png$'),
#             'spm8_nobias': os.path.join('(?P<database>[\w -/]+)', 'ANALYSIS', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', 'spm8_nobias_(?P=subject).nii.gz$'),
#             'spm8_grey': os.path.join('(?P<database>[\w -/]+)', 'ANALYSIS', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', 'spm8_probamap_grey_(?P=subject).nii.gz$'),
#             'spm8_white': os.path.join('(?P<database>[\w -/]+)', 'ANALYSIS', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', 'spm8_probamap_white_(?P=subject).nii.gz$'),
#             'spm8_csf': os.path.join('(?P<database>[\w -/]+)', 'ANALYSIS', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', 'spm8_probamap_csf_(?P=subject).nii.gz$'),
#             'snapshot_spm8_grey': os.path.join('(?P<database>[\w -/]+)', 'ANALYSIS', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', 'snapshot_spm8_grey_(?P=subject).png$'),
#             'snapshot_spm8_white': os.path.join('(?P<database>[\w -/]+)', 'ANALYSIS', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', 'snapshot_spm8_white_(?P=subject).png$'),
#             'snapshot_spm8_csf': os.path.join('(?P<database>[\w -/]+)', 'ANALYSIS', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', 'snapshot_spm8_csf_(?P=subject).png$'),
#             'snapshot_greywhite': os.path.join('(?P<database>[\w -/]+)', 'ANALYSIS', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', 'snapshot_greywhite_(?P=subject).png$'),

#                 'nobias': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'nobias_(?P=subject).(?P<extension>%s)'%image_extensions),
#                 'left_greywhite': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', '(?P<side>[L]?)grey_white_(?P=subject).(?P<extension>%s)'%image_extensions),
#                 'right_greywhite': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', '(?P<side>[R]?)grey_white_(?P=subject).(?P<extension>%s)'%image_extensions),
#                 'brainmask': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'brain_(?P=subject).(?P<extension>%s)'%image_extensions),
#                 'left_white': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'mesh', '(?P=subject)_(?P<side>[L]?)white.(?P<extension>%s)'%mesh_extensions),
#                 'right_white': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'mesh', '(?P=subject)_(?P<side>[R]?)white.(?P<extension>%s)'%mesh_extensions),
#                 'left_hemi': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'mesh', '(?P=subject)_(?P<side>[L]?)hemi.(?P<extension>%s)'%mesh_extensions),
#                 'right_hemi': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'mesh', '(?P=subject)_(?P<side>[R]?)hemi.(?P<extension>%s)'%mesh_extensions),
#                 'left_sulci': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'folds', '(?P<graph_version>[\d.]+)', '(?P<side>[L]?)(?P=subject).arg'),
#                 'right_sulci': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'folds', '(?P<graph_version>[\d.]+)', '(?P<side>[R]?)(?P=subject).arg'),
#                 'spm_nobias': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'nobias_(?P=subject).(?P<extension>%s)'%image_extensions),
#                 'spm_greymap': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_grey_probamap.(?P<extension>%s)'%image_extensions),
#                 'spm_whitemap': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_white_probamap.(?P<extension>%s)'%image_extensions),
#                 'spm_csfmap': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_csf_probamap.(?P<extension>%s)'%image_extensions),
#                 'spm_greymap_warped': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_grey_probamap_warped.(?P<extension>%s)'%image_extensions),
#                 'spm_whitemap_warped': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_white_probamap_warped.(?P<extension>%s)'%image_extensions),
#                 'spm_csfmap_warped': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_csf_probamap_warped.(?P<extension>%s)'%image_extensions),
#                 'spm_greymap_modulated': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_grey_probamap_modulated.(?P<extension>%s)'%image_extensions),
#                 'spm_whitemap_modulated': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_white_probamap_modulated.(?P<extension>%s)'%image_extensions),
#                 'spm_csfmap_modulated': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_csf_probamap_modulated.(?P<extension>%s)'%image_extensions),
#                 'spm_tiv_logfile' : os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_TIV_log_file.txt$'),

}

#import re
#for k, v in patterns.items():
#   patterns[k] = re.sub(r':?\\+', '\', r'%s'%v)

keyitems = ['t1natnii', 't1geonii', 't1natdcm', 't1geodcm', 'split_brain', 'brain_mask', 'snapshot_split', 'action_3dt1', 'spm8_nobias', 'spm8_grey', 'spm8_white', 'spm8_csf']


class CloudyCheckbase(Checkbase):
    def __init__(self, directory):
        from pluricent.checkbase.hierarchies import cloudy as cs
        self.patterns = cs.patterns
        self.keyitems = cs.keyitems
        Checkbase.__init__(self, directory)




