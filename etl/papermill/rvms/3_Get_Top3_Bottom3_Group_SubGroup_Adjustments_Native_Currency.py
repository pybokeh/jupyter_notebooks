# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.2'
#       jupytext_version: 1.1.6
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # PURPOSE:

# %% [markdown]
# ### To obtain the top 3 and bottom 3 GraphCat adjustments in native currency

# %% [markdown]
# **Procedure:** User just has to copy their graphcat data into "clipboard" and then execute all cells in this notebook

# %%
from pathlib import Path
import os
import pandas as pd
import numpy as np
import scrapbook as sb
from win10toast import ToastNotifier
pd.options.display.max_rows=1000
pd.options.display.max_columns=100
pd.options.display.float_format = '{:20,.2f}'.format

# %% [markdown]
# ### Parameters that will be used by the papermill library

# %% {"tags": ["parameters"]}
start_year = 2010
end_year = 2019
CLA_MONTH = '201903'

# %%
nb = sb.read_notebook('D:\\jupyter\\rvms\\production\\output\\RedAndGreenSheet.ipynb')

# For testing
# nb = sb.read_notebook('D:\\jupyter\\rvms\\production\\2_Comparing_Adjusted_GraphCat_CPUs_against_Original_GraphCat_CPUs-Access.ipynb')

# %%
nb.scraps['path_to_red_green_sheet_excel_file'].data

# %% [markdown]
# ### Define where to save the Red and Green raw data file based on CLA claim month:

# %%
base_dir = "//207.130.185.67/aqgbudget2/Cost/Reserve Adjustments/Reports/Normal Reserve Balance Verification/RVMS_Before_After_Checks"
p = Path(base_dir)
save_dir = p / CLA_MONTH
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# %% [markdown]
# ### Now retrieve the Excel file containing the raw "Red and Green Sheet" data:

# %%
df = pd.read_excel(nb.scraps['path_to_red_green_sheet_excel_file'].data)

# %%
df.shape

# %%
df.head()

# %% [markdown]
# ### But we need to limit our data to just the model years that are under RVMS adjustments:

# %%
rvms_years = list(range(start_year, end_year + 1))

# %%
rvms_years

# %%
df = df.query("ModelYear_After in(@rvms_years)")

# %%
df.shape

# %% [markdown]
# ### Create unique list of GraphCat descriptions:

# %%
gc_list = df[['GraphCatID_After','GraphCatDesc_After', 'Planned_Sales_RVMS_After','Budgeted_CPU_GC_Level_After_Minus_Before',
              'Budgeted_CPU_GC_Level_After', 'Budgeted_CPU_GC_Level_Before',
              'Orig_Saturation_CPU_GC_Level_After', 'Cum_Actual_CPU_GC_Level_After']].drop_duplicates()

# %%
gc_list.shape

# %%
gc_list.head()


# %% [markdown]
# ### Create helper functions to Add Model Year, Factory, and Model Name columns:

# %%
def getModelYear(row) -> str:
    # executing strip() also because someone can make a graphcat description with a trailing whitespace
    word_token = row['GraphCatDesc_After'].strip().split()
    
    model_year = word_token[3]
    
    if model_year.isdigit():
        return model_year
    else:
        return word_token[4]

def getFactoryCode(row) -> str:
    # executing strip() also because someone can make a graphcat description with a trailing whitespace
    word_token = row['GraphCatDesc_After'].strip().split()
    factory_code = word_token[1]
    
    return factory_code.upper()

def getModelName(row) -> str:
    # executing strip() also because someone can make a graphcat description with a trailing whitespace
    word_token = row['GraphCatDesc_After'].strip().split()
    model_name = word_token[2]
    
    return model_name.upper()

def getDestCode(row) -> str:
    # executing strip() also because someone can make a graphcat description with a trailing whitespace
    word_token = row['GraphCatDesc_After'].strip().split()
    destination_code = word_token[-1]
    
    return destination_code.upper()


# %% [markdown]
# ### Apply the above functions to create the model year, factory, and model name columns

# %%
gc_list['ModelYear'] = gc_list.apply(getModelYear, axis='columns')
gc_list['Factory'] = gc_list.apply(getFactoryCode, axis='columns')
gc_list['ModelName'] = gc_list.apply(getModelName, axis='columns')
gc_list['DestCodeCustom'] = gc_list.apply(getDestCode, axis='columns')

# %% [markdown]
# #### Let's confirm the new columns were added:

# %%
gc_list.head()

# %% [markdown]
# ### DEPRECATED Create pivot table where ```graphcat description``` is rows and sum of ```CPU_DIFF_SubGroup_Level_x_SALES``` column:

# %% [markdown]
# Basically, this is our list of top total cost adjustments by GraphCat description.

