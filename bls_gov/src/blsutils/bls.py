from datetime import date
from dateutil.relativedelta import relativedelta
import json
import matplotlib.pyplot as plt
import pandas as pd
import requests
import seaborn as sns


def plot_bls_series_id(
    series_id: str, series_descr: str, bls_key: str, past_n_years: int = 19
):
    """
    A function that plots a BLS series

    Parameters
    ----------
    series_id : str
        Series ID
    series_descr : str
        Series description
    bls_key : str
        BLS secret key that you need to obtain from registering here: https://data.bls.gov/registrationEngine/
    past_n_years : int
        Number of years worth of data to be plotted.  By default, will plot last 19 years' worth of data (bls.gov's max)

    Returns
    -------
    A MATPLOTLIB line chart with vertical regions to indicate when recessions have occurred to add historical context
    """

    try:
        current_date = date.today()
        current_year = current_date.year
        start_year = current_year - past_n_years

        # These 2 variables are used to shade the current year region
        previous_month = (current_date - relativedelta(months=1)).strftime("%Y-%m-%d")[:7] + "-01"
        start_of_current_year = str(current_year) + "-01-01"

        headers = {"Content-type": "application/json"}
        data = json.dumps(
            {
                "seriesid": [series_id],
                "startyear": str(start_year),
                "endyear": str(current_year),
                "registrationkey": bls_key,
            }
        )
        p = requests.post(
            "https://api.bls.gov/publicAPI/v2/timeseries/data/",
            data=data,
            headers=headers,
        )
        p.raise_for_status()  # Raise an exception for HTTP errors
        json_data = json.loads(p.text)

        df_list = []
        for series in json_data["Results"]["series"]:
            df = pd.DataFrame.from_dict(series["data"])
            # Transformations:
            # Create series_id column
            # Filter to just periods M01, M02, ..., M12
            # Create year-month column as date data type
            # Cast value column as float data type
            # Keep only series_id, year_month, and value columns
            df = (
                df.assign(series_id=series["seriesID"])
                .query("(period >= 'M01') & (period <= 'M12')")
                .assign(
                    year_month=pd.to_datetime(
                        df["year"].astype("str") + "-" + df["period"].str[-2:],
                        format="%Y-%m",
                    )
                )
                .assign(value=df["value"].astype("float"))
            )[["series_id", "year_month", "value"]]
            df_list.append(df)

        df_final = pd.concat(df_list, axis="columns")

        fig, ax = plt.subplots(figsize=(8, 5))
        sns.lineplot(
            data=df_final,
            x="year_month",
            y="value",
            ax=ax,
        )
        # Created shaded region for current year
        ax.fill_between(
            x=[start_of_current_year, previous_month],
            y1=[int(df_final["value"].max()) + 1, int(df_final["value"].max()) + 1],
            alpha=0.2,
            color="blue",
        )
        ax.set_ylim(int(df_final["value"].min()) - 1, int(df_final["value"].max()) + 1)
        ax.spines[["right", "top"]].set_visible(False)
        plt.xlabel("Year")
        plt.ylabel("Value")
        plt.suptitle(series_descr)

        # If default of past 19 years is chosen, then add recessions and covid pandemic regions
        if past_n_years == 19:
            # Create shaded vertical regions that indicate when recessions and COVID-19 pandemic happened
            # https://en.wikipedia.org/wiki/List_of_recessions_in_the_United_States
            ax.fill_between(
                x=["2001-03-01", "2001-11-01"],
                y1=[int(df_final["value"].max()) + 1, int(df_final["value"].max()) + 1],
                alpha=0.2,
                color="gray",
            )
            ax.fill_between(
                x=["2007-12-01", "2009-06-01"],
                y1=[int(df_final["value"].max()) + 1, int(df_final["value"].max()) + 1],
                alpha=0.2,
                color="gray",
            )
            ax.fill_between(
                x=["2020-02-01", "2020-04-01"],
                y1=[int(df_final["value"].max()) + 1, int(df_final["value"].max()) + 1],
                alpha=0.2,
                color="gray",
            )
            plt.title("grey=recession / blue=current year", fontsize=10)
            plt.tight_layout()
            plt.show()
        # else don't add the recession and covid pandemic regions
        else:
            plt.title("blue=current year", fontsize=10)
            plt.tight_layout()
            plt.show()
    except requests.exceptions.RequestException as e:
        print("An error occurred during the HTTP request:", e)
    except (ValueError, KeyError) as e:
        print("An error occurred while processing the data:", e)
