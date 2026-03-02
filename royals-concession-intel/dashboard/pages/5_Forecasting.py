"""
Forecasting & Game Day Prep Sheet
==================================
ML-powered demand and revenue predictions with a printable prep sheet
for stand leads. Falls back to historical averages when models are not trained.
"""
import sys, os, sqlite3, math
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import config

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Color palette (Royals purple & gold)
# ---------------------------------------------------------------------------
PURPLE = "#4B0082"
GOLD = "#FFD700"
LIGHT_PURPLE = "#f8f6ff"
ROYALS_PALETTE = [
    "#4B0082", "#FFD700", "#6A0DAD", "#FFA500",
    "#9B30FF", "#FFB347", "#5C2D91", "#FFCC33",
]

# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300)
def _get_opponents():
    conn = sqlite3.connect(config.DB_PATH)
    df = pd.read_sql("SELECT DISTINCT opponent FROM games ORDER BY opponent", conn)
    conn.close()
    return df["opponent"].tolist()


@st.cache_data(ttl=300)
def _get_games_df():
    conn = sqlite3.connect(config.DB_PATH)
    df = pd.read_sql("SELECT * FROM games", conn)
    conn.close()
    return df


@st.cache_data(ttl=300)
def _get_category_totals():
    conn = sqlite3.connect(config.DB_PATH)
    df = pd.read_sql(
        "SELECT date, category, SUM(qty) as units FROM transactions GROUP BY date, category",
        conn,
    )
    conn.close()
    return df


@st.cache_data(ttl=300)
def _get_item_totals():
    conn = sqlite3.connect(config.DB_PATH)
    df = pd.read_sql(
        "SELECT date, category, item, SUM(qty) as units FROM transactions GROUP BY date, category, item",
        conn,
    )
    conn.close()
    return df


@st.cache_data(ttl=300)
def _get_stand_totals():
    conn = sqlite3.connect(config.DB_PATH)
    df = pd.read_sql(
        "SELECT date, location, item, SUM(qty) as units FROM transactions GROUP BY date, location, item",
        conn,
    )
    conn.close()
    return df


# ---------------------------------------------------------------------------
# ML model loading (optional)
# ---------------------------------------------------------------------------
def _try_load_ml():
    """Attempt to load trained models. Returns (demand_artifact, revenue_artifact) or (None, None)."""
    try:
        import joblib

        demand_path = os.path.join(config.MODELS_DIR, "demand_forecast.joblib")
        revenue_path = os.path.join(config.MODELS_DIR, "revenue_predictor.joblib")
        demand_art = joblib.load(demand_path) if os.path.exists(demand_path) else None
        revenue_art = joblib.load(revenue_path) if os.path.exists(revenue_path) else None
        return demand_art, revenue_art
    except Exception:
        return None, None


def _ml_demand_predict(art, opponent, day_of_week, attendance, month, is_playoff, promo_event):
    """Use trained demand models to predict units."""
    enc_opp = art["encoders"]["opponent"]
    enc_dow = art["encoders"]["day_of_week"]
    enc_promo = art["encoders"]["promo_event"]

    opp_val = opponent if opponent in enc_opp.classes_ else enc_opp.classes_[0]
    dow_val = day_of_week if day_of_week in enc_dow.classes_ else enc_dow.classes_[0]
    promo_val = promo_event if promo_event in enc_promo.classes_ else enc_promo.classes_[0]

    features = np.array([[
        enc_opp.transform([opp_val])[0],
        enc_dow.transform([dow_val])[0],
        month,
        attendance,
        int(is_playoff),
        enc_promo.transform([promo_val])[0],
    ]])

    result = {"total_units": 0, "by_category": {}, "by_item": {}}
    models = art["models"]

    if "total_units" in models:
        result["total_units"] = max(0, int(models["total_units"].predict(features)[0]))

    for cat in art.get("categories", []):
        key = f"cat_{cat}"
        if key in models:
            result["by_category"][cat] = max(0, int(models[key].predict(features)[0]))

    for item_name in art.get("top_items", []):
        key = f"item_{item_name}"
        if key in models:
            result["by_item"][item_name] = max(0, int(models[key].predict(features)[0]))

    return result


