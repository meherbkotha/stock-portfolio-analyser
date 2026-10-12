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
│   ├── assistant.py               # Portfolio context and OpenAI service
│   ├── chat_ui.py                 # Chat controls and session history
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

## Enable the AI assistant

The AI assistant tab answers questions using the current portfolio's calculated summary. It uses the OpenAI Responses API and defaults to `gpt-4.1-mini`. Set another available Responses-compatible model with `OPENAI_MODEL` if needed.

For Streamlit Community Cloud, open **App settings → Secrets** and add:

```toml
OPENAI_API_KEY = "your-api-key"
OPENAI_MODEL = "gpt-4.1-mini"
```

Save and reboot the app. Locally, copy `.streamlit/secrets.example.toml` to `.streamlit/secrets.toml` and replace the placeholder, or set `OPENAI_API_KEY` in the server environment. The real secrets file is ignored by Git. An API account with billing and access to the configured model is required; API requests incur charges on that account.

Questions, recent conversation, and calculated portfolio summaries are sent to OpenAI only when a question is submitted. The full CSV is not sent. Responses are requested with `store=False`; this is not a guarantee of zero retention by the provider. Chat history is kept in the browser's Streamlit session, clears when portfolio settings change, and can be cleared manually.

Requests use a 30-second timeout, no automatic retries, a 3,000-character question limit, and a 1,200-token response limit. Each session allows 20 attempts. This session limit is a usability/cost guard, not account-wide access control; use provider billing limits or private app sharing to control a public deployment's usage. AI answers may contain mistakes and cannot retrieve live quotes or provide forecasts.

Without a key, all portfolio features remain usable and chat displays setup guidance. Tests use mocked API responses and never require an API key.

## Verify and build

```powershell
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -m pytest tests/unit
.\.venv\Scripts\python -m pytest tests/integration
.\.venv\Scripts\python -m pytest --cov=portfolio_lens --cov-report=term-missing
.\.venv\Scripts\python -m build
```

See [architecture and assumptions](docs/architecture.md) and [development workflow](docs/development.md).
