![logo](https://github.com/thorn-lab/coronavirus_structural_task_force/blob/master/outreach/banner.png)

# CORONAVIRUS STRUCTURAL TASKFORCE

A global public resource for the structures from beta-coronavirus with a focus on SARS-CoV and SARS-CoV-2.

## What is this?

This repository is a global public resource for the structures from beta-coronavirus with a focus on SARS-CoV and SARS-CoV-2.


## Why?

During this time of crisis, we basically decided to put or brains to where our hearts are. We hope to make a small difference for the cure of COVID-19.


## Download for non git users

This is a project in progress. While we strongly suggest users to work with Git so that they can synchronize with us conveniently, there is also a possibility to fetch the most recent update as a zip package by clicking the Green Button "Clone or download" and "Download Zip".

## Folder stucture

You can find the structures in a folder like this:
```
pdb/3c_like_proteinase/SARS-CoV-2/5re5
```
Following the scheme<br>
pdb/protein name/virus name/pdbid

In each pdbid directory, there may one or several of the following subfolders:<br><br>
validation/<br>
This folder contains [pdb-redo](https://pdb-redo.eu/) (including [whatcheck](https://swift.cmbi.umcn.nl/gv/whatcheck/)) and [phenix.xtriage](https://www.phenix-online.org/documentation/reference/xtriage.html#how-xtriage-works) results.


isolde/<br>
These are manual re-refinements from isolde, done by Tristan Croll.

auspex/<br>
These are results of the analysis of deposited data with [AUSPEX](www.auspex.de)

haruspex/<br>
These are results for the splitting of Cryo-EM maps accorindg to secondary structure with the neural network [Haruspex](https://github.com/thorn-lab/haruspex)
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


## References
PDB-REDO: Joosten, R.P., Long, F., Murshudov, G.N., Perrakis, A. (2014) The PDB_REDO server for macromolecular structure model optimization.  IUCrJ 1, 213-220. <br>
ISOLDE: <br>
PHENIX: Zwart, P.H., Grosse-Kunstleve, R.W., Adams, P.D. (2005) XTRIAGE: Xtriage   and   Fest:   automatic   assessment   of   X-ray   data   and substructure structure factor estimation. CCP4 newsletter 43 <br>
WHATCHECK: Hooft, R.W.W., Vriend, G., Sander, C., Abola, E.E. WHATCHECK: Errors in protein structures. (1996) Nature 381, 272-272.<br>
AUSPEX: Thorn, A., Parkhurst, J.M., Emsley, P., Nicholls, R., Evans, G., Vollmar, M., Murshudov, G.N. (2017) AUSPEX: a graphical tool for X-ray diffraction data analysis, Acta Cryst D73, 729-737. <br> 
HARUSPEX: Mostosi, P., Schindelin, H., Kollmannsberger, P., Thorn, A. Haruspex: A Neural Network for the Automatic Identification of Oligonucleotides and Protein Secondary Structure in Cryo‐EM Maps. (2020) Angewandte Chem. (Int. Ed.). https://doi.org/10.1002/ange.202000421


## References

If you would like to contact us, please write to:

Dr. Andrea Thorn
andrea.thorn@uni-wuerzburg.de
Rudolf Virchow Center, University of Wuerzburg
Josef-Schneider-Str. 2
97080 Wuerzburg
Germany
