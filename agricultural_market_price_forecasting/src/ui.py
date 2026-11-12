import streamlit as st

def init_state():
    defaults = {
        "raw_df": None, "clean_df": None, "monthly_df": None,
        "column_map": {}, "cleaning_log": [], "model_results": {},
        "forecast_results": {}, "selected_series_key": None,
        "dataset_name": None, "last_profile": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def page_header(title, subtitle=None):
    st.title(title)
    if subtitle:
        st.caption(subtitle)

def require_data():
    if st.session_state.get("raw_df") is None:
        st.warning("Upload the WFP Nigeria food-price CSV on the Overview page first.")
        st.stop()
    return st.session_state.raw_df
