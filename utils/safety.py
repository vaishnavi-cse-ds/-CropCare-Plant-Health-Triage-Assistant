"""
Safety & Compliance Engine for CropCare
Enforces safety rules: prohibits chemical/pesticide prescriptions, filters unsafe advice,
and ensures proper disclaimers.
"""

import re
from typing import Dict, Any, Tuple
from config import PROHIBITED_TERMS, DISCLAIMER_TEXT


def contains_prohibited_advice(text: str) -> bool:
    """Check if text contains banned chemical, pesticide, or exact dosage terms."""
    if not text:
        return False
    
    text_lower = text.lower()
    for pattern in PROHIBITED_TERMS:
        if re.search(pattern, text_lower):
            return True
    return False


def sanitize_text(text: str) -> Tuple[str, bool]:
    """
    Scans text for prohibited advice terms.
    If found, replaces them with safe advisory markers and returns (sanitized_text, was_modified).
    """
    if not text:
        return text, False

    was_modified = False
    sanitized = text

    for pattern in PROHIBITED_TERMS:
        if re.search(pattern, sanitized, flags=re.IGNORECASE):
            sanitized = re.sub(
                pattern,
                "[REDACTED: Specific chemical/pesticide advice prohibited - consult local agricultural expert]",
                sanitized,
                flags=re.IGNORECASE
            )
            was_modified = True

    return sanitized, was_modified


def validate_triage_output(triage_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitizes all string fields in triage output to ensure strict compliance
    with non-diagnostic safety policies.
    """
    cleaned = dict(triage_data)
    
    # Force disclaimer inclusion
    cleaned["disclaimer"] = DISCLAIMER_TEXT

    # Clean categories list
    if "categories" in cleaned and isinstance(cleaned["categories"], list):
        sanitized_cats = []
        for cat in cleaned["categories"]:
            if isinstance(cat, dict):
                c_copy = dict(cat)
                c_copy["name"], _ = sanitize_text(c_copy.get("name", ""))
                c_copy["evidence"], _ = sanitize_text(c_copy.get("evidence", ""))
                c_copy["look_alikes"], _ = sanitize_text(c_copy.get("look_alikes", ""))
                sanitized_cats.append(c_copy)
            else:
                sanitized_cats.append(cat)
        cleaned["categories"] = sanitized_cats

    # Clean safe next steps list
    if "safe_next_steps" in cleaned and isinstance(cleaned["safe_next_steps"], list):
        cleaned["safe_next_steps"] = [
            sanitize_text(step)[0] for step in cleaned["safe_next_steps"]
        ]

    return cleaned


def get_safety_policy_card() -> Dict[str, str]:
    """Return safety policy rules for UI rendering."""
    return {
        "title": "CropCare Safety & Ethical Principles",
        "rules": [
            "🚫 **No Chemical Prescriptions**: We do not recommend specific brand-name pesticides, active chemical compounds, or dosages.",
            "🔍 **Visual Similarity Only**: Model outputs represent visual patterns, not clinical laboratory diagnoses.",
            "🌱 **Cultural & Physical Management First**: Focus on isolation, sanitation, watering adjustment, and monitoring.",
            "👨‍🌾 **Human Expert Verification**: Always confirm findings with a qualified agricultural officer or lab.",
            "🔒 **Consent-Based Privacy**: Photos are retained only when you explicitly opt-in."
        ]
    }
