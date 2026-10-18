import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="UK Weather Trends", layout="wide")

METRICS = {
    "Mean temperature (°C)": "temp_mean_c",
    "Max temperature (°C)": "temp_max_c",
    "Min temperature (°C)": "temp_min_c",
    "Rainfall (mm)": "rain_mm",
    "Max wind speed (km/h)": "wind_max_kmh",
}

@st.cache_data
def load_data():
    return pd.read_csv("data/clean/weather_clean.csv", parse_dates=["date"])

df = load_data()

# Title
st.title("UK Historical Weather Trends")
st.caption("Daily data 2015-2025 | Source: Open-Meteo (CC BY 4.0)")

# Sidebar filters
st.sidebar.header("Filters")
cities = st.sidebar.multiselect(
    "City", sorted(df["city"].unique()), default=["Newcastle"]
)
year_range = st.sidebar.slider(
    "Years", int(df["year"].min()), int(df["year"].max()),
    (int(df["year"].min()), int(df["year"].max()))
)
metric_label = st.sidebar.selectbox("Metric", list(METRICS.keys()))
metric = METRICS[metric_label]

# Apply filters
f = df[df["city"].isin(cities) & df["year"].between(*year_range)]
if f.empty:
    st.warning("Select at least one city to see data.")
    st.stop()

# KPI row
c1, c2, c3 = st.columns(3)
c1.metric("Average temperature (°C)", f"{f['temp_mean_c'].mean():.1f}")
c2.metric("Total rainfall (mm)", f"{f['rain_mm'].sum():,.0f}")
c3.metric("Peak wind (km/h)", f"{f['wind_max_kmh'].max():.0f}")

# Chart 1: monthly trend
f = f.assign(month_start=f["date"].dt.to_period("M").dt.to_timestamp())
if metric == "rain_mm":
    monthly = f.groupby(["month_start", "city"])[metric].sum().reset_index()
else:
    monthly = f.groupby(["month_start", "city"])[metric].mean().reset_index()
fig1 = px.line(monthly, x="month_start", y=metric, color="city",
               title=f"Monthly trend: {metric_label}",
               labels={"month_start": "Month", metric: metric_label})
st.plotly_chart(fig1, width="stretch")

# Chart 2: seasonal comparison
order = ["Winter", "Spring", "Summer", "Autumn"]
season = f.groupby(["season", "city"])[metric].mean().reset_index()
fig2 = px.bar(season, x="season", y=metric, color="city", barmode="group",
              category_orders={"season": order},
              title=f"Seasonal average: {metric_label}",
              labels={"season": "Season", metric: metric_label})
st.plotly_chart(fig2, width="stretch")

# Chart 3: year x month heatmap
heat = f.groupby(["year", "month"])[metric].mean().reset_index()
fig3 = px.density_heatmap(heat, x="month", y="year", z=metric,
                          histfunc="avg", nbinsx=12,
                          title=f"Year × month heatmap: {metric_label}",
                          labels={"month": "Month", "year": "Year"})
st.plotly_chart(fig3, width="stretch")

# ---------- Deeper analysis ----------
st.subheader("Deeper analysis")
tab1, tab2, tab3, tab4 = st.tabs(["Anomalies", "Extreme days", "Warming trend", "Daily view"])

# Tab 1: anomalies vs the 2015-2025 average
with tab1:
    baseline = df.groupby("city")[metric].mean()
    yearly = f.groupby(["year", "city"])[metric].mean().reset_index()
    yearly["anomaly"] = yearly[metric] - yearly["city"].map(baseline)
    fig4 = px.bar(
        yearly, x="year", y="anomaly", color="city", barmode="group",
        title=f"Difference from 2015-2025 average: {metric_label}",
        labels={"anomaly": "Difference from average", "year": "Year"},
    )
    fig4.add_hline(y=0, line_color="grey")
    st.plotly_chart(fig4, width="stretch")
    st.caption("Above zero = higher than the 11-year average. Below zero = lower.")

