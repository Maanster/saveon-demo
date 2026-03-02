"""
Price lookup for Royals Concession Intelligence Platform.
Resolves item + price_point_name to estimated price using KNOWN_PRICES and CATEGORY_PRICES.
"""
from config import KNOWN_PRICES, CATEGORY_PRICES


def get_price(item: str, price_point_name: str, category: str) -> float:
    """
    Look up estimated price for an item.
    Tries (item, price_point_name), then (item, ""), then category fallback.
    """
    # Exact match
    key = (item, price_point_name)
    if key in KNOWN_PRICES:
        return KNOWN_PRICES[key]
    # Item with empty price point
    key_empty = (item, "")
    if key_empty in KNOWN_PRICES:
        return KNOWN_PRICES[key_empty]
    # Category fallback
    if category in CATEGORY_PRICES:
        return CATEGORY_PRICES[category]
    # Final fallback
    return CATEGORY_PRICES.get("Other", 5.00)
