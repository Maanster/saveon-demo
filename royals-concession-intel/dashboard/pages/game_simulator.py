"""
Live Game Simulator
====================
Animated game-night simulation that distributes ML-predicted demand across
periods, stands, and categories with a live clock, stand cards, and charts.
Dark-theme router version.
"""
import sys, os, time, math, sqlite3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import config

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from dashboard.components.theme import (
    page_header, section_header, BG_CARD, BG_SECONDARY, GOLD, PURPLE,
    TEXT_PRIMARY, TEXT_SECONDARY, BORDER_SUBTLE,
)
from dashboard.components.charts import ROYALS_PALETTE, _LAYOUT_DEFAULTS
from dashboard.components.simulator import (
    distribute_demand_by_period,
    generate_transaction_stream,
    distribute_to_stands,
    format_game_clock,
    PERIOD_ORDER,
    PERIOD_DISPLAY,
    PERIOD_DURATION,
    PERIOD_START_TIME,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
AVG_PRICE = 7.50  # average price per unit across all categories

CATEGORY_COLORS = {
    "Beer": "#FFD700",
    "Cocktail": "#7c3aed",
    "Wine": "#9b5de5",
    "NA Bev": "#2ea043",
    "Food": "#FFA500",
    "Snacks": "#FFB347",
    "Merch": "#b794f6",
    "Other": "#8b949e",
}

# Short names for stands
def _short(name):
    return name.replace("SOFMC ", "")


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300)
def _get_opponents():
    try:
        conn = sqlite3.connect(config.DB_PATH)
        df = pd.read_sql("SELECT DISTINCT opponent FROM games ORDER BY opponent", conn)
        conn.close()
        return df["opponent"].tolist()
    except Exception:
        return sorted(set(g["team"] for g in config.ALL_GAMES))


# ---------------------------------------------------------------------------
# HTML builders
# ---------------------------------------------------------------------------
def _clock_html(period_display_name, time_str, period_key):
    """Build the large game clock HTML block."""
    # Color the period name based on type
    if "intermission" in period_key:
        period_color = GOLD
    elif period_key == "pre_game":
        period_color = TEXT_SECONDARY
    elif period_key == "post_game":
        period_color = TEXT_SECONDARY
    else:
        period_color = "#e6edf3"

    return f"""
    <div style="background:{BG_CARD}; border:2px solid {GOLD}; border-radius:12px;
                padding:20px; text-align:center; margin-bottom:16px;">
        <div style="color:{period_color}; font-size:0.85rem; text-transform:uppercase;
                    letter-spacing:2px; font-weight:700;">
            {period_display_name}
        </div>
        <div style="color:{GOLD}; font-size:3rem; font-weight:800; font-family:monospace;
                    line-height:1.2;">
            {time_str}
        </div>
    </div>
    """


