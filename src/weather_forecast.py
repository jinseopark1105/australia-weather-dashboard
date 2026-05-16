import requests
import pandas as pd
from datetime import datetime
from pathlib import Path

cities = {
    "Sydney": {"latitude": -33.8688, "longitude": 151.2093},
    "Melbourne": {"latitude": -37.8136, "longitude": 144.9631},
    "Brisbane": {"latitude": -27.4698, "longitude": 153.0251},
    "Perth": {"latitude": -31.9523, "longitude": 115.8613},
    "Adelaide": {"latitude": -34.9285, "longitude": 138.6007},
    "Hobart": {"latitude": -42.8821, "longitude": 147.3272},
    "Canberra": {"latitude": -35.2809, "longitude": 149.1300}
}

run_datetime = datetime.now()
run_date = run_datetime.strftime("%Y-%m-%d %H:%M:%S")
run_date_only = run_datetime.date()

all_weather_data = []

for city, coords in cities.items():
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={coords['latitude']}"
        f"&longitude={coords['longitude']}"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code"
        f"&forecast_days=7"
        f"&timezone=auto"
    )

    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    daily = data["daily"]

    city_df = pd.DataFrame({
        "City": city,
        "Date": daily["time"],
        "Max Temp": daily["temperature_2m_max"],
        "Min Temp": daily["temperature_2m_min"],
        "Rain": daily["precipitation_sum"],
        "Weather Code": daily["weather_code"],
        "Run Date": run_date
    })

    all_weather_data.append(city_df)

df_weather = pd.concat(all_weather_data, ignore_index=True)

df_weather["Date"] = pd.to_datetime(df_weather["Date"]).dt.date

df_weather["Days Difference"] = (
    pd.to_datetime(df_weather["Date"]) - pd.to_datetime(run_date_only)
).dt.days

df_weather["Type"] = df_weather["Days Difference"].apply(
    lambda x: "Actual" if x == 0 else "Prediction"
)

print(df_weather)

output_path = Path("data/australia_weather_forecast.csv")
output_path.parent.mkdir(exist_ok=True)
df_weather.to_csv(output_path, index=False)

print(f"\nSaved to: {output_path}")