[![Documentation Status](https://readthedocs.org/projects/cytof-dataanalysis/badge/?version=latest)](https://cytof-dataanalysis.readthedocs.io/en/latest/?badge=latest)
# **Cy**TOF Si**gn**alling An**al**ysis (*CyGNAL*)

Repository of the [Cell Communication Lab](http://tape-lab.com/) at UCL's Cancer Institute. The Cell Communication Lab studies how oncogenic mutations communicate with stromal and immune cells in the colorectal cancer (CRC) tumour microenvironment (TME). By understanding how mutations regulate all cell types within a tumour, we aim to uncover novel approaches to treat cancer.

In this repo we present *CyGNAL*, a pipeline for analysing mass cytometry data similar to that used in our *Nature Methods* paper: [Cell-type-specific signaling networks in heterocellular organoids](https://www.nature.com/articles/s41592-020-0737-8). With code in both Python and R, CyGNAL assumes some preliminary and inter-step processing through the platform [Cytobank](https://cytobank.org/) (although the user could in theory use any other solution for this and the gating steps).

Overview of the current workflow:
![alt text][Overview]

[Overview]: https://github.com/TAPE-Lab/CyGNAL/blob/master/figs/flowchart_v1.png "Overview of cell identification"

## How to use

Main steps in code folder. Various utilities can be found in code/utils.

Raw data contains sample dataset files. Pipeline can take in both FCS and .txt files (as tab-separated dataframes).


*NOTE*: The dataset used in this tutorial is a down-sampled version (5,000 cells per time point, EpCAM/Pan-CK gated) of the small intestinal organoid time-course experiment described in Figure 4 of our [paper](https://www.nature.com/articles/s41592-020-0737-8). The full dataset is available through [Cytobank Community](https://community.cytobank.org/cytobank/experiments/81059). The users will need to register a free Cytobank Community account to access the project and are encouraged to clone the experiments and explore the data in further details.

### A Brief Step-by-Step Tutorial

<!-- (Refer to the Nature Protocols paper for more in-depth instructions) -->

1. **(SETUP):** Clone the repository and ensure you have all necessary software and dependencies.

2. **Pre-process:** Copy all the data files to the 'Raw_Data' folder and run `1-data_preprocess.py`. The output files with their antibody panel processed (i.e. measured channels decluttered, empty channels deleted, cell-index assigned) will be saved in the 'Preprocessed_Data' folder, together with a *'panel_markers.csv'* file listing all the markers measured in the given experiment.

    *Optional (if exporting .txt datasets from Cytobank):* Go to the working illustration page (Illustrations - My working illustration), highlight the population(s) of interest, and export events as untransformed text files (Actions - Export - Export events, with *'Include header with FCS filename'* unchecked).

    *Note:* This step is essential for getting the dataset compatible with downstream analysis and has to be performed as the first step in our workflow.

3. **UMAP:** Move the processed data file(s) and panel_marker.csv to 'Analysis/UMAP_input'. Edit *'panel_markers.csv'* to set all the markers used for UMAP analysis from 'N' to 'Y'. Run `2-umap.py`, and the output files will be saved within the 'Analysis/UMAP_output' folder. The markers and the indices of the cells used in the analysis will also be saved in the new folder.

   *Note:* When there is more than one data file used as input of the analysis, each data file can be downsampled to the lowest number of the input (i.e. 'equal' sampling) and concatenated prior to UMAP calculation. After the calculation is complete, the concatenated dataset as well as each individual condition are saved with their UMAP coordinates attached.

4. **EMD:** To perform EMD calculation (using the tools available in the [scprep](https://github.com/KrishnaswamyLab/scprep) library), copy the input data files to 'Analysis/EMD_input'. Run `3-emd.py` and follow the instructions. By default, the denominator of the EMD calculation will be the concatenation of all the input data files, but the user is given the option to provide a specific denominator data file. While EMD scores of all channels can be calculated by default, by default the user should place the *'panel_markers.csv'* in the input folder to specifiy which marker are to be used. The calculated EMD scores will be saved in 'Analysis/EMD_output', within the 'EMD_arc_no_norm' column in the saved file.

5. **DREMI:** To perform DREMI calculation (using the tools available in the [scprep](https://github.com/KrishnaswamyLab/scprep) library) copy the input data files to 'Analysis/DREMI_input'. Run `4-dremi.py` and follow the instructions. As with EMD, DREMI scores of all permutations of marker combinations can be calculated, but we suggest specifying the markers of interest by modifying the *'panel_markers.csv'* file. The calculated DREMI scores will be saved in 'Analysis/DREMI_output'.

    *Optional:* The user is given the option to save the density-resampled plots for data inspection and to perform a standard deviation-based outlier removal step prior to DREMI calculation.

6. **Heatmap:** To visualise EMD/DREMI scores in heatmaps, copy the EMD/DREMI calculation outputs to the 'Analysis/Vis_Heatmap' folder. Run `5v1-emd_dremi_htmp.py` and follow the instructions in the GUI. The script accepts only one EMD data file and one DREMI data file (with 'EMD' and 'DREMI' in their file names respectively) to be visualised.

7. **Principal component analysis (PCA):** To perform PCA and visualise the results, copy the EMD/DREMI calculation outputs to the 'Analysis/Vis_PCA' folder. Run `5v2-pca.py` and follow the instructions in the GUI.

## Dependencies

We strongly encourage using [conda](https://docs.conda.io/en/latest/miniconda.html) to setup an environment from 'conda_env.yml'.

* Python: Tested with Python v3.6 and v3.7. Used in the backbone of the workflow and most computational steps.
    * `fcsparser`
    * `fcswrite`
    * `numpy`
    * `pandas`
    * `plotly`
    * `rpy2`
    * `scprep`
    * `sklearn`
    * `umap-learn`

* R: Tested with R v3.6.1 and RStudio v1.2.5001. Mostly used for visualisation, but also for computing the PCA.
    * `DT`
    * `factoextra`
    * `FactoMineR`
    * `flowCore`
    * `Ggally`
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

## Authors

The work here is actively being developed by Ferran Cardoso ([@FerranC96](https://github.com/FerranC96)) and Dr. Xiao Qin ([@qinxiao1990](https://github.com/qinxiao1990)). 
Based also on original work by Pelagia Kyriakidou.
