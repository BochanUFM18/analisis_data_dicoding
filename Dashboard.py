import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- 0. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dashboard Analisis Penyewaan Sepeda",
                   page_icon="🚲",
                   layout="wide")

# --- 1. FUNGSI UNTUK MEMUAT DATA ---
@st.cache_data
def load_data():
    # Menggunakan path relatif untuk memastikan file ditemukan
    day_file = 'day_cleaned.csv'
    hour_file = 'hour_cleaned.csv'
    
    # Cek jika file ada
    if not os.path.exists(day_file) or not os.path.exists(hour_file):
        st.error(f"Error: Pastikan file '{day_file}' dan '{hour_file}' ada di folder yang sama dengan dashboard.py")
        return None, None

    # Muat data
    df_day = pd.read_csv(day_file)
    df_hour = pd.read_csv(hour_file)
    
    # Konversi kolom tanggal (penting untuk filter)
    df_day['dteday'] = pd.to_datetime(df_day['dteday'])
    df_hour['dteday'] = pd.to_datetime(df_hour['dteday'])
    
    # --- PERBAIKAN DI SINI ---
    # Memaksa kolom 'year_label' menjadi string agar cocok dengan kunci palette
    if 'year_label' in df_day.columns:
        df_day['year_label'] = df_day['year_label'].astype(str)
    # --------------------------
    
    return df_day, df_hour

# Muat data
df_day, df_hour = load_data()

# Jika data gagal dimuat, hentikan aplikasi
if df_day is None or df_hour is None:
    st.stop()

# --- 2. SIDEBAR UNTUK FILTER ---
st.sidebar.header("Filter Data 📅")

# Ambil tanggal min dan max dari data harian
min_date = df_day['dteday'].min()
max_date = df_day['dteday'].max()

# Buat filter rentang tanggal
date_range = st.sidebar.date_input(
    label="Pilih Rentang Tanggal:",
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]  # Nilai default (semua data)
)

# Pastikan date_range memiliki 2 nilai
if len(date_range) == 2:
    start_date, end_date = date_range
    # Ubah ke datetime untuk pemfilteran
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Terapkan filter ke kedua DataFrame
    df_day_filtered = df_day[
        (df_day['dteday'] >= start_date) & (df_day['dteday'] <= end_date)
    ]
    df_hour_filtered = df_hour[
        (df_hour['dteday'] >= start_date) & (df_hour['dteday'] <= end_date)
    ]
else:
    # Jika filter tidak lengkap, gunakan data asli
    df_day_filtered = df_day
    df_hour_filtered = df_hour


# --- 3. JUDUL UTAMA DASHBOARD ---
st.title("🚲 Dashboard Analisis Penyewaan Sepeda (2011-2012)")
st.markdown("Dashboard ini menampilkan hasil analisis data *bike sharing* untuk menjawab pertanyaan bisnis.")

st.markdown("---")

# --- 4. PLOT 1: Pertumbuhan Bisnis & Pola Musiman ---
st.header("📈 Pertumbuhan Bisnis & Pola Musiman")
st.write("Visualisasi ini menunjukkan rata-rata penyewaan harian berdasarkan musim dan tahun, sesuai dengan filter tanggal yang dipilih.")

# Siapkan plot
fig_day, ax_day = plt.subplots(figsize=(14, 7))
sns.barplot(
    data=df_day_filtered,
    x='season_label',
    y='cnt',
    hue='year_label',
    # Sekarang tipe data di 'hue' (string) akan cocok dengan 'palette' (string)
    palette={'2011': '#1f77b4', '2012': '#ff7f0e'},
    ci=None,
    ax=ax_day
)
# Kustomisasi plot
ax_day.set_title(f'Rata-rata Penyewaan Harian per Musim', fontsize=16)
ax_day.set_xlabel('Musim', fontsize=12)
ax_day.set_ylabel('Rata-rata Jumlah Penyewaan Harian (cnt)', fontsize=12)
ax_day.legend(title='Tahun', loc='upper left')

# Tampilkan plot di Streamlit
st.pyplot(fig_day)

st.markdown("---")

# --- 5. PLOT 2 & 3: Menjawab Pertanyaan Bisnis (Per Jam) ---
st.header("🕒 Analisis Pola Penyewaan per Jam")

