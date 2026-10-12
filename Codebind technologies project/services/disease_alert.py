"""
Dynamic Disease & Pest Early-Warning Service.
Correlates micro-climatic telemetry (temperature and relative humidity)
with crop-specific pathogen profiles to trigger actionable preventive alerts.
"""
from typing import Dict, Any, List

CROP_PATHOGEN_REGISTRY: Dict[str, List[Dict[str, Any]]] = {
    'rice': [
        {
            'name': 'Rice Blast (Magnaporthe oryzae)',
            'type': 'Fungal',
            'temp_range': (20, 28),
            'humidity_min': 80,
            'symptoms': 'Spindle-shaped lesions on leaves with greyish centers and brown margins.',
            'prevention': 'Seed treatment with Pseudomonas fluorescens (10g/kg); avoid excessive nitrogenous fertilizers; spray Tricyclazole 75 WP (0.6g/L) if lesions appear.'
        },
        {
            'name': 'Brown Plant Hopper (Nilaparvata lugens)',
            'type': 'Insect Pest',
            'temp_range': (25, 32),
            'humidity_min': 75,
            'symptoms': 'Hopper burn patches in circular drying zones near base of tillers.',
            'prevention': 'Form alleyways (30cm every 2m); alternate wetting and drying irrigation; apply Neem oil 3% or Azadirachtin 1500 ppm.'
        }
    ],
    'cotton': [
        {
            'name': 'Bacterial Blight (Xanthomonas citri pv. malvacearum)',
            'type': 'Bacterial',
            'temp_range': (24, 30),
            'humidity_min': 75,
            'symptoms': 'Angular water-soaked leaf spots and black lesions on stems (black arm).',
            'prevention': 'Delint seeds with concentrated sulphuric acid; spray Copper Oxychloride (0.25%) + Streptocycline (100 ppm).'
        },
        {
            'name': 'Whitefly & Aphid Complex',
            'type': 'Sucking Pest',
            'temp_range': (27, 36),
            'humidity_min': 40,
            'symptoms': 'Curling leaves, honeydew excretion, and sooty mold development.',
            'prevention': 'Install yellow sticky traps (10-12/acre); spray 5% Neem Seed Kernel Extract (NSKE) or Diafenthiuron 50 WP.'
        }
    ],
    'maize': [
        {
            'name': 'Fall Armyworm (Spodoptera frugiperda)',
            'type': 'Insect Pest',
            'temp_range': (20, 32),
            'humidity_min': 50,
            'symptoms': 'Ragged shot-hole feeding marks on leaves and heavy frass in whorls.',
            'prevention': 'Apply sand/soil mixed with ash into whorls; release Trichogramma pretiosum egg parasitoids; spray Emamectin Benzoate 5 SG.'
        },
        {
            'name': 'Maydis Leaf Blight',
            'type': 'Fungal',
            'temp_range': (22, 30),
            'humidity_min': 78,
            'symptoms': 'Elongated, rectangular buff-colored lesions bounded by veins.',
            'prevention': 'Use resistant hybrids; seed treatment with Captan or Thiram; foliar spray of Mancozeb 75 WP (2g/L).'
        }
    ],
    'banana': [
        {
            'name': 'Black Sigatoka (Pseudocercospora fijiensis)',
            'type': 'Fungal',
            'temp_range': (23, 29),
            'humidity_min': 80,
            'symptoms': 'Narrow rusty-brown streaks parallel to veins developing into necrotic patches.',
            'prevention': 'De-leaf infected lower fronds; improve drainage; spray mineral oil combined with Propiconazole 25 EC.'
        },
        {
            'name': 'Panama Wilt (Fusarium oxysporum f. sp. cubense)',
            'type': 'Soil Fungal',
            'temp_range': (24, 32),
            'humidity_min': 60,
            'symptoms': 'Yellowing of lower leaf margins and splitting of pseudostem base.',
            'prevention': 'Soil solarization; incorporate enriched Trichoderma viride in FYM (2kg/plant); avoid water stagnation.'
        }
    ],
    'grapes': [
        {
            'name': 'Downy Mildew (Plasmopara viticola)',
            'type': 'Fungal',
            'temp_range': (18, 26),
            'humidity_min': 80,
            'symptoms': 'Yellowish oil-spots on leaf upper surface and white downy growth underneath.',
            'prevention': 'Canopy management for air circulation; preventative spray of Bordeaux mixture 1% or Metalaxyl + Mancozeb.'
        },
        {
            'name': 'Powdery Mildew (Erysiphe necator)',
            'type': 'Fungal',
            'temp_range': (22, 32),
            'humidity_min': 50,
            'symptoms': 'Ash-grey powdery patches on young berries, shoots, and leaves.',
            'prevention': 'Dormant pruning spray with wettable sulfur (2g/L); apply bio-control Ampelomyces quisqualis.'
        }
    ],
    'chickpea': [
        {
            'name': 'Ascochyta Blight',
            'type': 'Fungal',
            'temp_range': (15, 23),
            'humidity_min': 75,
            'symptoms': 'Circular necrotic lesions with concentric rings of pycnidia on pods and stems.',
            'prevention': 'Plant resistant varieties; maintain wider row spacing; spray Chlorothalonil or Mancozeb.'
        },
        {
            'name': 'Fusarium Wilt',
            'type': 'Soil Fungal',
            'temp_range': (22, 28),
            'humidity_min': 45,
            'symptoms': 'Drooping of petioles, vascular browning, and sudden plant wilting.',
            'prevention': 'Deep summer plowing; seed treatment with Trichoderma harzianum (4g/kg seed); crop rotation with non-host cereals.'
        }
    ]
}