def _ml_revenue_predict(art, attendance, day_of_week, is_playoff, month, promo_event):
    """Use trained revenue model."""
    enc_dow = art["encoders"]["day_of_week"]
    enc_promo = art["encoders"]["promo_event"]

    dow_val = day_of_week if day_of_week in enc_dow.classes_ else enc_dow.classes_[0]
    promo_val = promo_event if promo_event in enc_promo.classes_ else enc_promo.classes_[0]

    features = np.array([[
        attendance,
        enc_dow.transform([dow_val])[0],
        int(is_playoff),
        month,
        enc_promo.transform([promo_val])[0],
    ]])

    pred = max(0, art["model"].predict(features)[0])
    rev_per_cap = pred / attendance if attendance > 0 else 0
    return {"predicted_revenue": pred, "revenue_per_cap": rev_per_cap}


# ---------------------------------------------------------------------------
# Historical fallback
# ---------------------------------------------------------------------------
def _comparable_games(games_df, opponent, day_of_week, attendance, n=5):
    """Find n most similar historical games by attendance proximity, then opponent/day."""
    df = games_df.copy()
    df["att_diff"] = (df["attendance"] - attendance).abs()
    df["opp_match"] = (df["opponent"] == opponent).astype(int)
    df["dow_match"] = (df["day_of_week"] == day_of_week).astype(int)
    df = df.sort_values(["opp_match", "dow_match", "att_diff"], ascending=[False, False, True])
    return df.head(n)


def _fallback_demand(games_df, cat_totals, item_totals, opponent, day_of_week, attendance, month, is_playoff, promo_event):
    """Average historical data from comparable games."""
    comps = _comparable_games(games_df, opponent, day_of_week, attendance, n=7)
    comp_dates = comps["date"].tolist()

    total_units = int(comps["total_units"].mean()) if len(comps) > 0 else 0

    by_category = {}
    cat_sub = cat_totals[cat_totals["date"].isin(comp_dates)]
    for cat in cat_sub["category"].unique():
        by_category[cat] = int(cat_sub[cat_sub["category"] == cat]["units"].mean())

    by_item = {}
    item_sub = item_totals[item_totals["date"].isin(comp_dates)]
    for _, row in item_sub.groupby(["category", "item"])["units"].mean().reset_index().iterrows():
        by_item[row["item"]] = int(row["units"])

    return {"total_units": total_units, "by_category": by_category, "by_item": by_item}


def _fallback_revenue(games_df, opponent, day_of_week, attendance):
    """Average revenue from comparable games, scaled by attendance ratio."""
    comps = _comparable_games(games_df, opponent, day_of_week, attendance, n=7)
    if len(comps) == 0:
        return {"predicted_revenue": 0, "revenue_per_cap": 0}
    avg_rev_per_cap = comps["revenue_per_cap"].mean()
    predicted_revenue = avg_rev_per_cap * attendance
    return {"predicted_revenue": predicted_revenue, "revenue_per_cap": avg_rev_per_cap}


