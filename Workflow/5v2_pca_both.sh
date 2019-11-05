#!/bin/bash

Rscript -e 'library(methods); shiny::runApp("5v2_pca_emd.R", launch.browser=TRUE)' $1 &
Rscript -e 'library(methods); shiny::runApp("5v2_pca_dremi.R", launch.browser=TRUE)' $1 &
