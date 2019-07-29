### Library imports

```{.python .cb.nb jupyter_kernel=python3}
import pandas as pd
import plotly.express as px
```

### Read in sample data

```{.python .cb.nb}
df = pd.read_csv('/home/pybokeh/Dropbox/python/jupyter_notebooks/plotly/data/defect_rate.csv')
```

### Data is in "wide format"

```{.python .cb.nb}
df.head()
```

### But to use plotly-express, data needs to be in long format

```{.python .cb.nb}
df_long = df.melt(id_vars=['Month'], value_vars=['Comp_A', 'Comp_B'])
df_long.columns = ['Month', 'Component', 'Defect_Rate']
df_long
```

### List of plotly available plotly templates

```{.python .cb.nb}
import plotly.io as pio
list(pio.templates)
```

### Now plot the defect rates

```{.python .cb.nb}
px.line(df_long, x='Month', line_group='Component', y='Defect_Rate', color='Component', title='Cum. Defect Rate', 
        template='presentation')
```
