import streamlit as st
import pandas as pd
import plotly.express as px

# =======================================
# POWER BI web-style UI configuration
# =======================================
st.set_page_config(
    page_title="PowerBI Web Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# THEME COLORS
MAIN_COLOR = "#1f77b4"
CARD_BG = "#f5f7fa"
CARD_BORDER = "#d6d6d6"

# =======================================
# DATA LOADING + CLEANING
# =======================================
@st.cache_data
def load_data(file):
    df = pd.read_excel(file)
    df = df.loc[:, ~df.columns.str.contains("Unnamed")]
    df.columns = df.columns.str.strip()

    # Numeric cleanup
    def clean_num(s):
        return pd.to_numeric(s.astype(str).str.replace(r'[^0-9.\-]', '', regex=True), errors="coerce")

    for col in ["NS (M EUR)", "Volume", "# SKUs"]:
        if col in df.columns:
            df[col] = clean_num(df[col])

    # Dates
    for col in df.columns:
        if "date" in col.lower() or "launch" in col.lower():
            df[col] = pd.to_datetime(df[col], errors="ignore")

    return df

# =======================================
# SIDEBAR
# =======================================
st.sidebar.title("📌 PowerBI Web Filters")

uploaded_file = st.sidebar.file_uploader("Upload Excel File", type=["xlsx"])

if not uploaded_file:
    st.warning("Please upload your Projects Excel file.")
    st.stop()

df = load_data(uploaded_file)

# FILTERS
cbus = st.sidebar.multiselect("CBU", df["CBU"].dropna().unique())
brands = st.sidebar.multiselect("Brand", df["Brand"].dropna().unique())
types = st.sidebar.multiselect("Type", df["Type of Project"].dropna().unique())
phases = st.sidebar.multiselect("Phase", df["Project Phase"].dropna().unique())

df_f = df.copy()
if cbus: df_f = df_f[df_f["CBU"].isin(cbus)]
if brands: df_f = df_f[df_f["Brand"].isin(brands)]
if types: df_f = df_f[df_f["Type of Project"].isin(types)]
if phases: df_f = df_f[df_f["Project Phase"].isin(phases)]

# =======================================
# KPI CARDS (Power BI Style)
# =======================================
st.markdown("## 📊 Portfolio Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Projects", len(df_f))
col2.metric("CBUs", df_f["CBU"].nunique())
col3.metric("Brands", df_f["Brand"].nunique())
col4.metric("Avg NS (M EUR)", round(df_f["NS (M EUR)"].mean(skipna=True), 2))

# =======================================
# CHARTS LAYOUT GRID (Power BI Style)
# =======================================
st.markdown("---")

row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("Projects by CBU")
    fig = px.bar(df_f, x="CBU", color="CBU", title="")
    st.plotly_chart(fig, use_container_width=True)

with row1_col2:
    st.subheader("Projects by Type")
    fig = px.bar(
        df_f["Type of Project"].value_counts(),
        labels={"index": "Type", "value": "Count"}
    )
    st.plotly_chart(fig, use_container_width=True)

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("Projects by Phase")
    fig = px.bar(
        df_f["Project Phase"].value_counts(),
        labels={"index": "Phase", "value": "Count"}
    )
    st.plotly_chart(fig, use_container_width=True)

with row2_col2:
    if "NS (M EUR)" in df_f.columns:
        st.subheader("Top 10 Projects by NS")
        df_ns = df_f.sort_values("NS (M EUR)", ascending=False).head(10)
        fig = px.bar(
            df_ns,
            x="NS (M EUR)",
            y="Project Name",
            orientation="h",
            color="CBU"
        )
        st.plotly_chart(fig, use_container_width=True)

# =======================================
# FOOTER
# =======================================
st.markdown("---")
st.markdown("""
### 👨‍💼 R&I Indonesia – Professional PowerBI Web Dashboard  
Built with Python + Streamlit + Plotly  
""")
