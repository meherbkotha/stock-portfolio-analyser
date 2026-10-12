"""Streamlit integration tests for the launch script and user flows."""
from pathlib import Path
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[2] / "app.py"


@pytest.fixture
def app():
    session = AppTest.from_file(str(APP), default_timeout=30).run()
    assert not session.exception
    return session


def test_default_dashboard_and_rebalancing(app):
    assert len(app.metric) == 4
    assert len(app.tabs) == 4
    app.selectbox[0].set_value("Daily rebalancing").run()
    assert not app.exception


def test_empty_stock_selection_displays_guidance(app):
    app.multiselect[0].set_value([]).run()
    assert not app.exception
    assert len(app.info) == 1


def test_zero_allocation_displays_warning(app):
    app.checkbox[0].uncheck().run()
    for ticker in ["AAPL", "AMZN", "GOOGL", "META", "NFLX"]:
        app.number_input(key=f"weight_{ticker}").set_value(0)
    app.run()
    assert not app.exception
    assert len(app.warning) == 1


def test_single_stock_and_short_period(app):
    app.multiselect[0].set_value(["AAPL"]).run()
    app.date_input[0].set_value((pd.Timestamp("2020-01-02").date(), pd.Timestamp("2020-01-03").date())).run()
    assert not app.exception
    assert app.metric[2].value == "N/A"


def test_period_without_enough_prices_displays_warning(app):
    day = pd.Timestamp("2020-01-02").date()
    app.date_input[0].set_value((day, day)).run()
    assert not app.exception
    assert len(app.warning) == 1


def test_invalid_dataset_displays_error(monkeypatch):
    monkeypatch.setattr("portfolio_lens.dashboard.bundled_prices_bytes", lambda: b"Date,A\n2020-01-01,-1\n2020-01-02,2")
    session = AppTest.from_file(str(APP), default_timeout=30).run()
    assert not session.exception
    assert len(session.error) == 1
    assert "Unable to load prices" in session.error[0].value
