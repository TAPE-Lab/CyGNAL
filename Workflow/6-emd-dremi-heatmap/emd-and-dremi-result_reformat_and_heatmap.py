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
from IPython import get_ipython


#%%
import os, glob
import pandas as pd
import numpy as np
from scipy.stats import zscore
import holoviews as hv
from IPython.core.interactiveshell import InteractiveShell


#%%
import rpy2.robjects as ro
from rpy2.robjects.packages import importr 
from rpy2.robjects import pandas2ri

from rpy2.robjects.conversion import localconverter

pandas2ri.activate()
get_ipython().magic(u'load_ext rpy2.ipython')


#%%
get_ipython().run_cell_magic(u'R', u'', u'# clean up the environment\nrm(list = ls())\n\n# load dependencies\nlibrary("ggplot2")\nlibrary("RColorBrewer")\nlibrary("forcats")')


#%%
# wide cells
hv.extension("bokeh", width=90)
# display all output in each cell
InteractiveShell.ast_node_interactivity = "all"


#%%
# Prepare file list
filelist = [f for f in os.listdir(f"./input") if f.endswith(".csv") or f.endswith(".txt")]
filelist


#%%
# read the data file into a pandas dataframe; mind the index and sep
# df = pd.read_csv(os.path.join('./input', 'figure-2_stem_all-event_dremi_info.txt'), sep = '\t')
df = pd.read_csv(os.path.join('./input', filelist[0]), sep = '\t', index_col = 0)
df.head()
# df.columns.values
# df.shape

#%% [markdown]
# ### DREMI

#%%
# Remove unused columns for DREMI
df = df.loc[:,['file', 'marker_x', 'marker_y', 'with_outliers_arcsinh_DREMI_score']]

df.head()
# df.shape


#%%
# removal of non-PTMs -- DREMI

row_to_remove = [r for r in df.marker_x if '113In_CEACAM1' in r or '113In_EpCAM' in r or '115In_Pan-CK' in r or
                '127I_IdU' in r or '130Te_TePhe' in r or '143Nd_C-MYC' in r or '144Nd_Lysozyme' in r or 
                '145Nd_FABP1' in r or '145Nd_Na_K-ATPase' in r or '162Dy_LRIG1' in r or '169Tm_GFP' in r or 
                '170Er_Arginase-1' in r or '171Yb_F4_80' in r  or '171Yb_CLCA1' in r or '173Yb_DCAMKL1' in r or 
                '173Yb_PDPN' in r or '174Yb_CHGA' in r or '174Yb_RFP' in r or '175Lu_CD44' in r or 
                '176Yb_Cyclin B1' in r or '209Bi_CD68' in r]

df = df.loc[~df.marker_x.isin(row_to_remove)]

df.shape

row_to_remove = [r for r in df.marker_y if '113In_CEACAM1' in r or '113In_EpCAM' in r or '115In_Pan-CK' in r or
                '127I_IdU' in r or '130Te_TePhe' in r or '143Nd_C-MYC' in r or '144Nd_Lysozyme' in r or 
                '145Nd_FABP1' in r or '145Nd_Na_K-ATPase' in r or '162Dy_LRIG1' in r or '169Tm_GFP' in r or 
                '170Er_Arginase-1' in r or '171Yb_F4_80' in r  or '171Yb_CLCA1' in r or '173Yb_DCAMKL1' in r or 
                '173Yb_PDPN' in r or '174Yb_CHGA' in r or '174Yb_RFP' in r or '175Lu_CD44' in r or 
                '176Yb_Cyclin B1' in r or '209Bi_CD68' in r]

df = df.loc[~df.marker_y.isin(row_to_remove)]

df.shape


#%%
# make a new column for 'x_y' DREMI pairs
for row in df.iterrows():
    df['x_y'] = df['marker_x'] + '_' + df['marker_y']  
df.head()

# df = df.loc[:,['condition', 'x_y', 'with_outliers_arcsinh_DREMI_score']]
df = df.loc[:,['file', 'x_y', 'with_outliers_arcsinh_DREMI_score']]
df.head()


#%%
# Rename columns for DREMI
df.columns = ['condition', 'x_y', 'dremi']
df.head()

#%% [markdown]
# #### Keep the curated list of dremi pairs (figure 1 and figure 2)

