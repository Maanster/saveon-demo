"""
Train revenue prediction model using LinearRegression.
Target: total_estimated_revenue per game.
"""
import sys, os, sqlite3, warnings
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import cross_val_score
import joblib

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

FEATURE_COLS = ["attendance", "dow_enc", "is_playoff", "month", "promo_enc"]


def train():
    """Train and save the revenue prediction model."""
    print("Loading game data...")
    conn = sqlite3.connect(config.DB_PATH)
    games = pd.read_sql_query("SELECT * FROM games", conn)
    conn.close()

    if len(games) == 0:
        print("ERROR: No game data in database. Aborting.")
        return

    # Encoders
    enc_dow = LabelEncoder()
    enc_dow.fit(games["day_of_week"].fillna("Unknown"))

    enc_promo = LabelEncoder()
    enc_promo.fit(games["promo_event"].fillna("Regular"))

    # Features
    df = games.copy()
    df["dow_enc"] = enc_dow.transform(df["day_of_week"].fillna("Unknown"))
    df["promo_enc"] = enc_promo.transform(df["promo_event"].fillna("Regular"))
    df["month"] = pd.to_datetime(df["date"]).dt.month
    df["is_playoff"] = df["is_playoff"].astype(int)

    X = df[FEATURE_COLS].values
    y = df["total_estimated_revenue"].values.astype(float)

    # Train
    model = LinearRegression()
    model.fit(X, y)

    # Metrics
    preds = model.predict(X)
    ss_res = np.sum((y - preds) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2_train = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

    cv_scores = cross_val_score(model, X, y, cv=min(5, len(y)), scoring="r2")
    r2_cv = cv_scores.mean()

    print(f"  Train R-squared: {r2_train:.4f}")
    print(f"  CV R-squared:    {r2_cv:.4f}")
    print(f"  Coefficients:    {dict(zip(FEATURE_COLS, model.coef_))}")
    print(f"  Intercept:       {model.intercept_:.2f}")

    # Residual stats for confidence interval
    residuals = y - preds
    residual_std = np.std(residuals)

    # Save
    os.makedirs(config.MODELS_DIR, exist_ok=True)
    output_path = os.path.join(config.MODELS_DIR, "revenue_predictor.joblib")

    artifact = {
        "model": model,
        "encoders": {
            "day_of_week": enc_dow,
            "promo_event": enc_promo,
        },
        "feature_names": FEATURE_COLS,
        "residual_std": residual_std,
        "training_stats": {
            "mean_revenue": float(np.mean(y)),
            "mean_attendance": float(np.mean(df["attendance"])),
            "n_games": len(y),
        },
    }
    joblib.dump(artifact, output_path)
    print(f"\nSaved revenue model to {output_path}")


if __name__ == "__main__":
    train()
