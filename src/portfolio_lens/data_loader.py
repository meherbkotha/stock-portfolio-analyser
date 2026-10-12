"""CSV validation and access to the bundled dataset."""
from importlib.resources import files
import numpy as np
import pandas as pd


def load_prices(source):
    frame = pd.read_csv(source)
    if "Date" not in frame or len(frame.columns) < 2:
        raise ValueError("CSV must contain Date and at least one stock price column.")
    dates = pd.to_datetime(frame.pop("Date"), errors="coerce")
    if dates.isna().any() or dates.duplicated().any():
        raise ValueError("Dates must be valid and unique.")
    prices = frame.apply(pd.to_numeric, errors="coerce")
    if prices.empty or prices.isna().any().any() or not np.isfinite(prices.to_numpy()).all():
        raise ValueError("Every stock must have a finite numeric price on every date.")
    if (prices <= 0).any().any():
        raise ValueError("Stock prices must be greater than zero.")
    prices.index = pd.DatetimeIndex(dates, name="Date")
    prices = prices.sort_index()
    if len(prices) < 2:
        raise ValueError("At least two price observations are required.")
    return prices



def bundled_prices_bytes():
    """Read package data independently of the working directory."""
    return files("portfolio_lens").joinpath("datasets/faang_stocks.csv").read_bytes()
