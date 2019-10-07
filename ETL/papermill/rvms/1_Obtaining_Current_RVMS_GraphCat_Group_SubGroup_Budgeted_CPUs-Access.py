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
# # Process for Obtaining Current RVMS GraphCat Group-SubGroup Budgeted CPUs

# %%
import great_expectations as ge
import pyodbc
import time
from pathlib import Path
from win10toast import ToastNotifier
import os
import pyodbc  # used for connecting to ODBC data sources
import pandas as pd  # data analysis library
pd.options.display.max_rows=1000
pd.options.display.max_columns=100

# %% [markdown]
# ### RVMS Database Credentials

# %%
userid_rvms = os.environ['windowsuser']
pw_rvms     = os.environ['windowspwd']
dsn_rvms = 'HDC-SQLP-RVMS'

# %% [markdown]
# ### Enter CLA claim month ("YYYYMM"):

# %%
# If using papermill, have to comment this out.  It doesn't support getting input from the user
# CLA_MONTH = input("Enter CLA Claim Month ('YYYYMM'): ")

# %% {"tags": ["parameters"]}
CLA_MONTH = '201903'

# %% [markdown]
# ### Define where the current budgeted CPUs will be saved:

# %%
base_dir = "//207.130.185.67/aqgbudget2/Cost/Reserve Adjustments/Reports/Normal Reserve Balance Verification/RVMS_Current_Budgeted_CPUs"
p = Path(base_dir)
save_dir = p / CLA_MONTH
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# %% [markdown]
# ### Run modified "Larry's Query"

# %% [markdown]
# This query obtains the current budgeted CPUs and "Planned" Sales that are in RVMS at the group-subgroup level.

# %% [markdown]
# **VERY IMPORTANT:** The CPU at the GraphCat level is calculated from summing the CPUs at the subgroup level using all decimal places.  The CPU at the GraphCat level is then rounded to 2 decimal places.

# %%
# %%time

cnxn_string = 'DSN=' + dsn_rvms + ';UID=' + userid_rvms + ';PWD=' + pw_rvms

cnxn = pyodbc.connect(cnxn_string)
cursor = cnxn.cursor()

