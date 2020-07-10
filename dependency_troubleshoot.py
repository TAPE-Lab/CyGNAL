#Script to test if all necessary dependencies have been installed:
import sys

python_packages =["fcsparser","fcswrite","rpy2","numpy","OpenSSL.version","os",
                    "pandas","scprep","subprocess","umap","warnings"]

for i in python_packages:
    try:
        import i
    except:
        print ("WARNING!: Python package ",i, " is not installed properly. Please install it manually")

try:
    from rpy2.robjects import r
except:
    sys.exit("ERROR: rpy2 python package is missing and we can not test for missing R packages")



r('''
    #Packages to use:
    list.of.packages <- c("DT", 
                            "GGally",
                            "psych",
                            "Hmisc",
                            "MASS",
                            "RColorBrewer",
                            "shiny",
                            "tidyverse",
                            "FactoMineR",
                            "factoextra",
                            "matrixStats",
                            "plotly"
                            )
    # check if pkgs are installed already, if not, install automatically:
    new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
    if(length(new.packages)) install.packages(new.packages, repos = "http://cran.us.r-project.org")
    #Load packages
    lapply(list.of.packages, require, character.only = TRUE)    
    ''')