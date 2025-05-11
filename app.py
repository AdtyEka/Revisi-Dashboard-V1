import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# Konfigurasi tema dan styling
st.set_page_config(
    page_title="Dashboard Analisis Penyewaan Sepeda",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .plot-container {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1, h2, h3 {
        color: #1E88E5;
    }
    .stButton>button {
        width: 100%;
        border-radius: 0.5rem;
        background-color: #1E88E5;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 style="text-align: center; color: #1E88E5;">Dashboard Analisis Perilaku Penyewa Sepeda</h1>', unsafe_allow_html=True)
st.markdown('<hr style="border: 2px solid #1E88E5; margin: 20px 0;">', unsafe_allow_html=True)

# Load data
day = pd.read_csv('C__Users_ASUS_Downloads_day_cleaned.csv')
hour = pd.read_csv('C__Users_ASUS_Downloads_hour_cleaned.csv')

day['dteday'] = pd.to_datetime(day['dteday'])  
hour['dteday'] = pd.to_datetime(hour['dteday'])

# Sidebar
with st.sidebar:
    st.title("Dashboard Analisis Penyewaan Sepeda")
    st.image("https://img.freepik.com/free-vector/bicycle-sharing-concept-illustration_114360-1013.jpg", width=200)
    
    st.markdown("---")
    st.subheader("Filter Data")
    
    # Filter tanggal
    date_range = st.date_input(
        "Pilih Rentang Tanggal",
        [day['dteday'].min(), day['dteday'].max()]
    )
    
    # Filter musim
    selected_seasons = st.multiselect(
        "Pilih Musim",
        options=day['musim'].unique(),
        default=day['musim'].unique()
    )
    
    # Filter tipe pengguna
    user_type = st.radio(
        "Tipe Pengguna",
        ["Semua", "Aktif", "Non Aktif"]
    )
    
    st.markdown("---")
    st.markdown("### Tentang Dashboard")
    st.markdown("""
    Dashboard ini menampilkan analisis data penyewaan sepeda, termasuk:
    - Tren penyewaan harian
    - Pola penggunaan per jam
    - Dampak cuaca
    - Analisis musiman
    """)

# Terapkan filter ke data
day_filtered = day[day['musim'].isin(selected_seasons)]
# Filter hour berdasarkan tanggal yang sesuai dengan day_filtered
hour_filtered = hour[hour['dteday'].isin(day_filtered['dteday'])]

# Main content
st.markdown("### Analisis Data Penyewaan Sepeda")

# Metrics dengan styling yang lebih baik
st.markdown("### Metrik Utama")
col1, col2, col3 = st.columns(3)

with col1:
    total_penyewa = day_filtered['Total Penyewa'].sum()
    st.metric(
        label="Total Penyewa",
        value=f"{total_penyewa:,}",
        delta=None
    )

with col2:
    mean_penyewa = np.mean(day_filtered['Total Penyewa'])
    st.metric(
        label="Rata-rata Penyewa per Hari",
        value=f"{mean_penyewa:.0f}",
        delta=None
    )

with col3:
    mean_jam = np.mean(hour_filtered['Jam'])
    st.metric(
        label="Rata-rata Jam Penggunaan",
        value=f"{mean_jam:.0f}",
        delta=None
    )

# Visualizations dengan container dan styling
st.markdown("### Analisis Tren Penyewaan")
with st.container():
    @st.cache_data
    def get_daily_rentals(day):
        daily_rentals = day.groupby(by=['dteday'])[['Total Penyewa', 'non aktif', 'aktif']].sum().reset_index()
        return daily_rentals

    daily_rentals = get_daily_rentals(day_filtered)

    fig = px.line(daily_rentals, x='dteday', y=['Total Penyewa', 'non aktif', 'aktif'],
                  title='Tren Penyewaan Harian',
                  template='plotly_white',
                  labels={'value': 'Jumlah Penyewa', 'variable': 'Tipe Pengguna'})
    fig.update_layout(
        height=400,
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    st.plotly_chart(fig, use_container_width=True)

# Analisis per jam dengan layout yang lebih baik
st.markdown("### Analisis Per Jam")
col1, col2 = st.columns(2)

@st.cache_data
def get_rent_by_hour(hour):
    hourly_rentals = hour.groupby(by=['Jam'])[['Total Penyewa', 'non aktif', 'aktif']].sum().sort_values(by=['Total Penyewa'], ascending=False)
    hourly_rentals = hourly_rentals.reset_index()
    melted_data = hourly_rentals.melt(id_vars=['Jam'], value_vars=['Total Penyewa', 'non aktif', 'aktif'], var_name='User Type', value_name='Total Rentals')
    return melted_data

@st.cache_data
def get_rent_by_hour_trend(hour):
    pagi_df = hour[(hour['Jam'] >= 6) & (hour['Jam'] <= 9)].copy()
    malam_df = hour[(hour['Jam'] >= 18) & (hour['Jam'] <= 21)].copy()
    pagi_df.loc[:, 'Waktu'] = 'Pagi'
    malam_df.loc[:, 'Waktu'] = 'Malam'
    pagi_malam_df = pd.concat([pagi_df, malam_df])
    return pagi_malam_df

melted_data = get_rent_by_hour(hour_filtered)
pagi_malam_df = get_rent_by_hour_trend(hour_filtered)

with col1:
    fig = px.bar(melted_data, x='Jam', y='Total Rentals', color='User Type',
                title='Penyewaan per Jam berdasarkan Tipe Pengguna',
                template='plotly_white',
                barmode='group',
                labels={'Total Rentals': 'Total Penyewa', 'Jam': 'Jam'})
    fig.update_layout(
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(pagi_malam_df, x='Jam', y='Total Penyewa', color='Waktu',
                title='Pola Penyewaan Pagi vs Malam',
                template='plotly_white',
                barmode='group',
                labels={'Total Penyewa': 'Jumlah Penyewa', 'Jam': 'Jam'})
    fig.update_layout(
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    st.plotly_chart(fig, use_container_width=True)

# Analisis cuaca dengan tampilan yang lebih menarik
st.markdown("### Analisis Dampak Cuaca")
with st.container():
    @st.cache_data
    def get_weather_impact(day):
        weather_impact = day.groupby(by=['weathersit'])[['Total Penyewa', 'non aktif', 'aktif']].mean().reset_index()
        weather_impact['weathersit'] = weather_impact['weathersit'].map({
            1: 'Cerah',
            2: 'Berawan',
            3: 'Hujan Ringan',
            4: 'Hujan Lebat'
        })
        return weather_impact

    weather_impact = get_weather_impact(day_filtered)

    fig = px.bar(weather_impact, x='weathersit', y=['Total Penyewa', 'non aktif', 'aktif'],
                 title='Dampak Cuaca terhadap Penyewaan',
                 template='plotly_white',
                 barmode='group',
                 labels={'value': 'Jumlah Penyewa', 'variable': 'Tipe Pengguna'})
    fig.update_layout(
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    st.plotly_chart(fig, use_container_width=True)

# Analisis musim dengan tampilan yang lebih menarik
st.markdown("### Analisis Musim")
with st.container():
    @st.cache_data
    def get_season_analysis(day):
        season_analysis = day.groupby(by=['musim'])[['Total Penyewa', 'non aktif', 'aktif']].mean().reset_index()
        return season_analysis

    season_analysis = get_season_analysis(day_filtered)

    fig = px.bar(season_analysis, x='musim', y=['Total Penyewa', 'non aktif', 'aktif'],
                 title='Penyewaan berdasarkan Musim',
                 template='plotly_white',
                 barmode='group',
                 labels={'value': 'Jumlah Penyewa', 'variable': 'Tipe Pengguna'})
    fig.update_layout(
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    st.plotly_chart(fig, use_container_width=True)

# Footer dengan informasi tambahan
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <p>Dashboard ini dibuat untuk analisis data penyewaan sepeda</p>
        <p>© 2024 Analisis Data Penyewaan Sepeda</p>
    </div>
""", unsafe_allow_html=True)
        