def _stand_card_html(name, total_units, revenue, by_category, is_active=False):
    """Build a single stand card with category mini-bars."""
    short = _short(name)
    pulse_class = "pulse" if is_active else ""

    # Category mini-bars
    cat_bars = ""
    if by_category:
        max_val = max(by_category.values()) if by_category.values() else 1
        for cat, units in sorted(by_category.items(), key=lambda x: -x[1]):
            if units <= 0:
                continue
            pct = min(100, int((units / max(1, max_val)) * 100))
            color = CATEGORY_COLORS.get(cat, "#8b949e")
            cat_bars += f"""
            <div style="display:flex; align-items:center; gap:6px; margin:2px 0;">
                <span style="color:{TEXT_SECONDARY}; font-size:0.65rem; width:50px;
                             text-align:right; flex-shrink:0;">{cat}</span>
                <div style="flex:1; background:rgba(255,255,255,0.06); border-radius:3px;
                            height:8px; overflow:hidden;">
                    <div style="width:{pct}%; height:100%; background:{color};
                                border-radius:3px;"></div>
                </div>
                <span style="color:{TEXT_SECONDARY}; font-size:0.65rem; width:30px;">{units}</span>
            </div>
            """

    active_border = f"border:1px solid {GOLD};" if is_active else f"border:1px solid {BORDER_SUBTLE};"

    return f"""
    <div class="{pulse_class}" style="background:{BG_CARD}; {active_border}
                border-radius:10px; padding:14px 16px;">
        <div style="display:flex; justify-content:space-between; align-items:center;
                    margin-bottom:8px;">
            <span style="color:{TEXT_PRIMARY}; font-weight:700; font-size:0.9rem;">
                {short}
            </span>
            <span style="color:{GOLD}; font-size:0.75rem; font-weight:600;">
                {'ACTIVE' if is_active else ''}
            </span>
        </div>
        <div style="display:flex; gap:16px; margin-bottom:8px;">
            <div>
                <div style="color:{TEXT_SECONDARY}; font-size:0.7rem; text-transform:uppercase;">Units</div>
                <div style="color:{TEXT_PRIMARY}; font-size:1.1rem; font-weight:700;">{total_units:,}</div>
            </div>
            <div>
                <div style="color:{TEXT_SECONDARY}; font-size:0.7rem; text-transform:uppercase;">Revenue</div>
                <div style="color:{GOLD}; font-size:1.1rem; font-weight:700;">${revenue:,.0f}</div>
            </div>
        </div>
        {cat_bars}
    </div>
    """


def _stand_grid_html(stand_totals, active_stands=None):
    """Build a 2x3 (or smaller) grid of stand cards."""
    if active_stands is None:
        active_stands = set()
    stands = list(stand_totals.keys())
    cards_html = ""
    for stand in stands:
        data = stand_totals[stand]
        card = _stand_card_html(
            stand,
            data["total"],
            data["revenue"],
            data.get("by_category", {}),
            is_active=(stand in active_stands),
        )
        cards_html += f'<div style="flex:1 1 calc(33% - 8px); min-width:200px;">{card}</div>'

    return f"""
    <div style="display:flex; flex-wrap:wrap; gap:10px; margin-bottom:16px;">
        {cards_html}
    </div>
    """


def _summary_table_html(summaries):
    """Build an HTML table for period summaries."""
    if not summaries:
        return ""
    header = """
    <tr>
        <th style="text-align:left; padding:8px 12px; color:{gold}; border-bottom:1px solid {border};">Period</th>
        <th style="text-align:right; padding:8px 12px; color:{gold}; border-bottom:1px solid {border};">Units</th>
        <th style="text-align:right; padding:8px 12px; color:{gold}; border-bottom:1px solid {border};">Revenue</th>
        <th style="text-align:right; padding:8px 12px; color:{gold}; border-bottom:1px solid {border};">Cumulative</th>
    </tr>
    """.format(gold=GOLD, border=BORDER_SUBTLE)

    rows = ""
    for s in summaries:
        rows += f"""
        <tr>
            <td style="padding:6px 12px; color:{TEXT_PRIMARY};">{s['period']}</td>
            <td style="padding:6px 12px; color:{TEXT_PRIMARY}; text-align:right;">{s['units']:,}</td>
            <td style="padding:6px 12px; color:{GOLD}; text-align:right;">${s['revenue']:,.0f}</td>
            <td style="padding:6px 12px; color:{TEXT_SECONDARY}; text-align:right;">${s['cumulative_revenue']:,.0f}</td>
        </tr>
        """

    return f"""
    <div style="background:{BG_CARD}; border:1px solid {BORDER_SUBTLE}; border-radius:10px;
                overflow:hidden; margin-top:12px;">
        <table style="width:100%; border-collapse:collapse; font-size:0.85rem;">
            {header}
            {rows}
        </table>
    </div>
    """


