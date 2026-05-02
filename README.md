# AQI Forecasting System (ML Project)

## Overview

This project predicts real-time and forecasted Air Quality Index (AQI) values based on live pollutant and weather data fetched from OpenWeatherMap. It uses a trained machine learning model to make predictions and includes a Gemini AI-powered chatbot for health advice.

The project follows a modular ML pipeline architecture — data ingestion, transformation, model training, and a production Flask web app.

---

## Project Objectives

- Fetch live air pollution and weather data from OpenWeatherMap API
- Predict AQI using a trained Random Forest regression model
- Forecast AQI for the next 1, 3, 6, and 24 hours
- Provide AI-powered health advice via Gemini chatbot
- Deploy a clean, responsive web interface

---

## Problem Statement

Given real-time pollutant readings (PM2.5, PM10, NO2, O3, CO, SO2, etc.) and weather conditions (temperature, humidity, wind speed) for a city and month, predict the AQI value and classify it into a health category.

---

## Project Structure

```
aqi-forecasting-system/
│
├── artifacts/                  # Generated model and preprocessor files
│   ├── model.pkl
│   └── preprocessor.pkl
│
├── data/
│   └── preprocessed/           # Cleaned dataset ready for ML
│       └── city_day_final_for_ml.csv
│
├── notebooks/                  # Jupyter notebooks (EDA & model training)
│   ├── 1_EDA_AQI_Dataset.ipynb
│   └── 2_ML_Model_Training.ipynb
│
├── src/
│   ├── components/
│   │   ├── data_ingestion.py
│   │   ├── data_transformation.py
│   │   └── model_trainer.py
│   │
│   ├── pipeline/
│   │   ├── train_pipeline.py
│   │   └── predict_pipeline.py
│   │
│   ├── __init__.py
│   ├── exception.py
│   ├── logger.py
│   └── utils.py
│
├── static/
│   ├── css/style.css
│   └── js/app.js
│
├── templates/
│   └── index.html
│
├── app.py                      # Flask web application
├── setup.py
├── requirements.txt
└── README.md
```

---

## Tech Stack

- **Python 3.13**
- **Pandas, NumPy** — data processing
- **Scikit-learn, XGBoost, CatBoost** — machine learning
- **Flask, Flask-CORS** — web framework
- **Google Gemini (google-genai)** — AI chatbot
- **OpenWeatherMap API** — live air quality and weather data
- **HTML, CSS, JavaScript** — frontend

---

## ML Pipeline Workflow

### 1. Data Ingestion
- Reads cleaned dataset from `data/preprocessed/city_day_final_for_ml.csv`
- Splits into 80% train and 20% test
- Saves to `artifacts/`

### 2. Data Transformation
- Handles missing values with `SimpleImputer`
- Scales numerical features with `StandardScaler`
- Encodes categorical features with `OneHotEncoder`
- Saves preprocessing pipeline as `artifacts/preprocessor.pkl`

### 3. Model Training
- Trains 10 regression models with GridSearchCV hyperparameter tuning
- Models: Random Forest, XGBoost, CatBoost, Gradient Boosting, AdaBoost, Decision Tree, Linear Regression, Ridge, Lasso, K-Nearest Neighbors
- Best model (Random Forest, R2 approximately 91.1%) saved as `artifacts/model.pkl`

---

## Features Used

**Numerical Features**
- `pm25`, `pm10`, `no`, `no2`, `nox`, `nh3`, `co`, `so2`, `o3`
- `temperature`, `humidity`, `wind_speed`
- `month`

**Categorical Features**
- `city`

**Target**
- `AQI` (continuous value)

---

## AQI Categories

| AQI Range | Category     | Meaning                                |
|-----------|--------------|----------------------------------------|
| 0 - 50    | Good         | Safe for all                           |
| 51 - 100  | Satisfactory | Acceptable for most                    |
| 101 - 200 | Moderate     | Sensitive groups should take care      |
| 201 - 300 | Poor         | Avoid prolonged outdoor exposure       |
| 301 - 400 | Very Poor    | Stay indoors, wear a mask outside      |
| 401+      | Severe       | Hazardous - avoid all outdoor activity |

---

## How to Run the Project

### Step 1: Clone the repository
```bash
git clone <your-repo-link>
cd aqi-forecasting-system
```

### Step 2: Create and activate virtual environment
```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set up environment variables
Create a `.env` file in the project root:
```
OPENWEATHER_API_KEY=your_openweathermap_api_key
GEMINI_API_KEY=your_gemini_api_key
```

### Step 5: Train the ML model (first time only)
```bash
python -m src.components.data_ingestion
```

### Step 6: Run the web app
```bash
python app.py
```

Open `http://localhost:5000` in your browser.

---

## Sample Output

After training, the following are generated:
```
artifacts/
 ├── model.pkl
 └── preprocessor.pkl
```

The web app shows:
- Live AQI with health category
- Current weather (temperature, humidity, wind)
- Pollutant breakdown (PM2.5, PM10, NO2, O3, CO, SO2)
- AQI forecast for +1, +3, +6, +24 hours
- AI chatbot for health advice

---

## Key Highlights

- Modular and scalable ML pipeline architecture
- Production-level folder structure
- Custom logging and exception handling
- Live data from OpenWeatherMap — no manual input needed
- Gemini AI chatbot with real-time AQI context
- Clean, responsive light-theme frontend

---

## Common Issues and Fixes

| Issue | Solution |
|-------|----------|
| File not found error | Ensure correct working directory |
| Model not found | Run data ingestion to train and save model |
| API errors | Check `.env` file has valid API keys |
| Import errors | Run using `python -m` or check `setup.py` install |
| Location access denied | Allow browser location permissions |

---

## Future Improvements

- Deploy on Render (cloud hosting)
- Add historical AQI charts
- Health recommendation engine
- Push notifications for hazardous AQI
- Docker containerization

---

## Author

Surya Prakash
Suresh Tak

---

## Acknowledgements

- OpenWeatherMap API
- Google Gemini AI
- Scikit-learn documentation
- Central Pollution Control Board (CPCB) - dataset inspiration
