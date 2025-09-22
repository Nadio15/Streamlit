import streamlit as st
import pandas as pd
import os

# === Page Config ===
st.set_page_config(
    page_title="Dashboard Availability",
    layout="wide"
)

# === Mode Siang/Malam ===
theme = st.sidebar.radio("🌓 Pilih Mode Tampilan:", ["Siang", "Malam"])

if theme == "Siang":
    bg_color = "#ffffff"
    text_color = "#000000"
    plotly_template = "plotly_white"
    mpl_facecolor = "#ffffff"
else:
    bg_color = "#000000"
    text_color = "#ffffff"
    plotly_template = "plotly_dark"
    mpl_facecolor = "#000000"

# CSS global
st.markdown(f"""
    <style>
        body {{
            background-color: {bg_color};
            color: {text_color};
        }}
        .block-container {{
            background-color: {bg_color};
            color: {text_color};
        }}
    </style>
""", unsafe_allow_html=True)

# Custom CSS padding
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# try import plotly
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except Exception:
    PLOTLY_AVAILABLE = False

# matplotlib import
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# === Load Data ===
csv_file = "Aggregate.csv"
if not os.path.exists(csv_file):
    st.error(f"File {csv_file} tidak ditemukan.")
    st.stop()

df = pd.read_csv(csv_file)

# Rename kolom blended 75
rename_map = {
    "2G Blended 75 Sites MW": "2G Part 75 from MW",
    "2G Blended 75 Sites SP": "2G Part 75 from SP",
    "2G Blended 75 Sites": "2G 75 Blended",
    "4G Blended 75 Sites MW": "4G Part 75 from MW",
    "4G Blended 75 Sites SP": "4G Part 75 from SP",
    "4G Blended 75 Sites": "4G 75 Blended"
}
df.rename(columns=rename_map, inplace=True)

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

if plot_choice.startswith("Plotly") and not PLOTLY_AVAILABLE:
    st.sidebar.warning("Plotly tidak tersedia. Pakai Matplotlib sebagai fallback.")
    plot_choice = "Matplotlib (static)"

days_map = {"Last 7 Days": 7, "Last 14 Days": 14,
            "Last 21 Days": 21, "Last 30 Days": 30}
days = days_map[filter_option]
min_date = max_date - pd.Timedelta(days=days)
df_filtered = df[df['DATE'] > min_date]

st.title("📊 Dashboard Availability")
st.write(f"Data terakhir: **{max_date.date()}**, filter: **{filter_option}**")

# === Warna konsisten untuk setiap region ===
region_colors = {
    "JAKARTA RAYA": "#0FFFFF",
    "JAVA": "#DC143C",
    "KALISUMAPA": "#66FF00",
    "SUMATERA": "#FFD700",
    "NATIONAL": "#C0C0C0",
    "Part 75 from MW": "#FF00FF",
    "Part 75 from SP": "#03C03C",
    "75 Blended": "#0000FF"
}

# Normalisasi nama region
def normalize_region(region_name: str):
    for key in region_colors.keys():
        if key in region_name:
            return key
    return region_name

# Mapping kolom
columns_map = {
    "2G": {
        "Normal": ["2G JAKARTA RAYA", "2G JAVA", "2G KALISUMAPA", "2G SUMATERA", "2G NATIONAL"],
        "MW": ["2G JAKARTA RAYA MW", "2G JAVA MW", "2G SUMATERA MW", "2G NATIONAL MW"],
        "SP": ["2G JAKARTA RAYA SP", "2G JAVA SP", "2G KALISUMAPA SP", "2G SUMATERA SP", "2G NATIONAL SP"],
        "75 Sites": ["2G Part 75 from MW", "2G Part 75 from SP", "2G 75 Blended"]
    },
    "4G": {
        "Normal": ["4G JAKARTA RAYA", "4G JAVA", "4G KALISUMAPA", "4G SUMATERA", "4G NATIONAL"],
        "MW": ["4G JAKARTA RAYA MW", "4G JAVA MW", "4G SUMATERA MW", "4G NATIONAL MW"],
        "SP": ["4G JAKARTA RAYA SP", "4G JAVA SP", "4G KALISUMAPA SP", "4G SUMATERA SP", "4G NATIONAL SP"],
        "75 Sites": ["4G Part 75 from MW", "4G Part 75 from SP", "4G 75 Blended"]
    }
}

