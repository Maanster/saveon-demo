"""
Unified prediction API for the Royals Concession Intelligence Platform.
Loads trained models lazily and exposes functions for demand, revenue,
affinity, and comparable-game lookups.
"""
import sys, os, json, sqlite3
import numpy as np
import pandas as pd
import joblib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

# ---------------------------------------------------------------------------
# Lazy model cache
# ---------------------------------------------------------------------------
_cache = {}


def load_models(force=False):
    """
    Load all model artifacts into memory. Cached after first call.
    Returns dict with keys: demand, revenue, affinity (each may be None).
    """
    if _cache and not force:
        return _cache

    # Demand forecast
    demand_path = os.path.join(config.MODELS_DIR, "demand_forecast.joblib")
    try:
        _cache["demand"] = joblib.load(demand_path)
    except Exception:
        _cache["demand"] = None

    # Revenue predictor
    revenue_path = os.path.join(config.MODELS_DIR, "revenue_predictor.joblib")
    try:
        _cache["revenue"] = joblib.load(revenue_path)
    except Exception:
        _cache["revenue"] = None

    # Affinity rules
    affinity_path = os.path.join(config.MODELS_DIR, "affinity_rules.json")
    try:
        with open(affinity_path) as f:
            _cache["affinity"] = json.load(f)
    except Exception:
        _cache["affinity"] = None

    return _cache


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_encode(encoder, value, fallback=0):
    """Encode a value with a LabelEncoder, returning fallback if unseen."""
    try:
        return int(encoder.transform([value])[0])
    except (ValueError, KeyError):
        # Unseen label -- use the most frequent class or fallback
        return fallback


def _get_historical_stand_proportions():
    """
    Compute historical proportion of units sold at each stand.
    Returns dict: {location: proportion}.
    """
    try:
        conn = sqlite3.connect(config.DB_PATH)
        df = pd.read_sql_query(
            "SELECT location, SUM(qty) as total_qty FROM transactions GROUP BY location",
            conn,
        )
        conn.close()
        total = df["total_qty"].sum()
        if total == 0:
            return {}
        return dict(zip(df["location"], (df["total_qty"] / total).round(4)))
    except Exception:
        return {}


def _current_month():
    """Return current month as int."""
    from datetime import datetime
    return datetime.now().month


# ---------------------------------------------------------------------------
# Demand forecast
# ---------------------------------------------------------------------------

def get_demand_forecast(
    opponent,
    day_of_week,
    attendance,
    month=None,
    is_playoff=False,
    promo_event="Regular",
):
    """
    Predict demand for a future game.

    Returns dict:
        total_units: int
        by_category: {category: predicted_units}
        by_item: {item_name: predicted_units}
        by_stand: {stand_name: predicted_units}
    """
    models_data = load_models()
    demand = models_data.get("demand")

    if month is None:
        month = _current_month()

    # Fallback if model not available
    if demand is None:
        avg_units = attendance * 0.8  # rough heuristic
        return {
            "total_units": int(avg_units),
            "by_category": {c: int(avg_units / len(config.CATEGORIES)) for c in config.CATEGORIES},
            "by_item": {},
            "by_stand": {},
            "_fallback": True,
        }

    encoders = demand["encoders"]
    models = demand["models"]

    opp_enc = _safe_encode(encoders["opponent"], opponent)
    dow_enc = _safe_encode(encoders["day_of_week"], day_of_week)
    promo_enc = _safe_encode(encoders["promo_event"], promo_event)

    features = np.array([[opp_enc, dow_enc, month, attendance, int(is_playoff), promo_enc]])

    # Total units
    total_model = models.get("total_units")
    total_units = int(max(0, total_model.predict(features)[0])) if total_model else 0

    # By category
    by_category = {}
    for cat in demand.get("categories", []):
        cat_model = models.get(f"cat_{cat}")
        if cat_model:
            pred = max(0, cat_model.predict(features)[0])
            by_category[cat] = int(pred)

    # By item
    by_item = {}
    for item_name in demand.get("top_items", []):
        item_model = models.get(f"item_{item_name}")
        if item_model:
            pred = max(0, item_model.predict(features)[0])
            by_item[item_name] = int(pred)

    # By stand
    stand_proportions = _get_historical_stand_proportions()
    by_stand = {}
    for stand, prop in stand_proportions.items():
        by_stand[stand] = int(total_units * prop)

    return {
        "total_units": total_units,
        "by_category": by_category,
        "by_item": by_item,
        "by_stand": by_stand,
    }


# ---------------------------------------------------------------------------
# Revenue prediction
# ---------------------------------------------------------------------------

