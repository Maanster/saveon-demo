"""
Revenue Estimation page - Estimated revenue tracking, per-cap analysis, and benchmark gaps.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import config

from dashboard.components.charts import ROYALS_PALETTE, _LAYOUT_DEFAULTS
from dashboard.components.kpi_cards import kpi_row, business_impact_callout
from dashboard.components.filters import season_filter

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

@st.cache_data(ttl=300)
def load_transactions():
    conn = sqlite3.connect(config.DB_PATH)
    df = pd.read_sql("SELECT date, category, location, estimated_revenue, season FROM transactions", conn)
    conn.close()
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    return df


@st.cache_data(ttl=300)
def load_games():
    conn = sqlite3.connect(config.DB_PATH)
    df = pd.read_sql(
        "SELECT date, opponent, attendance, season, is_playoff, promo_event, "
        "total_transactions, total_estimated_revenue, revenue_per_cap FROM games",
        conn,
    )
    conn.close()
    df["date"] = pd.to_datetime(df["date"])
    return df


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

st.title("\U0001f4b0 Revenue Estimation")

st.info(
    "**Estimated Revenue methodology:** Prices are assigned using a known price lookup "
    "table (item + variant \u2192 exact price). Where no exact match exists, a category-level "
    "median price is applied. Revenue = price \u00d7 quantity. All figures are pre-tax estimates.",
    icon="\u2139\ufe0f",
)

season = season_filter()

txn = load_transactions()
games = load_games()

# Apply season filter
if season is not None:
    txn = txn[txn["season"] == season]
    games = games[games["season"] == season]

# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------

total_rev = txn["estimated_revenue"].sum()
num_games = len(games)
avg_rev_per_game = total_rev / num_games if num_games else 0
avg_rev_per_cap = games["revenue_per_cap"].mean() if not games.empty else 0
total_txn = len(txn)

# Compute delta vs other season when a single season is selected
delta_rev = None
if season is not None:
    all_txn = load_transactions()
    other = all_txn[all_txn["season"] != season]
    if not other.empty:
        other_rev = other["estimated_revenue"].sum()
        delta_rev = f"{((total_rev - other_rev) / other_rev * 100):+.1f}%" if other_rev else None

kpi_row([
    {"label": "Total Estimated Revenue", "value": f"${total_rev:,.0f}", "delta": delta_rev},
    {"label": "Avg Revenue / Game", "value": f"${avg_rev_per_game:,.0f}"},
    {"label": "Avg Revenue / Cap", "value": f"${avg_rev_per_cap:,.2f}"},
    {"label": "Total Transactions", "value": f"{total_txn:,}"},
])

st.markdown("---")

# ---------------------------------------------------------------------------
# Chart 1 & 2: Revenue trend + Avg transaction value (side by side)
# ---------------------------------------------------------------------------

col_left, col_right = st.columns(2)

# Monthly revenue trend
with col_left:
    monthly = txn.groupby("month", as_index=False)["estimated_revenue"].sum()
    monthly = monthly.sort_values("month")

    fig_trend = px.line(
        monthly, x="month", y="estimated_revenue",
        title="Monthly Estimated Revenue",
        labels={"month": "", "estimated_revenue": "Estimated Revenue ($)"},
    )
    fig_trend.update_traces(line_color="#4B0082", line_width=3, mode="lines+markers")
    fig_trend.update_layout(height=370, **_LAYOUT_DEFAULTS)
    st.plotly_chart(fig_trend, use_container_width=True)

# Average transaction value trend
with col_right:
    monthly_avg = txn.groupby("month", as_index=False).agg(
        total_rev=("estimated_revenue", "sum"),
        count=("estimated_revenue", "size"),
    )
    monthly_avg["avg_txn_value"] = monthly_avg["total_rev"] / monthly_avg["count"]
    monthly_avg = monthly_avg.sort_values("month")

    fig_avg = px.line(
        monthly_avg, x="month", y="avg_txn_value",
        title="Avg Transaction Value Over Time",
        labels={"month": "", "avg_txn_value": "Avg Value ($)"},
    )
    fig_avg.update_traces(line_color="#FFD700", line_width=3, mode="lines+markers")
    fig_avg.update_layout(height=370, **_LAYOUT_DEFAULTS)
    st.plotly_chart(fig_avg, use_container_width=True)

# ---------------------------------------------------------------------------
# Chart 3: Revenue by stand
# ---------------------------------------------------------------------------

stand_rev = (
    txn.groupby("location", as_index=False)["estimated_revenue"]
    .sum()
    .sort_values("estimated_revenue", ascending=True)
)

fig_stand = go.Figure(go.Bar(
    x=stand_rev["estimated_revenue"],
    y=stand_rev["location"],
    orientation="h",
    marker_color="#6A0DAD",
    text=[f"${v:,.0f}" for v in stand_rev["estimated_revenue"]],
    textposition="outside",
))
fig_stand.update_layout(
    title="Estimated Revenue by Stand",
    yaxis=dict(autorange="reversed"),
    height=400,
    **_LAYOUT_DEFAULTS,
)
st.plotly_chart(fig_stand, use_container_width=True)

# ---------------------------------------------------------------------------
# Chart 4: Revenue Per Cap scatter vs attendance
# ---------------------------------------------------------------------------

if not games.empty:
    st.subheader("Revenue Per Cap vs Attendance")

    color_col = "promo_event" if games["promo_event"].nunique() > 1 else "season"
    if color_col == "season":
        games["season_label"] = games["season"].apply(lambda s: f"Season {s}")
        color_col = "season_label"

    fig_scatter = px.scatter(
        games,
        x="attendance",
        y="revenue_per_cap",
        color=color_col,
        hover_data=["date", "opponent"],
        trendline="ols",
        title="Per-Cap Revenue vs Attendance (each dot = one game)",
        labels={"attendance": "Attendance", "revenue_per_cap": "Revenue Per Cap ($)"},
        color_discrete_sequence=ROYALS_PALETTE,
    )

    # WHL benchmark line at $14
    fig_scatter.add_hline(
        y=14, line_dash="dash", line_color="#FFA500", line_width=2,
        annotation_text="WHL Benchmark $14",
        annotation_position="top left",
        annotation_font_color="#FFA500",
    )

    fig_scatter.update_layout(height=450, **_LAYOUT_DEFAULTS)
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------------------------
# Business Impact Callout
# ---------------------------------------------------------------------------

current_per_cap = f"${avg_rev_per_cap:.2f}" if avg_rev_per_cap else "N/A"
business_impact_callout(
    f"Revenue estimation enables tracking the ~$180K per-cap gap closure over time. "
    f"Current per-cap: {current_per_cap} vs WHL benchmark: $14-$16.",
    icon="\U0001f4c8",
)
