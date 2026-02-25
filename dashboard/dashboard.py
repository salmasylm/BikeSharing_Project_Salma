import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# ─────────────────────────────────────────────
# CONFIG & PATH
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Set plot style
plt.rcParams['figure.facecolor'] = 'lightgray'
plt.rcParams['axes.facecolor']   = 'lightgray'
plt.rcParams['text.color']       = 'black'
plt.rcParams['axes.labelcolor']  = 'black'
plt.rcParams['xtick.color']      = 'black'
plt.rcParams['ytick.color']      = 'black'

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    day  = pd.read_csv(os.path.join(BASE_DIR, "main_data.csv"))
    hour = pd.read_csv(os.path.join(BASE_DIR, "hour.csv"))
    day["dteday"]  = pd.to_datetime(day["dteday"])
    hour["dteday"] = pd.to_datetime(hour["dteday"])
    return day, hour

day_clean_df, hour_df = load_data()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='font-size:25px; font-weight:bold;'>Penggunaan Sepeda Tahun 2011 & 2012</h2>", unsafe_allow_html=True)

    logo_path = os.path.join(BASE_DIR, "sepeda_foto.png")
    if os.path.exists(logo_path):
        st.image(logo_path)

    min_date = day_clean_df["dteday"].min()
    max_date = day_clean_df["dteday"].max()

    start_date, end_date = st.date_input(
        label="Analysis Time:",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# ─────────────────────────────────────────────
# FILTER DATA
# ─────────────────────────────────────────────
main_df   = day_clean_df[(day_clean_df["dteday"].dt.date >= start_date) &
                          (day_clean_df["dteday"].dt.date <= end_date)]

second_df = hour_df[(hour_df["dteday"].dt.date >= start_date) &
                     (hour_df["dteday"].dt.date <= end_date)]

# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
def replace_year(df):
    return df.replace({"yr": {0: 2011, 1: 2012}})

def create_casual_register_df(df):
    casual = df.groupby("yr")["casual"].sum().reset_index()
    casual.columns = ["yr", "total_casual"]
    reg    = df.groupby("yr")["registered"].sum().reset_index()
    reg.columns = ["yr", "total_registered"]
    return casual.merge(reg, on="yr")

def create_monthly_df(df):
    return df.groupby(["mnth", "yr"]).agg(cnt=("cnt", "sum")).reset_index()

def create_hourly_df(df):
    return df.groupby(["hr", "yr"]).agg(cnt=("cnt", "sum")).reset_index()

def create_byholiday_df(df):
    return df.groupby(["holiday", "yr"]).agg(cnt=("cnt", "sum")).reset_index()

def create_byworkingday_df(df):
    return df.groupby(["workingday", "yr"]).agg(cnt=("cnt", "sum")).reset_index()

def create_byseason_df(df):
    return df.groupby(["season", "yr"]).agg(cnt=("cnt", "sum")).reset_index()

def create_byweather_df(df):
    return df.groupby(["weathersit", "yr"]).agg(cnt=("cnt", "sum")).reset_index()

# Build all DataFrames
casual_register_df = replace_year(create_casual_register_df(main_df))
monthly_df         = replace_year(create_monthly_df(main_df))
hourly_df          = replace_year(create_hourly_df(second_df))
holiday_df         = replace_year(create_byholiday_df(main_df))
workingday_df      = replace_year(create_byworkingday_df(main_df))
season_df          = replace_year(create_byseason_df(main_df))
weather_df         = replace_year(create_byweather_df(main_df))

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.header("Studi Kasus Penggunaan Sepeda")

# ─────────────────────────────────────────────
# METRIC CARDS
# ─────────────────────────────────────────────
total_rentals  = main_df["cnt"].sum()
total_casual   = main_df["casual"].sum()
total_register = main_df["registered"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("Total Penyewaan",   f"{total_rentals:,}")
col2.metric("Pengguna Tidak Resmi",   f"{total_casual:,}")
col3.metric("Pengguna Resmi", f"{total_register:,}")

st.markdown("---")

# ─────────────────────────────────────────────
# 1. CASUAL vs REGISTERED PER TAHUN
# ─────────────────────────────────────────────
st.subheader("Perbandingan Pengguna Resmi vs Tidak Resmi per Tahun")

fig, ax = plt.subplots(figsize=(8, 5))
x      = np.arange(len(casual_register_df))
width  = 0.35
bars1  = ax.bar(x - width/2, casual_register_df["total_casual"],     width, label="Casual",     color="#FF6347")
bars2  = ax.bar(x + width/2, casual_register_df["total_registered"], width, label="Registered", color="#4682B4")
ax.set_xticks(x)
ax.set_xticklabels(casual_register_df["yr"])
ax.set_xlabel("Tahun")
ax.set_ylabel("Jumlah")
ax.set_title("Total Pengguna Casual vs Registered per Tahun")
ax.legend()
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, _: f"{val:,.0f}"))
for bar in bars1:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5000,
            f"{bar.get_height():,.0f}", ha="center", va="bottom",
            fontsize=7, color="#FF6347", fontweight="bold")
