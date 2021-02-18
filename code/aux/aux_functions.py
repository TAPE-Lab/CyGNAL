
import os
import re
import sys

import fcsparser
import numpy as np
import pandas as pd
import umap


#Read broken FCS through r.flowCore
def read_rFCS(file_path):
    from rpy2.robjects import globalenv, pandas2ri, r
    from rpy2.robjects.packages import importr
    from rpy2.rinterface_lib.callbacks import logger
    import logging
    logger.setLevel(logging.ERROR)
    
    pandas2ri.activate()
    flowcore = importr("flowCore")
    base = importr("base")
    arg_transf = "transformation=FALSE"
    raw_FCS = flowcore.read_FCS(str(file_path), transformation=False,)
    r('''
        marker_names<-function(FF){
            return(flowCore::markernames(FF))
        }
        FF2dframe<-function(FF){
        if(class(FF) == "flowFrame"){
            return(as.data.frame(exprs(FF)))}
        else {
            stop("Object is not of type flowFrame")}
        }    
    ''')
    fcs_columns = globalenv["marker_names"](raw_FCS)
    df_file = globalenv["FF2dframe"](raw_FCS)
    if not isinstance(fcs_columns,np.ndarray): #Error checking for StrVector output from rpy2
        print("CALLUM'S ERROR. CONTACT @FerranC96")
        print(type(fcs_columns),": ", fcs_columns)
        columns_list = []
        for i in fcs_columns:
            print(i)
            columns_list.append(i)
        fcs_columns = columns_list
    else:
        fcs_columns = fcs_columns.tolist()
    if not isinstance(df_file,pd.core.frame.DataFrame):
        print("CALLUM'S ERROR. CONTACT @FerranC96")
        print(type(df_file),": ", df_file)
        for i in df_file:
            print(i)
    original_columns = df_file.columns.values.tolist()
    filtered_columns = []
    try:
        reg_markers = re.compile("(\d+Di$)")#|_dist$)") #All isotopes + debarcoder info
        reg_filter = re.compile("^\d+[A-Za-z]+")
        match_list=[]
        for i in original_columns:
            if reg_markers.search(i):
                match_list.append(i)
        for i in fcs_columns:
            if reg_filter.search(i):
                filtered_columns.append(i)
        if len(filtered_columns)==len(match_list) and len(filtered_columns)!=0:
            for new_n,old_n in zip(filtered_columns,match_list):
                df_file.rename({old_n: new_n}, axis="columns", inplace=True)
            no_filter=False
        elif len(match_list)==0 and len(filtered_columns)!=0: #Columns already have PnS?
            preprocessed_cols = []
            for i in original_columns:
                preprocessed_cols.append(i)
            if preprocessed_cols==filtered_columns: #Indeed, PnS and "PnN" match!
                print("WARNING: FCS was already processed. Keeping original columns")
                no_filter=False
            else:
                raise ValueError
        else:
            print("WARNING: $PnS (desc in flowCore) and $PnN channels don't match")
            print("marker PnS",fcs_columns)
            print("marker PnN (original column names)", match_list)
            raise ValueError
    except ValueError:
        print("ERROR: Couldn't read $PnS channel names")
        print("No filtering will be performed. Please manually rename your channels")
        no_filter=True #Not applying filtering to avoid losing unwated cols

    return df_file, no_filter

#Arcsinh transform the data
def arcsinh_transf(cofactor, no_arc):
    #Select only the columns containing the markers (as they start with a number for the isotope)
    cols = [x for x in no_arc.columns if x[0].isdigit()]
    #Apply the arcsinh only to those columns (don't want to change time or any other)
    arc = no_arc.apply(lambda x: np.arcsinh(x/cofactor) if x.name in cols else x)
    # put back the 'file_origin' column to the arcsinh-transformed data
    if "file_origin" in  no_arc.columns:
        arc["file_origin"] = no_arc["file_origin"]
    # else:
    #     print ("(there was no concatenation prior to transforming)")
    return arc, cols

#Function to concatenate all files: Read input .txt and .fcs. Sanity check. Concatenate
def concatenate_fcs(input_dir):
    txt_filelist = [f for f in os.listdir(input_dir) if f.endswith(".txt")]
    fcs_filelist = [f for f in os.listdir(input_dir) if f.endswith(".fcs")]
    filelist = txt_filelist+fcs_filelist
    if len(filelist)==0:
        sys.exit (f"ERROR: There are no files in {input_dir}!")
    no_arc = pd.DataFrame()
    #Add counter to keep track of the number of files in input -> 
    # -> cell ID will be a mix of these (Filenumber | filename.txt)
    fcounter = 0
    for i in filelist:
        file_path = f"{input_dir}/{i}"
        name = i.split('.')[0]
        fcounter += 1
        if i in txt_filelist:
            print (i)
            df = pd.read_csv(file_path, sep = '\t')
        else:
            try: #Use fcsparser to read the fcs data files
                print(i)
                df = fcsparser.parse(file_path, meta_data_only=False)[1]
                reg_pnn = re.compile("(\d+Di$)") #Detect if, despite flag
                pnn_extracted=[]                 #columns match PnN pattern
                for n in df.columns.values.tolist():
                    if reg_pnn.search(n):
                        pnn_extracted.append(n)
                if len(pnn_extracted)!=0:
                    raise fcsparser.api.ParserFeatureNotImplementedError
            except fcsparser.api.ParserFeatureNotImplementedError:
                print("WARNING: Non-standard .fcs file detected: ", i)
                #use rpy2 to read the files and load into python
                df = read_rFCS(file_path)[0]
        
        # add a new column of 'file_origin' that will be used to separate each file after umap calculation
        df["file_identifier"] = name
        df["file_origin"] = str(fcounter)+" | "+ name 
        #File+ID #This way the cell-index will be preserved after Cytobank upload
        try:
            df["Sample_ID-Cell_Index"] = df["Cell_Index"].apply(
                                            lambda x: str(fcounter)+"-"+str(x))
        except KeyError:
            sys.exit("ERROR: Cell_Index missing from data. Have you preprocessed it?")
        no_arc = no_arc.append(df, ignore_index=True)
    return no_arc, filelist

