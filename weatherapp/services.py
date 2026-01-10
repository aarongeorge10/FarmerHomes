import requests
from django.conf import settings

def get_weather(lat, lon):
    try:
        url = "https://api.openweathermap.org/data/3.0/onecall"

        params = {
            "lat": lat,
            "lon": lon,
            "appid": settings.WEATHER_API_KEY,
            "units": "metric",
            "exclude": "minutely,hourly"
        }

        response = requests.get(url, params=params, timeout=15)
        data = response.json()

        return {
            "temperature": data["current"]["temp"],
            "humidity": data["current"]["humidity"],
            "wind_speed": data["current"]["wind_speed"],
            "rain": data["current"].get("rain", {}).get("1h", 0),
            "description": data["current"]["weather"][0]["description"],
            "icon": data["current"]["weather"][0]["icon"],
            "forecast": data.get("daily", [])[:7]
        }

    except Exception as e:
        print("Weather API error:", e)

        # Fallback safe values
        return {
            "temperature": "--",
            "humidity": "--",
            "wind_speed": "--",
            "rain": 0,
            "description": "Weather unavailable",
            "icon": "01d",
            "forecast": []
        }