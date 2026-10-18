import requests
import pandas as pd

URL = "https://archive-api.open-meteo.com/v1/archive"

LOCATIONS = {
    "Newcastle": (54.9783, -1.6178),
    "Middlesbrough": (54.5742, -1.2350),
    "Sunderland": (54.9069, -1.3838),
    "London": (51.5072, -0.1276),
    "Manchester": (53.4808, -2.2426),
}

def fetch_weather(city, start, end):
    lat, lon = LOCATIONS[city]
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,wind_speed_10m_max",
        "timezone": "Europe/London",
    }
    response = requests.get(URL, params=params, timeout=30)
    response.raise_for_status()
    df = pd.DataFrame(response.json()["daily"])
    df["city"] = city
    return df

if __name__ == "__main__":
    frames = []
    for city in LOCATIONS:
        print(f"Fetching {city}...")
        frames.append(fetch_weather(city, "2015-01-01", "2025-12-31"))
    data = pd.concat(frames, ignore_index=True)
    data.to_csv("data/raw/weather_raw.csv", index=False)
    print(f"Saved {len(data)} rows")