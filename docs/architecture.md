# Architecture and data contract

The project uses a setuptools `src` layout. Install it in editable mode during development. Wheels include the bundled CSV, loaded with `importlib.resources` independently of the working directory. `app.py` calls `dashboard.main()`; importing the dashboard does not render it.

| Module | Responsibility | Tests |
| --- | --- | --- |
| `data_loader.py` | CSV validation and bundled resources | `tests/unit/test_data_loader.py` |
| `analytics.py` | Allocation, simulations, financial statistics | `tests/unit/test_analytics.py` |
| `charts.py` | Plotly styling without Streamlit | `tests/unit/test_charts.py` |
| `dashboard.py` | Controls, cached parsing, charts, exports | `tests/unit/test_dashboard.py` and integration tests |
| `app.py` | Streamlit launch adapter | `tests/integration/test_app.py` |

The presentation layer depends on the calculation, loading, and chart modules; those modules do not depend on the presentation layer. `__init__.py` is a package marker with no executable behavior requiring its own unit test.

## Data and calculation contracts

CSV files require a `Date` column and at least one ticker column. Dates must be valid and unique. Prices must be complete, finite, numeric, and positive, with at least two observations. Rows are sorted by date. Invalid data is rejected rather than filled. The original CSV is preserved byte for byte.

Calculation functions expect validated prices with a chronological datetime index. Allocations must include all selected tickers, be finite and nonnegative, and have a positive total. Capital must be finite and positive. Weights are normalized to 100%.

- Buy and hold invests the initial allocation in fractional shares.
- Daily rebalancing restores target weights after each observation.
- The comparison equally allocates to selected stocks and holds those shares.
- CAGR uses elapsed calendar days / 365.25.
- Annual volatility uses sample daily-return standard deviation times square root of 252.
- Sharpe uses mean daily excess return times 252 divided by annual volatility. Annual risk-free rates are converted to compounded daily rates.
- Maximum drawdown is the minimum value / running peak minus one.
- Insufficient observations and zero volatility produce undefined statistics displayed as N/A.

The dataset does not document split or dividend adjustment. Results use supplied historical prices without adding dividends, fees, taxes, deposits, withdrawals, or live quotes.