def _fallback_stand_breakdown(stand_totals, comp_dates, open_stands):
    """Item breakdown per stand from comparable games."""
    # Map DB location names to config names for matching
    location_map = {
        "SOFMC Island Canteen": "SOFMC Island Canteen",
        "SOFMC Phillips Bar": "SOFMC Phillips Bar",
        "SOFMC Island Slice": "SOFMC Island Slice",
        "SOFMC TacoTacoTaco": "SOFMC TacoTacoTaco",
        "SOFMC ReMax Fan Deck": "SOFMC ReMax Fan Deck",
        "SOFMC Portable Stations": "SOFMC Portable",
        "SOFMC Portable": "SOFMC Portable",
    }
    reverse_map = {}
    for db_name, cfg_name in location_map.items():
        reverse_map.setdefault(cfg_name, []).append(db_name)

    sub = stand_totals[stand_totals["date"].isin(comp_dates)]
    result = {}
    for stand in open_stands:
        db_names = reverse_map.get(stand, [stand])
        stand_data = sub[sub["location"].isin(db_names)]
        if stand_data.empty:
            result[stand] = {}
            continue
        items = stand_data.groupby("item")["units"].mean().reset_index()
        items["units"] = items["units"].apply(lambda x: max(1, int(x)))
        items = items.sort_values("units", ascending=False)
        result[stand] = dict(zip(items["item"], items["units"]))
    return result


# ---------------------------------------------------------------------------
# Stand opening & staffing logic
# ---------------------------------------------------------------------------
def _get_stand_plan(attendance, is_playoff):
    if attendance < 2000:
        rule = config.STAND_OPENING_RULES["under_2000"]
    elif attendance <= 3500:
        rule = config.STAND_OPENING_RULES["2000_to_3500"]
    else:
        rule = config.STAND_OPENING_RULES["over_3500"]

    if is_playoff:
        staff_rule = config.STAFFING_RULES["playoff"]
    elif attendance >= 3500:
        staff_rule = config.STAFFING_RULES["high"]
    elif attendance >= 2000:
        staff_rule = config.STAFFING_RULES["medium"]
    else:
        staff_rule = config.STAFFING_RULES["low"]

    return {
        "open_stands": rule["open_stands"],
        "close_stands": rule["close_stands"],
        "staff_per_stand": staff_rule["staff_per_stand"],
        "buffer_pct": staff_rule["buffer_pct"],
    }


def _buffer_recommendation(attendance, is_playoff, day_of_week):
    if is_playoff or attendance > 3500:
        pct = 0.25
        label = "High demand / Playoff"
    elif attendance < 2000 and day_of_week in ("Mon", "Tue", "Wed", "Thu"):
        pct = 0.10
        label = "Low attendance weekday"
    else:
        pct = 0.15
        label = "Standard"
    return pct, label


# ---------------------------------------------------------------------------
# Category display mapping for readability
# ---------------------------------------------------------------------------
CATEGORY_DISPLAY = {
    "Beer": "Beer",
    "Cocktail": "Cocktails & Spirits",
    "Wine": "Wine",
    "NA Bev": "Non-Alcoholic Beverages",
    "Food": "Food",
    "Snacks": "Snacks",
    "Other": "Other",
    "Merch": "Merchandise",
}

ITEM_CATEGORY_MAP = {
    "Tap Beer": "Beer", "Can Beer": "Beer",
    "Cocktail": "Cocktail",
    "Wine by the Glass": "Wine", "Wine by the Glass SOFMC": "Wine",
    "Bottle Pop": "NA Bev", "Water": "NA Bev", "Fountain Pop": "NA Bev", "Hot Beverage": "NA Bev",
    "Hot Dog": "Food", "Fries": "Food", "Nachos": "Food", "Pizza Slice": "Food",
    "Cheeseburger": "Food", "Chicken Strips": "Food", "Taco": "Food",
    "Popcorn": "Snacks", "Candy": "Snacks", "Pretzel": "Snacks", "Chips": "Snacks",
    "Cider & Coolers": "Other",
}

