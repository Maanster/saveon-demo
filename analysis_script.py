#!/usr/bin/env python3
"""
Victoria Royals - Comprehensive Data Science Analysis
Hockey Hackathon - POS Transaction Analysis
"""

import csv
import os
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import json
import math

# ============================================================================
# DATA LOADING
# ============================================================================

DATA_DIR = "/Users/chete/Library/CloudStorage/GoogleDrive-gabriel@gvlnetworks.com/My Drive/Hackaton - Hockey/data/"

CSV_FILES = [
    "items-2024-09-19-2024-10-01.csv",
    "items-2024-10-01-2024-11-01.csv",
    "items-2024-11-01-2024-12-01.csv",
    "items-2024-12-01-2025-01-01.csv",
    "items-2025-01-01-2025-02-01.csv",
    "items-2025-02-01-2025-03-01.csv",
    "items-2025-03-01-2025-04-01.csv",
    "items-2025-04-01-2025-05-01.csv",
    "items-2025-09-01-2025-10-01.csv",
    "items-2025-10-01-2025-11-01.csv",
    "items-2025-11-01-2025-12-01.csv",
    "items-2025-12-01-2026-01-01.csv",
    "items-2026-01-01-2026-02-01.csv",
    "items-2026-02-01-2026-02-21.csv",
]

# Game details
SEASON1_GAMES = [
    {"team": "Tri-City", "day": "Fri", "date": "2024-09-20", "attendance": 4218, "playoff": False},
    {"team": "Tri-City", "day": "Sat", "date": "2024-09-21", "attendance": 2030, "playoff": False},
    {"team": "Wenatchee", "day": "Fri", "date": "2024-10-11", "attendance": 2156, "playoff": False},
    {"team": "Wenatchee", "day": "Sat", "date": "2024-10-12", "attendance": 2164, "playoff": False},
    {"team": "Prince Albert", "day": "Fri", "date": "2024-10-18", "attendance": 3114, "playoff": False},
    {"team": "Moose Jaw", "day": "Fri", "date": "2024-11-01", "attendance": 3048, "playoff": False},
    {"team": "Saskatoon", "day": "Sun", "date": "2024-11-03", "attendance": 3421, "playoff": False},
    {"team": "Kamloops", "day": "Tue", "date": "2024-11-05", "attendance": 1310, "playoff": False},
    {"team": "Kamloops", "day": "Wed", "date": "2024-11-06", "attendance": 1477, "playoff": False},
    {"team": "Seattle", "day": "Fri", "date": "2024-11-29", "attendance": 2842, "playoff": False},
    {"team": "Seattle", "day": "Sat", "date": "2024-11-30", "attendance": 2340, "playoff": False},
    {"team": "Regina", "day": "Tue", "date": "2024-12-03", "attendance": 1491, "playoff": False},
    {"team": "Kelowna", "day": "Sat", "date": "2024-12-07", "attendance": 1835, "playoff": False},
    {"team": "Kelowna", "day": "Sun", "date": "2024-12-08", "attendance": 3558, "playoff": False},
    {"team": "Vancouver", "day": "Fri", "date": "2024-12-13", "attendance": 2726, "playoff": False},
    {"team": "Prince George", "day": "Fri", "date": "2024-12-27", "attendance": 2409, "playoff": False},
    {"team": "Prince George", "day": "Sat", "date": "2024-12-28", "attendance": 3085, "playoff": False},
    {"team": "Vancouver", "day": "Tue", "date": "2024-12-31", "attendance": 2939, "playoff": False},
    {"team": "Everett", "day": "Fri", "date": "2025-01-03", "attendance": 3367, "playoff": False},
    {"team": "Brandon", "day": "Wed", "date": "2025-01-15", "attendance": 2166, "playoff": False},
    {"team": "Kamloops", "day": "Fri", "date": "2025-01-17", "attendance": 2567, "playoff": False},
    {"team": "Kamloops", "day": "Sat", "date": "2025-01-18", "attendance": 2913, "playoff": False},
    {"team": "SWC", "day": "Sat", "date": "2025-01-25", "attendance": 3333, "playoff": False},
    {"team": "Kelowna", "day": "Tue", "date": "2025-02-04", "attendance": 1245, "playoff": False},
    {"team": "Kelowna", "day": "Wed", "date": "2025-02-05", "attendance": 1522, "playoff": False},
    {"team": "Vancouver", "day": "Fri", "date": "2025-02-14", "attendance": 3252, "playoff": False},
    {"team": "Everett", "day": "Mon", "date": "2025-02-17", "attendance": 3897, "playoff": False},
    {"team": "Prince George", "day": "Fri", "date": "2025-02-21", "attendance": 2754, "playoff": False},
    {"team": "Prince George", "day": "Sat", "date": "2025-02-22", "attendance": 2946, "playoff": False},
    {"team": "Portland", "day": "Fri", "date": "2025-02-28", "attendance": 2696, "playoff": False},
    {"team": "Portland", "day": "Sat", "date": "2025-03-01", "attendance": 3215, "playoff": False},
    {"team": "Spokane", "day": "Fri", "date": "2025-03-07", "attendance": 3015, "playoff": False},
    {"team": "Spokane", "day": "Sat", "date": "2025-03-08", "attendance": 3606, "playoff": False},
    {"team": "Vancouver", "day": "Fri", "date": "2025-03-14", "attendance": 4942, "playoff": False},
    {"team": "Tri-City", "day": "Fri", "date": "2025-03-28", "attendance": 3977, "playoff": False},
    {"team": "Tri-City", "day": "Sat", "date": "2025-03-29", "attendance": 4466, "playoff": False},
    {"team": "Spokane", "day": "Wed", "date": "2025-04-16", "attendance": 3670, "playoff": True},
    {"team": "Spokane", "day": "Fri", "date": "2025-04-18", "attendance": 5540, "playoff": True},
    {"team": "Spokane", "day": "Sat", "date": "2025-04-19", "attendance": 3361, "playoff": True},
]

