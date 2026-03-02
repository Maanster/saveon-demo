"""
Data loader for Royals Concession Intelligence Platform.
Reads CSV files, enriches rows, and populates SQLite database.
"""
import sys
import os
import csv
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    DB_PATH, DATA_DIR, CSV_FILES, KNOWN_PRICES,
    GAME_PERIODS, ALL_GAMES, CATEGORY_PRICES,
)
from data_foundation.price_lookup import get_price

# Map raw CSV categories to standardized categories
RAW_CATEGORY_MAP = {
    "Beer": "Beer",
    "Liquor": "Cocktail",
    "Wine": "Wine",
    "NA Bev": "NA Bev",
    "NA Bev PST Exempt": "NA Bev",
    "Food": "Food",
    "Food - Walking Taco": "Food",
    "Snack": "Snacks",
    "Snacks": "Snacks",
    "Sweets": "Snacks",
    "Extras": "Other",
    "None": "Other",
    '"Wine': "Wine",  # Handle possible quoting artifact
}

# Map raw CSV item names to our KNOWN_PRICES item names
RAW_ITEM_MAP = {
    "Draft Beer": "Tap Beer",
    "Draught Beer": "Tap Beer",
    "Cans of Beer": "Can Beer",
    "Dogs": "Hot Dog",
    "Hot Dog": "Hot Dog",
    "Pizza Slice": "Pizza Slice",
    "Pretzel": "Pretzel",
    "Popcorn": "Popcorn",
    "Fries": "Fries",
    "Sweet Potato Fries": "Fries",
    "Tacos": "Taco",
    "Walking Taco": "Taco",
    "Chicken Tenders": "Chicken Strips",
    "Burgers": "Cheeseburger",
    "Crispy Chicken Burger": "Cheeseburger",
    "Candy": "Candy",
    "Chips": "Chips",
    "Gummies": "Candy",
    "Cookies & Brownies": "Candy",
    "Cotton Candy": "Candy",
    "Bottle Pop": "Bottle Pop",
    "Water": "Water",
    "Hot Drinks": "Hot Beverage",
    "Non-Alcoholic Beverages": "Fountain Pop",
    "Other Beverages": "Fountain Pop",
    "Boozy Coffee": "Cocktail",
    "Coffee & Baileys": "Cocktail",
    "Tequila Slushy": "Cocktail",
    "Virgin Slushy": "Fountain Pop",
    "Churro": "Candy",
    "Paletas": "Candy",
    "Jalapeno Poppers": "Nachos",
    "Panini": "Cheeseburger",
    "Hot Pressed Sandwich": "Cheeseburger",
    "Sides": "Fries",
    "Extras": "Candy",
    "COMBOS": "Nachos",
    "50/50 Ticket": "50/50 Ticket",
    "Cider & Coolers\"": "Can Beer",
}


def classify_game_period(hour, minute):
    """Determine game period from hour and minute."""
    for period, (h1, m1, h2, m2) in GAME_PERIODS.items():
        time_val = hour * 60 + minute
        start_val = h1 * 60 + m1
        end_val = h2 * 60 + m2
        if start_val <= time_val <= end_val:
            return period
    return "other"


def determine_season(date_str):
    """Season 1 = before 2025-09-01, Season 2 = on or after 2025-09-01."""
    return 1 if date_str < "2025-09-01" else 2


