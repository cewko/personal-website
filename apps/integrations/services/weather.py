import requests
from datetime import datetime
from .base import BaseIntegrationService


class WeatherService(BaseIntegrationService):
    cache_timeout = 10800

    def __init__(self):
        # Warsaw coordinates
        self.latitude = 52.2297
        self.longitude = 21.0122
        self.api_url = 'https://api.open-meteo.com/v1/forecast'

    def get_cache_key(self):
        return "integration:weather:warsaw"

    def fetch_data(self):
        try:
            params = {
                'latitude': self.latitude,
                'longitude': self.longitude,
                'current': 'temperature_2m,relative_humidity_2m,weather_code',
                'timezone': 'Europe/Warsaw'
            }

            response = requests.get(self.api_url, params=params, timeout=5)
            response.raise_for_status()

            data = response.json()
            current = data.get("current", {})

            time_str = current['time']
            dt = datetime.fromisoformat(time_str)
            formatted_time = dt.strftime('%b. %-d, %-H:%M')

            return {
                "time": formatted_time,
                "temperature": round(current.get("temperature_2m", 0)),
                "humidity": current.get("relative_humidity_2m", 0),
                "description": self._get_weather_description(current.get("weather_code")),
            }

        except requests.RequestException:
            return None
        except Exception:
            return None

    @staticmethod
    def _get_weather_description(code):
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Foggy",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with hail",
            99: "Thunderstorm with hail",
        }
        return weather_codes.get(code, "Description not provided")
