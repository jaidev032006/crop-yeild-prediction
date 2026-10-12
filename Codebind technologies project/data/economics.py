"""
Crop economics and seasonal taxonomy for all 22 crops.
Based on Indian Ministry of Agriculture CACP (Commission for Agricultural Costs & Prices)
and National Horticulture Board benchmarks.
"""
from typing import Dict, Any, List

CROP_ECONOMICS: Dict[str, Dict[str, Any]] = {
    'rice': {
        'display_name': 'Rice (Paddy)',
        'category': 'cereal',
        'is_legume': False,
        'season': 'Kharif',
        'sowing_months': ['June', 'July'],
        'harvest_months': ['October', 'November'],
        'duration_days': 120,
        'cost_of_cultivation_per_ha': 42000,
        'price_per_quintal': 2300,  # MSP Grade A benchmark
        'avg_yield_quintals_per_ha': 38.0
    },
    'maize': {
        'display_name': 'Maize (Corn)',
        'category': 'cereal',
        'is_legume': False,
        'season': 'Kharif',
        'sowing_months': ['June', 'July'],
        'harvest_months': ['September', 'October'],
        'duration_days': 100,
        'cost_of_cultivation_per_ha': 32000,
        'price_per_quintal': 2225,  # MSP benchmark
        'avg_yield_quintals_per_ha': 32.0
    },
    'chickpea': {
        'display_name': 'Chickpea (Gram)',
        'category': 'pulse',
        'is_legume': True,
        'season': 'Rabi',
        'sowing_months': ['October', 'November'],
        'harvest_months': ['February', 'March'],
        'duration_days': 110,
        'cost_of_cultivation_per_ha': 28000,
        'price_per_quintal': 5440,  # MSP benchmark
        'avg_yield_quintals_per_ha': 14.5
    },
    'kidneybeans': {
        'display_name': 'Kidney Beans (Rajma)',
        'category': 'pulse',
        'is_legume': True,
        'season': 'Rabi',
        'sowing_months': ['October', 'November'],
        'harvest_months': ['February', 'March'],
        'duration_days': 120,
        'cost_of_cultivation_per_ha': 34000,
        'price_per_quintal': 7500,
        'avg_yield_quintals_per_ha': 12.0
    },
    'pigeonpeas': {
        'display_name': 'Pigeon Peas (Arhar/Tur)',
        'category': 'pulse',
        'is_legume': True,
        'season': 'Kharif',
        'sowing_months': ['June', 'July'],
        'harvest_months': ['December', 'January'],
        'duration_days': 180,
        'cost_of_cultivation_per_ha': 31000,
        'price_per_quintal': 7000,  # MSP benchmark
        'avg_yield_quintals_per_ha': 13.0
    },
    'mothbeans': {
        'display_name': 'Moth Beans',
        'category': 'pulse',
        'is_legume': True,
        'season': 'Kharif',
        'sowing_months': ['July', 'August'],
        'harvest_months': ['October', 'November'],
        'duration_days': 85,
        'cost_of_cultivation_per_ha': 19000,
        'price_per_quintal': 6200,
        'avg_yield_quintals_per_ha': 7.5
    },
    'mungbean': {
        'display_name': 'Mung Bean (Green Gram)',
        'category': 'pulse',
        'is_legume': True,
        'season': 'Zaid',
        'sowing_months': ['March', 'April'],
        'harvest_months': ['May', 'June'],
        'duration_days': 70,
        'cost_of_cultivation_per_ha': 22000,
        'price_per_quintal': 8558,  # MSP benchmark
        'avg_yield_quintals_per_ha': 9.0
    },
    'blackgram': {
        'display_name': 'Black Gram (Urad)',
        'category': 'pulse',
        'is_legume': True,
        'season': 'Kharif',
        'sowing_months': ['June', 'July'],
        'harvest_months': ['September', 'October'],
        'duration_days': 80,
        'cost_of_cultivation_per_ha': 23000,
        'price_per_quintal': 6950,  # MSP benchmark
        'avg_yield_quintals_per_ha': 9.5
    },
    'lentil': {
        'display_name': 'Lentil (Masoor)',
        'category': 'pulse',
        'is_legume': True,
        'season': 'Rabi',
        'sowing_months': ['October', 'November'],
        'harvest_months': ['March', 'April'],
        'duration_days': 120,
        'cost_of_cultivation_per_ha': 25000,
        'price_per_quintal': 6425,  # MSP benchmark
        'avg_yield_quintals_per_ha': 11.0
    },
    'pomegranate': {
        'display_name': 'Pomegranate',
        'category': 'fruit',
        'is_legume': False,
        'season': 'Perennial',
        'sowing_months': ['July', 'August'],
        'harvest_months': ['November', 'December', 'January'],
        'duration_days': 365,
        'cost_of_cultivation_per_ha': 110000,
        'price_per_quintal': 7800,
        'avg_yield_quintals_per_ha': 35.0
    },
    'banana': {
        'display_name': 'Banana',
        'category': 'fruit',
        'is_legume': False,
        'season': 'Perennial',
        'sowing_months': ['June', 'July'],
        'harvest_months': ['May', 'June', 'July'],
        'duration_days': 330,
        'cost_of_cultivation_per_ha': 125000,
        'price_per_quintal': 1800,
        'avg_yield_quintals_per_ha': 180.0
    },
    'mango': {
        'display_name': 'Mango',
        'category': 'fruit',
        'is_legume': False,
        'season': 'Perennial',
        'sowing_months': ['July', 'August'],
        'harvest_months': ['April', 'May', 'June'],
        'duration_days': 365,
        'cost_of_cultivation_per_ha': 85000,
        'price_per_quintal': 4200,
        'avg_yield_quintals_per_ha': 50.0
    },
    'grapes': {
        'display_name': 'Grapes',
        'category': 'fruit',
        'is_legume': False,
        'season': 'Perennial',
        'sowing_months': ['October', 'November'],
        'harvest_months': ['February', 'March', 'April'],
        'duration_days': 365,
        'cost_of_cultivation_per_ha': 180000,
        'price_per_quintal': 6500,
        'avg_yield_quintals_per_ha': 55.0
    },
    'watermelon': {
        'display_name': 'Watermelon',
        'category': 'fruit',
        'is_legume': False,
        'season': 'Zaid',
        'sowing_months': ['January', 'February'],
        'harvest_months': ['April', 'May'],
        'duration_days': 90,
        'cost_of_cultivation_per_ha': 48000,
        'price_per_quintal': 1100,
        'avg_yield_quintals_per_ha': 160.0
    },
    'muskmelon': {
        'display_name': 'Muskmelon',
        'category': 'fruit',
        'is_legume': False,
        'season': 'Zaid',
        'sowing_months': ['February', 'March'],
        'harvest_months': ['May', 'June'],
        'duration_days': 85,
        'cost_of_cultivation_per_ha': 45000,
        'price_per_quintal': 1600,
        'avg_yield_quintals_per_ha': 100.0
    },
    'apple': {
        'display_name': 'Apple',
        'category': 'fruit',
        'is_legume': False,
        'season': 'Perennial',
        'sowing_months': ['January', 'February'],
        'harvest_months': ['August', 'September', 'October'],
        'duration_days': 365,
        'cost_of_cultivation_per_ha': 140000,
        'price_per_quintal': 6200,
        'avg_yield_quintals_per_ha': 65.0
    },
    'orange': {
        'display_name': 'Orange',
        'category': 'fruit',
        'is_legume': False,
        'season': 'Perennial',
        'sowing_months': ['July', 'August'],
        'harvest_months': ['November', 'December', 'January'],
        'duration_days': 365,
        'cost_of_cultivation_per_ha': 90000,
        'price_per_quintal': 3800,
        'avg_yield_quintals_per_ha': 55.0
    },
    'papaya': {
        'display_name': 'Papaya',
        'category': 'fruit',
        'is_legume': False,
        'season': 'Perennial',
        'sowing_months': ['February', 'March'],
        'harvest_months': ['November', 'December', 'January'],
        'duration_days': 300,
        'cost_of_cultivation_per_ha': 75000,
        'price_per_quintal': 2100,
        'avg_yield_quintals_per_ha': 120.0
    },
    'coconut': {
        'display_name': 'Coconut',
        'category': 'plantation',
        'is_legume': False,
        'season': 'Perennial',
        'sowing_months': ['May', 'June'],
        'harvest_months': ['Year-round'],
        'duration_days': 365,
        'cost_of_cultivation_per_ha': 65000,
        'price_per_quintal': 3200,
        'avg_yield_quintals_per_ha': 70.0
    },
    'cotton': {
        'display_name': 'Cotton',
        'category': 'fiber',
        'is_legume': False,
        'season': 'Kharif',
        'sowing_months': ['April', 'May'],
        'harvest_months': ['October', 'November', 'December'],
        'duration_days': 160,
        'cost_of_cultivation_per_ha': 48000,
        'price_per_quintal': 7020,  # MSP Medium Staple
        'avg_yield_quintals_per_ha': 16.0
    },
    'jute': {
        'display_name': 'Jute',
        'category': 'fiber',
        'is_legume': False,
        'season': 'Kharif',
        'sowing_months': ['March', 'April'],
        'harvest_months': ['July', 'August'],
        'duration_days': 120,
        'cost_of_cultivation_per_ha': 38000,
        'price_per_quintal': 5050,  # MSP benchmark
        'avg_yield_quintals_per_ha': 24.0
    },
    'coffee': {
        'display_name': 'Coffee (Arabica/Robusta)',
        'category': 'plantation',
        'is_legume': False,
        'season': 'Perennial',
        'sowing_months': ['June', 'July'],
        'harvest_months': ['November', 'December', 'January'],
        'duration_days': 365,
        'cost_of_cultivation_per_ha': 95000,
        'price_per_quintal': 19500,
        'avg_yield_quintals_per_ha': 12.0
    }
}

def load_crop_economics() -> Dict[str, Dict[str, Any]]:
    """Return dictionary of all 22 crop economics & season metadata."""
    return CROP_ECONOMICS

def get_crop_profile(crop_name: str) -> Dict[str, Any]:
    """Retrieve profile for crop, case-insensitive."""
    name = crop_name.strip().lower()
    if name in CROP_ECONOMICS:
        return CROP_ECONOMICS[name]
    # Fallback default
    return {
        'display_name': crop_name.title(),
        'category': 'general',
        'is_legume': False,
        'season': 'General',
        'sowing_months': ['June'],
        'harvest_months': ['October'],
        'duration_days': 120,
        'cost_of_cultivation_per_ha': 35000,
        'price_per_quintal': 3000,
        'avg_yield_quintals_per_ha': 25.0
    }
