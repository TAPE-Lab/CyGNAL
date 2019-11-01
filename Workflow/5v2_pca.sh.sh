#!/bin/bash

Rscript -e 'library(methods); shiny::runApp("5v2_pca.R", launch.browser=TRUE)' $1