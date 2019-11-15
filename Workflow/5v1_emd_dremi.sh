#!/bin/bash

Rscript -e 'library(methods); shiny::runApp("5v1_emd.R", launch.browser=TRUE)' $1 &
Rscript -e 'library(methods); shiny::runApp("5v1_dremi.R", launch.browser=TRUE)' $2 &
