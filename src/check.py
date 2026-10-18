import pandas as pd

df = pd.read_csv("data/clean/weather_clean.csv", parse_dates=["date"])

print("Date range:", df["date"].min().date(), "to", df["date"].max().date())
print("Cities:", df["city"].nunique())
print("Days per city:")
print(df.groupby("city").size())
print()
print(df[["temp_max_c", "temp_min_c", "temp_mean_c", "rain_mm", "wind_max_kmh"]].describe().round(1))