SEASON2_GAMES = [
    {"team": "Penticton", "day": "Fri", "date": "2025-09-19", "attendance": 3527, "playoff": False, "note": ""},
    {"team": "Vancouver", "day": "Sat", "date": "2025-09-27", "attendance": 2247, "playoff": False, "note": ""},
    {"team": "Everett", "day": "Fri", "date": "2025-10-10", "attendance": 2075, "playoff": False, "note": ""},
    {"team": "Everett", "day": "Sat", "date": "2025-10-11", "attendance": 2104, "playoff": False, "note": ""},
    {"team": "Medicine Hat", "day": "Sat", "date": "2025-10-18", "attendance": 2861, "playoff": False, "note": ""},
    {"team": "Kelowna", "day": "Wed", "date": "2025-10-22", "attendance": 2245, "playoff": False, "note": "$1 Dog Night"},
    {"team": "Penticton", "day": "Sat", "date": "2025-11-01", "attendance": 1575, "playoff": False, "note": ""},
    {"team": "Penticton", "day": "Sun", "date": "2025-11-02", "attendance": 1846, "playoff": False, "note": ""},
    {"team": "Kelowna", "day": "Fri", "date": "2025-11-07", "attendance": 2387, "playoff": False, "note": ""},
    {"team": "Kelowna", "day": "Sat", "date": "2025-11-08", "attendance": 2043, "playoff": False, "note": ""},
    {"team": "Edmonton", "day": "Fri", "date": "2025-11-14", "attendance": 2896, "playoff": False, "note": ""},
    {"team": "Lethbridge", "day": "Tue", "date": "2025-11-18", "attendance": 1901, "playoff": False, "note": ""},
    {"team": "Seattle", "day": "Fri", "date": "2025-11-28", "attendance": 3161, "playoff": False, "note": ""},
    {"team": "Seattle", "day": "Sun", "date": "2025-11-30", "attendance": 2455, "playoff": False, "note": ""},
    {"team": "Prince George", "day": "Fri", "date": "2025-12-05", "attendance": 2161, "playoff": False, "note": ""},
    {"team": "Prince George", "day": "Sun", "date": "2025-12-07", "attendance": 1870, "playoff": False, "note": ""},
    {"team": "Vancouver", "day": "Fri", "date": "2025-12-12", "attendance": 3808, "playoff": False, "note": ""},
    {"team": "Vancouver", "day": "Thu", "date": "2025-12-18", "attendance": 1968, "playoff": False, "note": ""},
    {"team": "Calgary", "day": "Thu", "date": "2026-01-01", "attendance": 2989, "playoff": False, "note": ""},
    {"team": "TriCity", "day": "Sat", "date": "2026-01-03", "attendance": 2347, "playoff": False, "note": ""},
    {"team": "TriCity", "day": "Sun", "date": "2026-01-04", "attendance": 2295, "playoff": False, "note": ""},
    {"team": "Spokane", "day": "Fri", "date": "2026-01-09", "attendance": 2573, "playoff": False, "note": ""},
    {"team": "Spokane", "day": "Sat", "date": "2026-01-10", "attendance": 2804, "playoff": False, "note": ""},
    {"team": "Red Deer", "day": "Sat", "date": "2026-01-31", "attendance": 4217, "playoff": False, "note": ""},
    {"team": "Kamloops", "day": "Tue", "date": "2026-02-03", "attendance": 1883, "playoff": False, "note": ""},
    {"team": "Kamloops", "day": "Wed", "date": "2026-02-04", "attendance": 1613, "playoff": False, "note": ""},
    {"team": "Wenatchee", "day": "Fri", "date": "2026-02-20", "attendance": 2419, "playoff": False, "note": ""},
    {"team": "Wenatchee", "day": "Sat", "date": "2026-02-21", "attendance": 3167, "playoff": False, "note": ""},
]

ALL_GAMES = []
for g in SEASON1_GAMES:
    g2 = dict(g)
    g2["season"] = 1
    if "note" not in g2:
        g2["note"] = ""
    ALL_GAMES.append(g2)
for g in SEASON2_GAMES:
    g2 = dict(g)
    g2["season"] = 2
    ALL_GAMES.append(g2)

# Build game date lookup
game_date_lookup = {}
for g in ALL_GAMES:
    game_date_lookup[g["date"]] = g

print(f"Total games loaded: {len(ALL_GAMES)}")
print(f"Season 1 games: {len(SEASON1_GAMES)}")
print(f"Season 2 games: {len(SEASON2_GAMES)}")

# Load all CSV data
all_rows = []
file_counts = {}