# ---------------------------------------------------------------------------
# Chart builders
# ---------------------------------------------------------------------------
def _cumulative_revenue_chart(revenue_points, tick_labels):
    """Build a plotly line chart for cumulative revenue over simulation ticks."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(revenue_points))),
        y=revenue_points,
        mode="lines",
        line=dict(color=GOLD, width=3),
        fill="tozeroy",
        fillcolor="rgba(255,215,0,0.08)",
        name="Cumulative Revenue",
    ))
    fig.update_layout(
        title=dict(text="Cumulative Revenue", font=dict(color=GOLD, size=14)),
        xaxis=dict(
            title="",
            showticklabels=True,
            tickvals=list(range(0, len(tick_labels), max(1, len(tick_labels) // 8))),
            ticktext=[tick_labels[i] for i in range(0, len(tick_labels), max(1, len(tick_labels) // 8))],
        ),
        yaxis=dict(title="Revenue ($)", tickprefix="$"),
        height=300,
        **_LAYOUT_DEFAULTS,
    )
    return fig


def _category_bar_chart(category_totals):
    """Build a plotly bar chart for current category totals."""
    cats = list(category_totals.keys())
    vals = list(category_totals.values())
    colors = [CATEGORY_COLORS.get(c, "#8b949e") for c in cats]

    fig = go.Figure(go.Bar(
        x=cats,
        y=vals,
        marker_color=colors,
        text=[f"{v:,}" for v in vals],
        textposition="outside",
        textfont=dict(color=TEXT_PRIMARY, size=11),
    ))
    fig.update_layout(
        title=dict(text="Units by Category", font=dict(color=GOLD, size=14)),
        xaxis=dict(title=""),
        yaxis=dict(title="Units"),
        height=300,
        **_LAYOUT_DEFAULTS,
    )
    return fig


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------
def render():
    page_header(
        "Live Game Simulator",
        "Animated simulation of predicted concession demand across a full game night",
        "🏒",
    )

    # --- Input row 1 ---
    opponents = _get_opponents()
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        opponent = st.selectbox(
            "Opponent",
            opponents,
            index=opponents.index("Vancouver") if "Vancouver" in opponents else 0,
            key="sim_opponent",
        )
    with col2:
        day_of_week = st.selectbox(
            "Day of Week",
            days,
            index=4,
            key="sim_day",
        )
    with col3:
        attendance = st.slider(
            "Expected Attendance",
            1000, 6000, 3000, step=100,
            key="sim_attendance",
        )
    with col4:
        promo = st.selectbox(
            "Promo Event",
            config.PROMO_EVENTS,
            index=config.PROMO_EVENTS.index("Regular") if "Regular" in config.PROMO_EVENTS else 0,
            key="sim_promo",
        )

    # --- Input row 2 ---
    col_speed, col_start, col_stop = st.columns([2, 1, 1])
    with col_speed:
        speed = st.select_slider(
            "Simulation Speed",
            options=[1, 2, 5, 10],
            value=2,
            key="sim_speed",
        )
    with col_start:
        st.markdown("<br>", unsafe_allow_html=True)
        start_btn = st.button("Start Simulation", type="primary", use_container_width=True, key="sim_start")
    with col_stop:
        st.markdown("<br>", unsafe_allow_html=True)
        stop_btn = st.button("Stop", use_container_width=True, key="sim_stop")

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    # --- Stop handling ---
    if stop_btn:
        st.session_state["sim_running"] = False

    # --- Simulation ---
    if start_btn:
        st.session_state["sim_running"] = True

        # Get demand forecast
        from ml.predict import get_demand_forecast
        forecast = get_demand_forecast(
            opponent, day_of_week, attendance,
            month=None, is_playoff=False, promo_event=promo,
        )

        total_units = forecast["total_units"]
        by_category = forecast.get("by_category", {})

        # Distribute across periods
        period_demand = distribute_demand_by_period(total_units, by_category)

        # Determine open stands
        if attendance < 2000:
            open_stands = config.STAND_OPENING_RULES["under_2000"]["open_stands"]
        elif attendance <= 3500:
            open_stands = config.STAND_OPENING_RULES["2000_to_3500"]["open_stands"]
        else:
            open_stands = config.STAND_OPENING_RULES["over_3500"]["open_stands"]

        # Forecast info
        st.markdown(
            f"""<div style="background:{BG_CARD}; border:1px solid {BORDER_SUBTLE};
                        border-radius:10px; padding:14px 20px; margin-bottom:16px;
                        display:flex; gap:32px; flex-wrap:wrap;">
                <div>
                    <span style="color:{TEXT_SECONDARY}; font-size:0.8rem;">PREDICTED TOTAL UNITS</span><br>
                    <span style="color:{TEXT_PRIMARY}; font-size:1.3rem; font-weight:700;">{total_units:,}</span>
                </div>
                <div>
                    <span style="color:{TEXT_SECONDARY}; font-size:0.8rem;">EST. REVENUE</span><br>
                    <span style="color:{GOLD}; font-size:1.3rem; font-weight:700;">${total_units * AVG_PRICE:,.0f}</span>
                </div>
                <div>
                    <span style="color:{TEXT_SECONDARY}; font-size:0.8rem;">OPEN STANDS</span><br>
                    <span style="color:{TEXT_PRIMARY}; font-size:1.3rem; font-weight:700;">{len(open_stands)}</span>
                </div>
                <div>
                    <span style="color:{TEXT_SECONDARY}; font-size:0.8rem;">SPEED</span><br>
                    <span style="color:{PURPLE}; font-size:1.3rem; font-weight:700;">{speed}x</span>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

        # Create placeholders
        clock_ph = st.empty()
        stand_ph = st.empty()
        chart_col1, chart_col2 = st.columns(2)
        chart1_ph = chart_col1.empty()
        chart2_ph = chart_col2.empty()
        summary_ph = st.empty()

        # State accumulators
        cumulative_revenue_points = []
        tick_labels = []
        period_summaries = []
        category_totals = {}
        grand_total_units = 0
        grand_total_revenue = 0.0
        stand_totals = {
            s: {"total": 0, "revenue": 0.0, "by_category": {}}
            for s in open_stands
        }
        tick_count = 0

        # --- Period loop ---
        for period in PERIOD_ORDER:
            if not st.session_state.get("sim_running", True):
                break

            p_data = period_demand[period]
            p_minutes = PERIOD_DURATION[period]
            is_int = "intermission" in period

            stream = generate_transaction_stream(p_data["total"], p_minutes, is_int)
            period_units_so_far = 0
            period_revenue_so_far = 0.0

            # Distribute this period's demand across stands
            stand_dist = distribute_to_stands(
                p_data["total"], open_stands, p_data["by_category"]
            )

            # Build per-minute stand allocation weights
            n_stands = len(open_stands)
            stand_weights = np.array([1.5 if i == 0 else 1.0 for i in range(n_stands)])
            stand_weights = stand_weights / stand_weights.sum()

            # --- Minute-by-minute simulation ---
            for minute_offset, units in stream:
                if not st.session_state.get("sim_running", True):
                    break

                time_str = format_game_clock(period, minute_offset)
                period_name = PERIOD_DISPLAY[period]

                # Distribute this tick's units to categories
                tick_cats = {}
                if p_data["by_category"]:
                    p_total = max(1, p_data["total"])
                    for cat, cat_u in p_data["by_category"].items():
                        cat_pct = cat_u / p_total
                        tick_cats[cat] = int(round(units * cat_pct))

                # Update global category totals
                for cat, u in tick_cats.items():
                    category_totals[cat] = category_totals.get(cat, 0) + u

                # Distribute tick units to stands
                active_stands = set()
                for i, stand in enumerate(open_stands):
                    s_units = int(round(units * stand_weights[i]))
                    if s_units > 0:
                        active_stands.add(stand)
                    stand_totals[stand]["total"] += s_units
                    stand_totals[stand]["revenue"] += s_units * AVG_PRICE
                    for cat, u in tick_cats.items():
                        cat_stand_u = int(round(u * stand_weights[i]))
                        stand_totals[stand]["by_category"][cat] = (
                            stand_totals[stand]["by_category"].get(cat, 0) + cat_stand_u
                        )

                period_units_so_far += units
                period_revenue_so_far += units * AVG_PRICE
                grand_total_units += units
                grand_total_revenue += units * AVG_PRICE

                cumulative_revenue_points.append(grand_total_revenue)
                tick_labels.append(time_str)
                tick_count += 1

                # Update clock
                clock_ph.markdown(_clock_html(period_name, time_str, period), unsafe_allow_html=True)

                # Update stand grid
                stand_ph.markdown(_stand_grid_html(stand_totals, active_stands), unsafe_allow_html=True)

                # Update charts every 5 ticks (or last tick)
                if tick_count % 5 == 0 or minute_offset == stream[-1][0]:
                    chart1_ph.plotly_chart(
                        _cumulative_revenue_chart(cumulative_revenue_points, tick_labels),
                        use_container_width=True,
                        key=f"rev_chart_{tick_count}",
                    )
                    if category_totals:
                        chart2_ph.plotly_chart(
                            _category_bar_chart(category_totals),
                            use_container_width=True,
                            key=f"cat_chart_{tick_count}",
                        )

                time.sleep(0.5 / speed)

            # --- Period complete ---
            period_summaries.append({
                "period": PERIOD_DISPLAY[period],
                "units": period_units_so_far,
                "revenue": period_revenue_so_far,
                "cumulative_revenue": grand_total_revenue,
            })
            summary_ph.markdown(
                _summary_table_html(period_summaries),
                unsafe_allow_html=True,
            )

        # --- Simulation complete ---
        st.session_state["sim_running"] = False

        # Final summary banner
        st.markdown(
            f"""<div style="background:linear-gradient(135deg, {PURPLE}, #4B0082);
                        border:2px solid {GOLD}; border-radius:12px;
                        padding:24px; text-align:center; margin-top:20px;">
                <div style="color:{GOLD}; font-size:1.4rem; font-weight:800; margin-bottom:8px;">
                    SIMULATION COMPLETE
                </div>
                <div style="display:flex; justify-content:center; gap:40px; flex-wrap:wrap;">
                    <div>
                        <div style="color:rgba(255,255,255,0.7); font-size:0.8rem;">TOTAL UNITS</div>
                        <div style="color:white; font-size:1.8rem; font-weight:700;">{grand_total_units:,}</div>
                    </div>
                    <div>
                        <div style="color:rgba(255,255,255,0.7); font-size:0.8rem;">TOTAL REVENUE</div>
                        <div style="color:{GOLD}; font-size:1.8rem; font-weight:700;">${grand_total_revenue:,.0f}</div>
                    </div>
                    <div>
                        <div style="color:rgba(255,255,255,0.7); font-size:0.8rem;">REVENUE PER FAN</div>
                        <div style="color:white; font-size:1.8rem; font-weight:700;">
                            ${grand_total_revenue / max(1, attendance):.2f}
                        </div>
                    </div>
                    <div>
                        <div style="color:rgba(255,255,255,0.7); font-size:0.8rem;">STANDS ACTIVE</div>
                        <div style="color:white; font-size:1.8rem; font-weight:700;">{len(open_stands)}</div>
                    </div>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

        st.balloons()

    elif not st.session_state.get("sim_running", False):
        # Idle state -- show instructions
        st.markdown(
            f"""<div style="background:{BG_CARD}; border:1px solid {BORDER_SUBTLE};
                        border-radius:12px; padding:40px; text-align:center; margin-top:20px;">
                <div style="font-size:3rem; margin-bottom:12px;">🏒</div>
                <div style="color:{TEXT_PRIMARY}; font-size:1.1rem; font-weight:600; margin-bottom:8px;">
                    Ready to Simulate
                </div>
                <div style="color:{TEXT_SECONDARY}; font-size:0.9rem; max-width:500px; margin:0 auto;">
                    Configure the game parameters above and press <strong>Start Simulation</strong>
                    to watch predicted demand flow through each period of a game night
                    -- from gates open at 5:00 PM through post-game.
                </div>
            </div>""",
            unsafe_allow_html=True,
        )