#%%
# keep the curated list of dremi pairs (figure 1 and figure 2)
row_to_keep = [r for r in df.x_y if '148Nd_pSRC_146Nd_pMKK4_SEK1' in r or
              '148Nd_pSRC_170Er_pMEK1_2' in r or
              '148Nd_pSRC_157Gd_pMKK3_MKK6' in r or
              '157Gd_pMKK3_MKK6_158Gd_pP38 MAPK' in r or
              '158Gd_pP38 MAPK_159Tb_pMAPKAPK2' in r or
              '159Tb_pMAPKAPK2_153Eu_pCREB' in r or
              '170Er_pMEK1_2_167Er_pERK1_2'in r or
              '167Er_pERK1_2_163Dy_pP90RSK' in r or
              '163Dy_pP90RSK_153Eu_pCREB' in r or
              '163Dy_pP90RSK_161Dy_pBAD' in r or
              '148Nd_pSRC_164Dy_pP120-Catenin' in r or
              '148Nd_pSRC_141Pr_pPDPK1' in r or
              '141Pr_pPDPK1_151Eu_pPKCa' in r or
              '141Pr_pPDPK1_152Sm_pAKT T308' in r or
#               '152Sm_pAKT T308_161Dy_pBAD' in r or
              '166Er_pGSK3b_165Ho_Beta-Catenin_Active' in r or
              '152Sm_pAKT T308_149Sm_p4E-BP1' in r or
              '152Sm_pAKT T308_172Yb_pS6' in r or
              '155Gd_pAKT S473_149Sm_p4E-BP1' in r or
              '155Gd_pAKT S473_172Yb_pS6' in r or
              '160Gd_pAMPKa_155Gd_pAKT S473' in r or
              '147Sm_pBTK_156Gd_pNF-kB p65' in r]

# keep the curated list of dremi pairs (figure 3)
# row_to_keep = [r for r in df.x_y if '148Nd_pSRC_146Nd_pMKK4_SEK1' in r or
#               '148Nd_pSRC_144Nd_pMEK1_2' in r or
#               '148Nd_pSRC_157Gd_pMKK3_6' in r or
#               '157Gd_pMKK3_6_158Gd_pP38' in r or
#               '158Gd_pP38_159Tb_pMAPKAPK2' in r or
#               '159Tb_pMAPKAPK2_153Eu_pCREB' in r or
#               '144Nd_pMEK1_2_167Er_pERK1_2'in r or
#               '167Er_pERK1_2_163Dy_pP90RSK' in r or
#               '163Dy_pP90RSK_153Eu_pCREB' in r or
#               '163Dy_pP90RSK_161Dy_pBAD' in r or
#               '148Nd_pSRC_164Dy_pP120-Catenin' in r or
#               '148Nd_pSRC_141Pr_pPDK1' in r or
#               '141Pr_pPDK1_151Eu_pPKCa' in r or
#               '141Pr_pPDK1_152Sm_pAKT T308' in r or
##               '152Sm_pAKT T308_161Dy_pBAD' in r or
#               '166Er_pGSK3b_165Ho_Beta-Catenin_Active' in r or
#               '152Sm_pAKT T308_149Sm_p4E-BP1' in r or
#               '152Sm_pAKT T308_172Yb_pS6' in r or
#               '155Gd_pAKT S473_149Sm_p4E-BP1' in r or
#               '155Gd_pAKT S473_172Yb_pS6' in r or
#               '160Gd_pAMPKa_155Gd_pAKT S473' in r or
#               '147Sm_pBTK1_156Gd_pNF-kB' in r or 
#               '148Nd_pSRC_169Tm_pSTAT3' in r]

df = df.loc[df.x_y.isin(row_to_keep)]
df.head()
df.shape

# row_to_keep


#%%
for i, r in df.iterrows():
    if 'enterocyte' in r['condition']:
        df.at[i, 'condition'] = '01_Enterocytes'
    if 'goblet' in r['condition']:
        df.at[i, 'condition'] = '02_Goblet'
    if 'tuft' in r['condition']:
        df.at[i, 'condition'] = '03_Tuft'
    if 'enteroendocrine' in r['condition']:
        df.at[i, 'condition'] = '04_Enteroendocrine'
    if 'paneth' in r['condition']:
        df.at[i, 'condition'] = '05_Paneth'
    if 'stem' in r['condition']:
        df.at[i, 'condition'] = '06_Stem'


