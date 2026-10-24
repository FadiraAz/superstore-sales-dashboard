import streamlit as st
import pandas as pd
import plotly.express as px


# 1. KONFIGURASI DASHBOARD
st.set_page_config(
    page_title="Dashboard Kesehatan MVD",
    page_icon="🏥",
    layout="wide"
)

DATA_PATH = "Dataset_Kesehatan_MVD.xlsx - Raw_Data.csv"

st.title("🏥 Dashboard Kesehatan")
st.caption(
    "Dashboard interaktif kunjungan pasien, "
    "analisis pelayanan, dan ringkasan kinerja kesehatan."
)


# 2. MEMBACA DATA HASIL CLEANING
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip()

    required_columns = [
        "Visit_ID", "Visit_Date", "Patient_ID",
        "City", "Department", "Visit_Status",
        "Visit_Type", "Total_Bill",
        "Waiting_Time_Min", "Satisfaction_Score"
    ]

    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(
            "Kolom berikut tidak ditemukan: "
            + ", ".join(missing)
        )

    # Membersihkan format tanggal dan angka
    df["Visit_Date"] = pd.to_datetime(
        df["Visit_Date"], errors="coerce"
    )

    numeric_columns = [
        "Age", "Consultation_Fee", "Medicine_Cost",
        "Lab_Cost", "Total_Bill",
        "Waiting_Time_Min", "Satisfaction_Score"
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col], errors="coerce"
            )

    # Menyeragamkan penulisan kategori
    for col in [
        "City", "Department", "Visit_Status", "Visit_Type"
    ]:
        df[col] = df[col].astype("string").str.strip()
        df[col] = df[col].replace("", pd.NA)

    # Menyatukan variasi nama departemen
    df["Department"] = df["Department"].replace({
        "penyakit dalam": "Penyakit Dalam",
        "PENYAKIT DALAM": "Penyakit Dalam",
        "PD": "Penyakit Dalam"
    })

    # Menyatukan variasi penulisan kota
    df["City"] = df["City"].replace({
        "sukoharjo": "Sukoharjo",
        "SUKOHARJO": "Sukoharjo",
        "Surakarta ": "Surakarta",
        "SURAKARTA": "Surakarta",
        "solo": "Surakarta"
    })

    # Menyatukan status kunjungan
    df["Visit_Status"] = (
        df["Visit_Status"].str.lower().replace({
            "selesai": "Selesai",
            "batal": "Batal",
            "tidak hadir": "Tidak Hadir",
            "no show": "Tidak Hadir"
        })
    )

    # Baris tanpa tanggal tidak dapat masuk filter periode
    df = df.dropna(subset=["Visit_Date"]).copy()

    return df


try:
    df = load_data()
except FileNotFoundError:
    st.error(
        f"File {DATA_PATH} tidak ditemukan. "
        "Simpan file hasil cleaning di folder yang sama "
        "dengan app.py."
    )
    st.stop()
except Exception as e:
    st.error(f"Terjadi kesalahan saat membaca data: {e}")
    st.stop()

if df.empty:
    st.warning("Dataset tidak memiliki tanggal kunjungan yang valid.")
    st.stop()


# 3. FILTER DASHBOARD

st.sidebar.header("🔎 Filter Dashboard")

min_date = df["Visit_Date"].min().date()
max_date = df["Visit_Date"].max().date()

