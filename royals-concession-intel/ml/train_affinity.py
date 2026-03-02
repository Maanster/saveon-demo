"""
Market-basket / affinity analysis on concession transactions.
Groups transactions into baskets by (date, hour, location), computes
co-occurrence lift scores, and outputs bundle suggestions.
"""
import sys, os, sqlite3, json, warnings
from collections import Counter
from itertools import combinations

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config


def _load_transactions():
    """Load transaction data from DB."""
    conn = sqlite3.connect(config.DB_PATH)
    df = pd.read_sql_query(
        "SELECT date, hour, location, item, category, qty, estimated_price FROM transactions",
        conn,
    )
    conn.close()
    return df


def _build_baskets(df):
    """
    Group transactions into basket proxies: each unique (date, hour, location)
    is treated as one basket. Returns list of sets of item names.
    """
    baskets = []
    grouped = df.groupby(["date", "hour", "location"])
    for _, group in grouped:
        items_in_basket = set(group["item"].dropna().unique())
        if len(items_in_basket) >= 2:
            baskets.append(items_in_basket)
    return baskets


def _compute_cooccurrence(baskets, min_support_count=3):
    """
    Compute co-occurrence counts and lift for item pairs.
    Returns DataFrame with item_a, item_b, count_a, count_b, count_ab, support, lift.
    """
    n_baskets = len(baskets)
    if n_baskets == 0:
        return pd.DataFrame()

    # Item frequencies
    item_counts = Counter()
    for b in baskets:
        for item in b:
            item_counts[item] += 1

    # Pair frequencies
    pair_counts = Counter()
    for b in baskets:
        items = sorted(b)
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                pair_counts[(items[i], items[j])] += 1

    # Build results
    rows = []
    for (a, b), count_ab in pair_counts.items():
        if count_ab < min_support_count:
            continue
        count_a = item_counts[a]
        count_b = item_counts[b]
        support = count_ab / n_baskets
        expected = (count_a / n_baskets) * (count_b / n_baskets)
        lift = support / expected if expected > 0 else 0
        rows.append({
            "item_a": a,
            "item_b": b,
            "count_a": count_a,
            "count_b": count_b,
            "count_ab": count_ab,
            "support": round(support, 4),
            "lift": round(lift, 4),
        })

    return pd.DataFrame(rows).sort_values("lift", ascending=False).reset_index(drop=True)


def _compute_category_pairs(df, baskets_df_raw):
    """Compute co-occurrence at the category level."""
    # Build category baskets
    grouped = baskets_df_raw.groupby(["date", "hour", "location"])
    cat_baskets = []
    for _, group in grouped:
        cats = set(group["category"].dropna().unique())
        if len(cats) >= 2:
            cat_baskets.append(cats)

    n = len(cat_baskets)
    if n == 0:
        return []

    cat_counts = Counter()
    pair_counts = Counter()
    for b in cat_baskets:
        for c in b:
            cat_counts[c] += 1
        for a, b_item in combinations(sorted(b), 2):
            pair_counts[(a, b_item)] += 1

    rows = []
    for (a, b), count_ab in pair_counts.items():
        support = count_ab / n
        expected = (cat_counts[a] / n) * (cat_counts[b] / n)
        lift = support / expected if expected > 0 else 0
        rows.append({
            "category_a": a,
            "category_b": b,
            "count_ab": count_ab,
            "support": round(support, 4),
            "lift": round(lift, 4),
        })

    return sorted(rows, key=lambda x: x["lift"], reverse=True)[:10]


def _generate_bundles(pair_df, df):
    """
    Generate bundle suggestions from high-lift item pairs.
    """
    if pair_df.empty:
        return []

    # Average prices per item
    avg_prices = df.groupby("item")["estimated_price"].mean().to_dict()

    # Total games for annual projection
    n_games = df["date"].nunique()
    games_per_season = max(n_games, 30)

    bundles = []
    seen_items = set()
    top_pairs = pair_df.head(30)

    for _, row in top_pairs.iterrows():
        a, b = row["item_a"], row["item_b"]
        if a in seen_items or b in seen_items:
            continue

        price_a = avg_prices.get(a, 5.0)
        price_b = avg_prices.get(b, 5.0)
        combined = price_a + price_b
        suggested_price = round(combined * 0.90, 2)  # 10% bundle discount
        savings = round(combined - suggested_price, 2)

        # Estimate incremental revenue: assume bundle increases purchase rate by 15%
        avg_daily_pairs = row["count_ab"] / max(n_games, 1)
        incremental_units = avg_daily_pairs * 0.15
        annual_incremental_revenue = round(incremental_units * suggested_price * games_per_season, 2)

        bundle_name = f"{a} + {b}"
        bundles.append({
            "name": bundle_name,
            "items": [a, b],
            "individual_total": round(combined, 2),
            "suggested_price": suggested_price,
            "savings": savings,
            "lift": row["lift"],
            "support": row["support"],
            "estimated_annual_revenue": annual_incremental_revenue,
        })
        seen_items.update([a, b])

        if len(bundles) >= 8:
            break

    return bundles


def train():
    """Main affinity analysis pipeline."""
    print("Loading transactions...")
    df = _load_transactions()

    if len(df) == 0:
        print("ERROR: No transaction data. Aborting.")
        return

    print(f"  {len(df):,} transaction rows loaded")

    # Build item-level baskets
    print("Building baskets...")
    baskets = _build_baskets(df)
    print(f"  {len(baskets):,} baskets (date x hour x location)")

    # Item pair co-occurrence
    print("Computing item co-occurrence and lift...")
    pair_df = _compute_cooccurrence(baskets, min_support_count=3)
    print(f"  {len(pair_df):,} item pairs above min support")

    # Category pairs
    print("Computing category co-occurrence...")
    cat_pairs = _compute_category_pairs(df, df)

    # Top 20 item pairs
    top_item_pairs = []
    if not pair_df.empty:
        for _, row in pair_df.head(20).iterrows():
            top_item_pairs.append({
                "item_a": row["item_a"],
                "item_b": row["item_b"],
                "lift": row["lift"],
                "support": row["support"],
                "count_ab": int(row["count_ab"]),
            })

    # Bundle suggestions
    print("Generating bundle suggestions...")
    bundles = _generate_bundles(pair_df, df)

    # Save
    os.makedirs(config.MODELS_DIR, exist_ok=True)
    output_path = os.path.join(config.MODELS_DIR, "affinity_rules.json")

    result = {
        "top_20_item_pairs": top_item_pairs,
        "top_10_category_pairs": cat_pairs,
        "suggested_bundles": bundles,
        "metadata": {
            "n_baskets": len(baskets),
            "n_transactions": len(df),
            "n_unique_items": int(df["item"].nunique()),
        },
    }

    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\nSaved affinity rules to {output_path}")
    print(f"  Top item pairs:    {len(top_item_pairs)}")
    print(f"  Category pairs:    {len(cat_pairs)}")
    print(f"  Bundle suggestions: {len(bundles)}")

    if bundles:
        print("\nSuggested bundles:")
        for b in bundles:
            print(f"  {b['name']:40s}  ${b['suggested_price']:6.2f}  (lift={b['lift']:.2f})")


if __name__ == "__main__":
    train()
