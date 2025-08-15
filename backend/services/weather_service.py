"""
Weather service for getting weather information
خدمة الطقس للحصول على معلومات الطقس
"""

import requests
from typing import Dict, Any, Optional
from ..config import settings  # استيراد نسبي لضمان العمل من الجذر


class WeatherService:
    """Service for weather-related operations"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'weather_api_key', None)
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    def get_weather(self, city: str, country_code: str = "SA") -> Dict[str, Any]:
        """
        Get current weather for a city
        الحصول على الطقس الحالي لمدينة
        """
        try:
            if not self.api_key:
                return self._get_mock_weather(city)
            
            url = f"{self.base_url}/weather"
            params = {
                "q": f"{city},{country_code}",
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "city": data.get("name", city),
                "country": data.get("sys", {}).get("country", country_code),
                "temperature": data.get("main", {}).get("temp", 0),
                "feels_like": data.get("main", {}).get("feels_like", 0),
                "humidity": data.get("main", {}).get("humidity", 0),
                "description": data.get("weather", [{}])[0].get("description", ""),
                "icon": data.get("weather", [{}])[0].get("icon", ""),
                "wind_speed": data.get("wind", {}).get("speed", 0),
                "pressure": data.get("main", {}).get("pressure", 0),
                "timestamp": data.get("dt", 0)
            }
            
        except Exception as e:
            print(f"Error getting weather: {e}")
            return self._get_mock_weather(city)
    
    def get_forecast(self, city: str, country_code: str = "SA") -> Dict[str, Any]:
        """
        Get weather forecast for a city
        الحصول على توقعات الطقس لمدينة
        """
        try:
            if not self.api_key:
                return self._get_mock_forecast(city)
            
            url = f"{self.base_url}/forecast"
            params = {
                "q": f"{city},{country_code}",
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Process forecast data
            forecast_list = []
            for item in data.get("list", [])[:8]:  # Next 24 hours (3-hour intervals)
                forecast_list.append({
                    "time": item.get("dt", 0),
                    "temperature": item.get("main", {}).get("temp", 0),
                    "description": item.get("weather", [{}])[0].get("description", ""),
                    "icon": item.get("weather", [{}])[0].get("icon", ""),
                    "humidity": item.get("main", {}).get("humidity", 0),
                    "wind_speed": item.get("wind", {}).get("speed", 0)
                })
            
            return {
                "city": data.get("city", {}).get("name", city),
                "country": data.get("city", {}).get("country", country_code),
                "forecast": forecast_list
            }
            
        except Exception as e:
            print(f"Error getting forecast: {e}")
            return self._get_mock_forecast(city)
    
    def _get_mock_weather(self, city: str) -> Dict[str, Any]:
        """Get mock weather data for testing"""
        return {
            "city": city,
            "country": "SA",
            "temperature": 25.0,
            "feels_like": 27.0,
            "humidity": 60,
            "description": "clear sky",
            "icon": "01d",
            "wind_speed": 5.2,
            "pressure": 1013,
            "timestamp": 1640995200
        }
    
    def _get_mock_forecast(self, city: str) -> Dict[str, Any]:
        """Get mock forecast data for testing"""
        return {
            "city": city,
            "country": "SA",
            "forecast": [
                {
                    "time": 1640995200,
                    "temperature": 25.0,
                    "description": "clear sky",
                    "icon": "01d",
                    "humidity": 60,
                    "wind_speed": 5.2
                },
                {
                    "time": 1641006000,
                    "temperature": 23.0,
                    "description": "few clouds",
                    "icon": "02d",
                    "humidity": 65,
                    "wind_speed": 4.8
                }
            ]
        } 