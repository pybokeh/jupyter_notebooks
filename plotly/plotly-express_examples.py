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

# %%
import pandas as pd
import plotly.express as px

# %%
df = pd.read_csv('data/defect_rate.csv')


# %% [markdown]
# ### Data is in "wide format":

# %%
df.head()

# %% [markdown]
# ### But to use plotly-express, data needs to be in long format:

# %%
df_long = df.melt(id_vars=['Month'], value_vars=['Comp_A', 'Comp_B'])


# %%
df_long.columns = ['Month', 'Component', 'Defect_Rate']
# %%
df_long

# %% [markdown]
# ### List of plotly-express templates:

# %%
import plotly.io as pio
list(pio.templates)

# %%
px.line(df_long, x='Month', line_group='Component', y='Defect_Rate', color='Component', title='Cum. Defect Rate', 
        template='presentation')

