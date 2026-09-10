"""
Sample Seed Data Generator for CropCare
Populates SQLite database with realistic synthetic cases for agricultural students.
"""

import uuid
import random
from datetime import datetime, timedelta
from database import save_case, init_db
from config import CROPS, PLANT_STAGES, LOCATION_TYPES, WEATHER_CONDITIONS, WATERING_PRACTICES, AFFECTED_AREAS

SEED_CASES = [
    {
        "crop": "Tomato",
        "confirmed_crop": "Tomato",
        "plant_stage": "Fruiting / Grain Fill",
        "location_type": "Open Field",
        "weather": "Warm & Humid",
        "watering": "Overhead Sprinkler",
        "affected_area": "Lower Leaves Only",
        "symptom_duration": "3 to 7 days",
        "symptoms": ["Brown Spotting / Lesions", "Yellowing (Chlorosis)"],
        "top_issue": "Fungal Foliar Issue (e.g. Early Blight / Alternaria)",
        "confidence": 0.86,
        "status": "Under Observation"
    },
    {
        "crop": "Potato",
        "confirmed_crop": "Potato",
        "plant_stage": "Vegetative",
        "location_type": "Open Field",
        "weather": "Cool & Wet / Heavy Rain",
        "watering": "Rainfed Only",
        "affected_area": "Entire Canopy",
        "symptom_duration": "1 to 2 weeks",
        "symptoms": ["Dark / Necrotic Edges", "Wilting / Drooping"],
        "top_issue": "Late Blight Visual Pattern (Phytophthora infestans)",
        "confidence": 0.89,
        "status": "Confirmed Issue"
    },
    {
        "crop": "Corn / Maize",
        "confirmed_crop": "Corn / Maize",
        "plant_stage": "Flowering",
        "location_type": "Open Field",
        "weather": "Hot & Dry",
        "watering": "Drip Irrigation (Scheduled)",
        "affected_area": "Upper / New Leaves",
        "symptom_duration": "Less than 48 hours",
        "symptoms": ["Holes / Chewed Margins"],
        "top_issue": "Insect Feeding Damage (e.g. Fall Armyworm / Caterpillar)",
        "confidence": 0.92,
        "status": "Resolved"
    },
    {
        "crop": "Wheat",
        "confirmed_crop": "Wheat",
        "plant_stage": "Flowering",
        "location_type": "Open Field",
        "weather": "Warm & Humid",
        "watering": "Rainfed Only",
        "affected_area": "Upper / New Leaves",
        "symptom_duration": "3 to 7 days",
        "symptoms": ["Rust / Orange Pustules"],
        "top_issue": "Cereal Stripe/Puccinia Rust Pattern",
        "confidence": 0.84,
        "status": "Confirmed Issue"
    },
    {
        "crop": "Grape",
        "confirmed_crop": "Grape",
        "plant_stage": "Fruiting / Grain Fill",
        "location_type": "Open Field",
        "weather": "Warm & Humid",
        "watering": "Drip Irrigation (Scheduled)",
        "affected_area": "Entire Canopy",
        "symptom_duration": "1 to 2 weeks",
        "symptoms": ["Powdery White Coating"],
        "top_issue": "Powdery Mildew (Uncinula necator pattern)",
        "confidence": 0.88,
        "status": "Under Observation"
    },
    {
        "crop": "Citrus",
        "confirmed_crop": "Citrus",
        "plant_stage": "Mature / Harvest",
        "location_type": "Container / Raised Bed",
        "weather": "Normal Seasonal Weather",
        "watering": "Manual Hose / Watering Can",
        "affected_area": "Lower Leaves Only",
        "symptom_duration": "More than 2 weeks",
        "symptoms": ["Yellowing (Chlorosis)", "Stunted Growth"],
        "top_issue": "Nitrogen / Zinc Micronutrient Chlorosis",
        "confidence": 0.76,
        "status": "Resolved"
    }
]


def seed_database():
    """Seed the database with sample educational cases."""
    init_db()
    
    for item in SEED_CASES:
        case_id = f"CASE-{random.randint(1000, 9999)}"
        triage_summary = {
            "categories": [
                {
                    "name": item["top_issue"],
                    "confidence": item["confidence"],
                    "evidence": f"Visible signs on {item['affected_area']} under {item['weather']} weather.",
                    "look_alikes": "Physiological stress or secondary infection."
                }
            ],
            "additional_observations_needed": [
                "Inspect lower leaves morning and evening.",
                "Verify soil drainage and root zone health."
            ],
            "safe_next_steps": [
                "Isolate affected plants.",
                "Sanitize pruning tools after use.",
                "Consult local extension officer for lab verification."
            ],
            "disclaimer": "⚠️ Educational Triage Notice: Visual match only. Consult local extension lab."
        }

        save_case(
            case_id=case_id,
            crop=item["crop"],
            plant_stage=item["plant_stage"],
            location_type=item["location_type"],
            weather=item["weather"],
            watering=item["watering"],
            affected_area=item["affected_area"],
            symptom_duration=item["symptom_duration"],
            symptoms=item["symptoms"],
            image_quality_passed=True,
            image_metrics={"blur_variance": 120.0, "mean_brightness": 140.0, "plant_coverage_pct": 65.0},
            top_issue_category=item["top_issue"],
            confidence_score=item["confidence"],
            triage_summary=triage_summary,
            photo_opt_in=False,
            photo_bytes=None,
            user_notes=f"Synthetic seed case for {item['crop']} educational demonstration.",
            confirmed_crop=item["confirmed_crop"]
        )

    print("✅ Database successfully seeded with demo educational cases.")


if __name__ == "__main__":
    seed_database()
