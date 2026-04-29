import sys
import os
import pandas as pd
from src.exception import CustomException
from src.utils import load_object


AQI_CATEGORIES = [
    (50,  "Good",         "#00C853"),
    (100, "Satisfactory", "#64DD17"),
    (200, "Moderate",     "#FFD600"),
    (300, "Poor",         "#FF6D00"),
    (400, "Very Poor",    "#DD2C00"),
    (float('inf'), "Severe", "#6200EA")
]


def get_aqi_category(aqi_value):
    for limit, label, color in AQI_CATEGORIES:
        if aqi_value <= limit:
            return label, color
    return "Severe", "#6200EA"


class PredictPipeline:
    def __init__(self):
        pass

    def predict(self, features):
        try:
            model_path = os.path.join("artifacts", "model.pkl")
            preprocessor_path = os.path.join("artifacts", "preprocessor.pkl")
            print("Before Loading")
            model = load_object(file_path=model_path)
            preprocessor = load_object(file_path=preprocessor_path)
            print("After Loading")
            data_scaled = preprocessor.transform(features)
            preds = model.predict(data_scaled)
            return preds

        except Exception as e:
            raise CustomException(e, sys)


class PollutantData:
    def __init__(self, city, pm25, pm10, no, no2, nox, nh3, co, so2, o3,
                 month, temperature, humidity, wind_speed):
        self.city = city
        self.pm25 = pm25
        self.pm10 = pm10
        self.no = no
        self.no2 = no2
        self.nox = nox
        self.nh3 = nh3
        self.co = co
        self.so2 = so2
        self.o3 = o3
        self.month = month
        self.temperature = temperature
        self.humidity = humidity
        self.wind_speed = wind_speed

    def get_data_as_data_frame(self):
        try:
            return pd.DataFrame({
                'City':        [self.city],
                'PM2.5':       [self.pm25],
                'PM10':        [self.pm10],
                'NO':          [self.no],
                'NO2':         [self.no2],
                'NOx':         [self.nox],
                'NH3':         [self.nh3],
                'CO':          [self.co],
                'SO2':         [self.so2],
                'O3':          [self.o3],
                'Month':       [self.month],
                'Temperature': [self.temperature],
                'Humidity':    [self.humidity],
                'Wind_Speed':  [self.wind_speed]
            })

        except Exception as e:
            raise CustomException(e, sys)
