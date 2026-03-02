"""
Season KPIs -- The headline page of the Royals Concession Intelligence Platform.
Shows overall performance metrics, per-cap benchmark gap, and key insights.
(Dark-theme router version)
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st
import sqlite3
import pandas as pd
import config
from dashboard.components.kpi_cards import kpi_row, business_impact_callout
from dashboard.components.charts import horizontal_bar, donut_chart, line_chart, gauge_chart, ROYALS_PALETTE
from dashboard.components.filters import season_filter, day_of_week_filter, promo_filter
from dashboard.components.theme import (
    page_header, dark_card, section_header,
    BG_CARD, GOLD, TEXT_PRIMARY, TEXT_SECONDARY, PURPLE, PURPLE_DARK, BORDER_SUBTLE,
)


# ── Cached queries (defined outside render to avoid recreation) ──────────────

@st.cache_data(ttl=300)
def load_season_summary(_season, _db_path):
    """Load aggregate KPIs, optionally filtered by season."""
    conn = sqlite3.connect(_db_path)
    where = f"WHERE t.season = {_season}" if _season else ""
    game_where = f"WHERE season = {_season}" if _season else ""

    tx = pd.read_sql(f"""
        SELECT
            COUNT(*) as total_transactions,
            SUM(estimated_revenue) as total_revenue,
            SUM(qty) as total_units
        FROM transactions t {where}
    """, conn)

    games = pd.read_sql(f"""
        SELECT
            COUNT(*) as total_games,
            AVG(attendance) as avg_attendance,
            SUM(attendance) as total_attendance,
            AVG(revenue_per_cap) as avg_per_cap,
            AVG(units_per_cap) as avg_units_per_cap
        FROM games {game_where}
    """, conn)

    conn.close()
    return tx.iloc[0], games.iloc[0]


@st.cache_data(ttl=300)
def load_season_comparison(_db_path):
    """Load KPIs for season 1 and season 2 separately."""
    conn = sqlite3.connect(_db_path)
    results = {}
    for s in [1, 2]:
        tx = pd.read_sql(f"""
            SELECT COUNT(*) as total_transactions,
                   SUM(estimated_revenue) as total_revenue
            FROM transactions WHERE season = {s}
        """, conn)
        games = pd.read_sql(f"""
            SELECT COUNT(*) as total_games,
                   AVG(attendance) as avg_attendance,
                   AVG(revenue_per_cap) as avg_per_cap
            FROM games WHERE season = {s}
        """, conn)
        results[s] = {**tx.iloc[0].to_dict(), **games.iloc[0].to_dict()}
    conn.close()
    return results


@st.cache_data(ttl=300)
def load_category_breakdown(_season, _db_path):
    conn = sqlite3.connect(_db_path)
    where = f"WHERE season = {_season}" if _season else ""
    df = pd.read_sql(f"""
        SELECT category, SUM(estimated_revenue) as revenue, SUM(qty) as units
        FROM transactions {where}
        GROUP BY category ORDER BY revenue DESC
    """, conn)
    conn.close()
    return df


@st.cache_data(ttl=300)
def load_top_items(_season, _db_path, n=10):
    conn = sqlite3.connect(_db_path)
    where = f"WHERE season = {_season}" if _season else ""
    df = pd.read_sql(f"""
        SELECT item, SUM(qty) as total_qty, SUM(estimated_revenue) as revenue
        FROM transactions {where}
        GROUP BY item ORDER BY total_qty DESC LIMIT {n}
    """, conn)
    conn.close()
    return df


@st.cache_data(ttl=300)
def load_monthly_trend(_season, _db_path):
    conn = sqlite3.connect(_db_path)
    where = f"WHERE season = {_season}" if _season else ""
    df = pd.read_sql(f"""
        SELECT strftime('%Y-%m', date) as month,
               SUM(estimated_revenue) as revenue,
               COUNT(*) as transactions
        FROM transactions {where}
        GROUP BY month ORDER BY month
    """, conn)
    conn.close()
    return df


@st.cache_data(ttl=300)
def load_dollar_dog_stats(_db_path):
    """Stats for $1 Dog Night (2025-10-22)."""
    conn = sqlite3.connect(_db_path)
    dog_night = pd.read_sql("""
        SELECT SUM(qty) as dog_qty
        FROM transactions
        WHERE date = '2025-10-22' AND item LIKE '%Hot Dog%'
    """, conn)
    total_night = pd.read_sql("""
        SELECT COUNT(*) as total_tx FROM transactions WHERE date = '2025-10-22'
    """, conn)
    conn.close()
    return dog_night.iloc[0]["dog_qty"], total_night.iloc[0]["total_tx"]


# ── Render ───────────────────────────────────────────────────────────────────

def render():
    page_header("Season KPIs", "Revenue benchmarks and per-cap analysis", "\U0001f4ca")

    # ── DB connection ────────────────────────────────────────────────────────
    if not os.path.exists(config.DB_PATH):
        st.error("Database not found. Run the data pipeline first: `python data_foundation/build_all.py`")
        st.stop()

    db_path = config.DB_PATH

    # ── Inline filters ───────────────────────────────────────────────────────
    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        selected_season = season_filter(inline=True)
    with fcol2:
        selected_dow = day_of_week_filter(inline=True)
    with fcol3:
        selected_promo = promo_filter(inline=True)

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    # ── Load data ────────────────────────────────────────────────────────────
    tx_stats, game_stats = load_season_summary(selected_season, db_path)

    total_rev = tx_stats["total_revenue"] or 0
    total_tx = int(tx_stats["total_transactions"] or 0)
    avg_att = game_stats["avg_attendance"] or 0
    avg_per_cap = game_stats["avg_per_cap"] or 0
    total_games = int(game_stats["total_games"] or 0)

    # ── Season comparison deltas ─────────────────────────────────────────────
    comp = load_season_comparison(db_path)
    s1, s2 = comp.get(1, {}), comp.get(2, {})

    def fmt_delta(s2_val, s1_val, prefix="", suffix="", as_pct=False):
        if s1_val and s2_val:
            if as_pct:
                diff = ((s2_val - s1_val) / s1_val) * 100
                return f"{diff:+.1f}%"
            diff = s2_val - s1_val
            return f"{prefix}{diff:+,.0f}{suffix}"
        return None

    # ── TOP ROW: 5 KPI Cards ────────────────────────────────────────────────
    section_header("Overall Performance")

    kpi_row([
        {
            "label": "Total Est. Revenue",
            "value": f"${total_rev:,.0f}",
            "delta": fmt_delta(s2.get("total_revenue"), s1.get("total_revenue"), "$") if not selected_season else None,
        },
        {
            "label": "Total Transactions",
            "value": f"{total_tx:,}",
            "delta": fmt_delta(s2.get("total_transactions"), s1.get("total_transactions")) if not selected_season else None,
        },
        {
            "label": "Avg Attendance",
            "value": f"{avg_att:,.0f}",
            "delta": fmt_delta(s2.get("avg_attendance"), s1.get("avg_attendance")) if not selected_season else None,
        },
        {
            "label": "Avg Per-Cap Revenue",
            "value": f"${avg_per_cap:,.2f}",
            "delta": fmt_delta(s2.get("avg_per_cap"), s1.get("avg_per_cap"), "$", as_pct=False) if not selected_season else None,
        },
        {
            "label": "Total Games",
            "value": f"{total_games}",
        },
    ])

    # ── HERO: Per-Cap Benchmark Gap ──────────────────────────────────────────
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    section_header("Per-Cap Benchmark Analysis")

    WHL_BENCHMARK_LOW = 14.00
    WHL_BENCHMARK_HIGH = 16.00
    current_per_cap = avg_per_cap if avg_per_cap else 11.77

    gap_low = WHL_BENCHMARK_LOW - current_per_cap
    gap_high = WHL_BENCHMARK_HIGH - current_per_cap
    total_attendance = game_stats["total_attendance"] or (avg_att * total_games)

    annual_opp_low = gap_low * total_attendance if gap_low > 0 else 0
    annual_opp_high = gap_high * total_attendance if gap_high > 0 else 0

    # Per-cap hero visual
    hero_left, hero_right = st.columns([3, 2])

    with hero_left:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {PURPLE} 0%, {PURPLE_DARK} 100%);
            border-radius: 16px;
            padding: 32px 40px;
            color: white;
            margin-bottom: 16px;
            border: 1px solid {BORDER_SUBTLE};
        ">
            <div style="font-size: 0.95rem; text-transform: uppercase; letter-spacing: 2px; color: {GOLD}; margin-bottom: 8px;">
                Revenue Per Fan Per Game
            </div>
            <div style="display: flex; align-items: baseline; gap: 16px; margin-bottom: 20px;">
                <span style="font-size: 3.5rem; font-weight: 800; color: {GOLD};">${current_per_cap:.2f}</span>
                <span style="font-size: 1.1rem; color: {TEXT_SECONDARY};">current per-cap</span>
            </div>
            <div style="
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
                padding: 16px 20px;
                margin-bottom: 16px;
            ">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="color: {TEXT_PRIMARY};">Current</span>
                    <span style="color: {TEXT_PRIMARY};">WHL Benchmark: $14 - $16</span>
                </div>
                <div style="background: rgba(255,255,255,0.15); border-radius: 8px; height: 28px; position: relative; overflow: hidden;">
                    <div style="
                        background: linear-gradient(90deg, {GOLD}, #FFA500);
                        height: 100%; width: {min(current_per_cap / WHL_BENCHMARK_HIGH * 100, 100):.0f}%;
                        border-radius: 8px;
                    "></div>
                    <div style="
                        position: absolute; top: 0; left: {WHL_BENCHMARK_LOW / WHL_BENCHMARK_HIGH * 100:.0f}%;
                        height: 100%; width: 2px; background: #00ff88;
                    "></div>
                </div>
            </div>
            <div style="display: flex; gap: 32px;">
                <div>
                    <div style="color: {GOLD}; font-size: 0.8rem; text-transform: uppercase;">Gap to Benchmark</div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: {TEXT_PRIMARY};">${gap_low:.2f} - ${gap_high:.2f}</div>
                </div>
                <div>
                    <div style="color: {GOLD}; font-size: 0.8rem; text-transform: uppercase;">Annual Opportunity</div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: {TEXT_PRIMARY};">${annual_opp_low:,.0f} - ${annual_opp_high:,.0f}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with hero_right:
        fig_gauge = gauge_chart(
            value=current_per_cap,
            title="Per-Cap vs WHL Range",
            min_val=0,
            max_val=20,
            thresholds=[
                {"range": [0, 10], "color": "#3d1a1a"},
                {"range": [10, 14], "color": "#3d351a"},
                {"range": [14, 16], "color": "#1a3d1a"},
                {"range": [16, 20], "color": "#1a3d2a"},
            ],
            height=320,
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    # Business impact callout
    mid_target = (WHL_BENCHMARK_LOW + WHL_BENCHMARK_HIGH) / 2
    mid_opp = (mid_target - current_per_cap) * total_attendance if mid_target > current_per_cap else 0
    business_impact_callout(
        f"Closing the per-cap gap to ${mid_target:.2f} = <strong>+${mid_opp:,.0f}/year</strong> in additional revenue. "
        f"Every $1 increase in per-cap spending adds ~${total_attendance:,.0f} to the top line."
    )

    # ── Category Breakdown ───────────────────────────────────────────────────
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    section_header("Category Breakdown")

    cat_df = load_category_breakdown(selected_season, db_path)

    if not cat_df.empty:
        col_donut, col_table = st.columns([1, 1])

        with col_donut:
            fig_donut = donut_chart(
                labels=cat_df["category"].tolist(),
                values=cat_df["revenue"].tolist(),
                title="Revenue by Category",
                height=400,
            )
            st.plotly_chart(fig_donut, use_container_width=True)

        with col_table:
            display_df = cat_df.copy()
            display_df["revenue"] = display_df["revenue"].apply(lambda x: f"${x:,.0f}")
            display_df["units"] = display_df["units"].apply(lambda x: f"{x:,.0f}")
            display_df.columns = ["Category", "Revenue", "Units"]
            st.dataframe(display_df, use_container_width=True, hide_index=True)

    # ── Top 10 Items ─────────────────────────────────────────────────────────
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    section_header("Top 10 Items by Volume")

    top_items = load_top_items(selected_season, db_path)

    if not top_items.empty:
        fig_bar = horizontal_bar(
            labels=top_items["item"].tolist()[::-1],
            values=top_items["total_qty"].tolist()[::-1],
            title="",
            color=PURPLE,
            height=400,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── Monthly Revenue Trend ────────────────────────────────────────────────
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    section_header("Monthly Revenue Trend")

    monthly = load_monthly_trend(selected_season, db_path)

    if not monthly.empty:
        fig_line = line_chart(monthly, x="month", y="revenue", title="", color=PURPLE, height=350)
        st.plotly_chart(fig_line, use_container_width=True)

    # ── Dollar Dog Night Callout ─────────────────────────────────────────────
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    section_header("Promotion Spotlight: $1 Dog Night")

    try:
        dog_qty, total_dog_night_tx = load_dollar_dog_stats(db_path)
        dog_qty = int(dog_qty) if dog_qty else 0
        total_dog_night_tx = int(total_dog_night_tx) if total_dog_night_tx else 0
        dog_pct = (dog_qty / total_dog_night_tx * 100) if total_dog_night_tx > 0 else 0

        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {BG_CARD} 0%, #2a1f0a 100%);
            border: 2px solid {GOLD};
            border-radius: 12px;
            padding: 24px 32px;
            margin: 8px 0;
        ">
            <div style="display: flex; gap: 48px; align-items: center;">
                <div>
                    <span style="font-size: 2.5rem;">\U0001f32d</span>
                </div>
                <div>
                    <div style="font-size: 2rem; font-weight: 800; color: {GOLD};">{dog_qty:,} hot dog transactions</div>
                    <div style="font-size: 1.1rem; color: {TEXT_SECONDARY}; margin-top: 4px;">
                        {dog_pct:.0f}% of all sales that night. Proof that data-driven promotions work.
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        st.info("$1 Dog Night data will be available after the data pipeline runs.")

    # ── Final Impact ─────────────────────────────────────────────────────────
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    business_impact_callout(
        f"Closing the per-cap gap to $14.50 = <strong>+${(14.50 - current_per_cap) * total_attendance:,.0f}/year</strong> "
        "in additional revenue. Targeted promotions, optimized stand hours, and menu engineering "
        "are the three levers to get there."
    )
