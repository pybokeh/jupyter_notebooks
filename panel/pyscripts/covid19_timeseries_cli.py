from datetime import date
from datetime import datetime
from typing import TypeVar
import fire
import hvplot.pandas
import pandas as pd
import panel as pn
import platform
import sys
DataFrame = TypeVar('pd.core.frame.DataFrame')
DateTimeIndex = TypeVar('pd.core.indexes.datetimes.DatetimeIndex')
Panel = TypeVar('pn.layout.Row')


def covid19TimeSeries(iso_date: str, country: str='US', top: int=5) -> Panel:
    """Function that returns a Panel dashboard displaying confirmed COVID-19 cases
    SOURCE of data:
    https://www.soothsawyer.com/wp-content/uploads/2020/03/time_series_19-covid-Confirmed.csv

    Parameters
    ----------
    iso_date : str
        The date for which the desired data you are requesting in YYYY-MM-DD
    country : str
        Country for which you would like to obtain data for (default='US')
    top : int
        The Top N U.S. states for which you are requesting to plot (default=5)

    Returns
    -------
    Panel object

    Example Usage (command line):
        python covid19_timeseries.py '2020-03-28' --country 'canada'
    """
    
    if 'Linux' in platform.system():
        data_date: str = date.fromisoformat(iso_date).strftime('%-m/%-d/%Y')
    elif 'MacOS' in platform.system():
        data_date: str = date.fromisoformat(iso_date).strftime('%-m/%-d/%Y')
    elif 'Windows' in platform.system():
        data_date: str = date.fromisoformat(iso_date).strftime('%#m/%#d/%Y')
            
    if country == 'us':
        country = 'US'
    elif country == 'US':
        country = 'US'
    elif country == 'United States':
        country = 'US'
    elif country == 'united states':
        country = 'US'
    else:
        country = country.title()
            
    url = 'https://www.soothsawyer.com/wp-content/uploads/2020/03/time_series_19-covid-Confirmed.csv'
    
    df: DataFrame = pd.read_csv(url)

    if 'US' in country:
        df: DataFrame = df.fillna({'Province/State': ''})
        df: DataFrame = df[(df['Country/Region'] == country) & (~df['Province/State'].str.contains(','))]
        df: DataFrame = df.sort_values(by=data_date, ascending=False).drop(columns=['Country/Region', 'Lat', 'Long'])
    elif country in['Australia', 'Canada', 'China', 'Denmark', 'France', 'Netherlands', 'United Kingdom']:
        df: DataFrame = df.fillna({'Province/State': ''})
        df: DataFrame = df[df['Country/Region'] == country]
        df: DataFrame = df.sort_values(by=data_date, ascending=False).drop(columns=['Country/Region', 'Lat', 'Long'])
    else:
        df: DataFrame = df[df['Country/Region'] == country]
        df: DataFrame = df.sort_values(by=data_date, ascending=False).drop(columns=['Province/State', 'Lat', 'Long'])
    
    df_final: DataFrame = df.transpose()
    df_final: DataFrame = df_final.rename(columns=df_final.iloc[0]).drop(df_final.index[0])
    
    df_final.index: DateTimeIndex = [datetime.strptime(date, '%m/%d/%Y') for date in df_final.index]
    
    if country in['Australia', 'Canada', 'Denmark', 'France', 'Netherlands', 'United Kingdom', 'US']:
        panel_app: Panel = pn.Row(df_final['2020-03-10':].iloc[:, range(top)].hvplot(
                               title=f'{country}: Top {top} Provinces/States with COVID-19',
                               width=800,
                               height=600,
                               ylabel='# of Confirmed Cases',
                               xlabel='Date',
                               legend='bottom',
                               yformatter='%d'
                               ),
                               df_final['2020-03-10':].iloc[:, range(top)].hvplot.table(
                                                                                      sortable=True,
                                                                                      selectable=True,
                                                                                      width=600
                                                                                  )
                           )
    elif 'China' in country:
        panel_app: Panel = pn.Row(df_final.iloc[:, range(top)].hvplot(
                               title=f'{country}: Top {top} Provinces/States with COVID-19',
                               width=800,
                               height=600,
                               ylabel='# of Confirmed Cases',
                               xlabel='Date',
                               legend='bottom',
                               yformatter='%d'
                               ),
                               df_final.iloc[:, range(top)].hvplot.table(
                                                                                      sortable=True,
                                                                                      selectable=True,
                                                                                      width=600
                                                                                  )
                           )
    else:
        df_final = df_final[country].astype(int)
        print(df_final.dtypes)
        panel_app: Panel = pn.Row(df_final.hvplot(
                               title=f'{country}: Confirmed Cases with COVID-19',
                               width=800,
                               height=600,
                               ylabel='# of Confirmed Cases',
                               xlabel='Date',
                               legend='bottom',
                               yformatter='%d'
                               ),
                               df_final.hvplot.table(
                                                   sortable=True,
                                                   selectable=True,
                                                   width=600
                                               )
                           )
    
    return panel_app

if __name__ == '__main__':
    fire.Fire(covid19TimeSeries).show(host='localhost', port=9999)