# General fallback for remaining crops
DEFAULT_PATHOGENS = [
    {
        'name': 'Damping-Off & Root Rot Complex',
        'type': 'Fungal / Oomycete',
        'temp_range': (20, 30),
        'humidity_min': 75,
        'symptoms': 'Water-soaked collar rot and seedling collapse at ground level.',
        'prevention': 'Avoid poor drainage; treat seeds with Trichoderma viride (10g/kg); drench soil with Copper Oxychloride (2.5g/L).'
    },
    {
        'name': 'Aphids & Thrips Infestation',
        'type': 'Sucking Pest',
        'temp_range': (22, 34),
        'humidity_min': 40,
        'symptoms': 'Leaf deformation, mottling, and transmission of viral vectors.',
        'prevention': 'Conserve coccinellid ladybird predators; spray 2% Neem oil emulsion; use blue/yellow sticky traps.'
    }
]

class DiseaseAlertService:
    @staticmethod
    def get_alerts(crop_name: str, temperature: float, humidity: float) -> List[Dict[str, Any]]:
        """
        Evaluate real-time disease and pest vulnerability based on temperature & humidity.
        """
        crop_key = crop_name.strip().lower()
        pathogens = CROP_PATHOGEN_REGISTRY.get(crop_key, DEFAULT_PATHOGENS)
        
        alerts = []
        for p in pathogens:
            temp_min, temp_max = p['temp_range']
            humid_min = p['humidity_min']
            
            temp_match = temp_min <= temperature <= temp_max
            humid_match = humidity >= humid_min
            
            if temp_match and humid_match:
                risk_level = "High Risk"
                status_color = "#ef4444"  # Red
                trigger_reason = f"Current temperature ({temperature}°C) and high humidity ({humidity}%) are within optimal pathogen reproduction zone."
            elif temp_match or humid_match:
                risk_level = "Moderate Risk"
                status_color = "#f59e0b"  # Amber
                trigger_reason = f"Favorable environmental factors present ({'temperature' if temp_match else 'humidity'}). Monitor crop canopy regularly."
            else:
                risk_level = "Low Risk"
                status_color = "#10b981"  # Green
                trigger_reason = f"Current weather conditions are unfavorable for pathogen incubation."

            alerts.append({
                'name': p['name'],
                'type': p['type'],
                'risk_level': risk_level,
                'status_color': status_color,
                'trigger_reason': trigger_reason,
                'symptoms': p['symptoms'],
                'prevention': p['prevention']
            })
            
        return alerts
