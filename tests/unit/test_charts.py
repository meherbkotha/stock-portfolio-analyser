"""Unit tests for portfolio_lens.charts."""
import plotly.graph_objects as go

from portfolio_lens.charts import COLORS, style_figure


def test_styling_preserves_data_and_applies_shared_theme():
    figure = go.Figure(go.Scatter(x=[1, 2], y=[10, 20]))
    styled = style_figure(figure)
    assert styled is figure
    assert list(styled.data[0].y) == [10, 20]
    assert styled.layout.paper_bgcolor == "rgba(0,0,0,0)"
    assert list(styled.layout.colorway) == COLORS
    assert styled.layout.margin.l == 12
