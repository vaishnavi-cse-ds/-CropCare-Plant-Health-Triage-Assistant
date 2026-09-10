"""
CropCare Configuration & Constants
Theme, safety keywords, image thresholds, and default options.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "cropcare.db"

# Color Palette (Earthy Green, Amber, Cream, Warm Beige)
COLORS = {
    "primary": "#2D5A27",       # Forest Green
    "secondary": "#4A7C59",     # Sage Green
    "accent_amber": "#D97706",  # Warm Amber / Caution
    "accent_amber_light": "#FEF3C7",
    "bg_cream": "#FDFBF7",      # Cream Background
    "bg_card": "#FFFFFF",
    "border_beige": "#E5E0D8",  # Warm Beige Border
    "text_dark": "#1F2937",     # Dark Charcoal
    "text_muted": "#4B5563",
    "success_green": "#15803D",
    "warning_red": "#B91C1C",
}

# Image Quality Thresholds
IMAGE_THRESHOLDS = {
    "blur_min_variance": 50.0,    # Laplacian variance below this is considered blurry
    "darkness_min_mean": 40.0,    # Mean grayscale pixel brightness (0-255) below this is too dark
    "brightness_max_mean": 245.0, # Mean grayscale pixel brightness above this is overexposed
    "coverage_min_pct": 12.0,     # Percentage of green/plant-like pixels required
}

# Supported Options for Observation Form
CROPS = [
    "Tomato", "Potato", "Corn / Maize", "Rice", "Wheat",
    "Cotton", "Apple", "Grape", "Citrus", "Soybean", "Other / Unknown"
]

PLANT_STAGES = [
    "Seedling / Early Vegetative",
    "Vegetative",
    "Flowering",
    "Fruiting / Grain Fill",
    "Mature / Harvest"
]

LOCATION_TYPES = [
    "Open Field",
    "Greenhouse / Polyhouse",
    "Container / Raised Bed",
    "Indoor Grow",
    "Hydroponic / Aeroponic"
]

WEATHER_CONDITIONS = [
    "Hot & Dry",
    "Warm & Humid",
    "Cool & Wet / Heavy Rain",
    "Overcast & Mild",
    "Fluctuating Temperatures",
    "Normal Seasonal Weather"
]

WATERING_PRACTICES = [
    "Drip Irrigation (Scheduled)",
    "Overhead Sprinkler",
    "Manual Hose / Watering Can",
    "Rainfed Only",
    "Flood / Furrow Irrigation",
    "Irregular / Erratic"
]

AFFECTED_AREAS = [
    "Lower Leaves Only",
    "Upper / New Leaves",
    "Entire Canopy",
    "Stems / Stalks",
    "Fruit / Flower Pods",
    "Roots / Base"
]

SYMPTOM_CHIPS = [
    "Yellowing (Chlorosis)",
    "Brown Spotting / Lesions",
    "Wilting / Drooping",
    "Powdery White Coating",
    "Leaf Curling / Distortion",
    "Stunted Growth",
    "Dark / Necrotic Edges",
    "Holes / Chewed Margins",
    "Rust / Orange Pustules",
    "Webbing / Fine Silk",
    "Stem Canker / Rot"
]

SYMPTOM_DURATIONS = [
    "Less than 48 hours",
    "3 to 7 days",
    "1 to 2 weeks",
    "More than 2 weeks"
]

# Prohibited advice terms (Pesticides, active chemical ingredients, precise chemical dosages)
PROHIBITED_TERMS = [
    r"\bglyphosate\b", r"\bchlorpyrifos\b", r"\bimidacloprid\b", r"\bmalathion\b",
    r"\bcarbaryl\b", r"\bmancozeb\b", r"\bcopper oxychloride\b", r"\bparaquat\b",
    r"\bneonicotinoid\b", r"\batrazine\b", r"\b2,4-d\b", r"\bpermethrin\b",
    r"\bdose\b", r"\bdosage\b", r"\bml/L\b", r"\bgrams per liter\b", r"\bppm spray\b",
    r"\bspray chemical\b", r"\binsecticide spray\b", r"\bfungicide application\b"
]

DISCLAIMER_TEXT = (
    "⚠️ **Educational Triage Notice**: CropCare provides visual triage based on observed signs and user input. "
    "This tool **does not provide official agricultural diagnoses or chemical prescriptions**. "
    "Always consult a local agricultural extension office, certified agronomist, or plant pathology laboratory "
    "before taking management actions."
)
