"""Unit tests for portfolio_lens.data_loader."""
from io import BytesIO, StringIO

import pandas as pd
import pytest

from portfolio_lens.data_loader import bundled_prices_bytes, load_prices


def test_sorts_dates_and_parses_numeric_prices():
    actual = load_prices(StringIO("Date,A\n2020-01-02,20\n2020-01-01,10"))
    assert actual.index.name == "Date"
    assert actual.index.is_monotonic_increasing
    assert actual["A"].tolist() == [10, 20]
    assert isinstance(actual.index, pd.DatetimeIndex)


@pytest.mark.parametrize("csv", [
    "Day,A\n2020-01-01,1\n2020-01-02,2",
    "Date\n2020-01-01\n2020-01-02",
    "Date,A\ninvalid,1\n2020-01-02,2",
    "Date,A\n2020-01-01,1\n2020-01-01,2",
    "Date,A\n2020-01-01,0\n2020-01-02,2",
    "Date,A\n2020-01-01,-1\n2020-01-02,2",
    "Date,A\n2020-01-01,abc\n2020-01-02,2",
    "Date,A\n2020-01-01,\n2020-01-02,2",
    "Date,A\n2020-01-01,inf\n2020-01-02,2",
    "Date,A\n2020-01-01,1",
    "Date,A\n",
])
def test_rejects_invalid_data(csv):
    with pytest.raises(ValueError):
        load_prices(StringIO(csv))


def test_bundled_resource_is_available_outside_project_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    prices = load_prices(BytesIO(bundled_prices_bytes()))
    assert list(prices.columns) == ["AAPL", "AMZN", "GOOGL", "META", "NFLX"]
    assert prices.index[0] == pd.Timestamp("2020-01-02")
    assert prices.index[-1] == pd.Timestamp("2023-12-29")
