import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

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
    "careneeds": "No",
    "bmi": 25.0,
    "cfs": 4,
    "lvef": 55,
    "diabetes": False,
    "ckd": False,
    "copd": False,
    "af": False,
    "lbbb": False,
    "rbbb": False,
    "prior_cabg": False,
    "prior_pci": False,
    "prior_stroke": False,
    "pulm_hypertension": False,
    "approach": "Transfemoral",
    "include_procedural": False,
    "procedure_duration": 45,
    "contrast_load": 150,
    "vascular_complication": False,
    "valve_type": "Balloon-Expandable",
}

# --------------------------
# Custom Global Styling
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
    color: black !important;
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
# Session state
# --------------------------
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Assessment"

for key, val in DEFAULTS.items():
    st.session_state.setdefault(key, val)

# --------------------------
# Risk Score Calculation
# --------------------------
def calculate_los_risk(age, sex, careneeds, bmi, diabetes, ckd, copd, af, lbbb, rbbb, prior_cabg,
                       prior_pci, prior_stroke, lvef, pulm_hypertension,
                       cfs, approach, include_procedural=False, procedure_duration=None,
                       contrast_load=None, vascular_complication=False, valve_type=None):
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

    # Care Needs
    if careneeds == "Yes":
        score += 1; contributing_factors.append(("Care needs", 1))

    # BMI extremes
    if bmi < 20:
        score += 1; contributing_factors.append(("BMI <20 kg/m²", 1))
    elif bmi >= 35:
        score += 1; contributing_factors.append(("BMI ≥35 kg/m²", 1))

    # Comorbidities
    if diabetes:
        score += 1; contributing_factors.append(("Diabetes mellitus", 1))
    if ckd:
        score += 2; contributing_factors.append(("Chronic kidney disease", 2))
    if copd:
        score += 1; contributing_factors.append(("COPD/Chronic lung disease", 1))
    if af:
        score += 1; contributing_factors.append(("Atrial fibrillation", 1))
    if lbbb:
        score += 1; contributing_factors.append(("Left bundle branch block (LBBB)", 1))
    if rbbb:
        score += 1; contributing_factors.append(("Right bundle branch block (RBBB)", 1))
    if prior_cabg:
        score += 1; contributing_factors.append(("Prior CABG", 1))
    if prior_pci:
        score += 1; contributing_factors.append(("Prior PCI", 1))
    if prior_stroke:
        score += 1; contributing_factors.append(("Previous stroke/TIA", 1))
    if pulm_hypertension:
        score += 1; contributing_factors.append(("Pulmonary hypertension", 1))

    # Cardiac function
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

    # Procedural Factors (if included)
    if include_procedural:
        # Procedure Duration
        if procedure_duration > 75:
            score += 2; contributing_factors.append(("Procedure duration >75 min", 2))
        elif procedure_duration > 60:
            score += 1; contributing_factors.append(("Procedure duration >60 min", 1))
        
        # Contrast Load
        if contrast_load > 250:
            score += 2; contributing_factors.append(("Contrast load >250 ml", 2))
        elif contrast_load > 200:
            score += 1; contributing_factors.append(("Contrast load >200 ml", 1))
        
        # Vascular Complication
        if vascular_complication:
            score += 2; contributing_factors.append(("Vascular complication", 2))
        
        # Valve Type
        if valve_type == "Self-Expanding":
            score += 1; contributing_factors.append(("Self-expanding valve", 1))

    # ✅ Updated LOS categories (average ~1 day)
    if score <= 4:
        category = "Low"; los = "0–1 days"; los_min, los_max = 0, 1
        color, color_code = "🟢", "#28a745"
    elif score <= 8:
        category = "Intermediate"; los = "1–2 days"; los_min, los_max = 1, 2
        color, color_code = "🟡", "#ffc107"
    elif score <= 12:
        category = "High"; los = "3–5 days"; los_min, los_max = 3, 5
        color, color_code = "🟠", "#fd7e14"
    else:
        category = "Very High"; los = ">5 days"; los_min, los_max = 6, 10
        color, color_code = "🔴", "#dc3545"

    return score, category, los, color, color_code, contributing_factors, los_min, los_max