for bar in bars2:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5000,
            f"{bar.get_height():,.0f}", ha="center", va="bottom",
            fontsize=7, color="#4682B4", fontweight="bold")
plt.tight_layout()
st.pyplot(fig)

with st.expander("**Bagaimana Kesimpulannya?**"):
    st.markdown("""
    Jumlah pengguna *registered* jauh mendominasi dibandingkan pengguna *casual* di kedua tahun.
    Hal ini menunjukkan bahwa layanan bike sharing lebih banyak digunakan oleh pelanggan tetap
    yang memiliki pola penggunaan rutin, seperti para pekerja komuter. Kedua segmen pengguna
    mengalami pertumbuhan dari 2011 ke 2012.
    """)

st.markdown("---")

# ─────────────────────────────────────────────
# 2. TREND BULANAN
# ─────────────────────────────────────────────
st.subheader("Trend Pola Total Penyewaan Sepeda Setiap Tahun")

fig, ax = plt.subplots(figsize=(10, 5))
sns.lineplot(data=monthly_df, x="mnth", y="cnt", hue="yr",
             palette="bright", marker="o", ax=ax)
ax.set_xlabel("Urutan Bulan")
ax.set_ylabel("Jumlah")
ax.set_title("Jumlah Total Sepeda yang Disewakan per Bulan")
ax.legend(title="Tahun", loc="upper right")
ax.set_xticks(sorted(monthly_df["mnth"].unique()))
plt.tight_layout()
st.pyplot(fig)

with st.expander("**Bagaimana Kesimpulannya?**"):
    st.markdown("""
    Tren bulanan memperlihatkan pengaruh musim yang kuat terhadap jumlah penyewaan.
    Permintaan mulai meningkat pada bulan Maret dan mencapai puncaknya selama periode
    pertengahan tahun (Juni–September). Perbandingan tahun ke tahun menunjukkan pertumbuhan
    bisnis yang pesat — performa 2012 selalu berada di atas capaian 2011 untuk seluruh bulan.
    """)

st.markdown("---")

# ─────────────────────────────────────────────
# 3. TREND PER JAM
# ─────────────────────────────────────────────
st.subheader("Trend Penyewaan Sepeda Berdasarkan Jam")

fig, ax = plt.subplots(figsize=(12, 5))
sns.lineplot(data=hourly_df, x="hr", y="cnt", hue="yr",
             palette="bright", marker="o", ax=ax)
ax.set_xlabel("Jam")
ax.set_ylabel("Jumlah")
ax.set_title("Jumlah Total Sepeda yang Disewakan Berdasarkan Jam dan Tahun")
ax.legend(title="Tahun", loc="upper right")
ax.set_xticks(sorted(hourly_df["hr"].unique()))
plt.tight_layout()
st.pyplot(fig)

with st.expander("**Bagaimana Kesimpulannya?**"):
    st.markdown("""
    Terdapat dua puncak utama penyewaan sepeda setiap hari, yaitu sekitar pukul **08.00 pagi**
    dan **17.00–18.00 sore**. Ini menunjukkan pola perjalanan komuter yang menggunakan sepeda
    untuk berangkat dan pulang kerja/sekolah. Tahun 2012 mencatat volume yang lebih tinggi
    di hampir setiap jam dibandingkan 2011, dan aktivitas terendah terjadi pada dini hari (00.00–05.00).
    """)

st.markdown("---")

# ─────────────────────────────────────────────
# 4. BERDASARKAN MUSIM
# ─────────────────────────────────────────────
season_mapping = {1: "Musim Dingin", 2: "Musim Semi", 3: "Musim Panas", 4: "Musim Gugur"}
season_df["season"] = season_df["season"].map(season_mapping)

st.subheader("Trend Penyewaan Sepeda Berdasarkan Musim")

fig, ax = plt.subplots(figsize=(9, 5))
sns.barplot(data=season_df, x="season", y="cnt", hue="yr",
            palette="bright", ax=ax)
ax.set_ylabel("Jumlah")
ax.set_title("Jumlah Total Sepeda yang Disewakan Berdasarkan Musim")
ax.legend(title="Tahun", loc="upper left")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, _: f"{val:,.0f}"))

# Ambil warna bar otomatis dari patch
bars_all = [patch for patch in ax.patches if patch.get_height() > 0]
for bar in bars_all:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3000,
            f"{bar.get_height():,.0f}", ha="center", va="bottom",
            fontsize=8, color=bar.get_facecolor(), fontweight="bold")
plt.tight_layout()
st.pyplot(fig)

with st.expander("**Bagaimana Kesimpulannya?**"):
    st.markdown("""
    Penyewaan sepeda meningkat secara signifikan pada musim hangat dan mencapai puncak di
    Musim Panas/Gugur, lalu menurun di musim dingin. Terdapat peningkatan jumlah penyewaan
    secara keseluruhan dari 2011 ke 2012 di semua musim, menunjukkan pertumbuhan popularitas
    layanan bike sharing yang konsisten.
    """)

st.markdown("---")

# ─────────────────────────────────────────────
# 5. HARI LIBUR & HARI KERJA
# ─────────────────────────────────────────────
st.subheader("Trend Penyewaan Sepeda Berdasarkan Hari Libur dan Hari Kerja")

