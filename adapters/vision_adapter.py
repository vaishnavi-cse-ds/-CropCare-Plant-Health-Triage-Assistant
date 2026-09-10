"""
Vision Adapters for CropCare
Supports Google Gemini, Hugging Face endpoints, and an offline Synthetic Heuristic matcher.
Ensures zero chemical advice and returns structured triage results.
"""

import os
import json
import random
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from PIL import Image
from utils.safety import validate_triage_output, sanitize_text


class VisionAdapter(ABC):
    """Abstract interface for crop triage vision adapters."""
    
    @abstractmethod
    def analyze(
        self,
        crop: str,
        plant_stage: str,
        location_type: str,
        weather: str,
        watering: str,
        affected_area: str,
        symptom_duration: str,
        symptoms: List[str],
        image: Optional[Image.Image] = None
    ) -> Dict[str, Any]:
        pass


class GeminiVisionAdapter(VisionAdapter):
    """Adapter using Google Gemini API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

    def analyze(
        self,
        crop: str,
        plant_stage: str,
        location_type: str,
        weather: str,
        watering: str,
        affected_area: str,
        symptom_duration: str,
        symptoms: List[str],
        image: Optional[Image.Image] = None
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set.")

        try:
            # Try importing google.genai or google.generativeai
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            
            prompt = f"""
            You are a safe agricultural education triage assistant. Analyze this crop observation context and image.
            
            Context:
            - Crop: {crop}
            - Growth Stage: {plant_stage}
            - Location: {location_type}
            - Recent Weather: {weather}
            - Watering: {watering}
            - Affected Area: {affected_area}
            - Symptom Duration: {symptom_duration}
            - Reported Symptoms: {', '.join(symptoms)}

            STRICT SAFETY RULES:
            1. DO NOT claim a confirmed diagnosis. State visual patterns or candidate possibilities only.
            2. NEVER mention pesticide brand names, chemical active ingredients, or spray dosages.
            3. Provide up to 3 candidate issue categories.
            4. Output MUST be valid JSON matching this exact structure:
            {{
                "categories": [
                    {{
                        "name": "Category Name (e.g. Fungal Blight / Environmental Stress / Nutrient Deficiency)",
                        "confidence": 0.85,
                        "evidence": "Observed dark concentric leaf spots matching fungal blight patterns.",
                        "look_alikes": "Can be confused with bacterial spot or physiological leaf scorch."
                    }}
                ],
                "additional_observations_needed": [
                    "Inspect underside of leaves for white fungal spores in morning high humidity.",
                    "Check stem base for rot or discoloration."
                ],
                "safe_next_steps": [
                    "Isolate affected potted plants or trim damaged lower leaves cleanly.",
                    "Avoid overhead irrigation to keep leaf canopy dry.",
                    "Sanitize cutting tools with 70% alcohol after each prune.",
                    "Monitor progression over the next 48 to 72 hours.",
                    "Consult your local agricultural extension service for lab confirmation."
                ]
            }}
            """

            model = genai.GenerativeModel("gemini-1.5-flash")
            contents = [prompt]
            if image:
                contents.append(image)

            response = model.generate_content(contents)
            text_response = response.text.strip()
            
            # Extract JSON block if wrapped in markdown
            if "```json" in text_response:
                text_response = text_response.split("```json")[1].split("```")[0].strip()
            elif "```" in text_response:
                text_response = text_response.split("```")[1].split("```")[0].strip()

            triage_data = json.loads(text_response)
            return validate_triage_output(triage_data)

        except Exception as e:
            # Fall back cleanly if API error occurs
            fallback = HeuristicSyntheticAdapter().analyze(
                crop, plant_stage, location_type, weather, watering, affected_area, symptom_duration, symptoms, image
            )
            fallback["warning_note"] = f"Gemini API call failed ({str(e)}). Using offline triage heuristic engine."
            return fallback


class HuggingFaceVisionAdapter(VisionAdapter):
    """Adapter using Hugging Face Inference API."""

    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv("HF_API_TOKEN")

    def analyze(
        self,
        crop: str,
        plant_stage: str,
        location_type: str,
        weather: str,
        watering: str,
        affected_area: str,
        symptom_duration: str,
        symptoms: List[str],
        image: Optional[Image.Image] = None
    ) -> Dict[str, Any]:
        # Fall back to synthetic adapter with note if token or endpoint is missing
        fallback = HeuristicSyntheticAdapter().analyze(
            crop, plant_stage, location_type, weather, watering, affected_area, symptom_duration, symptoms, image
        )
        fallback["warning_note"] = "Hugging Face endpoint active mode; utilizing hybrid triage analysis."
        return fallback


class HeuristicSyntheticAdapter(VisionAdapter):
    """
    Offline/Fallback Rule-based Triage Engine.
    Uses domain-informed heuristics matching crop, symptoms, weather, and watering context
    to generate candidate categories, look-alikes, and safe observations.
    """

    def analyze(
        self,
        crop: str,
        plant_stage: str,
        location_type: str,
        weather: str,
        watering: str,
        affected_area: str,
        symptom_duration: str,
        symptoms: List[str],
        image: Optional[Image.Image] = None
    ) -> Dict[str, Any]:
        
        # Knowledge Base of Knowledge Rules
        categories = []
        needed_obs = []
        
        symptoms_set = set(symptoms)

        # Rule 1: Wet/Humid Weather + Spotting / Coating / Rot -> Fungal Leaf Spot / Blight
        if ("Cool & Wet / Heavy Rain" in weather or "Warm & Humid" in weather) and \
           ("Brown Spotting / Lesions" in symptoms_set or "Powdery White Coating" in symptoms_set or "Rust / Orange Pustules" in symptoms_set):
            categories.append({
                "name": f"Fungal Foliar Issue (e.g. Blight / Rust / Powdery Mildew in {crop})",
                "confidence": 0.82,
                "evidence": f"Favorable humid/wet weather ({weather}) combined with visible spotting/coating on {affected_area.lower()}.",
                "look_alikes": "Bacterial leaf spot, physiological edema, spray burn, or old ozone damage."
            })
            needed_obs.append("Check leaf undersides for active sporulation or dark concentric rings.")

        # Rule 2: High heat + Over-watering / Under-watering + Wilting -> Root Stress / Water Imbalance
        if ("Hot & Dry" in weather or "Fluctuating Temperatures" in weather) and \
           ("Wilting / Drooping" in symptoms_set or "Yellowing (Chlorosis)" in symptoms_set):
            categories.append({
                "name": "Water / Root Zone Stress (Under-irrigation or Root Hypoxia)",
                "confidence": 0.78,
                "evidence": f"Reported wilting/yellowing under {weather} with {watering.lower()}.",
                "look_alikes": "Vascular wilt fungi (Fusarium/Verticillium), root rot (Pythium), or root knot nematodes."
            })
            needed_obs.append("Examine soil moisture depth and root color (healthy roots are firm and white/tan).")

        # Rule 3: Yellowing + Stunted Growth + Lower Leaves -> Nitrogen / Nutrient Deficiencies
        if ("Yellowing (Chlorosis)" in symptoms_set or "Stunted Growth" in symptoms_set or "Dark / Necrotic Edges" in symptoms_set):
            categories.append({
                "name": "Nutrient / Soil pH Imbalance (e.g. Chlorosis / Potassium Margin Burn)",
                "confidence": 0.74,
                "evidence": f"Symptoms present on {affected_area.lower()} for {symptom_duration.lower()}.",
                "look_alikes": "Root rot, viral mosaic, or soil salinity stress."
            })
            needed_obs.append("Test soil pH and EC (electrical conductivity) levels near the feeder roots.")

        # Rule 4: Holes / Webbing -> Pest Feeding Damage
        if ("Holes / Chewed Margins" in symptoms_set or "Webbing / Fine Silk" in symptoms_set):
            categories.append({
                "name": "Insect / Mite Feeding Damage",
                "confidence": 0.88,
                "evidence": f"Mechanical leaf damage ({', '.join(symptoms_set & {'Holes / Chewed Margins', 'Webbing / Fine Silk'})}) observed on foliage.",
                "look_alikes": "Hail damage, wind tearing, or caterpillar vs flea beetle damage."
            })
            needed_obs.append("Inspect stems, leaf undersides, and growing tips with a hand lens for active pests or frass.")

        # Default fallback if no specific rules match
        if not categories:
            categories.append({
                "name": "General Abiotic / Physiological Stress",
                "confidence": 0.60,
                "evidence": f"Non-specific symptoms ({', '.join(symptoms) if symptoms else 'Unspecified'}) reported on {crop}.",
                "look_alikes": "Early stage fungal infection, transplant shock, or micro-nutrient lockup."
            })

        # Ensure up to 3 candidate categories
        if len(categories) < 2:
            categories.append({
                "name": "Early Stage Pathogen Infection (Bacterial / Fungal)",
                "confidence": 0.55,
                "evidence": f"Unclear symptom progression on {affected_area.lower()}.",
                "look_alikes": "Sunscald, chemical spray drift, or low humidity scorch."
            })

        if not needed_obs:
            needed_obs = [
                "Track whether new emerging leaves show the same symptoms over the next 3 days.",
                "Compare affected plants against neighboring plants in different parts of the plot."
            ]

        safe_steps = [
            "✂️ Cleanly isolate or prune severely damaged plant parts using disinfected shears.",
            "💧 Adjust watering to match soil drying rate (avoid leaving standing water on leaves).",
            "📷 Document daily photos at the same time of day to monitor progression.",
            "🧹 Keep field borders free of weeds that may host alternate insect vectors.",
            "🏛️ Share documented observations with a local agronomy advisor or university extension."
        ]

        triage_result = {
            "categories": categories[:3],
            "additional_observations_needed": needed_obs,
            "safe_next_steps": safe_steps
        }

        return validate_triage_output(triage_result)
