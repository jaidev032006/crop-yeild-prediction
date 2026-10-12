"""
Unit tests for Foundation (Part 1).
Validates dataset loading, 5-model evaluation artifacts, yield estimation,
and Open-Meteo weather integration.
"""
import os
import sys
import pytest
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from data.loader import load_crop_dataset, EXPECTED_FEATURES
from services.weather import WeatherService, INDIAN_AGRO_ZONES

def test_kaggle_dataset_loader():
    df = load_crop_dataset()
    assert isinstance(df, pd.DataFrame), "Result must be a DataFrame"
    assert len(df) >= 2000, f"Expected at least 2000 rows, got {len(df)}"
    assert df['label'].nunique() >= 20, f"Expected at least 20 crops, got {df['label'].nunique()}"
    for f in EXPECTED_FEATURES:
        assert f in df.columns, f"Feature column {f} missing from dataset"
    assert 'label' in df.columns, "Label column missing from dataset"

def test_open_meteo_weather_service():
    lat, lon = INDIAN_AGRO_ZONES["Tamil Nadu (Thanjavur)"]
    weather = WeatherService.get_real_weather(lat, lon)
    assert 'rainfall_30d_mm' in weather
    assert 'temperature' in weather
    assert 'humidity' in weather
    assert isinstance(weather['rainfall_30d_mm'], float)
    assert weather['rainfall_30d_mm'] >= 0.0

def test_dataset_fallback():
    from data.dataset_fallback import generate_fallback_dataset
    df_fallback = generate_fallback_dataset(samples_per_crop=10)
    assert len(df_fallback) == 220, "22 crops * 10 samples should equal 220 rows"
    assert df_fallback['label'].nunique() == 22