# --------------------------
# Graphical Functions
# --------------------------
def create_risk_gauge(score, category, color_code):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': f"<b>Risk Score</b><br><span style='font-size:0.8em'>{category} Risk</span>"},
        gauge={
            'axis': {'range': [None, 27]},
            'bar': {'color': color_code, 'thickness': 0.3},
            'steps': [
                {'range': [0, 4], 'color': '#d4edda'},
                {'range': [4, 8], 'color': '#fff3cd'},
                {'range': [8, 12], 'color': '#f8d7da'},
                {'range': [12, 27], 'color': '#f5c6cb'}
            ],
            'threshold': {'line': {'color': color_code, 'width': 4}, 'value': score}
        }
    ))
    fig.update_layout(height=300, paper_bgcolor="white")
    return fig

def create_los_distribution(los_min, los_max, category, color_code):
    days = list(range(0, 11))
    probabilities = [0] * len(days)
    if category == "Low":
        probabilities[0] = 0.4; probabilities[1] = 0.6
    elif category == "Intermediate":
        probabilities[1] = 0.4; probabilities[2] = 0.6
    elif category == "High":
        probabilities[3] = 0.3; probabilities[4] = 0.4; probabilities[5] = 0.3
    else:
        probabilities[6] = 0.3; probabilities[7] = 0.3; probabilities[8] = 0.2; probabilities[9] = 0.2

    fig = go.Figure(go.Bar(
        x=days, y=probabilities,
        marker_color=color_code,
        text=[f"{p:.0%}" if p > 0 else "" for p in probabilities],
        textposition='auto'
    ))
    fig.update_layout(
        title=f"Expected Length of Stay Distribution ({category})",
        xaxis_title="Days", yaxis_title="Probability",
        yaxis=dict(tickformat='.0%'), height=300, showlegend=False, paper_bgcolor="white"
    )
    return fig

def create_risk_factors_chart(contributing_factors):
    if not contributing_factors: return None
    df = pd.DataFrame(contributing_factors, columns=['Factor', 'Points']).sort_values('Points')
    fig = px.bar(df, x='Points', y='Factor', orientation='h', color='Points',
                 color_continuous_scale='Reds', title="Risk Factors Contributing to Score")
    fig.update_traces(texttemplate='%{x}', textposition='outside')
    fig.update_layout(height=max(300, len(df) * 40), paper_bgcolor="white")
    return fig

def create_timeline_visual(los_min, los_max):
    procedure_date = datetime.now().date()
    discharge_earliest = procedure_date + timedelta(days=los_min)
    discharge_latest = procedure_date + timedelta(days=los_max)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[procedure_date], y=[1], mode='markers+text',
        marker=dict(size=20, color='#140F4B', symbol='star'),
        text=['TAVI Procedure'], textposition="top center", showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=[discharge_earliest, discharge_latest], y=[1, 1],
        mode='markers+lines+text', line=dict(color='#005195', width=8),
        marker=dict(size=15, color='#005195'),
        text=[f'Earliest {discharge_earliest.strftime("%b %d")}',
              f'Latest {discharge_latest.strftime("%b %d")}'],
        textposition="top center", showlegend=False
    ))
    fig.update_layout(
        title="Procedure and Expected Discharge Timeline",
        xaxis_title="Date", yaxis=dict(visible=False, range=[0.5, 1.5]),
        height=250, paper_bgcolor="white"
    )
    return fig

# --------------------------
# Tabs
# --------------------------
tabs = ["Assessment", "Results", "Disclaimer"]
selected_tab = st.session_state.active_tab

