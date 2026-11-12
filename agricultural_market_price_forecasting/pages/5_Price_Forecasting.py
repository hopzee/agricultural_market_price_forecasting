
import streamlit as st
import pandas as pd
import plotly.express as px

from src.ui import init_state, page_header
from src.models.forecasting import forecast_future
from src.data.preprocessing import series_profile

# Initialize session variables
init_state()

page_header(
    "Price Forecasting",
    "Generate future monthly estimates from an eligible historical series."
)

monthly = st.session_state.monthly_df

if monthly is None or monthly.empty:
    st.warning("Prepare monthly data in Data Explorer first.")
    st.stop()

profile = series_profile(monthly)

if profile.empty:
    st.warning("No eligible monthly series are available for forecasting.")
    st.stop()

key = st.selectbox(
    "Select exact series",
    profile.series_key.tolist()
)

g = monthly[monthly.series_key == key].copy()
g = g.sort_values("month")

series = (
    g.set_index("month")["price"]
    .asfreq("MS")
)

if series.isna().any():
    st.error(
        "This series has missing months. Forecasting is disabled "
        "rather than silently filling missing target values."
    )
    st.stop()

if len(series) < 24:
    st.error("At least 24 monthly observations are required.")
    st.stop()

model = st.selectbox(
    "Forecasting method",
    ["SARIMAX", "XGBoost", "LightGBM", "Naïve", "Seasonal naïve"]
)

horizon = st.slider(
    "Forecast horizon (months)",
    min_value=1,
    max_value=18,
    value=6
)

if st.button("Generate forecast", type="primary"):
    try:
        result = forecast_future(series, model, horizon)

        st.session_state.forecast_results[key] = {
            "model": model,
            "data": result
        }

        st.success("Forecast generated successfully.")

    except Exception as e:
        st.error(f"Forecast could not be generated: {e}")

saved = st.session_state.forecast_results.get(key)

if saved:
    fc = saved["data"]

    st.success(f"Forecast generated using {saved['model']}.")

    hist = pd.DataFrame({
        "month": series.index,
        "price": series.values
    })

    hist["kind"] = "Observed"

    pred = fc.rename(
        columns={"forecast_price": "price"}
    ).copy()

    pred["kind"] = "Forecast"

    combined = pd.concat(
        [hist, pred],
        ignore_index=True
    )

    fig = px.line(
        combined,
        x="month",
        y="price",
        color="kind",
        markers=True,
        title="Historical prices and future forecast"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("Forecast values")

    st.dataframe(
        fc,
        use_container_width=True
    )

    st.download_button(
        "Download forecast CSV",
        fc.to_csv(index=False).encode("utf-8-sig"),
        "future_price_forecast.csv",
        "text/csv"
    )

    st.caption(
        "Forecasts extrapolate historical price patterns. They are not "
        "guarantees and do not include external economic or weather variables."
    )

else:
    st.info(
        "No forecast has been generated for this series yet. "
        "Choose a forecasting method and click Generate forecast."
    )
