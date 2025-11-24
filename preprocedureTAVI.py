import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

# --------------------------
# Password Check
# --------------------------
def check_password():
    def password_entered():
        if st.session_state["password"] == "TAVI2025":  
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Incorrect password")
        return False
    else:
        return True

# --------------------------
# Page Config
# --------------------------
st.set_page_config(page_title="TAVI LOS Calculator", layout="wide")
if not check_password():
    st.stop() 

# --------------------------
# Default Patient Values
# --------------------------
DEFAULTS = {
    "age": 82,
    "sex": "Male",
    "bmi": 25.0,
    "cfs": 4,
    "care_needs": False,  # NEW VARIABLE
    "lvef": 55,
    "diabetes": False,
    "ckd": False,
    "copd": False,
    "af": False,
    "lbbb": False,
    "prior_cabg": False,
    "prior_pci": False,
    "prior_stroke": False,
    "pulm_hypertension": False,
    "approach": "Transfemoral",
}

# --------------------------
# Styling
# --------------------------
st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #140F4B;
    color: white;
}
[data-testid="stSidebar"] * {
    color: white !important;
}
div.stButton > button {
    background-color: #1010EB;
    color: white;
    border-radius: 12px;
    padding: 0.6em 1.2em;
    border: none;
    font-weight: bold;
}
div.stButton > button:hover {
    background-color: #005195;
    color: white;
}
.stRadio label, .stCheckbox label {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# --------------------------
# Header
# --------------------------
st.markdown(f"""
<div style="
    background: linear-gradient(90deg, #140F4B, #005195);
    padding: 1rem; border-radius: 10px; margin-bottom: 2rem;
    display: flex; align-items: center;
">
    <img src="https://s3.eu-north-1.amazonaws.com/cdn-site.mediaplanet.com/app/uploads/sites/42/2021/11/07145553/P3-Full-Medtronic-logo.png"
         style="height: 100px; margin-right: 1rem;" alt="Medtronic Logo">
    <h1 style="color: white; margin: 0; font-family: sans-serif;">
        🫀 TAVI Pre-Procedure Length of Stay Calculator
    </h1>
</div>
""", unsafe_allow_html=True)

# --------------------------
# Session State
# --------------------------
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Assessment"
for key, val in DEFAULTS.items():
    st.session_state.setdefault(key, val)

# --------------------------
# LOS Risk Model
# --------------------------
def calculate_los_risk(age, sex, bmi, diabetes, ckd, copd, af, lbbb, prior_cabg,
                       prior_pci, prior_stroke, lvef, pulm_hypertension,
                       cfs, approach, care_needs):
    score = 0
    contributing_factors = []

    # Age
    if age >= 85:
        score += 2; contributing_factors.append(("Age ≥85 years", 2))
    elif age >= 75:
        score += 1; contributing_factors.append(("Age 75-84 years", 1))

    # Sex
    if sex == "Female":
        score += 1; contributing_factors.append(("Female sex", 1))

    # BMI extremes
    if bmi < 20:
        score += 1; contributing_factors.append(("BMI <20 kg/m²", 1))
    elif bmi >= 35:
        score += 1; contributing_factors.append(("BMI ≥35 kg/m²", 1))

    # Comorbidities
    if diabetes: score += 1; contributing_factors.append(("Diabetes mellitus", 1))
    if ckd: score += 2; contributing_factors.append(("Chronic kidney disease", 2))
    if copd: score += 1; contributing_factors.append(("COPD/Chronic lung disease", 1))
    if af: score += 1; contributing_factors.append(("Atrial fibrillation", 1))
    if lbbb: score += 1; contributing_factors.append(("Left bundle branch block", 1))
    if prior_cabg: score += 1; contributing_factors.append(("Prior CABG", 1))
    if prior_pci: score += 1; contributing_factors.append(("Prior PCI", 1))
    if prior_stroke: score += 1; contributing_factors.append(("Previous stroke/TIA", 1))
    if pulm_hypertension: score += 1; contributing_factors.append(("Pulmonary hypertension", 1))

    # LVEF
    if lvef < 40:
        score += 2; contributing_factors.append(("LVEF <40%", 2))
    elif lvef < 50:
        score += 1; contributing_factors.append(("LVEF 40-49%", 1))

    # Frailty
    if cfs >= 7:
        score += 3; contributing_factors.append(("Clinical Frailty Score ≥7", 3))
    elif cfs >= 5:
        score += 2; contributing_factors.append(("Clinical Frailty Score 5-6", 2))
    elif cfs == 4:
        score += 1; contributing_factors.append(("Clinical Frailty Score 4", 1))

    # Approach
    if approach != "Transfemoral":
        score += 2; contributing_factors.append(("Non-transfemoral access", 2))

    # LOS category
    if score <= 4:
        category = "Low"; los_min, los_max = 0, 1; color_code = "#28a745"
    elif score <= 8:
        category = "Intermediate"; los_min, los_max = 1, 2; color_code = "#ffc107"
    elif score <= 12:
        category = "High"; los_min, los_max = 3, 5; color_code = "#fd7e14"
    else:
        category = "Very High"; los_min, los_max = 6, 10; color_code = "#dc3545"

    # NEW: Care needs → add 1 day
    if care_needs:
        los_min += 1
        los_max += 1
        contributing_factors.append(("Care needs (+1 day)", 0))

    return score, category, color_code, contributing_factors, los_min, los_max

# --------------------------
# Assessment Tab
# --------------------------
if st.session_state.active_tab == "Assessment":
    st.subheader("👤 Patient Demographics")
    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input("Age (years)", 50, 100, st.session_state.age, key="age")
        sex = st.radio("Sex", ("Male", "Female"), key="sex")
    with col2:
        bmi = st.number_input("BMI (kg/m²)", 15, 50, int(st.session_state.bmi), key="bmi")
    with col3:
        cfs = st.slider("Clinical Frailty Score", 1, 9, st.session_state.cfs, key="cfs")

    # NEW CARE NEEDS QUESTION
    st.subheader("🏡 Care Needs")
st.write("Does the patient have newly identified care needs, or an existing package of care?")
    care_needs = st.radio(
        "Does the patient have newly identified care needs or an existing package of care?",
        ("No", "Yes"),
        index=1 if st.session_state.care_needs else 0,
        key="care_needs"
    )

    st.subheader("💓 Cardiac Function")
    lvef = st.slider("LVEF (%)", 15, 70, st.session_state.lvef, key="lvef")

    st.subheader("🩺 Comorbidities")
    col1, col2, col3 = st.columns(3)
    with col1:
        diabetes = st.checkbox("Diabetes", key="diabetes")
        copd = st.checkbox("COPD", key="copd")
        af = st.checkbox("AF", key="af")
        lbbb = st.checkbox("LBBB", key="lbbb")
    with col2:
        ckd = st.checkbox("CKD", key="ckd")
        prior_cabg = st.checkbox("Prior CABG", key="prior_cabg")
        prior_pci = st.checkbox("Prior PCI", key="prior_pci")
    with col3:
        prior_stroke = st.checkbox("Stroke/TIA", key="prior_stroke")
        pulm_hypertension = st.checkbox("Pulmonary Hypertension", key="pulm_hypertension")

    st.subheader("🩻 Procedural Details")
    approach = st.radio("Planned TAVI Approach", (
        "Transfemoral", "Transapical", "Subclavian/Axillary", "Other"), key="approach")

    if st.button("🔮 Calculate Predicted Length of Stay", use_container_width=True):
        st.session_state.result = calculate_los_risk(
            st.session_state.age, st.session_state.sex, st.session_state.bmi,
            st.session_state.diabetes, st.session_state.ckd, st.session_state.copd,
            st.session_state.af, st.session_state.lbbb,
            st.session_state.prior_cabg, st.session_state.prior_pci,
            st.session_state.prior_stroke, st.session_state.lvef,
            st.session_state.pulm_hypertension, st.session_state.cfs,
            st.session_state.approach, st.session_state.care_needs
        )
        st.session_state.active_tab = "Results"
        st.rerun()

# --------------------------
# Results Tab
# --------------------------
if st.session_state.active_tab == "Results":
    if "result" in st.session_state:
        score, category, color_code, contributing_factors, los_min, los_max = st.session_state.result
        los = f"{los_min}–{los_max} days" if los_max != los_min else f"{los_min} day"

        st.markdown(f"""
        <div style="background: linear-gradient(90deg, {color_code}, #f8f9fa);
            padding:20px; border-radius:10px; color:white; text-align:center;">
            <h2>Risk Category: {category}</h2>
            <h3>Predicted Length of Stay: {los}</h3>
            <p>Total Risk Score: {score}/20</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("➕ New Patient Entry", use_container_width=True):
            for key, val in DEFAULTS.items(): st.session_state[key] = val
            st.session_state.pop("result", None)
            st.session_state.active_tab = "Assessment"
            st.rerun()

# --------------------------
# Disclaimer
# --------------------------
if st.session_state.active_tab == "Disclaimer":
    st.markdown("""
    ### ⚠️ Disclaimer
    This tool is for clinical decision support and should not replace clinical judgment.
    """)
