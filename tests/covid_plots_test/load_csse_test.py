from covid_plots.load_csse import DataCsseTimeSeries
import pandas as pd
import logging

logger = logging.getLogger(__name__)
logger.info("Importing %s", __name__)


def test_smoke_load_data():
    """Smoke test that loads data but checks nothing"""
    data_src = DataCsseTimeSeries()
    assert data_src is not None
    assert len(data_src.get_countries()) > 100
    for country in data_src.get_countries():
        assert isinstance(data_src.get_data_for_country(country), pd.DataFrame)
    assert isinstance(data_src.get_data_for_countries(data_src.get_countries()), pd.DataFrame)
