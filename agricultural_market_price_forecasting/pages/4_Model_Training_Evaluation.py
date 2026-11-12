
import streamlit as st
import pandas as pd
import plotly.express as px

from src.ui import init_state, page_header
from src.models.forecasting import evaluate_series
from src.data.preprocessing import series_profile

# Initialize session variables
init_state()

page_header(
    "Model Training & Evaluation",
    "Chronological validation and held-out test comparison."
)

monthly = st.session_state.monthly_df

if monthly is None or monthly.empty:
    st.warning("Prepare monthly data in Data Explorer first.")
    st.stop()

profile = series_profile(monthly)

if profile.empty:
    st.warning("No eligible monthly series are available for evaluation.")
    st.stop()

key = st.selectbox(
    "Choose series to evaluate",
    profile.series_key.tolist()
)

g = monthly[monthly.series_key == key].copy()
g = g.sort_values("month")

series = (
    g.set_index("month")["price"]
    .asfreq("MS")
)

# Missing months remain missing; do not interpolate or score imputed values.
st.caption(
    f"{series.notna().sum()} observed monthly values · "
    f"{series.index.min().date()} to {series.index.max().date()}"
)

model_options = ["Naïve", "SARIMAX", "XGBoost", "LightGBM"]

if len(series.dropna()) >= 48:
    model_options.insert(1, "Seasonal naïve")

selected = st.multiselect(
    "Models to compare",
    model_options,
    default=model_options
)

st.warning(
    "The current implementation requires a continuous monthly series "
    "for model fitting. Missing months are not imputed; choose a series "
    "with complete monthly coverage."
)

if st.button("Run chronological evaluation", type="primary"):
    try:
        if not selected:
            raise ValueError("Select at least one model to evaluate.")

        if series.isna().any():
            raise ValueError(
                "This series contains missing months. The application "
                "will not silently interpolate them. Select a complete "
                "series or inspect its coverage."
            )

        result = evaluate_series(series, selected)

        st.session_state.model_results[key] = result

        st.success(
            "Evaluation complete. Validation-selected model: "
            f"{result['selected_model']}"
        )

    except Exception as e:
        st.error(f"Evaluation could not be completed: {e}")

result = st.session_state.model_results.get(key)

if result:
    st.subheader("Validation results")

    st.dataframe(
        result["validation"],
        use_container_width=True
    )

    st.metric(
        "Selected using validation MAE",
        result["selected_model"]
    )

    st.subheader("Untouched test-period comparison")

    st.dataframe(
        result["test_comparison"],
        use_container_width=True
    )

    comp = result["test_comparison"].dropna(subset=["MAE"])

    if not comp.empty:
        fig = px.bar(
            comp,
            x="model",
            y="MAE",
            title="Test MAE by model"
        )

        st.plotly_chart(fig, use_container_width=True)

    predictions = result["predictions"]

    if predictions is not None and not predictions.empty:
        st.subheader("Observed vs predicted on test period")

        fig = px.line(
            predictions,
            x="month",
            y=["actual", "predicted"],
            markers=True
        )

        st.plotly_chart(fig, use_container_width=True)

        st.download_button(
            "Download test predictions",
            predictions.to_csv(index=False).encode("utf-8-sig"),
            "test_predictions.csv",
            "text/csv"
        )

    st.caption(
        "Validation MAE selects the model. Test metrics are reported "
        "only after selection. Results are not pre-filled or fabricated."
    )
else:
    st.info(
        "No evaluation results are available for this series yet. "
        "Select your models and run chronological evaluation."
    )
