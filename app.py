"""
CropCare — Plant Health Triage Assistant
Main Streamlit Application File

Designed for agricultural students exploring agtech, image audit, computer vision,
and non-chemical plant health triage safety.
"""

import os
import uuid
import streamlit as st
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from config import COLORS, DISCLAIMER_TEXT
from database import init_db, save_case, get_all_cases
from adapters.vision_adapter import GeminiVisionAdapter, HuggingFaceVisionAdapter, HeuristicSyntheticAdapter
from components.observation_form import render_observation_form
from components.triage_display import render_triage_display
from components.safety_checklist import render_safety_checklist
from components.case_journal import render_case_journal
from components.analytics import render_analytics
from sample_data.seed_db import seed_database
from utils.safety import get_safety_policy_card

# Initialize database schema
init_db()

# Seed data if empty
if not get_all_cases():
    seed_database()

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="CropCare — Plant Health Triage Assistant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Theme Styling (Earthy Green, Amber, Cream)
st.markdown(
    f"""
    <style>
        /* Global Background & Font */
        .stApp {{
            background-color: {COLORS['bg_cream']};
            color: {COLORS['text_dark']};
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }}
        
        /* Headers */
        h1, h2, h3, h4 {{
            color: {COLORS['primary']} !important;
            font-weight: 700;
        }}
        
        /* Custom Header Banner */
        .header-banner {{
            background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
            color: white !important;
            padding: 24px;
            border-radius: 12px;
            margin-bottom: 24px;
            box-shadow: 0 4px 12px rgba(45, 90, 39, 0.15);
        }}
        .header-banner h1 {{
            color: white !important;
            margin: 0 0 8px 0;
            font-size: 2.2rem;
        }}
        .header-banner p {{
            color: #E2E8F0 !important;
            margin: 0;
            font-size: 1.05rem;
        }}
        
        /* Primary Buttons */
        .stButton>button {{
            background-color: {COLORS['primary']} !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
            padding: 8px 20px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease-in-out;
        }}
        .stButton>button:hover {{
            background-color: {COLORS['secondary']} !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}

        /* Metric cards */
        div[data-testid="stMetricValue"] {{
            color: {COLORS['primary']};
            font-weight: 700;
        }}

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {{
            background-color: #F4F1EA;
            border-right: 1px solid {COLORS['border_beige']};
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar Controls
with st.sidebar:
    st.image("https://img.icons8.com/color/96/sprout.png", width=64)
    st.title("CropCare")
    st.caption("Plant Health Triage Assistant")
    st.markdown("---")

    st.markdown("### ⚙️ Vision Engine Settings")
    
    # Engine Selector
    engine_choice = st.radio(
        "Select Vision Backend Engine",
        options=["Offline Heuristic (Default)", "Google Gemini Vision", "Hugging Face Endpoint"],
        index=0
    )

    api_key_input = None
    if engine_choice == "Google Gemini Vision":
        api_key_input = st.text_input(
            "Gemini API Key",
            type="password",
            value=os.getenv("GEMINI_API_KEY", ""),
            help="Enter your Gemini API key or set GEMINI_API_KEY in .env file."
        )
        if api_key_input:
            os.environ["GEMINI_API_KEY"] = api_key_input

    elif engine_choice == "Hugging Face Endpoint":
        api_key_input = st.text_input(
            "HF API Token",
            type="password",
            value=os.getenv("HF_API_TOKEN", ""),
            help="Enter your Hugging Face API Token."
        )

    st.markdown("---")
    st.markdown("### 🧪 Demo Tools")
    if st.button("🌱 Re-seed Demo Journal Data"):
        seed_database()
        st.success("Seeded database with demo cases!")
        st.rerun()

    st.markdown("---")
    st.caption("🌾 *Designed for Agricultural Students & Agtech Learners.*")

# Header Banner
st.markdown(
    """
    <div class="header-banner">
        <h1>🌱 CropCare — Plant Health Triage Assistant</h1>
        <p>Field context collection, automated leaf photo quality audit, safe triage, and non-chemical management guidance.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Navigation Tabs
tab_triage, tab_journal, tab_analytics, tab_safety = st.tabs([
    "🌿 Triage Assistant",
    "📔 Case Journal",
    "📊 Analytics & Insights",
    "🛡️ Safety & Guidelines"
])

# -----------------------------------------------------------------------------
# TAB 1: TRIAGE ASSISTANT
# -----------------------------------------------------------------------------
with tab_triage:
    form_data, pil_image, quality_result, photo_opt_in = render_observation_form()

    st.markdown("### 🚀 Run Triage Analysis")
    
    if st.button("🔍 Analyze Observation & Image", key="run_triage_btn"):
        if not form_data["symptoms"] and pil_image is None:
            st.error("Please provide either visible symptoms or upload a crop photo to run triage.")
        else:
            with st.spinner("Analyzing observation context and image quality..."):
                # Determine quality status
                quality_passed = quality_result.is_valid if quality_result else False
                
                # Instantiate Vision Adapter based on user choice
                if engine_choice == "Google Gemini Vision" and os.getenv("GEMINI_API_KEY"):
                    adapter = GeminiVisionAdapter()
                elif engine_choice == "Hugging Face Endpoint":
                    adapter = HuggingFaceVisionAdapter()
                else:
                    adapter = HeuristicSyntheticAdapter()

                # Perform analysis
                triage_result = adapter.analyze(
                    crop=form_data["crop"],
                    plant_stage=form_data["plant_stage"],
                    location_type=form_data["location_type"],
                    weather=form_data["weather"],
                    watering=form_data["watering"],
                    affected_area=form_data["affected_area"],
                    symptom_duration=form_data["symptom_duration"],
                    symptoms=form_data["symptoms"],
                    image=pil_image
                )

                # Store in session state for tab persistence
                st.session_state["latest_triage"] = triage_result
                st.session_state["latest_form"] = form_data
                st.session_state["latest_image"] = pil_image
                st.session_state["latest_quality_passed"] = quality_passed
                st.session_state["latest_photo_opt_in"] = photo_opt_in

    # Render results if present in session state
    if "latest_triage" in st.session_state:
        triage_data = st.session_state["latest_triage"]
        fdata = st.session_state["latest_form"]
        p_image = st.session_state["latest_image"]
        q_passed = st.session_state["latest_quality_passed"]
        opt_in = st.session_state["latest_photo_opt_in"]

        st.markdown("---")
        render_triage_display(triage_data, fdata["crop"], q_passed)

        st.markdown("---")
        render_safety_checklist(triage_data)

        st.markdown("---")
        st.markdown("### 💾 Save to Case Journal")
        
        col_s1, col_s2 = st.columns([2, 1])
        with col_s1:
            save_case_name = st.text_input(
                "Confirmed Crop Species Name for Journal Record",
                value=fdata["crop"],
                help="Confirm the exact crop species before saving."
            )
        with col_s2:
            st.write("") # Spacer
            st.write("")
            if st.button("💾 Save Case to Database"):
                case_id = f"CASE-{uuid.uuid4().hex[:6].upper()}"
                
                # Read image bytes if present and opt-in is active
                img_bytes = None
                if p_image and opt_in:
                    import io
                    buf = io.BytesIO()
                    p_image.save(buf, format="JPEG")
                    img_bytes = buf.getvalue()

                top_cat_name = triage_data.get("categories", [{}])[0].get("name", "Unclassified")
                top_confidence = triage_data.get("categories", [{}])[0].get("confidence", 0.5)

                save_case(
                    case_id=case_id,
                    crop=fdata["crop"],
                    plant_stage=fdata["plant_stage"],
                    location_type=fdata["location_type"],
                    weather=fdata["weather"],
                    watering=fdata["watering"],
                    affected_area=fdata["affected_area"],
                    symptom_duration=fdata["symptom_duration"],
                    symptoms=fdata["symptoms"],
                    image_quality_passed=q_passed,
                    image_metrics=quality_result.metrics if quality_result else {},
                    top_issue_category=top_cat_name,
                    confidence_score=top_confidence,
                    triage_summary=triage_data,
                    photo_opt_in=opt_in,
                    photo_bytes=img_bytes,
                    user_notes=fdata.get("user_notes", ""),
                    confirmed_crop=save_case_name
                )

                st.success(f"🎉 Case **{case_id}** saved to Case Journal! Go to the 'Case Journal' tab to track progression.")

# -----------------------------------------------------------------------------
# TAB 2: CASE JOURNAL
# -----------------------------------------------------------------------------
with tab_journal:
    render_case_journal()

# -----------------------------------------------------------------------------
# TAB 3: ANALYTICS & INSIGHTS
# -----------------------------------------------------------------------------
with tab_analytics:
    render_analytics()

# -----------------------------------------------------------------------------
# TAB 4: SAFETY & GUIDELINES
# -----------------------------------------------------------------------------
with tab_safety:
    st.markdown("## 🛡️ Agricultural Safety & Ethical Principles")
    st.markdown("CropCare is an educational tool built to teach students best practices in plant pathology triage.")

    policy = get_safety_policy_card()
    st.markdown(f"### {policy['title']}")
    for rule in policy["rules"]:
        st.markdown(f"- {rule}")

    st.markdown("---")
    st.markdown("### 🚫 Why Pesticide & Chemical Advice is Prohibited")
    st.markdown(
        """
        1. **Environmental & Non-Target Harm**: Misapplying synthetic pesticides can pollute local groundwater, kill beneficial pollinators like honeybees, and eradicate predatory insects.
        2. **Resistance Risk**: Sub-lethal or improper chemical dosages induce rapid evolutionary resistance in insect pests and fungal pathogens.
        3. **Diagnostic Errors**: Treating a physiological condition (like drought wilt or potassium burn) with a chemical fungicide damages plant tissues without solving the root issue.
        4. **Regulatory & Legal Safety**: Chemical recommendations require official state/country licensing and site-specific soil/crop testing.
        """
    )

    st.markdown("---")
    st.info(DISCLAIMER_TEXT)
