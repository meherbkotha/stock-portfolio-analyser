# Development workflow

## Plan and implement

Record intended behavior and acceptance criteria before a change. Keep CSV parsing in `data_loader.py`, calculations in `analytics.py`, chart styling in `charts.py`, and Streamlit interaction in `dashboard.py`. Update contracts and assumptions when behavior changes.

Dependencies belong in `pyproject.toml`. `requirements.txt` delegates to that file to prevent drift. Use editable installation rather than modifying `sys.path` or relying on the working directory.

## Test and review

Run `python -m pytest` in the installed project environment. Unit tests use deterministic examples with hand-calculated expectations. Integration tests use Streamlit AppTest to exercise the launch script and user flows. Unit-test filenames match the modules they exercise.

Inspect coverage with `python -m pytest --cov=portfolio_lens --cov-report=term-missing`. Add regression tests for bugs and meaningful edge cases. Review input handling, calculation assumptions, dataset changes, and user-visible behavior along with code changes.

## Build and release

Run `python -m build` to generate a source distribution and wheel in `dist/`. Verify the wheel includes `portfolio_lens/datasets/faang_stocks.csv` and test package imports outside the project directory. Update the version in `pyproject.toml` for a release.

Deploy the repository with `app.py` as the Streamlit entry point and install the package first. Theme configuration remains in `.streamlit`. Build artifacts, caches, local runtimes, and environments are excluded from version control.
