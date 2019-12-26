# CyTOF_Data Analysis

Repository of the [Cell Communication Lab](http://tape-lab.com/) at UCL's Cancer Institute. The Cell Communication Lab studies how oncogenic mutations communicate with stromal and immune cells in the colorectal cancer (CRC) tumour microenvironment (TME). By understanding how mutations regulate all cell types within a tumour, we aim to uncover novel approaches to treat cancer.

In this repo we present a workflow for analysing mass cytometry data similar to that used in our pre-print: [Single-Cell Signalling Analysis of Heterocellular Organoids](https://www.biorxiv.org/content/10.1101/659896v2). With code in both Python and R, the workflow assumes some preliminary and inter-step processing through the platform [Cytobank](https://cytobank.org/) (although the user could in theory use any other solution for this and the gating steps).

Provisional flowchart of the current workflow:
![alt text][Overview]

[Overview]: https://github.com/TAPE-Lab/CyTOF_DataAnalysis/blob/master/figs/provisional_Flowchart.png "Overview of cell identification"

## How to use

*NOTE*: The dataset used in this tutorial is a down-sampled version (5,000 cells per time point, EpCAM/Pan-CK gated) of the small intestinal organoid time-course experiment described in Figure 4 of our [pre-print](https://www.biorxiv.org/content/10.1101/659896v2). The full dataset is available through [Cytobank Community](https://community.cytobank.org/cytobank/experiments/81059). The users will need to register a free Cytobank Community account to access the project and are welcome to clone the experiments and explore the data in further details.

### A Brief Step-by-Step Tutorial

1. Clone the 'Workflow' and 'Data' folder to a local drive.

   *Optional (if exporting data from Cytobank):* Go to the working illustration page (Illustrations - My working illustration), highlight the population(s) of interest, and export events as untransformed text files (Actions - Export - Export events, with *'Include header with FCS filename'* unchecked).

2. Copy all the data files to the folder 'Workflow/input/1-data_preprocess'. Run 1-data_preprocess.py, and the output files with their antibody panel processed (i.e. measured channels decluttered, empty channels deleted, cell-index assigned) will be saved in the 'Workflow/output/1-data_preprocess' folder, together with a 'panel_markers.csv' file listing all the markers measured in the give experiment. 

    *Note:* This step is essential for getting the dataset compatible with downstream analysis and has to be performed as the first step in our workflow.

3. **UMAP:** Move the processed data file(s) and panel_marker.csv to 'Workflow/input/2-umap', edit panel_marker.csv to set all the markers used for UMAP analysis from 'N' to 'Y'. Run 2-umap.py, and the output files will be saved in a subfolder named by the 'umap_info' provided by the user in the 'Workflow/output/2-umap' folder. The markers and the indices of the cells used in the analysis will also be saved in the new folder.

   *Note:* When there is more than one data file used as input of the analysis, each data file will be downsampled to the lowest number of the input (i.e. 'equal' sampling) and concatenated prior to UMAP calculation. After the calculation is complete, the concatenated dataset as well as each individual condtion are saved with their UMAP coordinates attached.

   *Optional (skipped in this tutorial):* The data files can be uploaded to Cytobank and visualised and gated in the UMAP space for cell-type and cell-state analysis.

4. **EMD:** To perform EMD calculation, copy the input data files (in this case all the 5,000 cells per time-point in the tutorial dataset prior to cell-type identification) to 'Workflow/input/3-emd'. Run 3-emd.py and follow the instructions. By default, the denominator of the EMD calculation will be the concatenation of all the input data files, but the user is given the option to provide a specific denominator data file. The calculated EMD scores will be saved in 'Workflow/output/3-emd', and column 'EMD_arc_no_norm' is of interest.

5. **DREMI:** To perform EMD calculation, copy the input data files (in this case all the 5,000 cells per time-point in the tutorial dataset prior to cell-type identification) to 'Workflow/input/4-dremi'. Run 4-dremi.py and follow the instructions. The calculated DREMI scores will be saved in 'Workflow/output/4-dremi'.

6. **Heatmap:** To visualise EMD/DREMI scores in heatmaps, copy the EMD/DREMI calculation outputs to the 'Workflow/input/5v1-emd_dremi_htmp' folder. Run 5v1-emd_dremi_htmp.py and follow the instructions in the GUI.

7. **Principal component analysis (PCA):** To perform PCA and visualise the results, copy the EMD/DREMI calculation outputs to the 'Workflow/input/5v2-pca' folder. Run 5v2-pca.py and follow the instructions in the GUI.

## Dependencies

* Python: Tested with Python v3.6 and v3.7. Used in the bakcbone of the workflow and most computational steps.
    * `numpy`
    * `pandas`
    * `plotly`
    * `scprep`
    * `sklearn`
    * `umap-learn`

* R: Tested with R v3.6.1 and RStudio v1.2.5001. Mostly used for visualisation, but also for computing the PCA
    * `DT`
    * `factoextra`
    * `FactoMineR`
    * `Ggally`
    * `Hmisc`
    * `MASS`
    * `matrixStats`
    * `plotly`
    * `psych`
    * `RColorBrewer`
    * `shiny`
    * `tabplot`
    * `tidyverse`

* Bourne shell:
    * `Rscript`

## Authors

The work here is actively being developed by Ferran Cardoso ([@FerranC96](https://github.com/FerranC96)) and Dr. Xiao Qin ([@qinxiao1990](https://github.com/qinxiao1990)). Based on the original work of Pelagia Kyriakidou.
