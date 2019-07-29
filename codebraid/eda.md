---
title: "Simple EDA with Pandas"
---

### Library imports

```{.python .cb.nb jupyter_kernel=python3 number_lines=True}
%matplotlib inline
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
```

### Load sample mpg data set

```{.python .cb.nb}
mpg = sns.load_dataset('mpg')
```

### Peek at sample data

```{.python .cb.nb}
mpg.head()
```

### Plot mean mpg by Model Year

```{.python .cb.nb first_number=integer number_lines=true}
mpg.groupby(['model_year']).agg({'mpg': 'mean'}).plot()
plt.title('Mean MPG by Year')
plt.xlabel('Year')
plt.ylabel('Mean MPG')
sns.despine()
```

### Summary Statistics

```{.python .cb.nb first_number=integer number_lines=true}
mpg.describe()
```
