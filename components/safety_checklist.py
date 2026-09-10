"""
Safe Next-Step Checklist Component for CropCare
Focuses strictly on non-chemical cultural, physical, monitoring, and hygiene practices,
plus local expert referral instructions.
"""

import streamlit as st
from typing import List, Dict, Any


def render_safety_checklist(triage_data: Dict[str, Any]):
    """
    Renders interactive checklist of safe cultural practices.
    """
    st.markdown("## 🛡️ Safe Field Management & Action Checklist")
    st.caption(
        "Focus on non-chemical cultural controls, physical isolation, hygiene, "
        "and expert confirmation."
    )

    steps = triage_data.get("safe_next_steps", [
        "Isolate affected plants or remove infected lower leaves cleanly.",
        "Avoid overhead irrigation to keep foliage dry.",
        "Sanitize shears and tools with alcohol or 10% bleach solution.",
        "Document symptoms daily to track progression.",
        "Contact your local agricultural extension service or certified agronomist."
    ])

    st.markdown("#### 📝 Interactive Protocol Checklist")
    
    completed_count = 0
    for idx, step in enumerate(steps):
        is_checked = st.checkbox(f"{step}", key=f"safe_step_{idx}")
        if is_checked:
            completed_count += 1

    st.progress(completed_count / max(len(steps), 1), text=f"Completed {completed_count} of {len(steps)} safe management steps.")

    st.markdown("---")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### 🌾 How to Contact a Local Agriculture Expert")
        st.markdown(
            """
            When taking samples to a local agricultural extension office or plant diagnostics lab:
            1. **Collect Fresh Samples**: Cut a branch/leaf showing both healthy and diseased tissue boundaries.
            2. **Keep Dry & Cool**: Place in a paper bag or sealed plastic bag with paper towels (avoid direct heat).
            3. **Bring Field Notes**: Bring your CropCare Observation log & photos.
            """
        )

    with col2:
        st.markdown(
            """
            <div style="
                background-color: #FEF3C7;
                border: 1px solid #FDE68A;
                padding: 14px;
                border-radius: 8px;
                text-align: center;
            ">
                <h4 style="color: #92400E; margin-top: 0;">🚫 Pesticide Safety Reminder</h4>
                <p style="color: #78350F; font-size: 0.88rem; margin-bottom: 0;">
                    Unchecked chemical application can harm beneficial soil microbes, natural predators, and water sources.
                    Always get an official diagnostic lab test first!
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
