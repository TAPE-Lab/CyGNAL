#Script to test if all necessary dependencies have been installed:
import sys, importlib

python_packages =["copy","fcsparser","fcswrite","itertools","numpy","pandas",
                    "plotly","pynndescent","re","rpy2","scprep","sklearn",
                    "subprocess","umap"]
#copy, itertools, re, subprocess -> come with Python
count=0
for i in python_packages:
    try:
        importlib.import_module(i)
        count +=1
    except:
        print ("WARNING!: Python package ",i, " is not installed properly. Please install it manually")
if len(python_packages)==count:
    print("All Python packages are installed!")

try:
    from rpy2.robjects import r
except:
    sys.exit("ERROR: rpy2 python package is missing and we can not test for missing R packages")


r('''
    #Packages to use:
    list.of.packages <- c(
                            "ComplexHeatmap", 
                            "DT",
                            "factoextra",
                            "FactoMineR",
                            "flowCore",
                            "GGally",
                            "Hmisc",
                            "MASS",
                            "matrixStats",
                            "plotly",
                            "psych",
                            "RColorBrewer",
                            "shiny",
                            "tidyverse"
                        )
    # check if pkgs are already installed:
    new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
    if(length(new.packages)) {
        print(paste0("WARNING!: Missing R package(s): ", new.packages))
        # print("Attempting to install missing R package(s)...")
        # install.packages(new.packages, repos = "http://cran.us.r-project.org")
        # lapply(list.of.packages, require, character.only = TRUE) #Load packages
    } else {
        print("All R packages are installed!")
    }
    ''')
