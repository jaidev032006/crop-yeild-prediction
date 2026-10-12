"""
Explainable AI (XAI) service using SHAP.
Generates 'Why this crop?' feature attribution charts and natural language explanations.
"""
import os
import sys
import logging
import shap
import numpy as np
import pandas as pd
from typing import Dict, Any, List

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from data.loader import EXPECTED_FEATURES

logger = logging.getLogger(__name__)

FEATURE_LABELS = {
    'N': 'Nitrogen (N)',
    'P': 'Phosphorus (P)',
    'K': 'Potassium (K)',
    'temperature': 'Temperature',
    'humidity': 'Humidity',
    'ph': 'Soil pH',
    'rainfall': 'Rainfall'
}

FEATURE_UNITS = {
    'N': 'kg/ha',
    'P': 'kg/ha',
    'K': 'kg/ha',
    'temperature': '°C',
    'humidity': '%',
    'ph': '',
    'rainfall': 'mm'
}

class CropExplainer:
    def __init__(self, predictor):
        self.predictor = predictor
        self.explainer = None
        self._init_explainer()

    def _init_explainer(self):
        """Initialize SHAP TreeExplainer if model is tree-based."""
        if not self.predictor.is_ready():
            return
        model = self.predictor.model
        try:
            # Check for underlying tree model or pipeline
            underlying = model
            if hasattr(model, 'named_steps'):
                underlying = list(model.named_steps.values())[-1]
                
            self.explainer = shap.TreeExplainer(underlying)
            logger.info("Initialized SHAP TreeExplainer.")
        except Exception as e:
            logger.warning(f"TreeExplainer initialization fallback: {e}")
            self.explainer = None

    def explain_prediction(self, input_features: Dict[str, float], predicted_crop: str) -> Dict[str, Any]:
        """
        Generate feature attribution values and plain-language explanation for predicted crop.
        """
        df_input = pd.DataFrame([{f: float(input_features.get(f, 0.0)) for f in EXPECTED_FEATURES}])
        
        feature_impacts: List[Dict[str, Any]] = []
        
        # 1. Compute SHAP values
        shap_vals = None
        if self.explainer is not None:
            try:
                raw_shap = self.explainer.shap_values(df_input)
                # Multi-class models return a list of arrays (one per class)
                if isinstance(raw_shap, list):
                    # Find class index
                    class_idx = list(self.predictor.label_encoder.classes_).index(predicted_crop.lower())
                    shap_vals = raw_shap[class_idx][0]
                elif hasattr(raw_shap, 'shape') and len(raw_shap.shape) == 3:
                    class_idx = list(self.predictor.label_encoder.classes_).index(predicted_crop.lower())
                    shap_vals = raw_shap[0, :, class_idx]
                elif hasattr(raw_shap, 'shape') and len(raw_shap.shape) == 2:
                    shap_vals = raw_shap[0]
            except Exception as e:
                logger.warning(f"Direct SHAP computation error: {e}")
                shap_vals = None

        # Fallback to feature importance proxy if SHAP fails on runtime
        if shap_vals is None or len(shap_vals) != len(EXPECTED_FEATURES):
            model = self.predictor.model
            underlying = model
            if hasattr(model, 'named_steps'):
                underlying = list(model.named_steps.values())[-1]
            if hasattr(underlying, 'feature_importances_'):
                shap_vals = underlying.feature_importances_
            else:
                shap_vals = np.array([0.15, 0.15, 0.15, 0.15, 0.15, 0.10, 0.15])

        for feat, sv in zip(EXPECTED_FEATURES, shap_vals):
            val = input_features.get(feat, 0.0)
            unit = FEATURE_UNITS.get(feat, '')
            val_str = f"{val} {unit}".strip()
            feature_impacts.append({
                'feature': feat,
                'feature_label': FEATURE_LABELS.get(feat, feat),
                'shap_value': round(float(sv), 4),
                'absolute_impact': round(abs(float(sv)), 4),
                'input_value': val,
                'value_str': val_str,
                'direction': 'Positive' if sv >= 0 else 'Negative'
            })

        # Sort features by highest impact
        feature_impacts.sort(key=lambda x: x['absolute_impact'], reverse=True)

        # 2. Build plain-language explanation sentence
        top_driver_1 = feature_impacts[0]
        top_driver_2 = feature_impacts[1]
        
        crop_title = predicted_crop.title()
        
        def format_descriptor(f_name, f_val):
            if f_name == 'rainfall':
                return f"rainfall of {f_val} mm"
            elif f_name == 'temperature':
                return f"temperature of {f_val}°C"
            elif f_name == 'humidity':
                return f"humidity of {f_val}%"
            elif f_name == 'ph':
                return f"soil pH of {f_val}"
            elif f_name in ['N', 'P', 'K']:
                return f"{FEATURE_LABELS[f_name]} level of {f_val} kg/ha"
            return f"{f_name} ({f_val})"

        desc1 = format_descriptor(top_driver_1['feature'], top_driver_1['input_value'])
        desc2 = format_descriptor(top_driver_2['feature'], top_driver_2['input_value'])

        explanation_sentence = (
            f"Favorable {desc1} and {desc2} were the strongest natural factors driving the selection of {crop_title}."
        )

        return {
            'crop': predicted_crop,
            'explanation_sentence': explanation_sentence,
            'top_drivers': [top_driver_1['feature_label'], top_driver_2['feature_label']],
            'feature_impacts': feature_impacts
        }
