import io
import json
import pandas as pd

def csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8-sig")

def json_bytes(payload):
    def clean(v):
        if hasattr(v, "isoformat"): return v.isoformat()
        if hasattr(v, "item"): return v.item()
        return str(v)
    return json.dumps(payload, indent=2, default=clean, allow_nan=False).encode("utf-8")
