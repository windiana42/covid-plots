from typing import List, Optional

import matplotlib.pyplot as plt
from covid_plots.load_csse import DataCsseTimeSeries
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters
import numpy as np
import pandas as pd
import statsmodels.api as sm


def plot_country(data_src: DataCsseTimeSeries, country: str):
    fig, ax = plt.subplots(figsize=(5, 3))
    _subplot_country(ax, country, data_src)
    fig.tight_layout()
    plt.show()


def plot_countries(data_src: DataCsseTimeSeries, countries: List[str],
                   columns: int = 2, weeks: int = -1, death_only=False,
                   fix_recovered_weeks=3, regress_countries=None):
    rows = (len(countries) + columns - 1) // columns
    fig, axs = plt.subplots(rows, columns, figsize=(5 * columns, 3 * rows))

    for i, country in enumerate(countries):
        _subplot_country(axs[i % rows, i // rows], country, data_src, weeks, death_only,
                         fix_recovered_weeks=fix_recovered_weeks, regress_countries=regress_countries)

    fig.tight_layout()
    plt.show()


def _subplot_country(ax, country, data_src, weeks: int = -1, death_only=False,
                     fix_recovered_weeks=3, regress_countries: Optional[List[str]] = None):
    df = data_src.get_data_for_country(country)
    df = add_probably_recovered(df, fix_recovered_weeks)
    cutoff = df["confirmed"].max() / 100.
    cutoff_idx = df.query(f"confirmed>{cutoff}").iloc[0].name
    if weeks > 0:
        cutoff_idx = -weeks * 7
        cols = ['infected', 'deaths']
    else:
        # cutoff_idx = 0
        cols = ['infected', 'deaths', 'recovered']
        if fix_recovered_weeks is not None:
            cols = ['infected', 'deaths', 'recovered', 'probably_recovered']
    if death_only:
        cols = ['deaths']

    predict = get_regression_line(data_src, country, df, cutoff_idx, fix_recovered_weeks, regress_countries)

    color_map = ["#0000b6", "#e07000", "#00b000", "#00e000"]
    ax.stackplot(df["date"].iloc[cutoff_idx:], df[cols].iloc[cutoff_idx:].T,
                 labels=cols, colors=color_map)
    if predict is not None:
        predict.plot(ax=ax, color='r')
    ax.set_title(f'Covid19 infections for {country} ({list(df["date"])[-1]})')
    ax.legend(loc='upper left')
    ax.set_ylabel('Total debt')
    ax.set_xlim(xmin=df["date"].iloc[cutoff_idx], xmax=df["date"].iloc[-1])
    months = mdates.MonthLocator()  # every month
    days = mdates.DayLocator()  # every day
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_minor_locator(days)


def get_regression_line(data_src, country, df, cutoff_idx, fix_recovered_weeks, regress_countries) -> Optional[pd.Series]:
    if regress_countries is not None:
        offset_days = 14
        regress_dfs = [add_probably_recovered(data_src.get_data_for_country(country), fix_recovered_weeks) for country in regress_countries]
        regress_dfs.append(df.shift(offset_days))
        cutoff_idx = max(cutoff_idx,offset_days)
        regress_countries = regress_countries + [f"self[-{offset_days}]"]
        model = sm.OLS(df.loc[cutoff_idx:, "infected"], pd.DataFrame({i: r.loc[cutoff_idx:, "infected"]
                                                                        for i, r in enumerate(regress_dfs)}))
        results = model.fit()
        predict = sum([f * df["infected"] for f, df in zip(results.params, regress_dfs)])
        print(f"{country}=" + " + ".join([f"{round(f,2)}*{c}" for f, c in zip(results.params, regress_countries)]))
        predict.index = df["date"]
    else:
        predict = None
    return predict


def add_probably_recovered(df, fix_recovered_weeks):
    df["probably_recovered"] = 0
    if fix_recovered_weeks is not None:
        df["new_recovered"] = np.maximum(
            (df["confirmed"].shift(fix_recovered_weeks * 7).fillna(0)
             - df["deaths"]),
            df["recovered"])
        df["probably_recovered"] = df["new_recovered"] - df["recovered"]
    df["infected"] = df["confirmed"] - df["recovered"] - df["deaths"] - df["probably_recovered"]
    return df


if __name__ == "__main__":
    import logging

    """initialize logging library for pytest."""
    logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger(__name__)
    logger.info("Importing %s", __name__)

    register_matplotlib_converters()
    _data_src = DataCsseTimeSeries()
    logger.info("\n%s", "\n".join(sorted(_data_src.get_countries())))
    _countries = [
        "Germany", "Austria", "Switzerland", "Sweden", "Korea, South",
        "India", "Italy", "France", "Spain", "Singapore", "United Kingdom", "US"
    ]
    # for country in countries:
    #     plot_country(data_src, country)
    # plot_countries(_data_src, countries, columns=3)
    # plot_countries(data_src, countries, columns=3, death_only=True)

    # plot_countries(_data_src, countries, columns=3, weeks=10, fix_recovered_weeks=1)

    plot_countries(_data_src, _countries, columns=3, weeks=30, regress_countries=["Germany", "France"])

    # plot_countries(data_src, countries, columns=3, weeks=4, death_only=True)
    # plot_countries(data_src, countries, columns=3, weeks=6)
