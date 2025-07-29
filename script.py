import requests
import json
import matplotlib.pyplot as plt
from datetime import datetime
import os
import shutil

# ─────────────────────────────────────────────────────────────
# Get today's date formatted as YYYYMMDD (e.g., 20250728)
# ─────────────────────────────────────────────────────────────
today_str = datetime.today().strftime("%Y%m%d")

# ─────────────────────────────────────────────────────────────
# Ensure output directory exists and set file paths
# ─────────────────────────────────────────────────────────────
os.makedirs("data", exist_ok=True)
json_filename = os.path.join("data", f"{today_str}.json")
plot_filename = os.path.join("data", f"{today_str}.png")
plot_today_filename = os.path.join("data", "today.png")

# ─────────────────────────────────────────────────────────────
# Checks for coordinates with Pittsburgh as the default
# ─────────────────────────────────────────────────────────────
lat = 40.4406
long = -79.9959
def coords(lat, long):
    lat = latitude
    long = longitude


# ─────────────────────────────────────────────────────────────
# Creates endpoint
# ─────────────────────────────────────────────────────────────

url = (
    "https://api.open-meteo.com/v1/forecast?"
    f"latitude={lat}&longitude={long}&"
    "current_weather=true&"
    "hourly=temperature_2m,precipitation,wind_speed_10m&"
    "daily=temperature_2m_max,temperature_2m_min,precipitation_sum&"
    "timezone=America%2FNew_York"
)

try:
    # ─────────────────────────────────────────────────────────
    # Retrieves city name:
    # ─────────────────────────────────────────────────────────
    headers = {
    "User-Agent": "my-geocoding-app (luis@example.com)"  # Use your real email
    }
    
    city = requests.get("https://nominatim.openstreetmap.org/reverse?lat=32.3792&lon=-86.3077&format=json", headers=headers)
    
    
    output = city.json()
    print(output)
    
    #"http://api.geonames.org/findNearbyPlaceNameJSON?lat=32.3792&lng=-86.3077&username=luisjrubio"
    
    #https://nominatim.openstreetmap.org/reverse?lat=32.3792&lon=-86.3077&format=json
    
    address = output.get("address", {})
    name = address.get("city") or address.get("town") or address.get("village") or address.get("state") or address.get("suburb") or address.get("county")

    
    # ─────────────────────────────────────────────────────────
    # Fetch data from the Open-Meteo API
    # ─────────────────────────────────────────────────────────
    response = requests.get(url)
    response.raise_for_status()
    weather_data = response.json()

    # ─────────────────────────────────────────────────────────
    # Save raw weather data to a dated JSON file
    # ─────────────────────────────────────────────────────────
    with open(json_filename, "w") as f:
        json.dump(weather_data, f, indent=2)
    print(f"Weather data saved to '{json_filename}'.")

    # ─────────────────────────────────────────────────────────
    # Extract timestamps and temperatures from hourly forecast
    # ─────────────────────────────────────────────────────────
    timestamps = weather_data["hourly"]["time"]
    temperatures = weather_data["hourly"]["temperature_2m"]
    time_objs = [datetime.fromisoformat(t) for t in timestamps]

    # ─────────────────────────────────────────────────────────
    # Create a temperature line plot
    # ─────────────────────────────────────────────────────────
    plt.figure(figsize=(10, 5))
    plt.plot(time_objs, temperatures, label="Temperature (°C)", color="tab:red", linewidth=2)
    plt.title("Hourly Temperature Forecast - Pittsburgh")
    plt.xlabel("Time")
    plt.ylabel("Temperature (°C)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # ─────────────────────────────────────────────────────────
    # Save the plot to a dated PNG file and copy to today.png
    # ─────────────────────────────────────────────────────────
    plt.savefig(plot_filename)
    print(f"Plot saved to '{plot_filename}'.")

    shutil.copy(plot_filename, plot_today_filename)
    print(f"Copied '{plot_filename}' to '{plot_today_filename}'.")

# ─────────────────────────────────────────────────────────────
# Error handling for API or runtime failures
# ─────────────────────────────────────────────────────────────
except requests.RequestException as e:
    print(f"Error fetching data from Open-Meteo API: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
