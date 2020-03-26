![logo](https://github.com/thorn-lab/coronavirus_structural_task_force/blob/master/outreach/banner.png)

# CORONAVIRUS STRUCTURAL TASKFORCE

A global public resource for the structures from beta-coronavirus with a focus on SARS-CoV and SARS-CoV-2.

## What is this?

This repository is a global public resource for the structures from beta-coronavirus with a focus on SARS-CoV and SARS-CoV-2.
You can find here:
* The original files for 19 of the 28 proteins in SARS-CoV and SARS-CoV, over 300 different structures.
* Re-refined structures from different contributors(*)
* Validation statistics for these and the original structural models
* Diagnostic data for the quality of the experimental data

(*) Please be aware that while there is potential to improve some structures, this is not meant as criticism of the great achievements of the research groups who were able to initially elucidate these structures. It merely reflects on the potential to push our methods to their limit.

## Why?

We are methods developers in structural biology. During this time of crisis, we  decided to put or brains to where our hearts are. We hope this can make a (small) difference for the cure of COVID-19.

## Download for non-git users

This is a project in progress. While we strongly suggest users to work with Git so that they can synchronize with us conveniently, there is also a possibility to fetch the most recent update as a zip package by clicking the Green Button "Clone or download" and "Download Zip".

## Folder stucture 

In each folder, is a file **directory_info.txt**. It contains information on the file formats used in this directory, and where they came from.

You can find the structures in a folder named like this: `pdb/3c_like_proteinase/SARS-CoV-2/5re5`<br>
Following the scheme: `pdb/protein name/virus name/pdbid`<br><br>

We do not host Cryo-EM maps, as they are too large. Please download these maps from EMDB@EMBL_EBI: https://www.ebi.ac.uk/pdbe/emdb/<br>

In each `pdbid/` directory, there may one or several of the following subfolders:<br>

`validation/`<br>
This folder contains currently output from [phenix.xtriage](https://www.phenix-online.org/documentation/reference/xtriage.html#how-xtriage-works). Xtriage analyzes diffraction data for Wilson plot adherence, diffraction strength and twinning.

`validation/pdb-redo/`<br>
This folder contains [pdb-redo](https://pdb-redo.eu/) results (including [whatcheck](https://swift.cmbi.umcn.nl/gv/whatcheck/)). PDB-REDO is a procedure to optimise crystallographic structure models, providing algorithms that make a fully automated decision making system for refinement, rebuilding and validation. 

`isolde/`<br>
These are manual re-refinements from [ISOLDE](https://isolde.cimr.cam.ac.uk/what-isolde/) in [ChimeraX](https://www.cgl.ucsf.edu/chimerax/), done by Tristan Croll. Structures were energy-minimised, visually checked residue-by-residue and, where necessary, rebuilt. Crystal structures were further refined with [phenix.refine](https://www.phenix-online.org/documentation/reference/refinement.html).

`auspex/`<br>
These are results of the analysis of deposited diffraction data with [AUSPEX](www.auspex.de). AUSPEX can help to detect problems in experimental setup, integration, scaling and conversion from intensities to amplitudes.

`haruspex/`<br>
These are results for the splitting of Cryo-EM maps according to secondary structure with the neural network [Haruspex](https://github.com/thorn-lab/haruspex)

## Further resources
https://www.globalphasing.com/buster/wiki/index.cgi?Covid19<br>
re-processing and re-refinement of several SARS-CoV-2 structures<br><br>
https://www.diamond.ac.uk/covid-19/for-scientists.html<br>
Info on Diamond work on main protease; related: https://covid.postera.ai/covid<br><br>
https://www.ebi.ac.uk/ena/pathogens/covid-19<br>
Data resources held at EMBL-EBI relating to the COVID-19 outbreak, including sequences of outbreak isolates and records relating to coronavirus biology
https://www.rcsb.org/news?year=2020&article=5e74d55d2d410731e9944f52&feature=true
Varius links to COVID-19/SARS-CoV-2 Resources from RCSB PDB

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
Duke University
[The Richardson Laboratory](http://kinemage.biochem.duke.edu/)

We would also like to thank for their advice: Manfred Weiss *(HBZ BESSY, Berlin, Germany)* Gerard Bricogne *(Global Phasing, Cambridge, UK)*, Clemens Vonrhein *(Global Phasing, Freiburg, Germany)*, Robbie P. Joosten *(The Netherlands Cancer Institute, Amsterdam, Netherlands)*, Sameer Velankar *(European Potein Data Bank, Cambridge, UK)*.

## References
**PDB-REDO**: Joosten, R.P., Long, F., Murshudov, G.N., Perrakis, A. (2014) The PDB_REDO server for macromolecular structure model optimization. *IUCrJ* 1, 213-220. <br>
**ISOLDE**: Croll, T.I. (2018) ISOLDE: a physically realistic environment for model building into low-resolution electron-density maps. *Acta Cryst. D*74, 519-530. <br>
**ChimeraX**:  Goddard, T.D., Huang, C.C., Meng, E.C., Pettersen, E.F., Couch, G.S., Morris, J.H., Ferrin, T.E. (2018) UCSF ChimeraX: Meeting modern challenges in visualization and analysis. *Protein Sci.* 27, 14-25.
**Coot**: Emsley, P., Lohkamp, B., Scott, W.G., Cowtan, K. (2010) Features and Development of Coot. *Acta Cryst. D*66, 486-501.<br>
**phenix.xtriage**: Zwart, P.H., Grosse-Kunstleve, R.W., Adams, P.D. (2005) XTRIAGE: Xtriage   and   Fest:   automatic   assessment   of   X-ray   data   and substructure structure factor estimation. *CCP4 newsletter* 43 <br>
WHATCHECK: Hooft, R.W.W., Vriend, G., Sander, C., Abola, E.E. WHATCHECK: Errors in protein structures. (1996) Nature 381, 272-272.<br>
**phenix.refine**: Afonine, P.V., Grosse-Kunstleve, R.W., Echols, N., Headd, J.J., Moriarty, N.W., Mustyakimov, M., Terwilliger, T.C., Urzhumtsev, A., Zwart, P.H., Adams, P.D. (2012) Towards automated crystallographic structure refinement with phenix.refine. *Acta Cryst. D*68, 352-367.<br>
**AUSPEX**: Thorn, A., Parkhurst, J.M., Emsley, P., Nicholls, R., Evans, G., Vollmar, M., Murshudov, G.N. (2017) AUSPEX: a graphical tool for X-ray diffraction data analysis, *Acta Cryst* D73, 729-737. <br> 
**HARUSPEX**: Mostosi, P., Schindelin, H., Kollmannsberger, P., Thorn, A. Haruspex: A Neural Network for the Automatic Identification of Oligonucleotides and Protein Secondary Structure in Cryo‐EM Maps. (2020) *Angew. Chem. (Int. Ed.)* https://doi.org/10.1002/ange.202000421


## Contact information

If you would like to contact us, please write to:
<br>
Dr. Andrea Thorn<br>
andrea.thorn@uni-wuerzburg.de<br>
Rudolf Virchow Center, University of Wuerzburg<br>
Josef-Schneider-Str. 2<br>
97080 Wuerzburg<br>
Germany<br>
<br>
The contents of this repository for research and educational purposes. As a general rule, we do not render any medical advice.