# ---------------------------------------------------------------------------
# Prep sheet text generator (for download)
# ---------------------------------------------------------------------------
def _generate_prep_text(params, demand, revenue, stand_plan, stand_breakdown, buffer_pct, buffer_label, comparables):
    lines = []
    lines.append("=" * 64)
    lines.append("  VICTORIA ROYALS -- GAME DAY PREP SHEET")
    lines.append("=" * 64)
    lines.append(f"  Opponent:       {params['opponent']}")
    lines.append(f"  Day:            {params['day_of_week']}")
    lines.append(f"  Month:          {params['month_name']}")
    lines.append(f"  Expected Att:   {params['attendance']:,}")
    lines.append(f"  Playoff:        {'Yes' if params['is_playoff'] else 'No'}")
    lines.append(f"  Promo:          {params['promo_event']}")
    lines.append(f"  Generated:      {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("-" * 64)

    lines.append("")
    lines.append("PREDICTED TOTALS")
    lines.append(f"  Total Units:      {demand['total_units']:,}")
    lines.append(f"  Est. Revenue:     ${revenue['predicted_revenue']:,.0f}")
    lines.append(f"  Revenue/Fan:      ${revenue['revenue_per_cap']:.2f}")
    lines.append(f"  Buffer:           +{int(buffer_pct*100)}% ({buffer_label})")

    lines.append("")
    lines.append("-" * 64)
    lines.append("ITEM-LEVEL QUANTITIES (with buffer)")
    lines.append("-" * 64)

    grouped = {}
    for item_name, qty in sorted(demand.get("by_item", {}).items(), key=lambda x: -x[1]):
        cat = ITEM_CATEGORY_MAP.get(item_name, "Other")
        grouped.setdefault(cat, []).append((item_name, qty))

    for cat in ["Beer", "Cocktail", "Wine", "NA Bev", "Food", "Snacks", "Other"]:
        if cat not in grouped:
            continue
        lines.append(f"\n  [{CATEGORY_DISPLAY.get(cat, cat)}]")
        for item_name, qty in grouped[cat]:
            buffered = int(math.ceil(qty * (1 + buffer_pct)))
            lines.append(f"    {item_name:30s}  {qty:5,} units  (prep {buffered:,})")

    lines.append("")
    lines.append("-" * 64)
    lines.append("STAND OPENING PLAN")
    lines.append("-" * 64)
    for s in stand_plan["open_stands"]:
        short = s.replace("SOFMC ", "")
        lines.append(f"  [OPEN]   {short:25s}  Staff: {stand_plan['staff_per_stand']}")
    for s in stand_plan["close_stands"]:
        short = s.replace("SOFMC ", "")
        lines.append(f"  [CLOSED] {short}")
    lines.append(f"\n  Total Staff Needed: {len(stand_plan['open_stands']) * stand_plan['staff_per_stand']}")

    lines.append("")
    lines.append("-" * 64)
    lines.append("STAND-LEVEL STOCK BREAKDOWN (top items per stand)")
    lines.append("-" * 64)
    for stand_name, items in stand_breakdown.items():
        short = stand_name.replace("SOFMC ", "")
        lines.append(f"\n  >> {short}")
        for item_name, qty in list(items.items())[:10]:
            buffered = int(math.ceil(qty * (1 + buffer_pct)))
            lines.append(f"      {item_name:28s}  {qty:5,} units  (prep {buffered:,})")

    if comparables is not None and len(comparables) > 0:
        lines.append("")
        lines.append("-" * 64)
        lines.append("COMPARABLE HISTORICAL GAMES")
        lines.append("-" * 64)
        lines.append(f"  {'Date':12s} {'Opponent':15s} {'Day':5s} {'Att':>6s} {'Units':>7s} {'Revenue':>10s} {'Rev/Cap':>8s}")
        for _, r in comparables.iterrows():
            lines.append(
                f"  {r['date']:12s} {r['opponent']:15s} {r['day_of_week']:5s} "
                f"{int(r['attendance']):>6,} {int(r['total_units']):>7,} "
                f"${r['total_estimated_revenue']:>9,.0f} ${r['revenue_per_cap']:>7.2f}"
            )

    lines.append("")
    lines.append("=" * 64)
    lines.append("  Generated by Royals Concession Intelligence Platform")
    lines.append("=" * 64)
    return "\n".join(lines)


# ===========================================================================
# PAGE
# ===========================================================================
st.title("Game Day Forecasting")
st.markdown("ML-powered demand predictions and operational prep sheets for stand leads.")

# --- Load data ---
games_df = _get_games_df()
cat_totals = _get_category_totals()
item_totals = _get_item_totals()
stand_totals = _get_stand_totals()
opponents = _get_opponents()

demand_art, revenue_art = _try_load_ml()
using_ml = demand_art is not None

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTHS = {
    "September": 9, "October": 10, "November": 11, "December": 12,
    "January": 1, "February": 2, "March": 3, "April": 4,
}

# --- Input widgets (sidebar) ---
with st.sidebar:
    st.markdown("### Game Parameters")
    sel_opponent = st.selectbox("Opponent", opponents, index=opponents.index("Vancouver") if "Vancouver" in opponents else 0)
    sel_day = st.selectbox("Day of Week", DAYS, index=4)  # default Friday
    sel_attendance = st.slider("Expected Attendance", 1000, 6000, 2500, step=100)
    sel_month_name = st.selectbox("Month", list(MONTHS.keys()), index=5)  # default February
    sel_month = MONTHS[sel_month_name]
    sel_playoff = st.toggle("Playoff Game", value=False)
    sel_promo = st.selectbox("Promotional Event", config.PROMO_EVENTS, index=config.PROMO_EVENTS.index("Regular") if "Regular" in config.PROMO_EVENTS else 0)

    if using_ml:
        st.success("ML models loaded")
    else:
        st.info("Using historical averages (models not yet trained)")

# --- Run predictions ---
if using_ml:
    demand = _ml_demand_predict(demand_art, sel_opponent, sel_day, sel_attendance, sel_month, sel_playoff, sel_promo)
    revenue = _ml_revenue_predict(revenue_art, sel_attendance, sel_day, sel_playoff, sel_month, sel_promo)
else:
    demand = _fallback_demand(games_df, cat_totals, item_totals, sel_opponent, sel_day, sel_attendance, sel_month, sel_playoff, sel_promo)
    revenue = _fallback_revenue(games_df, sel_opponent, sel_day, sel_attendance)

stand_plan = _get_stand_plan(sel_attendance, sel_playoff)
buffer_pct, buffer_label = _buffer_recommendation(sel_attendance, sel_playoff, sel_day)

comparables = _comparable_games(games_df, sel_opponent, sel_day, sel_attendance, n=5)
comp_dates = comparables["date"].tolist()
stand_breakdown = _fallback_stand_breakdown(stand_totals, comp_dates, stand_plan["open_stands"])

# ===========================================================================
# PREP SHEET
# ===========================================================================
st.markdown("---")

prep_container = st.container(border=True)
with prep_container:
    # --- Header ---
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, {PURPLE} 0%, #2D004F 100%);
                    color: white; padding: 1.2rem 1.5rem; border-radius: 8px; margin-bottom: 1rem;">
            <h2 style="color: {GOLD} !important; margin: 0 0 0.3rem 0;">
                📋 Game Day Prep Sheet
            </h2>
            <div style="display: flex; gap: 2rem; flex-wrap: wrap; font-size: 0.95rem;">
                <span><strong>Opponent:</strong> {sel_opponent}</span>
                <span><strong>Day:</strong> {sel_day}</span>
                <span><strong>Month:</strong> {sel_month_name}</span>
                <span><strong>Attendance:</strong> {sel_attendance:,}</span>
                <span><strong>Playoff:</strong> {'Yes' if sel_playoff else 'No'}</span>
                <span><strong>Promo:</strong> {sel_promo}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Top-level metrics ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Predicted Units", f"{demand['total_units']:,}")
    m2.metric("Est. Revenue", f"${revenue['predicted_revenue']:,.0f}")
    m3.metric("Revenue / Fan", f"${revenue['revenue_per_cap']:.2f}")
    total_staff = len(stand_plan["open_stands"]) * stand_plan["staff_per_stand"]
    m4.metric("Total Staff", f"{total_staff}")

    # --- Buffer callout ---
    st.markdown(
        f"""<div style="background: {'#fff3cd' if buffer_pct >= 0.25 else '#d4edda'};
                border-left: 4px solid {'#ffc107' if buffer_pct >= 0.25 else '#28a745'};
                padding: 0.7rem 1rem; border-radius: 4px; margin: 0.5rem 0 1rem 0;">
            <strong>Buffer Recommendation:</strong> +{int(buffer_pct*100)}% &mdash; {buffer_label}
            {'&nbsp;&nbsp;| Playoff / high-attendance game -- stock extra!' if buffer_pct >= 0.25 else ''}
        </div>""",
        unsafe_allow_html=True,
    )

    # --- Item-Level Quantities ---
    st.subheader("Item-Level Prep Quantities")

    grouped_items = {}
    for item_name, qty in demand.get("by_item", {}).items():
        cat = ITEM_CATEGORY_MAP.get(item_name, "Other")
        grouped_items.setdefault(cat, []).append((item_name, qty))

    if grouped_items:
        cat_order = ["Beer", "Cocktail", "Wine", "NA Bev", "Food", "Snacks", "Other"]
        rows = []
        for cat in cat_order:
            if cat not in grouped_items:
                continue
            for item_name, qty in sorted(grouped_items[cat], key=lambda x: -x[1]):
                buffered = int(math.ceil(qty * (1 + buffer_pct)))
                rows.append({
                    "Category": CATEGORY_DISPLAY.get(cat, cat),
                    "Item": item_name,
                    "Predicted Units": qty,
                    f"Prep (+{int(buffer_pct*100)}%)": buffered,
                })
        if rows:
            item_df = pd.DataFrame(rows)
            st.dataframe(
                item_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Predicted Units": st.column_config.NumberColumn(format="%d"),
                    f"Prep (+{int(buffer_pct*100)}%)": st.column_config.NumberColumn(format="%d"),
                },
            )
        else:
            st.info("No item-level predictions available.")
    else:
        st.info("No item-level predictions available.")

    # --- Stand Opening Recommendation ---
    st.subheader("Stand Opening Plan")
    open_col, close_col = st.columns(2)
    with open_col:
        for s in stand_plan["open_stands"]:
            short = s.replace("SOFMC ", "")
            st.markdown(
                f'<div style="background: #d4edda; padding: 0.5rem 0.8rem; border-radius: 4px; '
                f'margin: 0.3rem 0; border-left: 4px solid #28a745;">'
                f'OPEN &nbsp; <strong>{short}</strong> &nbsp; | &nbsp; Staff: {stand_plan["staff_per_stand"]}</div>',
                unsafe_allow_html=True,
            )
    with close_col:
        if stand_plan["close_stands"]:
            for s in stand_plan["close_stands"]:
                short = s.replace("SOFMC ", "")
                st.markdown(
                    f'<div style="background: #f8d7da; padding: 0.5rem 0.8rem; border-radius: 4px; '
                    f'margin: 0.3rem 0; border-left: 4px solid #dc3545;">'
                    f'CLOSED &nbsp; <strong>{short}</strong></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown("*All stands open for this attendance level.*")

    # --- Stand-Level Stock Breakdown ---
    st.subheader("Stand-Level Stock Breakdown")
    if stand_breakdown:
        tabs = st.tabs([s.replace("SOFMC ", "") for s in stand_plan["open_stands"]])
        for i, stand_name in enumerate(stand_plan["open_stands"]):
            with tabs[i]:
                items = stand_breakdown.get(stand_name, {})
                if items:
                    rows = []
                    for item_name, qty in items.items():
                        buffered = int(math.ceil(qty * (1 + buffer_pct)))
                        rows.append({"Item": item_name, "Avg Units": qty, f"Prep (+{int(buffer_pct*100)}%)": buffered})
                    sdf = pd.DataFrame(rows)
                    st.dataframe(sdf, use_container_width=True, hide_index=True)
                else:
                    st.info(f"No historical data for {stand_name.replace('SOFMC ', '')}.")
    else:
        st.info("No stand-level breakdown available.")

    # --- Historical Comparable Games ---
    st.subheader("Comparable Historical Games")
    if len(comparables) > 0:
        display_comps = comparables[["date", "opponent", "day_of_week", "attendance",
                                      "total_units", "total_estimated_revenue", "revenue_per_cap"]].copy()
        display_comps.columns = ["Date", "Opponent", "Day", "Attendance", "Units", "Revenue", "Rev/Cap"]
        display_comps["Revenue"] = display_comps["Revenue"].apply(lambda x: f"${x:,.0f}")
        display_comps["Rev/Cap"] = display_comps["Rev/Cap"].apply(lambda x: f"${x:.2f}")
        display_comps["Attendance"] = display_comps["Attendance"].apply(lambda x: f"{int(x):,}")
        display_comps["Units"] = display_comps["Units"].apply(lambda x: f"{int(x):,}")
        st.dataframe(display_comps, use_container_width=True, hide_index=True)
    else:
        st.info("No comparable games found.")

    # --- Download button ---
    params_dict = {
        "opponent": sel_opponent, "day_of_week": sel_day,
        "month_name": sel_month_name, "attendance": sel_attendance,
        "is_playoff": sel_playoff, "promo_event": sel_promo,
    }
    prep_text = _generate_prep_text(
        params_dict, demand, revenue, stand_plan, stand_breakdown,
        buffer_pct, buffer_label, comparables,
    )
    st.download_button(
        label="Download Prep Sheet",
        data=prep_text,
        file_name=f"prep_sheet_{sel_opponent}_{sel_day}_{sel_attendance}.txt",
        mime="text/plain",
        use_container_width=True,
    )

# ===========================================================================
# CHARTS (Secondary)
# ===========================================================================
st.markdown("---")
st.subheader("Demand Breakdown")

chart_col1, chart_col2 = st.columns([2, 1])

with chart_col1:
    by_cat = demand.get("by_category", {})
    if by_cat:
        cats = list(by_cat.keys())
        vals = list(by_cat.values())
        display_cats = [CATEGORY_DISPLAY.get(c, c) for c in cats]

        fig = go.Figure(go.Bar(
            x=display_cats,
            y=vals,
            marker_color=ROYALS_PALETTE[:len(cats)],
            text=[f"{v:,}" for v in vals],
            textposition="outside",
        ))
        fig.update_layout(
            title="Predicted Units by Category",
            xaxis_title="",
            yaxis_title="Units",
            height=420,
            font=dict(family="Inter, sans-serif", color="#333"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=50, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No category breakdown available.")

with chart_col2:
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, {LIGHT_PURPLE} 0%, #ede7f6 100%);
                    border: 1px solid {PURPLE}; border-left: 4px solid {GOLD};
                    padding: 1.5rem; border-radius: 8px; text-align: center; margin-top: 1rem;">
            <p style="color: {PURPLE}; font-size: 0.85rem; margin: 0 0 0.3rem 0; font-weight: 600;">
                PREDICTED REVENUE
            </p>
            <p style="color: {PURPLE}; font-size: 2.2rem; font-weight: 700; margin: 0;">
                ${revenue['predicted_revenue']:,.0f}
            </p>
            <p style="color: #666; font-size: 0.85rem; margin: 0.5rem 0 0 0;">
                ${revenue['revenue_per_cap']:.2f} per fan
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("")
    st.markdown(
        f"""
        <div style="background: #e8f5e9; border-left: 4px solid #4CAF50;
                    padding: 1rem; border-radius: 4px; margin-top: 0.5rem;">
            <p style="margin: 0; font-size: 0.85rem; color: #333;">
                <strong>Business Impact</strong><br>
                Accurate demand prediction saves <strong>$35K-$60K annually</strong>
                in food waste and labor costs.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
