import streamlit as st
import platform
import pandas as pd
from src.ui import page_header

page_header("System Information", "Implementation details, assumptions and limitations.")
st.subheader("Research specification")
st.write({
    "Dataset":"WFP Nigeria food-price CSV supplied for the study",
    "Commodity groups":["Maize","Rice","Garri/cassava products","Tomatoes"],
    "Target":"Reported market price",
    "Models":["SARIMAX","XGBoost","LightGBM"],
    "Benchmark":"Naïve; seasonal-naïve where annual history is adequate",
    "Validation":"Chronological train/validation/test; expanding-window design",
    "Metrics":["MAE","RMSE","MAPE with zero handling"],
    "Interface":"Streamlit",
})
st.subheader("Data handling safeguards")
st.markdown("""
- The source upload is retained unchanged in the current session.
- Original commodity labels and variants are retained for traceability.
- Market, retail/wholesale price type, unit and currency remain separate.
- Monthly aggregation uses the median within each exact series.
- Missing months are identified and are not automatically interpolated.
- Random train/test shuffling is not used.
- Validation data selects the model; the test period is held out.
- External explanatory variables are not assumed or fabricated.
""")
st.subheader("Runtime")
st.write({"Python":platform.python_version(),"Pandas":pd.__version__,"Streamlit":st.__version__})
st.warning("Streamlit Community Cloud has ephemeral local storage. Uploaded data and session-trained models should be exported or reloaded after a restart. This application does not claim permanent cloud storage.")
