"""
Shared configuration for Royals Concession Intelligence Platform.
All modules import constants from here.
"""
import os

# === Paths ===
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, "db", "royals.db")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
DATA_DIR = os.path.join(os.path.dirname(PROJECT_ROOT), "data")

# === Tax Rates ===
TAX_RATE = 0.05  # 5% GST
LIQUOR_TAX_RATE = 0.10  # 10% liquor tax

# === Known Prices (item, price_point_name) -> price ===
KNOWN_PRICES = {
    # Beer - Tap
    ("Tap Beer", "Phillips IPA"): 9.49,
    ("Tap Beer", "Phillips Blue Buck"): 9.49,
    ("Tap Beer", "Phillips Dinosour"): 9.49,
    ("Tap Beer", "Phillips Electric Unicorn"): 9.49,
    ("Tap Beer", "Phillips Short Wave"): 9.49,
    ("Tap Beer", "Phillips Solaris"): 9.49,
    ("Tap Beer", "Rotating Phillips"): 9.49,
    ("Tap Beer", "Bud Light"): 9.49,
    ("Tap Beer", "Granville Island Honey Lager"): 9.49,
    ("Tap Beer", ""): 9.49,
    # Beer - Cans
    ("Can Beer", "Bud Light"): 8.49,
    ("Can Beer", "Budweiser"): 8.49,
    ("Can Beer", "Granville Island Honey Lager"): 8.49,
    ("Can Beer", "Mike's Hard White Freeze"): 8.49,
    ("Can Beer", "Mikes Hard Pink Lemonade"): 8.49,
    ("Can Beer", "Mike's Hard Blue Freeze"): 8.49,
    ("Can Beer", "Nutrl Vodka Soda - Grapefruit"): 8.49,
    ("Can Beer", "Nutrl Vodka Soda - Lemon"): 8.49,
    ("Can Beer", "Vizzy Pineapple Mango"): 8.49,
    ("Can Beer", "Vizzy Blueberry Pomegranate"): 8.49,
    ("Can Beer", "Corona"): 8.49,
    ("Can Beer", ""): 8.49,
    # Cocktails
    ("Cocktail", "Fireball Shot"): 9.99,
    ("Cocktail", "Jager Shot"): 9.99,
    ("Cocktail", "Vodka Shot"): 9.99,
    ("Cocktail", "Vodka Cran"): 9.99,
    ("Cocktail", "Rum & Coke"): 9.99,
    ("Cocktail", "Rye & Coke"): 9.99,
    ("Cocktail", "Rye & Ginger"): 9.99,
    ("Cocktail", "Vodka Soda"): 9.99,
    ("Cocktail", "Vodka Tonic"): 9.99,
    ("Cocktail", "Gin & Tonic"): 9.99,
    ("Cocktail", ""): 9.99,
    # Wine
    ("Wine", "White Wine"): 8.49,
    ("Wine", "Red Wine"): 8.49,
    ("Wine", ""): 8.49,
    # NA Beverages
    ("Bottle Pop", "Pepsi"): 4.99,
    ("Bottle Pop", "Diet Pepsi"): 4.99,
    ("Bottle Pop", "7UP"): 4.99,
    ("Bottle Pop", "Dr. Pepper"): 4.99,
    ("Bottle Pop", "Mug Root Beer"): 4.99,
    ("Bottle Pop", "Brisk Iced Tea"): 4.99,
    ("Bottle Pop", "Gatorade Blue"): 4.99,
    ("Bottle Pop", "Gatorade Orange"): 4.99,
    ("Bottle Pop", ""): 4.99,
    ("Water", ""): 3.99,
    ("Water", "Aquafina Water"): 3.99,
    ("Fountain Pop", "Pepsi"): 4.49,
    ("Fountain Pop", "Diet Pepsi"): 4.49,
    ("Fountain Pop", "7UP"): 4.49,
    ("Fountain Pop", "Dr. Pepper"): 4.49,
    ("Fountain Pop", "Mug Root Beer"): 4.49,
    ("Fountain Pop", ""): 4.49,
    ("Hot Beverage", "Hot Chocolate"): 3.99,
    ("Hot Beverage", "Coffee"): 3.49,
    ("Hot Beverage", ""): 3.49,
    # Food
    ("Hot Dog", ""): 5.99,
    ("Hot Dog", "Regular Hot Dog"): 5.99,
    ("Hot Dog", "$1 Dog"): 1.00,
    ("Pretzel", ""): 5.99,
    ("Pretzel", "Salted Pretzel"): 5.99,
    ("Pizza Slice", ""): 5.99,
    ("Pizza Slice", "Pepperoni"): 5.99,
    ("Pizza Slice", "Cheese"): 5.99,
    ("Pizza Slice", "Hawaiian"): 5.99,
    ("Popcorn", ""): 5.99,
    ("Popcorn", "Regular Popcorn"): 5.99,
    ("Nachos", ""): 7.99,
    ("Nachos", "Regular Nachos"): 7.99,
    ("Cheeseburger", ""): 8.99,
    ("Cheeseburger", "Cheeseburger"): 8.99,
    ("Chicken Strips", ""): 8.99,
    ("Chicken Strips", "Chicken Strips"): 8.99,
    ("Fries", ""): 5.99,
    ("Fries", "Regular Fries"): 5.99,
    ("Taco", ""): 5.99,
    ("Taco", "Regular Taco"): 5.99,
    ("Taco", "Fish Taco"): 6.99,
    # Snacks
    ("Candy", ""): 3.99,
    ("Candy", "Skittles"): 3.99,
    ("Candy", "M&Ms"): 3.99,
    ("Candy", "Reese's"): 3.99,
    ("Chips", ""): 3.99,
    ("Chips", "Doritos"): 3.99,
    ("Chips", "Lays"): 3.99,
    # Misc
    ("50/50 Ticket", ""): 5.00,
    ("50/50 Ticket", "50/50"): 5.00,
    ("Souvenir", ""): 15.00,
    ("Souvenir", "Program"): 10.00,
    ("Souvenir", "Puck"): 15.00,
}

