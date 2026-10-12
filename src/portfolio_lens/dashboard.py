"""Streamlit presentation layer; importable without rendering the app."""
from io import BytesIO
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from portfolio_lens.analytics import metrics, portfolio_values
from portfolio_lens.data_loader import load_prices, bundled_prices_bytes
from portfolio_lens.charts import style_figure


def chart(fig):
    st.plotly_chart(style_figure(fig), width="stretch")


@st.cache_data
def read_data(content):
    return load_prices(BytesIO(content))


def main():
    """Render the interactive portfolio dashboard."""
    st.set_page_config(page_title="Portfolio Lens", page_icon="📈", layout="wide")
    st.title("Portfolio Lens")
    st.caption("Build a portfolio. Explore its performance. Understand its risk.")
    with st.sidebar:
        st.header("Portfolio setup")
        uploaded = st.file_uploader("Use your own price dataset", type=["csv"])
        st.caption("CSV format: Date followed by ticker columns containing positive prices.")

    try:
        content = uploaded.getvalue() if uploaded else bundled_prices_bytes()
        all_prices = read_data(content)
    except (ValueError, OSError, pd.errors.ParserError) as error:
        st.error(f"Unable to load prices: {error}")
        st.stop()

    with st.sidebar:
        tickers = st.multiselect("Stocks", list(all_prices.columns), default=list(all_prices.columns))
        period = st.date_input("Analysis period", value=(all_prices.index[0].date(), all_prices.index[-1].date()),
                               min_value=all_prices.index[0].date(), max_value=all_prices.index[-1].date())
        capital = st.number_input("Initial investment ($)", min_value=100.0, value=10000.0, step=100.0)
        strategy = st.selectbox("Investment strategy", ["Buy and hold", "Daily rebalancing"])
        risk_free = st.number_input("Annual risk-free rate (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.25) / 100
        st.subheader("Allocation weights")
        equal = st.checkbox("Equal weights", value=True)
        raw_weights = {ticker: 1.0 if equal else st.number_input(f"{ticker} weight", min_value=0.0, value=20.0, step=5.0, key=f"weight_{ticker}") for ticker in tickers}
        st.caption("Weights are normalized to 100%. Zero weight excludes a stock from the investment.")

    if not tickers or len(period) != 2:
        st.info("Select at least one stock and a complete date range.")
        st.stop()
    prices = all_prices.loc[str(period[0]):str(period[1]), tickers]
    if len(prices) < 2 or sum(raw_weights.values()) <= 0:
        st.warning("Choose a period with at least two observations and a positive allocation total.")
        st.stop()
    weights = pd.Series(raw_weights) / sum(raw_weights.values())
    values = portfolio_values(prices, weights, capital, strategy == "Daily rebalancing")
    benchmark = portfolio_values(prices, dict.fromkeys(tickers, 1.0), capital)
    stats = metrics(values, risk_free)
    st.caption(f"{prices.index[0]:%b %d, %Y} – {prices.index[-1]:%b %d, %Y} · {len(prices):,} observations · {strategy} · Historical CSV data")
    cols = st.columns(4)
    cols[0].metric("Portfolio value", f"${values.iloc[-1]:,.2f}", f"${values.iloc[-1] - capital:,.2f}")
    cols[1].metric("Total return", f"{stats['Total return']:.2%}")
    cols[2].metric("Annual volatility", f"{stats['Annual volatility']:.2%}" if np.isfinite(stats['Annual volatility']) else "N/A")
    cols[3].metric("Max drawdown", f"{stats['Max drawdown']:.2%}")
    overview, stocks, risk, data = st.tabs(["Portfolio overview", "Stock comparison", "Risk analysis", "Data & exports"])

    with overview:
        st.subheader("Growth of your investment")
        growth = pd.concat([values, benchmark.rename("Equal-weight buy-and-hold comparison")], axis=1)
        chart(px.line(growth, labels={"value": "Value ($)", "Date": ""}))
        left, right = st.columns([1, 1.5])
        with left:
            st.subheader("Initial allocation")
            chart(px.pie(names=weights.index, values=weights.values, hole=0.65))
        with right:
            st.subheader("Performance summary")
            rows = pd.DataFrame({"Metric": list(stats), "Value": [f"{v:.2f}" if k == "Sharpe ratio" and np.isfinite(v) else f"{v:.2%}" if np.isfinite(v) else "N/A" for k, v in stats.items()]})
            st.dataframe(rows, hide_index=True, width="stretch")
            st.caption("CAGR uses elapsed calendar days; volatility and Sharpe use 252 trading days per year. Short periods can produce extreme annualized values.")

    with stocks:
        st.subheader("Stock performance · starting value = 100")
        chart(px.line(prices.div(prices.iloc[0]) * 100, labels={"value": "Indexed price", "Date": ""}))
        summary = pd.DataFrame({ticker: metrics(prices[ticker], risk_free) for ticker in tickers}).T
        summary.insert(0, "Final price ($)", prices.iloc[-1])
        summary.insert(1, "Initial weight", weights)
        st.dataframe(summary.style.format({col: "{:.2%}" for col in summary.columns if col not in ["Final price ($)", "Sharpe ratio"]}).format({"Final price ($)": "${:,.2f}", "Sharpe ratio": "{:.2f}"}), width="stretch")

    with risk:
        st.subheader("Portfolio drawdown")
        drawdown = (values / values.cummax() - 1) * 100
        chart(px.area(drawdown.rename("Drawdown"), labels={"value": "Drawdown (%)", "Date": ""}))
        left, right = st.columns(2)
        returns = prices.pct_change(fill_method=None).dropna()
        with left:
            st.subheader("Daily return correlations")
            chart(px.imshow(returns.corr(), zmin=-1, zmax=1, color_continuous_scale="RdBu", text_auto=".2f", aspect="auto"))
            st.caption("Correlation is undefined for constant returns or fewer than two daily returns.")
        with right:
            st.subheader("Daily portfolio returns")
            chart(px.histogram(x=values.pct_change().dropna() * 100, nbins=45, labels={"x": "Daily return (%)", "y": "Days"}))

    with data:
        st.subheader("Price observations")
        st.dataframe(prices, width="stretch")
        st.download_button("Download selected prices", prices.to_csv().encode(), "selected_prices.csv", "text/csv")
        export = growth.copy()
        export["Daily return"] = values.pct_change()
        export["Drawdown"] = values / values.cummax() - 1
        st.download_button("Download portfolio history", export.to_csv().encode(), "portfolio_history.csv", "text/csv")

    with st.expander("Data and calculation assumptions"):
        st.write("This app uses only the uploaded or bundled historical prices; it does not retrieve live quotes. The CSV does not specify whether prices are adjusted for splits or dividends. Results therefore reflect the supplied price series only.")
        st.write("Buy and hold invests the initial allocation using fractional shares. Daily rebalancing restores target weights after each observation. Both assume no fees, taxes, deposits, withdrawals, or trading constraints. The comparison invests equally in your selected stocks and holds those shares.")
