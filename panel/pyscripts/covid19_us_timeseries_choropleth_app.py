from datetime import date
from datetime import datetime
from datetime import timedelta
from typing import TypeVar, List
from urllib.request import urlopen
import hvplot.pandas
import json
import numpy as np
import pandas as pd
import panel as pn
import platform
import plotly.express as px
DataFrame = TypeVar('pd.core.frame.DataFrame')
Date = TypeVar('datetime.date')
DatePicker = TypeVar('panel.widgets.input.DatePicker')
DateTimeIndex = TypeVar('pd.core.indexes.datetimes.DatetimeIndex')
Panel = TypeVar('pn.layout.Row')
MultiChoice = TypeVar('panel.widgets.select.MultiChoice')
Series = TypeVar('pandas.core.series.Series')
css = '''
.black-theme {
  background-color: black;
  color: white;
}
.grey-theme {
  background-color: #CCD1D1;
  color: black;
}
'''
pn.config.raw_css.clear()
pn.config.raw_css.append(css)

url: str = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv'
df: DataFrame = pd.read_csv(url)

# Create input widgets: date widget, multi-choice, and selection widgets
# Make default date yesterday (today minus 1 day) since COVID-19 data is usually 1 day behind
states_provinces: List[str] = df['Province_State'].unique().tolist()
covid19_date: DatePicker = pn.widgets.DatePicker(name='Date:', value=(date.today() + timedelta(days=-1)), width=200, css_classes=['grey-theme'])
state_province = pn.widgets.MultiChoice(name='State of Province', value=['Ohio'],
    options=states_provinces)
ylog = pn.widgets.Select(name='log-y?', value=False, options=[True, False], width=200, css_classes=['grey-theme'])

@pn.depends(covid19_date.param.value, state_province.param.value, ylog.param.value)
def covid19TimeSeriesByState(covid19_date: Date, state_province: List[str], ylog: bool=False) -> Panel:
    """Function that returns a Panel dashboard displaying confirmed COVID-19 cases
    It is using Panel's "Reactive functions" API: https://panel.holoviz.org/user_guide/APIs.html

    Parameters
    ----------
    covid19_date : Date
        End date of data you wish to obtain up to
    country : str
        Country for which you would like to obtain data for (default='US')
    top : int
        The Top N provinces or states for which you are requesting to plot (default=5)
    ylog : bool
        To enable log scaling or not on y-axis.  Log scale can be useful to easily discern growth rate.

    Returns
    -------
    Panel object
    """
    
    iso_date: str = covid19_date.strftime('%Y-%m-%d')
    
    if 'Linux' in platform.system():
        data_date: str = date.fromisoformat(iso_date).strftime('%-m/%-d/%Y')
    elif 'MacOS' in platform.system():
        data_date: str = date.fromisoformat(iso_date).strftime('%-m/%-d/%Y')
    elif 'Windows' in platform.system():
        data_date: str = date.fromisoformat(iso_date).strftime('%#m/%#d/%Y')
            
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        geo_data = json.load(response)

    # Source of COVID-19 data
    # To leverage Plotly's choropleth_mapbox function, need to have FIPS as fixed length(n=5) values consisting of leading zeros
    url: str = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv'
    df: DataFrame = pd.read_csv(url, converters={'FIPS': lambda x: int(float(x)) if x != '' else x}).query("FIPS != ''")
    df['FIPS']: Series = df['FIPS'].astype('str').str.zfill(5)

    df_by_state = (df.query("not Province_State in('Diamond Princess', 'Grand Princess')")
                    .drop(columns=['UID', 'iso2', 'iso3', 'code3', 'FIPS', 'Admin2', 'Country_Region', 'Lat', 'Long_', 'Combined_Key'])
                    .groupby('Province_State').agg('sum')
                    .transpose()
                  )
    
    # https://stackoverflow.com/questions/53052914/selecting-non-adjacent-columns-by-column-number-pandas
    df_by_state_ts = df.iloc[:, np.r_[6, 11:df.shape[1]]].groupby('Province_State').agg('sum').transpose()
    
    df_by_counties = df.query("not Lat==0").iloc[:, [6, 10, -1]]
    
    df_choropleth: DataFrame = df.iloc[:, np.r_[4, 5, 6, df.shape[1]-1]]
    df_choropleth: DataFrame = df_choropleth.rename(columns={df_choropleth.columns[3]: 'Confirmed_Cases', 'Admin2': 'County'})
        
    # Make index an actual datetime data type for easier date filtering.
    # So far JHU has been incosistent with their year format (YYYY vs YY)
    # Therfore, have to account for either formats
    try:
        df_by_state.index: DateTimeIndex = [datetime.strptime(date, '%m/%d/%y') for date in df_by_state.index]
    except ValueError as e:
        print("YY year format not detected.  Using YYYY format instead.", e)
        df_by_state.index: DateTimeIndex = [datetime.strptime(date, '%m/%d/%Y') for date in df_by_state.index]

    # If only one state is selected, then also provide data tables containing counts by counties, by date, and counties choropleth map
    if len(state_province) == 1:
        fig = px.choropleth_mapbox(df_choropleth.query("Province_State in@state_province"), geojson=geo_data, locations='FIPS', color='Confirmed_Cases',
                               color_discrete_map="Viridis",
                               mapbox_style="carto-positron",
                               zoom=3.5, center = {"lat": 37.0902, "lon": -95.7129},
                               opacity=0.5,
                               hover_name='County',
                               width=1300,
                               height=700
                              )
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        
        panel_app: Panel = pn.Column(pn.Row(
                                           df_by_state['2020-03-10':data_date]
                                           .loc[:, state_province]
                                           .hvplot(
                                                   title='Confirmed COVID-19 Cases',
                                                   logy=ylog,
                                                   width=600,
                                                   height=500,
                                                   ylabel='# of Confirmed Cases',
                                                   xlabel='Date',
                                                   legend='bottom',
                                                   yformatter='%d'
                                           ),
                                           df_by_counties.query("Province_State == @state_province")
                                                         .sort_values(by=df_by_counties.columns[2], ascending=False)
                                                         .drop(columns='Province_State', axis='columns')
                                                         .rename(columns={'Combined_Key': 'County', df_by_counties.columns[2]: 'Qty as of ' + df_by_counties.columns[2]})
                                                         .hvplot.table(sortable=True,
                                                                       selectable=True,
                                                                       width=300,
                                                                       height=500
                                           ),
                                           df_by_state_ts.loc[:, state_province]
                                                         .sort_values(by=state_province, ascending=False)
                                                         .reset_index()
                                                         .rename(columns={'index': 'Date', state_province[0]: 'Cum. Qty'})
                                                         .hvplot.table(sortable=True,
                                                             selectable=True,
                                                             width=300,
                                                             height=500
                                           )
                                     ),
                                     fig
                           )
    # Else just provide line charts
    else:
        panel_app: Panel = pn.Row(df_by_state['2020-03-10':data_date].loc[:, state_province].hvplot(
                               title='Confirmed COVID-19 Cases',
                               logy=ylog,
                               width=600,
                               height=500,
                               ylabel='# of Confirmed Cases',
                               xlabel='Date',
                               legend='bottom',
                               yformatter='%d'
                              )
                           )

    return panel_app


# Final Panel object
app = pn.Column(
          covid19_date,
          state_province,
          ylog,
          covid19TimeSeriesByState
      )

app.show(host='localhost', port=8889, websocket_origin='localhost:8889', open=False)
