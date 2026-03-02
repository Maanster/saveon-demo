"""
Filter components for the Royals dashboard.
Supports both sidebar and inline (main area) modes.
"""
import streamlit as st
import pandas as pd
import sqlite3
from datetime import date


def season_filter(inline=False):
    """Season selector. Returns season int or None for 'All'.
    If inline=True, renders in main content area instead of sidebar.
    """
    container = st if inline else st.sidebar
    choice = container.selectbox("Season", ["All Seasons", "Season 1 (2024-25)", "Season 2 (2025-26)"])
    if choice == "Season 1 (2024-25)":
        return 1
    elif choice == "Season 2 (2025-26)":
        return 2
    return None


def game_selector(conn: sqlite3.Connection, inline=False):
    """
    Game picker. Returns a pandas Series for the selected game row,
    or None if no games available.
    """
    container = st if inline else st.sidebar
    games = pd.read_sql(
        "SELECT date, opponent, attendance, season FROM games ORDER BY date",
        conn,
    )
    if games.empty:
        container.warning("No games in database.")
        return None

    games["label"] = games.apply(
        lambda r: f"{r['date']}  vs {r['opponent']}  ({r['attendance']:,} fans)", axis=1
    )
    selected_label = container.selectbox("Select Game", games["label"].tolist())
    idx = games[games["label"] == selected_label].index[0]
    return games.loc[idx]


def date_range_filter(inline=False):
    """Date range picker. Returns (start_date, end_date)."""
    container = st if inline else st.sidebar
    col1, col2 = container.columns(2)
    with col1:
        start = st.date_input("From", value=date(2024, 9, 1))
    with col2:
        end = st.date_input("To", value=date.today())
    return start, end


def category_filter(conn: sqlite3.Connection, inline=True, key="cat_filter"):
    """Multi-select category filter. Returns list of selected categories or None for all."""
    container = st if inline else st.sidebar
    categories = pd.read_sql(
        "SELECT DISTINCT category FROM transactions ORDER BY category", conn
    )["category"].tolist()

    selected = container.multiselect("Categories", categories, default=[], key=key)
    return selected if selected else None


def location_filter(conn: sqlite3.Connection, inline=True, key="loc_filter"):
    """Multi-select stand/location filter. Returns list of selected locations or None for all."""
    container = st if inline else st.sidebar
    locations = pd.read_sql(
        "SELECT DISTINCT location FROM transactions ORDER BY location", conn
    )["location"].tolist()

    # Use short names for display
    short_names = [loc.replace("SOFMC ", "") for loc in locations]
    name_map = dict(zip(short_names, locations))

    selected_short = container.multiselect("Stands", short_names, default=[], key=key)
    if selected_short:
        return [name_map[s] for s in selected_short]
    return None


def promo_filter(inline=True, key="promo_filter"):
    """Promotional event filter. Returns selected promo or None for all."""
    import config
    container = st if inline else st.sidebar
    options = ["All Promos"] + config.PROMO_EVENTS
    choice = container.selectbox("Promotion", options, key=key)
    return choice if choice != "All Promos" else None


def day_of_week_filter(inline=True, key="dow_filter"):
    """Day of week multi-select filter. Returns list or None for all."""
    container = st if inline else st.sidebar
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    selected = container.multiselect("Day of Week", days, default=[], key=key)
    return selected if selected else None
