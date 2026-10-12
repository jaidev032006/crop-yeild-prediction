"""
Smart Fertilizer Advisory Engine.
Converts N-P-K soil deficits into exact commercial fertilizer quantities (kg/acre)
for Urea (46% N), SSP (16% P2O5), and MOP (60% K2O), along with organic alternatives
and a phased split application schedule.
"""
from typing import Dict, Any, List
from data.fallback_generator import CROP_PROFILES

class FertilizerService:
    @staticmethod
    def calculate_fertilizer_plan(current_npk: Dict[str, float], crop_name: str) -> Dict[str, Any]:
        """
        Compute commercial and organic fertilizer recommendations per acre.
        1 Hectare = 2.47105 Acres
        """
        crop_key = crop_name.strip().lower()
        optimal = CROP_PROFILES.get(crop_key, {
            'N': (80, 100), 'P': (40, 60), 'K': (40, 60)
        })

        # Ideal midpoints in kg/ha
        target_n_ha = (optimal['N'][0] + optimal['N'][1]) / 2.0
        target_p_ha = (optimal['P'][0] + optimal['P'][1]) / 2.0
        target_k_ha = (optimal['K'][0] + optimal['K'][1]) / 2.0

        current_n_ha = float(current_npk.get('N', 0.0))
        current_p_ha = float(current_npk.get('P', 0.0))
        current_k_ha = float(current_npk.get('K', 0.0))

        # Deficits per hectare (clamped to 0 if soil already has sufficient nutrients)
        deficit_n_ha = max(0.0, target_n_ha - current_n_ha)
        deficit_p_ha = max(0.0, target_p_ha - current_p_ha)
        deficit_k_ha = max(0.0, target_k_ha - current_k_ha)

        # Deficits per acre (kg/acre)
        HA_TO_ACRE = 2.47105
        deficit_n_acre = deficit_n_ha / HA_TO_ACRE
        deficit_p_acre = deficit_p_ha / HA_TO_ACRE
        deficit_k_acre = deficit_k_ha / HA_TO_ACRE

        # Fertilizer conversion factors
        # Urea: 46% Nitrogen
        urea_kg_acre = round(deficit_n_acre / 0.46, 1)
        # Single Super Phosphate (SSP): 16% P2O5
        ssp_kg_acre = round(deficit_p_acre / 0.16, 1)
        # Muriate of Potash (MOP): 60% K2O
        mop_kg_acre = round(deficit_k_acre / 0.60, 1)

        # Split Application Schedule
        split_schedule = [
            {
                'stage': 'Basal Application (Sowing / Planting)',
                'timing': 'At the time of final land preparation',
                'urea_kg': round(0.50 * urea_kg_acre, 1),
                'ssp_kg': ssp_kg_acre,  # 100% P at basal
                'mop_kg': round(0.50 * mop_kg_acre, 1),
                'instructions': 'Incorporate thoroughly into the top 10-15 cm soil layer.'
            },
            {
                'stage': 'First Top Dressing (Vegetative Growth)',
                'timing': '30-35 days after sowing (tillering / branching)',
                'urea_kg': round(0.25 * urea_kg_acre, 1),
                'ssp_kg': 0.0,
                'mop_kg': 0.0,
                'instructions': 'Broadcast when soil has adequate moisture; avoid waterlogged standing water.'
            },
            {
                'stage': 'Second Top Dressing (Panicle / Flowering)',
                'timing': '55-65 days after sowing (flowering / fruit initiation)',
                'urea_kg': round(0.25 * urea_kg_acre, 1),
                'ssp_kg': 0.0,
                'mop_kg': round(0.50 * mop_kg_acre, 1),
                'instructions': 'Apply near the root zone followed by light irrigation.'
            }
        ]

        # Organic Recommendations
        organic_advisory = [
            {
                'name': 'Well-Decomposed Farmyard Manure (FYM)',
                'quantity': '4 to 5 Tonnes / Acre',
                'application': 'Spread 3 weeks prior to sowing during primary tillage.',
                'benefit': 'Restores organic carbon, improves soil water retention, and supplies secondary micro-nutrients.'
            },
            {
                'name': 'Enriched Vermicompost',
                'quantity': '1 to 1.5 Tonnes / Acre',
                'application': 'Apply as basal dressing mixed with beneficial trichoderma.',
                'benefit': 'Provides slow-release macro nutrients (2% N, 1% P, 1.5% K) and beneficial rhizosphere microbes.'
            },
            {
                'name': 'Green Manuring (Dhaincha / Sunn Hemp)',
                'quantity': '20 kg seeds / Acre',
                'application': 'Sow 50 days before main crop and plow in situ at early flowering.',
                'benefit': 'Fixes 25-30 kg of atmospheric biological nitrogen per acre and suppresses weeds.'
            },
            {
                'name': 'Neem Cake (De-oiled)',
                'quantity': '150 kg / Acre',
                'application': 'Apply alongside basal fertilizers.',
                'benefit': 'Acts as a natural nitrification inhibitor to reduce urea losses and controls soil nematodes.'
            }
        ]

        return {
            'crop': crop_name.title(),
            'current_soil_npk': {
                'N': current_n_ha,
                'P': current_p_ha,
                'K': current_k_ha
            },
            'target_optimal_npk': {
                'N': round(target_n_ha, 1),
                'P': round(target_p_ha, 1),
                'K': round(target_k_ha, 1)
            },
            'deficits_kg_acre': {
                'N': round(deficit_n_acre, 1),
                'P': round(deficit_p_acre, 1),
                'K': round(deficit_k_acre, 1)
            },
            'commercial_fertilizers_kg_acre': {
                'urea': urea_kg_acre,
                'ssp': ssp_kg_acre,
                'mop': mop_kg_acre
            },
            'split_schedule': split_schedule,
            'organic_alternatives': organic_advisory
        }