# Copy/Paste your SQL text here
sql = """
/** Query to obtain current budgeted CPUs at the SubGroup level and also at the GraphCat level
    NOTE: The CPU at the GraphCat level was derived from summing the CPUs at the SubGroup level using all decimal places.
          Then the CPU at the GraphCat level was rounded to 2 decimal places
**/
WITH CPU_SUBGRP_LEVEL AS (

SELECT
    A.GraphCatID,
    RTRIM(D.GraphCatDesc) AS GraphCatDesc,
    B.GRP_NM,
    C.SUBGRP_NM,
    SUM(COALESCE(E.Budgeted_CPU,0.000)) AS Budgeted_CPU_SubGroup_Level

FROM dbo.tbl_GC_GRPS AS A
    INNER JOIN dbo.tbl_MQ_GRPKEYS AS F ON A.GRPKEY_ID = F.GRPKEY_ID
    INNER JOIN dbo.tbl_MQ_GRPS AS B ON F.GRP_ID = B.GRP_ID
    INNER JOIN tbl_MQ_SUBGRPS AS C ON F.SUBGRP_ID = C.SUBGRP_ID
    INNER JOIN tbl_GraphCatMaster AS D ON A.GraphCatID = D.GraphCatID
    LEFT JOIN tbl_GraphCat_MIS AS E ON A.GC_GRP_ID = E.GC_GRP_ID

WHERE
    D.GraphCatType = 'R'
    and D.GraphCatDesc like 'R %'

GROUP BY
    A.GraphCatID,
    D.GraphCatDesc,
    B.GRP_NM,
    C.SUBGRP_NM
),

GC_SALES as (

SELECT
    GraphCatID,
    sum(PlannedSales) as Planned_Sales_RVMS

FROM
    tbl_GraphCatMonthlySales

GROUP BY
    GraphCatID
),

CPU_GC_LEVEL as (
SELECT
    GraphCatID,
    SUM(Budgeted_CPU_SubGroup_Level) AS Budgeted_CPU_GC_Level,
    SUM(Orig_Saturation_CPU) as Orig_Saturation_CPU_GC_Level

FROM (

SELECT
    A.GraphCatID,
    RTRIM(D.GraphCatDesc) AS GraphCatDesc,
    B.GRP_NM,
    C.SUBGRP_NM,
    SUM(COALESCE(E.Budgeted_CPU,0.000)) AS Budgeted_CPU_SubGroup_Level,
    SUM(COALESCE(E.OriginalReserve_CPU,0.000)) as Orig_Saturation_CPU

FROM dbo.tbl_GC_GRPS AS A
    INNER JOIN dbo.tbl_MQ_GRPKEYS AS F ON A.GRPKEY_ID = F.GRPKEY_ID
    INNER JOIN dbo.tbl_MQ_GRPS AS B ON F.GRP_ID = B.GRP_ID
    INNER JOIN tbl_MQ_SUBGRPS AS C ON F.SUBGRP_ID = C.SUBGRP_ID
    INNER JOIN tbl_GraphCatMaster AS D ON A.GraphCatID = D.GraphCatID
    LEFT JOIN tbl_GraphCat_MIS AS E ON A.GC_GRP_ID = E.GC_GRP_ID

WHERE
    D.GraphCatType = 'R'
    and D.GraphCatDesc like 'R %'

GROUP BY
    A.GraphCatID,
    D.GraphCatDesc,
    B.GRP_NM,
    C.SUBGRP_NM

) AS CPU_GC_LEVEL

GROUP BY
    GraphCatID

),


GC_BudgetMatrix AS (

    SELECT
        GC_Budget.SaleMonth,
        GC_Master.GraphCatID,
        GC_Master.GraphCatDesc as GraphCat,
        CummActual_CPU as CumActual_CPU,
        CummBudgeted_Cpu as CumBudgeted_CPU

    FROM dbo.tbl_GraphCat_BudgetedMatrix as GC_Budget

        LEFT JOIN dbo.tbl_GC_GRPS AS GC_GRPS ON
        GC_Budget.GC_GRP_ID = GC_GRPS.GC_GRP_ID

        LEFT JOIN dbo.tbl_MQ_GRPKEYS AS MQ_GRPKEYS ON
        GC_GRPS.GRPKEY_ID = MQ_GRPKEYS.GRPKEY_ID

        LEFT JOIN dbo.tbl_MQ_GRPS AS MQ_GRPS ON
        MQ_GRPKEYS.GRP_ID = MQ_GRPS.GRP_ID

        LEFT JOIN dbo.tbl_MQ_SUBGRPS AS MQ_SUBGRPS ON
        MQ_GRPKEYS.SUBGRP_ID = MQ_SUBGRPS.SUBGRP_ID

        LEFT JOIN dbo.tbl_GraphCatMaster as GC_Master ON
        GC_GRPS.GraphCatID = GC_Master.GraphCatID


    WHERE
        GC_Master.GraphCatType = 'R'
        and GC_Master.GraphCatDesc like 'R %'

),


Actual_CPU_GC_Level as (

SELECT
    GraphCatID,
    GraphCat,
    max(CumActual_CPU) as CumActual_CPU

FROM (


SELECT
    SaleMonth,
    GraphCatID,
    GraphCat,
    sum(CumActual_CPU) as CumActual_CPU

FROM (

    SELECT
        SaleMonth,
        GraphCatID,
        GraphCat,
        CASE
            WHEN CumActual_CPU = 0 THEN NULL
        ELSE
            CumActual_CPU
        END AS CumActual_CPU,
        CumBudgeted_CPU

    FROM
        GC_BudgetMatrix

) AS TEMP1

GROUP BY
    SaleMonth,
    GraphCatID,
    GraphCat

) AS TEMP2

GROUP BY
    GraphCatID,
    GraphCat
)

SELECT
    CPU_SUBGRP_LEVEL.*,
    GC_SALES.Planned_Sales_RVMS,
    ROUND(CPU_GC_LEVEL.Budgeted_CPU_GC_Level, 2) AS Budgeted_CPU_GC_Level,
    ROUND(CPU_GC_LEVEL.Orig_Saturation_CPU_GC_Level, 2) AS Orig_Saturation_CPU_GC_Level,
    ROUND(Actual_CPU_GC_Level.CumActual_CPU, 2) as Cum_Actual_CPU_GC_Level

FROM
    CPU_SUBGRP_LEVEL AS CPU_SUBGRP_LEVEL

    LEFT JOIN GC_SALES as GC_SALES ON
    CPU_SUBGRP_LEVEL.GraphCatID = GC_SALES.GraphCatID

    LEFT JOIN CPU_GC_LEVEL as CPU_GC_LEVEL ON
    CPU_SUBGRP_LEVEL.GraphCatID = CPU_GC_LEVEL.GraphCatID

    LEFT JOIN Actual_CPU_GC_Level as Actual_CPU_GC_Level ON
    CPU_SUBGRP_LEVEL.GraphCatID = Actual_CPU_GC_Level.GraphCatID

ORDER BY
    GraphCatID
    """

