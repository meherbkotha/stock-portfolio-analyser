"""Deterministic fixtures shared by the unit tests."""
import pandas as pd
import pytest


@pytest.fixture
def prices():
    return pd.DataFrame(
        {"A": [100.0, 200.0, 100.0], "B": [100.0, 100.0, 200.0]},
        index=pd.date_range("2020-01-01", periods=3, name="Date"),
    )
