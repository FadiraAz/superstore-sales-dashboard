import streamlit as st
st.title("Dashboard Penjualan")
st.write("Ini adalah dashboard pertama saya!")

col1, col2, col3 = st.columns(3)
with col1:
	st.metric("Total Penjualan", "Rp. 50.000.000.000")

with col2:
	st.metric("Total Transaksi", "50.000.000")

with col3:
	st.metric("Total Produk Terjual", "50.000")



