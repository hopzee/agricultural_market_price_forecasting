import numpy as np
import pandas as pd

LAGS = [1, 2, 3, 6, 12]
WINDOWS = [3, 6, 12]

def make_features(series):
    s = series.sort_index().astype(float)
    x = pd.DataFrame(index=s.index)
    for lag in LAGS:
        x[f"lag_{lag}"] = s.shift(lag)
    for window in WINDOWS:
        shifted = s.shift(1)
        x[f"rolling_mean_{window}"] = shifted.rolling(window, min_periods=window).mean()
        x[f"rolling_std_{window}"] = shifted.rolling(window, min_periods=window).std()
    x["month"] = x.index.month
    x["year"] = x.index.year
    x["month_sin"] = np.sin(2*np.pi*x.index.month/12)
    x["month_cos"] = np.cos(2*np.pi*x.index.month/12)
    return x.replace([np.inf, -np.inf], np.nan)

def recursive_feature_row(history, date):
    vals = list(np.asarray(history, dtype=float))
    row = {}
    for lag in LAGS:
        row[f"lag_{lag}"] = vals[-lag] if len(vals) >= lag else np.nan
    for window in WINDOWS:
        if len(vals) >= window:
            arr = np.asarray(vals[-window:])
            row[f"rolling_mean_{window}"] = float(arr.mean())
            row[f"rolling_std_{window}"] = float(arr.std(ddof=1)) if window > 1 else 0.0
        else:
            row[f"rolling_mean_{window}"] = np.nan
            row[f"rolling_std_{window}"] = np.nan
    row.update({"month":date.month, "year":date.year,
                "month_sin":np.sin(2*np.pi*date.month/12),
                "month_cos":np.cos(2*np.pi*date.month/12)})
    return pd.DataFrame([row])
