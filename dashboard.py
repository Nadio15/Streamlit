import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# === Load Data ===
csv_file = "Aggregate.csv"  # file harus ada di repo
if not os.path.exists(csv_file):
    st.error(f"File {csv_file} tidak ditemukan. Pastikan ada di repo GitHub.")
    st.stop()

df = pd.read_csv(csv_file)

# Pastikan kolom DATE ada
if "DATE" not in df.columns:
    st.error("Kolom 'DATE' tidak ada di file CSV.")
    st.stop()

df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')

# === Ambil max date ===
max_date = df['DATE'].max()

# Sidebar filter
st.sidebar.header("Filter Tanggal")
filter_option = st.sidebar.selectbox(
    "Pilih range waktu:",
    ["Last 7 Days", "Last 14 Days", "Last 21 Days", "Last 30 Days"]
)

# Mapping filter ke jumlah hari
days_map = {
    "Last 7 Days": 7,
    "Last 14 Days": 14,
    "Last 21 Days": 21,
    "Last 30 Days": 30
}

# Filter data berdasarkan pilihan
days = days_map[filter_option]
min_date = max_date - pd.Timedelta(days=days)
df_filtered = df[df['DATE'] > min_date]

st.title("📊 Dashboard Availability Super 88 & Must Win 50 Kab")
st.write(f"Data terakhir: **{max_date.date()}**, filter: **{filter_option}**")

# === Grafik ===
if 'Technology' in df.columns:
    tech_list = df['Technology'].unique()
    for tech in tech_list:
        df_tech = df_filtered[df_filtered['Technology'] == tech]
        
        st.subheader(f"Availability Trend - {tech}")
        fig, ax = plt.subplots(figsize=(8, 4))
        for col in df_tech.columns:
            if col not in ['DATE', 'Technology']:
                ax.plot(df_tech['DATE'], df_tech[col], label=col)
        ax.legend()
        ax.set_xlabel("DATE")
        ax.set_ylabel("Availability (%)")
        st.pyplot(fig)
else:
    st.subheader("Availability Trend")
    fig, ax = plt.subplots(figsize=(8, 4))
    for col in df_filtered.columns:
        if col != 'DATE':
            ax.plot(df_filtered['DATE'], df_filtered[col], label=col)
    ax.legend()
    ax.set_xlabel("DATE")
    ax.set_ylabel("Availability (%)")
    st.pyplot(fig)
