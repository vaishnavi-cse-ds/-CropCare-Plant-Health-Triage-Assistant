# 🌱 CropCare — Plant Health Triage Assistant

**CropCare** is a safety-first Streamlit web application designed for agricultural students exploring agtech, computer vision, field context logging, and non-chemical plant health triage.

---

## 🌟 Key Features

1. **Structured Field Context Collection**:
   - Capture crop species (with explicit user confirmation), growth stage, location type, weather context, irrigation practice, affected area, and symptom duration.
   - Select symptom indicators using interactive chips.

2. **Automated Image Quality Audit**:
   - Computer vision checks for **sharpness/blur** (Laplacian variance), **brightness/exposure** (luminance mean), and **vegetation/leaf coverage %** before analysis.

3. **Multi-Backend Vision Adapters**:
   - **Google Gemini Vision API** adapter.
   - **Hugging Face Endpoint** adapter.
   - **Offline Synthetic Heuristic Engine** (runs seamlessly without API keys).

4. **Visual Triage & Confidence Cards**:
   - Displays up to 3 candidate issue categories with visual similarity confidence scores, visible evidence, and look-alike conditions.
   - Highlights recommended follow-up observations needed to confirm diagnoses.

5. **Safe Next-Step Checklist**:
   - Focuses strictly on physical isolation, moisture/canopy hygiene, sanitization, and step-by-step instructions for contacting local agricultural extension experts.

6. **Consent-Based Case Journal**:
   - SQLite database journal (`data/cropcare.db`).
   - Photos are retained **only** when the user explicitly opts in.
   - Track case timeline history, add follow-up notes, update status, and confirm crop types.

7. **Interactive Agricultural Analytics**:
   - Plotly dashboard showing issue category distributions, crop species breakdowns, weather correlations, and case outcomes.

8. **Strict Safety Guardrails**:
   - **No Prescriptions**: Blocks pesticide brand names, chemical active ingredients, and spray dosages.
   - **Non-Diagnostic**: Clearly states visual similarity rather than a clinical lab diagnosis.

---

## 🛠️ Tech Stack

- **Python**: 3.11+
- **Frontend / Framework**: Streamlit
- **Image Processing**: Pillow, NumPy (Laplacian blur & Excess Green Index)
- **Data & Visualization**: Pandas, Plotly
- **Database**: SQLite3
- **Testing**: pytest

---

## 🚀 Quick Start Guide

### 1. Environment Setup
```bash
# Navigate to project directory
cd C:\Users\Dell\.gemini\antigravity\scratch\cropcare_app

# Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Running Unit Tests

Run the full pytest suite covering image validation, safety rules, confidence thresholds, and privacy retention:
```bash
pytest tests/ -v
```

---

## 📁 Project Structure

```
cropcare_app/
├── app.py                      # Main Streamlit application
├── config.py                   # Styling tokens, thresholds, safety constants
├── database.py                 # SQLite database & journal management
├── requirements.txt            # Python dependencies
├── .env.example                # API key template
├── README.md                   # Application documentation
├── utils/
│   ├── image_checker.py        # Image blur, brightness & coverage audit
│   └── safety.py               # Safety filter & text sanitization
├── adapters/
│   └── vision_adapter.py       # Gemini, HuggingFace & Synthetic vision adapters
├── components/
│   ├── observation_form.py     # Field context & image upload form
│   ├── triage_display.py       # Styled confidence cards & triage output
│   ├── safety_checklist.py     # Non-chemical action protocol checklist
│   ├── case_journal.py         # Historical timeline & status logger
│   └── analytics.py            # Plotly agricultural insights
├── sample_data/
│   └── seed_db.py              # Demo database generator
└── tests/
    ├── test_image_checker.py   # Blur, darkness & coverage tests
    ├── test_safety.py          # Safety filter & disclaimer tests
    ├── test_confidence.py      # Triage confidence bound tests
    └── test_journal.py         # Privacy opt-in retention tests
```

---

## 🛡️ Safety & Ethical Principles

CropCare provides visual triage based on observed signs and user input. It **never provides official agricultural diagnoses or chemical prescriptions**. Always consult a local agricultural extension office, certified agronomist, or plant pathology laboratory before taking management actions.
