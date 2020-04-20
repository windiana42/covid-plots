import matplotlib.pyplot as plt
import numpy as np
from covid_plots.load_csse import DataCsseTimeSeries
import datetime as dt


def plot_country(data_src: DataCsseTimeSeries, country: str):
    df = data_src.get_data_for_country(country)
    df["infected"] = df["confirmed"] - df["recovered"] - df["deaths"]
    cutoff = df["confirmed"].max() / 100.
    cutoff_idx = df.query(f"confirmed>{cutoff}").iloc[0].name

    fig, ax = plt.subplots(figsize=(5, 3))
    ax.stackplot(df["date"], df[['infected', 'deaths', 'recovered']].T, labels=['infected', 'deaths', 'recovered'])
    ax.set_title(f'Covid19 infections for {country}')
    ax.legend(loc='upper left')
    ax.set_ylabel('Total debt')
    ax.set_xlim(xmin=df["date"].iloc[cutoff_idx], xmax=df["date"].iloc[-1])
    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    data_src = DataCsseTimeSeries()
    plot_country(data_src, "Germany")
    plot_country(data_src, "Austria")
    plot_country(data_src, "Switzerland")
