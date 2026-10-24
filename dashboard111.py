
import streamlit as st
import pandas as pd
import plotly.express as px

# 1. PENGATURAN HALAMAN
st.set_page_config(
    page_title="Dashboard Penjualan Sandal",
    page_icon="👡",
    layout="wide"
)

# 2. warna
WARNA_PINK = [
    "#E9A6C1",
    "#D681A5",
    "#F4C2D7",
    "#C783A2",
    "#F8DCE8",
    "#B85C83"
]

st.markdown("""
<style>
.stApp {
    background-color: #FFF7FA;
}

[data-testid="stHeader"] {
    background-color: #FFF7FA;
}

[data-testid="stSidebar"] {
    background-color: #FCE7F0;
}

h1, h2, h3 {
    color: #B85C83 !important;
}

[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border: 1px solid #F3CDDD;
    padding: 18px;
    border-radius: 15px;
    box-shadow: 0 3px 10px rgba(184, 92, 131, 0.08);
}

[data-testid="stMetricLabel"] {
    color: #98617A;
}

[data-testid="stMetricValue"] {
    color: #C45D8A;
}

div[data-testid="stPlotlyChart"] {
    background-color: #FFFFFF;
    border: 1px solid #F3CDDD;
    border-radius: 15px;
    padding: 8px;
}

.stButton button,
.stDownloadButton button {
    background-color: #E9A6C1;
    color: white;
    border: none;
    border-radius: 10px;
}

.stButton button:hover,
.stDownloadButton button:hover {
    background-color: #D681A5;
    color: white;
}

[data-testid="stDataFrame"] {
    border: 1px solid #F3CDDD;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)


# Fungsi untuk mengatur tampilan grafik
def style_chart(fig):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Arial",
            color="#80566A"
        ),
        title_font=dict(
            color="#B85C83",
            size=18
        ),
        colorway=WARNA_PINK,
        margin=dict(l=20, r=20, t=60, b=30),
        legend_title_text=""
    )

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#F7E5ED")

    return fig


# 3. MEMBACA DATA
@st.cache_data
def load_data():
    df = pd.read_csv(
        "penjualan_sandal.csv",
        parse_dates=["Tanggal"],
        dayfirst=True
    )

    df.columns = df.columns.str.strip()

    # Menyesuaikan nama kolom kategori
    if "Kategore" in df.columns:
        df = df.rename(columns={"Kategore": "Kategori"})

    # Membersihkan penulisan data kategorikal
    kolom_kategori = [
        "Kategori", "Gender", "Kota",
        "Channel_Penjualan", "Metode_Pembayaran"
    ]

    for kolom in kolom_kategori:
        if kolom in df.columns:
            df[kolom] = df[kolom].astype("string").str.strip()

    if "Kategori" in df.columns:
        df["Kategori"] = df["Kategori"].str.title()

    if "Gender" in df.columns:
        df["Gender"] = df["Gender"].str.strip().str.lower().replace({
        "wanita": "Perempuan",
        "perempuan": "Perempuan",
        "pria": "Laki-laki",
        "laki-laki": "Laki-laki",
        "laki laki": "Laki-laki"
    })

    if "Kota" in df.columns:
        df["Kota"] = df["Kota"].str.title()

    if "Channel_Penjualan" in df.columns:
        df["Channel_Penjualan"] = df["Channel_Penjualan"].str.title()
        df["Channel_Penjualan"] = df["Channel_Penjualan"].replace({
            "Tiktok": "TikTok"
        })

    if "Metode_Pembayaran" in df.columns:
        df["Metode_Pembayaran"] = df["Metode_Pembayaran"].str.upper()
        df["Metode_Pembayaran"] = df["Metode_Pembayaran"].replace({
            "E-WALLET": "E-Wallet"
        })

    # Mengubah kolom angka menjadi numerik
    for kolom in [
        "Jumlah", "Harga_Satuan", "Diskon", "Total_Penjualan"
    ]:
        if kolom in df.columns:
            df[kolom] = pd.to_numeric(
                df[kolom], errors="coerce"
            )

    return df


try:
    df = load_data()
except FileNotFoundError:
    st.error(
        "File penjualan_sandal.csv tidak ditemukan. "
        "Letakkan file di folder yang sama dengan app.py."
    )
    st.stop()
except Exception as e:
    st.error(f"Data gagal dibaca: {e}")
    st.stop()


# Memastikan kolom yang diperlukan tersedia
kolom_wajib = [
    "ID_Transaksi", "Tanggal", "Nama_Produk",
    "Kota", "Channel_Penjualan", "Jumlah",
    "Status", "Total_Penjualan"
]

kolom_hilang = [k for k in kolom_wajib if k not in df.columns]

if kolom_hilang:
    st.error(f"Kolom berikut belum tersedia: {kolom_hilang}")
    st.stop()


# 4. JUDUL DASHBOARD
st.title("👡 Dashboard Penjualan Sandal")
st.caption(
    "Visualisasi performa penjualan berdasarkan transaksi, "
    "produk, wilayah, dan channel."
)


# 5. FILTER DATA
st.sidebar.header("🎀 Filter Dashboard")

df = df.dropna(subset=["Tanggal"])

if df.empty:
    st.warning("Dataset tidak memiliki tanggal yang valid.")
    st.stop()

tanggal = st.sidebar.date_input(
    "Pilih rentang tanggal",
    value=(
        df["Tanggal"].min().date(),
        df["Tanggal"].max().date()
    )
)

data = df.copy()

if isinstance(tanggal, (tuple, list)) and len(tanggal) == 2:
    data = data[
        (data["Tanggal"].dt.date >= tanggal[0]) &
        (data["Tanggal"].dt.date <= tanggal[1])
    ]

filter_kolom = [
    "Kategori", "Gender", "Kota",
    "Channel_Penjualan", "Metode_Pembayaran"
]

for kolom in filter_kolom:
    if kolom in data.columns:
        pilihan_tersedia = sorted(
            data[kolom].dropna().unique().tolist(),
            key=str
        )

        pilihan = st.sidebar.multiselect(
            kolom.replace("_", " "),
            options=pilihan_tersedia,
            default=pilihan_tersedia
        )

        data = data[data[kolom].isin(pilihan)]


# Mengeluarkan transaksi batal atau gagal
status_gagal = ["batal", "cancel", "canceled", "gagal"]

data = data[
    ~data["Status"].astype(str).str.strip().str.lower()
    .isin(status_gagal)
].copy()

if data.empty:
    st.warning("Tidak ada transaksi sesuai filter yang dipilih.")
    st.stop()


# 6. KPI
st.subheader("Ringkasan Penjualan")

total_penjualan = data["Total_Penjualan"].sum()
total_transaksi = data["ID_Transaksi"].nunique()
total_sandal = data["Jumlah"].sum()

rata_transaksi = (
    total_penjualan / total_transaksi
    if total_transaksi > 0 else 0
)


def format_rupiah(nilai):
    return "Rp " + f"{nilai:,.0f}".replace(",", ".")


k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Penjualan", format_rupiah(total_penjualan))
k2.metric("Total Transaksi", f"{total_transaksi:,}")
k3.metric("Total Sandal Terjual", f"{total_sandal:,.0f}")
k4.metric("Rata-rata per Transaksi", format_rupiah(rata_transaksi))

st.divider()


# 7. GRAFIK TREN PENJUALAN
st.subheader(" Tren Penjualan Bulanan")
data["Bulan"] = data["Tanggal"].dt.to_period("M").astype(str)
tren = (
    data.groupby("Bulan", as_index=False)["Total_Penjualan"]
    .sum()
)
fig_tren = px.line(
    tren,
    x="Bulan",
    y="Total_Penjualan",
    markers=True,
    title="Total Penjualan per Bulan",
    labels={
        "Bulan": "Bulan",
        "Total_Penjualan": "Penjualan (Rp)"
    }
)
fig_tren.update_traces(
    line=dict(color="#D681A5", width=3),
    marker=dict(color="#B85C83", size=8),
    fill="tozeroy",
    fillcolor="rgba(233,166,193,0.18)"
)

fig_tren = style_chart(fig_tren)
st.plotly_chart(fig_tren, use_container_width=True)


# 8. PENJUALAN PER KATEGORI
kiri, kanan = st.columns(2)

with kiri:
    if "Kategori" in data.columns:
        kategori = (
            data.groupby("Kategori", as_index=False)
            ["Total_Penjualan"].sum()
            .sort_values("Total_Penjualan", ascending=False)
        )

        fig_kategori = px.bar(
            kategori,
            x="Kategori",
            y="Total_Penjualan",
            color="Kategori",
            color_discrete_sequence=WARNA_PINK,
            title="Penjualan per Kategori",
            labels={"Total_Penjualan": "Penjualan (Rp)"}
        )

        fig_kategori.update_layout(showlegend=False)
        fig_kategori = style_chart(fig_kategori)

        st.plotly_chart(fig_kategori, use_container_width=True)


# 9. PENJUALAN PER CHANNEL
with kanan:
    channel = (
        data.groupby("Channel_Penjualan", as_index=False)
        ["Total_Penjualan"].sum()
        .sort_values("Total_Penjualan", ascending=True)
    )

    fig_channel = px.bar(
        channel,
        x="Total_Penjualan",
        y="Channel_Penjualan",
        orientation="h",
        color="Channel_Penjualan",
        color_discrete_sequence=WARNA_PINK,
        title="Penjualan per Channel",
        labels={"Total_Penjualan": "Penjualan (Rp)"}
    )

    fig_channel.update_layout(showlegend=False)
    fig_channel = style_chart(fig_channel)

    st.plotly_chart(fig_channel, use_container_width=True)


# 10. PENJUALAN PER KOTA
kiri, kanan = st.columns(2)

with kiri:
    kota = (
        data.groupby("Kota", as_index=False)
        ["Total_Penjualan"].sum()
        .sort_values("Total_Penjualan", ascending=False)
    )

    fig_kota = px.bar(
        kota,
        x="Kota",
        y="Total_Penjualan",
        color="Kota",
        color_discrete_sequence=WARNA_PINK,
        title="Penjualan per Kota",
        labels={"Total_Penjualan": "Penjualan (Rp)"}
    )

    fig_kota.update_layout(showlegend=False)
    fig_kota = style_chart(fig_kota)

    st.plotly_chart(fig_kota, use_container_width=True)


# 11. PENJUALAN PER GENDER
with kanan:
    if "Gender" in data.columns:
        gender = (
            data.groupby("Gender", as_index=False)
            ["Total_Penjualan"].sum()
        )
        fig_gender = px.pie(
            gender,
            names="Gender",
            values="Total_Penjualan",
            hole=0.4,
            color_discrete_sequence=WARNA_PINK,
            title="Kontribusi Penjualan per Gender"
        )
        fig_gender.update_traces(
            textposition="inside",
            textinfo="percent+label"
        )
        fig_gender = style_chart(fig_gender)
        st.plotly_chart(fig_gender, use_container_width=True)


# 12. METODE PEMBAYARAN
if "Metode_Pembayaran" in data.columns:
    pembayaran = (
        data.groupby("Metode_Pembayaran", as_index=False)
        ["Total_Penjualan"].sum()
        .sort_values("Total_Penjualan", ascending=False)
    )

    fig_bayar = px.bar(
        pembayaran,
        x="Metode_Pembayaran",
        y="Total_Penjualan",
        color="Metode_Pembayaran",
        color_discrete_sequence=WARNA_PINK,
        title="Penjualan per Metode Pembayaran",
        labels={"Total_Penjualan": "Penjualan (Rp)"}
    )

    fig_bayar.update_layout(showlegend=False)
    fig_bayar = style_chart(fig_bayar)

    st.plotly_chart(fig_bayar, use_container_width=True)


# 13. INSIGHT OTOMATIS
st.subheader(" Insight Penjualan")

produk = data.groupby("Nama_Produk")["Jumlah"].sum()

kota_tertinggi = (
    data.groupby("Kota")["Total_Penjualan"].sum().idxmax()
)

channel_tertinggi = (
    data.groupby("Channel_Penjualan")
    ["Total_Penjualan"].sum().idxmax()
)

if not produk.empty:
    st.markdown(
        f"-  Produk terlaris berdasarkan jumlah: "
        f"**{produk.idxmax()}**"
    )

st.markdown(
    f"-  Kota dengan penjualan tertinggi: **{kota_tertinggi}**"
)

st.markdown(
    f"-  Channel penjualan tertinggi: **{channel_tertinggi}**"
)


# 14. TABEL DETAIL TRANSAKSI
st.subheader("🛍️ Detail Transaksi")

st.dataframe(
    data.sort_values("Tanggal", ascending=False),
    use_container_width=True,
    hide_index=True
)

# Download data sesuai filter
csv = data.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label=" Download Data Hasil Filter",
    data=csv,
    file_name="penjualan_sandal_filtered.csv",
    mime="text/csv"
)

st.markdown(
    "<p style='text-align:center; color:#B85C83;'>"
    "Made with love ♡ Dashboard Penjualan Sandal"
    "</p>",
    unsafe_allow_html=True
)