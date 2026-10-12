"""
Crop Rotation and Seasonal Calendar Planner.
Analyzes current crop taxonomy (Cereal vs Legume, Kharif/Rabi/Zaid)
and formulates restorative rotation plans with month-by-month calendars.
"""
from typing import Dict, Any, List
from data.economics import CROP_ECONOMICS, get_crop_profile

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

class RotationPlanner:
    @staticmethod
    def get_rotation_plan(current_crop: str) -> Dict[str, Any]:
        """
        Produce a sustainable multi-season crop rotation recommendation.
        """
        crop_key = current_crop.strip().lower()
        profile = get_crop_profile(crop_key)
        
        current_season = profile.get('season', 'Kharif')
        is_legume = profile.get('is_legume', False)
        category = profile.get('category', 'cereal')
        
        # Determine next season
        season_succession = {
            'Kharif': 'Rabi',
            'Rabi': 'Zaid',
            'Zaid': 'Kharif',
            'Perennial': 'Intercrop / Cover Crop'
        }
        next_season = season_succession.get(current_season, 'Rabi')
        
        # Suggest restorative next crops
        candidate_rotations = []
        for name, data in CROP_ECONOMICS.items():
            if name == crop_key:
                continue
            
            # If current crop is cereal/exhaustive, prioritize legumes
            if not is_legume and data.get('is_legume', False):
                if data.get('season') == next_season or next_season == 'Intercrop / Cover Crop':
                    candidate_rotations.append(data)
            # If current crop is legume, prioritize nutrient-demanding cereals or fibers
            elif is_legume and not data.get('is_legume', False):
                if data.get('season') == next_season:
                    candidate_rotations.append(data)

        # Fallback if no exact season match
        if not candidate_rotations:
            for name, data in CROP_ECONOMICS.items():
                if name != crop_key and data.get('is_legume', False):
                    candidate_rotations.append(data)
                    if len(candidate_rotations) >= 3:
                        break

        # Agronomic rationale
        if not is_legume:
            rationale = (
                f"{profile['display_name']} is a nutrient-demanding {category} crop that depletes soil nitrogen. "
                f"Following it with a leguminous crop in the upcoming {next_season} season will replenish soil organic "
                f"matter, fix atmospheric nitrogen through rhizobium root nodules, and break weed/pest reproductive cycles."
            )
        else:
            rationale = (
                f"{profile['display_name']} is a nitrogen-fixing pulse crop that enriches soil fertility. "
                f"Rotating into a commercial cereal or cash crop during {next_season} will maximize profit by capitalizing "
                f"on the residual nitrogen and enhanced microbial activity."
            )

        # Build month-by-month calendar
        sowing = set(profile.get('sowing_months', []))
        harvest = set(profile.get('harvest_months', []))
        
        calendar = []
        for m in MONTHS:
            status = "Idle / Field Prep"
            if m in sowing:
                status = "Sowing & Germination"
            elif m in harvest:
                status = "Maturity & Harvesting"
            else:
                # Approximate growing cycle
                status = "Vegetative Growth & Care"
            calendar.append({
                'month': m,
                'status': status
            })

        return {
            'current_crop': profile['display_name'],
            'current_season': current_season,
            'next_season': next_season,
            'is_legume': is_legume,
            'agronomic_rationale': rationale,
            'recommended_next_crops': candidate_rotations[:3],
            'month_calendar': calendar
        }