RVMS_Current_Budgeted_CPU = pd.read_sql(sql, cnxn, index_col=None)

# For large data (data > RAM, use chunking):
"""
for c in pd.read_sql(sql, cnxn, chunksize=10000):
    c.to_csv(r'D:\temp\resultset.csv', index=False, mode='a')"""

# Close connections
cursor.close()
cnxn.close()

# %%
RVMS_Current_Budgeted_CPU.shape

# %%
RVMS_Current_Budgeted_CPU.head()

# %% [markdown]
# ### Create ```RVMS_Claim_Month``` column to contain the CLA claim month:

# %%
RVMS_Current_Budgeted_CPU['RVMS_Claim_Month'] = CLA_MONTH

# %%
RVMS_Current_Budgeted_CPU.head()

# %% [markdown]
# ### Create data set of CPUs at GraphCat level:

# %%
cpu_at_gc_level = RVMS_Current_Budgeted_CPU[['GraphCatID', 'Budgeted_CPU_GC_Level']].drop_duplicates()

# %%
cpu_at_gc_level.head()

# %% [markdown]
# ### Create data set of original saturation CPUs at GraphCat level:

# %%
orig_sat_cpu_at_gc_level = RVMS_Current_Budgeted_CPU[['GraphCatID', 'Orig_Saturation_CPU_GC_Level']].drop_duplicates()

# %%
orig_sat_cpu_at_gc_level.head()

# %% [markdown]
# ### Create data set of cumulative actual CPUs at GraphCat level:

# %%
actual_cpu_at_gc_level = RVMS_Current_Budgeted_CPU[['GraphCatID', 'Cum_Actual_CPU_GC_Level']].drop_duplicates()

# %%
actual_cpu_at_gc_level.head()

# %% [markdown]
# ### Ensure that the sum of the CPUs at the subgroup level differ from the sum of the CPUs at the GraphCat level is less than 1 currency unit

# %%
assert abs(RVMS_Current_Budgeted_CPU['Budgeted_CPU_SubGroup_Level'].sum() - cpu_at_gc_level['Budgeted_CPU_GC_Level'].sum()) < 1.0

# %%
RVMS_Current_Budgeted_CPU['Budgeted_CPU_SubGroup_Level'].sum()

# %%
cpu_at_gc_level['Budgeted_CPU_GC_Level'].sum()


# %% [markdown]
# ### Create helper functions to Add Model Year, Factory, Model Name, and custom destination code to the RVMS Original Budgeted CPU data set:

# %%
def getModelYear(row) -> str:
    word_token = row['GraphCatDesc'].strip().split()
    
    model_year = word_token[3]
    
    if model_year.isdigit():
        return model_year
    else:
        return word_token[4]
        

def getFactoryCode(row) -> str:
    word_token = row['GraphCatDesc'].strip().split()
    factory_code = word_token[1]
    
    return factory_code.upper()

def getModelName(row) -> str:
    word_token = row['GraphCatDesc'].strip().split()
    model_name = word_token[2]
    
    return model_name.upper()
    
def getDestCode(row) -> str:
    word_token = row['GraphCatDesc'].strip().split()
    destination_code = word_token[-1]
    
    return destination_code.upper()


