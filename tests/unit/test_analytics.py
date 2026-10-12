"""Unit tests for portfolio_lens.analytics using hand-calculated examples."""
import numpy as np
import pandas as pd
import pytest

from portfolio_lens.analytics import metrics, portfolio_values


def test_buy_and_hold_normalizes_weights(prices):
    actual = portfolio_values(prices, {"A": 20, "B": 20}, 100)
    np.testing.assert_allclose(actual, [100, 150, 150])
    assert actual.name == "Portfolio"
    pd.testing.assert_index_equal(actual.index, prices.index)


def test_daily_rebalancing_restores_target_weights(prices):
    np.testing.assert_allclose(
        portfolio_values(prices, {"B": 1, "A": 1}, 100, True),
        [100, 150, 187.5],
    )


def test_zero_weight_excludes_stock(prices):
    np.testing.assert_allclose(portfolio_values(prices, {"A": 1, "B": 0}, 100), prices.A)


@pytest.mark.parametrize("weights", [
    {"A": 0, "B": 0}, {"A": -1, "B": 2}, {"A": 1},
    {"A": float("nan"), "B": 1}, {"A": float("inf"), "B": 1},
])
def test_rejects_invalid_weights(prices, weights):
    with pytest.raises(ValueError, match="Allocations"):
        portfolio_values(prices, weights, 100)


@pytest.mark.parametrize("capital", [0, -10, float("nan"), float("inf")])
def test_rejects_invalid_capital(prices, capital):
    with pytest.raises(ValueError, match="capital"):
        portfolio_values(prices, {"A": 1, "B": 1}, capital)


def test_metrics_match_known_returns(prices):
    result = metrics(prices.A)
    # Daily returns are +100% and -50%; final price equals initial price.
    expected_volatility = np.std([1, -.5], ddof=1) * np.sqrt(252)
    assert result["Total return"] == 0
    assert result["CAGR"] == 0
    assert result["Max drawdown"] == -.5
    assert result["Annual volatility"] == pytest.approx(expected_volatility)
    assert result["Sharpe ratio"] == pytest.approx(.25 * 252 / expected_volatility)


def test_risk_free_rate_reduces_sharpe(prices):
    result = metrics(prices.A, .05)
    daily_rate = 1.05 ** (1 / 252) - 1
    assert result["Sharpe ratio"] == pytest.approx((.25 - daily_rate) * 252 / result["Annual volatility"])


def test_cagr_uses_calendar_duration():
    values = pd.Series([100., 121.], index=pd.to_datetime(["2020-01-01", "2022-01-01"]))
    assert metrics(values)["CAGR"] == pytest.approx(1.21 ** (365.25 / 731) - 1)


def test_constant_portfolio_has_undefined_sharpe(prices):
    result = metrics(pd.Series(100., index=prices.index))
    assert result["Annual volatility"] == 0
    assert result["Max drawdown"] == 0
    assert np.isnan(result["Sharpe ratio"])


def test_two_observations_have_undefined_sample_volatility(prices):
    result = metrics(prices.A.iloc[:2])
    assert result["Total return"] == 1
    assert np.isnan(result["Annual volatility"])
    assert np.isnan(result["Sharpe ratio"])
