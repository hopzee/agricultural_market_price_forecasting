import pandas as pd
import numpy as np
from .schema import validate_mapping

COMMODITY_RULES = {
    "Maize": ["maize", "corn"],
    "Rice": ["rice"],
    "Garri/cassava products": ["garri", "gari", "cassava"],
    "Tomatoes": ["tomato"],
}

def classify_commodity(value):
    text = str(value).strip().lower()
    for group, terms in COMMODITY_RULES.items():
        if any(term in text for term in terms):
            return group
    return None

def prepare_data(raw, mapping, keep_unmapped=False):
    validate_mapping(mapping)
    df = raw.copy()
    log = []
    selected = {k: v for k, v in mapping.items() if v and v in df.columns}
    out = pd.DataFrame(index=df.index)
    for target, source in selected.items():
        out[target] = df[source]
    out["source_row"] = np.arange(len(out))
    before = len(out)
    out["date"] = pd.to_datetime(out["date"], errors="coerce", dayfirst=False)
    out["price"] = pd.to_numeric(out["price"].astype(str).str.replace(",", "", regex=False), errors="coerce")
    bad = out["date"].isna() | out["price"].isna() | (out["price"] < 0)
    log.append({"step":"Invalid date/price removal", "rows_removed":int(bad.sum()), "rows_remaining":int((~bad).sum())})
    out = out.loc[~bad].copy()
    out["commodity_original"] = out["commodity"].astype(str).str.strip()
    duplicate_fields = ["date", "market", "admin1", "admin2", "commodity_original",
                        "unit", "price_type", "currency", "price"]
    duplicate_fields = [c for c in duplicate_fields if c in out.columns]
    duplicate_mask = out.duplicated(subset=duplicate_fields, keep="first")
    log.append({"step":"Exact duplicate assessment", "rows_removed":int(duplicate_mask.sum()),
                "rows_remaining":int((~duplicate_mask).sum())})
    out = out.loc[~duplicate_mask].copy()
    out["commodity_group"] = out["commodity_original"].map(classify_commodity)
    if not keep_unmapped:
        mask = out["commodity_group"].isna()
        log.append({"step":"Outside selected commodity groups", "rows_removed":int(mask.sum()), "rows_remaining":int((~mask).sum())})
        out = out.loc[~mask].copy()
    else:
        out["commodity_group"] = out["commodity_group"].fillna("Other / unmapped")
    for col in ["market", "admin1", "admin2", "unit", "price_type", "currency"]:
        if col not in out:
            out[col] = "Not supplied"
        out[col] = out[col].fillna("Not supplied").astype(str).str.strip()
        out.loc[out[col].isin(["", "nan", "None"]), col] = "Not supplied"
    out["month"] = out["date"].dt.to_period("M").dt.to_timestamp()
    # Preserve product variants and source labels; no automatic unit conversion.
    out["series_key"] = (
        out["commodity_group"].astype(str) + " | " +
        out["commodity_original"].astype(str) + " | " +
        out["admin1"].astype(str) + " | " +
        out["admin2"].astype(str) + " | " +
        out["market"].astype(str) + " | " +
        out["price_type"].astype(str) + " | " +
        out["unit"].astype(str) + " | " +
        out["currency"].astype(str)
    )
    log.append({"step":"Prepared records", "rows_removed":0, "rows_remaining":len(out)})
    return out.reset_index(drop=True), log

def aggregate_monthly(clean):
    if clean is None or clean.empty:
        return pd.DataFrame()
    keys = ["series_key","commodity_group","commodity_original","market","admin1","admin2","price_type","unit","currency","month"]
    monthly = (clean.groupby(keys, dropna=False)
               .agg(price=("price","median"), observations=("price","size"))
               .reset_index()
               .sort_values(["series_key","month"]))
    return monthly

def series_profile(monthly):
    if monthly.empty:
        return pd.DataFrame()
    rows = []
    for key, g in monthly.groupby("series_key"):
        idx = pd.date_range(g.month.min(), g.month.max(), freq="MS")
        missing = len(idx.difference(pd.DatetimeIndex(g.month)))
        rows.append({
            "series_key":key, "commodity_group":g.commodity_group.iloc[0],
            "market":g.market.iloc[0], "state":g.admin1.iloc[0], "admin2":g.admin2.iloc[0],
            "price_type":g.price_type.iloc[0],
            "unit":g.unit.iloc[0], "currency":g.currency.iloc[0],
            "observations":len(g), "missing_months":missing,
            "start":g.month.min().date(), "end":g.month.max().date(),
            "median_price":float(g.price.median())
        })
    return pd.DataFrame(rows)