# %%
#total_adj_gc_level = df.pivot_table(values=['CPU_DIFF_SubGroup_Level_x_SALES'], index=['GraphCatDesc_After'], 
                                    #aggfunc='sum').sort_values(by=['CPU_DIFF_SubGroup_Level_x_SALES'], ascending=False)

# %% [markdown]
# ### Create list of total adjustment costs at the GraphCat level:

# %% [markdown]
# Basically, this is our list of top total cost adjustments by GraphCat description.

# %%
total_adj_gc_level = df[['GraphCatDesc_After', 'CPU_DIFF_GC_LEVEL_x_SALES']].drop_duplicates()

# %%
total_adj_gc_level

# %% [markdown]
# ### Create list of CPU differences at the GraphCat level:

# %%
### DEPRECATED ###
# cpu_diff_gc_level = df[['GraphCatDesc_After', 'Budgeted_CPU_GC_Level_After_Minus_Before']].drop_duplicates()

# %%
# cpu_diff_gc_level

# %% [markdown]
# ### Create pivot table where GraphCat-SubGroup is the rows and sum the SubGroup level graphcat CPU adjustments:

# %%
pivot = df.pivot_table(values=['Budgeted_CPU_SubGroup_Level_After_Minus_Before'], index=['GraphCatDesc_After','Group-SubGroup_After'], aggfunc='sum')

# %%
pivot

# %% [markdown]
# ### But...how do we obtain the top 3 and bottom 3 adjustments at the subgroup level??!!  Google search to the rescue!!!

# %% [markdown]
# ### Found this StackOverflow [example](https://stackoverflow.com/questions/45365923/how-to-use-nlargest-on-multilevel-pivot-table-in-pandas)

# %%
top3 = pivot.groupby(level='GraphCatDesc_After')['Budgeted_CPU_SubGroup_Level_After_Minus_Before'].nlargest(3).reset_index(level=0, drop=True).reset_index()
bottom3 = pivot.groupby(level='GraphCatDesc_After')['Budgeted_CPU_SubGroup_Level_After_Minus_Before'].nsmallest(3).reset_index(level=0, drop=True).reset_index()

# %% [markdown]
# ### Now merge or concatenate the 2 data sets together along the row axis direction:

# %%
top3_bottom3 = pd.concat([top3, bottom3], axis='rows')

# %% [markdown]
# #### Sort by GraphCat and SubGroup CPU column in descending order:

# %%
top3_bottom3.sort_values(by=['GraphCatDesc_After','Budgeted_CPU_SubGroup_Level_After_Minus_Before'], ascending=[False, False], inplace=True)

# %%
top3_bottom3.head(12)

# %% [markdown]
# **From above, we can see that for each GraphCat, we have the top 3 subgroup CPU adjustment and bottom 3 subgroup adjustment!**

# %% [markdown]
# ### Merge with the previously created data sets to obtain additional columns:

# %%
### DEPRECATED ###
# top3_bottom3 = pd.merge(top3_bottom3, total_adj_gc_level, how='left', left_on=['GraphCatDesc_After'], right_index=True)
# top3_bottom3 = pd.merge(top3_bottom3, cpu_diff_gc_level, how='left', left_on=['GraphCatDesc_After'], right_on=['GraphCatDesc_After'])
# top3_bottom3 = pd.merge(top3_bottom3, gc_list, how='left', left_on=['GraphCatDesc_After'], right_on=['GraphCatDesc_After'])

# %%
top3_bottom3 = pd.merge(top3_bottom3, total_adj_gc_level, how='left', left_on=['GraphCatDesc_After'], right_on=['GraphCatDesc_After'])
top3_bottom3 = pd.merge(top3_bottom3, gc_list, how='left', left_on=['GraphCatDesc_After'], right_on=['GraphCatDesc_After'])

# %%
top3_bottom3.head(12)

# %% [markdown]
# ### Confirm our data set is sorted by GraphCat total adjustment amount, then GraphCat, and then SubGrpu CPU amount:

# %%
top3_bottom3.sort_values(by=['CPU_DIFF_GC_LEVEL_x_SALES','GraphCatDesc_After','Budgeted_CPU_SubGroup_Level_After_Minus_Before'], 
                                        ascending=[False, False, False], inplace=True)

# %%
top3_bottom3.head(12)

# %% [markdown]
# #### We need a way to "blank out" / "zero out" repeating values in the ```CPU_DIFF_SubGroup_Level_x_SALES``` column and ```Budgeted_CPU_GC_Level_After_Minus_Before``` column.  But how?!

# %% [markdown]
# ### SOLUTION: Create "ROW_NUM" column and then identify rows using the ROW_NUM value.

# %%
top3_bottom3['ROW_NUM'] = top3_bottom3.groupby(['GraphCatDesc_After']).cumcount() + 1

