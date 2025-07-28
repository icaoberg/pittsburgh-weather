import requests
import json
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Get today's date in YYYYMMDD format
today_str = datetime.today().strftime("%Y%m%d")

# Prepare output folder and file paths
os.makedirs("data", exist_ok=True)
json_filename = os.path.join("data", f"{today_str}.json")
plot_filename = os.path.join("data", f"{today_str}.png")
symlink_json = os.path.join("data", "weather.json")
symlink_png = os.path.join("data", "weather.png")

# Define the Open-Meteo API URL for Pittsburgh
url = (
    "https://api.open-meteo.com/v1/forecast?"
    "latitude=40.4406&longitude=-79.9959&"
    "current_weather=true&"
    "hourly=temperature_2m,precipitation,wind_speed_10m&"
    "daily=temperature_2m_max,temperature_2m_min,precipitation_sum&"
    "timezone=America%2FNew_York"
)

try:
    # Make the API request
    response = requests.get(url)
    response.raise_for_status()
    weather_data = response.json()

    # Save JSON data to file
    with open(json_filename, "w") as f:
        json.dump(weather_data, f, indent=2)
    print(f"Weather data saved to '{json_filename}'.")

    # Create or update JSON symlink
    if os.path.islink(symlink_json) or os.path.exists(symlink_json):
        os.remove(symlink_json)
    os.symlink(os.path.abspath(json_filename), symlink_json)
    print(f"Symlink created: {symlink_json} -> {json_filename}")

    # Extract hourly timestamps and temperatures
    timestamps = weather_data["hourly"]["time"]
    temperatures = weather_data["hourly"]["temperature_2m"]
    time_objs = [datetime.fromisoformat(t) for t in timestamps]

    # Plot the hourly temperature
    plt.figure(figsize=(10, 5))
    plt.plot(time_objs, temperatures, label="Temperature (°C)", color="tab:red", linewidth=2)
    plt.title("Hourly Temperature Forecast - Pittsburgh")
    plt.xlabel("Time")
    plt.ylabel("Temperature (°C)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # Save the plot
    plt.savefig(plot_filename)
    print(f"Plot saved to '{plot_filename}'.")

    # Create or update PNG symlink
    if os.path.islink(symlink_png) or os.path.exists(symlink_png):
        os.remove(symlink_png)
    os.symlink(os.path.abspath(plot_filename), symlink_png)
    print(f"Symlink created: {symlink_png} -> {plot_filename}")

except requests.RequestException as e:
    print(f"Error fetching data from Open-Meteo API: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")