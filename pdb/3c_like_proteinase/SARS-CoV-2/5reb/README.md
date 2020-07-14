# PDB 5reb

## Overview

**Protein name**: 3c like proteinase

**Organism**: SARS-CoV-2

**Method**: X-Ray Diffraction

## Description

Full length 3C-like protease from SARS-CoV-2 forming a dimer. This protein is bound to a small molecule fragment, 1-[(thiophen-3-yl)methyl]piperidin-4-ol. This X-ray crystal structure has data to a resolution of 1.68Å

## Basefolder

5reb.pdb and 5reb.cif - the coordinates of the threedimensional molecular model

5reb-sf.cif - deposited diffraction data for this PDB entry

5reb.mtz - structure factors after automatic refinement of molecular model against the diffraction data

## Subfolders



**old** - contains files from historical revisions

**validation** - contains validation reports. This structure has been analyzed by [**AUSPEX**](https://github.com/thorn-lab/coronavirus_structural_task_force/tree/master/pdb/3c_like_proteinase/SARS-CoV-2/5reb/validation/auspex) [**PDB-REDO**](https://github.com/thorn-lab/coronavirus_structural_task_force/tree/master/pdb/3c_like_proteinase/SARS-CoV-2/5reb/validation/pdb-redo) [**MOLPROBITY**](https://github.com/thorn-lab/coronavirus_structural_task_force/tree/master/pdb/3c_like_proteinase/SARS-CoV-2/5reb/validation/molprobity) [**XTRIAGE**](https://github.com/thorn-lab/coronavirus_structural_task_force/blob/master/pdb/3c_like_proteinase/SARS-CoV-2/5reb/validation/Xtriage_output.log) [**BUSTER**](https://www.globalphasing.com/buster/wiki/index.cgi?Covid19Pdb5REB) 



## Raw diffraction data

Available. **Click** [here](https://zenodo.org/record/3730578) 

## Data Summary
**Diffraction Data Quality**

|   | Resolution | Completeness| I/sigma |
|---|-------------:|----------------:|--------------:|
|   |1.68 Å|99.2  %|<img width=50/>6.900|

**Discrepancy between model and data (the lower the better)**

|   | **R-work**| **R-free**   
|---|-------------:|----------------:|           
||  0.1760|  0.2240|

**Geometry validation (the lower, the better)**

|   |**MolProbity<br>score**| **Ramachandran<br>outliers** 
|---|-------------:|----------------:|
||  1.25|  0.33 %|

**Auspex Pathologies**<br> missing line (For more information, read [this](https://github.com/thorn-lab/coronavirus_structural_task_force/blob/master/pdb/3c_like_proteinase/SARS-CoV-2/5reb/validation/auspex/5reb_auspex_comments.txt))

 


## Comments On The Structure
`Tristan Croll`

The ligand in PDB 5REB is established well enough in the density to be believable, and the conformation looks right.

PDB-REDO gets the ligand wrong- a potential bug. Given its definition in the PDB it is not an aromatic ring, but a piperidine.

In this case we would recommend to use the original structure, potentially with the following changes:
- all amino acid residues should have, when added up, full occupancy (some residues add up to less than occupancy 1 for no good reason, possibly an artifact from the starting structure)
- two waters near the active site that may be DMSO, given the electron density



## Other relevant links 
**PDBe**:  https://www.ebi.ac.uk/pdbe/entry/pdb/5reb

**PDBe-KB**:https://www.ebi.ac.uk/pdbe/pdbe-kb/covid19/PRO_0000449623 
 
**PDBr**: https://www.rcsb.org/structure/5reb 

**Structure view with 3D Bionotes**: https://3dbionotes.cnb.csic.es/?queryId=5reb

