import os
import time
from datetime import date, timedelta

import pandas as pd
import requests

URL = "https://archive-api.open-meteo.com/v1/archive"

LOCATIONS = {
    "Newcastle": (54.9783, -1.6178),
    "Middlesbrough": (54.5742, -1.2350),
    "Sunderland": (54.9069, -1.3838),
    "London": (51.5072, -0.1276),
    "Manchester": (53.4808, -2.2426),
}

START = "2015-01-01"
# The archive lags a few days behind, so stop 5 days before today
END = (date.today() - timedelta(days=5)).isoformat()


def fetch_weather(city, start, end, retries=5):
    lat, lon = LOCATIONS[city]
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,wind_speed_10m_max",
        "timezone": "Europe/London",
    }
    for attempt in range(1, retries + 1):
        response = requests.get(URL, params=params, timeout=30)
        if response.status_code == 429:
            wait = 30 * attempt
            print(f"  Rate limited. Waiting {wait}s (attempt {attempt}/{retries})...")
            time.sleep(wait)
            continue
        response.raise_for_status()
        df = pd.DataFrame(response.json()["daily"])
        df["city"] = city
        return df
    raise RuntimeError(f"Still rate limited for {city} after {retries} attempts")


if __name__ == "__main__":
    os.makedirs("data/raw", exist_ok=True)
    frames = []
    for city in LOCATIONS:
        print(f"Fetching {city}...")
        frames.append(fetch_weather(city, START, END))
        time.sleep(10)  # pause between cities
    data = pd.concat(frames, ignore_index=True)
    data.to_csv("data/raw/weather_raw.csv", index=False)
    print(f"Saved {len(data)} rows up to {END}")