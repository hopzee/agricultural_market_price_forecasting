import warnings
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from src.features.build import make_features, recursive_feature_row

def metrics(actual, predicted):
    a = np.asarray(actual, dtype=float); p = np.asarray(predicted, dtype=float)
    valid = np.isfinite(a) & np.isfinite(p)
    a, p = a[valid], p[valid]
    if len(a) == 0:
        return {"MAE":np.nan, "RMSE":np.nan, "MAPE":np.nan, "MAPE_n":0, "n":0}
    nonzero = a != 0
    mape = float(np.mean(np.abs((a[nonzero]-p[nonzero])/a[nonzero]))*100) if nonzero.any() else np.nan
    return {"MAE":float(mean_absolute_error(a,p)),
            "RMSE":float(np.sqrt(mean_squared_error(a,p))),
            "MAPE":mape, "MAPE_n":int(nonzero.sum()), "n":len(a)}

def split_series(s, test_fraction=0.2, validation_fraction=0.15):
    s = s.dropna().sort_index()
    n = len(s)
    test_n = max(2, int(np.ceil(n*test_fraction)))
    val_n = max(2, int(np.ceil((n-test_n)*validation_fraction)))
    if n - test_n - val_n < 24 or n < 36:
        raise ValueError("At least 36 monthly observations are required for this training/validation/test design.")
    return s.iloc[:n-test_n-val_n], s.iloc[n-test_n-val_n:n-test_n], s.iloc[n-test_n:]

def _tree_model(kind, y_train, params=None):
    params = params or {}
    if kind == "XGBoost":
        from xgboost import XGBRegressor
        return XGBRegressor(
            n_estimators=int(params.get("n_estimators",300)),
            max_depth=int(params.get("max_depth",3)),
            learning_rate=float(params.get("learning_rate",0.03)),
            subsample=0.9, colsample_bytree=0.9,
            objective="reg:squarederror", random_state=42, n_jobs=2,
        )
    if kind == "LightGBM":
        from lightgbm import LGBMRegressor
        return LGBMRegressor(
            n_estimators=int(params.get("n_estimators",300)),
            num_leaves=int(params.get("num_leaves",15)),
            learning_rate=float(params.get("learning_rate",0.03)),
            max_depth=-1, verbosity=-1, random_state=42, n_jobs=2,
        )
    raise ValueError(f"Unsupported tree model: {kind}")


def fit_tree_predict(train, target_dates, kind, params=None):
    x = make_features(train).dropna()
    if len(x) < 12:
        raise ValueError("Not enough lagged observations for tree model.")
    model = _tree_model(kind, train)
    model.fit(x, train.loc[x.index])
    history = list(train.astype(float).values)
    preds = []
    for date in target_dates:
        row = recursive_feature_row(history, date)
        if row.isna().any(axis=None):
            raise ValueError("Insufficient history for recursive feature generation.")
        pred = float(model.predict(row[x.columns])[0])
        preds.append(pred); history.append(pred)
    return np.asarray(preds), model

def fit_sarimax_predict(train, target_dates):
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    seasonal = (1,1,1,12) if len(train) >= 48 else (0,0,0,0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = SARIMAX(train.astype(float), order=(1,1,1), seasonal_order=seasonal,
                        enforce_stationarity=False, enforce_invertibility=False)
        fitted = model.fit(disp=False, maxiter=150)
        pred = fitted.get_forecast(steps=len(target_dates)).predicted_mean
    return np.asarray(pred, dtype=float), fitted

def walk_forward_predict(initial_history, target, model_name):
    """One-step-ahead expanding-window predictions; actuals enter history only after each forecast."""
    history = initial_history.copy().astype(float)
    predictions = []
    for date, actual in target.items():
        if model_name == "Naïve":
            pred = float(history.iloc[-1])
        elif model_name == "Seasonal naïve":
            pred = float(history.iloc[-12]) if len(history) >= 12 else float(history.iloc[-1])
        elif model_name == "SARIMAX":
            pred_arr, _ = fit_sarimax_predict(history, [date])
            pred = float(pred_arr[0])
        else:
            pred_arr, _ = fit_tree_predict(history, [date], model_name)
            pred = float(pred_arr[0])
        predictions.append(pred)
        history.loc[date] = float(actual)
    return np.asarray(predictions)

def evaluate_series(series, models=None):
    models = models or ["Naïve", "SARIMAX", "XGBoost", "LightGBM"]
    s = series.dropna().sort_index()
    n = len(s)
    test_n = max(2, int(np.ceil(n*0.2)))
    val_n = max(2, int(np.ceil((n-test_n)*0.15)))
    if n - test_n - val_n < 36 or n < 48:
        raise ValueError("At least 48 continuous monthly observations are required for the expanding-window train/validation/test design.")
    train = s.iloc[:n-test_n-val_n]
    val = s.iloc[n-test_n-val_n:n-test_n]
    test = s.iloc[n-test_n:]
    # Validation walk-forward: each forecast uses only information available at its origin.
    validation_rows = []
    for name in models:
        try:
            p = walk_forward_predict(train, val, name)
            validation_rows.append({"model":name, **metrics(val.values, p)})
        except Exception as e:
            validation_rows.append({"model":name, "MAE":np.nan, "RMSE":np.nan, "MAPE":np.nan,
                                    "MAPE_n":0, "n":0, "error":str(e)})
    valid = [r for r in validation_rows if np.isfinite(r["MAE"])]
    if not valid:
        raise ValueError("All candidate models failed on validation. Check installed dependencies and series length.")
    selected = min(valid, key=lambda r:r["MAE"])["model"]
    development = pd.concat([train, val])
    # Final test walk-forward: test observations are revealed only after each one-step prediction.
    comparison = []
    test_predictions = {}
    for name in models:
        try:
            p = walk_forward_predict(development, test, name)
            test_predictions[name] = p
            comparison.append({"model":name, **metrics(test.values,p)})
        except Exception as e:
            comparison.append({"model":name,"MAE":np.nan,"RMSE":np.nan,"MAPE":np.nan,
                               "MAPE_n":0,"n":0,"error":str(e)})
    if selected not in test_predictions:
        raise ValueError(f"The validation-selected model ({selected}) failed during test evaluation.")
    pred_df = pd.DataFrame({"month":test.index, "actual":test.values,
                            "predicted":test_predictions[selected]})
    test_metrics = metrics(test.values, test_predictions[selected])
    return {"selected_model":selected, "validation":pd.DataFrame(validation_rows),
            "test_metrics":test_metrics, "test_comparison":pd.DataFrame(comparison),
            "predictions":pred_df, "train":train, "validation_series":val, "test":test}


def forecast_future(series, model_name, horizon=6):
    s = series.dropna().sort_index().astype(float)
    if len(s) < 24:
        raise ValueError("At least 24 monthly observations are required for future forecasting.")
    dates = pd.date_range(s.index.max()+pd.offsets.MonthBegin(1), periods=horizon, freq="MS")
    if model_name == "Naïve":
        preds = np.repeat(float(s.iloc[-1]), horizon)
    elif model_name == "Seasonal naïve":
        preds = np.array([float(s.iloc[-12 + (i % 12)]) for i in range(horizon)])
    elif model_name == "SARIMAX":
        preds, _ = fit_sarimax_predict(s, dates)
    else:
        preds, _ = fit_tree_predict(s, dates, model_name)
    return pd.DataFrame({"month":dates, "forecast_price":preds})