# Tab 2: extreme day counts
with tab2:
    a, b, c = st.columns(3)
    hot = a.slider("Hot day above (°C)", 20, 35, 25)
    wet = b.slider("Wet day above (mm)", 5, 30, 10)
    windy = c.slider("Windy day above (km/h)", 30, 70, 50)
    kind = st.radio("Show", ["Hot days", "Wet days", "Windy days"], horizontal=True)

    col, limit = {
        "Hot days": ("temp_max_c", hot),
        "Wet days": ("rain_mm", wet),
        "Windy days": ("wind_max_kmh", windy),
    }[kind]

    counts = (f[f[col] > limit].groupby(["year", "city"]).size()
              .reset_index(name="days"))
    if counts.empty:
        st.info("No days exceed this threshold. Try lowering it.")
    else:
        fig5 = px.bar(counts, x="year", y="days", color="city", barmode="group",
                      title=f"{kind} per year (threshold: {limit})",
                      labels={"days": "Number of days", "year": "Year"})
        st.plotly_chart(fig5, width="stretch")
        st.caption("Years with no qualifying days do not show a bar.")

# Tab 3: warming trend
with tab3:
    annual = f.groupby(["year", "city"])["temp_mean_c"].mean().reset_index()
    fig6 = px.line(annual, x="year", y="temp_mean_c", color="city", markers=True,
                   title="Annual mean temperature",
                   labels={"temp_mean_c": "Mean temperature (°C)", "year": "Year"})
    st.plotly_chart(fig6, width="stretch")

    rows = []
    for city, g in annual.groupby("city"):
        if len(g) >= 3:
            slope = np.polyfit(g["year"], g["temp_mean_c"], 1)[0]
            rows.append({"City": city, "Change per decade (°C)": round(slope * 10, 2)})
    if rows:
        st.dataframe(pd.DataFrame(rows), hide_index=True)
    st.caption("Based on a short record (about 11 years), so treat this as indicative, "
               "not a climate conclusion.")

# Tab 4: daily view
with tab4:
    min_d, max_d = df["date"].min().date(), df["date"].max().date()
    day = st.date_input("Pick a day", value=max_d, min_value=min_d, max_value=max_d)

    day_df = df[df["city"].isin(cities) & (df["date"].dt.date == day)]

    # Same calendar date across all years, for comparison
    same_date = df[(df["date"].dt.month == day.month) & (df["date"].dt.day == day.day)]
    normal = same_date.groupby("city")["temp_mean_c"].mean()

    st.markdown(f"### {day.strftime('%A %d %B %Y')}")
    cols = st.columns(len(day_df))
    for col, (_, r) in zip(cols, day_df.iterrows()):
        delta = r["temp_mean_c"] - normal[r["city"]]
        col.metric(r["city"], f"{r['temp_mean_c']:.1f} °C",
                   f"{delta:+.1f} °C vs usual for this date")
        col.write(f"High {r['temp_max_c']:.1f} °C / Low {r['temp_min_c']:.1f} °C")
        col.write(f"Rain {r['rain_mm']:.1f} mm")
        col.write(f"Wind {r['wind_max_kmh']:.0f} km/h")

    # Window around the chosen day
    window = st.slider("Days either side to show", 3, 60, 14)
    start = pd.Timestamp(day) - pd.Timedelta(days=window)
    end = pd.Timestamp(day) + pd.Timedelta(days=window)
    win = df[df["city"].isin(cities) & df["date"].between(start, end)]

    fig7 = px.line(win, x="date", y=metric, color="city", markers=True,
                   title=f"{metric_label} around {day.strftime('%d %b %Y')}",
                   labels={"date": "Date", metric: metric_label})
    fig7.add_vline(x=pd.Timestamp(day), line_dash="dash", line_color="grey")
    st.plotly_chart(fig7, width="stretch")

# Download
st.download_button(
    "Download filtered data (CSV)",
    f.drop(columns="month_start").to_csv(index=False),
    "filtered_weather.csv",
    "text/csv",
)