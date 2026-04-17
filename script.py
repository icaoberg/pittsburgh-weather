# ╔══════════════════════════════════════════════════════════════════════════╗
# ║         Pittsburgh Weather — Hourly Forecast Collector & Plotter         ║
# ║                                                                          ║
# ║  Copyright © 2026  Ivan E. Cao-Berg <icaoberg@andrew.cmu.edu>            ║
# ║  Computational Biology Department                                        ║
# ║  Carnegie Mellon University                                              ║
# ║                                                                          ║
# ║  Data sourced from the Open-Meteo API (https://open-meteo.com)           ║
# ╚══════════════════════════════════════════════════════════════════════════╝

import requests
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os
import shutil

today = datetime.today()
today_str = today.strftime("%Y%m%d")
month_str = today.strftime("%Y%m")

os.makedirs("data", exist_ok=True)
parquet_filename = os.path.join("data", f"{month_str}.parquet")
plot_filename = os.path.join("data", f"{today_str}.png")
plot_today_filename = os.path.join("data", "today.png")

url = (
    "https://api.open-meteo.com/v1/forecast?"
    "latitude=40.4406&longitude=-79.9959&"
    "current_weather=true&"
    "hourly=temperature_2m,precipitation,wind_speed_10m&"
    "daily=temperature_2m_max,temperature_2m_min,precipitation_sum&"
    "timezone=America%2FNew_York"
)

try:
    response = requests.get(url)
    response.raise_for_status()
    weather_data = response.json()

    # Build DataFrame from hourly forecast
    hourly = weather_data["hourly"]
    df_new = pd.DataFrame({
        "timestamp": pd.to_datetime(hourly["time"]),
        "temperature_2m": hourly["temperature_2m"],
        "precipitation": hourly["precipitation"],
        "wind_speed_10m": hourly["wind_speed_10m"],
    })
    df_new["fetched_date"] = today_str

    # Append to monthly parquet, replacing any existing rows fetched today
    if os.path.exists(parquet_filename):
        df_existing = pd.read_parquet(parquet_filename)
        df_existing = df_existing[df_existing["fetched_date"] != today_str]
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    df_combined.sort_values("timestamp", inplace=True)
    df_combined.to_parquet(parquet_filename, index=False)
    print(f"Weather data saved to '{parquet_filename}'.")

    # ── Plot ──────────────────────────────────────────────────────────────────
    timestamps = df_new["timestamp"]
    temperatures = df_new["temperature_2m"]
    precipitation = df_new["precipitation"]
    now = datetime.now()

    plt.style.use("seaborn-v0_8-darkgrid")
    fig, ax1 = plt.subplots(figsize=(14, 6))

    # Precipitation bars on secondary y-axis (drawn first so temp line sits on top)
    ax2 = ax1.twinx()
    ax2.bar(timestamps, precipitation, width=1 / 24, color="steelblue", alpha=0.4, label="Precipitation (mm)")
    ax2.set_ylabel("Precipitation (mm)", color="steelblue", fontsize=10)
    ax2.tick_params(axis="y", labelcolor="steelblue")
    max_precip = precipitation.max()
    ax2.set_ylim(0, max_precip * 5 if max_precip > 0 else 5)

    # Temperature line on primary y-axis
    ax1.plot(timestamps, temperatures, color="tab:red", linewidth=2, label="Temperature (°C)", zorder=3)
    ax1.set_ylabel("Temperature (°C)", color="tab:red", fontsize=10)
    ax1.tick_params(axis="y", labelcolor="tab:red")
    ax1.set_xlabel("Date / Time", fontsize=10)

    # Current-time marker with temperature annotation
    if timestamps.min() <= now <= timestamps.max():
        ax1.axvline(x=now, color="dimgray", linestyle="--", linewidth=1.5, zorder=4)
        idx = (timestamps - now).abs().idxmin()
        nearest_temp = temperatures.iloc[idx]
        ax1.annotate(
            f"Now\n{nearest_temp:.1f}°C",
            xy=(now, nearest_temp),
            xytext=(12, 8),
            textcoords="offset points",
            fontsize=8,
            color="dimgray",
            arrowprops=dict(arrowstyle="->", color="dimgray"),
            zorder=5,
        )

    # X-axis: one label per day, minor ticks at 6-hour intervals
    ax1.xaxis.set_major_locator(mdates.DayLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%a\n%m/%d"))
    ax1.xaxis.set_minor_locator(mdates.HourLocator(byhour=[6, 12, 18]))
    plt.xticks(rotation=0)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=9)

    plt.title("7-Day Hourly Forecast — Pittsburgh, PA", fontsize=13)
    plt.tight_layout()

    plt.savefig(plot_filename, dpi=120)
    shutil.copy(plot_filename, plot_today_filename)
    print(f"Plot saved to '{plot_filename}' and copied to '{plot_today_filename}'.")

except requests.RequestException as e:
    print(f"Error fetching data from Open-Meteo API: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
