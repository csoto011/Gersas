import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="PowerBI Web Dashboard", layout="wide")

@st.cache_data
def load_data(file):
    df = pd.read_excel(file)
    df = df.loc[:, ~df.columns.str.contains("Unnamed")]
    df.columns = df.columns.str.strip()
    
    def clean_num(s):
        return pd.to_numeric(s.astype(str).str.replace(r'[^0-9.\-]', '', regex=True), errors="coerce")

    for col in ["NS (M EUR)", "Volume", "# SKUs"]:
        if col in df.columns:
            df[col] = clean_num(df[col])

    for col in df.columns:
        if "date" in col.lower() or "launch" in col.lower():
            df[col] = pd.to_datetime(df[col], errors="ignore")

    return df

st.sidebar.title("📌 Filtros Power BI Web")
uploaded_file = st.sidebar.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if not uploaded_file:
    st.warning("Sube un archivo para continuar")
    st.stop()

df = load_data(uploaded_file)

# Filtros
cbus = st.sidebar.multiselect("CBU", df["CBU"].dropna().unique())
brands = st.sidebar.multiselect("Brand", df["Brand"].dropna().unique())
types = st.sidebar.multiselect("Type of Project", df["Type of Project"].dropna().unique())
phases = st.sidebar.multiselect("Phase", df["Project Phase"].dropna().unique())

df_f = df.copy()
if cbus: df_f = df_f[df_f["CBU"].isin(cbus)]
if brands: df_f = df_f[df_f["Brand"].isin(brands)]
if types: df_f = df_f[df_f["Type of Project"].isin(types)]
if phases: df_f = df_f[df_f["Project Phase"].isin(phases)]

# KPIs
st.markdown("## 📊 Portfolio Overview")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Projects", len(df_f))
c2.metric("CBUs", df_f["CBU"].nunique())
c3.metric("Brands", df_f["Brand"].nunique())
c4.metric("Avg NS (M EUR)", round(df_f["NS (M EUR)"].mean(skipna=True), 2) if "NS (M EUR)" in df_f else 0)

# Charts
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Projects by CBU")
    st.plotly_chart(px.bar(df_f, x="CBU", color="CBU"), use_container_width=True)

with col2:
    st.subheader("Projects by Type")
    st.plotly_chart(px.bar(df_f["Type of Project"].value_counts()), use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Projects by Phase")
    st.plotly_chart(px.bar(df_f["Project Phase"].value_counts()), use_container_width=True)

with col4:
    st.subheader("Top 10 por NS")
    if "NS (M EUR)" in df_f.columns:
        dft = df_f.dropna(subset=["NS (M EUR)"]).sort_values("NS (M EUR)", ascending=False).head(10)
        st.plotly_chart(px.bar(dft, x="NS (M EUR)", y="Project Name", orientation="h", color="CBU"), use_container_width=True)