#%%
df


#%%
df.to_csv(os.path.join('./output', 'figure-2_stem_all-event_dremi_info_for-heatmap.csv'), index = False)

#%% [markdown]
# ### EMD

#%%
# Remove unused columns for EMD
df = df.loc[:,['marker', 'EMD_no_norm_arc', 'compare_from']]
df.head()
# df.shape


#%%
# # removal of non-PTMs -- EMD (Figure 1 & 3)
# row_to_remove = [r for r in df.marker if '113In_CEACAM1' in r or '113In_EpCAM' in r or '115In_Pan-CK' in r or
#                 '127I_IdU' in r or '130Te_TePhe' in r or '143Nd_C-MYC' in r or '144Nd_Lysozyme' in r or 
#                 '145Nd_FABP1' in r or '145Nd_Na_K-ATPase' in r or '162Dy_LRIG1' in r or '169Tm_GFP' in r or 
#                 '170Er_Arginase-1' in r or '171Yb_F4_80' in r  or '171Yb_CLCA1' in r or '173Yb_DCAMKL1' in r or 
#                 '173Yb_PDPN' in r or '174Yb_CHGA' in r or '174Yb_RFP' in r or '175Lu_CD44' in r or 
#                 '176Yb_Cyclin B1' in r or '209Bi_CD68' in r or 'pHH3' in r]

# # removal of non-PTMs -- EMD with new order (Figure 2)
# row_to_remove = [r for r in df.marker if '113In_CEACAM1' in r or '113In_EpCAM' in r or '115In_Pan-CK' in r or
#                 '127I_IdU' in r or '130Te_TePhe' in r or '143Nd_C-MYC' in r or '144Nd_Lysozyme' in r or 
#                 '145Nd_FABP1' in r or '145Nd_Na_K-ATPase' in r or '162Dy_LRIG1' in r or '169Tm_GFP' in r or 
#                 '170Er_Arginase-1' in r or '171Yb_F4_80' in r  or '171Yb_CLCA1' in r or '173Yb_DCAMKL1' in r or 
#                 '173Yb_PDPN' in r or '174Yb_CHGA' in r or '174Yb_RFP' in r or '175Lu_CD44' in r or 
#                 '176Yb_Cyclin B1' in r or '209Bi_CD68' in r or '89Y_pHH3' in r or '157Gd_pMKK3_6' in r or '209Bi_DiMeHH3' in r]

# df = df.loc[~df.marker.isin(row_to_remove)]

# keep cell-ID markers -- EMD (Figure 1)
row_to_keep = [r for r in df.marker if 'Lysozyme' in r or 'FABP1' in r or 'LRIG1' in r or 'CLCA1' in r or 'DCAMKL1' in r or 'CHGA' in r]
df = df.loc[df.marker.isin(row_to_keep)]

# keep LRIG1+ and GFP+ populations
# row_to_keep = [r for r in df.compare_from if 'LRIG1' in r or 'GFP' in r]
# df = df.loc[df.compare_from.isin(row_to_keep)]

# Histone modifications
# row_to_remove_histone = [r for r in df.marker if 'pHH3' in r or '209Bi_DiMeHH3' in r]
# df = df.loc[~df.marker.isin(row_to_remove_histone)]

df.shape


#%%
# Rename columns for EMD
df.columns = ['marker', 'emd', 'condition']
df = df[['condition', 'marker', 'emd']]
df.head()


#%%
for i, r in df.iterrows():
    if 'LRIG1' in r['marker']:
        df.at[i, 'marker'] = '01_LRIG1'
    if 'Lysozyme' in r['marker']:
        df.at[i, 'marker'] = '02_Lysozyme'
    if 'CHGA' in r['marker']:
        df.at[i, 'marker'] = '03_CHGA'
    if 'DCAMKL1' in r['marker']:
        df.at[i, 'marker'] = '04_DCAMKL1'
    if 'CLCA1' in r['marker']:
        df.at[i, 'marker'] = '05_CLCA1'
    if 'FABP1' in r['marker']:
        df.at[i, 'marker'] = '06_FABP1'


