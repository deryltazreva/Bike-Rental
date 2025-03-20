import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from datetime import datetime

# Konfigurasi tampilan
st.set_page_config(
    page_title="Bicycle Rental Analysis Dashboard",
    page_icon="🚴",
    layout="wide"
)

# Fungsi untuk memuat dan membersihkan data
@st.cache_data
def load_data(file_path="dashboard/day.csv"):
    """Load and preprocess the bicycle rental data"""
    df = pd.read_csv(file_path)
    
    # Mengganti nama kolom untuk lebih deskriptif
    column_mapping = {
        'dteday': 'date',
        'yr': 'year',
        'mnth': 'month',
        'weathersit': 'weather_condition',
        'cnt': 'total_rentals'
    }
    df.rename(columns=column_mapping, inplace=True)
    
    # Menghapus kolom yang tidak diperlukan
    if 'windspeed' in df.columns:
        df.drop(columns=['windspeed'], inplace=True)
    
    # Mengubah nilai numerik menjadi kategori
    month_names = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April', 
        5: 'May', 6: 'June', 7: 'July', 8: 'August', 
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }
    
    season_names = {
        1: 'Spring', 2: 'Summer', 3: 'Autumn', 4: 'Winter'
    }
    
    weekday_names = {
        0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 
        4: 'Thursday', 5: 'Friday', 6: 'Saturday'
    }
    
    weather_descriptions = {
        1: 'Clear/Fair', 
        2: 'Cloudy/Mist', 
        3: 'Light Precipitation', 
        4: 'Extreme Weather'
    }
    
    df['month'] = df['month'].map(month_names)
    df['season'] = df['season'].map(season_names)
    df['weekday'] = df['weekday'].map(weekday_names)
    df['weather_condition'] = df['weather_condition'].map(weather_descriptions)
    
    return df

# Fungsi untuk analisis data
def create_aggregated_data(df, group_by_col, agg_col='total_rentals', include_user_types=False):
    """Create aggregated data based on specified grouping column"""
    if include_user_types:
        agg_data = df.groupby(group_by_col)[['casual', 'registered', agg_col]].sum().reset_index()
    else:
        agg_data = df.groupby(group_by_col)[agg_col].sum().reset_index()
    
    return agg_data

def create_sorted_monthly_data(df):
    """Create monthly data sorted in calendar order"""
    monthly_data = df.groupby('month')['total_rentals'].sum().reset_index()
    month_order = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    monthly_data['month_order'] = monthly_data['month'].map({m: i for i, m in enumerate(month_order)})
    monthly_data = monthly_data.sort_values('month_order').drop('month_order', axis=1)
    
    return monthly_data

