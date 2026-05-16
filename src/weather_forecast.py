import sqlite3
from datetime import datetime
from pathlib import Path

import boto3
import pandas as pd
import requests
from botocore.exceptions import ClientError

# =========================
# S3 Settings
# =========================
S3_BUCKET = "jinseo-data-storage"
S3_KEY = "database/weather_forecast.db"

LOCAL_DB_PATH = Path("data/weather_forecast.db")

# =========================
# Main Australian Cities
# =========================
cities = {
    "Sydney": {"latitude": -33.8688, "longitude": 151.2093},
    "Melbourne": {"latitude": -37.8136, "longitude": 144.9631},
    "Brisbane": {"latitude": -27.4698, "longitude": 153.0251},
    "Perth": {"latitude": -31.9523, "longitude": 115.8613},
    "Adelaide": {"latitude": -34.9285, "longitude": 138.6007},
    "Hobart": {"latitude": -42.8821, "longitude": 147.3272},
    "Canberra": {"latitude": -35.2809, "longitude": 149.1300},
}


def download_db_from_s3():
    s3 = boto3.client("s3")
    LOCAL_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    try:
        s3.download_file(S3_BUCKET, S3_KEY, str(LOCAL_DB_PATH))
        print("Existing database downloaded from S3.")
    except ClientError as e:
        error_code = e.response["Error"]["Code"]

        if error_code in ["404", "NoSuchKey"]:
            print("No existing database found in S3. A new one will be created.")
        else:
            raise


def upload_db_to_s3():
    s3 = boto3.client("s3")
    s3.upload_file(str(LOCAL_DB_PATH), S3_BUCKET, S3_KEY)
    print(f"Database uploaded to s3://{S3_BUCKET}/{S3_KEY}")


def create_table():
    conn = sqlite3.connect(LOCAL_DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS weather_forecast (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            date TEXT NOT NULL,
            max_temp REAL,
            min_temp REAL,
            rain REAL,
            weather_code INTEGER,
            run_date TEXT NOT NULL,
            days_difference INTEGER,
            type TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(city, date, run_date)
        )
        """
    )

    conn.commit()
    conn.close()


def collect_weather_data():
    run_datetime = datetime.now()
    run_date = run_datetime.strftime("%Y-%m-%d %H:%M:%S")
    run_date_only = run_datetime.date()

    all_weather_data = []

    for city, coords in cities.items():
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={coords['latitude']}"
            f"&longitude={coords['longitude']}"
            "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code"
            "&forecast_days=7"
            "&timezone=auto"
        )

        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        daily = data["daily"]

        city_df = pd.DataFrame(
            {
                "city": city,
                "date": daily["time"],
                "max_temp": daily["temperature_2m_max"],
                "min_temp": daily["temperature_2m_min"],
                "rain": daily["precipitation_sum"],
                "weather_code": daily["weather_code"],
                "run_date": run_date,
            }
        )

        all_weather_data.append(city_df)

    df_weather = pd.concat(all_weather_data, ignore_index=True)

    df_weather["date"] = pd.to_datetime(df_weather["date"]).dt.date.astype(str)

    df_weather["days_difference"] = (
        pd.to_datetime(df_weather["date"]) - pd.to_datetime(run_date_only)
    ).dt.days

    df_weather["type"] = df_weather["days_difference"].apply(
        lambda x: "Actual" if x == 0 else "Prediction"
    )

    return df_weather


def insert_data(df_weather):
    conn = sqlite3.connect(LOCAL_DB_PATH)

    rows = df_weather[
        [
            "city",
            "date",
            "max_temp",
            "min_temp",
            "rain",
            "weather_code",
            "run_date",
            "days_difference",
            "type",
        ]
    ].values.tolist()

    cursor = conn.cursor()

    cursor.executemany(
        """
        INSERT OR IGNORE INTO weather_forecast (
            city,
            date,
            max_temp,
            min_temp,
            rain,
            weather_code,
            run_date,
            days_difference,
            type
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )

    conn.commit()

    inserted_count = cursor.rowcount

    conn.close()

    print(f"New rows inserted: {inserted_count}")


def preview_data():
    conn = sqlite3.connect(LOCAL_DB_PATH)

    df_preview = pd.read_sql_query(
        """
        SELECT *
        FROM weather_forecast
        ORDER BY run_date DESC, city, date
        LIMIT 10
        """,
        conn,
    )

    conn.close()

    print(df_preview)


def main():
    download_db_from_s3()
    create_table()

    df_weather = collect_weather_data()
    insert_data(df_weather)

    preview_data()
    upload_db_to_s3()


if __name__ == "__main__":
    main()