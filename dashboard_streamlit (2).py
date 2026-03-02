# AQUI empieza el código real
import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data(file):
    df = pd.read_excel(file)
    df = df.loc[:, ~df.columns.str.contains("Unnamed")]
    df.columns = df.columns.str.strip()

    def to_numeric(series):
        return pd.to_numeric(series.astype(str).str.replace(r'[^0-9.\-]', '', regex=True),
                             errors='coerce')
    for col in ["# SKUs", "NS (M EUR)", "Volume"]:
        if col in df.columns:
            df[col] = to_numeric(df[col])

    for col in df.columns:
        if "date" in col.lower() or "launch" in col.lower():
            df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

st.set_page_config(page_title="Project Portfolio Dashboard", layout="wide")
st.title("📊 Project Portfolio Dashboard (PowerBI/Tableau Style)")

uploaded_file = st.sidebar.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)

    st.sidebar.header("Filtros")

    cbu = st.sidebar.multiselect("CBU", df["CBU"].dropna().unique())
    brand = st.sidebar.multiselect("Marca", df["Brand"].dropna().unique())
    tipo = st.sidebar.multiselect("Tipo", df["Type of Project"].dropna().unique())
    phase = st.sidebar.multiselect("Fase", df["Project Phase"].dropna().unique())

    df_f = df.copy()

    if cbu: df_f = df_f[df_f["CBU"].isin(cbu)]
    if brand: df_f = df_f[df_f["Brand"].isin(brand)]
    if tipo: df_f = df_f[df_f["Type of Project"].isin(tipo)]
    if phase: df_f = df_f[df_f["Project Phase"].isin(phase)]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Proyectos", len(df_f))
    col2.metric("CBUs", df_f["CBU"].nunique())
    col3.metric("Marcas", df_f["Brand"].nunique())

    st.subheader("Projects by CBU")
    st.plotly_chart(px.bar(df_f, x="CBU", color="CBU"), use_container_width=True)

    st.subheader("Projects by Type")
    st.plotly_chart(px.bar(df_f["Type of Project"].value_counts()), use_container_width=True)

    st.subheader("Projects by Phase")
    st.plotly_chart(px.bar(df_f["Project Phase"].value_counts()), use_container_width=True)

else:
    st.info("Sube un archivo Excel para ver el dashboard.")
