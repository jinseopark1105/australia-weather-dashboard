# Australia Weather Forecast Dashboard

This project collects 7-day weather forecast data for major Australian cities using the Open-Meteo API.

The goal of this project is to build a dashboard that compares weather forecasts with actual weather data and shows how accurate the predictions are over time.

## Project Overview

The project currently collects daily weather forecast data for seven major Australian cities:

- Sydney
- Melbourne
- Brisbane
- Perth
- Adelaide
- Hobart
- Canberra

The collected data includes:

- City
- Date
- Max Temp
- Min Temp
- Rain
- Weather Code
- Run Date
- Days Difference
- Type

## Data Meaning

`Run Date` means the date and time when the script was executed.

`Type` is used to separate actual weather and forecast weather:

- `Actual`: when Date and Run Date are the same day
- `Prediction`: when Date is after Run Date

`Days Difference` shows how many days ahead the forecast is.

For example:

- 0 = today / actual
- 1 = tomorrow forecast
- 2 = two days ahead forecast

## API Used

This project uses the Open-Meteo Forecast API.

Example API format:

```txt
https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code&forecast_days=7&timezone=auto


## Project Structure

australia-weather-dashboard/
│
├── src/
│   └── weather_forecast.py
│
├── data/
│
├── README.md
├── requirements.txt
└── .gitignore