#%%
for i, r in df.iterrows():
    if 'enterocyte' in r['condition']:
        df.at[i, 'condition'] = '01_Enterocytes'
    if 'goblet' in r['condition']:
        df.at[i, 'condition'] = '02_Goblet'
    if 'tuft' in r['condition']:
        df.at[i, 'condition'] = '03_Tuft'
    if 'enteroendocrine' in r['condition']:
        df.at[i, 'condition'] = '04_Enteroendocrine'
    if 'paneth' in r['condition']:
        df.at[i, 'condition'] = '05_Paneth'
    if 'stem' in r['condition']:
        df.at[i, 'condition'] = '06_Stem'


#%%
df

#%% [markdown]
# ## Heatmap (ggplot2 in R)

#%%
get_ipython().run_cell_magic(u'R', u'-i df', u'typeof(df)\nhead(df)\nrange(df$emd)')

#%% [markdown]
# ### EMD

#%%
get_ipython().run_cell_magic(u'R', u'-i df', u'\n# emd\n\n# the order of the rows are controlled by using \'y = marker\' or \'y = factor(marker, levels=rev(unique(marker)))\'\nheatmap <- ggplot(data = df, aes(x = fct_rev(condition), y = fct_rev(marker))) +\n  geom_tile(aes(fill = emd))\n\n# define the range of the colour scale here\n\nlower = -1.5\nupper = 1.5\nlower_s = paste(\'<\', toString(lower), sep = "", collapse = NULL)\nupper_s = paste(\'<\', toString(upper), sep = "", collapse = NULL)\n\nheatmap_new_palette <- heatmap + \nscale_fill_distiller(palette = "RdBu", limits=c(lower, upper), oob = scales::squish, breaks = c(lower, upper), labels = c(lower_s, upper_s), guide = guide_colourbar(nbin=100, draw.ulim = FALSE, draw.llim = FALSE, ticks = FALSE)) + \ntheme(legend.position="bottom", legend.direction="horizontal") + ggtitle("") + xlab("") + ylab("") +\ntheme(axis.text.x = element_text(angle = 45, hjust = 1))\n\n# preview the heatmap\nheatmap_new_palette\n\n# save the heatmap\n# ggsave("EMD_lrig1_validation_revision.pdf", plot = heatmap_new_palette)')

#%% [markdown]
# ### DREMI

#%%
get_ipython().run_cell_magic(u'R', u'-i df', u'\n# dremi\n\n# the order of the rows are controlled by using \'y = x_y\' or \'y = factor(x_y, levels=rev(unique(x_y)))\'\nheatmap <- ggplot(data = df, aes(x = condition, y = factor(x_y, levels=rev(unique(x_y))))) +\n  geom_tile(aes(fill = dremi))\n\n# define the range of the colour scale here\nheatmap_new_palette <- heatmap + \nscale_fill_gradient(low = "#F6F6F6", high = "#A12014", limits=c(0.08, 0.75), oob = scales::squish, breaks = c(0.1, 0.75), labels = c(\'<0.1\', \'>0.75\'), guide = guide_colourbar(nbin=100, draw.ulim = FALSE, draw.llim = FALSE, ticks = FALSE)) + \ntheme(legend.position="bottom", legend.direction="horizontal") + ggtitle("") + xlab("") + ylab("") +\ntheme(axis.text.x = element_text(angle = 45, hjust = 1))\n\n# preview the heatmap\nheatmap_new_palette\n# ggsave("figure-1_dremi_heatmap_ordered.pdf", plot = heatmap_new_palette)')

#%% [markdown]
# ## Miscelleanous
# ### Fiugre 3: TOBis mapping

#%%
# set conditions for Figure 3