# Fungsi untuk visualisasi
def create_time_series_chart(data, x_col, y_col, title, color='skyblue'):
    """Create a time series chart with data labels"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(data[x_col], data[y_col], marker='o', linestyle='-', linewidth=2, color=color)
    
    # Menambahkan label data
    for i, val in enumerate(data[y_col]):
        ax.annotate(f"{val:,}", (i, val), textcoords="offset points", 
                    xytext=(0, 10), ha='center', fontsize=10)
    
    ax.set_title(title, fontsize=16)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='x', rotation=45)
    
    return fig

def create_dual_bar_chart(data, x_col, y1_col, y2_col, title):
    """Create a dual bar chart for comparing two categories"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = range(len(data))
    width = 0.35
    
    # Membuat dua bar chart berdampingan
    bars1 = ax.bar([i - width/2 for i in x], data[y1_col], width, label=y1_col.capitalize(), color='steelblue')
    bars2 = ax.bar([i + width/2 for i in x], data[y2_col], width, label=y2_col.capitalize(), color='darkorange')
    
    # Menambahkan label data
    for bar in bars1:
        height = bar.get_height()
        ax.annotate(f"{int(height):,}", xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')
    
    for bar in bars2:
        height = bar.get_height()
        ax.annotate(f"{int(height):,}", xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')
    
    ax.set_title(title, fontsize=16)
    ax.set_xticks(x)
    ax.set_xticklabels(data[x_col])
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    return fig

def create_single_bar_chart(data, x_col, y_col, title, color_palette=None):
    """Create a single bar chart"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    bars = sns.barplot(data=data, x=x_col, y=y_col, palette=color_palette, ax=ax)
    
    # Menambahkan label data
    for i, bar in enumerate(bars.patches):
        height = bar.get_height()
        ax.annotate(f"{int(height):,}", xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5), textcoords="offset points", ha='center', va='bottom')
    
    ax.set_title(title, fontsize=16)
    ax.grid(True, alpha=0.3, axis='y')
    
    return fig

# Main application
def main():
    # Judul dashboard
    st.title("🚴 Bicycle Rental Analysis Dashboard")
    
    # Path ke file data
    file_path = "day.csv"
    
    # Memuat dan memproses data
    try:
        df = load_data(file_path)
        
        # Mengubah format tanggal
        df['date'] = pd.to_datetime(df['date'])
        
        # Filter tanggal di sidebar
        with st.sidebar:
            st.header("Date Range Filter")
            min_date = df['date'].min().date()
            max_date = df['date'].max().date()
            
            date_range = st.date_input(
                "Select Date Range",
                value=[min_date, max_date],
                min_value=min_date,
                max_value=max_date
            )
            
            if len(date_range) == 2:
                start_date, end_date = date_range
                filtered_df = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]
            else:
                filtered_df = df
            
            # Tambahan filter di sidebar
            st.header("Additional Filters")
            
            # Filter berdasarkan season
            seasons = df['season'].unique().tolist()
            selected_seasons = st.multiselect(
                "Select Seasons", 
                options=seasons,
                default=seasons
            )
            
            # Filter berdasarkan kondisi cuaca
            weather_conditions = df['weather_condition'].unique().tolist()
            selected_weather = st.multiselect(
                "Select Weather Conditions",
                options=weather_conditions,
                default=weather_conditions
            )
            
            # Terapkan filter tambahan
            if selected_seasons:
                filtered_df = filtered_df[filtered_df['season'].isin(selected_seasons)]
            
            if selected_weather:
                filtered_df = filtered_df[filtered_df['weather_condition'].isin(selected_weather)]
        
        # Dashboard metrics
        st.header("Rental Overview")
        
        # Tampilkan KPI
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_rentals = filtered_df['total_rentals'].sum()
            st.metric("Total Rentals", f"{total_rentals:,}")
        
        with col2:
            casual_rentals = filtered_df['casual'].sum()
            st.metric("Casual Users", f"{casual_rentals:,}")
        
        with col3:
            registered_rentals = filtered_df['registered'].sum()
            st.metric("Registered Users", f"{registered_rentals:,}")
        
        with col4:
            avg_daily_rentals = filtered_df['total_rentals'].mean()
            st.metric("Average Daily Rentals", f"{avg_daily_rentals:.1f}")
        
        # Visualisasi tren bulanan
        st.header("Monthly Rental Trends")
        monthly_data = create_sorted_monthly_data(filtered_df)
        monthly_chart = create_time_series_chart(
            monthly_data, 'month', 'total_rentals', 
            "Monthly Rental Distribution", color='royalblue'
        )
        st.pyplot(monthly_chart)
        
        # Visualisasi berdasarkan musim
        st.header("Seasonal Analysis")
        season_data = create_aggregated_data(filtered_df, 'season', include_user_types=True)
        season_chart = create_dual_bar_chart(
            season_data, 'season', 'registered', 'casual',
            "Rental Distribution by Season"
        )
        st.pyplot(season_chart)
        
        # Visualisasi berdasarkan kondisi cuaca
        st.header("Weather Impact Analysis")
        weather_data = create_aggregated_data(filtered_df, 'weather_condition')
        weather_colors = ["#3498db", "#f39c12", "#2ecc71", "#e74c3c"]
        weather_chart = create_single_bar_chart(
            weather_data, 'weather_condition', 'total_rentals',
            "Rental Distribution by Weather Condition", color_palette=weather_colors
        )
        st.pyplot(weather_chart)
        
        # Visualisasi berdasarkan hari dalam seminggu
        st.header("Weekly Patterns")
        
        # Mengatur tampilan beberapa grafik dalam tab
        tab1, tab2, tab3 = st.tabs(["Weekday Analysis", "Working Day Analysis", "Holiday Analysis"])
        
        with tab1:
            weekday_data = create_aggregated_data(filtered_df, 'weekday')
            # Mengurutkan hari dalam seminggu
            weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekday_data['weekday_order'] = weekday_data['weekday'].map({d: i for i, d in enumerate(weekday_order)})
            weekday_data = weekday_data.sort_values('weekday_order').drop('weekday_order', axis=1)
            
            weekday_colors = sns.color_palette("husl", 7)
            weekday_chart = create_single_bar_chart(
                weekday_data, 'weekday', 'total_rentals',
                "Rental Distribution by Day of Week", color_palette=weekday_colors
            )
            st.pyplot(weekday_chart)
        
        with tab2:
            working_day_data = create_aggregated_data(filtered_df, 'workingday')
            working_day_data['workingday'] = working_day_data['workingday'].map({0: 'Non-Working Day', 1: 'Working Day'})
            working_day_chart = create_single_bar_chart(
                working_day_data, 'workingday', 'total_rentals',
                "Rental Distribution by Working vs Non-Working Days", color_palette=["#9b59b6", "#3498db"]
            )
            st.pyplot(working_day_chart)
        
        with tab3:
            holiday_data = create_aggregated_data(filtered_df, 'holiday')
            holiday_data['holiday'] = holiday_data['holiday'].map({0: 'Non-Holiday', 1: 'Holiday'})
            holiday_chart = create_single_bar_chart(
                holiday_data, 'holiday', 'total_rentals',
                "Rental Distribution on Holidays vs Non-Holidays", color_palette=["#e74c3c", "#2ecc71"]
            )
            st.pyplot(holiday_chart)
        
        # Eksplorasi data mentah
        st.header("Raw Data Explorer")
        if st.checkbox("Show Raw Data"):
            st.dataframe(filtered_df)
            
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
        st.info("Please ensure the day.csv file is in the same directory as this script")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

    # Footer
    st.divider()
    st.caption(f"Bicycle Rental Analysis Dashboard • Created by Your Name • {datetime.now().year}")

if __name__ == "__main__":
    main()