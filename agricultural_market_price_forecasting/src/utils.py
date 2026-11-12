import pandas as pd

def read_uploaded_file(uploaded):
    name = uploaded.name.lower()
    if name.endswith(".csv"):
        # WFP exports can contain a metadata preamble; inspect both standard and first-row headers.
        try:
            df = pd.read_csv(uploaded, low_memory=False)
        except UnicodeDecodeError:
            uploaded.seek(0)
            df = pd.read_csv(uploaded, encoding="latin-1", low_memory=False)
        if len(df.columns) == 1:
            uploaded.seek(0)
            df = pd.read_csv(uploaded, sep=None, engine="python")
        return df
    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded)
    raise ValueError("Upload a CSV or Excel file.")
