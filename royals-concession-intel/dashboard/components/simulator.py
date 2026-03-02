"""
Game Simulator Logic Engine.
Distributes predicted demand across game periods with realistic timing curves.
"""
import numpy as np
import math

# Period distribution derived from actual transaction data analysis
PERIOD_DISTRIBUTION = {
    "pre_game": 0.15,
    "1st_period": 0.10,
    "1st_intermission": 0.22,
    "2nd_period": 0.08,
    "2nd_intermission": 0.20,
    "3rd_period": 0.12,
    "post_game": 0.13,
}

# Duration of each period in minutes
PERIOD_DURATION = {
    "pre_game": 124,        # 5:00 PM - 7:04 PM
    "1st_period": 20,       # 7:05 - 7:24
    "1st_intermission": 20, # 7:25 - 7:44
    "2nd_period": 20,       # 7:45 - 8:04
    "2nd_intermission": 20, # 8:05 - 8:24
    "3rd_period": 35,       # 8:25 - 8:59
    "post_game": 60,        # 9:00 - 10:00
}

PERIOD_ORDER = [
    "pre_game", "1st_period", "1st_intermission",
    "2nd_period", "2nd_intermission", "3rd_period", "post_game",
]

PERIOD_DISPLAY = {
    "pre_game": "Pre-Game",
    "1st_period": "1st Period",
    "1st_intermission": "1st Intermission",
    "2nd_period": "2nd Period",
    "2nd_intermission": "2nd Intermission",
    "3rd_period": "3rd Period",
    "post_game": "Post-Game",
}

# Start time of each period as (hour, minute) in 24-h format
PERIOD_START_TIME = {
    "pre_game": (17, 0),
    "1st_period": (19, 5),
    "1st_intermission": (19, 25),
    "2nd_period": (19, 45),
    "2nd_intermission": (20, 5),
    "3rd_period": (20, 25),
    "post_game": (21, 0),
}


def distribute_demand_by_period(total_units, by_category=None):
    """
    Split total demand into per-period amounts.
    Returns dict: {period: {"total": int, "by_category": {cat: int}}}
    """
    result = {}
    for period, pct in PERIOD_DISTRIBUTION.items():
        period_total = int(round(total_units * pct))
        period_cats = {}
        if by_category:
            cat_total_predicted = sum(by_category.values()) or 1
            for cat, cat_units in by_category.items():
                cat_pct = cat_units / cat_total_predicted
                period_cats[cat] = int(round(period_total * cat_pct))
        result[period] = {"total": period_total, "by_category": period_cats}
    return result


def generate_transaction_stream(period_units, period_minutes, is_intermission=False):
    """
    Generate a list of (minute_offset, units) tuples simulating realistic timing.
    Intermissions use a bell curve (peak in middle).
    Regular periods use a slight front-load.
    Returns list of (minute, units) sorted by minute.
    """
    if period_units <= 0 or period_minutes <= 0:
        return []

    minutes = list(range(period_minutes))

    if is_intermission:
        # Bell curve centered at middle of intermission
        center = period_minutes / 2
        sigma = period_minutes / 4
        weights = [math.exp(-0.5 * ((m - center) / sigma) ** 2) for m in minutes]
    else:
        # Slight front-load with some randomness
        weights = [max(0.3, 1.0 - (m / period_minutes) * 0.5) for m in minutes]

    # Normalize weights
    total_weight = sum(weights)
    weights = [w / total_weight for w in weights]

    # Distribute units across minutes
    stream = []
    remaining = period_units
    for i, minute in enumerate(minutes):
        if i == len(minutes) - 1:
            units = remaining
        else:
            units = int(round(period_units * weights[i]))
            # Add some noise
            noise = np.random.randint(-max(1, units // 4), max(2, units // 4 + 1))
            units = max(0, units + noise)
            remaining -= units

        if units > 0:
            stream.append((minute, units))

    # Make sure remaining is accounted for
    if remaining > 0 and stream:
        last_min, last_units = stream[-1]
        stream[-1] = (last_min, last_units + remaining)

    return stream


def distribute_to_stands(units, stand_names, by_category=None):
    """
    Distribute units across open stands with some variation.
    Returns dict: {stand_name: {"total": int, "by_category": {cat: int}}}
    """
    n_stands = len(stand_names)
    if n_stands == 0:
        return {}

    # Weighted distribution - first stand gets more (main canteen)
    weights = np.array([1.5 if i == 0 else 1.0 for i in range(n_stands)])
    weights = weights / weights.sum()

    result = {}
    for i, stand in enumerate(stand_names):
        stand_units = int(round(units * weights[i]))
        stand_cats = {}
        if by_category:
            cat_total = sum(by_category.values()) or 1
            for cat, cat_units in by_category.items():
                cat_pct = cat_units / cat_total
                stand_cats[cat] = int(round(stand_units * cat_pct))
        result[stand] = {"total": stand_units, "by_category": stand_cats}

    return result


def format_game_clock(period, minute_offset):
    """
    Convert a period name and minute offset into a display time string (HH:MM).
    Returns a 12-hour formatted time like '7:25 PM'.
    """
    start_h, start_m = PERIOD_START_TIME[period]
    total_minutes = start_h * 60 + start_m + minute_offset
    hour = (total_minutes // 60) % 24
    minute = total_minutes % 60
    # 12-hour format
    suffix = "PM" if hour >= 12 else "AM"
    display_hour = hour % 12
    if display_hour == 0:
        display_hour = 12
    return f"{display_hour}:{minute:02d} {suffix}"
