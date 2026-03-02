"""
Plotly chart helpers -- dark theme with Royals purple/gold accents.
"""
import plotly.graph_objects as go
import plotly.express as px

# Royals palette -- tuned for dark backgrounds
PURPLE_SCALE = ["#7c3aed", "#9b5de5", "#b794f6", "#6A0DAD", "#5C2D91"]
GOLD_SCALE = ["#FFD700", "#FFA500", "#FFB347", "#FFCC33", "#FFE066"]
ROYALS_PALETTE = [
    "#7c3aed", "#FFD700", "#9b5de5", "#FFA500",
    "#b794f6", "#FFB347", "#6A0DAD", "#FFCC33",
]

# Base layout (no xaxis/yaxis to avoid conflicts with per-chart overrides)
_LAYOUT_DEFAULTS = dict(
    font=dict(family="Inter, sans-serif", color="#e6edf3"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=20, r=20, t=40, b=20),
)

# Grid styling applied after layout defaults
_GRID_STYLE = dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.06)")


def _apply_dark_axes(fig):
    """Apply dark grid styling to axes."""
    fig.update_xaxes(**_GRID_STYLE)
    fig.update_yaxes(**_GRID_STYLE)
    return fig


def horizontal_bar(labels, values, title="", color="#7c3aed", height=400):
    """Horizontal bar chart."""
    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker_color=color,
        text=[f"{v:,.0f}" for v in values],
        textposition="outside",
        textfont=dict(color="#e6edf3"),
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(color="#FFD700")),
        yaxis=dict(autorange="reversed"),
        height=height,
        **_LAYOUT_DEFAULTS,
    )
    _apply_dark_axes(fig)
    return fig


def donut_chart(labels, values, title="", colors=None, height=400):
    """Donut / pie chart."""
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.45,
        marker=dict(colors=colors or ROYALS_PALETTE[:len(labels)]),
        textinfo="label+percent",
        textfont_size=12,
        textfont_color="#e6edf3",
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(color="#FFD700")),
        height=height,
        showlegend=True,
        legend=dict(orientation="h", y=-0.1, font=dict(color="#8b949e")),
        **_LAYOUT_DEFAULTS,
    )
    return fig


def line_chart(df, x, y, title="", color="#7c3aed", height=350):
    """Simple line chart from a dataframe."""
    fig = px.line(df, x=x, y=y, title=title)
    fig.update_traces(line_color=color, line_width=3)
    fig.update_layout(
        height=height,
        title=dict(font=dict(color="#FFD700")),
        **_LAYOUT_DEFAULTS,
    )
    _apply_dark_axes(fig)
    return fig


def gauge_chart(value, title="", min_val=0, max_val=20, thresholds=None, height=300):
    """
    Gauge chart for per-cap or benchmark comparisons.
    thresholds: list of dicts with 'range' and 'color' keys.
    """
    if thresholds is None:
        thresholds = [
            {"range": [min_val, max_val * 0.5], "color": "#3d1a1a"},
            {"range": [max_val * 0.5, max_val * 0.75], "color": "#3d351a"},
            {"range": [max_val * 0.75, max_val], "color": "#1a3d1a"},
        ]

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title=dict(text=title, font=dict(size=16, color="#e6edf3")),
        number=dict(prefix="$", font=dict(size=28, color="#FFD700")),
        gauge=dict(
            axis=dict(range=[min_val, max_val], tickprefix="$", tickcolor="#8b949e"),
            bar=dict(color="#7c3aed"),
            bgcolor="#161b22",
            steps=[{"range": t["range"], "color": t["color"]} for t in thresholds],
            threshold=dict(
                line=dict(color="#FFD700", width=4),
                thickness=0.8,
                value=value,
            ),
        ),
    ))
    fig.update_layout(height=height, **_LAYOUT_DEFAULTS)
    return fig
