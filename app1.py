# streamlit.io/gallery
import streamlit as st 
import pandas as pd 
import plotly.express as px


st.set_page_config(    
    page_title="Dashboard Penjualan Enzo",    
    layout="wide" )

@st.cache_data 
def load_data():    
    df = pd.read_csv("data_penjualan.csv", parse_dates=["Tanggal"])    
    return df 
df = load_data()

st.sidebar.header(" Filter Dashboard")
min_date = df["Tanggal"].min().date() 
max_date = df["Tanggal"].max().date() 
date_range = st.sidebar.date_input(    
    "Periode",    
    value=(min_date, max_date),   
    min_value=min_date,    
    max_value=max_date)

categories = st.sidebar.multiselect(    
    "Kategori",    
    sorted(df["Kategori"].unique()),    
    default=sorted(df["Kategori"].unique()) 
    ) 
channels = st.sidebar.multiselect(    
    "Channel",
     sorted(df["Channel"].unique()),    
     default=sorted(df["Channel"].unique()) 
     ) 
regions = st.sidebar.multiselect(    
    "Wilayah",    
    sorted(df["Wilayah"].unique()),    
    default=sorted(df["Wilayah"].unique()) 
    )

if isinstance(date_range, tuple):    
    if len(date_range) == 2:        
        start_date, end_date = date_range    
    else:
        start_date = end_date = date_range[0] 
else:    
        start_date = end_date = date_range

filtered = df[    
     (df["Tanggal"].dt.date >= start_date) &    
     (df["Tanggal"].dt.date <= end_date) &    
     (df["Kategori"].isin(categories)) &    
     (df["Channel"].isin(channels)) &    
     (df["Wilayah"].isin(regions)) 
     ].copy()

st.title(" Dashboard Penjualan") 
st.caption("Dashboard interaktif menggunakan Streamlit + Pandas + Plotly")

total_sales = filtered["Penjualan"].sum() 
total_profit = filtered["Profit"].sum() 
total_qty = filtered["Qty"].sum() 
total_transactions = filtered["No_Transaksi"].nunique() 
margin = (total_profit / total_sales * 100) if total_sales else 0

c1, c2, c3, c4, c5 = st.columns(5) 
c1.metric(" Total Penjualan", f"Rp {total_sales:,.0f}") 
c2.metric(" Total Profit", f"Rp {total_profit:,.0f}") 
c3.metric(" Transaksi", f"{total_transactions:,}") 
c4.metric(" Produk Terjual", f"{total_qty:,}") 
c5.metric(" Profit Margin", f"{margin:.1f}%")

monthly = (    
    filtered.assign(Bulan=filtered["Tanggal"].dt.to_period("M").astype(str))    
    .groupby("Bulan", as_index=False)["Penjualan"]    
    .sum() ) 
fig = px.line(    
    monthly,    
    x="Bulan",
    y="Penjualan",   
    markers=True,    
    title="Tren Penjualan Bulanan" 
    ) 
fig.update_layout(yaxis_title="Penjualan (Rp)", xaxis_title="") 
st.plotly_chart(fig, use_container_width=True)

category_sales = (    
    filtered.groupby("Kategori", as_index=False)["Penjualan"]    
    .sum()    
    .sort_values("Penjualan", ascending=False) 
    ) 
fig = px.bar(    
    category_sales,    
    x="Kategori",    
    y="Penjualan",    
    title="Penjualan Berdasarkan Kategori",    
    text_auto=".2s" 
    ) 
fig.update_layout(yaxis_title="Penjualan (Rp)", xaxis_title="") 
st.plotly_chart(fig, use_container_width=True)

# 16
product_sales = (    
    filtered.groupby("Produk", as_index=False)["Penjualan"]    
    .sum()    
    .sort_values("Penjualan", ascending=True)    
    .tail(8) 
    ) 
fig = px.bar(    
     product_sales,    
     x="Penjualan",    
     y="Produk",    
     orientation="h",    
     title="Top Produk Berdasarkan Penjualan",    
     text_auto=".2s" 
     ) 
fig.update_layout(xaxis_title="Penjualan (Rp)", yaxis_title="") 
st.plotly_chart(fig, use_container_width=True)

channel_sales = (    
    filtered.groupby("Channel", as_index=False)["Penjualan"]    
    .sum()    
    .sort_values("Penjualan", ascending=False)
)
fig = px.pie(    
    channel_sales,    
    names="Channel",    
    values="Penjualan",    
    title="Kontribusi Penjualan per Channel",    
    hole=0.45 ) 
st.plotly_chart(fig, use_container_width=True)

st.subheader(" Detail Transaksi") 
display_df = filtered.sort_values("Tanggal", ascending=False).copy() 
st.dataframe(    
    display_df,    
    use_container_width=True,    
    hide_index=True,    column_config={        
        "Tanggal": st.column_config.DateColumn(            
            "Tanggal", format="DD-MM-YYYY"        
        ),        
        "Harga_Satuan": st.column_config.NumberColumn(            
            "Harga Satuan", format="Rp %d"        
        ),        
        "Diskon": st.column_config.NumberColumn(            
            "Diskon", format="Rp %d"        
        ),        
        "Penjualan": st.column_config.NumberColumn(            
            "Penjualan", format="Rp %d"        
        ),        
        "HPP": st.column_config.NumberColumn(            
            "HPP", format="Rp %d"        
        ),        
        "Profit": st.column_config.NumberColumn(            
            "Profit", format="Rp %d"        
        ),        
        "Diskon_Persen": st.column_config.NumberColumn(            
            "Diskon", format="%.0f%%"        
        ),    
    } 
)

csv = filtered.to_csv(index=False).encode("utf-8") 
st.download_button(    
    " Download Data Hasil Filter",    
    data=csv,    
    file_name="data_penjualan_filtered.csv",    
    mime="text/csv" )

st.caption(    
    f"Menampilkan {len(filtered):,} transaksi dari total {len(df):,} transaksi." )

