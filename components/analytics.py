"""
Analytics & Insights Component for CropCare
Displays interactive Plotly charts for issue distributions, crop breakdowns,
case outcomes, and temporal trends using database data.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any
from database import get_all_cases


def render_analytics():
    """
    Renders Plotly visualizations for agricultural student exploration.
    """
    st.markdown("## 📊 Agricultural Health Analytics & Dashboard")
    st.caption("Explore patterns across crop types, weather conditions, symptom co-occurrences, and case outcomes.")

    cases = get_all_cases()

    if not cases:
        st.info("No records in database. Please generate sample data or record cases to view analytics.")
        return

    df = pd.DataFrame(cases)

    # Top Summary Metrics Cards
    total_cases = len(df)
    under_obs = len(df[df['status'] == 'Under Observation'])
    resolved = len(df[df['status'] == 'Resolved'])
    confirmed = len(df[df['status'] == 'Confirmed Issue'])

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Observations", total_cases)
    m2.metric("Under Observation", under_obs)
    m3.metric("Resolved Cases", resolved)
    m4.metric("Confirmed Issues", confirmed)

    st.markdown("---")

    # Chart Row 1: Issue Distribution & Crop Distribution
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### 🦠 Candidate Issue Category Frequency")
        issue_counts = df['top_issue_category'].value_counts().reset_index()
        issue_counts.columns = ['Issue Category', 'Count']
        
        fig_issue = px.bar(
            issue_counts,
            x='Count',
            y='Issue Category',
            orientation='h',
            color='Count',
            color_continuous_scale=['#86EFAC', '#2D5A27'],
            title="Frequency of Identified Candidate Issues"
        )
        fig_issue.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#1F2937"),
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_issue, use_container_width=True)

    with c2:
        st.markdown("#### 🌾 Crop Species Distribution")
        crop_counts = df['crop'].value_counts().reset_index()
        crop_counts.columns = ['Crop', 'Count']

        fig_crop = px.pie(
            crop_counts,
            names='Crop',
            values='Count',
            hole=0.4,
            color_discrete_sequence=['#2D5A27', '#4A7C59', '#D97706', '#86EFAC', '#F59E0B', '#10B981'],
            title="Observations by Crop Type"
        )
        fig_crop.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#1F2937"),
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_crop, use_container_width=True)

    st.markdown("---")

    # Chart Row 2: Weather Correlation & Case Outcome Breakdown
    c3, c4 = st.columns(2)

    with c3:
        st.markdown("#### 🌤️ Weather Context Breakdown")
        weather_counts = df['weather'].value_counts().reset_index()
        weather_counts.columns = ['Weather Condition', 'Count']

        fig_weather = px.bar(
            weather_counts,
            x='Weather Condition',
            y='Count',
            color='Weather Condition',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            title="Observations by Environmental Weather"
        )
        fig_weather.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#1F2937"),
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_weather, use_container_width=True)

    with c4:
        st.markdown("#### 📈 Case Resolution Outcomes")
        status_counts = df['status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']

        fig_status = px.pie(
            status_counts,
            names='Status',
            values='Count',
            color='Status',
            color_discrete_map={
                "Under Observation": "#F59E0B",
                "Confirmed Issue": "#EF4444",
                "Resolved": "#10B981",
                "Inconclusive": "#9CA3AF"
            },
            title="Final Status Outcomes"
        )
        fig_status.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#1F2937"),
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_status, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 📋 Data Summary Table")
    st.dataframe(
        df[['case_id', 'created_at', 'crop', 'confirmed_crop', 'weather', 'top_issue_category', 'confidence_score', 'status']],
        use_container_width=True
    )
