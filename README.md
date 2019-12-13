# CyTOF_Data Analysis

Repository of the [Cell Communication Lab](http://tape-lab.com/) at UCL's Cancer Institute. The Cell Communication Lab studies how oncogenic mutations communicate with stromal and immune cells in the colorectal cancer (CRC) tumour microenvironment (TME). By understanding how mutations regulate all cell types within a tumour, we aim to uncover novel approaches to treat cancer.

In this repo we present a workflow for analysing mass cytometry data similar to that used in our pre-print: [Single-Cell Signalling Analysis of Heterocellular Organoids](https://www.biorxiv.org/content/10.1101/659896v2). With code in both Python and R, the workflow assumes some preliminary and inter-step processing through the platform [Cytobank](https://cytobank.org/) (although the user could in theory use any other solution for this and the gating steps).

Provisional flowchart of the current workflow:
![alt text][Overview]

[Overview]: https://github.com/TAPE-Lab/CyTOF_DataAnalysis/blob/master/figs/provisional_Flowchart.png "Overview of cell identification"

*MISSING*: Explain the workflow, when we move from code to cytobank, and what kind of data we have as I/O. Add proper documentation and tutorial.

## How to use

*NOTE*: The data contained here has been trimmed to minimise file size while mantaining educational purposes of the scripts

### A tutorial should go here

1. First step
2. Second step
3. ....

## Dependencies

* Python: Tested with Python v3.6 and v3.7. Use in the bakcbone of the workflow and most computational steps.
    * `numpy`
    * `pandas`
    * `plotly`
    * `scprep`
    * `sklearn`
    * `umap-learn`

* R: Tested with R v3.6.1 and RStudio v1.2.5001. Mostly used for visualisation, but also for computing the PCA
    * `packages`

## Authors

The work here is actively being developed by Ferran Cardoso ([@FerranC96](https://github.com/FerranC96)) and Dr. Xiao Qin ([@qinxiao1990](https://github.com/qinxiao1990)). Based on the original work of Pelagia Kyriakidou.