if selected_tab == "Assessment":
    st.subheader("👤 Patient Demographics")
    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input("Age (years)", 50, 100, st.session_state.age, key="age")
        sex = st.radio("Sex", ("Male", "Female"),
                       index=0 if st.session_state.sex == "Male" else 1, key="sex")
        careneeds = st.radio("Does this patient have newly identified care needs or an existing package of care?", ("Yes", "No"),
                        index=0 if st.session_state.careneeds == "No" else 1, key="careneeds")
    with col2:
        bmi = st.number_input("BMI (kg/m²)", min_value=15, max_value=50,
                        value=int(st.session_state.bmi), step=1, key="bmi")
        st.caption(f"BMI Category: {'Underweight' if bmi<18.5 else 'Normal' if bmi<25 else 'Overweight' if bmi<30 else 'Obese'}")
    with col3:
        cfs = st.slider("Clinical Frailty Score", 1, 9, st.session_state.cfs, key="cfs")
        st.caption(f"Frailty Status: {'Fit' if cfs<=3 else 'Vulnerable to mildly frail' if cfs<=6 else 'Severely frail'}")

    st.subheader("💓 Cardiac Function")
    lvef = st.slider("LVEF (%)", 15, 70, st.session_state.lvef, key="lvef")
    st.caption(f"LVEF Classification: {'Reduced' if lvef<40 else 'Mildly reduced' if lvef<50 else 'Normal'}")

    st.subheader("🩺 Comorbidities")
    col1, col2, col3 = st.columns(3)
    with col1:
        diabetes = st.checkbox("Diabetes Mellitus", value=st.session_state.diabetes, key="diabetes")
        copd = st.checkbox("COPD / Chronic Lung Disease", value=st.session_state.copd, key="copd")
        af = st.checkbox("Atrial Fibrillation", value=st.session_state.af, key="af")
        lbbb = st.checkbox("Left bundle branch block (LBBB)", value=st.session_state.lbbb, key="lbbb")
        rbbb = st.checkbox("Right bundle branch block (RBBB)", value=st.session_state.rbbb, key="rbbb")
    with col2:
        ckd = st.checkbox("Chronic Kidney Disease (Stage 3–5)", value=st.session_state.ckd, key="ckd")
        prior_cabg = st.checkbox("Prior CABG", value=st.session_state.prior_cabg, key="prior_cabg")
        prior_pci = st.checkbox("Prior PCI", value=st.session_state.prior_pci, key="prior_pci")
    with col3:
        prior_stroke = st.checkbox("Previous Stroke/TIA", value=st.session_state.prior_stroke, key="prior_stroke")
        pulm_hypertension = st.checkbox("Pulmonary Hypertension", value=st.session_state.pulm_hypertension, key="pulm_hypertension")

    st.subheader("⚙️ Procedural Factors (Optional)")
    include_procedural = st.checkbox("Include procedural factors in risk assessment", 
                                    value=st.session_state.include_procedural, key="include_procedural")
    
    if include_procedural:
        approach = st.radio("Planned TAVI Approach",
                            ("Transfemoral", "Transapical", "Subclavian/Axillary", "Other"),
                            index=["Transfemoral", "Transapical", "Subclavian/Axillary", "Other"].index(st.session_state.approach),
                            key="approach")
        
        col1, col2 = st.columns(2)
        with col1:
            procedure_duration = st.slider("Procedure Duration (minutes)", 
                                          min_value=20, max_value=100, 
                                          value=st.session_state.procedure_duration,
                                          step=5,
                                          format="%d min" if st.session_state.procedure_duration < 90 else ">90 min",
                                          key="procedure_duration")
            if procedure_duration >= 90:
                st.caption("Duration: >90 minutes")
            
            contrast_load = st.slider("Contrast Load (ml)", 
                                     min_value=50, max_value=320, 
                                     value=st.session_state.contrast_load,
                                     step=10,
                                     key="contrast_load")
            if contrast_load < 80:
                st.caption("Load: <80 ml")
            elif contrast_load > 300:
                st.caption("Load: >300 ml")
        
        with col2:
            vascular_complication = st.checkbox("Presence of Vascular Complication", 
                                               value=st.session_state.vascular_complication, 
                                               key="vascular_complication")
            
            valve_type = st.radio("Valve Type", 
                                 ("Balloon-Expandable", "Self-Expanding"),
                                 index=0 if st.session_state.valve_type == "Balloon-Expandable" else 1,
                                 key="valve_type")
    else:
        # Set default approach when procedural factors are not included
        approach = "Transfemoral"

    if st.button("🔮 Calculate Predicted Length of Stay", use_container_width=True):
        if include_procedural:
            st.session_state.result = calculate_los_risk(
                st.session_state.age, st.session_state.sex, st.session_state.careneeds, st.session_state.bmi,
                st.session_state.diabetes, st.session_state.ckd, st.session_state.copd,
                st.session_state.af, st.session_state.lbbb, st.session_state.rbbb,
                st.session_state.prior_cabg, st.session_state.prior_pci,
                st.session_state.prior_stroke, st.session_state.lvef,
                st.session_state.pulm_hypertension, st.session_state.cfs,
                st.session_state.approach, include_procedural=True,
                procedure_duration=st.session_state.procedure_duration,
                contrast_load=st.session_state.contrast_load,
                vascular_complication=st.session_state.vascular_complication,
                valve_type=st.session_state.valve_type
            )
        else:
            st.session_state.result = calculate_los_risk(
                st.session_state.age, st.session_state.sex, st.session_state.careneeds, st.session_state.bmi,
                st.session_state.diabetes, st.session_state.ckd, st.session_state.copd,
                st.session_state.af, st.session_state.lbbb, st.session_state.rbbb,
                st.session_state.prior_cabg, st.session_state.prior_pci,
                st.session_state.prior_stroke, st.session_state.lvef,
                st.session_state.pulm_hypertension, st.session_state.cfs,
                st.session_state.approach
            )
        st.session_state.active_tab = "Results"
        st.rerun()

