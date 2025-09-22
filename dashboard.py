import streamlit as st
import pandas as pd
import os

# try import plotly
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except Exception:
    PLOTLY_AVAILABLE = False

# matplotlib import (selalu di-import karena fallback/opsi)
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

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

# Sidebar: filter tanggal + pilihan plotting
st.sidebar.header("Filter & Options")
filter_option = st.sidebar.selectbox(
    "Pilih range waktu:",
    ["Last 7 Days", "Last 14 Days", "Last 21 Days", "Last 30 Days"]
)

plot_choice = st.sidebar.radio(
    "Library visualisasi:",
    ("Plotly (interaktif)", "Matplotlib (static)")
)

# Jika user pilih Plotly tetapi lib tidak terinstall, beri info
if plot_choice.startswith("Plotly") and not PLOTLY_AVAILABLE:
    st.sidebar.warning("Plotly tidak terdeteksi di environment. Aplikasi akan menggunakan Matplotlib sebagai fallback.")
    plot_choice = "Matplotlib (static)"

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

# Grafik list (8)
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

st.header("📊 Dashboard Availability - 8 Grafik (4 kolom × 2 baris)")

# Helper: dapatkan list kolom yang betul2 ada pada df_filtered
def existing_cols(cols):
    return [c for c in cols if c in df_filtered.columns]

# Tampilkan grid (4 kolom per baris)
for i in range(0, len(graph_list), 4):
    cols = st.columns(4)
    for j, col_container in enumerate(cols):
        idx = i + j
        if idx >= len(graph_list):
            continue
        tech, prog = graph_list[idx]
        selected_cols = existing_cols(columns_map[tech][prog])

        with col_container:
            st.subheader(f"{tech} - {prog}")
            if not selected_cols:
                st.info("Tidak ada kolom data untuk kombinasi ini.")
                continue

            # Prepare dataframe untuk plotting
            df_plot = df_filtered[["DATE"] + selected_cols].melt(id_vars="DATE",
                                                                 value_vars=selected_cols,
                                                                 var_name="Region",
                                                                 value_name="Availability")
            # jika semua kosong, skip
            if df_plot["Availability"].dropna().empty:
                st.info("Data kosong untuk range tanggal ini.")
                continue

            # jika nilai <= 1 dianggap proporsi -> convert ke persen
            if df_plot["Availability"].dropna().max() <= 1.0:
                df_plot["Availability"] = df_plot["Availability"] * 100

            if plot_choice.startswith("Plotly") and PLOTLY_AVAILABLE:
                # Plotly interactive
                fig = px.line(df_plot, x="DATE", y="Availability", color="Region",
                              markers=True, labels={"Availability": "Availability (%)"},
                              template="plotly_white")
                fig.update_yaxes(ticksuffix="%", showgrid=True)
                fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20),
                                  legend=dict(font=dict(size=9)))
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Matplotlib static
                fig, ax = plt.subplots(figsize=(4.5, 2.8))
                for region, grp in df_plot.groupby("Region"):
                    ax.plot(grp["DATE"], grp["Availability"], marker='o', label=region)
                ax.set_xlabel("DATE")
                ax.set_ylabel("Availability (%)")
                ax.yaxis.set_major_formatter(mtick.PercentFormatter())
                ax.legend(fontsize=7)
                fig.tight_layout()
                st.pyplot(fig)
