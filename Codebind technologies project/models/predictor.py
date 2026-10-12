"""
Crop Predictor Service.
Loads the trained best model and generates Top-K recommendations
with confidence scores via predict_proba().
"""
import os
import sys
import logging
import joblib
import numpy as np
import pandas as pd
from typing import List, Dict, Any

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from data.loader import EXPECTED_FEATURES
from data.economics import get_crop_profile
from models.yield_model import YieldEstimator

logger = logging.getLogger(__name__)

SAVED_MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saved_models')
MODEL_PATH = os.path.join(SAVED_MODELS_DIR, 'best_crop_model.joblib')
LABEL_ENCODER_PATH = os.path.join(SAVED_MODELS_DIR, 'label_encoder.joblib')

class CropPredictor:
    def __init__(self, model_path: str = MODEL_PATH, encoder_path: str = LABEL_ENCODER_PATH):
        self.model_path = model_path
        self.encoder_path = encoder_path
        self.model = None
        self.label_encoder = None
        self.yield_estimator = YieldEstimator()
        self.load_artifacts()

    def load_artifacts(self) -> bool:
        """Load trained model and label encoder from disk."""
        if os.path.exists(self.model_path) and os.path.exists(self.encoder_path):
            try:
                self.model = joblib.load(self.model_path)
                self.label_encoder = joblib.load(self.encoder_path)
                logger.info("Successfully loaded crop prediction model and label encoder.")
                return True
            except Exception as e:
                logger.error(f"Error loading model artifacts: {e}")
        return False

    def is_ready(self) -> bool:
        return self.model is not None and self.label_encoder is not None

    def predict_top_k(self, input_features: Dict[str, float], k: int = 3) -> List[Dict[str, Any]]:
        """
        Generate top-K recommended crops ranked by probability.
        Input features: {'N': ..., 'P': ..., 'K': ..., 'temperature': ..., 'humidity': ..., 'ph': ..., 'rainfall': ...}
        """
        if not self.is_ready():
            raise RuntimeError("Model artifacts are not loaded. Train the models first.")

        # Build feature dataframe
        input_data = {}
        for feat in EXPECTED_FEATURES:
            input_data[feat] = [float(input_features.get(feat, 0.0))]
        df_input = pd.DataFrame(input_data)

        # Get class probabilities
        if hasattr(self.model, "predict_proba"):
            probabilities = self.model.predict_proba(df_input)[0]
        else:
            # Fallback for models without native probabilities
            pred_idx = self.model.predict(df_input)[0]
            probabilities = np.zeros(len(self.label_encoder.classes_))
            probabilities[pred_idx] = 1.0

        top_indices = np.argsort(probabilities)[::-1][:k]
        
        results = []
        for rank, idx in enumerate(top_indices, start=1):
            crop_label = self.label_encoder.classes_[idx]
            confidence_pct = round(float(probabilities[idx]) * 100, 2)
            profile = get_crop_profile(crop_label)
            
            # Estimate yield for this candidate
            yield_info = self.yield_estimator.estimate_yield(crop_label, input_features)
            
            # Economics calculation (Cost, Revenue, Profit per Hectare)
            yield_q_ha = yield_info['estimated_yield_q_ha']
            price_per_q = profile['price_per_quintal']
            cost_ha = profile['cost_of_cultivation_per_ha']
            revenue_ha = int(yield_q_ha * price_per_q)
            profit_ha = revenue_ha - cost_ha
            
            results.append({
                'rank': rank,
                'crop': crop_label,
                'display_name': profile['display_name'],
                'confidence_pct': confidence_pct,
                'category': profile['category'],
                'season': profile['season'],
                'is_legume': profile['is_legume'],
                'sowing_months': profile['sowing_months'],
                'harvest_months': profile['harvest_months'],
                'duration_days': profile['duration_days'],
                'estimated_yield_q_ha': yield_q_ha,
                'estimated_yield_tonnes_ha': yield_info['estimated_yield_tonnes_ha'],
                'cost_per_ha': cost_ha,
                'price_per_quintal': price_per_q,
                'expected_revenue_ha': revenue_ha,
                'expected_profit_ha': profit_ha
            })
            
        return results
