import streamlit as st
from src.ui import page_header
from src.utils import read_uploaded_file
from src.data.schema import suggest_mapping

page_header("Overview", "Upload and inspect the original WFP Nigeria food-price file.")
st.markdown("""
**Research focus:** monthly agricultural market-price forecasting in Nigeria.
The target is the reported food price, not market arrivals, crop yield or consumer demand.
""")
uploaded = st.file_uploader("Upload WFP Nigeria food-price dataset", type=["csv","xlsx","xls"])
if uploaded:
    try:
        df = read_uploaded_file(uploaded)
        st.session_state.raw_df = df
        st.session_state.dataset_name = uploaded.name
        st.session_state.column_map = suggest_mapping(df.columns)
        st.session_state.clean_df = None
        st.session_state.monthly_df = None
        st.success(f"Loaded {len(df):,} rows and {len(df.columns)} columns from {uploaded.name}.")
    except Exception as e:
        st.error(f"Could not read the file: {e}")
if st.session_state.raw_df is not None:
    df = st.session_state.raw_df
    a,b,c = st.columns(3)
    a.metric("Source rows", f"{len(df):,}")
    b.metric("Source columns", len(df.columns))
    c.metric("Dataset file", st.session_state.dataset_name or "Uploaded")
    st.subheader("Source preview")
    st.dataframe(df.head(15), use_container_width=True)
    st.caption("The uploaded source is retained separately. Processing creates a working copy and does not overwrite the original.")
    st.info("Next: open **Data Explorer** to confirm the automatically suggested column mapping and prepare the monthly series.")
else:
    st.info("No data loaded yet. Upload the actual WFP CSV to begin.")
