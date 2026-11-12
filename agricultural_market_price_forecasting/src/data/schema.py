import re
import pandas as pd

ALIASES = {
    "date": ["date", "month", "time", "period"],
    "market": ["market", "market_name", "location", "city"],
    "admin1": ["admin1", "state", "province", "region"],
    "admin2": ["admin2", "lga", "district", "county"],
    "commodity": ["commodity", "product", "item", "food"],
    "unit": ["unit", "measurement", "measure"],
    "price_type": ["pricetype", "price_type", "price type", "type"],
    "price": ["price", "value", "usdprice", "localprice", "price_value"],
    "currency": ["currency"],
}

def normalise_name(value):
    return re.sub(r"[^a-z0-9]+", "", str(value).strip().lower())

def suggest_mapping(columns):
    result = {}
    for target, aliases in ALIASES.items():
        normal_aliases = {normalise_name(a) for a in aliases}
        matches = [c for c in columns if normalise_name(c) in normal_aliases]
        result[target] = matches[0] if matches else None
    return result

def validate_mapping(mapping):
    required = ["date", "commodity", "unit", "price"]
    missing = [x for x in required if not mapping.get(x)]
    if missing:
        raise ValueError("Map these required fields before processing: " + ", ".join(missing))
