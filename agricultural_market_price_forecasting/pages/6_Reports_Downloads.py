import streamlit as st
import pandas as pd
from src.ui import page_header

page_header("Reports & Downloads", "Export prepared data and verified outputs for research documentation.")
if st.session_state.monthly_df is None:
    st.info("Prepare the dataset in Data Explorer to enable downloads.")
else:
    st.download_button("Download cleaned observations", st.session_state.clean_df.to_csv(index=False).encode("utf-8-sig"),
                       "cleaned_price_observations.csv", "text/csv")
    st.download_button("Download monthly series", st.session_state.monthly_df.to_csv(index=False).encode("utf-8-sig"),
                       "monthly_price_series.csv", "text/csv")
if st.session_state.model_results:
    st.subheader("Model evaluation exports")
    for i,(key,res) in enumerate(st.session_state.model_results.items()):
        st.markdown(f"**{key}**")
        st.download_button(f"Download test comparison · {i+1}", res["test_comparison"].to_csv(index=False).encode("utf-8-sig"),
                           f"comparison_{i+1}.csv", "text/csv", key=f"comp_{i}")
        st.download_button(f"Download test predictions · {i+1}", res["predictions"].to_csv(index=False).encode("utf-8-sig"),
                           f"predictions_{i+1}.csv", "text/csv", key=f"pred_{i}")
if st.session_state.forecast_results:
    st.subheader("Forecast exports")
    for i,(key,res) in enumerate(st.session_state.forecast_results.items()):
        st.download_button(f"Download forecast · {i+1}", res["data"].to_csv(index=False).encode("utf-8-sig"),
                           f"forecast_{i+1}.csv", "text/csv", key=f"forecast_{i}")
st.info("For academic reporting, use the actual exported metrics and predictions. Do not report model rankings until the experiments have run successfully.")
