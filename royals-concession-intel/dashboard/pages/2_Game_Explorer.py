"""
Game Explorer — drill into any single game's concession performance.
"""

import sys, os

# Allow imports from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import config

# ---------------------------------------------------------------------------
# Colour palette — Royals purples & golds
# ---------------------------------------------------------------------------
PURPLES = ["#4B0082", "#6A0DAD", "#9B30FF"]
GOLDS = ["#FFD700", "#FFA500"]
ROYALS_PALETTE = [PURPLES[0], GOLDS[0], PURPLES[1], GOLDS[1], PURPLES[2],
                  "#C0C0C0", "#8B008B", "#DAA520"]

# ---------------------------------------------------------------------------
# Helpers / cached queries
# ---------------------------------------------------------------------------

def _conn():
    return sqlite3.connect(config.DB_PATH)


@st.cache_data(ttl=300)
def load_games() -> pd.DataFrame:
    """Return all rows from the games table."""
    with _conn() as con:
        df = pd.read_sql("SELECT * FROM games ORDER BY date", con)
    return df


@st.cache_data(ttl=300)
def load_transactions_for_game(game_date: str) -> pd.DataFrame:
    """Return every transaction row for a given game date."""
    with _conn() as con:
        df = pd.read_sql(
            "SELECT * FROM transactions WHERE date = ?",
            con,
            params=(game_date,),
        )
    return df


# ---------------------------------------------------------------------------
# Chart builders
# ---------------------------------------------------------------------------

def chart_units_by_category(txn: pd.DataFrame):
    """Horizontal bar — total units sold per category."""
    cat = txn.groupby("category", as_index=False)["qty"].sum().sort_values("qty")
    fig = px.bar(
        cat, x="qty", y="category", orientation="h",
        color="category", color_discrete_sequence=ROYALS_PALETTE,
        labels={"qty": "Units Sold", "category": "Category"},
    )
    fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=10, b=0), height=350)
    return fig


def chart_transaction_timeline(txn: pd.DataFrame):
    """Line chart with 5-min buckets from 18:00-22:00, period boundaries marked."""
    df = txn.copy()
    df["ts"] = pd.to_datetime(df["date"] + " " + df["time"], errors="coerce")
    df = df.dropna(subset=["ts"])
    df = df.set_index("ts")

    # 5-minute resample
    timeline = df.resample("5min")["qty"].sum().reset_index()
    timeline.columns = ["time", "units"]

    # Restrict to 6pm-10pm window
    timeline = timeline[
        (timeline["time"].dt.hour >= 18) & (timeline["time"].dt.hour < 22)
    ]

    fig = px.line(
        timeline, x="time", y="units",
        labels={"time": "Time", "units": "Units Sold"},
    )
    fig.update_traces(line_color=PURPLES[1], line_width=2.5)

    # Period boundaries from config
    period_labels = {
        "1st Period": "19:05", "1st Int.": "19:25",
        "2nd Period": "19:45", "2nd Int.": "20:05",
        "3rd Period": "20:25", "Post-Game": "21:00",
    }
    base_date = timeline["time"].dt.date.min() if len(timeline) else None
    if base_date is not None:
        for label, hm in period_labels.items():
            ts = pd.Timestamp(f"{base_date} {hm}")
            fig.add_vline(x=ts, line_dash="dot", line_color=GOLDS[0], opacity=0.6)
            fig.add_annotation(
                x=ts, y=1, yref="paper", text=label,
                showarrow=False, font=dict(size=9, color=GOLDS[1]),
                textangle=-90, yanchor="top",
            )

    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=350)
    return fig


def chart_top_items(txn: pd.DataFrame, n: int = 10):
    """Horizontal bar — top N items by units."""
    items = txn.groupby("item", as_index=False)["qty"].sum()
    items = items.nlargest(n, "qty").sort_values("qty")
    fig = px.bar(
        items, x="qty", y="item", orientation="h",
        color_discrete_sequence=[PURPLES[1]],
        labels={"qty": "Units Sold", "item": "Item"},
    )
    fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=10, b=0), height=350)
    return fig


def chart_stand_breakdown(txn: pd.DataFrame):
    """Pie chart — share of transactions per stand/location."""
    stand = txn.groupby("location", as_index=False)["qty"].sum()
    fig = px.pie(
        stand, names="location", values="qty",
        color_discrete_sequence=ROYALS_PALETTE,
        hole=0.35,
    )
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=10), height=350)
    return fig


# ---------------------------------------------------------------------------
# Forecast vs Actual
# ---------------------------------------------------------------------------

def _try_forecast(game_date: str, txn: pd.DataFrame):
    """Attempt to load forecast data. Returns (forecast_df | None, error_msg | None)."""
    try:
        from ml.predict import get_demand_forecast
        forecast = get_demand_forecast(game_date)
        return forecast, None
    except ImportError:
        return None, "Models not yet trained"
    except Exception as exc:
        return None, f"Models not yet trained ({exc})"


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Game Explorer | Royals", page_icon="🏒", layout="wide")
st.title("🏒 Game Explorer")

