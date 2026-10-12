"""Historical portfolio simulations and performance statistics."""
import numpy as np
import pandas as pd


def portfolio_values(prices, weights, capital, rebalance=False):
    if not np.isfinite(capital) or capital <= 0:
        raise ValueError("Initial capital must be finite and positive.")
    weights = pd.Series(weights).reindex(prices.columns)
    if not np.isfinite(weights.to_numpy()).all() or (weights < 0).any() or weights.sum() <= 0:
        raise ValueError("Allocations must be nonnegative with a positive total.")
    weights = weights / weights.sum()
    if rebalance:
        returns = prices.pct_change(fill_method=None).iloc[1:].mul(weights).sum(axis=1)
        values = pd.concat([pd.Series([capital], index=prices.index[:1]), capital * (1 + returns).cumprod()])
    else:
        values = prices.div(prices.iloc[0]).mul(weights).sum(axis=1) * capital
    return values.rename("Portfolio")


def metrics(values, risk_free=0.0):
    returns = values.pct_change(fill_method=None).dropna()
    years = (values.index[-1] - values.index[0]).days / 365.25
    volatility = returns.std(ddof=1) * np.sqrt(252) if len(returns) > 1 else np.nan
    excess = returns - ((1 + risk_free) ** (1 / 252) - 1)
    sharpe = excess.mean() * 252 / volatility if volatility > 1e-12 else np.nan
    return {
        "Total return": values.iloc[-1] / values.iloc[0] - 1,
        "CAGR": (values.iloc[-1] / values.iloc[0]) ** (1 / years) - 1 if years > 0 else np.nan,
        "Annual volatility": volatility,
        "Sharpe ratio": sharpe,
        "Max drawdown": (values / values.cummax() - 1).min(),
    }