# Grafik list
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

def existing_cols(cols):
    return [c for c in cols if c in df_filtered.columns]

# Tampilkan grid
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

            df_plot = df_filtered[["DATE"] + selected_cols].melt(
                id_vars="DATE",
                value_vars=selected_cols,
                var_name="Region",
                value_name="Availability"
            )

            if df_plot["Availability"].dropna().empty:
                st.info("Data kosong untuk range tanggal ini.")
                continue

            if df_plot["Availability"].dropna().max() <= 1.0:
                df_plot["Availability"] = df_plot["Availability"] * 100

            df_plot["BaseRegion"] = df_plot["Region"].apply(normalize_region)

            if plot_choice.startswith("Plotly") and PLOTLY_AVAILABLE:
                fig = px.line(
                    df_plot, x="DATE", y="Availability", color="BaseRegion",
                    markers=True, labels={"Availability": "Availability (%)"},
                    template=plotly_template,
                    color_discrete_map=region_colors
                )
                fig.update_yaxes(ticksuffix="%", showgrid=True)
                fig.update_xaxes(tickangle=90)
                fig.update_layout(
                    height=280,
                    margin=dict(l=10, r=10, t=40, b=10),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.1,
                        xanchor="center",
                        x=0.5,
                        font=dict(size=9)
                    ),
                    legend_title_text="",
                    paper_bgcolor="rgba(0,0,0,0)",  # transparan
                    plot_bgcolor="rgba(0,0,0,0)"    # transparan
                )
                if tech == "4G" and prog in ["Normal", "SP", "MW"]:
                    fig.add_hline(
                        y=99.7,
                        line_dash="dash",
                        line_color="red"
                    )
                st.plotly_chart(fig, use_container_width=True)

            else:
                fig, ax = plt.subplots(figsize=(4.5, 2.8))
                fig.patch.set_alpha(0)       # figure transparan
                ax.set_facecolor("none")     # axes transparan

                for region, grp in df_plot.groupby("Region"):
                    base_region = normalize_region(region)
                    color = region_colors.get(base_region, None)
                    ax.plot(grp["DATE"], grp["Availability"], marker='o', label=region, color=color)

                if tech == "4G" and prog in ["Normal", "SP", "MW"]:
                    ax.axhline(
                        y=99.7,
                        color="red",
                        linestyle="--",
                        linewidth=1,
                        label="Threshold 99.7%"
                    )

                ax.set_xlabel("DATE", color=text_color)
                ax.set_ylabel("Availability (%)", color=text_color)
                ax.tick_params(colors=text_color)
                ax.yaxis.set_major_formatter(mtick.PercentFormatter())
                plt.setp(ax.get_xticklabels(), rotation=90, ha="center")
                ax.legend(
                    fontsize=6,
                    loc='upper center',
                    bbox_to_anchor=(0.5, 1.25),
                    ncol=2,
                    title=None
                )
                fig.tight_layout()
                st.pyplot(fig, transparent=True)

# === Tabel Data Lengkap ===
st.markdown("---")
st.subheader("📋 Data Tabel")

df_table = df_filtered.copy()
for col in df_table.select_dtypes(include="number").columns:
    if df_table[col].max() <= 1:
        df_table[col] = (df_table[col] * 100).round(2).astype(str) + "%"
    else:
        df_table[col] = df_table[col].round(2).astype(str) + "%"

st.dataframe(df_table, use_container_width=True)

# === Opsi Download ===
st.markdown("### 💾 Download Data")

csv = df_filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download CSV",
    data=csv,
    file_name="dashboard_filtered.csv",
    mime="text/csv"
)

import io
output = io.BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df_filtered.to_excel(writer, index=False, sheet_name="FilteredData")
output.seek(0)

st.download_button(
    label="⬇️ Download Excel",
    data=output,
    file_name="dashboard_filtered.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