date_range = st.sidebar.date_input(
    "Periode Kunjungan",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

departments = sorted(
    df["Department"].dropna().unique().tolist()
)
cities = sorted(
    df["City"].dropna().unique().tolist()
)
statuses = sorted(
    df["Visit_Status"].dropna().unique().tolist()
)

selected_departments = st.sidebar.multiselect(
    "Departemen",
    options=departments,
    default=departments
)

selected_cities = st.sidebar.multiselect(
    "Kota",
    options=cities,
    default=cities
)

selected_statuses = st.sidebar.multiselect(
    "Status Kunjungan",
    options=statuses,
    default=statuses
)

# Menangani pemilihan satu tanggal atau rentang tanggal
if isinstance(date_range, (tuple, list)):
    if len(date_range) == 2:
        start_date, end_date = date_range
    elif len(date_range) == 1:
        start_date = end_date = date_range[0]
    else:
        start_date, end_date = min_date, max_date
else:
    start_date = end_date = date_range

if start_date > end_date:
    start_date, end_date = end_date, start_date

filtered = df[
    (df["Visit_Date"].dt.date >= start_date)
    & (df["Visit_Date"].dt.date <= end_date)
    & (df["Department"].isin(selected_departments))
    & (df["City"].isin(selected_cities))
    & (df["Visit_Status"].isin(selected_statuses))
].copy()


# 4. KPI CARDS

st.subheader("📊 Indikator Kinerja Utama")

total_visits = filtered["Visit_ID"].nunique()
total_patients = filtered["Patient_ID"].nunique()
total_bill = filtered["Total_Bill"].sum()
avg_waiting = filtered["Waiting_Time_Min"].mean()
avg_satisfaction = filtered["Satisfaction_Score"].mean()

completed_visits = filtered.loc[
    filtered["Visit_Status"] == "Selesai",
    "Visit_ID"
].nunique()

completion_rate = (
    completed_visits / total_visits * 100
    if total_visits else 0
)

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric(
    "Total Kunjungan",
    f"{total_visits:,}"
)

k2.metric(
    " Banyaknya Pasien",
    f"{total_patients:,}"
)

k3.metric(
    "Total Tagihan",
    f"Rp {total_bill:,.0f}"
)

k4.metric(
    "Rata-rata Waktu Tunggu",
    f"{avg_waiting:.1f} menit"
    if pd.notna(avg_waiting) else "—"
)

k5.metric(
    "Rata-rata Kepuasan",
    f"{avg_satisfaction:.2f}/5"
    if pd.notna(avg_satisfaction) else "—"
)

st.caption(
    f"Tingkat kunjungan selesai: {completion_rate:.1f}% "
    f"({completed_visits:,} dari {total_visits:,} kunjungan unik)."
)

if filtered.empty:
    st.warning(
        "Tidak ada data yang sesuai dengan filter. "
        "Silakan ubah pilihan filter di sidebar."
    )
    st.stop()


# 5. GRAFIK 1: TREN KUNJUNGAN BULANAN

st.subheader("📈 Analisis Kunjungan Pasien")

left, right = st.columns(2)

with left:
    monthly = filtered.copy()
    monthly["Bulan"] = (
        monthly["Visit_Date"]
        .dt.to_period("M")
        .astype(str)
    )

    monthly = (
        monthly.groupby("Bulan", as_index=False)
        ["Visit_ID"].nunique()
        .rename(columns={"Visit_ID": "Jumlah Kunjungan"})
        .sort_values("Bulan")
    )

    fig = px.line(
        monthly,
        x="Bulan",
        y="Jumlah Kunjungan",
        markers=True,
        title="Tren Kunjungan per Bulan",
        hover_data={"Jumlah Kunjungan": ":,"}
    )

    fig.update_layout(
        xaxis_title="Bulan",
        yaxis_title="Jumlah Kunjungan"
    )

    st.plotly_chart(fig, use_container_width=True)


# 6. GRAFIK 2: KUNJUNGAN PER DEPARTEMEN

with right:
    dept_data = (
        filtered.groupby("Department", as_index=False)
        ["Visit_ID"].nunique()
        .rename(columns={"Visit_ID": "Jumlah Kunjungan"})
        .sort_values("Jumlah Kunjungan", ascending=False)
    )

    fig = px.bar(
        dept_data,
        x="Department",
        y="Jumlah Kunjungan",
        title="Kunjungan Berdasarkan Departemen",
        text_auto=True,
        hover_data={"Jumlah Kunjungan": ":,"}
    )

    fig.update_layout(
        xaxis_title="Departemen",
        yaxis_title="Jumlah Kunjungan"
    )

    st.plotly_chart(fig, use_container_width=True)


# 7. GRAFIK 3: KUNJUNGAN PER KOTA

left, right = st.columns(2)

with left:
    city_data = (
        filtered.groupby("City", as_index=False)
        ["Visit_ID"].nunique()
        .rename(columns={"Visit_ID": "Jumlah Kunjungan"})
        .sort_values("Jumlah Kunjungan", ascending=False)
    )

    fig = px.bar(
        city_data,
        x="City",
        y="Jumlah Kunjungan",
        title="Kunjungan Berdasarkan Kota",
        text_auto=True
    )

    fig.update_layout(
        xaxis_title="Kota",
        yaxis_title="Jumlah Kunjungan"
    )

    st.plotly_chart(fig, use_container_width=True)


# 8. GRAFIK 4: STATUS KUNJUNGAN

with right:
    status_data = (
        filtered.groupby("Visit_Status", as_index=False)
        ["Visit_ID"].nunique()
        .rename(columns={"Visit_ID": "Jumlah Kunjungan"})
    )

    fig = px.pie(
        status_data,
        names="Visit_Status",
        values="Jumlah Kunjungan",
        title="Distribusi Status Kunjungan",
        hole=0.4
    )

    st.plotly_chart(fig, use_container_width=True)


# 9. GRAFIK 5: WAKTU TUNGGU PER DEPARTEMEN

left, right = st.columns(2)

with left:
    waiting_data = (
        filtered.groupby("Department", as_index=False)
        ["Waiting_Time_Min"].mean()
        .dropna()
        .sort_values("Waiting_Time_Min", ascending=False)
    )

    fig = px.bar(
        waiting_data,
        x="Department",
        y="Waiting_Time_Min",
        title="Rata-rata Waktu Tunggu per Departemen",
        text_auto=".1f"
    )

    fig.update_layout(
        xaxis_title="Departemen",
        yaxis_title="Waktu Tunggu (menit)"
    )

    st.plotly_chart(fig, use_container_width=True)


# 10. GRAFIK 6: TAGIHAN PER JENIS KUNJUNGAN

with right:
    bill_data = (
        filtered.groupby("Visit_Type", as_index=False)
        ["Total_Bill"].mean()
        .dropna()
        .sort_values("Total_Bill", ascending=False)
    )

    fig = px.bar(
        bill_data,
        x="Visit_Type",
        y="Total_Bill",
        title="Rata-rata Tagihan per Jenis Kunjungan",
        text_auto=",.0f"
    )

    fig.update_layout(
        xaxis_title="Jenis Kunjungan",
        yaxis_title="Rata-rata Tagihan (Rp)"
    )

    st.plotly_chart(fig, use_container_width=True)


# 11. INSIGHT DAN REKOMENDASI OTOMATIS

st.subheader("💡 Ringkasan Insight dan Rekomendasi")

insights = []
recommendations = []

# Departemen dengan kunjungan tertinggi
top_dept = dept_data.iloc[0]

insights.append(
    f"Departemen dengan kunjungan terbanyak adalah "
    f"**{top_dept['Department']}** dengan "
    f"{int(top_dept['Jumlah Kunjungan']):,} kunjungan."
)

recommendations.append(
    f"Evaluasi kebutuhan dokter, jadwal, dan kapasitas "
    f"layanan di departemen {top_dept['Department']}."
)

# Kota dengan kunjungan tertinggi
top_city = city_data.iloc[0]

insights.append(
    f"Kota dengan kunjungan terbanyak adalah "
    f"**{top_city['City']}** dengan "
    f"{int(top_city['Jumlah Kunjungan']):,} kunjungan."
)

recommendations.append(
    f"Gunakan data kunjungan dari {top_city['City']} "
    "untuk membantu perencanaan kapasitas dan akses layanan."
)

# Status tidak hadir
status_counts = (
    filtered.groupby("Visit_Status")["Visit_ID"].nunique()
)

no_show = int(status_counts.get("Tidak Hadir", 0))
no_show_rate = (
    no_show / total_visits * 100
    if total_visits else 0
)

insights.append(
    f"Jumlah kunjungan berstatus tidak hadir adalah "
    f"**{no_show:,} ({no_show_rate:.1f}%)**."
)

if no_show_rate >= 10:
    recommendations.append(
        "Pertimbangkan pengingat janji melalui SMS atau WhatsApp "
        "dan konfirmasi jadwal untuk mengurangi ketidakhadiran."
    )
else:
    recommendations.append(
        "Pertahankan proses pengingat jadwal dan pantau "
        "tren ketidakhadiran secara berkala."
    )

# Waktu tunggu
if pd.notna(avg_waiting):
    insights.append(
        f"Rata-rata waktu tunggu adalah **{avg_waiting:.1f} menit**."
    )

    if avg_waiting > 60:
        recommendations.append(
            "Tinjau proses pendaftaran, triase, dan penjadwalan "
            "karena rata-rata waktu tunggu melebihi 60 menit."
        )
    else:
        recommendations.append(
            "Pantau departemen dengan waktu tunggu tertinggi "
            "dan pertahankan alur pelayanan yang efisien."
        )

# Kepuasan pasien
if pd.notna(avg_satisfaction):
    insights.append(
        f"Skor kepuasan rata-rata adalah "
        f"**{avg_satisfaction:.2f} dari 5**."
    )

    if avg_satisfaction < 3.5:
        recommendations.append(
            "Tinjau umpan balik pasien dan prioritaskan perbaikan "
            "pengalaman layanan, komunikasi, serta waktu tunggu."
        )
    else:
        recommendations.append(
            "Pertahankan kualitas pelayanan dan tindak lanjuti "
            "masukan pasien dengan skor kepuasan rendah."
        )

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Temuan Utama")

    for item in insights:
        st.markdown(f"- {item}")

with col2:
    st.markdown("#### Rekomendasi")

    for item in recommendations:
        st.markdown(f"- {item}")


# 12. TABEL DATA HASIL FILTER

st.subheader("📋 Detail Data Kunjungan")

display_df = filtered.sort_values(
    "Visit_Date", ascending=False
).copy()

column_config = {
    "Visit_Date": st.column_config.DateColumn(
        "Tanggal Kunjungan",
        format="DD-MM-YYYY"
    ),
    "Consultation_Fee": st.column_config.NumberColumn(
        "Biaya Konsultasi",
        format="Rp %d"
    ),
    "Medicine_Cost": st.column_config.NumberColumn(
        "Biaya Obat",
        format="Rp %d"
    ),
    "Lab_Cost": st.column_config.NumberColumn(
        "Biaya Lab",
        format="Rp %d"
    ),
    "Total_Bill": st.column_config.NumberColumn(
        "Total Tagihan",
        format="Rp %d"
    ),
    "Waiting_Time_Min": st.column_config.NumberColumn(
        "Waktu Tunggu (menit)",
        format="%.0f"
    ),
    "Satisfaction_Score": st.column_config.NumberColumn(
        "Skor Kepuasan",
        format="%.1f"
    )
}

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config=column_config
)


# 13. DOWNLOAD CSV HASIL FILTER
csv = display_df.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    label="⬇️ Download Data Hasil Filter",
    data=csv,
    file_name="data_kesehatan_mvd_filtered.csv",
    mime="text/csv"
)

st.caption(
    f"Menampilkan {len(filtered):,} baris dari "
    f"{len(df):,} baris data valid bertanggal. "
    "Seluruh KPI, grafik, insight, rekomendasi, dan tabel "
    "mengikuti filter yang dipilih."
)