# %%
RVMS_Current_Budgeted_CPU['ModelYear'] = RVMS_Current_Budgeted_CPU.apply(getModelYear, axis='columns')
RVMS_Current_Budgeted_CPU['Factory'] = RVMS_Current_Budgeted_CPU.apply(getFactoryCode, axis='columns')
RVMS_Current_Budgeted_CPU['ModelName'] = RVMS_Current_Budgeted_CPU.apply(getModelName, axis='columns')
RVMS_Current_Budgeted_CPU['DestCode'] = RVMS_Current_Budgeted_CPU.apply(getDestCode, axis='columns')

# %%
RVMS_Current_Budgeted_CPU.head()

# %% [markdown]
# ### Perform data validation checks using Great Expectations library

# %% [markdown]
# #### Create Great Expectations dataframe from pandas dataframe:

# %%
ge_df = ge.from_pandas(RVMS_Current_Budgeted_CPU)

# %% [markdown]
# #### Check Model Years are between 1994 and 2099

# %%
if ge_df.expect_column_values_to_be_between(column="ModelYear", min_value='1994', max_value='2099')['success']:
    print('Passed Model Year Check')
else:
    print('FAILED Model Year Check')
    toaster = ToastNotifier()
    toaster.show_toast("### Check Status ###",
                   "FAILED Model Year Check",
                   icon_path="images/honda_logo.ico",
                   duration=10)
    raise Exception("ERROR: Failed Model Year Check")

# %% [markdown]
# #### Check Factory values are limited to one of:

# %% [markdown]
# 'ELP','HCL','HCM','HDM','HMA','HMI','MAP','PMC'

# %%
if ge_df.expect_column_values_to_be_in_set(column="Factory", value_set=['ELP','HCL','HCM','HDM','HMA','HMI','MAP','PMC'])['success']:
    print('Passed Factory Check')
else:
    print('FAILED Factory Check')
    toaster = ToastNotifier()
    toaster.show_toast("### Check Status ###",
                   "FAILED Factory Check",
                   icon_path="images/honda_logo.ico",
                   duration=10)
    raise Exception("ERROR: Failed Factory Check")

# %% [markdown]
# #### Check Model Names are limited to one of:

# %% [markdown]
# 'ACCORD','CIVIC','CROSSTOUR','CRV','CSX','EL','ELEMENT','FIT','HRV','ILX','INSIGHT','MDX','NSX','ODYSSEY','PASSPORT','PILOT','RDX','RIDGELINE','TL','TLX','ZDX'

# %%
if ge_df.expect_column_values_to_be_in_set(column="ModelName", value_set=['ACCORD','CIVIC','CROSSTOUR','CRV','CSX','EL',
                                                                          'ELEMENT','FIT','HRV','ILX','INSIGHT','MDX','NSX',
                                                                          'ODYSSEY','PASSPORT','PILOT','RDX','RIDGELINE','TL','TLX','ZDX'
                                                                         ])['success']:
    print('Passed Model Name Check')
else:
    print('FAILED Model Name Check')
    toaster = ToastNotifier()
    toaster.show_toast("### Check Status ###",
                   "FAILED Factory Check",
                   icon_path="images/honda_logo.ico",
                   duration=10)
    raise Exception("ERROR: Failed Model Name Check")

# %% [markdown]
# I think Great_Expectations library has a [bug](https://github.com/great-expectations/great_expectations/issues/412).  If my column contains missing model names or None objects, the above test still passes!  So I have to test for Null or missing values with this test below:

# %%
if ge_df.expect_column_values_to_not_be_null(column="ModelName")['success']:
    print('No model names are null')
else:
    print('Null model names found')
    toaster = ToastNotifier()
    toaster.show_toast("### Check Status ###",
                   "FAILED Factory Check",
                   icon_path="images/honda_logo.ico",
                   duration=10)
    raise Exception("ERROR: Failed Model Name Check")

# %%
RVMS_Current_Budgeted_CPU.to_excel(save_dir / 'All_Plants_Budgeted_CPU_By_Group_SubGroup.xlsx', index=False)

