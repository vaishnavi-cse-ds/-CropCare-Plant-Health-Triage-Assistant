"""
Observation Form Component for CropCare
Collects crop species, stage, location, weather, watering, symptoms, photo upload,
and opt-in retention consent.
"""

import streamlit as st
from PIL import Image
from typing import Dict, Any, Tuple, Optional
from config import (
    CROPS, PLANT_STAGES, LOCATION_TYPES, WEATHER_CONDITIONS,
    WATERING_PRACTICES, AFFECTED_AREAS, SYMPTOM_CHIPS, SYMPTOM_DURATIONS
)
from utils.image_checker import check_image_quality, ImageQualityResult


def render_observation_form() -> Tuple[Optional[Dict[str, Any]], Optional[Image.Image], Optional[ImageQualityResult], bool]:
    """
    Renders field context form and image uploader with field-note styling.
    Returns (form_data_dict, pil_image, image_quality_result, photo_opt_in).
    """
    st.markdown("### 📋 Field Context & Observation Details")
    st.caption("Provide details about the affected crop and environment to help ground the triage analysis.")

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            crop_selected = st.selectbox(
                "🌾 Target Crop Type",
                options=CROPS,
                help="Select the crop species you are inspecting."
            )
            
            # Require explicit confirmation if "Other" or custom
            if crop_selected == "Other / Unknown":
                confirmed_crop_name = st.text_input(
                    "Specify Crop Name (Required)",
                    placeholder="e.g. Bell Pepper, Cassava, Brinjal",
                    help="User confirmation of exact crop species."
                )
                crop_name = confirmed_crop_name if confirmed_crop_name.strip() else "Unknown Crop"
            else:
                crop_name = crop_selected

            plant_stage = st.selectbox(
                "🌱 Plant Growth Stage",
                options=PLANT_STAGES
            )

            location_type = st.selectbox(
                "🏡 Location / Growing Environment",
                options=LOCATION_TYPES
            )

            weather = st.selectbox(
                "🌤️ Recent Weather (Past 7 Days)",
                options=WEATHER_CONDITIONS
            )

        with col2:
            watering = st.selectbox(
                "💧 Watering Practice",
                options=WATERING_PRACTICES
            )

            affected_area = st.selectbox(
                "📍 Affected Plant Part",
                options=AFFECTED_AREAS
            )

            symptom_duration = st.selectbox(
                "⏱️ Symptom Duration",
                options=SYMPTOM_DURATIONS
            )

    st.markdown("---")
    st.markdown("### 🔍 Visible Symptoms (Select all that apply)")
    
    # Symptom Pills / Chips multiselect
    selected_symptoms = st.multiselect(
        "Symptom Indicators",
        options=SYMPTOM_CHIPS,
        default=["Yellowing (Chlorosis)", "Brown Spotting / Lesions"] if "Yellowing (Chlorosis)" in SYMPTOM_CHIPS else [],
        help="Select key visual clues observed on the foliage or stems."
    )

    st.markdown("---")
    st.markdown("### 📸 Crop / Leaf Photo Upload & Quality Verification")
    
    uploaded_file = st.file_uploader(
        "Upload a clear close-up leaf or canopy photo (JPG/PNG)",
        type=["jpg", "jpeg", "png"],
        help="Make sure the leaf is well-lit, in focus, and occupies most of the frame."
    )

    pil_image: Optional[Image.Image] = None
    quality_result: Optional[ImageQualityResult] = None

    if uploaded_file is not None:
        try:
            pil_image = Image.open(uploaded_file)
            
            # Show image preview and quality metrics side by side
            p_col1, p_col2 = st.columns([1, 1])
            with p_col1:
                st.image(pil_image, caption="Uploaded Image Preview", use_container_width=True)

            with p_col2:
                st.markdown("#### 📐 Automated Image Quality Audit")
                quality_result = check_image_quality(pil_image)
                
                # Display metrics badges
                m = quality_result.metrics
                st.write(f"• **Sharpness Score**: `{m.get('blur_variance', 0)}` (Min threshold: 50.0)")
                st.write(f"• **Brightness Level**: `{m.get('mean_brightness', 0)} / 255` (Target: 40 - 245)")
                st.write(f"• **Plant Coverage**: `{m.get('plant_coverage_pct', 0)}%` (Min threshold: 12.0%)")

                if quality_result.is_valid:
                    st.success(quality_result.get_summary_message())
                else:
                    st.error("⚠️ Image Quality Warning")
                    for issue in quality_result.issues:
                        st.markdown(f"- ❌ {issue}")
                    st.info("💡 *Tip: Retake photo in bright daylight, hold phone steady, and fill the frame with the leaf.*")

                if quality_result.warnings:
                    for w in quality_result.warnings:
                        st.warning(f"⚠️ {w}")

        except Exception as e:
            st.error(f"Error loading image: {str(e)}")

    st.markdown("---")
    st.markdown("### 🔒 Privacy & Consent")
    photo_opt_in = st.checkbox(
        "Opt-in: Retain uploaded photo in local case journal database.",
        value=False,
        help="If unchecked, only text metadata and symptom observations will be saved to your journal."
    )

    user_notes = st.text_area(
        "📝 Additional Field Notes / Observations (Optional)",
        placeholder="e.g. Observed on 3 adjacent plants along the field edge near irrigation ditch."
    )

    form_data = {
        "crop": crop_name,
        "plant_stage": plant_stage,
        "location_type": location_type,
        "weather": weather,
        "watering": watering,
        "affected_area": affected_area,
        "symptom_duration": symptom_duration,
        "symptoms": selected_symptoms,
        "user_notes": user_notes
    }

    return form_data, pil_image, quality_result, photo_opt_in
