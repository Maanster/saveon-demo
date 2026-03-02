"""
Home page -- landing page for the Royals Concession Intelligence Platform.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import sqlite3
import pandas as pd
import config
import streamlit as st
from dashboard.components.theme import page_header, GOLD, TEXT_PRIMARY, TEXT_SECONDARY, BG_CARD, BORDER_SUBTLE


def render():
    page_header(
        "Royals Concession Intelligence",
        "Turning Point-of-Sale Data Into Revenue Strategy",
        "\U0001f3d2",
    )

    # Live stats from DB
    db_available = os.path.exists(config.DB_PATH)

    if db_available:
        conn = sqlite3.connect(config.DB_PATH)

        total_tx = pd.read_sql("SELECT COUNT(*) as n FROM transactions", conn).iloc[0]["n"]
        total_rev = pd.read_sql("SELECT SUM(estimated_revenue) as r FROM transactions", conn).iloc[0]["r"]
        total_games = pd.read_sql("SELECT COUNT(DISTINCT date) as g FROM games", conn).iloc[0]["g"]
        avg_att = pd.read_sql("SELECT AVG(attendance) as a FROM games", conn).iloc[0]["a"]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Transactions", f"{int(total_tx):,}")
        c2.metric("Est. Revenue", f"${total_rev:,.0f}")
        c3.metric("Games Tracked", f"{int(total_games)}")
        c4.metric("Avg Attendance", f"{avg_att:,.0f}")

        conn.close()
    else:
        st.info("Database not yet built. Run the data pipeline first: `python data_foundation/build_all.py`")

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### What's Inside")
        st.markdown("""
- **Season KPIs** -- Revenue, per-cap analysis, benchmark gaps
- **Game Explorer** -- Drill into any single game night
- **Stand Performance** -- Location-level analysis
- **Intermission Analysis** -- Transaction velocity heatmaps
- **Forecasting** -- ML-powered demand predictions
- **Revenue Estimation** -- Revenue tracking & benchmarks
- **Concession Advisor** -- AI-driven recommendations
- **Game Simulator** -- Live game demand simulator
""")

    with col2:
        st.markdown("#### Key Questions We Answer")
        st.markdown("""
- How much revenue are we leaving on the table per fan?
- Which stands and items drive the most revenue?
- When should we staff up or open extra stands?
- What promotions actually move the needle?
- How can we close the per-cap gap to WHL benchmarks?
""")

    # Key opportunity callout
    st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #7c3aed 0%, #4B0082 100%);
    border-radius: 12px;
    padding: 28px 32px;
    margin-top: 1.5rem;
    border: 1px solid rgba(255,215,0,0.3);
">
    <div style="color:{GOLD}; font-size:0.85rem; text-transform:uppercase; letter-spacing:2px; margin-bottom:8px;">
        Total Revenue Opportunity
    </div>
    <div style="font-size:2.5rem; font-weight:800; color:white; margin-bottom:8px;">
        $250K+ / year
    </div>
    <div style="color:rgba(255,255,255,0.7); font-size:0.95rem;">
        Per-cap gap closure ($180K) + Phillips Bar food ($25K) + Intermission throughput ($80K)
    </div>
</div>
""", unsafe_allow_html=True)