# Gunakan tabs untuk merapikan
tab1, tab2 = st.tabs(["Jawaban Q1: Pola Hari Kerja vs Akhir Pekan", 
                      "Jawaban Q2: Pola Pengguna Casual vs Registered"])

# --- Tab 1: Jawaban Pertanyaan 1 ---
with tab1:
    st.subheader("Q1: Bagaimana pola penyewaan di Hari Kerja vs. Akhir Pekan?")
    
    fig_q1, ax_q1 = plt.subplots(figsize=(15, 7))
    sns.lineplot(
        data=df_hour_filtered, 
        x='hr', 
        y='cnt', 
        hue='tipe_hari',
        palette={'Hari Kerja': '#1f77b4', 'Akhir Pekan': '#ff7f0e'},
        ci=None,
        ax=ax_q1
    )
    # Kustomisasi plot
    ax_q1.set_title('Pola Penyewaan per Jam: "Pola Komuter" vs "Pola Rekreasi"', fontsize=16)
    ax_q1.set_xlabel('Jam dalam Sehari (hr)', fontsize=12)
    ax_q1.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=12)
    ax_q1.set_xticks(range(0, 24))
    ax_q1.legend(title='Tipe Hari', loc='upper left')
    
    # Tampilkan plot
    st.pyplot(fig_q1)
    
    # Tulis insight
    st.write("""
    **Insight (Jawaban Q1):**
    - **Hari Kerja (Pola Komuter):** Terdapat dua puncak jelas di **jam 8 pagi** dan **5-6 sore**, sesuai jam pergi/pulang kantor.
    - **Akhir Pekan (Pola Rekreasi):** Terdapat satu puncak lebar di **siang hari (10 pagi - 4 sore)**, sesuai jam rekreasi.
    """)

# --- Tab 2: Jawaban Pertanyaan 2 ---
with tab2:
    st.subheader("Q2: Bagaimana perbedaan perilaku pengguna Casual vs. Registered?")
    
    # 1. Aggregate data (HARUS di-agregasi ulang dari data terfilter)
    hourly_usage_filtered = df_hour_filtered.groupby('hr').agg({
        'casual': 'mean',
        'registered': 'mean'
    }).reset_index()

    # 2. Melt data
    hourly_usage_melted = hourly_usage_filtered.melt(
        id_vars='hr', 
        var_name='Tipe Pengguna', 
        value_name='Rata-rata Penyewaan'
    )
    
    # 3. Buat plot
    fig_q2, ax_q2 = plt.subplots(figsize=(15, 7))
    sns.lineplot(
        data=hourly_usage_melted,
        x='hr',
        y='Rata-rata Penyewaan',
        hue='Tipe Pengguna',
        palette={'casual': '#2ca02c', 'registered': '#9467bd'}, # Warna spesifik
        ci=None,
        ax=ax_q2
    )
    # Kustomisasi plot
    ax_q2.set_title('Pola Pengguna "Registered" (Komuter) vs "Casual" (Rekreasi)', fontsize=16)
    ax_q2.set_xlabel('Jam dalam Sehari (hr)', fontsize=12)
    ax_q2.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=12)
    ax_q2.set_xticks(range(0, 24))
    ax_q2.legend(title='Tipe Pengguna', loc='upper left')
    
    # Tampilkan plot
    st.pyplot(fig_q2)
    
    # Tulis insight
    st.write("""
    **Insight (Jawaban Q2):**
    - **Pengguna 'Registered' (Komuter):** Pola mereka identik dengan "Pola Komuter", mengkonfirmasi mereka adalah komuter.
    - **Pengguna 'Casual' (Rekreasi):** Pola mereka identik dengan "Pola Rekreasi", mengkonfirmasi mereka adalah pengguna rekreasi.
    """)

# --- 6. MENAMPILKAN DATA MENTAH (Opsional) ---
st.markdown("---")
if st.checkbox("Tampilkan Data Mentah (Terfilter)"):
    st.subheader("Data Harian (day_cleaned.csv)")
    st.dataframe(df_day_filtered)
    st.subheader("Data Per Jam (hour_cleaned.csv)")
    st.dataframe(df_hour_filtered)

st.caption("Proyek Analisis Data - Dibuat dengan Streamlit")