col_holiday, col_workingday = st.columns(2)

with col_holiday:
    fig, ax = plt.subplots(figsize=(5, 4))
    plot_df = holiday_df.copy()
    plot_df["holiday"] = plot_df["holiday"].map({0: "Hari Biasa", 1: "Tanggal Merah"})
    sns.barplot(data=plot_df, x="holiday", y="cnt", hue="yr",
                palette="bright", ax=ax)
    ax.set_ylabel("Jumlah")
    ax.set_xlabel("")
    ax.set_title("Berdasarkan Hari Libur")
    ax.legend(title="Tahun", loc="upper left")
    ax.set_ylim(0, 2200000)
    ax.set_yticks(range(0, 2400000, 200000))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, _: f"{val:,.0f}"))
    for bar in [p for p in ax.patches if p.get_height() > 0]:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3000,
                f"{bar.get_height():,.0f}", ha="center", va="bottom",
                fontsize=7, color=bar.get_facecolor(), fontweight="bold")
    plt.tight_layout()
    st.pyplot(fig)

with col_workingday:
    fig, ax = plt.subplots(figsize=(5, 4))
    plot_df = workingday_df.copy()
    plot_df["workingday"] = plot_df["workingday"].map({0: "Hari Libur", 1: "Hari Kerja"})
    sns.barplot(data=plot_df, x="workingday", y="cnt", hue="yr",
                palette="bright", ax=ax)
    ax.set_ylabel("Jumlah")
    ax.set_xlabel("")
    ax.set_title("Berdasarkan Hari Kerja")
    ax.legend(title="Tahun", loc="upper left")
    ax.set_ylim(0, 2000000)
    ax.set_yticks(range(0, 2200000, 200000))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, _: f"{val:,.0f}"))
    for bar in [p for p in ax.patches if p.get_height() > 0]:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3000,
                f"{bar.get_height():,.0f}", ha="center", va="bottom",
                fontsize=7, color=bar.get_facecolor(), fontweight="bold")
    plt.tight_layout()
    st.pyplot(fig)

with st.expander("**Bagaimana Kesimpulannya?**"):
    st.markdown("""
    Jumlah total penyewaan sepeda lebih tinggi pada hari kerja dibandingkan hari libur
    di kedua tahun. Pada hari kerja tahun kedua, total penyewaan melonjak signifikan
    hingga melewati angka **1,4 juta**, hampir dua kali lipat dari capaian tahun sebelumnya.
    Dominasi volume pada hari kerja memperkuat indikasi bahwa penggunaan sepeda didorong oleh
    kebutuhan transportasi komuter rutin.
    """)

st.markdown("---")


# ─────────────────────────────────────────────
# 6. BERDASARKAN CUACA
# ─────────────────────────────────────────────
weather_mapping = {
    1: "Cerah",
    2: "Berawan/Berkabut",
    3: "Hujan Ringan/Salju",
    4: "Hujan Lebat/Badai"
}
weather_df["weathersit"] = weather_df["weathersit"].map(weather_mapping)

st.subheader("Trend Penyewaan Sepeda Berdasarkan Cuaca")

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=weather_df, x="weathersit", y="cnt", hue="yr",
            palette="bright", ax=ax)
ax.set_xlabel("Kondisi Cuaca")
ax.set_ylabel("Jumlah")
ax.set_title("Jumlah Total Sepeda yang Disewakan Berdasarkan Kondisi Cuaca")
ax.legend(title="Tahun", loc="upper left")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, _: f"{val:,.0f}"))
bars_all = [patch for patch in ax.patches if patch.get_height() > 0]
for bar in bars_all:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3000,
            f"{bar.get_height():,.0f}", ha="center", va="bottom",
            fontsize=8, color=bar.get_facecolor(), fontweight="bold")
plt.tight_layout()
st.pyplot(fig)

with st.expander("**Bagaimana Kesimpulannya?**"):
    st.markdown("""
    Kondisi cuaca berpengaruh besar terhadap jumlah penyewaan. Cuaca **cerah** menghasilkan
    volume penyewaan tertinggi, sementara cuaca buruk seperti hujan lebat atau badai
    menyebabkan penurunan drastis. Pola ini konsisten di kedua tahun, dengan 2012 selalu
    mengungguli 2011 pada setiap kondisi cuaca.
    """)

st.markdown("---")

# ─────────────────────────────────────────────
# KESIMPULAN AKHIR
# ─────────────────────────────────────────────
st.subheader("Kesimpulan Akhir")
st.info("""
Bisnis penyewaan sepeda mengalami pertumbuhan pesat dengan volume penyewaan pada tahun kedua yang jauh melampaui tahun pertama di semua kategori waktu. Pola penggunaan didominasi oleh aktivitas komuter pada hari kerja dengan puncak kepadatan di jam berangkat dan pulang kantor. Selain faktor rutinitas kerja, minat penyewaan juga sangat dipengaruhi oleh faktor musim di mana permintaan mencapai titik tertinggi pada periode pertengahan hingga menjelang akhir tahun.
""")