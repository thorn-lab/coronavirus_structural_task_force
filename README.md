![logo](https://github.com/thorn-lab/coronavirus_structural_task_force/blob/master/outreach/new_banner.png)

# CORONAVIRUS STRUCTURAL TASKFORCE

A global public resource for the structures from beta-coronavirus with a focus on SARS-CoV and SARS-CoV-2.

## What is this?

This repository is a global public resource for the structures from beta-coronavirus with a focus on SARS-CoV and SARS-CoV-2.
You can find here:
* The original files for 19 of the 28 proteins in SARS-CoV and SARS-CoV-2, over 300 different structures.
* Re-refined structures from different contributors(*)
* Validation statistics for these and the original structural models
* Diagnostic data for the quality of the experimental data

(*) Please be aware that while there is potential to improve some structures, this is not meant as criticism of the great achievements of the research groups who were able to initially elucidate these structures. It merely reflects on the potential to push our methods to their limit.

## Why?

We are methods developers in structural biology. During this time of crisis, we decided to put our brains to where our hearts are. We hope this can make a (small) difference for the cure of COVID-19.

## Download for non-git users

This is a project in progress. While we strongly suggest users to work with Git so that they can synchronize with us conveniently, there is also a possibility to fetch the most recent update as a zip package by clicking the Green Button "Clone or download" and "Download Zip". If you only want a part of the data (for example a certain PDB entry or a certain file type from all PDB entries), then you download the python script [git_fetch.py](https://github.com/thorn-lab/coronavirus_structural_task_force/raw/master/utils/git_fetch.py). You need a working python to use it, and it works like this from your command line:<br>
Usage:<br>
```python git_fetch.py -A kw1,kw2 [-P prefix_dir]```
<br><br>
Examples:<br>
Download all txt files in 6vww entry: ```python git_fetch.py -A 6vww,txt```
<br>
Download all reflection files for all PDB entries to /home/user: ```python git_fetch.py -A -sf.mtz -P /home/user```
<br>
Download all data in the methyltransferase subdirectory: ```python git_fetch.py -A methyltransferase```

## Total number of COVID structures by experimental methods

X-ray Crystallography: 1017
<br>
3D Electron Microscopy: 371
<br>
Solution NMR: 30
<br>
Solid-State NMR: 1
<br>
Neutron Diffraction: 2

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

`validation/auspex/`<br>
These are results of the analysis of deposited diffraction data with [AUSPEX](www.auspex.de). AUSPEX can help to detect problems in experimental setup, integration, scaling and conversion from intensities to amplitudes.

`ccpem/`<br>
These are manual re-refinements made with the [CCP-EM suite](https://www.ccpem.ac.uk/), done by Agnel Praveen Joseph. Maps were optimized with LocScale, then refined with refmac and Coot and validated with Validation:Model in the CCP-EM interface.

`isolde/`<br>
These are manual re-refinements from [ISOLDE](https://isolde.cimr.cam.ac.uk/what-isolde/) in [ChimeraX](https://www.cgl.ucsf.edu/chimerax/), done by Tristan Croll. Structures were energy-minimised, visually checked residue-by-residue and, where necessary, rebuilt. Crystal structures were further refined with [phenix.refine](https://www.phenix-online.org/documentation/reference/refinement.html).

## Bored? 
Watch us refine structures! https://www.twitch.tv/taskforcec19

## Further resources
https://www.ebi.ac.uk/pdbe/covid-19<br>
All available PDB data for SARS-CoV-2 proteins, highlighting small molecule binding sites and protein-protein interactions<br><br>
https://www-structmed.cimr.cam.ac.uk/COVID19_Open_Structures.html<br>
The COVID-19 Open Structures initiative enables biologists with unsolved or partly solved structures to elucidate them much quicker in an open-science effort.<br><br>
https://www.globalphasing.com/buster/wiki/index.cgi?Covid19<br>
re-processing and re-refinement of several SARS-CoV-2 structures<br><br>
https://covid-19.bioreproducibility.org/<br>
A resource providing assessment of the quality of SARS-CoV-2 drug target models, including corrected versions of some of these models<br><br> 
https://www.diamond.ac.uk/covid-19/for-scientists.html<br>
Info on Diamond work on main protease; related: https://covid.postera.ai/covid<br><br>
https://www.ebi.ac.uk/ena/pathogens/covid-19<br>
Data resources held at EMBL-EBI relating to the COVID-19 outbreak, including sequences of outbreak isolates and records relating to coronavirus biology<br><br>
http://www.hecbiosim.ac.uk/covid-19<br>
Links for covid19 related research that falls into biomolecular modelling and simulation <br><br>
https://www.rcsb.org/news?year=2020&article=5e74d55d2d410731e9944f52&feature=true<br>
Various links to COVID-19/SARS-CoV-2 Resources from RCSB PDB<br><br>
https://www.compbiomed.eu/compbiomed-and-coronavirus/<br>
CompBioMed is a consortium redirecting research effort and funding to computational investigations that will improve our understanding of the SARS-CoV-2 virus, COVID-19, and accelerate the development of treatment options, including antiviral drugs and vaccines.<br><br>
http://predictioncenter.org/caspcommons/index.cgi<br>
SARS-2-CoV structure modelling initiative<br><br>
https://instruct-eric.eu/news/resources-information-and-collaborations-to-support-covid-19-research/<br>
Resources, funding and collaborations regarding COVID-19 research<br><br><br>
https://falconierivisuals.com/wp-content/uploads/2020/03/20034_SARSCoV2_Spike_InfographicFalconieriV5-scaled.jpg<br>
Poster on Spike protein function<br>


## Contributors

This is a collaborative effort. These are the current contributors (in order of joining):<br><br>
Universitaet Hamburg, Germany -<br>
[Andrea Thorn - Group leader](https://www.uni-wuerzburg.de/en/rvz/research/associated-research-groups/thorn-group/)<br>
Yunyun Gao - Postdoc in the AUSPEX project (www.auspex.de)<br>
Kristopher Nolte - Biochemistry B.Sc. student<br>
Ferdinand Kirsten - Biochemistry B.Sc. student<br>
Sabrina Stäb - Biochemistry M.Sc. student<br>
<br>
European Synchrotron Facility, Grenoble, France -<br>
Gianluca Santoni - Serial crystallography data scientist<br>
<br>
CIMR, University of Cambridge, UK -<br>
[Tristan Croll - Research associate](https://isolde.cimr.cam.ac.uk/what-isolde/)<br><br>
Duke University -<br>
[The Richardson Laboratory](http://kinemage.biochem.duke.edu/)<br><br>
Diamond Light Source, UK -<br>
Sam Horrell - Postdoctoral Researcher<br>
CCP_EM, STFC, UK -<br>
Agnel Praveen Joseph - Researcher<br>

We would also like to thank: Manfred Weiss *(HBZ BESSY, Berlin, Germany)* , James Holton *(ALS/Lawrence Berkeley National Laboratory, Berkeley, USA)*, Gerard Bricogne *(Global Phasing, Cambridge, UK)*, Clemens Vonrhein *(Global Phasing, Freiburg, Germany)*, Robbie P. Joosten *(The Netherlands Cancer Institute, Amsterdam, Netherlands)*, Sameer Velankar *(European Potein Data Bank, Cambridge, UK)*.

## References
**PDB-REDO**: Joosten, R.P., Long, F., Murshudov, G.N., Perrakis, A. (2014) The PDB_REDO server for macromolecular structure model optimization. *IUCrJ* 1, 213-220. <br>
**ISOLDE**: Croll, T.I. (2018) ISOLDE: a physically realistic environment for model building into low-resolution electron-density maps. *Acta Cryst. D*74, 519-530. <br>
**ChimeraX**:  Goddard, T.D., Huang, C.C., Meng, E.C., Pettersen, E.F., Couch, G.S., Morris, J.H., Ferrin, T.E. (2018) UCSF ChimeraX: Meeting modern challenges in visualization and analysis. *Protein Sci.* 27, 14-25.
**Coot**: Emsley, P., Lohkamp, B., Scott, W.G., Cowtan, K. (2010) Features and Development of Coot. *Acta Cryst. D*66, 486-501.<br>
**phenix.xtriage**: Zwart, P.H., Grosse-Kunstleve, R.W., Adams, P.D. (2005) XTRIAGE: Xtriage   and   Fest:   automatic   assessment   of   X-ray   data   and substructure structure factor estimation. *CCP4 newsletter* 43 <br>
WHATCHECK: Hooft, R.W.W., Vriend, G., Sander, C., Abola, E.E. WHATCHECK: Errors in protein structures. (1996) Nature 381, 272-272.<br>
**phenix.refine**: Afonine, P.V., Grosse-Kunstleve, R.W., Echols, N., Headd, J.J., Moriarty, N.W., Mustyakimov, M., Terwilliger, T.C., Urzhumtsev, A., Zwart, P.H., Adams, P.D. (2012) Towards automated crystallographic structure refinement with phenix.refine. *Acta Cryst. D*68, 352-367.<br>
**AUSPEX**: Thorn, A., Parkhurst, J.M., Emsley, P., Nicholls, R., Evans, G., Vollmar, M., Murshudov, G.N. (2017) AUSPEX: a graphical tool for X-ray diffraction data analysis, *Acta Cryst D*73, 729-737. <br> 
**HARUSPEX**: Mostosi, P., Schindelin, H., Kollmannsberger, P., Thorn, A. (2020) Haruspex: A Neural Network for the Automatic Identification of Oligonucleotides and Protein Secondary Structure in Cryo‐EM Maps. *Angew. Chem. (Int. Ed.)* https://doi.org/10.1002/ange.202000421<br>
**CCP-EM**: Burnley. T., Palmer, C.M., Winn, M.D. (2017) Recent developments in the CCP-EM software suite. *Acta Cryst. D*73, 469 - 477. <br>
**REFMAC**: Murshudov, G.N., Vagin, A.A., Dodson, E.J. (1997) Refinement of Macromolecular Structures by the Maximum-Likelihood method. *Acta Cryst. D*53, 240-255. <br> 
**COOT**: Emsley, P., Lohkamp, B., Scott, W.G., Cowtan, K. (2010) Features and Development of Coot. *Acta Cryst D*66, 486-501 <br>
**LOCSCALE**: Jakobi, A. J., Wilmann, M., Sachse, C. (2017) Model-based local density sharpening of cryo-EM maps. *Elife* 6:e27131 doi: 10.7554/eLife.27131
<br>
## Contact information

If you would like to contact us, please write to:
<br>
Dr. Andrea Thorn<br>
andrea.thorn@uni-hamburg.de<br>
HARBOR (Institute for Nanostructure and Solid State Physics), Universität Hamburg<br>
Luruper Chaussee 149 / Bldg. 610 | 22761 Hamburg | Germany<br>
Tel. +49 (0)40 42838 3651<br>
www.thorn-lab.de | www.insidecorona.de<br>
<br>
The contents of this repository website are for research and educational purposes only. As a general rule, we do not render any medical advice.
