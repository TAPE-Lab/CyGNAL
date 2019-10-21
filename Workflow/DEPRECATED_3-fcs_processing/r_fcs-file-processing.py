# To add a new cell, type '#%%'
# To add a new markdown cell, type '#%% [markdown]'
#%% Change working directory from the workspace root to the ipynb file location. Turn this addition off with the DataScience.changeDirOnImportExport setting
# ms-python.python added
import os
try:
	os.chdir(os.path.join(os.getcwd(), '../../../../../../var/folders/hw/fqkcybzs3gq_bksy6wfr534m0000gr/T'))
	print(os.getcwd())
except:
	pass

#%%
# clean up the environment
rm(list = ls())
library(flowCore)
library(CATALYST)


#%%
getwd()
setwd(file.path(getwd(), paste("input", sep = "")))
filelist <- list.files(pattern = ".fcs")
print(filelist)


#%%
for(i in 1:length(filelist)){
  write.FCS(read.FCS(filelist[i]), filelist[i])
}


#%%
# to concatenate the fcs files
launchGUI()

