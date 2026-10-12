"""
Weather & Meteorological Telemetry Service.
Integrates the Open-Meteo API to fetch:
1. Real 30-day cumulative precipitation (mm) from historical/archive telemetry.
2. Real-time temperature (°C) and relative humidity (%).
3. Comprehensive regional Indian agricultural hubs dictionary.
"""
import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Representative agricultural district coordinates
INDIAN_AGRO_ZONES = {
    "Punjab (Ludhiana)": (30.9010, 75.8573),
    "Haryana (Karnal)": (29.6857, 76.9905),
    "Uttar Pradesh (Varanasi)": (25.3176, 82.9739),
    "Tamil Nadu (Thanjavur)": (10.7870, 79.1378),
    "Tamil Nadu (Coimbatore)": (11.0168, 76.9558),
    "Maharashtra (Nashik)": (19.9975, 73.7898),
    "Maharashtra (Pune)": (18.5204, 73.8567),
    "Karnataka (Dharwad)": (15.4589, 75.0078),
    "Karnataka (Bengaluru)": (12.9716, 77.5946),
    "Andhra Pradesh (Guntur)": (16.3067, 80.4365),
    "Madhya Pradesh (Indore)": (22.7196, 75.8577),
    "Gujarat (Anand)": (22.5645, 72.9289),
    "West Bengal (Burdwan)": (23.2324, 87.8615),
    "Kerala (Palakkad)": (10.7867, 76.6548),
    "Rajasthan (Kota)": (25.2138, 75.8648)
}

class WeatherService:
    @staticmethod
    def get_real_weather(lat: float, lon: float) -> Dict[str, Any]:
        """
        Query Open-Meteo telemetry endpoint.
        Calculates real 30-day cumulative precipitation by summing daily rainfall over the past 30 days.
        """
        endpoint = "https://api.open-meteo.com/v1/forecast"
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
            resp = requests.get(endpoint, params=params, timeout=8)
            if resp.status_code == 200:
                payload = resp.json()
                current = payload.get("current", {})
                daily = payload.get("daily", {})
                
                # Extract past 30 days of empirical precipitation
                precip_records = daily.get("precipitation_sum", [])
                past_30d_precip = precip_records[:30] if len(precip_records) >= 30 else precip_records
                real_rainfall_30d = round(float(sum(p for p in past_30d_precip if p is not None)), 1)
                
                temp_means = daily.get("temperature_2m_mean", [])
                avg_30d_temp = round(float(sum(t for t in temp_means if t is not None) / max(1, len(temp_means))), 1) if temp_means else 25.5
                
                current_temp = float(current.get("temperature_2m", avg_30d_temp))
                current_humidity = float(current.get("relative_humidity_2m", 68.0))

                return {
                    "success": True,
                    "rainfall_30d_mm": real_rainfall_30d,
                    "temperature": current_temp,
                    "humidity": current_humidity,
                    "avg_30d_temp": avg_30d_temp,
                    "source": "Open-Meteo Real Empirical Telemetry",
                    "lat": lat,
                    "lon": lon
                }
        except Exception as e:
            logger.warning(f"Live Open-Meteo API query encountered an error: {e}. Falling back to regional baseline.")

        # Robust offline fallback
        return {
            "success": False,
            "rainfall_30d_mm": 115.0,
            "temperature": 26.0,
            "humidity": 70.0,
            "avg_30d_temp": 25.5,
            "source": "Agro-Climatic Baseline (Offline Fallback)",
            "lat": lat,
            "lon": lon
        }

    @staticmethod
    def get_regional_zones() -> Dict[str, tuple]:
        return INDIAN_AGRO_ZONES