# === Category-level fallback prices ===
CATEGORY_PRICES = {
    "Beer": 9.00,
    "Cocktail": 9.99,
    "Wine": 8.49,
    "NA Bev": 4.49,
    "Food": 6.49,
    "Snacks": 4.99,
    "Merch": 15.00,
    "Other": 5.00,
}

# === Locations / Stands ===
LOCATIONS = [
    "SOFMC Island Canteen",
    "SOFMC Phillips Bar",
    "SOFMC Island Slice",
    "SOFMC TacoTacoTaco",
    "SOFMC ReMax Fan Deck",
    "SOFMC Portable",
]

# === Categories ===
CATEGORIES = [
    "Beer",
    "Cocktail",
    "Wine",
    "NA Bev",
    "Food",
    "Snacks",
    "Merch",
    "Other",
]

# === Game Periods (derived from time) ===
GAME_PERIODS = {
    "pre_game": (17, 0, 19, 4),       # 5:00 PM - 7:04 PM
    "1st_period": (19, 5, 19, 24),     # 7:05 PM - 7:24 PM
    "1st_intermission": (19, 25, 19, 44),  # 7:25 PM - 7:44 PM
    "2nd_period": (19, 45, 20, 4),     # 7:45 PM - 8:04 PM
    "2nd_intermission": (20, 5, 20, 24),   # 8:05 PM - 8:24 PM
    "3rd_period": (20, 25, 20, 59),    # 8:25 PM - 8:59 PM
    "post_game": (21, 0, 23, 59),      # 9:00 PM - 11:59 PM
}

# === Stand Opening Rules ===
STAND_OPENING_RULES = {
    "under_2000": {
        "threshold": 2000,
        "open_stands": ["SOFMC Island Canteen", "SOFMC Phillips Bar", "SOFMC Portable"],
        "close_stands": ["SOFMC Island Slice", "SOFMC TacoTacoTaco", "SOFMC ReMax Fan Deck"],
        "staff_per_stand": 2,
    },
    "2000_to_3500": {
        "threshold": 3500,
        "open_stands": ["SOFMC Island Canteen", "SOFMC Phillips Bar", "SOFMC Portable", "SOFMC Island Slice"],
        "close_stands": ["SOFMC TacoTacoTaco", "SOFMC ReMax Fan Deck"],
        "staff_per_stand": 3,
    },
    "over_3500": {
        "threshold": 99999,
        "open_stands": ["SOFMC Island Canteen", "SOFMC Phillips Bar", "SOFMC Portable", "SOFMC Island Slice", "SOFMC TacoTacoTaco", "SOFMC ReMax Fan Deck"],
        "close_stands": [],
        "staff_per_stand": 3,
    },
}

# === Promotional Events ===
PROMO_EVENTS = ["Dollar Dog Night", "Family Night", "School Night", "Taco Tuesday", "Playoff", "Regular"]

