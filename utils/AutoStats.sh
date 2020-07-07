#! /bin/bash
# does everything I usually do
cd /data/id30a3/inhouse/gianluca/coronavirus_structural_task_force

git pull
cd utils
./run_xtriage.sh

cd ..
git add *
git commit -m 'New xtriage run'

cd utils
./get_pdb_redo.sh
python pdbredo_cleanup.py

cd ..
git add *
git commit -m 'retrieved new pdb redo data'

cd utils
./run_molprobity.sh

cd ..
git add *
git commit -m 'new molprobity run'


cd utils
rm stats*
rm emList.txt
rm mxList.txt
python populateDatabase.py
cd ..
git add *
git commit -m "new Stats"

git push
