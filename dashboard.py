import streamlit as st
import pandas as pd
import plotly.express as px
import os

# === Load Data ===
csv_file = "Aggregate.csv"
if not os.path.exists(csv_file):
    st.error(f"File {csv_file} tidak ditemukan. Pastikan ada di repo GitHub.")
    st.stop()

df = pd.read_csv(csv_file)

if "DATE" not in df.columns:
    st.error("Kolom 'DATE' tidak ada di file CSV.")
    st.stop()

df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')

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
    }
}

# Grafik yang mau ditampilkan
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

# === Tampilkan 8 grafik dengan 4 kolom per baris ===
for i in range(0, len(graph_list), 4):
    cols = st.columns(4)
    for j, col_container in enumerate(cols):
        if i + j < len(graph_list):
            tech, prog = graph_list[i + j]
            selected_cols = columns_map[tech][prog]
            df_plot = df_filtered.melt(id_vars="DATE", value_vars=selected_cols,
                                       var_name="Region", value_name="Availability")
            # kalau datanya <1, konversi ke %
            if df_plot["Availability"].max() <= 1.0:
                df_plot["Availability"] = df_plot["Availability"] * 100

            with col_container:
                st.subheader(f"{tech} - {prog}")
                fig = px.line(df_plot, x="DATE", y="Availability",
                              color="Region", markers=True,
                              labels={"Availability": "Availability (%)"},
                              template="plotly_white")
                fig.update_yaxes(ticksuffix="%", showgrid=True)
                fig.update_layout(height=300, legend=dict(font=dict(size=9)))
                st.plotly_chart(fig, use_container_width=True)