# === Game Details (pre-parsed) ===
SEASON1_GAMES = [
    {"team": "Tri-City", "day": "Fri", "date": "2024-09-20", "attendance": 4218, "playoff": False, "note": ""},
    {"team": "Tri-City", "day": "Sat", "date": "2024-09-21", "attendance": 2030, "playoff": False, "note": ""},
    {"team": "Wenatchee", "day": "Fri", "date": "2024-10-11", "attendance": 2156, "playoff": False, "note": ""},
    {"team": "Wenatchee", "day": "Sat", "date": "2024-10-12", "attendance": 2164, "playoff": False, "note": ""},
    {"team": "Prince Albert", "day": "Fri", "date": "2024-10-18", "attendance": 3114, "playoff": False, "note": ""},
    {"team": "Moose Jaw", "day": "Fri", "date": "2024-11-01", "attendance": 3048, "playoff": False, "note": ""},
    {"team": "Saskatoon", "day": "Sun", "date": "2024-11-03", "attendance": 3421, "playoff": False, "note": ""},
    {"team": "Kamloops", "day": "Tue", "date": "2024-11-05", "attendance": 1310, "playoff": False, "note": ""},
    {"team": "Kamloops", "day": "Wed", "date": "2024-11-06", "attendance": 1477, "playoff": False, "note": ""},
    {"team": "Seattle", "day": "Fri", "date": "2024-11-29", "attendance": 2842, "playoff": False, "note": ""},
    {"team": "Seattle", "day": "Sat", "date": "2024-11-30", "attendance": 2340, "playoff": False, "note": ""},
    {"team": "Regina", "day": "Tue", "date": "2024-12-03", "attendance": 1491, "playoff": False, "note": ""},
    {"team": "Kelowna", "day": "Sat", "date": "2024-12-07", "attendance": 1835, "playoff": False, "note": ""},
    {"team": "Kelowna", "day": "Sun", "date": "2024-12-08", "attendance": 3558, "playoff": False, "note": ""},
    {"team": "Vancouver", "day": "Fri", "date": "2024-12-13", "attendance": 2726, "playoff": False, "note": ""},
    {"team": "Prince George", "day": "Fri", "date": "2024-12-27", "attendance": 2409, "playoff": False, "note": ""},
    {"team": "Prince George", "day": "Sat", "date": "2024-12-28", "attendance": 3085, "playoff": False, "note": ""},
    {"team": "Vancouver", "day": "Tue", "date": "2024-12-31", "attendance": 2939, "playoff": False, "note": ""},
    {"team": "Everett", "day": "Fri", "date": "2025-01-03", "attendance": 3367, "playoff": False, "note": ""},
    {"team": "Brandon", "day": "Wed", "date": "2025-01-15", "attendance": 2166, "playoff": False, "note": ""},
    {"team": "Kamloops", "day": "Fri", "date": "2025-01-17", "attendance": 2567, "playoff": False, "note": ""},
    {"team": "Kamloops", "day": "Sat", "date": "2025-01-18", "attendance": 2913, "playoff": False, "note": ""},
    {"team": "SWC", "day": "Sat", "date": "2025-01-25", "attendance": 3333, "playoff": False, "note": ""},
    {"team": "Kelowna", "day": "Tue", "date": "2025-02-04", "attendance": 1245, "playoff": False, "note": ""},
    {"team": "Kelowna", "day": "Wed", "date": "2025-02-05", "attendance": 1522, "playoff": False, "note": ""},
    {"team": "Vancouver", "day": "Fri", "date": "2025-02-14", "attendance": 3252, "playoff": False, "note": ""},
    {"team": "Everett", "day": "Mon", "date": "2025-02-17", "attendance": 3897, "playoff": False, "note": ""},
    {"team": "Prince George", "day": "Fri", "date": "2025-02-21", "attendance": 2754, "playoff": False, "note": ""},
    {"team": "Prince George", "day": "Sat", "date": "2025-02-22", "attendance": 2946, "playoff": False, "note": ""},
    {"team": "Portland", "day": "Fri", "date": "2025-02-28", "attendance": 2696, "playoff": False, "note": ""},
    {"team": "Portland", "day": "Sat", "date": "2025-03-01", "attendance": 3215, "playoff": False, "note": ""},
    {"team": "Spokane", "day": "Fri", "date": "2025-03-07", "attendance": 3015, "playoff": False, "note": ""},
    {"team": "Spokane", "day": "Sat", "date": "2025-03-08", "attendance": 3606, "playoff": False, "note": ""},
    {"team": "Vancouver", "day": "Fri", "date": "2025-03-14", "attendance": 4942, "playoff": False, "note": ""},
    {"team": "Tri-City", "day": "Fri", "date": "2025-03-28", "attendance": 3977, "playoff": False, "note": ""},
    {"team": "Tri-City", "day": "Sat", "date": "2025-03-29", "attendance": 4466, "playoff": False, "note": ""},
    {"team": "Spokane", "day": "Wed", "date": "2025-04-16", "attendance": 3670, "playoff": True, "note": ""},
    {"team": "Spokane", "day": "Fri", "date": "2025-04-18", "attendance": 5540, "playoff": True, "note": ""},
    {"team": "Spokane", "day": "Sat", "date": "2025-04-19", "attendance": 3361, "playoff": True, "note": ""},
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
    ALL_GAMES.append(g2)
for g in SEASON2_GAMES:
    g2 = dict(g)
    g2["season"] = 2
    ALL_GAMES.append(g2)

# CSV files list
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

# Category mapping from CSV categories to our standardized categories
CATEGORY_MAP = {
    "Beer": "Beer",
    "Cocktail": "Cocktail",
    "Wine": "Wine",
    "NA Bev": "NA Bev",
    "Food": "Food",
    "Snacks": "Snacks",
    "Merch": "Merch",
}

# Staffing rules per stand based on expected traffic
STAFFING_RULES = {
    "low": {"threshold": 2000, "staff_per_stand": 2, "buffer_pct": 0.10},
    "medium": {"threshold": 3500, "staff_per_stand": 3, "buffer_pct": 0.15},
    "high": {"threshold": 5000, "staff_per_stand": 3, "buffer_pct": 0.25},
    "playoff": {"threshold": 99999, "staff_per_stand": 4, "buffer_pct": 0.30},
}
