"""Unit tests for the presentation layer's small adapters."""
from unittest.mock import patch
import plotly.graph_objects as go
import pytest

from portfolio_lens.dashboard import chart, read_data


def test_read_data_parses_uploaded_bytes():
    assert read_data(b"Date,A\n2020-01-01,10\n2020-01-02,12").A.tolist() == [10, 12]


def test_read_data_propagates_validation_errors():
    with pytest.raises(ValueError):
        read_data(b"Date,A\n2020-01-01,-10\n2020-01-02,12")


def test_chart_passes_styled_figure_to_streamlit():
    figure = go.Figure()
    with patch("portfolio_lens.dashboard.st.plotly_chart") as render:
        chart(figure)
    render.assert_called_once_with(figure, width="stretch")
    assert figure.layout.paper_bgcolor == "rgba(0,0,0,0)"
