pluricent
==========

sadisplay -u sqlite:///pluricent.db
-> copy the output in datamodel.dot
dot -Tpng datamodel.dot > datamodel.png
![alt tag](https://raw.github.com/xgrg/choropleth/pluricent/datamodel.png)

Instructions:

- first create or reset a database or create a session :
import pluricent as pl
pl.initialize_database('pluricent.db', '/tmp/pluricent')
or
s = pl.create_session('pluricent.db')

- create a study
pl.add_study(s, 'study01')

- find the id of the created study (might be 1 if first ever created)
study_id = pl.study_id(s, 'study01')
print study_id
> 1

- add a few subjects
subjects = ['toto01', 'toto02', 'toto03']
pl.add_subjects(s, subjects, study_id)
