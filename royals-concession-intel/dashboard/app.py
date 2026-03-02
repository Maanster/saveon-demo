"""
Royals Concession Intelligence Platform -- Single-entrypoint router.
Dark sports-analytics theme with horizontal navigation.
"""
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Royals Concession Intelligence",
    page_icon="\U0001f3d2",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Apply global dark theme CSS
from dashboard.components.theme import apply_theme
apply_theme()

# ── Mode toggle: Slides vs Demo ─────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
mode = st.radio(
    "Switch view",
    options=["View Demo", "View Slides"],
    horizontal=True,
    label_visibility="collapsed",
    key="mode_toggle",
)

if mode == "View Slides":
    slides_path = os.path.join(PROJECT_ROOT, "slides.html")
    if os.path.exists(slides_path):
        with open(slides_path, "r", encoding="utf-8") as f:
            slides_html = f.read()
        components.html(slides_html, height=850, scrolling=True)
    else:
        st.error(f"Slides not found at {slides_path}")
    st.stop()

# Horizontal navigation (Demo mode)
from streamlit_option_menu import option_menu

selected = option_menu(
    menu_title=None,
    options=[
        "Home", "Season KPIs", "Game Explorer", "Stand Performance",
        "Intermission", "Forecasting", "Revenue", "Advisor", "Simulator",
    ],
    icons=[
        "house", "bar-chart-line", "controller", "shop",
        "clock-history", "graph-up-arrow", "currency-dollar", "robot", "play-circle",
    ],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {
            "padding": "0 !important",
            "background-color": "#161b22",
            "border-radius": "10px",
            "margin-bottom": "1.2rem",
            "border": "1px solid rgba(255,255,255,0.06)",
        },
        "icon": {"color": "#8b949e", "font-size": "14px"},
        "nav-link": {
            "font-size": "14px",
            "text-align": "center",
            "margin": "0px",
            "color": "#8b949e",
            "padding": "10px 16px",
            "--hover-color": "#1c2333",
        },
        "nav-link-selected": {
            "background-color": "#1c2333",
            "color": "#FFD700",
            "font-weight": "700",
            "border-bottom": "3px solid #FFD700",
        },
    },
)

# ── Route to page ─────────────────────────────────────────────────────────────
if selected == "Home":
    from dashboard.pages.home import render
    render()
elif selected == "Season KPIs":
    from dashboard.pages.season_kpis import render
    render()
elif selected == "Game Explorer":
    from dashboard.pages.game_explorer import render
    render()
elif selected == "Stand Performance":
    from dashboard.pages.stand_performance import render
    render()
elif selected == "Intermission":
    from dashboard.pages.intermission_analysis import render
    render()
elif selected == "Forecasting":
    from dashboard.pages.forecasting import render
    render()
elif selected == "Revenue":
    from dashboard.pages.revenue_estimation import render
    render()
elif selected == "Advisor":
    from dashboard.pages.concession_advisor import render
    render()
elif selected == "Simulator":
    from dashboard.pages.game_simulator import render
    render()
