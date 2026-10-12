"""
Weather Service integrating Open-Meteo telemetry.
Fetches real 30-day historical precipitation and live temperature/humidity.
Replaces synthetic rainfall formulas with empirical meteorological data.
"""
import requests
import datetime
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Popular agricultural locations in India
AGRICULTURAL_HUBS = {
    "Punjab (Ludhiana)": (30.9010, 75.8573),
    "Haryana (Karnal)": (29.6857, 76.9905),
    "Uttar Pradesh (Varanasi)": (25.3176, 82.9739),
    "Tamil Nadu (Coimbatore)": (11.0168, 76.9558),
    "Tamil Nadu (Thanjavur)": (10.7870, 79.1378),
    "Maharashtra (Nashik)": (19.9975, 73.7898),
    "Maharashtra (Pune)": (18.5204, 73.8567),
    "Karnataka (Bengaluru)": (12.9716, 77.5946),
    "Karnataka (Dharwad)": (15.4589, 75.0078),
    "Andhra Pradesh (Guntur)": (16.3067, 80.4365),
    "Madhya Pradesh (Indore)": (22.7196, 75.8577),
    "Gujarat (Anand)": (22.5645, 72.9289),
    "West Bengal (Burdwan)": (23.2324, 87.8615),
    "Kerala (Palakkad)": (10.7867, 76.6548),
    "Rajasthan (Kota)": (25.2138, 75.8648)
}

class WeatherService:
    @staticmethod
    def fetch_weather_and_30d_rainfall(lat: float, lon: float) -> Dict[str, Any]:
        """
        Query Open-Meteo forecast & historical telemetry for:
        - Real 30-day cumulative rainfall (mm)
        - Current temperature (°C)
        - Current relative humidity (%)
        - Mean 30-day temperature (°C)
        """
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": ["temperature_2m", "relative_humidity_2m", "precipitation"],
            "daily": ["precipitation_sum", "temperature_2m_mean"],
            "past_days": 30,
            "forecast_days": 1,
            "timezone": "auto"
        }
        
        try:
            resp = requests.get(url, params=params, timeout=7)
            if resp.status_code == 200:
                data = resp.json()
                current = data.get("current", {})
                daily = data.get("daily", {})
                
                precip_list = daily.get("precipitation_sum", [])
                # Take past 30 days of real precipitation
                past_30d_precip = precip_list[:30] if len(precip_list) >= 30 else precip_list
                real_30d_rainfall_mm = round(float(sum(p for p in past_30d_precip if p is not None)), 1)
                
                temp_means = daily.get("temperature_2m_mean", [])
                avg_30d_temp = round(float(sum(t for t in temp_means if t is not None) / max(1, len(temp_means))), 1) if temp_means else 26.0

                current_temp = float(current.get("temperature_2m", avg_30d_temp))
                current_humid = float(current.get("relative_humidity_2m", 68.0))

                return {
                    "success": True,
                    "rainfall_30d_mm": real_30d_rainfall_mm,
                    "temperature": current_temp,
                    "humidity": current_humid,
                    "avg_30d_temp": avg_30d_temp,
                    "source": "Open-Meteo Real Telemetry",
                    "lat": lat,
                    "lon": lon
                }
        except Exception as e:
            logger.warning(f"Open-Meteo API connection failed: {e}. Using seasonal fallback.")

        # Fallback values if device is offline or API unreachable
        return {
            "success": False,
            "rainfall_30d_mm": 110.0,
            "temperature": 25.5,
            "humidity": 70.0,
            "avg_30d_temp": 25.0,
            "source": "Agro-Climatic Baseline (Offline Fallback)",
            "lat": lat,
            "lon": lon
        }

    @staticmethod
    def get_preset_locations() -> Dict[str, tuple]:
        return AGRICULTURAL_HUBS
