#!/bin/bash

Rscript -e 'library(methods); shiny::runApp("v1_emd.R", launch.browser=TRUE)' $1