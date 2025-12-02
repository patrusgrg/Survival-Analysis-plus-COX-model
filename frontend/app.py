"""
Streamlit Frontend for Survival Analysis
Interactive UI for patient risk prediction
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Survival Analysis - Heart Disease Predictor",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
    <style>
    .metric-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .risk-high {
        color: #d62828;
        font-weight: bold;
    }
    .risk-medium {
        color: #f77f00;
        font-weight: bold;
    }
    .risk-low {
        color: #06a77d;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("🏥 Heart Disease Survival Predictor")
st.markdown("### Cox Proportional Hazards Model for Personalized Risk Assessment")

# Sidebar configuration
st.sidebar.header("⚙️ Configuration")

API_URL = st.sidebar.text_input(
    "API Base URL",
    value="http://localhost:8000",
    help="Enter the FastAPI backend URL"
)

# Check API health
try:
    health_response = requests.get(f"{API_URL}/health", timeout=5)
    api_status = health_response.json()["status"]
    st.sidebar.success(f"✅ API Status: {api_status}")
except Exception as e:
    st.sidebar.error(f"❌ API Connection Error: {str(e)}")
    api_status = "disconnected"

st.sidebar.divider()

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📋 Patient Information")
    
    # Create input form
    with st.form("patient_form"):
        col_a, col_b = st.columns(2)
        
        with col_a:
            patient_age = st.number_input("Age (years)", min_value=18, max_value=100, value=55)
            sex = st.selectbox("Sex", options=[0, 1], format_func=lambda x: "Male" if x == 0 else "Female")
            chest_pain = st.selectbox("Chest Pain Type", options=[0, 1, 2, 3], 
                                     format_func=lambda x: ["Typical Angina", "Atypical Angina", "Non-anginal Pain", "Asymptomatic"][x])
            resting_bp = st.number_input("Resting Blood Pressure (mmHg)", min_value=80, max_value=200, value=140)
            cholesterol = st.number_input("Cholesterol (mg/dL)", min_value=0, max_value=400, value=200)
        
        with col_b:
            max_hr = st.number_input("Max Heart Rate (bpm)", min_value=60, max_value=220, value=140)
            fasting_bs = st.selectbox("Fasting Blood Sugar > 120 mg/dL", options=[0, 1],
                                     format_func=lambda x: "No" if x == 0 else "Yes")
            resting_ecg = st.selectbox("Resting ECG", options=[0, 1, 2],
                                      format_func=lambda x: ["Normal", "ST-T Abnormality", "LVH"][x])
            exercise_angina = st.selectbox("Exercise-Induced Angina", options=[0, 1],
                                          format_func=lambda x: "No" if x == 0 else "Yes")
            oldpeak = st.number_input("ST Depression (Oldpeak)", min_value=-3.0, max_value=7.0, value=1.0)
            st_slope = st.selectbox("ST Slope", options=[0, 1, 2],
                                   format_func=lambda x: ["Downsloping", "Flat", "Upsloping"][x])
        
        submit_button = st.form_submit_button("🔮 Predict Survival Risk", use_container_width=True)

with col2:
    st.header("📊 Quick Stats")
    st.metric("Dataset Samples", "918")
    st.metric("Event Rate", "55.4%")
    st.metric("Model C-Index", "0.85+")

# Handle prediction
if submit_button:
    if api_status != "disconnected":
        st.divider()
        st.header("🎯 Prediction Results")
        
        # Prepare patient data
        patient_data = {
            "time": patient_age,
            "sex": sex,
            "chest_pain_type": chest_pain,
            "resting_bp": resting_bp,
            "cholesterol": cholesterol,
            "fasting_bs": fasting_bs,
            "resting_ecg": resting_ecg,
            "max_hr": max_hr,
            "exercise_angina": exercise_angina,
            "oldpeak": oldpeak,
            "st_slope": st_slope
        }
        
        try:
            # Make API request
            response = requests.post(
                f"{API_URL}/predict",
                json=patient_data,
                timeout=10
            )
            
            if response.status_code == 200:
                prediction = response.json()
                
                # Display results
                col1_result, col2_result = st.columns(2)
                
                with col1_result:
                    st.subheader("Risk Assessment")
                    
                    hazard_ratio = prediction["hazard_ratio"]
                    risk_score = prediction["risk_score"]
                    
                    # Risk score with color coding
                    if "High" in risk_score:
                        st.markdown(f'<p class="risk-high">{risk_score}</p>', unsafe_allow_html=True)
                        st.warning("⚠️ High risk - Immediate medical consultation recommended")
                    elif "Medium" in risk_score:
                        st.markdown(f'<p class="risk-medium">{risk_score}</p>', unsafe_allow_html=True)
                        st.info("ℹ️ Moderate risk - Regular follow-up recommended")
                    else:
                        st.markdown(f'<p class="risk-low">{risk_score}</p>', unsafe_allow_html=True)
                        st.success("✅ Low risk - Continue routine screening")
                    
                    # Hazard ratio
                    st.metric("Hazard Ratio (Risk Score)", f"{hazard_ratio:.3f}")
                    
                    # Interpretation
                    st.caption("⚡ Interpretation: HR > 1 indicates increased risk")
                
                with col2_result:
                    st.subheader("Survival Prognosis")
                    
                    median_survival = prediction.get("median_survival_age", patient_age + 20)
                    st.metric(
                        "Median Survival Age",
                        f"{median_survival:.1f} years",
                        delta=f"+{median_survival - patient_age:.1f} years from now"
                    )
                    
                    # Survival probabilities
                    st.subheader("Survival Probabilities")
                    survival_probs = prediction.get("survival_probabilities", {})
                    
                    for age, prob in sorted(survival_probs.items()):
                        years_ahead = age - patient_age
                        col_a, col_b = st.columns([1, 2])
                        with col_a:
                            st.write(f"**In {years_ahead:.0f} years**")
                        with col_b:
                            st.progress(prob, text=f"{prob:.1%}")
                
                # Visualization
                st.divider()
                st.subheader("📈 Risk Profile")
                
                col_viz1, col_viz2 = st.columns(2)
                
                with col_viz1:
                    # Risk gauge
                    fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(projection='polar'))
                    
                    # Create gauge
                    theta = np.linspace(0, np.pi, 100)
                    r = np.ones_like(theta)
                    
                    # Color zones
                    low_theta = np.linspace(0, np.pi/3, 100)
                    med_theta = np.linspace(np.pi/3, 2*np.pi/3, 100)
                    high_theta = np.linspace(2*np.pi/3, np.pi, 100)
                    
                    ax.plot(low_theta, np.ones_like(low_theta), color='green', linewidth=10, label='Low')
                    ax.plot(med_theta, np.ones_like(med_theta), color='orange', linewidth=10, label='Medium')
                    ax.plot(high_theta, np.ones_like(high_theta), color='red', linewidth=10, label='High')
                    
                    # Needle
                    needle_angle = (hazard_ratio / 3.0) * np.pi  # Scale hazard ratio to gauge
                    needle_angle = min(needle_angle, np.pi)
                    ax.plot([needle_angle, needle_angle], [0, 1], 'k-', linewidth=3)
                    ax.plot(needle_angle, 1, 'ko', markersize=10)
                    
                    ax.set_ylim(0, 1.3)
                    ax.set_theta_offset(np.pi)
                    ax.set_theta_direction(-1)
                    ax.set_xticks(np.linspace(0, np.pi, 4))
                    ax.set_xticklabels(['High', 'Medium', 'Low', 'Very Low'])
                    ax.remove()
                    
                    st.pyplot(fig)
                
                with col_viz2:
                    # Patient characteristics radar
                    characteristics = {
                        'Age': patient_age / 100,
                        'Heart Rate': max_hr / 220,
                        'Blood Pressure': resting_bp / 200,
                        'Cholesterol': cholesterol / 300,
                        'ST Depression': oldpeak / 7
                    }
                    
                    fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(projection='polar'))
                    
                    categories = list(characteristics.keys())
                    values = list(characteristics.values())
                    values += values[:1]
                    
                    angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
                    angles += angles[:1]
                    
                    ax.plot(angles, values, 'o-', linewidth=2, color='steelblue', label='Patient')
                    ax.fill(angles, values, alpha=0.25, color='steelblue')
                    ax.set_xticks(angles[:-1])
                    ax.set_xticklabels(categories)
                    ax.set_ylim(0, 1)
                    ax.grid(True)
                    
                    st.pyplot(fig)
                
                # Additional information
                st.divider()
                st.subheader("ℹ️ About This Prediction")
                
                col_info1, col_info2 = st.columns(2)
                
                with col_info1:
                    st.info("""
                    **Model Information**
                    - Type: Cox Proportional Hazards
                    - Training Set: 734 patients
                    - C-Index: ~0.85
                    - Features: 11 clinical variables
                    """)
                
                with col_info2:
                    st.warning("""
                    **Disclaimer**
                    - This prediction is for informational purposes only
                    - Not a substitute for professional medical advice
                    - Consult healthcare providers for medical decisions
                    - Use alongside clinical judgment and other tests
                    """)
            
            else:
                st.error(f"❌ Prediction failed: {response.status_code}")
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    else:
        st.error("❌ Cannot make prediction - API is not connected. Please check the configuration.")

# Footer
st.divider()
st.markdown("""
---
**Survival Analysis + Cox Proportional Hazards Model**  
*Built with Streamlit, FastAPI, and lifelines*  
Dataset: Heart Failure Dataset from Kaggle
""")
