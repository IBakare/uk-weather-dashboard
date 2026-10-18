import pandas as pd

# Load
df = pd.read_csv("data/raw/weather_raw.csv", parse_dates=["time"])
print("Raw rows:", len(df))

# Rename columns
df = df.rename(columns={
    "time": "date",
    "temperature_2m_max": "temp_max_c",
    "temperature_2m_min": "temp_min_c",
    "temperature_2m_mean": "temp_mean_c",
    "precipitation_sum": "rain_mm",
    "wind_speed_10m_max": "wind_max_kmh",
})

# Quality checks
print("\nMissing values per column:")
print(df.isna().sum())
print("\nDuplicate rows:", df.duplicated(subset=["date", "city"]).sum())

# Clean
df = df.drop_duplicates(subset=["date", "city"])
df = df.dropna(subset=["temp_mean_c", "rain_mm", "wind_max_kmh"])
df = df[df["temp_max_c"].between(-30, 45)]
df = df[df["rain_mm"] >= 0]

# Add features
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["month_name"] = df["date"].dt.strftime("%b")

def get_season(month):
    if month in (12, 1, 2):
        return "Winter"
    if month in (3, 4, 5):
        return "Spring"
    if month in (6, 7, 8):
        return "Summer"
    return "Autumn"

df["season"] = df["month"].apply(get_season)

# Save
df.to_csv("data/clean/weather_clean.csv", index=False)
print("\nClean rows:", len(df))
print(df.head())