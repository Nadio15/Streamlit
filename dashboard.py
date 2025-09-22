import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import os

# === Load Data ===
csv_file = "Aggregate.csv"
if not os.path.exists(csv_file):
    st.error(f"File {csv_file} tidak ditemukan. Pastikan ada di repo GitHub.")
    st.stop()

df = pd.read_csv(csv_file)

# Pastikan ada kolom DATE
if "DATE" not in df.columns:
    st.error("Kolom 'DATE' tidak ada di file CSV.")
    st.stop()

df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')

# === Ambil max date ===
max_date = df['DATE'].max()

# Sidebar filter tanggal
st.sidebar.header("Filter Tanggal")
filter_option = st.sidebar.selectbox(
    "Pilih range waktu:",
    ["Last 7 Days", "Last 14 Days", "Last 21 Days", "Last 30 Days"]
)

days_map = {"Last 7 Days": 7, "Last 14 Days": 14,
            "Last 21 Days": 21, "Last 30 Days": 30}
days = days_map[filter_option]
min_date = max_date - pd.Timedelta(days=days)
df_filtered = df[df['DATE'] > min_date]

st.title("📊 Dashboard Availability")
st.write(f"Data terakhir: **{max_date.date()}**, filter: **{filter_option}**")

# === Mapping kolom berdasarkan Teknologi & Program ===
columns_map = {
    "2G": {
        "Normal": ["2G JAKARTA RAYA", "2G JAVA", "2G KALISUMAPA", "2G SUMATERA", "2G NATIONAL"],
        "MW": ["2G JAKARTA RAYA MW", "2G JAVA MW", "2G SUMATERA MW", "2G NATIONAL MW"],
        "SP": ["2G JAKARTA RAYA SP", "2G JAVA SP", "2G KALISUMAPA SP", "2G SUMATERA SP", "2G NATIONAL SP"],
        "75 Sites": ["2G Blended 75 Sites MW", "2G Blended 75 Sites SP", "2G Blended 75 Sites"]
    },
    "4G": {
        "Normal": ["4G JAKARTA RAYA", "4G JAVA", "4G KALISUMAPA", "4G SUMATERA", "4G NATIONAL"],
        "MW": ["4G JAKARTA RAYA MW", "4G JAVA MW", "4G SUMATERA MW", "4G NATIONAL MW"],
        "SP": ["4G JAKARTA RAYA SP", "4G JAVA SP", "4G KALISUMAPA SP", "4G SUMATERA SP", "4G NATIONAL SP"],
        "75 Sites": ["4G Blended 75 Sites MW", "4G Blended 75 Sites SP", "4G Blended 75 Sites"]
    },
    "Blended": {
        "All": ["2G Blended 75 Sites", "4G Blended 75 Sites"],
        "MW": ["2G Blended 75 Sites MW", "4G Blended 75 Sites MW"],
        "SP": ["2G Blended 75 Sites SP", "4G Blended 75 Sites SP"]
    },
    "Other": {
        "Threshold": ["Threshold"]
    }
}

# === List grafik yang mau ditampilkan (8 grafik utama) ===
graph_list = [
    ("2G", "Normal"),
    ("2G", "MW"),
    ("2G", "SP"),
    ("2G", "75 Sites"),
    ("4G", "Normal"),
    ("4G", "MW"),
    ("4G", "SP"),
    ("4G", "75 Sites"),
]

st.header("📊 Dashboard Availability - 8 Grafik")

# === Loop tampilkan dalam grid 2 kolom x 4 baris ===
for i in range(0, len(graph_list), 2):
    col1, col2 = st.columns(2)

    # Grafik kiri
    tech1, prog1 = graph_list[i]
    with col1:
        st.subheader(f"{tech1} - {prog1}")
        fig, ax = plt.subplots(figsize=(6, 3))
        for col in columns_map[tech1][prog1]:
            if col in df_filtered.columns:
                y = df_filtered[col]
                if y.max() <= 1.0:
                    y = y * 100
                ax.plot(df_filtered['DATE'], y, label=col)
        ax.legend(fontsize=7)
        ax.set_xlabel("DATE")
        ax.set_ylabel("Availability (%)")
        ax.yaxis.set_major_formatter(mtick.PercentFormatter())
        st.pyplot(fig)

    # Grafik kanan (kalau ada)
    if i + 1 < len(graph_list):
        tech2, prog2 = graph_list[i+1]
        with col2:
            st.subheader(f"{tech2} - {prog2}")
            fig, ax = plt.subplots(figsize=(6, 3))
            for col in columns_map[tech2][prog2]:
                if col in df_filtered.columns:
                    y = df_filtered[col]
                    if y.max() <= 1.0:
                        y = y * 100
                    ax.plot(df_filtered['DATE'], y, label=col)
            ax.legend(fontsize=7)
            ax.set_xlabel("DATE")
            ax.set_ylabel("Availability (%)")
            ax.yaxis.set_major_formatter(mtick.PercentFormatter())
            st.pyplot(fig)
