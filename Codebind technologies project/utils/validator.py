"""
Input validation and agronomic safety checks.
"""
from typing import Dict, Tuple, List

VALID_RANGES = {
    'N': (0.0, 140.0, 'Nitrogen'),
    'P': (5.0, 145.0, 'Phosphorus'),
    'K': (5.0, 205.0, 'Potassium'),
    'temperature': (5.0, 50.0, 'Temperature'),
    'humidity': (10.0, 100.0, 'Humidity'),
    'ph': (3.5, 9.9, 'Soil pH'),
    'rainfall': (10.0, 350.0, 'Rainfall')
}

def validate_inputs(features: Dict[str, float]) -> Tuple[bool, List[str]]:
    """Check if inputs fall within agronomically viable thresholds."""
    warnings = []
    is_valid = True
    
    for key, (low, high, label) in VALID_RANGES.items():
        val = features.get(key)
        if val is None:
            warnings.append(f"Missing parameter: {label}")
            is_valid = False
        elif val < low or val > high:
            warnings.append(f"{label} ({val}) is outside recommended agronomic monitoring range ({low} - {high}).")
            
    # Specialized soil warnings
    ph = features.get('ph', 7.0)
    if ph < 5.0:
        warnings.append("Soil is strongly acidic (pH < 5.0). Consider agricultural lime (calcium carbonate) treatment.")
    elif ph > 8.5:
        warnings.append("Soil is alkaline / saline (pH > 8.5). Consider gypsum amendment and organic mulch.")

    return is_valid, warnings
