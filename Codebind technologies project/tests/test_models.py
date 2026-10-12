"""
Unit tests for data loader and ML predictor/explainer.
"""
import pytest
from data.loader import load_crop_dataset
from models.predictor import CropPredictor
from models.explainer import CropExplainer

def test_dataset_loader():
    df = load_crop_dataset()
    assert len(df) >= 2000, "Dataset should have at least 2000 rows"
    assert df['label'].nunique() >= 20, "Dataset should have at least 20 unique crops"
    expected_cols = {'N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'label'}
    assert expected_cols.issubset(set(df.columns))

def test_crop_predictor_top_3():
    predictor = CropPredictor()
    assert predictor.is_ready(), "Model and label encoder should be loaded"
    
    sample_input = {
        'N': 90.0, 'P': 42.0, 'K': 43.0,
        'temperature': 20.8, 'humidity': 82.0,
        'ph': 6.5, 'rainfall': 202.9
    }
    top_crops = predictor.predict_top_k(sample_input, k=3)
    assert len(top_crops) == 3, "Should return exactly top 3 candidates"
    assert top_crops[0]['rank'] == 1
    assert top_crops[1]['rank'] == 2
    assert top_crops[2]['rank'] == 3
    assert top_crops[0]['confidence_pct'] >= top_crops[1]['confidence_pct']
    assert top_crops[0]['estimated_yield_q_ha'] > 0
    assert 'expected_profit_ha' in top_crops[0]

def test_crop_explainer():
    predictor = CropPredictor()
    explainer = CropExplainer(predictor)
    
    sample_input = {
        'N': 90.0, 'P': 42.0, 'K': 43.0,
        'temperature': 20.8, 'humidity': 82.0,
        'ph': 6.5, 'rainfall': 202.9
    }
    explanation = explainer.explain_prediction(sample_input, 'rice')
    assert 'explanation_sentence' in explanation
    assert len(explanation['explanation_sentence']) > 15
    assert len(explanation['feature_impacts']) == 7
