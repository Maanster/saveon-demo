"""
Tool implementations for the Concession Intelligence Advisor.
Each function is callable by the Claude API tool_use flow.
"""
import sys
import os
import sqlite3
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config


# ---------------------------------------------------------------------------
# 1. query_database
# ---------------------------------------------------------------------------

def query_database(sql: str) -> dict:
    """
    Execute a read-only SQL query against the royals.db database.
    Only SELECT statements are allowed. Results limited to 100 rows.
    """
    sql_stripped = sql.strip().rstrip(";")

    # Safety: only allow SELECT
    if not sql_stripped.upper().startswith("SELECT"):
        return {"error": "Only SELECT queries are allowed."}

    # Block dangerous keywords
    blocked = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE", "ATTACH", "DETACH"]
    sql_upper = sql_stripped.upper()
    for word in blocked:
        if word in sql_upper.split():
            return {"error": f"Queries containing {word} are not allowed."}

    try:
        conn = sqlite3.connect(config.DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(sql_stripped + " LIMIT 100")
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = [list(row) for row in cursor.fetchall()]
        conn.close()
        return {"columns": columns, "rows": rows, "row_count": len(rows)}
    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# 2. get_forecast
# ---------------------------------------------------------------------------

def get_forecast(
    opponent: str,
    day_of_week: str,
    attendance: int,
    month: int = None,
    is_playoff: bool = False,
    promo_event: str = "Regular",
) -> dict:
    """
    Get ML-powered demand forecast for an upcoming game.
    Falls back to historical averages if models are not trained yet.
    """
    # Try ML predict module
    try:
        from ml import predict
        result = predict.get_demand_forecast(
            opponent=opponent,
            day_of_week=day_of_week,
            attendance=attendance,
            month=month,
            is_playoff=is_playoff,
            promo_event=promo_event,
        )
        return result
    except Exception:
        pass

    # Fallback: historical averages from DB
    try:
        conn = sqlite3.connect(config.DB_PATH)

        # Overall averages
        avg_row = conn.execute(
            "SELECT AVG(total_units) as avg_units, AVG(total_estimated_revenue) as avg_rev, "
            "AVG(units_per_cap) as avg_upc, AVG(revenue_per_cap) as avg_rpc, "
            "COUNT(*) as n_games FROM games"
        ).fetchone()

        # Per-category averages
        cat_rows = conn.execute(
            "SELECT t.category, ROUND(AVG(cat_total), 0) as avg_units "
            "FROM (SELECT date, category, SUM(qty) as cat_total FROM transactions GROUP BY date, category) t "
            "GROUP BY t.category ORDER BY avg_units DESC"
        ).fetchall()

        # Per-item averages (top 15)
        item_rows = conn.execute(
            "SELECT t.item, ROUND(AVG(item_total), 0) as avg_units "
            "FROM (SELECT date, item, SUM(qty) as item_total FROM transactions GROUP BY date, item) t "
            "GROUP BY t.item ORDER BY avg_units DESC LIMIT 15"
        ).fetchall()

        # Scale by attendance ratio
        avg_attendance = avg_row[4] if avg_row else 1
        if avg_attendance and avg_attendance > 0:
            # Get real average attendance
            real_avg = conn.execute("SELECT AVG(attendance) FROM games").fetchone()[0] or 2800
            scale = attendance / real_avg
        else:
            scale = 1.0

        conn.close()

        category_forecast = {row[0]: int(row[1] * scale) for row in cat_rows} if cat_rows else {}
        item_forecast = {row[0]: int(row[1] * scale) for row in item_rows} if item_rows else {}

        return {
            "source": "historical_averages",
            "note": "ML models not yet trained. Using scaled historical averages.",
            "inputs": {
                "opponent": opponent,
                "day_of_week": day_of_week,
                "attendance": attendance,
                "is_playoff": is_playoff,
                "promo_event": promo_event,
            },
            "predicted_total_units": int((avg_row[0] or 0) * scale),
            "predicted_total_revenue": round((avg_row[1] or 0) * scale, 2),
            "predicted_units_per_cap": round(avg_row[2] or 0, 2),
            "predicted_revenue_per_cap": round(avg_row[3] or 0, 2),
            "category_forecast": category_forecast,
            "item_forecast": item_forecast,
            "scale_factor": round(scale, 2),
        }

    except Exception as e:
        return {"error": f"Forecast failed: {str(e)}"}


# ---------------------------------------------------------------------------
# 3. get_game_summary
# ---------------------------------------------------------------------------

def get_game_summary(game_date: str) -> dict:
    """
    Get a complete summary of a specific game date with all KPIs.
    """
    try:
        conn = sqlite3.connect(config.DB_PATH)

        # Game info
        game = conn.execute(
            "SELECT * FROM games WHERE date = ?", (game_date,)
        ).fetchone()
        if not game:
            conn.close()
            return {"error": f"No game found for date {game_date}"}

        cols = [desc[0] for desc in conn.execute("SELECT * FROM games LIMIT 1").description]
        game_dict = dict(zip(cols, game))

        # Category breakdown
        cat_rows = conn.execute(
            "SELECT category, SUM(qty) as units, SUM(estimated_revenue) as revenue "
            "FROM transactions WHERE date = ? GROUP BY category ORDER BY revenue DESC",
            (game_date,),
        ).fetchall()
        categories = [
            {"category": r[0], "units": r[1], "revenue": round(r[2], 2)} for r in cat_rows
        ]

        # Stand breakdown
        stand_rows = conn.execute(
            "SELECT location, SUM(qty) as units, SUM(estimated_revenue) as revenue "
            "FROM transactions WHERE date = ? GROUP BY location ORDER BY revenue DESC",
            (game_date,),
        ).fetchall()
        stands = [
            {"stand": r[0], "units": r[1], "revenue": round(r[2], 2)} for r in stand_rows
        ]

        # Top items
        item_rows = conn.execute(
            "SELECT item, SUM(qty) as units, SUM(estimated_revenue) as revenue "
            "FROM transactions WHERE date = ? GROUP BY item ORDER BY units DESC LIMIT 10",
            (game_date,),
        ).fetchall()
        top_items = [
            {"item": r[0], "units": r[1], "revenue": round(r[2], 2)} for r in item_rows
        ]

        # Period breakdown
        period_rows = conn.execute(
            "SELECT game_period, SUM(qty) as units, SUM(estimated_revenue) as revenue "
            "FROM transactions WHERE date = ? GROUP BY game_period ORDER BY units DESC",
            (game_date,),
        ).fetchall()
        periods = [
            {"period": r[0], "units": r[1], "revenue": round(r[2], 2)} for r in period_rows
        ]

        conn.close()

        # Benchmark comparison
        attendance = game_dict.get("attendance", 0)
        revenue_per_cap = game_dict.get("revenue_per_cap", 0)
        whl_low, whl_high = 14.0, 16.0
        gap_low = round((whl_low - revenue_per_cap) * attendance, 2) if revenue_per_cap < whl_low else 0
        gap_high = round((whl_high - revenue_per_cap) * attendance, 2) if revenue_per_cap < whl_high else 0

        return {
            "game": game_dict,
            "categories": categories,
            "stands": stands,
            "top_items": top_items,
            "periods": periods,
            "benchmark": {
                "revenue_per_cap": round(revenue_per_cap, 2),
                "whl_benchmark_low": whl_low,
                "whl_benchmark_high": whl_high,
                "gap_this_game_low": gap_low,
                "gap_this_game_high": gap_high,
            },
        }

    except Exception as e:
        return {"error": f"Game summary failed: {str(e)}"}


# ---------------------------------------------------------------------------
# 4. get_prep_sheet
# ---------------------------------------------------------------------------

def get_prep_sheet(
    opponent: str,
    day_of_week: str,
    attendance: int,
    promo_event: str = "Regular",
) -> dict:
    """
    Generate a full game-day prep sheet with item quantities, stand assignments,
    staffing recommendations, and buffer percentages.
    """
    try:
        # Get demand forecast first
        forecast = get_forecast(
            opponent=opponent,
            day_of_week=day_of_week,
            attendance=attendance,
            is_playoff=False,
            promo_event=promo_event,
        )
        if "error" in forecast:
            return forecast

        # Determine stand configuration
        if attendance < 2000:
            rule_key = "under_2000"
        elif attendance < 3500:
            rule_key = "2000_to_3500"
        else:
            rule_key = "over_3500"

        stand_rules = config.STAND_OPENING_RULES[rule_key]
        open_stands = stand_rules["open_stands"]
        closed_stands = stand_rules["close_stands"]
        staff_per_stand = stand_rules["staff_per_stand"]

        # Determine buffer percentage from staffing rules
        if promo_event == "Playoff" or attendance >= 5000:
            buffer_pct = config.STAFFING_RULES["playoff"]["buffer_pct"]
            staff_per_stand = config.STAFFING_RULES["playoff"]["staff_per_stand"]
        elif attendance >= 3500:
            buffer_pct = config.STAFFING_RULES["high"]["buffer_pct"]
        elif attendance >= 2000:
            buffer_pct = config.STAFFING_RULES["medium"]["buffer_pct"]
        else:
            buffer_pct = config.STAFFING_RULES["low"]["buffer_pct"]

        # Get comparable games
        try:
            conn = sqlite3.connect(config.DB_PATH)
            comps = conn.execute(
                "SELECT date, opponent, attendance, total_units, total_estimated_revenue, "
                "units_per_cap, revenue_per_cap "
                "FROM games WHERE ABS(attendance - ?) < 800 AND day_of_week = ? "
                "ORDER BY ABS(attendance - ?) LIMIT 5",
                (attendance, day_of_week, attendance),
            ).fetchall()
            comp_cols = ["date", "opponent", "attendance", "total_units",
                         "total_estimated_revenue", "units_per_cap", "revenue_per_cap"]
            comparable_games = [dict(zip(comp_cols, row)) for row in comps]

            # Stand-level historical averages for allocation
            stand_share = conn.execute(
                "SELECT location, SUM(qty) as total_units "
                "FROM transactions GROUP BY location ORDER BY total_units DESC"
            ).fetchall()
            total_all_stands = sum(r[1] for r in stand_share) if stand_share else 1
            stand_pcts = {r[0]: r[1] / total_all_stands for r in stand_share}

            conn.close()
        except Exception:
            comparable_games = []
            stand_pcts = {}

        # Build item prep quantities (with buffer)
        item_forecast = forecast.get("item_forecast", {})
        item_prep = {}
        for item, qty in item_forecast.items():
            buffered = int(qty * (1 + buffer_pct))
            item_prep[item] = {"forecast": qty, "prep_qty": buffered}

        # Build stand assignments
        stand_assignments = []
        for stand in open_stands:
            share = stand_pcts.get(stand, 1 / len(open_stands))
            allocated_units = int(forecast.get("predicted_total_units", 0) * share)
            stand_assignments.append({
                "stand": stand,
                "historical_share": round(share * 100, 1),
                "allocated_units": allocated_units,
                "staff": staff_per_stand,
            })

        return {
            "game_params": {
                "opponent": opponent,
                "day_of_week": day_of_week,
                "expected_attendance": attendance,
                "promo_event": promo_event,
            },
            "stand_config": {
                "open": open_stands,
                "closed": closed_stands,
                "rule_applied": rule_key,
            },
            "staffing": {
                "staff_per_stand": staff_per_stand,
                "total_staff_needed": staff_per_stand * len(open_stands),
                "buffer_pct": buffer_pct,
            },
            "forecast_summary": {
                "predicted_total_units": forecast.get("predicted_total_units", 0),
                "predicted_total_revenue": forecast.get("predicted_total_revenue", 0),
                "source": forecast.get("source", "unknown"),
            },
            "item_prep": item_prep,
            "stand_assignments": stand_assignments,
            "comparable_games": comparable_games,
        }

    except Exception as e:
        return {"error": f"Prep sheet failed: {str(e)}"}


# ---------------------------------------------------------------------------
# 5. get_product_recommendations
# ---------------------------------------------------------------------------

def get_product_recommendations() -> dict:
    """
    Load affinity analysis results and return bundle/combo suggestions
    with estimated revenue impact.
    """
    affinity_path = os.path.join(config.MODELS_DIR, "affinity_rules.json")

    if os.path.exists(affinity_path):
        try:
            with open(affinity_path, "r") as f:
                rules = json.load(f)
            return {
                "source": "affinity_analysis",
                "suggested_bundles": rules.get("suggested_bundles", []),
                "top_item_pairs": rules.get("top_20_item_pairs", [])[:10],
                "top_category_pairs": rules.get("top_10_category_pairs", []),
                "metadata": rules.get("metadata", {}),
            }
        except Exception as e:
            return {"error": f"Failed to load affinity rules: {str(e)}"}

    # Fallback: generate basic recommendations from DB
    try:
        conn = sqlite3.connect(config.DB_PATH)

        # Top items by volume
        top_items = conn.execute(
            "SELECT item, category, SUM(qty) as total_units, "
            "ROUND(AVG(estimated_price), 2) as avg_price "
            "FROM transactions GROUP BY item ORDER BY total_units DESC LIMIT 10"
        ).fetchall()

        conn.close()

        # Generate simple bundle suggestions pairing beer with food
        beer_items = [r for r in top_items if r[1] == "Beer"]
        food_items = [r for r in top_items if r[1] == "Food"]

        bundles = []
        for b in beer_items[:3]:
            for f in food_items[:2]:
                combined = (b[3] or 8.0) + (f[3] or 6.0)
                bundles.append({
                    "name": f"{b[0]} + {f[0]}",
                    "items": [b[0], f[0]],
                    "individual_total": round(combined, 2),
                    "suggested_price": round(combined * 0.90, 2),
                    "savings": round(combined * 0.10, 2),
                    "estimated_annual_revenue": round(combined * 0.15 * 67, 2),
                    "rationale": "Beer + food cross-sell at Phillips Bar opportunity",
                })

        return {
            "source": "database_fallback",
            "note": "Affinity model not yet trained. Showing basic cross-sell suggestions.",
            "suggested_bundles": bundles[:6],
            "top_items_by_volume": [
                {"item": r[0], "category": r[1], "total_units": r[2], "avg_price": r[3]}
                for r in top_items
            ],
        }

    except Exception as e:
        return {"error": f"Recommendations failed: {str(e)}"}
