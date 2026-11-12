
import streamlit as st
import pandas as pd
from src.ui import init_state, page_header

# Initialize session variables before accessing them
init_state()

page_header(
    "Reports & Downloads",
    "Export prepared data and verified outputs for research documentation."
)

# Download prepared datasets
monthly_df = st.session_state.get("monthly_df")
clean_df = st.session_state.get("clean_df")

if monthly_df is None or monthly_df.empty:
    st.info(
        "Prepare the dataset in Data Explorer first. "
        "Monthly data will become available here after preparation."
    )
else:
    st.subheader("Prepared dataset downloads")

    if clean_df is not None:
        st.download_button(
            "Download cleaned observations",
            clean_df.to_csv(index=False).encode("utf-8-sig"),
            "cleaned_price_observations.csv",
            "text/csv"
        )

    st.download_button(
        "Download monthly series",
        monthly_df.to_csv(index=False).encode("utf-8-sig"),
        "monthly_price_series.csv",
        "text/csv"
    )

# Model evaluation downloads
model_results = st.session_state.get("model_results", {})

if model_results:
    st.subheader("Model evaluation exports")

    for i, (key, res) in enumerate(model_results.items()):
        st.markdown(f"**{key}**")

        st.download_button(
            f"Download test comparison · {i+1}",
            res["test_comparison"].to_csv(index=False).encode("utf-8-sig"),
            f"comparison_{i+1}.csv",
            "text/csv",
            key=f"comp_{i}"
        )

        st.download_button(
            f"Download test predictions · {i+1}",
            res["predictions"].to_csv(index=False).encode("utf-8-sig"),
            f"predictions_{i+1}.csv",
            "text/csv",
            key=f"pred_{i}"
        )
else:
    st.info(
        "No model evaluation results yet. "
        "Run Model Training & Evaluation to generate them."
    )

# Forecast downloads
forecast_results = st.session_state.get("forecast_results", {})

if forecast_results:
    st.subheader("Forecast exports")

    for i, (key, res) in enumerate(forecast_results.items()):
        st.download_button(
            f"Download forecast · {i+1}",
            res["data"].to_csv(index=False).encode("utf-8-sig"),
            f"forecast_{i+1}.csv",
            "text/csv",
            key=f"forecast_{i}"
        )
else:
    st.info(
        "No forecasts generated yet. "
        "Visit Price Forecasting after preparing your data."
    )

st.info(
    "For academic reporting, use actual exported metrics and predictions. "
    "Do not report model rankings until experiments have run successfully."
)
