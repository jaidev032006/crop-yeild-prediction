"""
Synthetic Fallback Dataset Generator.
Refactored from original dataset.py to cover all 22 Kaggle crop profiles.
Used only if the local CSV is missing and remote download is unreachable.
"""
import pandas as pd
import numpy as np

CROP_PROFILES = {
    'rice': {'N': (60, 100), 'P': (35, 60), 'K': (35, 45), 'temp': (20, 27), 'humid': (80, 85), 'ph': (5.0, 7.8), 'rain': (180, 300)},
    'maize': {'N': (60, 100), 'P': (35, 60), 'K': (15, 25), 'temp': (18, 27), 'humid': (55, 75), 'ph': (5.5, 7.0), 'rain': (60, 110)},
    'chickpea': {'N': (20, 60), 'P': (55, 80), 'K': (75, 85), 'temp': (17, 21), 'humid': (14, 20), 'ph': (6.0, 8.8), 'rain': (65, 95)},
    'kidneybeans': {'N': (0, 40), 'P': (55, 80), 'K': (15, 25), 'temp': (15, 25), 'humid': (18, 25), 'ph': (5.5, 6.0), 'rain': (60, 150)},
    'pigeonpeas': {'N': (0, 40), 'P': (55, 80), 'K': (15, 25), 'temp': (18, 37), 'humid': (30, 70), 'ph': (4.5, 7.5), 'rain': (90, 200)},
    'mothbeans': {'N': (0, 40), 'P': (35, 60), 'K': (15, 25), 'temp': (24, 32), 'humid': (40, 65), 'ph': (3.5, 9.9), 'rain': (30, 75)},
    'mungbean': {'N': (0, 40), 'P': (35, 60), 'K': (15, 25), 'temp': (27, 30), 'humid': (80, 90), 'ph': (6.2, 7.2), 'rain': (36, 60)},
    'blackgram': {'N': (20, 60), 'P': (55, 80), 'K': (15, 25), 'temp': (25, 35), 'humid': (60, 70), 'ph': (6.5, 7.8), 'rain': (60, 75)},
    'lentil': {'N': (10, 40), 'P': (55, 80), 'K': (15, 25), 'temp': (15, 30), 'humid': (60, 70), 'ph': (5.9, 7.8), 'rain': (35, 55)},
    'pomegranate': {'N': (10, 40), 'P': (10, 30), 'K': (35, 45), 'temp': (18, 25), 'humid': (85, 95), 'ph': (5.5, 7.2), 'rain': (100, 115)},
    'banana': {'N': (80, 120), 'P': (70, 95), 'K': (45, 55), 'temp': (25, 30), 'humid': (75, 85), 'ph': (5.5, 6.5), 'rain': (90, 120)},
    'mango': {'N': (10, 40), 'P': (15, 35), 'K': (25, 35), 'temp': (27, 36), 'humid': (45, 55), 'ph': (4.5, 7.0), 'rain': (89, 101)},
    'grapes': {'N': (10, 40), 'P': (120, 145), 'K': (195, 205), 'temp': (8, 42), 'humid': (80, 85), 'ph': (5.5, 6.5), 'rain': (65, 75)},
    'watermelon': {'N': (80, 120), 'P': (5, 30), 'K': (45, 55), 'temp': (24, 27), 'humid': (80, 90), 'ph': (6.0, 7.0), 'rain': (40, 60)},
    'muskmelon': {'N': (80, 120), 'P': (5, 30), 'K': (45, 55), 'temp': (27, 30), 'humid': (90, 95), 'ph': (6.0, 6.8), 'rain': (20, 30)},
    'apple': {'N': (10, 40), 'P': (120, 145), 'K': (195, 205), 'temp': (21, 24), 'humid': (90, 95), 'ph': (5.5, 6.5), 'rain': (100, 125)},
    'orange': {'N': (10, 40), 'P': (5, 30), 'K': (5, 15), 'temp': (10, 35), 'humid': (90, 95), 'ph': (6.0, 8.0), 'rain': (100, 120)},
    'papaya': {'N': (30, 70), 'P': (45, 70), 'K': (45, 55), 'temp': (23, 44), 'humid': (90, 95), 'ph': (6.5, 7.0), 'rain': (40, 250)},
    'coconut': {'N': (10, 40), 'P': (5, 30), 'K': (25, 35), 'temp': (25, 30), 'humid': (90, 99), 'ph': (5.5, 6.5), 'rain': (130, 230)},
    'cotton': {'N': (100, 140), 'P': (35, 60), 'K': (15, 25), 'temp': (22, 26), 'humid': (75, 85), 'ph': (6.0, 8.0), 'rain': (60, 100)},
    'jute': {'N': (60, 100), 'P': (35, 60), 'K': (35, 45), 'temp': (23, 27), 'humid': (70, 90), 'ph': (6.0, 7.5), 'rain': (150, 200)},
    'coffee': {'N': (80, 120), 'P': (15, 40), 'K': (25, 35), 'temp': (23, 28), 'humid': (50, 70), 'ph': (6.0, 7.5), 'rain': (115, 200)}
}

def generate_fallback_dataset(samples_per_crop: int = 100) -> pd.DataFrame:
    """Generate balanced synthetic fallback dataset matching Kaggle distributions."""
    np.random.seed(42)
    rows = []
    for crop, r in CROP_PROFILES.items():
        for _ in range(samples_per_crop):
            rows.append({
                'N': int(np.random.uniform(*r['N'])),
                'P': int(np.random.uniform(*r['P'])),
                'K': int(np.random.uniform(*r['K'])),
                'temperature': round(float(np.random.uniform(*r['temp'])), 2),
                'humidity': round(float(np.random.uniform(*r['humid'])), 2),
                'ph': round(float(np.random.uniform(*r['ph'])), 2),
                'rainfall': round(float(np.random.uniform(*r['rain'])), 2),
                'label': crop
            })
    df = pd.DataFrame(rows)
    return df.sample(frac=1.0, random_state=42).reset_index(drop=True)
