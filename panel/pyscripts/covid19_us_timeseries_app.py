from datetime import date
from datetime import datetime
from datetime import timedelta
from typing import TypeVar, List
import hvplot.pandas
import numpy as np
import pandas as pd
import panel as pn
import platform
DataFrame = TypeVar('pd.core.frame.DataFrame')
Date = TypeVar('datetime.date')
DatePicker = TypeVar('panel.widgets.input.DatePicker')
DateTimeIndex = TypeVar('pd.core.indexes.datetimes.DatetimeIndex')
Panel = TypeVar('pn.layout.Row')
MultiChoice = TypeVar('panel.widgets.select.MultiChoice')
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

# Create input widgets: date widget and 2 selection widgets
# There is bug in the date widget in version 0.9.3: https://github.com/holoviz/panel/issues/1173
# Manually fixed the bug by modifying input.py source file
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

    # Source of COVID-19 data        
    url: str = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv'
    df: DataFrame = pd.read_csv(url)

    df_by_state = (df.query("not Province_State in('Diamond Princess', 'Grand Princess')")
                    .drop(columns=['UID', 'iso2', 'iso3', 'code3', 'FIPS', 'Admin2', 'Country_Region', 'Lat', 'Long_', 'Combined_Key'])
                    .groupby('Province_State').agg('sum')
                    .transpose()
                  )
    
    # https://stackoverflow.com/questions/53052914/selecting-non-adjacent-columns-by-column-number-pandas
    df_by_state_ts = df.iloc[:, np.r_[6, 11:df.shape[1]]].groupby('Province_State').agg('sum').transpose()
    
    df_by_counties = df.query("not Lat==0").iloc[:, [6, 10, -1]]

    # Make index an actual datetime data type for easier date filtering.
    # So far JHU has been incosistent with their year format (YYYY vs YY)
    # Therfore, have to account for either formats
    try:
        df_by_state.index: DateTimeIndex = [datetime.strptime(date, '%m/%d/%y') for date in df_by_state.index]
    except ValueError as e:
        print("YY year format not detected.  Using YYYY format instead.", e)
        df_by_state.index: DateTimeIndex = [datetime.strptime(date, '%m/%d/%Y') for date in df_by_state.index]

    # If only one state is selected, then also provide data tables containing counts by counties and by date
    if len(state_province) == 1:
        panel_app: Panel = pn.Row(df_by_state['2020-03-10':data_date].loc[:, state_province].hvplot(
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
                           )
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

#################  Deployment Options  ###############
# Various ways to deploy Panel app(s)
# Reference: https://panel.holoviz.org/user_guide/Deploy_and_Export.html

# Another Panel object to demonstrate that we can deploy 2 Panel apps
# marquee = pn.panel('<marquee>ALL YOUR BASE ARE BELONG TO US!</marquee>')

# Deploy a single Panel app
# app.show(host='localhost', port=8889)
# or
# app.servable()

# Deploy two or more Panel apps on single bokeh server
# Launch main bokeh server entry point and then visit websocket_origin url
# pn.serve({'marquee': marquee, 'covid19': app}, port=8890, websocket_origin='10.87.159.68:8890', show=False)