def load_all_data():
    """Load all CSV data into SQLite database, create games table, compute metrics."""
    # Ensure db directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Remove existing DB for clean rebuild
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # --- Create transactions table ---
    cur.execute("""
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time TEXT,
            category TEXT,
            item TEXT,
            qty INTEGER,
            price_point_name TEXT,
            location TEXT,
            estimated_price REAL,
            estimated_revenue REAL,
            hour INTEGER,
            minute INTEGER,
            game_period TEXT,
            season INTEGER
        )
    """)

    # --- Create games table ---
    cur.execute("""
        CREATE TABLE games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            opponent TEXT,
            day_of_week TEXT,
            attendance INTEGER,
            season INTEGER,
            is_playoff INTEGER,
            promo_event TEXT,
            note TEXT,
            total_units INTEGER DEFAULT 0,
            total_transactions INTEGER DEFAULT 0,
            total_estimated_revenue REAL DEFAULT 0.0,
            units_per_cap REAL DEFAULT 0.0,
            revenue_per_cap REAL DEFAULT 0.0
        )
    """)

    # --- Create price_lookup table ---
    cur.execute("""
        CREATE TABLE price_lookup (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT,
            price_point_name TEXT,
            price REAL
        )
    """)

    # --- Populate games from config ---
    for g in ALL_GAMES:
        note = g.get("note", "")
        if "$1 Dog" in note:
            promo_event = "Dollar Dog Night"
        elif g["playoff"]:
            promo_event = "Playoff"
        else:
            promo_event = "Regular"

        cur.execute("""
            INSERT INTO games (date, opponent, day_of_week, attendance, season,
                               is_playoff, promo_event, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            g["date"], g["team"], g["day"], g["attendance"],
            g["season"], int(g["playoff"]), promo_event, note,
        ))

    # --- Populate price_lookup table ---
    for (item, ppn), price in KNOWN_PRICES.items():
        cur.execute(
            "INSERT INTO price_lookup (item, price_point_name, price) VALUES (?, ?, ?)",
            (item, ppn, price),
        )

    # --- Load CSV files into transactions ---
    total_rows = 0
    skipped_rows = 0

    for csv_file in CSV_FILES:
        csv_path = os.path.join(DATA_DIR, csv_file)
        if not os.path.exists(csv_path):
            print(f"  WARNING: {csv_file} not found, skipping.")
            continue

        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            batch = []
            for row in reader:
                date_str = row.get("Date", "").strip()
                time_str = row.get("Time", "").strip()
                raw_category = row.get("Category", "").strip()
                raw_item = row.get("Item", "").strip()
                qty_str = row.get("Qty", "0").strip()
                price_point_name = row.get("Price Point Name", "").strip()
                location = row.get("Location", "").strip()

                # Skip header-like or empty rows
                if not date_str or date_str == "Date":
                    skipped_rows += 1
                    continue

                # Parse qty
                try:
                    qty = int(float(qty_str))
                except (ValueError, TypeError):
                    qty = 1

                if qty <= 0:
                    skipped_rows += 1
                    continue

                # Map category
                category = RAW_CATEGORY_MAP.get(raw_category, "Other")

                # Map item name
                mapped_item = RAW_ITEM_MAP.get(raw_item, raw_item)

                # Get price
                estimated_price = get_price(mapped_item, price_point_name, category)
                estimated_revenue = estimated_price * qty

                # Parse time
                try:
                    parts = time_str.split(":")
                    hour = int(parts[0])
                    minute = int(parts[1])
                except (ValueError, IndexError):
                    hour = 0
                    minute = 0

                # Game period
                game_period = classify_game_period(hour, minute)

                # Season
                season = determine_season(date_str)

                batch.append((
                    date_str, time_str, category, mapped_item, qty,
                    price_point_name, location, estimated_price,
                    estimated_revenue, hour, minute, game_period, season,
                ))

            if batch:
                cur.executemany("""
                    INSERT INTO transactions (date, time, category, item, qty,
                        price_point_name, location, estimated_price,
                        estimated_revenue, hour, minute, game_period, season)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, batch)
                total_rows += len(batch)

        print(f"  Loaded {csv_file}: {len(batch) if batch else 0} rows")

    conn.commit()

    # --- Update games with computed metrics ---
    cur.execute("""
        UPDATE games SET
            total_units = COALESCE((
                SELECT SUM(t.qty) FROM transactions t WHERE t.date = games.date
            ), 0),
            total_transactions = COALESCE((
                SELECT COUNT(*) FROM transactions t WHERE t.date = games.date
            ), 0),
            total_estimated_revenue = COALESCE((
                SELECT SUM(t.estimated_revenue) FROM transactions t WHERE t.date = games.date
            ), 0.0)
    """)
    cur.execute("""
        UPDATE games SET
            units_per_cap = CASE WHEN attendance > 0 THEN ROUND(1.0 * total_units / attendance, 2) ELSE 0.0 END,
            revenue_per_cap = CASE WHEN attendance > 0 THEN ROUND(total_estimated_revenue / attendance, 2) ELSE 0.0 END
    """)
    conn.commit()

    # --- Create indexes ---
    cur.execute("CREATE INDEX idx_transactions_date ON transactions(date)")
    cur.execute("CREATE INDEX idx_transactions_category ON transactions(category)")
    cur.execute("CREATE INDEX idx_transactions_location ON transactions(location)")
    cur.execute("CREATE INDEX idx_transactions_game_period ON transactions(game_period)")
    cur.execute("CREATE INDEX idx_games_date ON games(date)")
    conn.commit()

    # --- Gather summary stats ---
    games_count = cur.execute("SELECT COUNT(*) FROM games").fetchone()[0]
    games_with_data = cur.execute(
        "SELECT COUNT(*) FROM games WHERE total_transactions > 0"
    ).fetchone()[0]
    total_revenue = cur.execute(
        "SELECT COALESCE(SUM(estimated_revenue), 0) FROM transactions"
    ).fetchone()[0]

    conn.close()

    stats = {
        "total_rows": total_rows,
        "skipped_rows": skipped_rows,
        "games_count": games_count,
        "games_with_data": games_with_data,
        "total_revenue": total_revenue,
        "db_path": DB_PATH,
    }
    return stats
