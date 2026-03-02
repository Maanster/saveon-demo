"""
Stand Performance -- Location-level analysis across all concession stands.
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

st.set_page_config(page_title="Stand Performance", page_icon="\U0001f3ea", layout="wide")

# ── Data Loading ──────────────────────────────────────────────────────────────

@st.cache_data(ttl=600)
def load_stand_data(season_filter: str):
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
    pb_where = where.replace("WHERE", "WHERE t.location='SOFMC Phillips Bar' AND") if where else "WHERE t.location='SOFMC Phillips Bar'"
    df_pb = pd.read_sql(f"""
        SELECT t.category, SUM(t.qty) AS units, SUM(t.estimated_revenue) AS revenue
        FROM transactions t
        {pb_where}
        GROUP BY t.category
        ORDER BY units DESC
    """, conn)

    conn.close()
    return df_cat, df_stand, df_top, df_pb


# ── Sidebar / Filters ────────────────────────────────────────────────────────

st.title("\U0001f3ea Stand Performance")
st.markdown("---")

season_opt = st.selectbox("Season", ["All", "Season 1", "Season 2"], index=0)
df_cat, df_stand, df_top, df_pb = load_stand_data(season_opt)

# Short stand names for display
def short_name(name: str) -> str:
    return name.replace("SOFMC ", "")

df_cat["stand_short"] = df_cat["stand"].apply(short_name)
df_stand["stand_short"] = df_stand["stand"].apply(short_name)

# ── 1. Units by Stand by Category (stacked bar) ──────────────────────────────

st.subheader("Units Sold by Stand & Category")

cat_order = ["Beer", "Cocktail", "Wine", "Food", "NA Bev", "Snacks", "Merch", "Other"]
cat_colors = {
    "Beer": "#FFD700", "Cocktail": "#9C27B0", "Wine": "#C62828",
    "Food": "#FF6F00", "NA Bev": "#1565C0", "Snacks": "#2E7D32",
    "Merch": "#4B0082", "Other": "#757575",
}

fig_stacked = px.bar(
    df_cat.sort_values("units", ascending=False),
    x="stand_short", y="units", color="category",
    category_orders={"category": cat_order},
    color_discrete_map=cat_colors,
    labels={"stand_short": "Stand", "units": "Units Sold", "category": "Category"},
)
fig_stacked.update_layout(
    barmode="stack", height=500,
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font=dict(size=13),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
)
st.plotly_chart(fig_stacked, use_container_width=True)

# ── 2. Revenue by Stand ──────────────────────────────────────────────────────

st.subheader("Revenue by Stand")

fig_rev = px.bar(
    df_stand.sort_values("total_revenue", ascending=True),
    x="total_revenue", y="stand_short", orientation="h",
    color="total_revenue",
    color_continuous_scale=["#ede7f6", "#4B0082"],
    labels={"total_revenue": "Est. Revenue ($)", "stand_short": ""},
)
fig_rev.update_layout(
    height=400, showlegend=False,
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    coloraxis_showscale=False,
)
fig_rev.update_traces(
    text=[f"${v:,.0f}" for v in df_stand.sort_values("total_revenue", ascending=True)["total_revenue"]],
    textposition="outside",
)
st.plotly_chart(fig_rev, use_container_width=True)

# ── 3. Stand Ranking Table ────────────────────────────────────────────────────

st.subheader("Stand Ranking")

# Build top-category lookup: keep first (highest) per stand
top_cat_map = df_top.drop_duplicates(subset="stand", keep="first").set_index("stand")["top_category"]

ranking = df_stand.copy()
ranking["top_category"] = ranking["stand"].map(top_cat_map)
ranking["avg_units_per_game"] = (ranking["total_units"] / ranking["games_active"]).round(1)

display_df = ranking[["stand_short", "total_units", "total_revenue", "top_category", "avg_units_per_game"]].copy()
display_df.columns = ["Stand", "Total Units", "Total Revenue", "Top Category", "Avg Units/Game"]
display_df["Total Revenue"] = display_df["Total Revenue"].apply(lambda x: f"${x:,.0f}")
display_df["Total Units"] = display_df["Total Units"].apply(lambda x: f"{x:,}")
display_df = display_df.reset_index(drop=True)

st.dataframe(display_df, use_container_width=True, hide_index=True)

# ── 4. Category Mix Comparison ────────────────────────────────────────────────

st.subheader("Category Mix by Stand")

# Calculate proportions
totals_by_stand = df_cat.groupby("stand_short")["units"].sum().rename("stand_total")
df_mix = df_cat.merge(totals_by_stand, on="stand_short")
df_mix["pct"] = (df_mix["units"] / df_mix["stand_total"] * 100).round(1)

fig_mix = px.bar(
    df_mix,
    x="stand_short", y="pct", color="category",
    category_orders={"category": cat_order},
    color_discrete_map=cat_colors,
    labels={"stand_short": "Stand", "pct": "% of Units", "category": "Category"},
    barmode="group",
)
fig_mix.update_layout(
    height=500,
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font=dict(size=13),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
)
st.plotly_chart(fig_mix, use_container_width=True)

# ── 5. Phillips Bar Cross-Sell Alert ──────────────────────────────────────────

st.markdown("---")

# Compute food attach rate from real data
pb_total = df_pb["units"].sum() if len(df_pb) > 0 else 1
pb_beer = df_pb.loc[df_pb["category"] == "Beer", "units"].sum() if len(df_pb) > 0 else 0
pb_food = df_pb.loc[df_pb["category"] == "Food", "units"].sum() if len(df_pb) > 0 else 0
food_pct = (pb_food / pb_total * 100) if pb_total > 0 else 0

st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #fffbe6 0%, #fff3e0 100%);
    border: 3px solid #FFD700;
    border-left: 8px solid #FFD700;
    border-radius: 10px;
    padding: 24px 28px;
    margin: 16px 0;
    font-size: 1.15rem;
">
    <span style="font-size:1.6rem;">\U0001f37a</span>&nbsp;
    <strong style="color:#4B0082; font-size:1.2rem;">Phillips Bar Cross-Sell Opportunity</strong>
    <br><br>
    <span style="color:#333;">
    Phillips Bar recorded <strong>{pb_beer:,}</strong> beer transactions with a
    <strong>{food_pct:.1f}%</strong> food attach rate.
    Adding simple food items (pretzels, hot dogs) could generate
    <strong>$18K--$25K/season</strong> in new revenue.
    </span>
</div>
""", unsafe_allow_html=True)

# ── 6. Business Impact Callout ────────────────────────────────────────────────

st.markdown("""
<div style="
    background: linear-gradient(135deg, #fffbe6 0%, #fff8e1 100%);
    border: 2px solid #FFD700;
    border-left: 6px solid #FFD700;
    border-radius: 8px;
    padding: 20px 24px;
    margin: 16px 0;
    font-size: 1.1rem;
">
    <span style="font-size:1.4rem;">\U0001f4a1</span>&nbsp;
    <strong style="color:#4B0082;">Business Impact:</strong>
    <span style="color:#333;">
    Adding food to Phillips Bar = <strong>+$18K--$25K/year</strong>.
    Rebalancing stand traffic = <strong>+$15K--$25K/year</strong>.
    </span>
</div>
""", unsafe_allow_html=True)
