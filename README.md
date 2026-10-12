# Portfolio Lens

A Python and Streamlit portfolio analyser using the bundled FAANG price dataset (2020–2023). Supports custom CSV uploads, portfolio allocations, buy-and-hold and daily rebalancing, performance and risk charts, and CSV exports.

## Structure

```text
Week1/
├── app.py                         # Thin Streamlit entry point
├── pyproject.toml                 # Packaging, dependencies, test configuration
├── requirements.txt               # Delegates installation to pyproject.toml
├── .streamlit/config.toml          # Theme configuration
├── src/portfolio_lens/
│   ├── __init__.py
│   ├── analytics.py               # Simulations and financial metrics
│   ├── data_loader.py             # Validation and resource loading
│   ├── charts.py                  # Shared Plotly styling
│   ├── dashboard.py               # Streamlit presentation layer
│   └── datasets/faang_stocks.csv   # Bundled, unmodified source data
├── tests/
│   ├── conftest.py                 # Deterministic fixtures
│   ├── unit/                      # Tests matching each Python module
│   └── integration/test_app.py     # Launch script and user flows
├── scripts/run.ps1                 # Windows launcher
└── docs/
    ├── architecture.md
    └── development.md
```

Local `.venv313`, `.venv`, and `.python` directories are tooling environments excluded from version control.

## Run locally

After completing the setup below, run from the repository root:

```powershell
.\.venv\Scripts\python -m streamlit run app.py
# Or:
.\scripts\run.ps1
```

Open http://localhost:8501.

## Fresh setup

Python 3.11–3.13 is recommended for dependency compatibility. Install the package before launching.

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\python -m streamlit run app.py
```

For runtime dependencies only, install with `pip install -e .` or `pip install -r requirements.txt`. `pyproject.toml` is the dependency source of truth.

## Verify and build

```powershell
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -m pytest tests/unit
.\.venv\Scripts\python -m pytest tests/integration
.\.venv\Scripts\python -m pytest --cov=portfolio_lens --cov-report=term-missing
.\.venv\Scripts\python -m build
```

See [architecture and assumptions](docs/architecture.md) and [development workflow](docs/development.md).
