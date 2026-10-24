
import streamlit as st
import pandas as pd
import plotly.express as px


# 1. KONFIGURASI DASHBOARD
st.set_page_config(
    page_title="Dashboard Kesehatan MVD",
    page_icon="🏥",
    layout="wide"
)

DATA_PATH = "L0225002_UTSMVD_dataclean.xlsx"

st.title("🏥 Dashboard Kesehatan")
st.caption(
    "Dashboard interaktif penjualan jas hujan, "
    "analisis penjualan, omzet, laba dan rugi."
)


# 2. MEMBACA DATA HASIL CLEANING
@st.cache_data
def load_data():
    df = pd.read_excel(DATA_PATH)
    df.columns = df.columns.str.strip()

# 3. FILTER DASHBOARD

st.sidebar.header("🔎 Filter Dashboard")

min_date = df["Tanggal"].min().date()
max_date = df["Tanggal"].max().date()