#Function to concatenate all files and save as txt -> DEPRECATE IN THE NEAR FUTURE!
def concatenate_save(input_dir, output_dir):
    input_files = [f for f in os.listdir(input_dir) if f.endswith(".txt")]
    concat = pd.DataFrame()
    #Add counter to keep track of the number of files in input -> 
    # -> cell ID will be a mix of these (Filenumber | filename.txt)
    fcounter = 0
    for file in input_files:
        name = file.split('.txt')[0]
        fcounter += 1
        df = pd.read_csv(f"{input_dir}/{file}", sep = '\t')
        df["file_origin"] = str(fcounter)+" | "+ name # add a new column of 'file_origin' that will be used to separate each file after umap calculation
        df["Sample_ID-Cell_Index"] = df["Cell_Index"].apply(
                                        lambda x: str(fcounter)+"-"+str(x)) #File+ID #This way the cell-index will be preserved after Cytobank upload
        # df["Cell_Index"] = df["Cell_Index"].apply(lambda x: str(fcounter)+"-"+str(x)) #File+ID
        concat = concat.append(df, ignore_index=True)
    print("Concatenating...")
    concat.to_csv(f'{output_dir}/concat_{name}.txt', index = False, sep = '\t')
    print(f"Concatenated file saved as:\nconcat_{name}.txt")

#Downsample dataframe by column and save to file which IDs were removed
def downsample_data(no_arc, info_run, output_dir, 
                    split_bycol="file_identifier"): 
    downsampled_dframe = no_arc.copy()
    #Defiine downsampling size (N) per file: at least N cells in all input files
    downsample_size = downsampled_dframe[split_bycol].value_counts().min() 
    print ("Working with ", downsample_size, " cells per split")
    #Group by file+origin and sample without replacement -> 
    # thus we can sample file for which len(file)=N without -tive consequences 
    reduced_df = downsampled_dframe.groupby(split_bycol).apply(lambda x:
                                                    x.sample(downsample_size))
    # reduced_df['new-cell-index'] = list(range(len(reduced_df.index)))
    # reduced_df['post_downsample-cell_index'] = reduced_df.index
    
    #Create new file to store downsampling status for all cell IDs
    new_df = pd.DataFrame()
    os.makedirs(f'{output_dir}/{info_run}', exist_ok = True)
    new_df["Sample_ID-Cell_Index"] = no_arc["Sample_ID-Cell_Index"]
    new_df["In_donwsampled_file"] = new_df["Sample_ID-Cell_Index"].isin(
                                    reduced_df["Sample_ID-Cell_Index"])
    new_df.to_csv(f"{output_dir}/{info_run}/{info_run}_downsampled_IDs.csv", 
                    index = False)
    no_arc = no_arc[no_arc["Sample_ID-Cell_Index"].isin(
                reduced_df["Sample_ID-Cell_Index"])]
    return reduced_df 

# Random downsampling of a dataframe to n rows
def downsample_df(df, n):
    df_downsampled = df.sample(n)
    return df_downsampled

#Function to read a .csv file of the panel's markers with some to be selected
def read_marker_csv(input_dir):
    marker_files = [f for f in os.listdir(f"{input_dir}") if f.endswith(".csv")]
    if len(marker_files) != 1: #Sanity check
        sys.exit("ERROR: There should be ONE .csv file with the markers to use in the input folder!")
    else: #Get markers flagged for use
        marker_file = pd.read_csv(f"{input_dir}/{marker_files[0]}", header=None)
        selected_markers = marker_file.loc[marker_file[1] == "Y", [0]].values.tolist()
        selected_markers = [item for sublist in selected_markers for item in sublist]
    return selected_markers

def write_panel_emd(df, input_dir):
    all_markers = list(set(df['marker']))
    counter_marker = []
    for i in all_markers:
        counter_marker.append("Y")
    markers = pd.DataFrame(list(zip(all_markers, counter_marker)))
    markers.to_csv(f"{input_dir}/panel_markers.csv", index=False, header=False)

def write_panel_dremi(df, input_dir):
    all_markers = list(set(df['marker_x']))
    counter_marker = []
    for i in all_markers:
        counter_marker.append("Y")
    markers = pd.DataFrame(list(zip(all_markers, counter_marker)))
    markers.to_csv(f"{input_dir}/panel_markers.csv", index=False, header=False)

#Simple yes or no input function (default NO)
def yes_or_NO(question, default="NO"):
    if default.lower() == "no":
        while True:
            reply = str(input(question+' (y/[N]): ')).lower().strip()
            if reply[:1] == 'y':
                return True
            elif reply[:1] == 'n':
                return False
            elif reply[:1] == "":
                return False
            else:
                print ("Please answer Y or N")
    elif default.lower() == "yes":
        while True:
            reply = str(input(question+' ([Y]/n): ')).lower().strip()
            if reply[:1] == 'y':
                return True
            elif reply[:1] == 'n':
                return False
            elif reply[:1] == "":
                return True
            else:
                print ("Please answer Y or N")
