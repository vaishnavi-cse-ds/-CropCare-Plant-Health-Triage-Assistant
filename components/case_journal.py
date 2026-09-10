"""
Case Journal Component for CropCare
Displays stored observation cases, privacy status, confirmed crop confirmation,
status updates, and follow-up timeline logs.
"""

import streamlit as st
import base64
from io import BytesIO
from PIL import Image
from typing import List, Dict, Any
from database import (
    get_all_cases, get_case_by_id, update_case_status,
    get_case_logs, delete_case
)
from config import CROPS


def render_case_journal():
    """
    Renders historical case timeline, privacy retention status, and follow-up logger.
    """
    st.markdown("## 📔 Field Observation & Case Journal")
    st.caption("Track plant health progression over time with consent-based record keeping.")

    cases = get_all_cases()

    if not cases:
        st.info("No cases recorded yet. Submit an observation from the 'Triage Assistant' tab to start your journal!")
        return

    # Filter Controls
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        search_query = st.text_input("🔍 Search by Crop or Case ID", placeholder="e.g. Tomato or CASE-1234")
    with col_f2:
        status_filter = st.selectbox(
            "Filter by Status",
            options=["All", "Under Observation", "Confirmed Issue", "Resolved", "Inconclusive"]
        )

    # Filter records
    filtered_cases = cases
    if status_filter != "All":
        filtered_cases = [c for c in filtered_cases if c["status"] == status_filter]
    if search_query.strip():
        q = search_query.lower().strip()
        filtered_cases = [
            c for c in filtered_cases
            if q in c["case_id"].lower() or q in c["crop"].lower() or q in (c.get("confirmed_crop") or "").lower()
        ]

    st.markdown(f"**Showing {len(filtered_cases)} case(s)**")

    # Display list of case accordions
    for case in filtered_cases:
        case_id = case["case_id"]
        crop = case["crop"]
        confirmed_crop = case.get("confirmed_crop") or crop
        status = case["status"]
        created_at = case["created_at"][:16].replace("T", " ")
        top_issue = case["top_issue_category"] or "Unclassified"
        confidence_pct = int(case["confidence_score"] * 100) if case.get("confidence_score") else 0
        photo_retained = bool(case.get("photo_retained", 0))

        # Status badge color
        status_colors = {
            "Under Observation": "🟡",
            "Confirmed Issue": "🔴",
            "Resolved": "🟢",
            "Inconclusive": "⚪"
        }
        icon = status_colors.get(status, "🔵")

        header_str = f"{icon} `{case_id}` | **{confirmed_crop}** ({crop}) — {top_issue} [{status}] ({created_at})"
        
        with st.expander(header_str, expanded=False):
            c_col1, c_col2 = st.columns([1, 1])

            with c_col1:
                st.markdown(f"**Target Crop**: {crop}")
                st.markdown(f"**User Confirmed Crop**: `{confirmed_crop}`")
                st.markdown(f"**Growth Stage**: {case.get('plant_stage')}")
                st.markdown(f"**Environment**: {case.get('location_type')}")
                st.markdown(f"**Weather / Irrigation**: {case.get('weather')} / {case.get('watering')}")
                st.markdown(f"**Affected Area**: {case.get('affected_area')}")
                st.markdown(f"**Symptoms**: {', '.join(case.get('symptoms', []))}")
                st.markdown(f"**Top Triage Category**: {top_issue} ({confidence_pct}% visual match)")

                if case.get("user_notes"):
                    st.info(f"📝 **Field Note**: {case['user_notes']}")

            with c_col2:
                st.markdown("#### 🔒 Photo Privacy Status")
                if photo_retained and case.get("image_base64"):
                    st.success("📷 Retained photo (Opt-in consented)")
                    try:
                        img_bytes = base64.b64decode(case["image_base64"])
                        image = Image.open(BytesIO(img_bytes))
                        st.image(image, caption=f"Case Photo ({case_id})", use_container_width=True)
                    except Exception as e:
                        st.error("Error loading stored image payload.")
                else:
                    st.info("🛡️ Photo not stored in database (Privacy opt-out mode)")

            st.markdown("---")
            st.markdown("#### ⏳ Case Follow-up & Timeline History")
            
            logs = get_case_logs(case_id)
            for log in logs:
                l_time = log["created_at"][:16].replace("T", " ")
                st.markdown(f"• `{l_time}` | **Status**: `{log['status_update']}` — {log['observation_notes']}")

            # Update Form
            st.markdown("##### ✏️ Add Follow-up Log / Update Status")
            with st.form(key=f"update_form_{case_id}"):
                u_col1, u_col2 = st.columns(2)
                with u_col1:
                    new_confirmed_crop = st.selectbox(
                        "Confirm / Update Crop Species",
                        options=CROPS,
                        index=CROPS.index(crop) if crop in CROPS else 0,
                        key=f"crop_select_{case_id}"
                    )
                    new_status = st.selectbox(
                        "Update Case Status",
                        options=["Under Observation", "Confirmed Issue", "Resolved", "Inconclusive"],
                        index=["Under Observation", "Confirmed Issue", "Resolved", "Inconclusive"].index(status),
                        key=f"status_select_{case_id}"
                    )
                with u_col2:
                    new_log_notes = st.text_area(
                        "Follow-up Observation Notes",
                        placeholder="e.g. Pruned affected leaves. New emerging leaves look healthy after 4 days.",
                        key=f"log_notes_{case_id}"
                    )

                submit_update = st.form_submit_button("Update Case Record")
                if submit_update:
                    update_case_status(
                        case_id=case_id,
                        new_status=new_status,
                        notes=new_log_notes or f"Updated status to {new_status}.",
                        confirmed_crop=new_confirmed_crop
                    )
                    st.success(f"Case {case_id} updated successfully!")
                    st.rerun()

            # Delete case button
            if st.button(f"🗑️ Delete Case {case_id}", key=f"del_{case_id}"):
                delete_case(case_id)
                st.warning(f"Case {case_id} deleted.")
                st.rerun()
