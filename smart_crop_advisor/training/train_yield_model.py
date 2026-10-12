"""
Yield Regressor Training Pipeline.
Trains a continuous RandomForestRegressor to estimate realistic crop yields (Quintals/Hectare)
calibrated to ICAR and National Horticulture Board agricultural baselines.
"""
import os
import sys
import logging
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from data.loader import load_crop_dataset, EXPECTED_FEATURES

logger = logging.getLogger(__name__)

MODELS_DIR = os.path.join(PROJECT_ROOT, 'models')
YIELD_MODEL_PATH = os.path.join(MODELS_DIR, 'yield_model.joblib')

# Benchmark average yields in Quintals/Hectare (1 Quintal = 100 kg)
CROP_BASE_YIELDS = {
    'rice': 38.0, 'maize': 32.0, 'chickpea': 14.5, 'kidneybeans': 12.0,
    'pigeonpeas': 13.0, 'mothbeans': 7.5, 'mungbean': 9.0, 'blackgram': 9.5,
    'lentil': 11.0, 'pomegranate': 35.0, 'banana': 180.0, 'mango': 50.0,
    'grapes': 55.0, 'watermelon': 160.0, 'muskmelon': 100.0, 'apple': 65.0,
    'orange': 55.0, 'papaya': 120.0, 'coconut': 70.0, 'cotton': 16.0,
    'jute': 24.0, 'coffee': 12.0
}

def generate_calibrated_yield_targets(df: pd.DataFrame) -> pd.DataFrame:
    """Derive continuous yield response targets based on soil and climate adequacy."""
    np.random.seed(42)
    yield_targets = []
    
    for _, row in df.iterrows():
        crop = str(row['label']).lower()
        base_yield = CROP_BASE_YIELDS.get(crop, 25.0)
        
        # Agronomic suitability modifiers
        ph_factor = 1.0 - 0.12 * abs(row['ph'] - 6.5) / 3.0
        rain_factor = 0.95 + 0.10 * min(1.0, row['rainfall'] / 160.0)
        nutrient_factor = 0.90 + 0.15 * min(1.0, (row['N'] + row['P'] + row['K']) / 200.0)
        noise = np.random.normal(0, 0.04 * base_yield)
        
        simulated_yield = max(2.0, round((base_yield * ph_factor * rain_factor * nutrient_factor) + noise, 2))
        yield_targets.append(simulated_yield)
        
    df_yield = df.copy()
    df_yield['target_yield'] = yield_targets
    return df_yield

def train_yield_regressor():
    """Train and persist the RandomForestRegressor for yield estimation."""
    logger.info("Loading crop dataset for yield regression training...")
    df = load_crop_dataset()
    df_train = generate_calibrated_yield_targets(df)
    
    X = df_train[EXPECTED_FEATURES]
    y = df_train['target_yield']
    
    regressor = RandomForestRegressor(
        n_estimators=120, max_depth=14, random_state=42, n_jobs=-1
    )
    regressor.fit(X, y)
    
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(regressor, YIELD_MODEL_PATH)
    logger.info(f"Successfully trained and saved Yield Regressor to {YIELD_MODEL_PATH}")
    return regressor

if __name__ == '__main__':
    train_yield_regressor()