# %%
top3_bottom3.head(6)

# %% [markdown]
# ### Perform IF-ELSE logic to "blank out" / "zero out" repeating values in the 2 columns:

# %%
# If ROW_NUM == 1, then keep the orginal value, otherwise, make it zero/0
top3_bottom3['CPU_DIFF_GC_LEVEL_x_SALES'] = np.where(top3_bottom3['ROW_NUM'] == 1, 
                                                                          top3_bottom3['CPU_DIFF_GC_LEVEL_x_SALES'], 0)
top3_bottom3['Budgeted_CPU_GC_Level_After_Minus_Before'] = np.where(top3_bottom3['ROW_NUM'] == 1, 
                                                                          top3_bottom3['Budgeted_CPU_GC_Level_After_Minus_Before'], 0)
top3_bottom3['Budgeted_CPU_GC_Level_After'] = np.where(top3_bottom3['ROW_NUM'] == 1, 
                                                                          top3_bottom3['Budgeted_CPU_GC_Level_After'], 0)
top3_bottom3['Budgeted_CPU_GC_Level_Before'] = np.where(top3_bottom3['ROW_NUM'] == 1, 
                                                                          top3_bottom3['Budgeted_CPU_GC_Level_Before'], 0)
top3_bottom3['Orig_Saturation_CPU_GC_Level_After'] = np.where(top3_bottom3['ROW_NUM'] == 1, 
                                                                          top3_bottom3['Orig_Saturation_CPU_GC_Level_After'], 0)
top3_bottom3['Cum_Actual_CPU_GC_Level_After'] = np.where(top3_bottom3['ROW_NUM'] == 1, 
                                                                          top3_bottom3['Cum_Actual_CPU_GC_Level_After'], 0)

# %% [markdown]
# ### Let's see if that worked:

# %%
top3_bottom3.head(12)

# %% [markdown]
# #### Nice, it worked!

# %% [markdown]
# ### Rename columns by creating a Python dictionary data structure:

# %%
rename_columns_mapper = {'GraphCatDesc_After': 'GraphCatDesc', 
                         'Group-SubGroup_After': 'Group-SubGroup',
                         'Budgeted_CPU_SubGroup_Level_After_Minus_Before': 'Total_CPU_Adj_at_SubGroup_Level',
                         'CPU_DIFF_GC_LEVEL_x_SALES': 'Total_Adjustment_Cost_Native',
                         'Budgeted_CPU_GC_Level_After_Minus_Before': 'Total_CPU_Adj_at_GraphCat_Level',
                         'GraphCatID_After': 'GraphCatID',
                         'Planned_Sales_RVMS_After': 'Planned_Sales',
                         'Orig_Saturation_CPU_GC_Level_After': 'Orig_Saturation_CPU_GC_Level',
                         'Cum_Actual_CPU_GC_Level_After': 'Cum_Actual_CPU_GC_Level'
                        }

# %% [markdown]
# #### Then apply pandas' ```rename()``` function:

# %%
top3_bottom3.rename(rename_columns_mapper, axis='columns', inplace=True)

# %%
top3_bottom3.head(6)

# %% [markdown]
# ### I want to now re-order columns

# %% [markdown]
# #### Let's get print out of column names:

# %%
top3_bottom3.columns

# %% [markdown]
# #### Now, re-order the column names:

# %%
top3_bottom3 = top3_bottom3[['GraphCatID',
                             'GraphCatDesc',
                             'ModelYear',
                             'Factory',
                             'ModelName',
                             'DestCodeCustom',
                             'Total_Adjustment_Cost_Native',
                             'Total_CPU_Adj_at_GraphCat_Level',
                             'Budgeted_CPU_GC_Level_After',
                             'Budgeted_CPU_GC_Level_Before',
                             'Group-SubGroup',
                             'Total_CPU_Adj_at_SubGroup_Level',
                             'ROW_NUM',
                             'Planned_Sales',
                             'Orig_Saturation_CPU_GC_Level',
                             'Cum_Actual_CPU_GC_Level'
                            ]]

# %%
top3_bottom3.head(6)

# %% [markdown]
# ### We're done!  Now we can export to Excel, to clipboard, etc

# %%
# top3_bottom3.to_excel(r'D:\temp\top3_bottom3.xlsx', index=False)

# %%
file_name = 'top3_bottom3_native.xlsx'

# %%
top3_bottom3.to_excel(save_dir / file_name, index=False)

# %% [markdown]
# ### If script made it this far, send out Windows 10 toast notification:

# %%
toaster = ToastNotifier()
toaster.show_toast("### Job Status ###",
                   "Successfuly Summarized Red and Green Sheet Data to Native Currency",
                   icon_path="images/honda_logo.ico",
                   duration=5)
