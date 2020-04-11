from datetime import date
from datetime import datetime
from datetime import timedelta
from typing import TypeVar, List
from urllib.request import urlopen
import json
import numpy as np
import pandas as pd
import panel as pn
import platform
import plotly.express as px
DataFrame = TypeVar('pd.core.frame.DataFrame')
Date = TypeVar('datetime.date')
DatePicker = TypeVar('panel.widgets.input.DatePicker')
Panel = TypeVar('pn.layout.Row')
MultiChoice = TypeVar('panel.widgets.select.MultiChoice')
RangeIndex = TypeVar('pandas.core.indexes.range.RangeIndex')
Series = TypeVar('pandas.core.series.Series')
 

url: str = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv'
df: DataFrame = pd.read_csv(url, converters={'FIPS': lambda x: int(float(x)) if x != '' else x}).query("FIPS != ''")
df['FIPS']: Series = df['FIPS'].astype('str').str.zfill(5)

df_choropleth: DataFrame = df.iloc[:, np.r_[4, 5, 6, df.shape[1]-1]]
df_choropleth: DataFrame = df_choropleth.rename(columns={df_choropleth.columns[3]: 'Confirmed_Cases', 'Admin2': 'County'})

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    geo_data = json.load(response)

fig = px.choropleth_mapbox(df_choropleth.query("Province_State == 'Ohio'"), geojson=geo_data, locations='FIPS', color='Confirmed_Cases',
                       color_discrete_map="Viridis",
                       mapbox_style="carto-positron",
                       zoom=3, center = {"lat": 37.0902, "lon": -95.7129},
                       opacity=0.5,
                       hover_name='County',
                       width=600,
                       height=400
                      )

fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

app = pn.Row(fig)

app.show(host='localhost', port=8889, websocket_origin='localhost:8889', open=False)