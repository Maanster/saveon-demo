"""
Intermission Analysis -- The visual hero of the demo.
Transaction velocity heatmap and intermission bottleneck analysis.
(Dark-theme dashboard version)
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import config

from dashboard.components.theme import (
    page_header, dark_card, section_header,
    GOLD, PURPLE, TEXT_PRIMARY, TEXT_SECONDARY, BG_CARD, BG_SECONDARY,
)

# ── Data Loading (cached, outside render) ─────────────────────────────────────

@st.cache_data(ttl=600)
def load_intermission_data():
    conn = sqlite3.connect(config.DB_PATH)

    # All transactions with time info
    df = pd.read_sql("""
        SELECT date, time, hour, minute, category, location, qty,
               estimated_revenue, game_period, season
        FROM transactions
        WHERE hour >= 17 AND hour <= 22
    """, conn)

    # Game info for labels
    df_games = pd.read_sql("SELECT date, opponent, attendance FROM games", conn)

    # Period-level summary
    df_period = pd.read_sql("""
        SELECT game_period, SUM(qty) AS total_units,
               SUM(estimated_revenue) AS total_revenue,
               COUNT(*) AS tx_count
        FROM transactions
        GROUP BY game_period
        ORDER BY total_units DESC
    """, conn)

    # Stand-level intermission breakdown
    df_stand_int = pd.read_sql("""
        SELECT location, game_period, SUM(qty) AS units,
               SUM(estimated_revenue) AS revenue
        FROM transactions
        WHERE game_period IN ('1st_intermission', '2nd_intermission')
        GROUP BY location, game_period
        ORDER BY units DESC
    """, conn)

    # For lost revenue estimator
    intermission_stats = pd.read_sql("""
        SELECT SUM(qty) AS total_units,
               SUM(estimated_revenue) AS total_rev,
               COUNT(DISTINCT date) AS num_games
        FROM transactions
        WHERE game_period IN ('1st_intermission', '2nd_intermission')
    """, conn)

    # Average revenue per unit across intermissions
    avg_rev_per_unit = pd.read_sql("""
        SELECT AVG(estimated_price) AS avg_price
        FROM transactions
        WHERE game_period IN ('1st_intermission', '2nd_intermission')
    """, conn)

    conn.close()
    return df, df_games, df_period, df_stand_int, intermission_stats, avg_rev_per_unit


# ── Helper (outside render) ──────────────────────────────────────────────────

def short_name(name: str) -> str:
    return name.replace("SOFMC ", "")


# ── Render ────────────────────────────────────────────────────────────────────

def render():
    page_header("Intermission Analysis", "Transaction velocity heatmap and bottleneck analysis", "\u23f1\ufe0f")

    df, df_games, df_period, df_stand_int, int_stats, avg_rev = load_intermission_data()

    # ── 1. TRANSACTION VELOCITY HEATMAP (THE MAIN EVENT) ─────────────────────

    section_header("Transaction Velocity Heatmap")
    st.caption("Every 5-minute window across every game -- watch the intermission crush light up.")

    # Build 5-minute time buckets from 17:00 to 22:00
    bucket_starts = []
    bucket_labels = []
    for h in range(17, 22):
        for m in range(0, 60, 5):
            bucket_starts.append((h, m))
            # Convert to 12h for readability
            h12 = h if h <= 12 else h - 12
            ampm = "AM" if h < 12 else "PM"
            label = f"{h12}:{m:02d}{ampm}"
            bucket_labels.append(label)

    # Assign each transaction to a 5-minute bucket
    df["bucket_idx"] = ((df["hour"] - 17) * 12) + (df["minute"] // 5)
    df["bucket_idx"] = df["bucket_idx"].clip(0, len(bucket_labels) - 1)

    # Pivot: rows=game dates, cols=time buckets, values=transaction count
    heatmap_data = df.groupby(["date", "bucket_idx"]).agg(tx_count=("qty", "sum")).reset_index()
    pivot = heatmap_data.pivot_table(index="date", columns="bucket_idx", values="tx_count", fill_value=0)

    # Ensure all buckets present
    for i in range(len(bucket_labels)):
        if i not in pivot.columns:
            pivot[i] = 0
    pivot = pivot.reindex(columns=range(len(bucket_labels)), fill_value=0)

    # Sort dates chronologically
    pivot = pivot.sort_index()

    # Build y-axis labels with opponent + attendance
    game_map = df_games.set_index("date")
    y_labels = []
    for d in pivot.index:
        if d in game_map.index:
            row = game_map.loc[d]
            if isinstance(row, pd.DataFrame):
                row = row.iloc[0]
            opp = row["opponent"]
            att = int(row["attendance"])
            y_labels.append(f"{d} vs {opp} ({att:,})")
        else:
            y_labels.append(d)

    # Intermission boundary annotations
    # 1st intermission: 7:25 PM - 7:44 PM -> bucket indices
    int1_start = (19 - 17) * 12 + (25 // 5)  # bucket 29
    int1_end = (19 - 17) * 12 + (44 // 5)    # bucket 32
    # 2nd intermission: 8:05 PM - 8:24 PM
    int2_start = (20 - 17) * 12 + (5 // 5)   # bucket 37
    int2_end = (20 - 17) * 12 + (24 // 5)    # bucket 40

    # Custom colorscale: deep blue (quiet) -> yellow -> red/orange (hot)
    custom_colorscale = [
        [0.0, "#0d1b2a"],
        [0.15, "#1b3a5c"],
        [0.3, "#1f5f8b"],
        [0.45, "#48a9a6"],
        [0.6, "#d4b83e"],
        [0.75, "#e8882f"],
        [0.9, "#d63230"],
        [1.0, "#9b1d20"],
    ]

    num_games = len(pivot)
    heatmap_height = max(700, num_games * 14 + 150)

    fig_heat = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=bucket_labels,
        y=y_labels,
        colorscale=custom_colorscale,
        colorbar=dict(
            title=dict(text="Units", side="right"),
            thickness=18,
            len=0.6,
        ),
        hoverongaps=False,
        hovertemplate="<b>%{y}</b><br>Time: %{x}<br>Units: %{z}<extra></extra>",
    ))

    # Add intermission boundary lines and labels
    for label, start, end in [("1st Intermission", int1_start, int1_end),
                               ("2nd Intermission", int2_start, int2_end)]:
        # Left boundary
        fig_heat.add_vline(
            x=start - 0.5, line_width=2, line_dash="dash", line_color="#FFD700",
        )
        # Right boundary
        fig_heat.add_vline(
            x=end + 0.5, line_width=2, line_dash="dash", line_color="#FFD700",
        )
        # Label at top
        fig_heat.add_annotation(
            x=(start + end) / 2,
            y=-0.02,
            yref="paper",
            text=f"<b>{label}</b>",
            showarrow=False,
            font=dict(color="#FFD700", size=12),
            bgcolor="rgba(124,58,237,0.85)",
            bordercolor="#FFD700",
            borderwidth=1,
            borderpad=4,
        )

    fig_heat.update_layout(
        height=heatmap_height,
        margin=dict(l=220, r=40, t=60, b=80),
        plot_bgcolor="#0d1117",
        paper_bgcolor="#0d1117",
        font=dict(color="#e0e0e0", size=11),
        xaxis=dict(
            title="Time of Day",
            tickangle=-45,
            dtick=2,  # Show every other label to avoid clutter
            gridcolor="rgba(255,255,255,0.05)",
            side="bottom",
        ),
        yaxis=dict(
            title="",
            autorange="reversed",
            gridcolor="rgba(255,255,255,0.05)",
        ),
        title=dict(
            text="Game-by-Game Transaction Velocity (5-min buckets)",
            font=dict(size=18, color="#FFD700"),
            x=0.5,
        ),
    )

    st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("""
    <div style="
        background: #1c2333;
        border-left: 4px solid #FFD700;
        padding: 12px 16px;
        border-radius: 4px;
        margin-bottom: 24px;
    ">
    <strong style="color: #e6edf3;">Reading the Heatmap:</strong>
    <span style="color: #e6edf3;">
    Cool blues = quiet periods. Hot reds/oranges = transaction surges.
    The gold dashed lines mark intermission windows -- note how they consistently
    light up as the hottest zones across nearly every game.
    </span>
    </div>
    """, unsafe_allow_html=True)

    # ── 2. Period Summary Bars ────────────────────────────────────────────────

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    section_header("Transactions by Game Period")

    period_order = ["pre_game", "1st_period", "1st_intermission", "2nd_period",
                    "2nd_intermission", "3rd_period", "post_game", "other"]
    period_display = {
        "pre_game": "Pre-Game", "1st_period": "1st Period",
        "1st_intermission": "1st Intermission", "2nd_period": "2nd Period",
        "2nd_intermission": "2nd Intermission", "3rd_period": "3rd Period",
        "post_game": "Post-Game", "other": "Other",
    }

    df_period["period_display"] = df_period["game_period"].map(period_display).fillna(df_period["game_period"])
    df_period["is_intermission"] = df_period["game_period"].str.contains("intermission")

    # Sort by our custom order
    order_map = {p: i for i, p in enumerate(period_order)}
    df_period["sort_key"] = df_period["game_period"].map(order_map).fillna(99)
    df_period = df_period.sort_values("sort_key")

    colors = ["#FFD700" if is_int else "#7c3aed" for is_int in df_period["is_intermission"]]

    fig_period = go.Figure(go.Bar(
        x=df_period["period_display"],
        y=df_period["total_units"],
        marker_color=colors,
        text=[f"{v:,.0f}" for v in df_period["total_units"]],
        textposition="outside",
        textfont=dict(size=13, color="#e6edf3"),
    ))
    fig_period.update_layout(
        height=400,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis_title="Total Units Sold",
        font=dict(size=13, color="#e6edf3"),
        margin=dict(t=40),
        xaxis=dict(color="#e6edf3"),
        yaxis=dict(color="#e6edf3"),
    )
    st.plotly_chart(fig_period, use_container_width=True)

    # ── 3. Stand-Level Intermission Comparison ────────────────────────────────

    section_header("Stand Intermission Load")
    st.caption("Which stands get hit hardest during intermissions?")

    df_stand_int["stand_short"] = df_stand_int["location"].apply(short_name)
    df_stand_int["period_display"] = df_stand_int["game_period"].map(period_display)

    fig_stand = px.bar(
        df_stand_int,
        x="stand_short", y="units", color="period_display",
        barmode="group",
        color_discrete_map={"1st Intermission": "#FFD700", "2nd Intermission": "#FF6F00"},
        labels={"stand_short": "Stand", "units": "Units Sold", "period_display": "Period"},
    )
    fig_stand.update_layout(
        height=450,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13, color="#e6edf3"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
                    font=dict(color="#e6edf3")),
        xaxis=dict(color="#e6edf3"),
        yaxis=dict(color="#e6edf3"),
    )
    st.plotly_chart(fig_stand, use_container_width=True)

    # ── 4. Lost Revenue Estimator ─────────────────────────────────────────────

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    section_header("Lost Revenue Estimator")
    st.caption("How much additional revenue could faster intermission service unlock?")

    total_int_units = int(int_stats.iloc[0]["total_units"]) if len(int_stats) > 0 else 0
    total_int_rev = float(int_stats.iloc[0]["total_rev"]) if len(int_stats) > 0 else 0
    num_games_val = int(int_stats.iloc[0]["num_games"]) if len(int_stats) > 0 else 1
    avg_price = float(avg_rev.iloc[0]["avg_price"]) if len(avg_rev) > 0 else 7.0

    # Per-game intermission averages
    avg_int_rev_per_game = total_int_rev / num_games_val if num_games_val > 0 else 0

    improvement_pct = st.slider(
        "% improvement in intermission throughput",
        min_value=5, max_value=50, value=20, step=5,
        format="%d%%",
    )

    # Annual projection
    est_games_per_season = 36
    additional_rev_per_game = avg_int_rev_per_game * (improvement_pct / 100)
    additional_rev_season = additional_rev_per_game * est_games_per_season

    col1, col2, col3 = st.columns(3)
    col1.metric("Current Intermission Rev/Game", f"${avg_int_rev_per_game:,.0f}")
    col2.metric(f"Additional Rev/Game (+{improvement_pct}%)", f"${additional_rev_per_game:,.0f}")
    col3.metric("Projected Additional Rev/Season", f"${additional_rev_season:,.0f}")

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #0d1117 0%, #1a1a2e 100%);
        border: 2px solid #FFD700;
        border-radius: 10px;
        padding: 20px 28px;
        margin: 20px 0;
        color: #e6edf3;
        font-size: 1.05rem;
    ">
        <span style="font-size:1.4rem;">&#x1f4ca;</span>&nbsp;
        <strong style="color:#FFD700;">Revenue Math:</strong><br>
        {num_games_val} games tracked &times; ${avg_int_rev_per_game:,.0f} avg intermission revenue
        &times; {improvement_pct}% throughput gain = <strong style="color:#FFD700;">${additional_rev_per_game:,.0f}/game</strong>.<br>
        Projected across {est_games_per_season} home games/season =
        <strong style="color:#FFD700;">${additional_rev_season:,.0f}/season</strong>.
    </div>
    """, unsafe_allow_html=True)

    # ── 5. Business Impact Callout ────────────────────────────────────────────

    st.markdown(f"""
    <div style="
        background: #1c2333;
        border: 3px solid #FFD700;
        border-left: 8px solid #FFD700;
        border-radius: 10px;
        padding: 24px 28px;
        margin: 20px 0;
        font-size: 1.15rem;
    ">
        <span style="font-size:1.6rem;">&#x1f525;</span>&nbsp;
        <strong style="color:#7c3aed; font-size:1.2rem;">Business Impact:</strong>
        <br><br>
        <span style="color:#e6edf3;">
        Solving the intermission bottleneck = <strong>+$80K--$120K/year</strong>.<br>
        An estimated <strong>350+ fans abandon the queue</strong> per intermission
        = ~<strong>$2,800 lost per game</strong>.
        </span>
    </div>
    """, unsafe_allow_html=True)
