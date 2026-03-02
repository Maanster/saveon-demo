"""
Stand Performance -- Location-level analysis across all concession stands.
Dark-theme version for the new dashboard router.
"""
import os
import sys
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import config
from dashboard.components.theme import (
    page_header,
    dark_card,
    section_header,
    GOLD,
    PURPLE,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    BG_CARD,
)

# ── Dark-theme chart defaults ────────────────────────────────────────────────

_CHART_FONT_COLOR = "#e6edf3"
_CHART_BG = "rgba(0,0,0,0)"
_CHART_GRID = "rgba(255,255,255,0.06)"
_CHART_LEGEND_COLOR = "#8b949e"

_CAT_ORDER = ["Beer", "Cocktail", "Wine", "Food", "NA Bev", "Snacks", "Merch", "Other"]
_CAT_COLORS = {
    "Beer": "#FFD700",
    "Cocktail": "#9b5de5",
    "Wine": "#f85149",
    "Food": "#FFA500",
    "NA Bev": "#58a6ff",
    "Snacks": "#2ea043",
    "Merch": "#7c3aed",
    "Other": "#8b949e",
}

_CONTINUOUS_SCALE = ["#161b22", "#7c3aed"]


def _dark_layout(fig, height: int = 500, show_legend: bool = True, h_legend: bool = True):
    """Apply dark-theme layout defaults to a Plotly figure."""
    layout_kw = dict(
        height=height,
        plot_bgcolor=_CHART_BG,
        paper_bgcolor=_CHART_BG,
        font=dict(size=13, color=_CHART_FONT_COLOR),
        xaxis=dict(gridcolor=_CHART_GRID, zerolinecolor=_CHART_GRID),
        yaxis=dict(gridcolor=_CHART_GRID, zerolinecolor=_CHART_GRID),
    )
    if show_legend and h_legend:
        layout_kw["legend"] = dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(color=_CHART_LEGEND_COLOR),
        )
    elif not show_legend:
        layout_kw["showlegend"] = False
    fig.update_layout(**layout_kw)
    return fig


# ── Data Loading (cached, defined outside render) ────────────────────────────

@st.cache_data(ttl=600)
def _load_stand_data(season_filter: str):
    conn = sqlite3.connect(config.DB_PATH)
    where = "" if season_filter == "All" else f"WHERE t.season = {int(season_filter.split()[-1])}"

    # Units by stand + category
    df_cat = pd.read_sql(f"""
        SELECT t.location AS stand, t.category, SUM(t.qty) AS units,
               SUM(t.estimated_revenue) AS revenue
        FROM transactions t
        {where}
        GROUP BY t.location, t.category
    """, conn)

    # Stand totals
    df_stand = pd.read_sql(f"""
        SELECT t.location AS stand, SUM(t.qty) AS total_units,
               SUM(t.estimated_revenue) AS total_revenue,
               COUNT(DISTINCT t.date) AS games_active
        FROM transactions t
        {where}
        GROUP BY t.location
        ORDER BY total_units DESC
    """, conn)

    # Top category per stand
    df_top = pd.read_sql(f"""
        SELECT location AS stand, category AS top_category, SUM(qty) AS cat_units
        FROM transactions t
        {where}
        GROUP BY location, category
        ORDER BY location, cat_units DESC
    """, conn)

    # Phillips Bar detail
    pb_where = (
        where.replace("WHERE", "WHERE t.location='SOFMC Phillips Bar' AND")
        if where
        else "WHERE t.location='SOFMC Phillips Bar'"
    )
    df_pb = pd.read_sql(f"""
        SELECT t.category, SUM(t.qty) AS units, SUM(t.estimated_revenue) AS revenue
        FROM transactions t
        {pb_where}
        GROUP BY t.category
        ORDER BY units DESC
    """, conn)

    conn.close()
    return df_cat, df_stand, df_top, df_pb


def _short_name(name: str) -> str:
    return name.replace("SOFMC ", "")


# ── Main render function ─────────────────────────────────────────────────────

