import os
import sys
import requests
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq

from src.pipeline.predict_pipeline import PredictPipeline, PollutantData, get_aqi_category
from src.logger import logging
from src.exception import CustomException

load_dotenv()

application = Flask(__name__)
app = application
CORS(app)

OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
GROQ_API_KEY        = os.getenv('GROQ_API_KEY')

groq_client = Groq(api_key=GROQ_API_KEY)


# ─── OpenWeatherMap Helpers ────────────────────────────────────────────────────

def get_city_name(lat, lon):
    url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={OPENWEATHER_API_KEY}"
    data = requests.get(url).json()
    return data[0].get('name', 'Unknown') if data else 'Unknown'


def get_air_pollution(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
    return requests.get(url).json()


def get_weather(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    return requests.get(url).json()


def get_air_pollution_forecast(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
    return requests.get(url).json()


def get_weather_forecast(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    return requests.get(url).json()


def build_pollutant_data(components, weather, city, month):
    no  = components.get('no', 0)
    no2 = components.get('no2', 0)
    return PollutantData(
        city=city,
        pm25=components.get('pm2_5', 0),
        pm10=components.get('pm10', 0),
        no=no,
        no2=no2,
        nox=no + no2,
        nh3=components.get('nh3', 0),
        co=components.get('co', 0),
        so2=components.get('so2', 0),
        o3=components.get('o3', 0),
        month=month,
        temperature=weather['main']['temp'],
        humidity=weather['main']['humidity'],
        wind_speed=weather['wind']['speed']
    )


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/aqi', methods=['POST'])
def get_aqi():
    try:
        data        = request.get_json()
        lat         = data['lat']
        lon         = data['lon']
        month       = datetime.now().month

        city            = get_city_name(lat, lon)
        pollution_data  = get_air_pollution(lat, lon)
        weather_data    = get_weather(lat, lon)

        components = pollution_data['list'][0]['components']

        pollutant_obj = build_pollutant_data(components, weather_data, city, month)
        df            = pollutant_obj.get_data_as_data_frame()

        pipeline  = PredictPipeline()
        preds     = pipeline.predict(df)
        aqi_value = round(float(preds[0]), 2)
        category, color = get_aqi_category(aqi_value)

        logging.info(f"AQI predicted for {city}: {aqi_value} ({category})")

        return jsonify({
            'aqi':      aqi_value,
            'category': category,
            'color':    color,
            'city':     city,
            'pollutants': {
                'pm25': round(components.get('pm2_5', 0), 2),
                'pm10': round(components.get('pm10',  0), 2),
                'no2':  round(components.get('no2',   0), 2),
                'o3':   round(components.get('o3',    0), 2),
                'co':   round(components.get('co',    0), 2),
                'so2':  round(components.get('so2',   0), 2),
            },
            'weather': {
                'temperature': weather_data['main']['temp'],
                'humidity':    weather_data['main']['humidity'],
                'wind_speed':  weather_data['wind']['speed'],
                'description': weather_data['weather'][0]['description']
            }
        })

    except Exception as e:
        raise CustomException(e, sys)


@app.route('/api/forecast', methods=['POST'])
def get_forecast():
    try:
        data = request.get_json()
        lat  = data['lat']
        lon  = data['lon']

        city               = get_city_name(lat, lon)
        pollution_forecast = get_air_pollution_forecast(lat, lon)
        weather_forecast   = get_weather_forecast(lat, lon)

        pipeline     = PredictPipeline()
        forecasts    = []
        target_hours = [1, 3, 6, 24]

        for hours in target_hours:
            poll_idx    = min(hours, len(pollution_forecast['list']) - 1)
            weather_idx = min(hours // 3, len(weather_forecast['list']) - 1)

            components = pollution_forecast['list'][poll_idx]['components']
            weather    = weather_forecast['list'][weather_idx]
            month      = datetime.now().month

            pollutant_obj = build_pollutant_data(components, weather, city, month)
            df            = pollutant_obj.get_data_as_data_frame()
            preds         = pipeline.predict(df)
            aqi_value     = round(float(preds[0]), 2)
            category, color = get_aqi_category(aqi_value)

            forecasts.append({
                'hours':    hours,
                'aqi':      aqi_value,
                'category': category,
                'color':    color
            })

        return jsonify({'forecasts': forecasts})

    except Exception as e:
        raise CustomException(e, sys)


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data         = request.get_json()
        user_message = data['message']
        context      = data.get('context', {})

        system_prompt = f"""You are a helpful AI assistant inside an AQI (Air Quality Index) monitoring app.

Current air quality data for {context.get('city', 'the user location')}:
- AQI: {context.get('aqi', 'N/A')} — {context.get('category', 'N/A')}
- PM2.5: {context.get('pm25', 'N/A')} µg/m³
- PM10: {context.get('pm10', 'N/A')} µg/m³
- NO2: {context.get('no2', 'N/A')} µg/m³
- O3: {context.get('o3', 'N/A')} µg/m³
- Temperature: {context.get('temperature', 'N/A')}°C
- Humidity: {context.get('humidity', 'N/A')}%
- Wind Speed: {context.get('wind_speed', 'N/A')} m/s

Answer questions about air quality, health impacts, safety advice, and current readings.
Be concise, friendly, and helpful. Keep responses under 3 sentences unless detail is needed."""

        response = groq_client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message}
            ]
        )

        return jsonify({'response': response.choices[0].message.content})

    except Exception as e:
        raise CustomException(e, sys)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