def get_revenue_prediction(
    attendance,
    day_of_week,
    is_playoff=False,
    month=None,
    promo_event="Regular",
):
    """
    Predict total revenue for a game.

    Returns dict:
        predicted_revenue: float
        confidence_interval: (low, high)
        revenue_per_cap: float
    """
    models_data = load_models()
    rev = models_data.get("revenue")

    if month is None:
        month = _current_month()

    # Fallback
    if rev is None:
        avg_rev_per_cap = 6.50
        predicted = attendance * avg_rev_per_cap
        return {
            "predicted_revenue": round(predicted, 2),
            "confidence_interval": [round(predicted * 0.8, 2), round(predicted * 1.2, 2)],
            "revenue_per_cap": avg_rev_per_cap,
            "_fallback": True,
        }

    encoders = rev["encoders"]
    model = rev["model"]
    residual_std = rev.get("residual_std", 0)

    dow_enc = _safe_encode(encoders["day_of_week"], day_of_week)
    promo_enc = _safe_encode(encoders["promo_event"], promo_event)

    features = np.array([[attendance, dow_enc, int(is_playoff), month, promo_enc]])
    predicted = float(model.predict(features)[0])
    predicted = max(0, predicted)

    # 95% confidence interval using residual std
    ci_low = max(0, predicted - 1.96 * residual_std)
    ci_high = predicted + 1.96 * residual_std

    rev_per_cap = predicted / attendance if attendance > 0 else 0

    return {
        "predicted_revenue": round(predicted, 2),
        "confidence_interval": [round(ci_low, 2), round(ci_high, 2)],
        "revenue_per_cap": round(rev_per_cap, 2),
    }


# ---------------------------------------------------------------------------
# Affinity / bundles
# ---------------------------------------------------------------------------

def get_affinity_recommendations():
    """
    Return bundle suggestions from affinity analysis.

    Returns list of dicts:
        [{name, items, suggested_price, estimated_annual_revenue}, ...]
    """
    models_data = load_models()
    affinity = models_data.get("affinity")

    if affinity is None:
        return []

    bundles = affinity.get("suggested_bundles", [])
    return [
        {
            "name": b["name"],
            "items": b["items"],
            "suggested_price": b["suggested_price"],
            "individual_total": b.get("individual_total", 0),
            "savings": b.get("savings", 0),
            "estimated_annual_revenue": b.get("estimated_annual_revenue", 0),
        }
        for b in bundles
    ]


# ---------------------------------------------------------------------------
# Comparable games
# ---------------------------------------------------------------------------

def get_comparable_games(opponent=None, day_of_week=None, attendance=None, limit=5):
    """
    Find 3-5 most similar historical games from the database.

    Matches by: opponent (exact), day_of_week (exact), attendance (within 500).
    Returns list of game dicts with actual metrics.
    """
    try:
        conn = sqlite3.connect(config.DB_PATH)
        games = pd.read_sql_query("SELECT * FROM games ORDER BY date DESC", conn)
        conn.close()
    except Exception:
        return []

    if games.empty:
        return []

    # Score each game by similarity
    games["score"] = 0.0

    if opponent:
        games["score"] += (games["opponent"] == opponent).astype(float) * 3.0

    if day_of_week:
        games["score"] += (games["day_of_week"] == day_of_week).astype(float) * 2.0

    if attendance:
        att_diff = np.abs(games["attendance"] - attendance)
        games["score"] += (att_diff <= 500).astype(float) * 2.0
        games["score"] += (att_diff <= 1000).astype(float) * 1.0
        # Tie-breaker: closer attendance is better
        games["score"] -= (att_diff / 10000.0)

    # Sort by score descending, take top N
    games = games.sort_values("score", ascending=False).head(max(limit, 3))

    result = []
    for _, row in games.iterrows():
        result.append({
            "date": row["date"],
            "opponent": row["opponent"],
            "day_of_week": row["day_of_week"],
            "attendance": int(row["attendance"]),
            "is_playoff": bool(row["is_playoff"]),
            "promo_event": row.get("promo_event", "Regular"),
            "total_units": int(row.get("total_units", 0)),
            "total_transactions": int(row.get("total_transactions", 0)),
            "total_estimated_revenue": float(row.get("total_estimated_revenue", 0)),
            "units_per_cap": float(row.get("units_per_cap", 0)),
            "revenue_per_cap": float(row.get("revenue_per_cap", 0)),
        })

    return result


# ---------------------------------------------------------------------------
# Quick test when run directly
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Loading models...")
    m = load_models()
    print(f"  Demand model:   {'loaded' if m.get('demand') else 'NOT FOUND'}")
    print(f"  Revenue model:  {'loaded' if m.get('revenue') else 'NOT FOUND'}")
    print(f"  Affinity rules: {'loaded' if m.get('affinity') else 'NOT FOUND'}")

    print("\nSample demand forecast (Kelowna, Fri, 3000 attendance):")
    forecast = get_demand_forecast("Kelowna", "Fri", 3000, month=11)
    for k, v in forecast.items():
        if isinstance(v, dict):
            print(f"  {k}:")
            for sub_k, sub_v in list(v.items())[:5]:
                print(f"    {sub_k}: {sub_v}")
        else:
            print(f"  {k}: {v}")

    print("\nSample revenue prediction (3000 attendance, Fri):")
    rev = get_revenue_prediction(3000, "Fri", month=11)
    for k, v in rev.items():
        print(f"  {k}: {v}")

    print("\nAffinity recommendations:")
    recs = get_affinity_recommendations()
    for r in recs[:3]:
        print(f"  {r['name']}: ${r['suggested_price']}")

    print("\nComparable games (Kelowna, Fri, ~3000):")
    comps = get_comparable_games("Kelowna", "Fri", 3000)
    for c in comps[:3]:
        print(f"  {c['date']} vs {c['opponent']} att={c['attendance']} rev=${c['total_estimated_revenue']:.0f}")