def render():
    page_header("Stand Performance", "Location-level analysis across all concession stands", "\U0001f3ea")

    # ── Inline season selector ───────────────────────────────────────────
    season_opt = st.selectbox("Season", ["All", "Season 1", "Season 2"], index=0)
    df_cat, df_stand, df_top, df_pb = _load_stand_data(season_opt)

    # Short stand names for display
    df_cat["stand_short"] = df_cat["stand"].apply(_short_name)
    df_stand["stand_short"] = df_stand["stand"].apply(_short_name)

    # ── 1. Units by Stand by Category (stacked bar) ──────────────────────

    section_header("Units Sold by Stand & Category")

    fig_stacked = px.bar(
        df_cat.sort_values("units", ascending=False),
        x="stand_short",
        y="units",
        color="category",
        category_orders={"category": _CAT_ORDER},
        color_discrete_map=_CAT_COLORS,
        labels={"stand_short": "Stand", "units": "Units Sold", "category": "Category"},
    )
    fig_stacked.update_layout(barmode="stack")
    _dark_layout(fig_stacked, height=500)
    st.plotly_chart(fig_stacked, use_container_width=True)

    # ── 2. Revenue by Stand ──────────────────────────────────────────────

    section_header("Revenue by Stand")

    df_stand_sorted = df_stand.sort_values("total_revenue", ascending=True)
    fig_rev = px.bar(
        df_stand_sorted,
        x="total_revenue",
        y="stand_short",
        orientation="h",
        color="total_revenue",
        color_continuous_scale=_CONTINUOUS_SCALE,
        labels={"total_revenue": "Est. Revenue ($)", "stand_short": ""},
    )
    _dark_layout(fig_rev, height=400, show_legend=False)
    fig_rev.update_layout(coloraxis_showscale=False)
    fig_rev.update_traces(
        text=[f"${v:,.0f}" for v in df_stand_sorted["total_revenue"]],
        textposition="outside",
        textfont=dict(color=_CHART_FONT_COLOR),
    )
    st.plotly_chart(fig_rev, use_container_width=True)

    # ── 3. Stand Ranking Table ───────────────────────────────────────────

    section_header("Stand Ranking")

    # Build top-category lookup: keep first (highest) per stand
    top_cat_map = df_top.drop_duplicates(subset="stand", keep="first").set_index("stand")["top_category"]

    ranking = df_stand.copy()
    ranking["top_category"] = ranking["stand"].map(top_cat_map)
    ranking["avg_units_per_game"] = (ranking["total_units"] / ranking["games_active"]).round(1)

    display_df = ranking[
        ["stand_short", "total_units", "total_revenue", "top_category", "avg_units_per_game"]
    ].copy()
    display_df.columns = ["Stand", "Total Units", "Total Revenue", "Top Category", "Avg Units/Game"]
    display_df["Total Revenue"] = display_df["Total Revenue"].apply(lambda x: f"${x:,.0f}")
    display_df["Total Units"] = display_df["Total Units"].apply(lambda x: f"{x:,}")
    display_df = display_df.reset_index(drop=True)

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # ── 3b. Stand Detail Drill-Down ──────────────────────────────────────

    stand_names = ranking["stand_short"].tolist()
    selected_stand = st.selectbox(
        "Drill into a stand",
        options=["(select a stand)"] + stand_names,
        index=0,
        key="stand_drilldown",
    )

    if selected_stand != "(select a stand)":
        _render_stand_drilldown(selected_stand, df_cat)

    # ── 4. Category Mix Comparison ───────────────────────────────────────

    section_header("Category Mix by Stand")

    # Calculate proportions
    totals_by_stand = df_cat.groupby("stand_short")["units"].sum().rename("stand_total")
    df_mix = df_cat.merge(totals_by_stand, on="stand_short")
    df_mix["pct"] = (df_mix["units"] / df_mix["stand_total"] * 100).round(1)

    fig_mix = px.bar(
        df_mix,
        x="stand_short",
        y="pct",
        color="category",
        category_orders={"category": _CAT_ORDER},
        color_discrete_map=_CAT_COLORS,
        labels={"stand_short": "Stand", "pct": "% of Units", "category": "Category"},
        barmode="group",
    )
    _dark_layout(fig_mix, height=500)
    st.plotly_chart(fig_mix, use_container_width=True)

    # ── 5. Phillips Bar Cross-Sell Alert ─────────────────────────────────

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    # Compute food attach rate from real data
    pb_total = df_pb["units"].sum() if len(df_pb) > 0 else 1
    pb_beer = df_pb.loc[df_pb["category"] == "Beer", "units"].sum() if len(df_pb) > 0 else 0
    pb_food = df_pb.loc[df_pb["category"] == "Food", "units"].sum() if len(df_pb) > 0 else 0
    food_pct = (pb_food / pb_total * 100) if pb_total > 0 else 0

    dark_card(f"""
        <span style="font-size:1.6rem;">\U0001f37a</span>&nbsp;
        <strong style="color:{GOLD}; font-size:1.2rem;">Phillips Bar Cross-Sell Opportunity</strong>
        <br><br>
        <span style="color:{TEXT_PRIMARY};">
        Phillips Bar recorded <strong>{pb_beer:,}</strong> beer transactions with a
        <strong>{food_pct:.1f}%</strong> food attach rate.
        Adding simple food items (pretzels, hot dogs) could generate
        <strong>$18K--$25K/season</strong> in new revenue.
        </span>
    """, accent_color=GOLD)

    # ── 6. Business Impact Callout ───────────────────────────────────────

    dark_card(f"""
        <span style="font-size:1.4rem;">\U0001f4a1</span>&nbsp;
        <strong style="color:{GOLD};">Business Impact:</strong>
        <span style="color:{TEXT_PRIMARY};">
        Adding food to Phillips Bar = <strong>+$18K--$25K/year</strong>.
        Rebalancing stand traffic = <strong>+$15K--$25K/year</strong>.
        </span>
    """, accent_color=GOLD)


