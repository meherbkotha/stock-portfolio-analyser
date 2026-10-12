"""Shared Plotly styling, independent of Streamlit rendering."""
COLORS = ["#38BDF8", "#A78BFA", "#34D399", "#FBBF24", "#FB7185", "#818CF8"]


def style_figure(fig):
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=12, r=12, t=30, b=12),
                      legend_title_text="", colorway=COLORS)
    return fig


