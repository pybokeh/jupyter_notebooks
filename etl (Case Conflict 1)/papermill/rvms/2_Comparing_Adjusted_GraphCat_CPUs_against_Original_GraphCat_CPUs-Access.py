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
# # Comparing Before Budgeted CPU versus After Budgeted CPU

# %% [markdown]
# ### This creates the raw "Red and Green" sheet master data

# %% [markdown]
# ### Overall Process

# %% [markdown]
# - Get current or "After" budgeted CPU file
# - Get "Before" budgeted CPU file
# - Merge between the 2 using full OUTER JOIN
# - Create 2 new columns:
#     1. After Budgeted CPU minus Before Budgeted CPU (at group-subgroup level)
#     2. After Budgeted CPU minus Before Budgeted CPU (at GraphCat level)
# - Export to Excel and save in ```\\207.130.185.67\aqgbudget2\Cost\Reserve Adjustments\Reports\Normal Reserve Balance Verification\RVMS_Before_After_Checks``` folder

# %%
from datetime import datetime
from dateutil import relativedelta
from pathlib import Path
import os
import pandas as pd
import pyodbc
import scrapbook as sb
import time
from win10toast import ToastNotifier
pd.options.display.max_rows=1000
pd.options.display.max_columns=100

# %% [markdown]
# ### Enter CLA Claim Month:

# %%
# If using papermill, have to comment this out.  It doesn't support getting input from the user
# CLA_MONTH = input("Enter CLA Claim Month ('YYYYMM'): ")

# %% {"tags": ["parameters"]}
CLA_MONTH = '201903'

# %% [markdown]
# ### Define where to save the Red and Green raw data file based on CLA claim month:

# %%
base_dir = "//207.130.185.67/aqgbudget2/Cost/Reserve Adjustments/Reports/Normal Reserve Balance Verification/RVMS_Before_After_Checks"
p = Path(base_dir)
save_dir = p / CLA_MONTH
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# %% [markdown]
# ### Define where to retrieve the current budgeted CPUs ("after" CPUs):

# %%
current_cpu_dir = Path("//207.130.185.67/aqgbudget2/Cost/Reserve Adjustments/Reports/Normal Reserve Balance Verification/RVMS_Current_Budgeted_CPUs/" 
                       + CLA_MONTH + "/All_Plants_Budgeted_CPU_By_Group_SubGroup.xlsx")

# %% [markdown]
# #### Now fetch the "after" CPUs:

# %%
cpu_after = pd.read_excel(current_cpu_dir)

# %%
cpu_after.shape

# %%
cpu_after['Group-SubGroup'] = cpu_after['GRP_NM'].map(str) + ' - ' + cpu_after['SUBGRP_NM'].map(str)

# %%
cpu_after.head()

# %%
after_column_names = [col + '_After' for col in cpu_after.columns]

# %%
after_column_names

# %%
cpu_after.columns = after_column_names

# %%
cpu_after.head()

# %% [markdown]
# #### Get "Before" budgeted CPU file and rename columns:

# %%
conn_str = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            r'DBQ=\\207.130.185.67\aqgbudget2\Cost\Reserve Adjustments\Reports\databases\RVMS.accdb;'
           )
cnxn = pyodbc.connect(conn_str)
cursor = cnxn.cursor()

sql = """
SELECT
    *
    
FROM tbl_Historical_Budgeted_CPU

WHERE
    RVMS_Claim_Month = (SELECT max(tbl_Historical_Budgeted_CPU.[RVMS_Claim_Month]) FROM tbl_Historical_Budgeted_CPU)
"""

try:
    cpu_before = pd.read_sql(sql, cnxn)
    #cpu_before = pd.read_sql(sql, cnxn)
    
    # Close connections
    cursor.close()
    cnxn.close()
except:
    print("Error connecting to database")
    cursor.close()
    cnxn.close()

# %%
cpu_before.shape

# %%
cpu_before.head()

# %%
before_column_names = [col + '_Before' for col in cpu_before.columns]

# %%
cpu_before.columns = before_column_names

# %%
cpu_before.head()

# %%
try:
    assert cpu_before.shape[0] == cpu_after.shape[0]
except:
    toaster = ToastNotifier()
    toaster.show_toast("### ERROR ###",
                   "Number of rows don't match between CPU after and CPU before data sets",
                   icon_path=None,
                   duration=5)
    print('ERROR!!! - Number of rows do not match between CPU after and CPU before data sets')

# %% [markdown]
# ### Merge the after CPU data set with the before CPU data set

# %%
cpu_before_after_merge = pd.merge(cpu_after, cpu_before, how='outer', 
                                  left_on=['GraphCatID_After','GRP_NM_After','SUBGRP_NM_After'], 
                                  right_on=['GraphCatID_Before','GRP_NM_Before','SUBGRP_NM_Before']
                                 )

# %%
cpu_before_after_merge.shape

# %%
cpu_before_after_merge.head()

# %% [markdown]
# ### Create columns that represent the before and after CPUs at GraphCat level, subgroup level, and total adjustment costs

# %%
cpu_before_after_merge['Budgeted_CPU_SubGroup_Level_After_Minus_Before'] = cpu_before_after_merge['Budgeted_CPU_SubGroup_Level_After'] \
                                                            - cpu_before_after_merge['Budgeted_CPU_SubGroup_Level_Before']
cpu_before_after_merge['Budgeted_CPU_GC_Level_After_Minus_Before'] = cpu_before_after_merge['Budgeted_CPU_GC_Level_After'] \
                                                                     - cpu_before_after_merge['Budgeted_CPU_GC_Level_Before']
cpu_before_after_merge['CPU_DIFF_SubGroup_Level_x_SALES'] = cpu_before_after_merge['Budgeted_CPU_SubGroup_Level_After_Minus_Before'] \
                                                      * cpu_before_after_merge['Planned_Sales_RVMS_After']
cpu_before_after_merge['CPU_DIFF_GC_LEVEL_x_SALES'] = cpu_before_after_merge['Budgeted_CPU_GC_Level_After_Minus_Before'] \
                                                      * cpu_before_after_merge['Planned_Sales_RVMS_After']

# %%
cpu_before_after_merge.head()

# %% [markdown]
# ### Define file name format:

# %%
date_hour_stamp = time.strftime('%Y-%m-%d_%H_%M')
file_name = 'All_Plants_Before_After_Budgeted_CPUs_' + date_hour_stamp + '.xlsx'

# %% [markdown]
# ### Write/save file to designated network share drive location:

# %%
cpu_before_after_merge.to_excel(save_dir / file_name, index=False)

# %% [markdown]
# ### Now, we need to "glue" the location of the saved file location to this notebook so that another notebook can retrieve/reference from it:

# %%
str(save_dir / file_name)

# %%
sb.glue("path_to_red_green_sheet_excel_file", str(save_dir / file_name))

# %% [markdown]
# ### Send Windows Toast notification when script completes

# %%
toaster = ToastNotifier()
toaster.show_toast("### Before vs After CPU Status ###",
                   "Successfuly compared before CPUs with after CPU adjustments",
                   icon_path="images/honda_logo.ico",
                   duration=5)
