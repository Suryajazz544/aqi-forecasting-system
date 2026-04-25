import pandas as pd
import numpy as np
from datetime import datetime

# Load the dataset
df = pd.read_csv('data/raw/city_day.csv')
print("Original dataset shape:", df.shape)
print("Columns:", df.columns.tolist())

# Convert Date to datetime
df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
# Extract month for seasonal patterns
df['Month'] = df['Date'].dt.month

# GENERATE TEMPERATURE
def generate_temperature(row):
    """Generate realistic temperature based on month"""
    month = row['Month']
    
    # India seasonal temperatures (approximate)
    if month in [12, 1, 2]:  # Winter
        base_temp = np.random.uniform(15, 25)
    elif month in [3, 4, 5]:  # Summer
        base_temp = np.random.uniform(35, 45)
    elif month in [6, 7, 8, 9]:  # Monsoon
        base_temp = np.random.uniform(25, 32)
    else:  # Oct, Nov (post-monsoon)
        base_temp = np.random.uniform(25, 35)
    # Add small variation
    variation = np.random.normal(0, 1.5)
    temp = base_temp + variation
    
    return round(temp, 1)

# GENERATE HUMIDITY
def generate_humidity(row):
    """Generate realistic humidity based on month and AQI"""
    month = row['Month']
    aqi = row['AQI']
    
    # Base humidity by month
    if month in [6, 7, 8, 9]:  # Monsoon (wet)
        base_humidity = np.random.uniform(70, 85)
    elif month in [12, 1, 2]:  # Winter (dry)
        base_humidity = np.random.uniform(50, 65)
    else:  # Others (moderate)
        base_humidity = np.random.uniform(55, 70)
    # High AQI often correlates with low humidity (inverse relationship)
    if aqi > 200:
        humidity_adjustment = -5  # Lower humidity in high pollution
    elif aqi > 150:
        humidity_adjustment = -2
    else:
        humidity_adjustment = 0
    
    humidity = base_humidity + humidity_adjustment
    humidity = np.clip(humidity, 20, 100)  # Keep between 20-100%
    
    return round(humidity, 1)

# GENERATE WIND SPEED
def generate_wind_speed(row):
    """Generate realistic wind speed based on month"""
    month = row['Month']
    aqi = row['AQI']
    
    # Base wind speed by month
    if month in [3, 4, 5]:  # Pre-monsoon (windy)
        base_wind = np.random.uniform(5, 12)
    elif month in [6, 7, 8, 9]:  # Monsoon (very windy)
        base_wind = np.random.uniform(8, 15)
    else:  # Others (calm)
        base_wind = np.random.uniform(2, 8)
    # High wind = low AQI expected
    variation = np.random.normal(0, 1)
    wind_speed = base_wind + variation
    wind_speed = np.clip(wind_speed, 0, 20)  # Max 20 km/h
    
    return round(wind_speed, 1)

# APPLY GENERATION
print("\nGenerating Temperature...")
df['Temperature'] = df.apply(generate_temperature, axis=1)

print("Generating Humidity...")
df['Humidity'] = df.apply(generate_humidity, axis=1)

print("Generating Wind_Speed...")
df['Wind_Speed'] = df.apply(generate_wind_speed, axis=1)

# VERIFY AND SAVE
print("\nNew columns generated!")
print("New dataset shape:", df.shape)
print("New columns:", df.columns.tolist())

print("\nFirst few rows with new columns:")
print(df[['City', 'Date', 'Temperature', 'Humidity', 'Wind_Speed', 'AQI']].head(10))

print("\nSummary statistics:")
print("\nTemperature:")
print(df['Temperature'].describe())
print("\nHumidity:")
print(df['Humidity'].describe())
print("\nWind_Speed:")
print(df['Wind_Speed'].describe())

# Save the enhanced dataset
output_path = 'data/preprocessed/city_day_with_weather.csv'
df.to_csv(output_path, index=False)
print(f"\n✅ Enhanced dataset saved to: {output_path}")
print(f"Total rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")