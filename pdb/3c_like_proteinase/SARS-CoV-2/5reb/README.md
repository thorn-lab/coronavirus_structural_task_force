# PDB 5reb

## Overview

**Protein name:** 3c like proteinase

**Organism:** SARS-CoV-2

**Method:** X-Ray Diffraction

## Basefolder

5reb.pdb and 5reb.cif - contain the coordinates of the threedimensional molecular model, and can be viewed with, for example, Coot or Pymol.

5reb-sf.cif - contains deposited diffraction data for this PDB entry, if the structure has been solved with X-ray or neutron crystallography.

5reb.mtz - contains structure factors after automatic refinement of molecular model against the diffraction data.

## Subfolders



**old** - contains files from historical revisions

**validation** - contains validation reports. This structure has been analyzed by [**AUSPEX**](https://github.com/thorn-lab/coronavirus_structural_task_force/tree/master/pdb/3c_like_proteinase/SARS-CoV-2/5reb/validation/auspex) [**PDB-REDO**](https://github.com/thorn-lab/coronavirus_structural_task_force/tree/master/pdb/3c_like_proteinase/SARS-CoV-2/5reb/validation/pdb-redo) [**MOLPROBITY**](https://github.com/thorn-lab/coronavirus_structural_task_force/tree/master/pdb/3c_like_proteinase/SARS-CoV-2/5reb/validation/molprobity) [**PDB-REDO**](https://github.com/thorn-lab/coronavirus_structural_task_force/blob/master/pdb/3c_like_proteinase/SARS-CoV-2/5reb/validation/Xtriage_output.log) [**BUSTER**](https://www.globalphasing.com/buster/wiki/index.cgi?Covid19Pdb5REB)

## Raw diffraction data

Avaibale. **Click** [here](https://zenodo.org/record/3730578) 

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

**Auspex Pathologies**: missing line (For more information, read [this](https://github.com/thorn-lab/coronavirus_structural_task_force/blob/master/pdb/3c_like_proteinase/SARS-CoV-2/5reb/validation/auspex/5reb_auspex_comments.txt))

 


## Comments On The Structure
`Tristan Croll`

The ligand in PDB 5REB is established well enough in the density to be believable, and the conformation looks right.

PDB-REDO gets the ligand wrong- a potential bug. Given its definition in the PDB it is not an aromatic ring, but a piperidine.

In this case we would recommend to use the original structure, potentially with the following changes:
- all amino acid residues should have, when added up, full occupancy (some residues add up to less than occupancy 1 for no good reason, possibly an artifact from the starting structure)
- two waters near the active site that may be DMSO, given the electron density



## Other relevant links 
**PDBe**:  https://www.ebi.ac.uk/pdbe/entry/pdb/5reb
 
**PDBr**: https://www.rcsb.org/structure/5reb 

**Look at the structure with 3D Bionotes**: https://3dbionotes.cnb.csic.es/?queryId=5reb