elif selected_tab == "Results":
    if "result" in st.session_state:
        score, category, los, color, color_code, contributing_factors, los_min, los_max = st.session_state.result
        max_score = 27 if st.session_state.include_procedural else 20
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, {color_code}, #f8f9fa);
            padding:20px; border-radius:10px; color:white; text-align:center;">
            <h2>Risk Category: {color} {category}</h2>
            <h3>Predicted Length of Stay: {los}</h3>
            <p>Total Risk Score: {score}/{max_score}</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(create_risk_gauge(score, category, color_code), use_container_width=True)
        with col2:
            st.plotly_chart(create_los_distribution(los_min, los_max, category, color_code), use_container_width=True)

        st.plotly_chart(create_timeline_visual(los_min, los_max), use_container_width=True)

        if contributing_factors:
            st.plotly_chart(create_risk_factors_chart(contributing_factors), use_container_width=True)
            with st.expander("📋 Detailed Risk Factors", expanded=False):
                st.dataframe(pd.DataFrame(contributing_factors, columns=['Risk Factor', 'Points']), use_container_width=True)
        else:
            st.success("✅ Excellent prognosis! No significant risk factors identified.")

        if st.button("➕ New Patient Entry", use_container_width=True):
            for key, val in DEFAULTS.items():
                st.session_state[key] = val
            st.session_state.pop("result", None)
            st.session_state.active_tab = "Assessment"
            st.rerun()
    else:
        st.warning("Please complete the patient assessment and calculate risk first.")
        if st.button("← Go to Assessment", use_container_width=True):
            st.session_state.active_tab = "Assessment"
            st.rerun()

# --------------------------
# Disclaimer Tab
# --------------------------
elif selected_tab == "Disclaimer":
    st.markdown("""
    ### ⚠️ Disclaimer
    This calculator is a **clinical decision-support tool** intended for use by healthcare professionals.
    It is **not a substitute for clinical judgment**.

    - The risk estimates are based on common predictors of prolonged hospital stay following TAVI.
    - Actual outcomes will vary depending on individual patient factors and peri-procedural events.
    - Always integrate these results with patient-specific clinical context.

    © 2025 Medtronic — For professional use only.
    """)

    if st.button("⬅️ Back to Assessment", use_container_width=True):
        st.session_state.active_tab = "Assessment"
        st.rerun()
