**Suppplier: ABC Corp # 12345**&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**Document Control # 1234567890**
<center><h1>Model XXX - Washer Tank Leaks</h1></center>
<center><h3>Created by Daniel J. Kim</h3></center>
<center><h3>9/26/16</h3></center>

### Affected Vehicles / Trim Levels / Failed Part Numbers:
- 2015 Model XXX, fail part # 12345 (windshield washer tank assy)<br><br>  

### Market Problem Description / Dealer Repair Method:
Customer states that the washer tank is leaking or that they are consistently refilling their washer fluid.  Dealers are replacing the washer tank (**reference # 13 below**).<br><br>  

<center><h4>Image from American Honda's Parts Catalog:</h4></center>
```{python, echo=False}
from IPython.display import Image
Image(filename='parts_catalog.png')
```
#  <br>    

### Root Cause per QIS:  
Washer tank cracking is a result of a combination of internal seam thickness with a higher material crystallinity factor.   Note:  Model years 09M-14M  did not experience this warranty trend.<br><br>  
  
<center><strong>Before C/M:</strong></center>
```{python, echo=False}
from IPython.display import Image 
Image(filename='BeforeCMImage.png')
```
### Countermeasure Activity:
- Manufacturig molding change (7/7/16): A small insert was added to the washer tank mold to reduce the depth of the parison pocket which allows more material to fill in to increase seam thickness.  Increasing this thickness will accommodate stress in the area that is cracking.
    - **Before:** 3.84 mm average thickness on the radius and 3.5-4.17mm  overall thickness in the lower area of the tank.
    - **After:** 5.36 mm average thickness on the radius and 4.7- 6.02 mm overall thickness in the lower area of the tank.  
  

```{python, echo=False}
from IPython.display import Image 
Image(filename='AfterCMImage.png')
```

### Warranty Summary:
- **Criteria**:  
    - Model years 2012-2016, Model XXX, part # 12345 replaced, U.S. market

```{python, echo=False}
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("white")

df = pd.read_excel(r'D:\temp\stitch\Model_XXX.xlsx', sheetname='mfss')

# Remove percent symbols and multiply by 100 to convert to percentage
data = df.applymap(lambda x:float(str(x).replace('%',''))).applymap(lambda x: x * 100)
fig, ax = plt.subplots(figsize=(8,5))
data.plot(ax=ax)
plt.title('2012 - 2016 Model XXX Washer Tank Replaced Warranty', weight='bold')
plt.xlabel('Months From Start of Sales (MFSS)')
plt.ylabel('Cumulative Defect Rate (%)')
plt.grid(True)
sns.despine(left=True, bottom=True)
plt.show()
```

**Countermeasure has been over 90% effective.**

```{python, echo=False}
df = pd.read_excel(r'D:\temp\stitch\Model_XXX.xlsx', sheetname='AF_Mth', index_col=0)

# Remove percent symbols and commas.  Then multiple by 100 to convert to percentage.
data = df.applymap(lambda x:float(str(x).replace('%',''))).applymap(lambda x: x * 100)

fig, ax = plt.subplots(figsize=(12,5))
data.plot.bar(ax=ax)
plt.title('Defect Rate versus Vehicle Build Month', weight='bold')
plt.xlabel('Vehicle Build Month')
plt.xticks(fontsize=7)
plt.ylabel('Defect Rate % (claims / sales)')
plt.grid(True)
sns.despine(left=True, bottom=True)
plt.show()
```

```{python, echo=False}
df = pd.read_excel(r'D:\temp\stitch\Model_XXX.xlsx', sheetname='Claims', parse_cols=[0,24,25,29]).query("MODEL_YEAR==2015")

fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10,4))

plt.suptitle('Histograms')
axes[0].set_title('DTF')
axes[1].set_title('MTF')
df.DAYS_TO_FAIL_MINZERO.plot.hist(ax=axes[0],bins=15)
df.MILES_TO_FAIL.plot.hist(ax=axes[1])
sns.despine()
plt.show()
```

# <br>  

**No apparent trend by state/region found:**

```{ir, echo=False}
options(warn=-1)
options(repr.plot.width=7, repr.plot.height=5)
par(mar=c(1,1,1,1))
suppressMessages(library(choroplethr))
suppressMessages(library(dplyr))
suppressMessages(library(readxl))

state_code = c("AL",
               "AK",
               "AR",
               "AZ",
               "CA",
               "CO",
               "CT",
               "DE",
               "FL",
               "GA",
               "HI",
               "IA",
               "ID",
               "IL",
               "IN",
               "KS",
               "KY",
               "LA",
               "ME",
               "MA",
               "MD",
               "MI",
               "MN",
               "MO",
               "MS",
               "MT",
               "NC",
               "ND",
               "NE",
               "NH",
               "NJ",
               "NM",
               "NV",
               "NY",
               "OH",
               "OK",
               "OR",
               "PA",
               "RI",
               "SC",
               "SD",
               "TN",
               "TX",
               "UT",
               "VA",
               "VT",
               "WA",
               "WI",
               "WV",
               "WY")

state_name = c("alabama",
               "alaska",
               "arkansas",
               "arizona",
               "california",
               "colorado",
               "connecticut",
               "delaware",
               "florida",
               "georgia",
               "hawaii",
               "iowa",
               "idaho",
               "illinois",
               "indiana",
               "kansas",
               "kentucky",
               "louisiana",
               "maine",
               "massachusetts",
               "maryland",
               "michigan",
               "minnesota",
               "missouri",
               "mississippi",
               "montana",
               "north carolina",
               "north dakota",
               "nebraska",
               "new hampshire",
               "new jersey",
               "new mexico",
               "nevada",
               "new york",
               "ohio",
               "oklahoma",
               "oregon",
               "pennsylvania",
               "rhode island",
               "south carolina",
               "south dakota",
               "tennessee",
               "texas",
               "utah",
               "virginia",
               "vermont",
               "washington",
               "wisconsin",
               "west virginia",
               "wyoming")

df <- data.frame(state_code, state_name)
col_headings <- c("state", "region")
names(df) <- col_headings

# Copy state data with values
# data <- read.table("clipboard", sep="\t", header=TRUE)

# Or get from Excel file
data <- read_excel("D:/temp/stitch/Model_XXX.xlsx", sheet = "Sheet7", col_names = TRUE )

                   
# Join
final <- inner_join(df, data, by = c('state' = 'state_code'))

col_headings <- c("state_code", "region", "value")
names(final) <- col_headings

# Finally, generate state choropleth map
state_choropleth(final, title="Defect Rate by State", legend="Defect Rate(%)")
```



### Supplier Percent Responsibility
Supplier's percent responsibility was based on 2015 Model XXX warranty compared to prior model years Model XXX warranty after same months since start of sales.  2015 Model XXX is 92.55% worse than prior model years.  This is supplier design issue.  Therefore, share rate reduced from 100% to 80%.  Final supplier percent responsibility is 92.55% x 80% = **74.04%**.

# <br>  

### Honda Motor Company versus Supplier Warranty Share Amount:
- Honda Motor Company: $92,087.50
- ABC Corp, Inc: **$60,138.73**:
    - (part cost + labor cost + handling cost) = ($18.12 + $77 + $21.75) = $116.87 (cost per claim)
    - Total claims to date: 695
    - Total reimbursement amount = 695 x $116.87 x 74.04% = **$60,138.73**

```{python, echo=False}
df = pd.read_excel(r'D:\temp\stitch\Model_XXX.xlsx', sheetname='initial_amount')
data = df.applymap(lambda x:float(str(x).replace('$','').replace(',','')))
fig, ax = plt.subplots(figsize=(7,5))
data.plot.bar(ax=ax)
plt.title('Honda Motor Co versus Supplier Reimbursement Amount', weight='bold')
plt.ylabel('Cost US$')
sns.despine(left=True, bottom=True)
plt.grid(True)

```