# %% [markdown]
# ### Send notification that MS Access process will begin

# %%
toaster = ToastNotifier()
toaster.show_toast("### MS Access Proccess ###",
                   "Storing current budgeted CPUs - Please wait...",
                   icon_path="images/honda_logo.ico",
                   duration=5)

# %% [markdown]
# ### Also save the current budgeted CPUs into an MS Access database, but first we must empty the table containing data from a previous run:

# %%
conn_str = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            r'DBQ=\\207.130.185.67\aqgbudget2\Cost\Reserve Adjustments\Reports\databases\RVMS.accdb;'
           )

cnxn = pyodbc.connect(conn_str)
cursor = cnxn.cursor()

sql = """
DELETE

FROM tbl_Current_Budgeted_CPU
"""

try:
    cursor.execute(sql)
    cnxn.commit()
    
    # Close connections
    cursor.close()
    cnxn.close()
except:
    print("Error connecting to database")
    cursor.close()
    cnxn.close()

# %% [markdown]
# ### Now insert the current CPUs into the MS Access database

# %%
# %%time
conn_str = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            r'DBQ=\\207.130.185.67\aqgbudget2\Cost\Reserve Adjustments\Reports\databases\RVMS.accdb;'
           )
cnxn = pyodbc.connect(conn_str, autocommit=True)

try:
    for index, row in RVMS_Current_Budgeted_CPU.iterrows():
        with cnxn.cursor() as cursor:
            #cursor.setinputsizes([(pyodbc.SQL_INTEGER,)])
            cursor.execute("INSERT INTO tbl_Current_Budgeted_CPU(GraphCatID, \
                                                                 GraphCatDesc, \
                                                                 GRP_NM, \
                                                                 SUBGRP_NM, \
                                                                 Budgeted_CPU_SubGroup_Level, \
                                                                 Planned_Sales_RVMS, \
                                                                 Budgeted_CPU_GC_Level, \
                                                                 Orig_Saturation_CPU_GC_Level, \
                                                                 Cum_Actual_CPU_GC_Level, \
                                                                 RVMS_Claim_Month, \
                                                                 ModelYear, \
                                                                 Factory, \
                                                                 ModelName, \
                                                                 DestCode \
                                                                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                           row[0],
                           row[1],
                           row[2],
                           row[3],
                           row[4],
                           row[5],
                           row[6],
                           row[7],
                           row[8],
                           row[9],
                           row[10],
                           row[11],
                           row[12],
                           row[13]
                          )
            cursor.commit()
        
    cnxn.close()

except Exception as e:
    print("Error connecting to the database: ", str(e))
    cnxn.close()

# %% [markdown]
# ### Confirm that the number of rows inserted into ```tbl_Current_Budgeted_CPU``` matches the``` RVMS_Current_Budgeted_CPU``` dataframe.  There could be in theory, a network drop or latency issue where not all the rows were inserted.  This has happened before!

# %%
conn_str = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            r'DBQ=\\207.130.185.67\aqgbudget2\Cost\Reserve Adjustments\Reports\databases\RVMS.accdb;'
           )
cnxn = pyodbc.connect(conn_str)
cursor = cnxn.cursor()

sql = """
SELECT
    count(*) as Qty
    
FROM tbl_Current_Budgeted_CPU
"""

try:
    cpu_current = pd.read_sql(sql, cnxn)
    #cpu_before = pd.read_sql(sql, cnxn)
    
    # Close connections
    cursor.close()
    cnxn.close()
except Exception as e:
    print("Error connecting to the database: ", str(e))
    cursor.close()
    cnxn.close()

# %%
cpu_current.values[0][0]

# %%
assert cpu_current.values[0][0] == RVMS_Current_Budgeted_CPU.shape[0]

# %% [markdown]
# #### If the script made it this far, then it must have completed without errors.  Send out a Windows toast notification that the script has successfully completed:

# %%
toaster = ToastNotifier()
toaster.show_toast("### Export COMPLETED ###",
                   "Successfuly Obtained and Validated Current RVMS Group-SubGroup Budgeted CPUs",
                   icon_path="images/honda_logo.ico",
                   duration=5)
