"""
Location Intelligence & Crop Recommendation Service.
Integrates the 730+ location dataset and models from the archive
into the unified AgriSmart platform.
"""
import os
import re
import json
import logging
import joblib
import numpy as np
import pandas as pd
import requests

logger = logging.getLogger(__name__)

# Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
ARCHIVE_CSV = os.path.join(BASE_DIR, 'archive', 'CropDataset-Enhanced.csv')
ARCHIVE_MODELS_DIR = os.path.join(BASE_DIR, 'archive', 'Crop Recommender (1)', 'Crop Recommender', 'models')


def parse_percentage(val):
    """Safely parse percentage string '96.42%' to float 96.42"""
    if pd.isna(val) or val is None:
        return 0.0
    val_str = str(val).strip().replace('%', '')
    try:
        return float(val_str)
    except ValueError:
        return 0.0


class LocationCropService:
    _instance = None
    _df = None
    _states_map = None
    _soil_models = None
    _soil_encoders = None
    _soil_scaler = None
    _crop_model = None
    _crop_scaler = None
    _mlb = None
    _models_loaded = False

    @classmethod
    def initialize(cls):
        """Loads and pre-processes the 730+ location dataset and pre-trained models."""
        if cls._df is not None:
            return

        try:
            if not os.path.exists(ARCHIVE_CSV):
                logger.error(f"Archive CSV not found at {ARCHIVE_CSV}")
                return

            df = pd.read_csv(ARCHIVE_CSV)
            # Clean column names
            df.columns = [c.strip() for c in df.columns]

            # Parse numeric lat/lon
            df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
            df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')

            # Clean address & region
            df['Address'] = df['Address'].fillna('').astype(str).str.strip()
            df['Region'] = df['Region'].fillna('General India').astype(str).str.strip()
            df['Formatted address'] = df['Formatted address'].fillna(df['Address']).astype(str).str.strip()
            df['Crop'] = df['Crop'].fillna('').astype(str).str.strip()

            # Parse percentages for soil nutrients
            perc_cols = [
                'Nitrogen - High', 'Nitrogen - Medium', 'Nitrogen - Low',
                'Phosphorous - High', 'Phosphorous - Medium', 'Phosphorous - Low',
                'Potassium - High', 'Potassium - Medium', 'Potassium - Low',
                'pH - Acidic', 'pH - Neutral', 'pH - Alkaline'
            ]
            for col in perc_cols:
                if col in df.columns:
                    df[col] = df[col].apply(parse_percentage)
                else:
                    df[col] = 0.0

            cls._df = df

            # Build states and locations hierarchy
            states_map = {}
            for _, row in df.iterrows():
                state = row['Region']
                addr = row['Address']
                if not addr or 'Urban area' in row['Crop']:
                    continue
                if state not in states_map:
                    states_map[state] = []
                states_map[state].append({
                    'id': int(row.name),
                    'address': addr,
                    'formatted': row['Formatted address'],
                    'lat': float(row['Latitude']) if not pd.isna(row['Latitude']) else 0.0,
                    'lon': float(row['Longitude']) if not pd.isna(row['Longitude']) else 0.0,
                    'crops': [c.strip() for c in row['Crop'].split(',') if c.strip()]
                })

            # Sort states and locations
            sorted_states = {}
            for state in sorted(states_map.keys()):
                sorted_states[state] = sorted(states_map[state], key=lambda x: x['address'].lower())
            cls._states_map = sorted_states
            logger.info(f"Loaded {len(df)} locations across {len(sorted_states)} regions.")

        except Exception as e:
            logger.error(f"Error loading location dataset: {e}", exc_info=True)

        # Attempt to load ML models from archive
        cls._load_archive_models()

    @classmethod
    def _load_archive_models(cls):
        """Loads archive pre-trained soil and crop models if available."""
        if cls._models_loaded:
            return

        try:
            if not os.path.exists(ARCHIVE_MODELS_DIR):
                logger.warning(f"Archive models directory not found at {ARCHIVE_MODELS_DIR}")
                return

            soil_m_path = os.path.join(ARCHIVE_MODELS_DIR, 'soil_prediction_models.pkl')
            soil_enc_path = os.path.join(ARCHIVE_MODELS_DIR, 'soil_level_encoders.pkl')
            soil_sc_path = os.path.join(ARCHIVE_MODELS_DIR, 'soil_feature_scaler.pkl')

            crop_m_path = os.path.join(ARCHIVE_MODELS_DIR, 'crop_recommender_model.pkl')
            crop_sc_path = os.path.join(ARCHIVE_MODELS_DIR, 'crop_feature_scaler.pkl')
            crop_mlb_path = os.path.join(ARCHIVE_MODELS_DIR, 'crop_multilabel_binarizer.pkl')

            if os.path.exists(soil_m_path):
                cls._soil_models = joblib.load(soil_m_path)
                cls._soil_encoders = joblib.load(soil_enc_path)
                cls._soil_scaler = joblib.load(soil_sc_path)

            if os.path.exists(crop_m_path):
                cls._crop_model = joblib.load(crop_m_path)
                cls._crop_scaler = joblib.load(crop_sc_path)
                cls._mlb = joblib.load(crop_mlb_path)

            cls._models_loaded = True
            logger.info("Archive soil and crop recommender models loaded.")
        except Exception as e:
            logger.warning(f"Could not load archive ML models (fallback to dataset indexing): {e}")

    @classmethod
    def get_states(cls):
        """Returns sorted list of all available states / regions."""
        cls.initialize()
        if not cls._states_map:
            return []
        return list(cls._states_map.keys())

    @classmethod
    def get_locations(cls, state=None, search=None):
        """Returns locations filtered by state or search term."""
        cls.initialize()
        if cls._df is None:
            return []

        if state and state in cls._states_map:
            locations = cls._states_map[state]
            if search:
                s_lower = search.lower().strip()
                return [loc for loc in locations if s_lower in loc['address'].lower() or s_lower in loc['formatted'].lower()]
            return locations

        # Search across all locations
        results = []
        s_lower = search.lower().strip() if search else ''
        for state_name, loc_list in cls._states_map.items():
            for loc in loc_list:
                if not s_lower or s_lower in loc['address'].lower() or s_lower in loc['formatted'].lower() or s_lower in state_name.lower():
                    results.append({
                        **loc,
                        'state': state_name
                    })
        return results[:100]

    @classmethod
    def get_location_profile(cls, location_id=None, address_name=None):
        """
        Retrieves full agronomic profile:
        - Lat, Lon, Region
        - Soil N, P, K, pH percentages
        - Derived estimated numeric values (mg/kg) for soil sliders
        - Historical / verified traditional crops
        """
        cls.initialize()
        if cls._df is None:
            return None

        row = None
        if location_id is not None:
            try:
                row = cls._df.loc[int(location_id)]
            except Exception:
                pass

        if row is None and address_name:
            addr_clean = address_name.strip().lower()
            matches = cls._df[cls._df['Address'].str.lower().str.contains(addr_clean, regex=False)]
            if not matches.empty:
                row = matches.iloc[0]
            else:
                matches_fmt = cls._df[cls._df['Formatted address'].str.lower().str.contains(addr_clean, regex=False)]
                if not matches_fmt.empty:
                    row = matches_fmt.iloc[0]

        if row is None:
            return None

        # Calculate estimated NPK and pH numeric values from distributions
        n_high = float(row.get('Nitrogen - High', 0.0)) / 100.0
        n_med = float(row.get('Nitrogen - Medium', 0.0)) / 100.0
        n_low = float(row.get('Nitrogen - Low', 0.0)) / 100.0
        # Typical levels: High ~ 125 mg/kg, Med ~ 80 mg/kg, Low ~ 38 mg/kg
        est_n = round(n_high * 125.0 + n_med * 80.0 + n_low * 38.0, 1)
        if est_n < 20: est_n = 45.0

        p_high = float(row.get('Phosphorous - High', 0.0)) / 100.0
        p_med = float(row.get('Phosphorous - Medium', 0.0)) / 100.0
        p_low = float(row.get('Phosphorous - Low', 0.0)) / 100.0
        # Typical levels: High ~ 75 mg/kg, Med ~ 42 mg/kg, Low ~ 18 mg/kg
        est_p = round(p_high * 75.0 + p_med * 42.0 + p_low * 18.0, 1)
        if est_p < 15: est_p = 35.0

        k_high = float(row.get('Potassium - High', 0.0)) / 100.0
        k_med = float(row.get('Potassium - Medium', 0.0)) / 100.0
        k_low = float(row.get('Potassium - Low', 0.0)) / 100.0
        # Typical levels: High ~ 240 mg/kg, Med ~ 140 mg/kg, Low ~ 55 mg/kg
        est_k = round(k_high * 240.0 + k_med * 140.0 + k_low * 55.0, 1)
        if est_k < 20: est_k = 42.0

        ph_acid = float(row.get('pH - Acidic', 0.0)) / 100.0
        ph_neut = float(row.get('pH - Neutral', 0.0)) / 100.0
        ph_alk = float(row.get('pH - Alkaline', 0.0)) / 100.0
        # Acidic ~ 5.6, Neutral ~ 6.8, Alkaline ~ 8.2
        est_ph = round(ph_acid * 5.6 + ph_neut * 6.8 + ph_alk * 8.2, 1)
        if est_ph < 4.0 or est_ph > 9.5: est_ph = 6.6

        # Dominant levels
        def get_dominant(h, m, l, high_lbl="High", med_lbl="Medium", low_lbl="Low"):
            if h >= m and h >= l: return high_lbl
            if m >= h and m >= l: return med_lbl
            return low_lbl

        crops_raw = str(row.get('Crop', ''))
        crops_list = [c.strip() for c in crops_raw.split(',') if c.strip() and 'Urban' not in c]

        return {
            'id': int(row.name),
            'address': str(row.get('Address', '')),
            'formatted_address': str(row.get('Formatted address', '')),
            'region': str(row.get('Region', '')),
            'country': str(row.get('Country', 'India')),
            'latitude': float(row.get('Latitude', 0.0)),
            'longitude': float(row.get('Longitude', 0.0)),
            'traditional_crops': crops_list,
            'soil_distributions': {
                'nitrogen': {
                    'high': round(float(row.get('Nitrogen - High', 0.0)), 1),
                    'medium': round(float(row.get('Nitrogen - Medium', 0.0)), 1),
                    'low': round(float(row.get('Nitrogen - Low', 0.0)), 1),
                    'dominant': get_dominant(n_high, n_med, n_low)
                },
                'phosphorus': {
                    'high': round(float(row.get('Phosphorous - High', 0.0)), 1),
                    'medium': round(float(row.get('Phosphorous - Medium', 0.0)), 1),
                    'low': round(float(row.get('Phosphorous - Low', 0.0)), 1),
                    'dominant': get_dominant(p_high, p_med, p_low)
                },
                'potassium': {
                    'high': round(float(row.get('Potassium - High', 0.0)), 1),
                    'medium': round(float(row.get('Potassium - Medium', 0.0)), 1),
                    'low': round(float(row.get('Potassium - Low', 0.0)), 1),
                    'dominant': get_dominant(k_high, k_med, k_low)
                },
                'ph': {
                    'acidic': round(float(row.get('pH - Acidic', 0.0)), 1),
                    'neutral': round(float(row.get('pH - Neutral', 0.0)), 1),
                    'alkaline': round(float(row.get('pH - Alkaline', 0.0)), 1),
                    'dominant': get_dominant(ph_acid, ph_neut, ph_alk, "Acidic", "Neutral", "Alkaline")
                }
            },
            'estimated_inputs': {
                'n': est_n,
                'p': est_p,
                'k': est_k,
                'ph': est_ph
            }
        }

    @classmethod
    def fetch_live_weather(cls, lat, lon):
        """Fetches live meteorological parameters from Open-Meteo for exact coordinates."""
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation&daily=precipitation_sum&timezone=auto"
            res = requests.get(url, timeout=5).json()
            curr = res.get('current', {})
            temp = float(curr.get('temperature_2m', 25.0))
            humid = float(curr.get('relative_humidity_2m', 70.0))
            daily_precip = curr.get('precipitation', 0.0)
            
            daily_sum = res.get('daily', {}).get('precipitation_sum', [0.0])
            avg_daily = sum(daily_sum) / max(len(daily_sum), 1) if daily_sum else daily_precip
            monthly_rain = round(avg_daily * 30 + 40, 1)
            if monthly_rain < 30: monthly_rain = 65.0
            if monthly_rain > 350: monthly_rain = 320.0

            return {
                'temperature': round(temp, 1),
                'humidity': round(humid, 1),
                'rainfall': round(monthly_rain, 1),
                'source': 'Open-Meteo Satellite Telemetry'
            }
        except Exception as e:
            logger.warning(f"Failed to fetch live weather for ({lat}, {lon}): {e}")
            return {
                'temperature': 25.5,
                'humidity': 72.0,
                'rainfall': 140.0,
                'source': 'Regional Seasonal Average (Fallback)'
            }

    @classmethod
    def recommend_for_location(cls, location_id=None, address_name=None):
        """
        End-to-End Location Analysis:
        1. Look up location profile (730+ Indian districts)
        2. Fetch real-time weather for that GPS coordinate
        3. Derive soil characteristics
        4. Predict top suitable crops with confidence scores
        """
        profile = cls.get_location_profile(location_id=location_id, address_name=address_name)
        if not profile:
            return None

        # Fetch live weather for coordinates
        weather = cls.fetch_live_weather(profile['latitude'], profile['longitude'])

        # Blend inputs
        inputs = {
            'n': profile['estimated_inputs']['n'],
            'p': profile['estimated_inputs']['p'],
            'k': profile['estimated_inputs']['k'],
            'temp': weather['temperature'],
            'humid': weather['humidity'],
            'ph': profile['estimated_inputs']['ph'],
            'rain': weather['rainfall']
        }

        # Check multi-label model recommendation if loaded
        multi_label_crops = []
        if cls._models_loaded and cls._crop_model is not None and cls._crop_scaler is not None:
            try:
                loc_input = np.array([[profile['latitude'], profile['longitude']]])
                scaled_loc = cls._crop_scaler.transform(loc_input)
                
                # Distribution vectors
                sd = profile['soil_distributions']
                n_dist = [sd['nitrogen']['high']/100.0, sd['nitrogen']['medium']/100.0, sd['nitrogen']['low']/100.0]
                p_dist = [sd['phosphorus']['high']/100.0, sd['phosphorus']['medium']/100.0, sd['phosphorus']['low']/100.0]
                k_dist = [sd['potassium']['high']/100.0, sd['potassium']['medium']/100.0, sd['potassium']['low']/100.0]
                ph_dist = [sd['ph']['acidic']/100.0, sd['ph']['neutral']/100.0, sd['ph']['alkaline']/100.0]
                
                feats = list(scaled_loc[0]) + n_dist + p_dist + k_dist + ph_dist
                x_pred = np.array(feats).reshape(1, -1)
                
                probs = cls._crop_model.predict_proba(x_pred)
                crop_classes = cls._mlb.classes_
                
                ranked = []
                for i, prob_arr in enumerate(probs):
                    if len(prob_arr[0]) > 1:
                        p_val = prob_arr[0][1]
                        if p_val > 0.05:
                            ranked.append({'crop': str(crop_classes[i]), 'score': round(float(p_val) * 100, 1)})
                
                ranked.sort(key=lambda x: x['score'], reverse=True)
                multi_label_crops = ranked[:5]
            except Exception as ex:
                logger.warning(f"Error in multi-label crop prediction: {ex}")

        return {
            'location': profile,
            'weather': weather,
            'inputs': inputs,
            'archive_model_crops': multi_label_crops
        }