for fname in CSV_FILES:
    fpath = os.path.join(DATA_DIR, fname)
    count = 0
    with open(fpath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['Qty'] = int(row['Qty']) if row['Qty'] else 0
            all_rows.append(row)
            count += 1
    file_counts[fname] = count
    print(f"  Loaded {fname}: {count} rows")

print(f"\nTotal rows loaded: {len(all_rows)}")

# ============================================================================
# DATA QUALITY ASSESSMENT
# ============================================================================
print("\n=== DATA QUALITY ASSESSMENT ===")

# Negative quantities (refunds)
neg_qty = [r for r in all_rows if r['Qty'] < 0]
print(f"Negative Qty records (refunds/voids): {len(neg_qty)}")
neg_qty_dist = Counter(r['Qty'] for r in neg_qty)
print(f"  Qty distribution: {dict(sorted(neg_qty_dist.items()))}")

# Blank Price Point Name
blank_ppn = [r for r in all_rows if not r['Price Point Name'].strip()]
print(f"Blank 'Price Point Name' records: {len(blank_ppn)}")

# Qty distribution
qty_dist = Counter(r['Qty'] for r in all_rows)
print(f"Qty value range: {min(qty_dist.keys())} to {max(qty_dist.keys())}")
print(f"Qty distribution (top 10): {dict(sorted(qty_dist.items(), key=lambda x: -x[1])[:10])}")

# Unique values
unique_cats = sorted(set(r['Category'] for r in all_rows))
unique_items = sorted(set(r['Item'] for r in all_rows))
unique_locs = sorted(set(r['Location'] for r in all_rows))
unique_dates = sorted(set(r['Date'] for r in all_rows))

print(f"\nUnique Categories: {len(unique_cats)}")
for c in unique_cats:
    print(f"  - {c}")
print(f"\nUnique Items: {len(unique_items)}")
for i in unique_items:
    print(f"  - {i}")
print(f"\nUnique Locations: {len(unique_locs)}")
for l in unique_locs:
    print(f"  - {l}")
print(f"\nUnique Dates: {len(unique_dates)}")

# Dates that match game days
game_dates_set = set(g["date"] for g in ALL_GAMES)
data_dates_set = set(r['Date'] for r in all_rows)
matched_dates = game_dates_set & data_dates_set
non_game_dates = data_dates_set - game_dates_set
print(f"\nDates matching game days: {len(matched_dates)}")
print(f"Non-game dates in data: {len(non_game_dates)}")
if non_game_dates:
    for d in sorted(non_game_dates):
        count_d = sum(1 for r in all_rows if r['Date'] == d)
        print(f"  {d}: {count_d} transactions")

# ============================================================================
# FOUNDATIONAL METRICS
# ============================================================================
print("\n\n=== FOUNDATIONAL METRICS ===")

# Filter to positive quantities for most analyses
pos_rows = [r for r in all_rows if r['Qty'] > 0]
total_units_pos = sum(r['Qty'] for r in pos_rows)
print(f"Total units sold (positive Qty): {total_units_pos}")

# 1. Total units by category
print("\n--- Units by Category ---")
cat_units = defaultdict(int)
cat_txns = defaultdict(int)
for r in pos_rows:
    cat_units[r['Category']] += r['Qty']
    cat_txns[r['Category']] += 1

for cat, units in sorted(cat_units.items(), key=lambda x: -x[1]):
    pct = units / total_units_pos * 100
    print(f"  {cat}: {units:,} units ({pct:.1f}%) [{cat_txns[cat]:,} transactions]")

# 2. Total units by location
print("\n--- Units by Location ---")
loc_units = defaultdict(int)
loc_txns = defaultdict(int)
for r in pos_rows:
    loc_units[r['Location']] += r['Qty']
    loc_txns[r['Location']] += 1

for loc, units in sorted(loc_units.items(), key=lambda x: -x[1]):
    pct = units / total_units_pos * 100
    print(f"  {loc}: {units:,} units ({pct:.1f}%) [{loc_txns[loc]:,} transactions]")

# 3. Total units by item
print("\n--- Top 30 Items by Volume ---")
item_units = defaultdict(int)
item_txns = defaultdict(int)
for r in pos_rows:
    item_units[r['Item']] += r['Qty']
    item_txns[r['Item']] += 1

for i, (item, units) in enumerate(sorted(item_units.items(), key=lambda x: -x[1])[:30]):
    pct = units / total_units_pos * 100
    print(f"  {i+1}. {item}: {units:,} units ({pct:.1f}%) [{item_txns[item]:,} txns]")

# Bottom 20 items
print("\n--- Bottom 20 Items (Menu Simplification Candidates) ---")
for i, (item, units) in enumerate(sorted(item_units.items(), key=lambda x: x[1])[:20]):
    print(f"  {i+1}. {item}: {units:,} units [{item_txns[item]:,} txns]")

# 4. Per-game analysis
print("\n--- Per-Game Unit Volumes ---")
game_units = defaultdict(int)
game_txns = defaultdict(int)
for r in pos_rows:
    if r['Date'] in game_date_lookup:
        game_units[r['Date']] += r['Qty']
        game_txns[r['Date']] += 1

total_game_units = sum(game_units.values())
total_game_txns = sum(game_txns.values())
print(f"Total units on game days: {total_game_units:,}")
print(f"Total transactions on game days: {total_game_txns:,}")
print(f"Total units on non-game days: {total_units_pos - total_game_units:,}")

# Per-game details
print("\n  Date       | Day | Team          | Attend | Units | Txns  | Units/Cap | Txns/Cap")
print("  " + "-"*90)
per_game_data = []
for g in sorted(ALL_GAMES, key=lambda x: x['date']):
    d = g['date']
    units = game_units.get(d, 0)
    txns = game_txns.get(d, 0)
    att = g['attendance']
    upc = units / att if att > 0 else 0
    tpc = txns / att if att > 0 else 0
    playoff_str = " [P]" if g.get('playoff', False) else ""
    note_str = f" [{g['note']}]" if g.get('note', '') else ""
    print(f"  {d} | {g['day']:3s} | {g['team']:13s} | {att:5d} | {units:5d} | {txns:5d} | {upc:9.2f} | {tpc:.2f}{playoff_str}{note_str}")
    per_game_data.append({
        "date": d, "day": g["day"], "team": g["team"], "attendance": att,
        "units": units, "txns": txns, "upc": upc, "tpc": tpc,
        "season": g["season"], "playoff": g.get("playoff", False),
        "note": g.get("note", "")
    })

# Summary stats
if per_game_data:
    upcs = [g['upc'] for g in per_game_data if g['units'] > 0]
    tpcs = [g['tpc'] for g in per_game_data if g['txns'] > 0]
    atts = [g['attendance'] for g in per_game_data]
    units_list = [g['units'] for g in per_game_data if g['units'] > 0]

    print(f"\n  Summary Statistics:")
    print(f"    Avg units/game: {sum(units_list)/len(units_list):.0f}")
    print(f"    Avg units/cap: {sum(upcs)/len(upcs):.2f}")
    print(f"    Min units/cap: {min(upcs):.2f}, Max: {max(upcs):.2f}")
    print(f"    Avg txns/cap: {sum(tpcs)/len(tpcs):.2f}")
    print(f"    Avg attendance: {sum(atts)/len(atts):.0f}")

# ============================================================================
# ESTIMATED REVENUE
# ============================================================================
print("\n\n=== ESTIMATED REVENUE ===")

# Price mapping based on known prices and category/item inference
# We'll build a price lookup based on Price Point Name and Item
price_map = {}

# Collect all unique Price Point Names and their categories
ppn_cat = defaultdict(set)
for r in pos_rows:
    if r['Price Point Name'].strip():
        ppn_cat[r['Price Point Name']].add(r['Category'])

# Known pricing from menu photos
KNOWN_PRICES = {
    # Beer - cans typically $8-10
    "Budweiser": 8.49, "Bud Light": 8.49, "Michelob Ultra": 8.49,
    "Corona": 8.49, "Coors Light": 8.49, "Coors Original": 8.49,
    # Craft beer
    "Phillips": 9.49, "Stanley Park Amber": 9.49, "Stanley Park Pale Ale 12oz": 9.49,
    "Stanley Park Hazy 12oz": 9.49, "Stanley Park Pilsner 12oz": 9.49,
    "Stanley Park Amber 24oz": 13.99, "Stanley Park Hazy 24oz": 13.99,
    "Stanley Park Pilsner 24oz": 13.99, "Stanley Park Pale Ale 24oz": 13.99,
    # Cocktails / Coolers
    "Nutrl": 9.99, "Nutrl Cherry": 9.99, "Nutrl Mango": 9.99,
    "Ward's Cider": 9.99, "Mike's Hard Lemonade": 9.99,
    "Tempo Mango Peach": 9.99, "Mott's Caesar": 9.99,
    "Ole Margarita": 9.99, "Strait & Narrow": 9.99,
    # Non-alc
    "Aquafina 591ml": 3.99, "Aquafina": 3.99,
    # Pop
    "Pepsi": 4.99, "Diet Pepsi": 4.99, "7-Up": 4.99, "Mug Root Beer": 4.99,
    "Dr. Pepper": 4.99, "Ginger Ale": 4.99,
    # Other
    "Iced Tea": 4.99, "Lemonade": 4.99,
    "Pretzel": 5.99,
    "Coffee": 3.99, "Tea": 3.99, "Hot Chocolate": 3.99,
    "Fries": 6.99,
    "Regular": 5.99,  # for Popcorn, Churro etc
}

# Category-level average price estimates
CATEGORY_PRICES = {
    "Beer": 9.00,
    "Wine, Cider & Coolers": 9.99,
    "Liquor": 10.99,
    "Food": 7.99,
    "Snacks": 5.49,
    "Sweets": 5.49,
    "NA Bev": 4.99,
    "NA Bev PST Exempt": 3.99,
    "Merch": 25.00,
}

# Estimate revenue per game
def estimate_price(row):
    ppn = row['Price Point Name'].strip()
    cat = row['Category']
    item = row['Item']

    # Check specific price point name
    if ppn in KNOWN_PRICES:
        return KNOWN_PRICES[ppn]

    # Check partial matches
    for k, v in KNOWN_PRICES.items():
        if k.lower() in ppn.lower() or ppn.lower() in k.lower():
            return v

    # Check item name
    if item in KNOWN_PRICES:
        return KNOWN_PRICES[item]

    # Fall back to category
    return CATEGORY_PRICES.get(cat, 7.00)

game_revenue = defaultdict(float)
game_cat_revenue = defaultdict(lambda: defaultdict(float))
total_est_revenue = 0.0

for r in pos_rows:
    price = estimate_price(r)
    rev = price * r['Qty']
    total_est_revenue += rev
    if r['Date'] in game_date_lookup:
        game_revenue[r['Date']] += rev
        game_cat_revenue[r['Date']][r['Category']] += rev

print(f"Total estimated revenue (all days): ${total_est_revenue:,.2f}")
total_game_rev = sum(game_revenue.values())
print(f"Total estimated revenue (game days): ${total_game_rev:,.2f}")

print("\n  Per-Game Revenue Estimates:")
print(f"  {'Date':<12} {'Team':<14} {'Attend':>6} {'Revenue':>12} {'Rev/Cap':>8}")
print("  " + "-"*60)
rev_per_caps = []
for g in sorted(ALL_GAMES, key=lambda x: x['date']):
    d = g['date']
    rev = game_revenue.get(d, 0)
    att = g['attendance']
    rpc = rev / att if att > 0 else 0
    if rev > 0:
        rev_per_caps.append(rpc)
    print(f"  {d:<12} {g['team']:<14} {att:>6} ${rev:>11,.2f} ${rpc:>7.2f}")

if rev_per_caps:
    print(f"\n  Avg revenue/cap: ${sum(rev_per_caps)/len(rev_per_caps):.2f}")
    print(f"  Min revenue/cap: ${min(rev_per_caps):.2f}")
    print(f"  Max revenue/cap: ${max(rev_per_caps):.2f}")

# ============================================================================
# TEMPORAL ANALYSIS
# ============================================================================
print("\n\n=== TEMPORAL ANALYSIS ===")

# 5. Time-of-day patterns
print("\n--- Time-of-Day Transaction Patterns ---")
hour_units = defaultdict(int)
hour_txns = defaultdict(int)
minute_units = defaultdict(int)  # for finer granularity

# Only game day data
game_rows = [r for r in pos_rows if r['Date'] in game_date_lookup]

for r in game_rows:
    time_parts = r['Time'].split(':')
    hour = int(time_parts[0])
    minute = int(time_parts[1])
    hour_units[hour] += r['Qty']
    hour_txns[hour] += 1
    # 5-minute bucket
    bucket = f"{hour:02d}:{(minute // 5) * 5:02d}"
    minute_units[bucket] += r['Qty']

print(f"  Hour | Units    | Txns     | Avg Qty/Txn | % of Total")
print("  " + "-"*65)
total_game_u = sum(hour_units.values())
for h in sorted(hour_units.keys()):
    pct = hour_units[h] / total_game_u * 100
    avg_qty = hour_units[h] / hour_txns[h] if hour_txns[h] > 0 else 0
    print(f"  {h:4d}  | {hour_units[h]:>8,} | {hour_txns[h]:>8,} | {avg_qty:>11.2f} | {pct:>6.1f}%")

# Peak periods around 7pm puck drop
print("\n  Peak periods (5-min buckets around puck drop, top 20):")
for i, (bucket, units) in enumerate(sorted(minute_units.items(), key=lambda x: -x[1])[:20]):
    print(f"    {bucket}: {units:,} units")

# 6. Day-of-week analysis
print("\n--- Day-of-Week Analysis ---")
dow_data = defaultdict(lambda: {"units": 0, "txns": 0, "games": 0, "attendance": 0})
for g in per_game_data:
    if g['units'] > 0:
        dow_data[g['day']]["units"] += g['units']
        dow_data[g['day']]["txns"] += g['txns']
        dow_data[g['day']]["games"] += 1
        dow_data[g['day']]["attendance"] += g['attendance']

print(f"  {'Day':<5} | {'Games':>5} | {'Total Units':>11} | {'Avg Units/Game':>14} | {'Avg Attend':>10} | {'Avg UPC':>7}")
print("  " + "-"*70)
dow_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
for day in dow_order:
    if day in dow_data:
        d = dow_data[day]
        avg_u = d['units'] / d['games'] if d['games'] > 0 else 0
        avg_a = d['attendance'] / d['games'] if d['games'] > 0 else 0
        avg_upc = d['units'] / d['attendance'] if d['attendance'] > 0 else 0
        print(f"  {day:<5} | {d['games']:>5} | {d['units']:>11,} | {avg_u:>14.0f} | {avg_a:>10.0f} | {avg_upc:>7.2f}")

# 7. Month-over-month trends
print("\n--- Month-over-Month Trends ---")
month_data = defaultdict(lambda: {"units": 0, "txns": 0, "games": 0, "attendance": 0})
for g in per_game_data:
    if g['units'] > 0:
        month_key = g['date'][:7]  # YYYY-MM
        month_data[month_key]["units"] += g['units']
        month_data[month_key]["txns"] += g['txns']
        month_data[month_key]["games"] += 1
        month_data[month_key]["attendance"] += g['attendance']

print(f"  {'Month':<8} | {'Games':>5} | {'Total Units':>11} | {'Avg Units/Game':>14} | {'Avg UPC':>7}")
print("  " + "-"*60)
for month in sorted(month_data.keys()):
    d = month_data[month]
    avg_u = d['units'] / d['games'] if d['games'] > 0 else 0
    avg_upc = d['units'] / d['attendance'] if d['attendance'] > 0 else 0
    print(f"  {month:<8} | {d['games']:>5} | {d['units']:>11,} | {avg_u:>14.0f} | {avg_upc:>7.2f}")

# 8. Year-over-year comparison
print("\n--- Season-over-Season Comparison ---")
season_data = defaultdict(lambda: {"units": 0, "txns": 0, "games": 0, "attendance": 0})
for g in per_game_data:
    if g['units'] > 0:
        season_data[g['season']]["units"] += g['units']
        season_data[g['season']]["txns"] += g['txns']
        season_data[g['season']]["games"] += 1
        season_data[g['season']]["attendance"] += g['attendance']

for s in [1, 2]:
    d = season_data[s]
    if d['games'] > 0:
        avg_u = d['units'] / d['games']
        avg_a = d['attendance'] / d['games']
        avg_upc = d['units'] / d['attendance']
        avg_tpc = d['txns'] / d['attendance']
        print(f"  Season {s}: {d['games']} games, {d['units']:,} units, avg {avg_u:.0f} units/game, avg attend {avg_a:.0f}, UPC {avg_upc:.2f}, TPC {avg_tpc:.2f}")

# ============================================================================
# GAME CONTEXT ANALYSIS
# ============================================================================
print("\n\n=== GAME CONTEXT ANALYSIS ===")

# 9. Per-cap by visiting team
print("\n--- Per-Cap Units by Visiting Team ---")
team_data = defaultdict(lambda: {"units": 0, "attendance": 0, "games": 0, "txns": 0})
for g in per_game_data:
    if g['units'] > 0:
        # Normalize team names
        team = g['team'].replace("TriCity", "Tri-City")
        team_data[team]["units"] += g['units']
        team_data[team]["attendance"] += g['attendance']
        team_data[team]["games"] += 1
        team_data[team]["txns"] += g['txns']

print(f"  {'Team':<15} | {'Games':>5} | {'Avg Attend':>10} | {'Avg Units':>9} | {'Avg UPC':>7}")
print("  " + "-"*60)
for team, d in sorted(team_data.items(), key=lambda x: -(x[1]['units']/x[1]['attendance']) if x[1]['attendance'] > 0 else 0):
    avg_a = d['attendance'] / d['games']
    avg_u = d['units'] / d['games']
    upc = d['units'] / d['attendance']
    print(f"  {team:<15} | {d['games']:>5} | {avg_a:>10.0f} | {avg_u:>9.0f} | {upc:>7.2f}")

# 10. Attendance impact on per-cap spending
print("\n--- Attendance Impact on Per-Cap Spending ---")
# Bin games by attendance
att_bins = [(0, 2000), (2000, 2500), (2500, 3000), (3000, 3500), (3500, 4000), (4000, 6000)]
for lo, hi in att_bins:
    bin_games = [g for g in per_game_data if lo <= g['attendance'] < hi and g['units'] > 0]
    if bin_games:
        avg_upc = sum(g['upc'] for g in bin_games) / len(bin_games)
        avg_att = sum(g['attendance'] for g in bin_games) / len(bin_games)
        avg_rev_pc = sum(game_revenue.get(g['date'], 0) / g['attendance'] for g in bin_games) / len(bin_games)
        print(f"  Attendance {lo}-{hi}: {len(bin_games)} games, avg UPC {avg_upc:.2f}, avg attend {avg_att:.0f}, est rev/cap ${avg_rev_pc:.2f}")

# Correlation between attendance and UPC
if len(per_game_data) > 2:
    valid_games = [g for g in per_game_data if g['units'] > 0]
    n = len(valid_games)
    sum_x = sum(g['attendance'] for g in valid_games)
    sum_y = sum(g['upc'] for g in valid_games)
    sum_xy = sum(g['attendance'] * g['upc'] for g in valid_games)
    sum_x2 = sum(g['attendance']**2 for g in valid_games)
    sum_y2 = sum(g['upc']**2 for g in valid_games)

    numerator = n * sum_xy - sum_x * sum_y
    denominator = math.sqrt((n * sum_x2 - sum_x**2) * (n * sum_y2 - sum_y**2))
    if denominator > 0:
        corr = numerator / denominator
        print(f"\n  Pearson correlation (attendance vs UPC): {corr:.4f}")

# 11. Playoff vs regular season
print("\n--- Playoff vs Regular Season ---")
playoff_games = [g for g in per_game_data if g['playoff'] and g['units'] > 0]
regular_games = [g for g in per_game_data if not g['playoff'] and g['units'] > 0]

if playoff_games:
    p_avg_u = sum(g['units'] for g in playoff_games) / len(playoff_games)
    p_avg_upc = sum(g['upc'] for g in playoff_games) / len(playoff_games)
    p_avg_att = sum(g['attendance'] for g in playoff_games) / len(playoff_games)
    print(f"  Playoff ({len(playoff_games)} games): avg units {p_avg_u:.0f}, avg UPC {p_avg_upc:.2f}, avg attend {p_avg_att:.0f}")

if regular_games:
    r_avg_u = sum(g['units'] for g in regular_games) / len(regular_games)
    r_avg_upc = sum(g['upc'] for g in regular_games) / len(regular_games)
    r_avg_att = sum(g['attendance'] for g in regular_games) / len(regular_games)
    print(f"  Regular ({len(regular_games)} games): avg units {r_avg_u:.0f}, avg UPC {r_avg_upc:.2f}, avg attend {r_avg_att:.0f}")

if playoff_games and regular_games:
    upc_lift = (p_avg_upc - r_avg_upc) / r_avg_upc * 100
    print(f"  Playoff UPC lift: {upc_lift:+.1f}%")

# 12. Special event impact ($1 Dog Night)
print("\n--- Special Event Impact ---")
dog_night = [g for g in per_game_data if g.get('note') == '$1 Dog Night']
if dog_night:
    dg = dog_night[0]
    # Compare to similar games (same day of week, similar attendance)
    similar = [g for g in per_game_data if g['day'] == 'Wed' and g['units'] > 0 and g['date'] != dg['date']]
    if similar:
        avg_sim_upc = sum(g['upc'] for g in similar) / len(similar)
        print(f"  $1 Dog Night (2025-10-22): UPC {dg['upc']:.2f}, attendance {dg['attendance']}")
        print(f"  Comparable Wed games ({len(similar)}): avg UPC {avg_sim_upc:.2f}")
        print(f"  Dog Night lift: {(dg['upc'] - avg_sim_upc) / avg_sim_upc * 100:+.1f}%")

    # Check food category specifically
    dog_night_food = sum(r['Qty'] for r in game_rows if r['Date'] == '2025-10-22' and r['Category'] == 'Food')
    dog_night_total = sum(r['Qty'] for r in game_rows if r['Date'] == '2025-10-22')
    print(f"  Dog Night food units: {dog_night_food}, total units: {dog_night_total}")
    print(f"  Food share: {dog_night_food/dog_night_total*100:.1f}%")

    # Compare food share to average
    avg_food_share = sum(r['Qty'] for r in game_rows if r['Category'] == 'Food') / sum(r['Qty'] for r in game_rows) * 100
    print(f"  Overall avg food share: {avg_food_share:.1f}%")

# ============================================================================
# STAND PERFORMANCE ANALYSIS
# ============================================================================
print("\n\n=== STAND PERFORMANCE ANALYSIS ===")

# 14. Per-stand volumes and category mix
print("\n--- Per-Stand Unit Volumes ---")
stand_cat_units = defaultdict(lambda: defaultdict(int))
stand_total_units = defaultdict(int)
stand_total_txns = defaultdict(int)

for r in pos_rows:
    if r['Date'] in game_date_lookup:
        stand_cat_units[r['Location']][r['Category']] += r['Qty']
        stand_total_units[r['Location']] += r['Qty']
        stand_total_txns[r['Location']] += 1

num_games_with_data = len([d for d in game_date_lookup if d in data_dates_set])
print(f"\n  Games with transaction data: {num_games_with_data}")

for loc in sorted(stand_total_units.keys(), key=lambda x: -stand_total_units[x]):
    u = stand_total_units[loc]
    t = stand_total_txns[loc]
    avg_per_game = u / num_games_with_data if num_games_with_data > 0 else 0
    print(f"\n  {loc}:")
    print(f"    Total units: {u:,} ({u/sum(stand_total_units.values())*100:.1f}% of all)")
    print(f"    Total txns: {t:,}")
    print(f"    Avg units/game: {avg_per_game:.0f}")
    print(f"    Category mix:")
    for cat, cu in sorted(stand_cat_units[loc].items(), key=lambda x: -x[1]):
        pct = cu / u * 100
        print(f"      {cat}: {cu:,} ({pct:.1f}%)")

# 15. Stand utilization by time
print("\n--- Stand Utilization by Time (game days) ---")
stand_hour_units = defaultdict(lambda: defaultdict(int))
for r in game_rows:
    hour = int(r['Time'].split(':')[0])
    stand_hour_units[r['Location']][hour] += r['Qty']

for loc in sorted(stand_total_units.keys(), key=lambda x: -stand_total_units[x]):
    print(f"\n  {loc}:")
    hours = sorted(stand_hour_units[loc].keys())
    for h in hours:
        u = stand_hour_units[loc][h]
        bar = '#' * max(1, int(u / 200))
        print(f"    {h:02d}:00 - {u:>5,} units {bar}")

# 16. Product concentration risk
print("\n--- Product Concentration Risk by Stand ---")
for loc in sorted(stand_total_units.keys(), key=lambda x: -stand_total_units[x]):
    # Get items sold at this stand
    stand_items = defaultdict(int)
    for r in game_rows:
        if r['Location'] == loc:
            stand_items[r['Item']] += r['Qty']

    total = sum(stand_items.values())
    if total == 0:
        continue

    # Top 3 items concentration
    top3 = sorted(stand_items.items(), key=lambda x: -x[1])[:3]
    top3_pct = sum(x[1] for x in top3) / total * 100
    print(f"  {loc}:")
    print(f"    Top 3 items = {top3_pct:.1f}% of units")
    for item, units in top3:
        print(f"      {item}: {units:,} ({units/total*100:.1f}%)")

# ============================================================================
# PRODUCT & CATEGORY ANALYSIS
# ============================================================================
print("\n\n=== PRODUCT & CATEGORY ANALYSIS ===")

# 18. Top 20 items by volume (already done above, repeat concisely)
print("\n--- Top 20 Items by Volume ---")
for i, (item, units) in enumerate(sorted(item_units.items(), key=lambda x: -x[1])[:20]):
    # Get most common Price Point Name for this item
    ppns = defaultdict(int)
    for r in pos_rows:
        if r['Item'] == item and r['Price Point Name'].strip():
            ppns[r['Price Point Name']] += r['Qty']
    top_ppn = sorted(ppns.items(), key=lambda x: -x[1])[:3] if ppns else []
    ppn_str = ", ".join(f"{p[0]}({p[1]})" for p in top_ppn)
    print(f"  {i+1:>2}. {item:<30} {units:>7,} units | Top variants: {ppn_str}")

# 19. Bottom 20 items
print("\n--- Bottom 20 Items (Menu Simplification Candidates) ---")
for i, (item, units) in enumerate(sorted(item_units.items(), key=lambda x: x[1])[:20]):
    cats = set(r['Category'] for r in pos_rows if r['Item'] == item)
    print(f"  {i+1:>2}. {item:<30} {units:>5} units | Category: {', '.join(cats)}")

# 20. Category growth between seasons
print("\n--- Category Growth: Season 1 vs Season 2 ---")
s1_dates = set(g['date'] for g in ALL_GAMES if g['season'] == 1)
s2_dates = set(g['date'] for g in ALL_GAMES if g['season'] == 2)
s1_attendance = sum(g['attendance'] for g in ALL_GAMES if g['season'] == 1)
s2_attendance = sum(g['attendance'] for g in ALL_GAMES if g['season'] == 2)

s1_cat_units = defaultdict(int)
s2_cat_units = defaultdict(int)
for r in pos_rows:
    if r['Date'] in s1_dates:
        s1_cat_units[r['Category']] += r['Qty']
    elif r['Date'] in s2_dates:
        s2_cat_units[r['Category']] += r['Qty']

all_cats = sorted(set(list(s1_cat_units.keys()) + list(s2_cat_units.keys())))
print(f"  S1: {len(s1_dates)} games, {s1_attendance:,} total attendance")
print(f"  S2: {len(s2_dates)} games, {s2_attendance:,} total attendance")
print(f"\n  {'Category':<30} | {'S1 Units':>8} | {'S1/Cap':>7} | {'S2 Units':>8} | {'S2/Cap':>7} | {'Growth':>7}")
print("  " + "-"*80)
for cat in all_cats:
    s1u = s1_cat_units.get(cat, 0)
    s2u = s2_cat_units.get(cat, 0)
    s1pc = s1u / s1_attendance if s1_attendance > 0 else 0
    s2pc = s2u / s2_attendance if s2_attendance > 0 else 0
    growth = ((s2pc - s1pc) / s1pc * 100) if s1pc > 0 else float('inf')
    growth_str = f"{growth:+.1f}%" if growth != float('inf') else "NEW"
    print(f"  {cat:<30} | {s1u:>8,} | {s1pc:>7.3f} | {s2u:>8,} | {s2pc:>7.3f} | {growth_str:>7}")

# 21. Beer brand analysis
print("\n--- Beer Brand Analysis ---")
beer_rows = [r for r in pos_rows if r['Category'] == 'Beer']
beer_brand_units = defaultdict(int)
for r in beer_rows:
    ppn = r['Price Point Name'].strip()
    if not ppn:
        ppn = r['Item']
    beer_brand_units[ppn] += r['Qty']

print(f"  Total beer units: {sum(beer_brand_units.values()):,}")
for brand, units in sorted(beer_brand_units.items(), key=lambda x: -x[1])[:20]:
    pct = units / sum(beer_brand_units.values()) * 100
    print(f"    {brand:<35} {units:>6,} ({pct:.1f}%)")

# Classify beer brands
macro_brands = {"Budweiser", "Bud Light", "Michelob Ultra", "Corona", "Coors Light", "Coors Original"}
sp_brands = set(b for b in beer_brand_units.keys() if "Stanley Park" in b)
phillips_brands = set(b for b in beer_brand_units.keys() if "Phillips" in b or "phillips" in b.lower())
iota_brands = set(b for b in beer_brand_units.keys() if "iOTA" in b or "iota" in b.lower())

macro_total = sum(beer_brand_units[b] for b in macro_brands if b in beer_brand_units)
sp_total = sum(beer_brand_units[b] for b in sp_brands)
phillips_total = sum(beer_brand_units[b] for b in phillips_brands)
other_beer = sum(beer_brand_units.values()) - macro_total - sp_total - phillips_total

total_beer = sum(beer_brand_units.values())
print(f"\n  Beer Category Breakdown:")
print(f"    Macro (Bud/Coors/Corona/Michelob): {macro_total:,} ({macro_total/total_beer*100:.1f}%)")
print(f"    Stanley Park: {sp_total:,} ({sp_total/total_beer*100:.1f}%)")
print(f"    Phillips: {phillips_total:,} ({phillips_total/total_beer*100:.1f}%)")
print(f"    Other: {other_beer:,} ({other_beer/total_beer*100:.1f}%)")

# Beer by season
s1_beer = sum(r['Qty'] for r in beer_rows if r['Date'] in s1_dates)
s2_beer = sum(r['Qty'] for r in beer_rows if r['Date'] in s2_dates)
print(f"\n  Season 1 beer units: {s1_beer:,} ({s1_beer/s1_attendance:.3f}/cap)")
print(f"  Season 2 beer units: {s2_beer:,} ({s2_beer/s2_attendance:.3f}/cap)")

# 22. Food/alcohol correlation
print("\n--- Food/Alcohol Correlation Analysis ---")
# Per-game food and alcohol units
game_food = defaultdict(int)
game_alcohol = defaultdict(int)
game_na = defaultdict(int)
alcohol_cats = {"Beer", "Wine, Cider & Coolers", "Liquor"}
food_cats = {"Food", "Snacks", "Sweets"}
na_cats = {"NA Bev", "NA Bev PST Exempt"}

for r in game_rows:
    d = r['Date']
    if r['Category'] in alcohol_cats:
        game_alcohol[d] += r['Qty']
    elif r['Category'] in food_cats:
        game_food[d] += r['Qty']
    elif r['Category'] in na_cats:
        game_na[d] += r['Qty']

# Correlation between food and alcohol per game
common_dates = sorted(set(game_food.keys()) & set(game_alcohol.keys()))
if len(common_dates) > 2:
    food_vals = [game_food[d] for d in common_dates]
    alc_vals = [game_alcohol[d] for d in common_dates]

    n = len(common_dates)
    sum_x = sum(food_vals)
    sum_y = sum(alc_vals)
    sum_xy = sum(f*a for f,a in zip(food_vals, alc_vals))
    sum_x2 = sum(f**2 for f in food_vals)
    sum_y2 = sum(a**2 for a in alc_vals)

    num = n * sum_xy - sum_x * sum_y
    den = math.sqrt((n * sum_x2 - sum_x**2) * (n * sum_y2 - sum_y**2))
    if den > 0:
        corr_fa = num / den
        print(f"  Food-Alcohol correlation (per game): {corr_fa:.4f}")

    # Food-to-alcohol ratio
    ratios = [game_food[d] / game_alcohol[d] if game_alcohol[d] > 0 else 0 for d in common_dates]
    avg_ratio = sum(ratios) / len(ratios)
    print(f"  Avg food:alcohol ratio: {avg_ratio:.2f}")

    # Per-cap food and alcohol
    for d in common_dates[:5]:
        att = game_date_lookup[d]['attendance']
        print(f"    {d}: food/cap={game_food[d]/att:.2f}, alc/cap={game_alcohol[d]/att:.2f}, ratio={game_food[d]/game_alcohol[d]:.2f}")

# 23. Non-alcoholic beverage trends
print("\n--- Non-Alcoholic Beverage Trends ---")
na_items = defaultdict(int)
for r in pos_rows:
    if r['Category'] in na_cats:
        ppn = r['Price Point Name'].strip() if r['Price Point Name'].strip() else r['Item']
        na_items[ppn] += r['Qty']

total_na = sum(na_items.values())
print(f"  Total NA bev units: {total_na:,}")
for item, units in sorted(na_items.items(), key=lambda x: -x[1])[:15]:
    print(f"    {item:<35} {units:>5,} ({units/total_na*100:.1f}%)")

# ============================================================================
# BASKET / AFFINITY ANALYSIS
# ============================================================================
print("\n\n=== PRODUCT AFFINITY & BASKET ANALYSIS ===")

# 24. Items bought in same time window = basket proxy
# Group by Date + Time (same second) + Location as basket proxy
basket_items = defaultdict(list)
for r in game_rows:
    key = (r['Date'], r['Time'], r['Location'])
    basket_items[key].append(r['Item'])

# Baskets with multiple items
multi_baskets = {k: v for k, v in basket_items.items() if len(v) > 1}
print(f"Total baskets (unique date/time/location): {len(basket_items):,}")
print(f"Multi-item baskets: {len(multi_baskets):,} ({len(multi_baskets)/len(basket_items)*100:.1f}%)")

# Average basket size
sizes = [len(v) for v in basket_items.values()]
avg_size = sum(sizes) / len(sizes) if sizes else 0
print(f"Average basket size (items): {avg_size:.2f}")
size_dist = Counter(len(v) for v in basket_items.values())
print(f"Basket size distribution:")
for s in sorted(size_dist.keys())[:10]:
    print(f"  {s} items: {size_dist[s]:,} ({size_dist[s]/len(basket_items)*100:.1f}%)")

# Co-occurrence analysis
from itertools import combinations
pair_counts = Counter()
for basket_list in multi_baskets.values():
    unique_items = list(set(basket_list))
    if len(unique_items) >= 2:
        for pair in combinations(sorted(unique_items), 2):
            pair_counts[pair] += 1

print(f"\nTop 20 Product Pairs (co-purchased):")
for pair, count in pair_counts.most_common(20):
    print(f"  {pair[0]} + {pair[1]}: {count} times")

# Category co-occurrence
cat_pair_counts = Counter()
basket_cats = defaultdict(list)
for r in game_rows:
    key = (r['Date'], r['Time'], r['Location'])
    basket_cats[key].append(r['Category'])

multi_cat_baskets = {k: v for k, v in basket_cats.items() if len(set(v)) > 1}
for basket_list in multi_cat_baskets.values():
    unique_cats = list(set(basket_list))
    if len(unique_cats) >= 2:
        for pair in combinations(sorted(unique_cats), 2):
            cat_pair_counts[pair] += 1

print(f"\nTop Category Pairs (co-purchased):")
for pair, count in cat_pair_counts.most_common(15):
    print(f"  {pair[0]} + {pair[1]}: {count} times")

# ============================================================================
# INTERMISSION RUSH ANALYSIS
# ============================================================================
print("\n\n=== INTERMISSION RUSH ANALYSIS ===")

# 26. Transaction density by minute relative to puck drop (7pm assumed)
# Typical WHL game: puck drop ~7:05pm, 1st intermission ~7:45pm, 2nd intermission ~8:25pm

# Calculate per-minute transaction density for game days
minute_txn_density = defaultdict(int)
minute_unit_density = defaultdict(int)

for r in game_rows:
    time_parts = r['Time'].split(':')
    h = int(time_parts[0])
    m = int(time_parts[1])
    total_min = h * 60 + m
    minute_txn_density[total_min] += 1
    minute_unit_density[total_min] += r['Qty']

# Show density around key times
print("  Minute-by-minute transaction density (game days, all games combined):")
print("  Showing key periods:")

# Pre-game (6:00-7:05)
print("\n  PRE-GAME (6:00 PM - 7:05 PM):")
for t in range(18*60, 19*60+6):
    if minute_txn_density[t] > 0:
        h = t // 60
        m = t % 60
        bar = '#' * max(1, minute_txn_density[t] // 20)
        print(f"    {h:02d}:{m:02d} | txns: {minute_txn_density[t]:>4} | units: {minute_unit_density[t]:>5} {bar}")

# 1st period (7:05-7:45)
print("\n  1ST PERIOD (7:05 PM - 7:45 PM):")
for t in range(19*60+5, 19*60+46):
    if minute_txn_density[t] > 0:
        h = t // 60
        m = t % 60
        bar = '#' * max(1, minute_txn_density[t] // 20)
        print(f"    {h:02d}:{m:02d} | txns: {minute_txn_density[t]:>4} | units: {minute_unit_density[t]:>5} {bar}")

# 1st intermission (7:45-8:05)
print("\n  1ST INTERMISSION (7:45 PM - 8:05 PM):")
for t in range(19*60+45, 20*60+6):
    if minute_txn_density[t] > 0:
        h = t // 60
        m = t % 60
        bar = '#' * max(1, minute_txn_density[t] // 20)
        print(f"    {h:02d}:{m:02d} | txns: {minute_txn_density[t]:>4} | units: {minute_unit_density[t]:>5} {bar}")

# 2nd period (8:05-8:45)
print("\n  2ND PERIOD (8:05 PM - 8:45 PM):")
for t in range(20*60+5, 20*60+46):
    if minute_txn_density[t] > 0:
        h = t // 60
        m = t % 60
        bar = '#' * max(1, minute_txn_density[t] // 20)
        print(f"    {h:02d}:{m:02d} | txns: {minute_txn_density[t]:>4} | units: {minute_unit_density[t]:>5} {bar}")

# 2nd intermission (8:45-9:05)
print("\n  2ND INTERMISSION (8:45 PM - 9:05 PM):")
for t in range(20*60+45, 21*60+6):
    if minute_txn_density[t] > 0:
        h = t // 60
        m = t % 60
        bar = '#' * max(1, minute_txn_density[t] // 20)
        print(f"    {h:02d}:{m:02d} | txns: {minute_txn_density[t]:>4} | units: {minute_unit_density[t]:>5} {bar}")

# 3rd period and beyond
print("\n  3RD PERIOD & POST (9:05 PM+):")
for t in range(21*60+5, 22*60+30):
    if minute_txn_density[t] > 0:
        h = t // 60
        m = t % 60
        bar = '#' * max(1, minute_txn_density[t] // 20)
        print(f"    {h:02d}:{m:02d} | txns: {minute_txn_density[t]:>4} | units: {minute_unit_density[t]:>5} {bar}")

# Summary of period-based transactions
periods = {
    "Pre-game (6:00-7:05)": (18*60, 19*60+5),
    "1st Period (7:05-7:45)": (19*60+5, 19*60+45),
    "1st Intermission (7:45-8:05)": (19*60+45, 20*60+5),
    "2nd Period (8:05-8:45)": (20*60+5, 20*60+45),
    "2nd Intermission (8:45-9:05)": (20*60+45, 21*60+5),
    "3rd Period (9:05-9:45)": (21*60+5, 21*60+45),
    "Post-game (9:45+)": (21*60+45, 23*60),
}

print("\n  Summary by Game Period:")
print(f"  {'Period':<30} | {'Txns':>8} | {'Units':>8} | {'% Txns':>7} | {'% Units':>7}")
print("  " + "-"*70)
total_period_txns = sum(minute_txn_density.values())
total_period_units = sum(minute_unit_density.values())
for period_name, (start, end) in periods.items():
    p_txns = sum(minute_txn_density[t] for t in range(start, end))
    p_units = sum(minute_unit_density[t] for t in range(start, end))
    pct_t = p_txns / total_period_txns * 100 if total_period_txns > 0 else 0
    pct_u = p_units / total_period_units * 100 if total_period_units > 0 else 0
    print(f"  {period_name:<30} | {p_txns:>8,} | {p_units:>8,} | {pct_t:>6.1f}% | {pct_u:>6.1f}%")

# Intermission rush intensity
print("\n  Intermission Rush Intensity:")
for period_name, (start, end) in periods.items():
    minutes = end - start
    p_txns = sum(minute_txn_density[t] for t in range(start, end))
    if p_txns > 0:
        txns_per_min = p_txns / minutes
        print(f"  {period_name}: {txns_per_min:.1f} txns/min ({minutes} min window)")

# ============================================================================
# DEMAND FORECASTING MODEL DESIGN
# ============================================================================
print("\n\n=== DEMAND FORECASTING MODEL DESIGN ===")
print("""
  Target Variable: Total units sold per game (or per category per game)

  Feature Engineering:

  1. TEMPORAL FEATURES:
     - Day of week (one-hot: Mon, Tue, Wed, Thu, Fri, Sat, Sun)
     - Month of season (ordinal)
     - Season number (1 or 2)
     - Is weekend (Fri/Sat/Sun)
     - Days since season start
     - Days until/since Christmas break
     - Is January (post-holiday slump potential)

  2. GAME CONTEXT FEATURES:
     - Visiting team (one-hot or target-encoded)
     - Is rival team (e.g., Kamloops, Kelowna, Vancouver)
     - Is playoff game (binary)
     - Expected attendance (from ticket sales pre-game)
     - Actual attendance (for post-game analysis)
     - Is special event ($1 Dog Night, etc.)
     - Game number in homestand (1st, 2nd, 3rd)
     - Days since last home game

  3. EXTERNAL FEATURES:
     - Weather (temperature, precipitation - Victoria BC)
     - Is school holiday / PA day
     - Competing events in Victoria
     - Is long weekend

  4. LAGGED FEATURES:
     - Units sold at previous home game
     - Units sold at same matchup last season
     - Rolling 3-game average of units/cap
     - Rolling 3-game average of attendance

  5. TREND FEATURES:
     - Season-to-date cumulative attendance
     - Team record / standing (win momentum)
     - Attendance trend (up/down from rolling avg)

  Recommended Models:
  - Baseline: Linear Regression with above features
  - Advanced: Gradient Boosted Trees (XGBoost/LightGBM)
  - For time-series: SARIMA for seasonal patterns

  Evaluation Strategy:
  - Train on Season 1, validate on early Season 2, test on late Season 2
  - Metrics: RMSE, MAPE, directional accuracy

  Expected predictive power:
  - Attendance alone explains ~70-80% of variance in total units
  - Day-of-week adds ~5-10% improvement
  - Visiting team adds ~3-5% improvement
  - Special events/playoffs add conditional spikes
""")

# Simple linear model: units = a * attendance + b
valid_games_model = [g for g in per_game_data if g['units'] > 0]
n = len(valid_games_model)
x_vals = [g['attendance'] for g in valid_games_model]
y_vals = [g['units'] for g in valid_games_model]

mean_x = sum(x_vals) / n
mean_y = sum(y_vals) / n
ss_xy = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_vals, y_vals))
ss_xx = sum((x - mean_x)**2 for x in x_vals)
ss_yy = sum((y - mean_y)**2 for y in y_vals)

beta = ss_xy / ss_xx if ss_xx > 0 else 0
alpha = mean_y - beta * mean_x
r_squared = (ss_xy**2) / (ss_xx * ss_yy) if ss_xx > 0 and ss_yy > 0 else 0

print(f"\n  Simple Linear Model: Units = {beta:.2f} * Attendance + {alpha:.2f}")
print(f"  R-squared: {r_squared:.4f}")
print(f"  Interpretation: Each additional attendee generates ~{beta:.2f} additional unit sales")

# Residuals
print(f"\n  Sample Predictions vs Actual:")
for g in valid_games_model[:10]:
    predicted = beta * g['attendance'] + alpha
    residual = g['units'] - predicted
    print(f"    {g['date']} | Actual: {g['units']:5d} | Predicted: {predicted:7.0f} | Residual: {residual:+7.0f}")

print("\n\nANALYSIS COMPLETE - Generating report...")
print(f"Total rows analyzed: {len(all_rows)}")
print(f"Total game days: {len(ALL_GAMES)}")
