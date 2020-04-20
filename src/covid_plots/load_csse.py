import logging
import os
import re
from typing import Dict, Iterable

import pandas as pd

logger = logging.getLogger(__name__)
logger.info("Importing %s", __name__)


def _get_default_repo_dir():
    # it would be possible to create dynamic checkout in /tmp here, but just for simplicity:
    logger.info("Assume checkout of https://github.com/CSSEGISandData/COVID-19 is located next to covid-plots package")
    return os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, "COVID-19")


class DataCsseTimeSeries:
    def __init__(self, repo_dir=_get_default_repo_dir()):
        self._repo_dir = repo_dir
        if not os.path.isdir(repo_dir):
            raise EnvironmentError(f"Failed to find CSSE data repo (https://github.com/CSSEGISandData/COVID-19). Expected here: {repo_dir}")
        ts_dir = os.path.join(repo_dir, "csse_covid_19_data", "csse_covid_19_time_series")
        if not os.path.isdir(ts_dir):
            raise EnvironmentError(f"Failed to find CSSE timeseries data. Expected here: {ts_dir}")
        self._data = {}  # type: Dict[str, Dict[str, pd.DataFrame]]
        for region in ["global", "US"]:
            if region not in self._data:
                self._data[region] = {}  # type: Dict[str, pd.DataFrame]
            for data_type in ["confirmed", "deaths", "recovered"]:
                filename = os.path.join(ts_dir, f"time_series_covid19_{data_type}_{region}.csv")
                if not os.path.exists(filename):
                    logger.warning("%s", f"Failed locating data file for {region}/{data_type} (expected for US/recovered): {filename}")
                else:
                    self._data[region][data_type] = pd.read_csv(filename)
                    self._data[region][data_type].rename({"Country/Region": "CountryOrRegion"}, axis="columns", inplace=True)

    def get_countries(self):
        """Get list of all countries in global dataset."""
        return set(self._data["global"]["confirmed"]["CountryOrRegion"].unique())

    def get_data_for_country(self, country: str) -> pd.DataFrame:
        """Return dataframe with columns "date, confirmed, deaths, recovered" for country from global dataset."""
        return self.get_data_for_countries([country])

    def get_data_for_countries(self, countries: Iterable[str]) -> pd.DataFrame:
        """Return dataframe with columns "date, confirmed, deaths, recovered" for sum of countries from global dataset."""
        dates = [date for date in self._data["global"]["confirmed"].columns if re.search("[0-9]+/[0-9]+/[0-9]+", date) is not None]
        columns = {}
        for data_type in ["confirmed", "deaths", "recovered"]:
            _filter = self._data["global"][data_type]["CountryOrRegion"].isin(countries)
            sum_data = self._data["global"][data_type][_filter].sum(axis=0)
            columns[data_type] = [sum_data[date] for date in dates]
        converted_dates = [pd.datetime.strptime(date, "%m/%d/%y").date() for date in dates]
        return pd.DataFrame(dict(date=converted_dates, **columns))
