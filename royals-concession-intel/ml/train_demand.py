"""
Train demand-forecasting models using GradientBoostingRegressor.
Produces one model for total units, one per category, and one per top-20 item.
"""
import sys, os, sqlite3, warnings
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import cross_val_score
import joblib

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

FEATURE_COLS = ["opponent_enc", "dow_enc", "month", "attendance", "is_playoff", "promo_enc"]


def _load_game_data():
    """Load game-level data from DB."""
    conn = sqlite3.connect(config.DB_PATH)

    games = pd.read_sql_query("SELECT * FROM games", conn)

    # Category totals per game
    cat_totals = pd.read_sql_query(
        "SELECT date, category, SUM(qty) as cat_units FROM transactions GROUP BY date, category",
        conn,
    )

    # Item totals per game
    item_totals = pd.read_sql_query(
        "SELECT date, item, SUM(qty) as item_units FROM transactions GROUP BY date, item",
        conn,
    )

    conn.close()
    return games, cat_totals, item_totals


def _build_encoders(games):
    """Fit label encoders for categorical features."""
    enc_opp = LabelEncoder()
    enc_opp.fit(games["opponent"].fillna("Unknown"))

    enc_dow = LabelEncoder()
    enc_dow.fit(games["day_of_week"].fillna("Unknown"))

    enc_promo = LabelEncoder()
    enc_promo.fit(games["promo_event"].fillna("Regular"))

    return enc_opp, enc_dow, enc_promo


def _build_features(games, enc_opp, enc_dow, enc_promo):
    """Create feature matrix from game data."""
    df = games.copy()
    df["opponent_enc"] = enc_opp.transform(df["opponent"].fillna("Unknown"))
    df["dow_enc"] = enc_dow.transform(df["day_of_week"].fillna("Unknown"))
    df["promo_enc"] = enc_promo.transform(df["promo_event"].fillna("Regular"))
    df["month"] = pd.to_datetime(df["date"]).dt.month
    df["is_playoff"] = df["is_playoff"].astype(int)
    return df


def _train_model(X, y, label=""):
    """Train a single GBR model and print metrics."""
    model = GradientBoostingRegressor(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.1,
        min_samples_leaf=3,
        random_state=42,
    )
    model.fit(X, y)

    # Metrics on training set (small dataset -- cross-val more informative)
    preds = model.predict(X)
    mask = y > 0
    if mask.sum() > 0:
        mape = np.mean(np.abs((y[mask] - preds[mask]) / y[mask])) * 100
    else:
        mape = 0.0

    r2_scores = cross_val_score(model, X, y, cv=min(5, len(y)), scoring="r2")
    r2 = r2_scores.mean()

    print(f"  {label:30s}  MAPE={mape:6.1f}%  CV-R2={r2:.3f}  (n={len(y)})")
    return model


def train():
    """Main training pipeline."""
    print("Loading data...")
    games, cat_totals, item_totals = _load_game_data()

    if len(games) == 0:
        print("ERROR: No game data in database. Aborting.")
        return

    enc_opp, enc_dow, enc_promo = _build_encoders(games)
    df = _build_features(games, enc_opp, enc_dow, enc_promo)

    X = df[FEATURE_COLS].values
    models = {}
    categories_trained = []
    top_items = []

    # --- Total units model ---
    print("\nTraining total-units model...")
    y_total = df["total_units"].values.astype(float)
    models["total_units"] = _train_model(X, y_total, "total_units")

    # --- Per-category models ---
    print("\nTraining per-category models...")
    for cat in config.CATEGORIES:
        cat_df = cat_totals[cat_totals["category"] == cat]
        if cat_df.empty:
            continue
        merged = df.merge(cat_df[["date", "cat_units"]], on="date", how="left")
        merged["cat_units"] = merged["cat_units"].fillna(0)
        y_cat = merged["cat_units"].values.astype(float)
        if y_cat.sum() == 0:
            continue
        models[f"cat_{cat}"] = _train_model(X, y_cat, f"category: {cat}")
        categories_trained.append(cat)

    # --- Top-20 items by volume ---
    print("\nTraining per-item models (top 20)...")
    item_volume = item_totals.groupby("item")["item_units"].sum().sort_values(ascending=False)
    top_20_items = item_volume.head(20).index.tolist()

    for item_name in top_20_items:
        item_df = item_totals[item_totals["item"] == item_name]
        if item_df.empty:
            continue
        merged = df.merge(item_df[["date", "item_units"]], on="date", how="left")
        merged["item_units"] = merged["item_units"].fillna(0)
        y_item = merged["item_units"].values.astype(float)
        if y_item.sum() == 0:
            continue
        safe_key = f"item_{item_name}"
        models[safe_key] = _train_model(X, y_item, f"item: {item_name[:25]}")
        top_items.append(item_name)

    # --- Save ---
    os.makedirs(config.MODELS_DIR, exist_ok=True)
    output_path = os.path.join(config.MODELS_DIR, "demand_forecast.joblib")

    artifact = {
        "models": models,
        "encoders": {
            "opponent": enc_opp,
            "day_of_week": enc_dow,
            "promo_event": enc_promo,
        },
        "feature_names": FEATURE_COLS,
        "top_items": top_items,
        "categories": categories_trained,
    }
    joblib.dump(artifact, output_path)
    print(f"\nSaved {len(models)} models to {output_path}")
    print(f"Categories: {categories_trained}")
    print(f"Top items:  {top_items}")


if __name__ == "__main__":
    train()
