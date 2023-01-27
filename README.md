<!-- [![Documentation Status](https://readthedocs.org/projects/cytof-dataanalysis/badge/?version=latest)](https://cytof-dataanalysis.readthedocs.io/en/latest/?badge=latest) -->
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4587193.svg)](https://doi.org/10.5281/zenodo.4587193)

Development branch to add some new functionality related to Dimensionality reduction 
(and perhaps clustering), adding ARM support (for Apple silicon), and improving 
code annotation for our functions.

# **Cy**TOF Si**gn**alling An**al**ysis (*CyGNAL*)

In this repository we present CyGNAL, a pipeline for analysing mass cytometry 
data featured in our 2021 Nature Protocols, Sufi and Qin et al. paper: 
[Multiplexed single-cell analysis of organoid signaling networks](https://doi.org/10.1038/s41596-021-00603-4). 
In [Qin et al. 2020](https://www.nature.com/articles/s41592-020-0737-8) we show 
a practical application to a complex biological system of the data analysis 
enabled by CyGNAL. 

With code in both Python and R, CyGNAL assumes some preliminary and inter-step 
processing through the platform [Cytobank](https://cytobank.org/) (although the 
user could use any other solution for this and the gating steps).

Overview of CyGNAL (dashed blue line) within a standard mass cytometry analysis:
![alt text][Overview]

[Overview]: https://github.com/TAPE-Lab/CyGNAL/blob/master/figs/flowchart_v1.2.png "Overview of CyGNAL"

### Table of contents

* [1.-System requirements](#1-system-requirements)
    * [Dependencies](#dependencies)
* [2.-Using CygNAL](#2-using-cygnal)
    * [Input data](#input-data)
    * [A brief step-by-step tutorial](#a-brief-step-by-step-tutorial)
* [3.-About](#authors)


## 1. System requirements

CyGNAL has been tested on both macOS (from Catalina onwards) and Debian-based 
Linux distributions (including Ubuntu on [WSL](https://github.com/Microsoft/WSL)).

Windows users can run CyGNAL either using Ubuntu through [WSL](https://github.com/Microsoft/WSL)
([available on the windows Store](https://www.microsoft.com/en-gb/p/ubuntu/9nblggh4msv6#activetab=pivot:overviewtab)) 
or installing Docker and using the container (see below).

We suggest users use [Conda](https://docs.conda.io/en/latest/) to setup an 
environment with all necessary dependencies. 
Alternatively a [Docker](https://www.docker.com/) container is also available 
on [dockerhub](https://hub.docker.com/repository/docker/ferranc96/cygnal).

For further details regarding seting up CyGNAL, please refer to the tutorial 
section below.

### Dependencies

* Python: Tested with Python v3.6, v3.7, and v3.8. Used in the backbone of the 
workflow and most computational steps.
    * `fcsparser`
    * `fcswrite`
    * `natsort`
    * `numpy`
    * `pandas`
    * `plotly`
    * `pynndescent`
    * `rpy2`
    * `scprep`
    * `sklearn`
    * `umap-learn`

* R: Tested with v3.6 < R <= v4.0. Mostly used for visualisation, but also for 
computing the PCA.
    * `ComplexHeatmap`
    * `DT`
    * `factoextra`
    * `FactoMineR`
    * `flowCore`
    * `Ggally`
    * `ggrepel`
    * `Hmisc`
    * `MASS`
    * `matrixStats`
    * `plotly`
    * `psych`
    * `RColorBrewer`
    * `shiny`
    * `tidyverse`

* Bourne shell:
    * `Rscript`


## 2. Using CyGNAL

CyGNAL is distributed as a set of directories. The 'code' folder contains the 
main steps, with other utility scripts found in 'code/utils/', to be run as `python` scripts.
Input data should be added to 'Raw_Data' for pre-processing, and processed 
datasets are stored in 'Preprocessed_Data'. Input and output directories for 
the analysis and visualisation steps are found in the 'Analysis' directory.

For detailed step-by-step instructions please read [Sufi and Qin et al. 2021](https://doi.org/10.1038/s41596-021-00603-4). 
Otherwise see the brief tutorial below

### Input data

CyGNAL can take in both FCS and .txt files (as tab-separated dataframes and 
without a header). The 'Raw Data' directory contains sample dataset files. 

*NOTE*: The toy dataset used in this tutorial is a down-sampled version 
(5,000 cells per time point, EpCAM/Pan-CK gated) of the small intestinal 
organoid time-course experiment described in Figure 4 of our [paper](https://www.nature.com/articles/s41592-020-0737-8). 
The full dataset is available through [Cytobank Community](https://community.cytobank.org/cytobank/experiments/81059). 
The users will need to register a free Cytobank Community account to access 
the project and are encouraged to clone the experiments and explore the data in 
further details.

### **A brief step-by-step tutorial**

This here is a brief tutotorial to run all main steps in CyGNAL with a 
sequential order. 

All console commands given assume the user is in the tool's root directory 
(.../CyGNAL/) and moves the relevant data from the ouput folder of the previous 
step to the input of the current.

With the toy datasets present by default in the 'Raw_Data' folder, running the
full set of steps within CyGNAL should take less than 15 minutes in total. 
Keep in mind however that runtimes will scale with bigger, or multiple, datasets.
<!-- (Refer to the Nature Protocols paper for more in-depth instructions) -->

0. **(SETUP):** Clone (or download) the repository and ensure you have all 
necessary software and dependencies.
    * We strongly encourage using [conda](https://docs.conda.io/en/latest/miniconda.html) 
    to setup an environment with the following command once CyGNAL has been downloaded:
        * `conda env create -f conda_env.yml`: This command creates a conda 
        environment named *cygnal* that contains all necessary dependencies. 
        It needs to be **run only once** when dowloading CyGNAL for the first time 
        (or after a major update)
        * `conda activate cygnal`: This command ensures that CyGNAL's conda 
        environment is active and ready to use. It needs to be **run each session**.
        
    * Alternatively, if you have Docker installed in your machine, you can use 
    a Docker container 
    [available on dockerhub](https://hub.docker.com/repository/docker/ferranc96/cygnal). 
    If using the container we suggest the following workflow:
        * Clone CyGNAL on your home directory: 
        `git clone https://github.com/TAPE-Lab/CyGNAL.git ~/CyGNAL_docker`
        * Run the CyGNAL docker container:
        `docker run -v ~/CyGNAL_docker/:/usr/app/CyGNAL -it --entrypoint /bin/bash -p 12241-12252:12241-12252 ferranc96/cygnal:one`
            * The command above runs a live terminal on the container with a 
            conda environment that already contains all necessary dependencies. 
            Communication with the host machine is done via the shared 
            directory in ~/CyGNAL_docker (i.e. where you will need to input 
            data and fetch CyGNAL's outputs), with open ports for the Heatmap 
            and PCA shinyApps.

            * This *docker run* command is to be run everytime the user wants 
            to use CyGNAL through docker.

1. **Pre-process:** Copy all the data files to the 'Raw_Data' folder and run
`1-data_preprocess.py`. The output files with their antibody panel processed 
(i.e. measured channels decluttered, empty channels deleted, cell-index assigned) 
will be saved in the 'Preprocessed_Data' folder, together with a *'panel_markers.csv'* 
file listing all the markers measured in the given experiment.
    * `python code/1-data_preprocess.py`

    *Optional (if exporting .txt datasets from Cytobank):* Go to the working 
    illustration page (Illustrations - My working illustration), highlight the 
    population(s) of interest, and export events as untransformed text files 
    (Actions - Export - Export events, with *'Include header with FCS filename'* unchecked).

    *Note:* This step is essential for getting the dataset compatible with 
    downstream analysis and has to be performed as the first step in our 
    workflow.

2. **UMAP:** Move the processed data file(s) and panel_marker.csv to 'Analysis/UMAP_input'. 
Edit *'panel_markers.csv'* to set all the markers used for UMAP analysis from 'N' to 'Y'. 
Run `2-umap.py`, and the output files will be saved within the 'Analysis/UMAP_output' folder. 
The markers and the indices of the cells used in the analysis will also be saved in the new folder.
    * `python code/2-umap.py`
   
   *Note:* When there is more than one data file used as input of the analysis, 
   each data file can be downsampled to the lowest number of the input 
   (i.e. 'equal' sampling) and concatenated prior to UMAP calculation. 
   After the calculation is complete, the concatenated dataset as well as each 
   individual condition are saved with their UMAP coordinates attached.

3. **EMD:** To perform EMD calculation (using the tools available in the 
[scprep](https://github.com/KrishnaswamyLab/scprep) library), copy the input 
data files to 'Analysis/EMD_input'. Run `3-emd.py` and follow the instructions. 
By default, the reference of the EMD calculation will be the concatenation 
of all the input data files, but the user is given the option to provide a 
specific reference data file. While EMD scores of all channels can be 
calculated, the default behaviour requires the user to place the *'panel_markers.csv'* 
in the input folder to specifiy which markers are to be used. 
The calculated EMD scores will be saved in 'Analysis/EMD_output', within the 
'EMD_arc_no_norm' column in the saved file.
    * `python code/3-emd.py`

4. **DREMI:** To perform DREMI calculation (using the tools available in the 
[scprep](https://github.com/KrishnaswamyLab/scprep) library) copy the input 
data files to 'Analysis/DREMI_input'. Run `4-dremi.py` and follow the 
instructions. As with EMD, DREMI scores of all permutations of marker 
combinations can be calculated, but we suggest specifying the markers of 
interest by modifying the *'panel_markers.csv'* file. 
The calculated DREMI scores will be saved in 'Analysis/DREMI_output'.
    * `python code/4-dremi.py`
    
    *Optional:* The user is given the option to save the density-resampled 
    plots for data inspection and to perform a standard deviation-based outlier 
    removal step prior to DREMI calculation.

5. **Heatmap:** To visualise EMD/DREMI scores in heatmaps, copy the EMD/DREMI 
calculation outputs to the 'Analysis/Vis_Heatmap' folder. 
Run `5v1-htmp.py` and follow the instructions in the GUI. The script accepts 
only one EMD data file and one DREMI data file (with 'EMD' and 'DREMI' in their 
file names respectively) to be visualised.
    * `python code/5v1-htmp.py`

6. **Principal component analysis (PCA):** To perform PCA and visualise the 
results, copy the EMD/DREMI calculation outputs to the 'Analysis/Vis_PCA' folder. 
Run `5v2-pca.py` and follow the instructions in the GUI.
    * `python code/5v2-pca.py`


## 3. About

### Support

For any queries or issues regarding CyGNAL please check the 
[Issues](https://github.com/TAPE-Lab/CyGNAL/issues) section in this repository.
Alternatively you can also email Ferran Cardoso at 
[ferran.cardoso.19@ucl.ac.uk](mailto:ferran.cardoso.19@ucl.ac.uk).

### Authors

The work here is actively being developed by 
Ferran Cardoso ([@FerranC96](https://github.com/FerranC96)) and 
Dr. Xiao Qin ([@qinxiao1990](https://github.com/qinxiao1990)). 
Based also on original work by Pelagia Kyriakidou.

### The group

Repository of the [Cell Communication Lab](http://tape-lab.com/) at UCL's 
Cancer Institute. 

The Cell Communication Lab studies how oncogenic mutations communicate with 
stromal and immune cells in the colorectal cancer (CRC) tumour microenvironment (TME). 
By understanding how mutations regulate all cell types within a tumour, 
we aim to uncover novel approaches to treat cancer.

>We acknowledge the work of all third-parties whose packages are used in CyGNAL.
