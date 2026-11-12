
import streamlit as st
import pandas as pd

from src.ui import init_state, page_header
from src.data.schema import suggest_mapping
from src.data.preprocessing import (
    prepare_data,
    aggregate_monthly,
    series_profile
)

# Initialize session variables
init_state()

page_header(
    "Data Explorer",
    "Validate source fields, clean observations and build monthly series."
)

raw = st.session_state.raw_df

if raw is None:
    st.warning("Upload a dataset on Overview first.")
    st.stop()

st.subheader("1 · Map source columns")

suggested = suggest_mapping(raw.columns)
existing = st.session_state.column_map or suggested

mapping = {}

fields = [
    ("date", "Date *"),
    ("commodity", "Commodity *"),
    ("unit", "Measurement unit *"),
    ("price", "Price *"),
    ("market", "Market"),
    ("admin1", "State / admin level 1"),
    ("admin2", "LGA / admin level 2"),
    ("price_type", "Price type"),
    ("currency", "Currency")
]

cols = st.columns(2)

for i, (key, label) in enumerate(fields):
    options = ["— Not available —"] + list(raw.columns)
    default = existing.get(key)
    idx = options.index(default) if default in options else 0

    choice = cols[i % 2].selectbox(
        label,
        options,
        index=idx,
        key=f"map_{key}"
    )

    mapping[key] = None if choice == options[0] else choice

keep = st.checkbox(
    "Keep records outside the four selected commodity groups for inspection",
    value=False
)

if st.button("Validate and prepare monthly data", type="primary"):
    try:
        clean, log = prepare_data(
            raw,
            mapping,
            keep_unmapped=keep
        )

        monthly = aggregate_monthly(clean)

        st.session_state.column_map = mapping
        st.session_state.clean_df = clean
        st.session_state.monthly_df = monthly
        st.session_state.cleaning_log = log

        # Clear old model and forecast results after data changes
        st.session_state.model_results = {}
        st.session_state.forecast_results = {}
        st.session_state.selected_series_key = None

        st.success(
            f"Prepared {len(clean):,} valid records across "
            f"{monthly.series_key.nunique():,} monthly series."
        )

    except Exception as e:
        st.error(str(e))

if st.session_state.clean_df is not None:
    clean = st.session_state.clean_df
    monthly = st.session_state.monthly_df

    if monthly is not None:
        st.divider()

        st.subheader("2 · Cleaning log")
        st.dataframe(
            pd.DataFrame(st.session_state.cleaning_log),
            use_container_width=True
        )

        st.subheader("3 · Monthly series profile")
        profile = series_profile(monthly)

        st.metric(
            "Eligible series discovered",
            f"{len(profile):,}"
        )

        st.dataframe(profile, use_container_width=True)

        st.subheader("4 · Monthly data preview")
        st.dataframe(
            monthly.head(30),
            use_container_width=True
        )

        st.download_button(
            "Download prepared monthly data (CSV)",
            monthly.to_csv(index=False).encode("utf-8-sig"),
            "prepared_monthly_prices.csv",
            "text/csv"
        )

        st.caption(
            "Product variants, market, price type, unit and currency "
            "remain separate. Monthly median is used within each exact series."
        )
