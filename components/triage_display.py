"""
Triage Results Display Component for CropCare
Renders up to 3 candidate issue categories in styled confidence cards with
visible evidence, look-alike conditions, additional observations needed, and safety disclaimers.
"""

import streamlit as st
from typing import Dict, Any, List


def render_triage_display(triage_data: Dict[str, Any], crop_name: str, quality_passed: bool):
    """
    Renders visual confidence cards and observation guidance.
    """
    st.markdown("## 🎯 Triage Analysis Results")
    st.caption("Visual similarity breakdown based on reported context and image patterns.")

    # Warning banner if image quality failed
    if not quality_passed:
        st.warning(
            "⚠️ **Quality Alert**: Image quality checks failed or were skipped. "
            "Triage results are based primarily on field symptom heuristics."
        )

    if "warning_note" in triage_data:
        st.info(f"ℹ️ {triage_data['warning_note']}")

    categories = triage_data.get("categories", [])

    if not categories:
        st.error("No triage categories could be determined. Please refine your symptom selections.")
        return

    st.markdown(f"### 🏷️ Top Candidate Issue Categories for **{crop_name}**")
    
    # Render cards for up to 3 categories
    for idx, cat in enumerate(categories, 1):
        name = cat.get("name", "Unknown Issue")
        confidence = float(cat.get("confidence", 0.5))
        confidence_pct = int(confidence * 100)
        evidence = cat.get("evidence", "No specific evidence noted.")
        look_alikes = cat.get("look_alikes", "N/A")

        # Color badges based on confidence level
        if confidence >= 0.75:
            badge_color = "#15803D" # Dark Green
            card_bg = "#F0FDF4"
            border_color = "#BBF7D0"
        elif confidence >= 0.50:
            badge_color = "#D97706" # Amber
            card_bg = "#FFFBEB"
            border_color = "#FDE68A"
        else:
            badge_color = "#6B7280" # Gray
            card_bg = "#F9FAFB"
            border_color = "#E5E7EB"

        st.markdown(
            f"""
            <div style="
                background-color: {card_bg};
                border: 1px solid {border_color};
                border-left: 6px solid {badge_color};
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 16px;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <h4 style="margin: 0; color: #1F2937;">Option #{idx}: {name}</h4>
                    <span style="
                        background-color: {badge_color};
                        color: white;
                        padding: 4px 12px;
                        border-radius: 12px;
                        font-weight: bold;
                        font-size: 0.85rem;
                    ">Visual Match: {confidence_pct}%</span>
                </div>
                <p style="margin: 6px 0; color: #374151;"><strong>🔍 Visible Evidence:</strong> {evidence}</p>
                <p style="margin: 6px 0; color: #4B5563; font-style: italic;"><strong>⚡ Look-alike Conditions:</strong> {look_alikes}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Required Follow-up Observations
    needed_obs = triage_data.get("additional_observations_needed", [])
    if needed_obs:
        st.markdown("### 🔬 Recommended Additional Field Observations")
        st.markdown("To help narrow down these possibilities, check for these specific signs:")
        for obs in needed_obs:
            st.markdown(f"- 🔍 {obs}")

    # Educational Disclaimer Box
    st.markdown("---")
    disclaimer = triage_data.get(
        "disclaimer",
        "⚠️ **Educational Notice**: Visual triage only. Always consult a certified local agronomist."
    )
    st.info(disclaimer)
