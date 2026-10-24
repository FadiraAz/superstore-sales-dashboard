import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Penjualan Superstore",
    layout="wide"
)


@st.cache_data
def load_data():
    df = pd.read_csv(
        "Sample - Superstore.csv",
        encoding="cp1252"
    )
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%m/%d/%Y")
    return df


df = load_data()

st.sidebar.header("Filter Dashboard")

min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()

date_range = st.sidebar.date_input(
    "Periode",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

categories = st.sidebar.multiselect(
    "Kategori",
    sorted(df["Category"].unique()),
    default=sorted(df["Category"].unique())
)

regions = st.sidebar.multiselect(
    "Wilayah",
    sorted(df["Region"].unique()),
    default=sorted(df["Region"].unique())
)

segments = st.sidebar.multiselect(
    "Segmen Pelanggan",
    sorted(df["Segment"].unique()),
    default=sorted(df["Segment"].unique())
)

if isinstance(date_range, (tuple, list)):
    if len(date_range) == 2:
        start_date, end_date = date_range
    elif len(date_range) == 1:
        start_date = end_date = date_range[0]
    else:
        start_date, end_date = min_date, max_date
else:
    start_date = end_date = date_range

filtered = df[
    (df["Order Date"].dt.date >= start_date) &
    (df["Order Date"].dt.date <= end_date) &
    (df["Category"].isin(categories)) &
    (df["Region"].isin(regions)) &
    (df["Segment"].isin(segments))
].copy()

st.title("Dashboard Penjualan Superstore")
st.markdown(
    "Dashboard ini menyajikan performa penjualan, profit, dan pelanggan "
    "toko Superstore selama periode 2014-2017. Analisis mencakup kategori "
    "produk, wilayah, dan segmen pelanggan untuk mengetahui tren penjualan, "
    "produk dan wilayah dengan kontribusi terbesar, serta pengaruh diskon "
    "terhadap profit. Gunakan filter di sidebar untuk menjelajahi data dan "
    "melihat hasil analisis sesuai kebutuhan."
)
st.caption(
    "Sumber data: Superstore Dataset (Kaggle) | "
    "Dibuat menggunakan Streamlit, Pandas, dan Plotly"
)

if filtered.empty:
    st.warning("Tidak ada data untuk filter yang dipilih. Ubah filter di sidebar.")
    st.stop()

total_sales = filtered["Sales"].sum()
total_profit = filtered["Profit"].sum()
total_qty = filtered["Quantity"].sum()
total_orders = filtered["Order ID"].nunique()
margin = total_profit / total_sales * 100 if total_sales else 0

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Total Penjualan", f"$ {total_sales:,.2f}")
c2.metric("Total Profit", f"$ {total_profit:,.2f}")
c3.metric("Total Pesanan", f"{total_orders:,}")
c4.metric("Produk Terjual", f"{total_qty:,}")
c5.metric("Profit Margin", f"{margin:.1f}%")

monthly = (
    filtered.assign(
        Bulan=filtered["Order Date"].dt.to_period("M").astype(str)
    )
    .groupby("Bulan", as_index=False)["Sales"]
    .sum()
)

fig = px.line(
    monthly,
    x="Bulan",
    y="Sales",
    markers=True,
    title="Tren Penjualan Bulanan"
)
fig.update_layout(yaxis_title="Penjualan ($)", xaxis_title="")
st.plotly_chart(fig, use_container_width=True)

col_a, col_b = st.columns(2)

category_sales = (
    filtered.groupby("Category", as_index=False)["Sales"]
    .sum()
    .sort_values("Sales", ascending=False)
)

fig = px.bar(
    category_sales,
    x="Category",
    y="Sales",
    title="Penjualan Berdasarkan Kategori",
    text_auto=".2s"
)
fig.update_layout(yaxis_title="Penjualan ($)", xaxis_title="")
col_a.plotly_chart(fig, use_container_width=True)

region_sales = (
    filtered.groupby("Region", as_index=False)["Sales"]
    .sum()
    .sort_values("Sales", ascending=False)
)

fig = px.pie(
    region_sales,
    names="Region",
    values="Sales",
    title="Kontribusi Penjualan per Wilayah",
    hole=0.45
)
col_b.plotly_chart(fig, use_container_width=True)

product_sales = (
    filtered.groupby("Product Name", as_index=False)["Sales"]
    .sum()
    .sort_values("Sales", ascending=True)
    .tail(8)
)

fig = px.bar(
    product_sales,
    x="Sales",
    y="Product Name",
    orientation="h",
    title="Top 8 Produk Berdasarkan Penjualan",
    text_auto=".2s"
)
fig.update_layout(xaxis_title="Penjualan ($)", yaxis_title="")
st.plotly_chart(fig, use_container_width=True)

fig = px.scatter(
    filtered,
    x="Sales",
    y="Profit",
    color="Category",
    opacity=0.6,
    hover_data=["Product Name", "Sub-Category"],
    title="Hubungan Penjualan dan Profit"
)
fig.update_layout(xaxis_title="Penjualan ($)", yaxis_title="Profit ($)")
st.plotly_chart(fig, use_container_width=True)

col_c, col_d = st.columns(2)

fig = px.histogram(
    filtered,
    x="Discount",
    title="Distribusi Diskon"
)
fig.update_traces(xbins=dict(start=-0.05, end=0.85, size=0.1))
fig.update_xaxes(tickmode="linear", tick0=0, dtick=0.1, tickformat=".0%")
fig.update_layout(
    xaxis_title="Diskon",
    yaxis_title="Jumlah Transaksi",
    bargap=0.1
)
col_c.plotly_chart(fig, use_container_width=True)

heat = filtered.pivot_table(
    index="Sub-Category",
    columns="Region",
    values="Profit",
    aggfunc="sum",
    fill_value=0
)

fig = px.imshow(
    heat,
    text_auto=".0f",
    aspect="auto",
    color_continuous_scale="RdYlGn",
    color_continuous_midpoint=0,
    title="Heatmap Profit: Sub-Category x Wilayah ($)"
)
fig.update_layout(xaxis_title="", yaxis_title="")
col_d.plotly_chart(fig, use_container_width=True)

st.subheader("Detail Transaksi")

display_df = filtered.sort_values("Order Date", ascending=False).copy()
display_df["Discount"] = display_df["Discount"] * 100

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Order Date": st.column_config.DateColumn(
            "Tanggal Pesanan", format="DD-MM-YYYY"
        ),
        "Ship Date": st.column_config.DateColumn(
            "Tanggal Pengiriman", format="DD-MM-YYYY"
        ),
        "Sales": st.column_config.NumberColumn(
            "Penjualan ($)", format="$ %.2f"
        ),
        "Profit": st.column_config.NumberColumn(
            "Profit ($)", format="$ %.2f"
        ),
        "Discount": st.column_config.NumberColumn(
            "Diskon", format="%.0f%%"
        )
    }
)

csv = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Data Hasil Filter",
    data=csv,
    file_name="data_superstore_filtered.csv",
    mime="text/csv"
)

st.caption(
    f"Menampilkan {len(filtered):,} baris dari "
    f"total {len(df):,} baris data."
)
