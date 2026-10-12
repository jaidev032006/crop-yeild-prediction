"""
Unit tests for fertilizer calculations and crop rotation planner.
"""
import pytest
from services.fertilizer import FertilizerService
from services.rotation import RotationPlanner
from services.disease_alert import DiseaseAlertService

def test_fertilizer_deficit_calculation():
    # Deficit test: low N, low P, low K for Rice
    current_npk = {'N': 20.0, 'P': 10.0, 'K': 10.0}
    plan = FertilizerService.calculate_fertilizer_plan(current_npk, 'rice')
    
    com = plan['commercial_fertilizers_kg_acre']
    assert com['urea'] > 0, "Urea should be prescribed when soil N is deficient"
    assert com['ssp'] > 0, "SSP should be prescribed when soil P is deficient"
    assert com['mop'] > 0, "MOP should be prescribed when soil K is deficient"
    assert len(plan['split_schedule']) == 3, "Split schedule must contain 3 growth phases"
    assert len(plan['organic_alternatives']) >= 3, "Organic alternatives should provide multiple options"

def test_rotation_planner_cereal_to_legume():
    # Rotating after Rice (cereal) should suggest legumes
    rot = RotationPlanner.get_rotation_plan('rice')
    assert rot['next_season'] == 'Rabi', "Kharif rice should rotate to Rabi"
    assert len(rot['recommended_next_crops']) >= 1
    # Check that recommended crops include legumes
    has_legume = any(c.get('is_legume') for c in rot['recommended_next_crops'])
    assert has_legume, "Cereal rotation must include leguminous restorers"

def test_disease_alerts():
    # Warm humid conditions for Rice should trigger blast alert
    alerts = DiseaseAlertService.get_alerts('rice', temperature=24.0, humidity=85.0)
    assert len(alerts) >= 1
    high_risks = [a for a in alerts if a['risk_level'] == 'High Risk']
    assert len(high_risks) >= 1, "Warm humid rice should trigger high risk fungal alerts"