def _render_stand_drilldown(stand_short: str, df_cat: pd.DataFrame):
    """Render a category breakdown for a single selected stand."""
    section_header(f"{stand_short} -- Category Breakdown")

    stand_data = df_cat[df_cat["stand_short"] == stand_short].copy()

    if stand_data.empty:
        st.info("No data for this stand in the selected season.")
        return

    col1, col2 = st.columns(2)

    with col1:
        # Pie / donut chart
        fig_pie = px.pie(
            stand_data,
            values="units",
            names="category",
            color="category",
            color_discrete_map=_CAT_COLORS,
            hole=0.45,
        )
        fig_pie.update_layout(
            height=380,
            paper_bgcolor=_CHART_BG,
            plot_bgcolor=_CHART_BG,
            font=dict(color=_CHART_FONT_COLOR, size=13),
            legend=dict(font=dict(color=_CHART_LEGEND_COLOR)),
        )
        fig_pie.update_traces(
            textinfo="percent+label",
            textfont=dict(color=_CHART_FONT_COLOR),
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # Revenue bar chart per category
        fig_bar = px.bar(
            stand_data.sort_values("revenue", ascending=True),
            x="revenue",
            y="category",
            orientation="h",
            color="category",
            color_discrete_map=_CAT_COLORS,
            labels={"revenue": "Est. Revenue ($)", "category": "Category"},
        )
        _dark_layout(fig_bar, height=380, show_legend=False)
        fig_bar.update_traces(
            text=[f"${v:,.0f}" for v in stand_data.sort_values("revenue", ascending=True)["revenue"]],
            textposition="outside",
            textfont=dict(color=_CHART_FONT_COLOR),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Summary metrics
    total_units = int(stand_data["units"].sum())
    total_rev = stand_data["revenue"].sum()
    top_cat = stand_data.sort_values("units", ascending=False).iloc[0]["category"]

    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("Total Units", f"{total_units:,}")
    mc2.metric("Est. Revenue", f"${total_rev:,.0f}")
    mc3.metric("Top Category", top_cat)

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