# --- load games ----------------------------------------------------------
try:
    games_df = load_games()
except Exception:
    st.error("Game data is not available yet. Please run the data pipeline first (python build_all.py).")
    st.stop()

if games_df.empty:
    st.warning("No games found in the database.")
    st.stop()

# --- game selector --------------------------------------------------------
games_df["label"] = (
    games_df["date"] + "  |  " + games_df["opponent"]
    + "  |  Attendance: " + games_df["attendance"].astype(str)
)
selected_label = st.selectbox("Select a game", games_df["label"].tolist())
sel_idx = games_df[games_df["label"] == selected_label].index[0]
game = games_df.loc[sel_idx]

game_date = game["date"]

# --- transactions for this game ------------------------------------------
try:
    txn = load_transactions_for_game(game_date)
except Exception:
    txn = pd.DataFrame()

# === $1 Dog Night callout ================================================
if game_date == "2025-10-22":
    st.markdown(
        """
        <div style="background:linear-gradient(90deg,#FFD700 0%,#FFA500 100%);
                    padding:18px 24px;border-radius:12px;margin-bottom:18px;">
        <h3 style="margin:0;color:#4B0082;">🌭 $1 Dog Night</h3>
        <p style="margin:6px 0 0;color:#333;font-size:1.05rem;">
        1,167 hot dog transactions. 30% of all sales.
        Proof that data-driven promotions work.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# === Game metadata card ===================================================
st.subheader("Game Snapshot")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Opponent", game.get("opponent", "—"))
c2.metric("Day", game.get("day_of_week", "—"))
c3.metric("Attendance", f"{int(game.get('attendance', 0)):,}")
c4.metric("Season", int(game.get("season", 1)))

c5, c6, c7, c8 = st.columns(4)
c5.metric("Total Revenue (est.)", f"${game.get('total_estimated_revenue', 0):,.0f}")
c6.metric("Total Units", f"{int(game.get('total_units', 0)):,}")
c7.metric("Units / Cap", f"{game.get('units_per_cap', 0):.2f}")
c8.metric("Revenue / Cap", f"${game.get('revenue_per_cap', 0):.2f}")

# === Business impact callout ==============================================
rev_per_cap = game.get("revenue_per_cap", 0)
attendance = int(game.get("attendance", 0))
if rev_per_cap and attendance:
    whl_low, whl_high = 14.0, 16.0
    if rev_per_cap < whl_high:
        gap = whl_high - rev_per_cap
        annual_upside = gap * attendance * 35  # ~35 home games per season
        st.info(
            f"This game's per-cap was **${rev_per_cap:.2f}**. The WHL benchmark is "
            f"**$14 -- $16**. At scale, closing this gap = **${annual_upside:,.0f} annually**."
        )
    else:
        st.success(
            f"This game's per-cap of **${rev_per_cap:.2f}** meets or exceeds the WHL benchmark ($14 -- $16)."
        )

# === Charts — only if we have transaction data ============================
if txn.empty:
    st.warning("No transaction-level data found for this game.")
    st.stop()

st.divider()

# Row 1: Units by category + Transaction timeline
col_a, col_b = st.columns(2)
with col_a:
    st.markdown("**Units by Category**")
    st.plotly_chart(chart_units_by_category(txn), use_container_width=True)
with col_b:
    st.markdown("**Transaction Timeline (5-min buckets)**")
    st.plotly_chart(chart_transaction_timeline(txn), use_container_width=True)

# Row 2: Top 10 items + Stand breakdown
col_c, col_d = st.columns(2)
with col_c:
    st.markdown("**Top 10 Items**")
    st.plotly_chart(chart_top_items(txn), use_container_width=True)
with col_d:
    st.markdown("**Stand Breakdown**")
    st.plotly_chart(chart_stand_breakdown(txn), use_container_width=True)

# === Forecast vs Actual toggle ============================================
st.divider()
show_forecast = st.toggle("Show Forecast vs. Actual", value=False)
if show_forecast:
    forecast_df, err = _try_forecast(game_date, txn)
    if err:
        st.warning(err)
    elif forecast_df is not None and not forecast_df.empty:
        st.markdown("**Forecast vs. Actual — Units by Category**")
        actual = txn.groupby("category", as_index=False)["qty"].sum().rename(columns={"qty": "Actual"})
        merged = actual.merge(forecast_df, on="category", how="outer").fillna(0)
        merged = merged.sort_values("Actual", ascending=True)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=merged["category"], x=merged["Actual"], name="Actual",
            orientation="h", marker_color=PURPLES[1],
        ))
        if "predicted" in merged.columns:
            fig.add_trace(go.Bar(
                y=merged["category"], x=merged["predicted"], name="Forecast",
                orientation="h", marker_color=GOLDS[0],
            ))
        fig.update_layout(barmode="group", margin=dict(l=0, r=0, t=10, b=0), height=350)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No forecast data returned for this game.")
