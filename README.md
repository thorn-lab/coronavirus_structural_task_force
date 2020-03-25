![logo](https://github.com/thorn-lab/coronavirus_structural_task_force/blob/master/outreach/banner.png)

# CORONAVIRUS STRUCTURAL TASKFORCE

A global public resource for the structures from beta-coronavirus with a focus on SARS-CoV and SARS-CoV-2.

## Contributors

This is a collaborative effort. These are the current contributors (in order of joining):<br>
University of Wuerzburg, Germany -<br>
[Andrea Thorn - group leader](https://www.uni-wuerzburg.de/en/rvz/research/associated-research-groups/thorn-group/)<br>
Yunyun Gao - postdoc in the AUSPEX (www.auspex.de)<br>
Kristopher Nolte - biochemistry B.Sc. student<br>
Ferdinand Kirsten - biochemistry B.Sc. student<br>
Sabrina Staeb - biochemistry M.Sc. student<br>
<br>
European Synchrotron Facility, Grenoble, France -<br>
Gianluca Santoni - Serial crystallography data scientist<br>
<br>
CIMR, University of Cambridge, UK -<br>
[Tristan Croll - Research associate](https://isolde.cimr.cam.ac.uk/what-isolde/)<br>


## What is this?

This repository is a global public resource for the structures from beta-coronavirus with a focus on SARS-CoV and SARS-CoV-2.


## Why?

During this time of crisis, we basically decided to put or brains to where our hearts are. We hope to make a small difference for the cure of COVID-19.


## Download for non git users

This is a project in progress. While we strongly suggest users to work with Git so that they can synchronize with us conveniently, there is also a possibility to fetch the most recent update as a zip package by clicking the Green Button "Clone or download" and "Download Zip".

## Folder stucture

You can find the structures in a folder like this:
pdb/3c_like_proteinase/SARS-CoV-2/5re5
___ __________________ __________ ____
pdb  protein name      virus name pdbid

In each pdbid directory, there may one or several of the following subfolders:
validation/
This folder contains [pdb-redo](https://pdb-redo.eu/) (including whatcheck) and phenix.xtriage results.

auspex/
These are results of the analysis of deposited data with [AUSPEX](www.auspex.de)

haruspex/
These are results for the splitting of Cryo-EM maps accorindg to secondary structure with the neural network [Haruspex]()

isolde/
These are manual re-refinements from isolde, done by Tristan Croll.

## References
PDB-REDO: Joosten RP, Long F, Murshudov GN, Perrakis A. The PDB_REDO server for macromolecular structure model optimization. IUCrJ. 2014 May 30;1(Pt 4):213-20. <br>
ISOLDE: <br>
PHENIX:XTRIAGE: <br>
WHATCHECK: <br>
AUSPEX: <>