for index, row in df.iterrows():
    if row['condition'] == 'WT':
        df.at[index,'condition'] = '01_WT'
    if row['condition'] == 'WT-M0':
        df.at[index,'condition'] = '02_WT-M0'
    if row['condition'] == 'WT-mCF-1':
        df.at[index,'condition'] = '03_WT-mCF-1'
    if row['condition'] == 'WT-mCF-1-M0':
        df.at[index,'condition'] = '04_WT-mCF-1-M0'
    if row['condition'] == 'A':
        df.at[index,'condition'] = '05_A'
    if row['condition'] == 'A-M0':
        df.at[index,'condition'] = '06_A-M0'
    if row['condition'] == 'A-mCF-1':
        df.at[index,'condition'] = '07_A-mCF-1'
    if row['condition'] == 'A-mCF-1-M0':
        df.at[index,'condition'] = '08_A-mCF-1-M0'
    if row['condition'] == 'AK':
        df.at[index,'condition'] = '09_AK'
    if row['condition'] == 'AK-M0': 
        df.at[index,'condition'] = '10_AK-M0'
    if row['condition'] == 'AK-mCF-1':
        df.at[index,'condition'] = '11_AK-mCF-1'
    if row['condition'] == 'AK-mCF-1-M0':
        df.at[index,'condition'] = '12_AK-mCF-1-M0'
    if row['condition'] == 'AKPm':
        df.at[index,'condition'] = '13_AKPm'
    if row['condition'] == 'AKPm-M0':
        df.at[index,'condition'] = '14_AKPm-M0'
    if row['condition'] == 'AKPm-mCF-1':
        df.at[index,'condition'] = '15_AKPm-mCF-1'
    if row['condition'] == 'AKPm-mCF-1-M0':
        df.at[index,'condition'] = '16_AKPm-mCF-1-M0'
    if row['condition'] == 'M0':
        df.at[index,'condition'] = '17_M0'
    if row['condition'] == 'mCF-1':
        df.at[index,'condition'] = '18_mCF-1'
    if row['condition'] == 'mCF-1-M0':
        df.at[index,'condition'] = '19_mCF-1-M0'
        
df.head()
# df.shape

df = df.sort_values(by=['condition'])
df.head()


#%%
# New TOBis order!!

for index, row in df.iterrows():
    if '01' in row['condition']:
        df.at[index,'condition'] = 'WT'
    if '02' in row['condition']:
        df.at[index,'condition'] = 'WT-M0'
    if '03' in row['condition']:
        df.at[index,'condition'] = 'WT-mCF-1'
    if '04' in row['condition']:
        df.at[index,'condition'] = 'WT-mCF-1-M0'
    if '05' in row['condition']:
        df.at[index,'condition'] = 'A'
    if '06' in row['condition']:
        df.at[index,'condition'] = 'A-M0'
    if '07' in row['condition']:
        df.at[index,'condition'] = 'A-mCF-1'
    if '08' in row['condition']:
        df.at[index,'condition'] = 'A-mCF-1-M0'
    if '09' in row['condition']:
        df.at[index,'condition'] = 'AK'
    if '10' in row['condition']:
        df.at[index,'condition'] = 'AK-M0'
    if '11' in row['condition']:
        df.at[index,'condition'] = 'AK-mCF-1'
    if '12' in row['condition']:
        df.at[index,'condition'] = 'AK-mCF-1-M0'
    if '13' in row['condition']:
        df.at[index,'condition'] = 'AKPm'
    if '14' in row['condition']:
        df.at[index,'condition'] = 'AKPm-M0'
    if '15' in row['condition']:
        df.at[index,'condition'] = 'AKPm-mCF-1'
    if '16' in row['condition']:
        df.at[index,'condition'] = 'AKPm-mCF-1-M0'
    if '17' in row['condition']:
        df.at[index,'condition'] = 'M0'
    if '18' in row['condition']:
        df.at[index,'condition'] = 'mCF-1'
    if '19' in row['condition']:
        df.at[index,'condition'] = 'mCF-1-M0'
        
df.head()
# df.shape

df = df.sort_values(by=['condition'])
df.head()


#%%
df.to_csv('macrophage-cell-type_cond-tobis-02_04_06_08_10_12_14_16_17_19_dremi_for-heatmap.csv', index = False)

#%% [markdown]
# ### z-score

#%%
# z-score calculation (peli)
df_1 = (df - df.mean(axis = 0)) / df.std(axis = 0)
df_1.head()
# df_1.mean(axis = 0)
# df_1.std(axis = 0)


#%%
# z-score calculation (scipy)
df_zscore = df.apply(zscore, ddof = 1)
df_zscore.head()


#%%
df_zscore.to_csv('stem_all-event_emd_for-heatmap_wide_zscore.csv', index = True)

