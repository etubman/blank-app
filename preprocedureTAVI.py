import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

# --------------------------
# Page Config
# --------------------------
st.set_page_config(page_title="TAVI LOS Calculator", layout="wide")

# --------------------------
# Default Patient Values
# --------------------------
DEFAULTS = {
    "age": 82,
    "sex": "Male",
    "bmi": 25.0,     # ✅ keep only one BMI default
    "cfs": 4,
    "lvef": 55,
    "diabetes": False,
    "ckd": False,
    "copd": False,
    "af": False,
    "prior_cabg": False,
    "prior_pci": False,
    "prior_stroke": False,
    "pulm_hypertension": False,
    "approach": "Transfemoral",
}

# --------------------------
# Custom Global Styling (Medtronic colors)
# --------------------------
st.markdown("""
<style>
/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #140F4B;
    color: white;
}
[data-testid="stSidebar"] * {
    color: white !important;
}

/* Buttons */
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

/* Radio & Checkbox labels */
.stRadio label, .stCheckbox label {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# --------------------------
# Header with Medtronic Branding
# --------------------------
st.markdown(f"""
<div style="
    background: linear-gradient(90deg, #140F4B, #005195);
    padding: 1rem; border-radius: 10px; margin-bottom: 2rem;
    display: flex; align-items: center;
">
    <img src="https://s3.eu-north-1.amazonaws.com/cdn-site.mediaplanet.com/app/uploads/sites/42/2021/11/07145553/P3-Full-Medtronic-logo.png"
         style="height: 100px; margin-right: 1rem;" alt="Medtronic Logo">
    <div>
        <h1 style="color: white; margin: 0; font-family: sans-serif;">
            🫀 TAVI Pre-Procedure Length of Stay Calculator
        </h1>
        <p style="color: white; margin: 0; font-family: sans-serif;">
            Predict length of stay based on pre-procedural patient characteristics
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# --------------------------
# Initialize session state
# --------------------------
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Assessment"

for key, val in DEFAULTS.items():
    st.session_state.setdefault(key, val)

# --------------------------
# Function: Risk Score Calculation
# --------------------------
def calculate_los_risk(age, sex, bmi, diabetes, ckd, copd, af, prior_cabg, 
                       prior_pci, prior_stroke, lvef, pulm_hypertension, 
                       cfs, approach):
    score = 0
    contributing_factors = []

    # Age
    if age >= 85:
        score += 2
        contributing_factors.append(("Age ≥85 years", 2))
    elif age >= 75:
        score += 1
        contributing_factors.append(("Age 75-84 years", 1))

    # Sex
    if sex == "Female":
        score += 1
        contributing_factors.append(("Female sex", 1))

    # BMI extremes
    if bmi < 20:
        score += 1
        contributing_factors.append(("BMI <20 kg/m²", 1))
    elif bmi >= 35:
        score += 1
        contributing_factors.append(("BMI ≥35 kg/m²", 1))

    # Comorbidities
    if diabetes:
        score += 1
        contributing_factors.append(("Diabetes mellitus", 1))
    if ckd:
        score += 2
        contributing_factors.append(("Chronic kidney disease", 2))
    if copd:
        score += 1
        contributing_factors.append(("COPD/Chronic lung disease", 1))
    if af:
        score += 1
        contributing_factors.append(("Atrial fibrillation", 1))
    if prior_cabg:
        score += 1
        contributing_factors.append(("Prior CABG", 1))
    if prior_pci:
        score += 1
        contributing_factors.append(("Prior PCI", 1))
    if prior_stroke:
        score += 1
        contributing_factors.append(("Previous stroke/TIA", 1))
    if pulm_hypertension:
        score += 1
        contributing_factors.append(("Pulmonary hypertension", 1))

    # Cardiac function
    if lvef < 40:
        score += 2
        contributing_factors.append(("LVEF <40%", 2))
    elif lvef < 50:
        score += 1
        contributing_factors.append(("LVEF 40-49%", 1))

    # Frailty
    if cfs >= 7:
        score += 3
        contributing_factors.append(("Clinical Frailty Score ≥7", 3))
    elif cfs >= 5:
        score += 2
        contributing_factors.append(("Clinical Frailty Score 5-6", 2))
    elif cfs == 4:
        score += 1
        contributing_factors.append(("Clinical Frailty Score 4", 1))

    # Procedural approach
    if approach != "Transfemoral":
        score += 2
        contributing_factors.append(("Non-transfemoral access", 2))

    # Categorize risk
    if score <= 4:
        category = "Low"
        los = "2–3 days"
        los_min, los_max = 2, 3
        color = "🟢"
        color_code = "#28a745"
    elif score <= 8:
        category = "Intermediate"
        los = "4–6 days"
        los_min, los_max = 4, 6
        color = "🟡"
        color_code = "#ffc107"
    elif score <= 12:
        category = "High"
        los = "7–10 days"
        los_min, los_max = 7, 10
        color = "🟠"
        color_code = "#fd7e14"
    else:
        category = "Very High"
        los = ">10 days"
        los_min, los_max = 10, 15
        color = "🔴"
        color_code = "#dc3545"

    # ✅ Return all values needed downstream
    return score, category, los, color, color_code, contributing_factors, los_min, los_max

# --------------------------
# Graphical Functions
# --------------------------
def create_risk_gauge(score, category, color_code):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        title = {'text': f"<b>Risk Score</b><br><span style='font-size:0.8em'>{category} Risk</span>"},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [None, 20], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color_code, 'thickness': 0.3},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 4], 'color': '#d4edda'},
                {'range': [4, 8], 'color': '#fff3cd'},
                {'range': [8, 12], 'color': '#f8d7da'},
                {'range': [12, 20], 'color': '#f5c6cb'}
            ],
            'threshold': {
                'line': {'color': color_code, 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    fig.update_layout(height=300, font={'color': "darkblue", 'family': "Arial"}, paper_bgcolor="white")
    return fig

def create_los_distribution(los_min, los_max, category, color_code):
    days = list(range(1, 16))
    probabilities = [0] * 15
    if category == "Low":
        probabilities[1] = 0.4
        probabilities[2] = 0.6
    elif category == "Intermediate":
        probabilities[3] = 0.3
        probabilities[4] = 0.4
        probabilities[5] = 0.3
    elif category == "High":
        probabilities[6] = 0.2
        probabilities[7] = 0.3
        probabilities[8] = 0.3
        probabilities[9] = 0.2
    else:
        probabilities[9] = 0.2
        probabilities[10] = 0.3
        probabilities[11] = 0.3
        probabilities[12] = 0.2
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=days,
        y=probabilities,
        marker_color=color_code,
        name="Probability",
        text=[f"{p:.1%}" if p > 0 else "" for p in probabilities],
        textposition='auto',
    ))
    fig.update_layout(
        title=f"<b>Expected Length of Stay Distribution</b><br><span style='font-size:0.8em'>{category} Risk Category</span>",
        xaxis_title="Days",
        yaxis_title="Probability",
        height=300,
        showlegend=False,
        yaxis=dict(tickformat='.0%'),
        paper_bgcolor="white"
    )
    return fig

def create_risk_factors_chart(contributing_factors):
    if not contributing_factors:
        return None
    df = pd.DataFrame(contributing_factors, columns=['Factor', 'Points'])
    df = df.sort_values('Points', ascending=True)
    fig = px.bar(
        df,
        x='Points',
        y='Factor',
        orientation='h',
        color='Points',
        color_continuous_scale='Reds',
        title="<b>Risk Factors Contributing to Score</b>"
    )
    fig.update_layout(
        height=max(300, len(contributing_factors) * 40),
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'},
        paper_bgcolor="white"
    )
    fig.update_traces(
        texttemplate='%{x}',
        textposition='outside'
    )
    return fig

def create_timeline_visual(los_min, los_max):
    procedure_date = datetime.now().date()
    discharge_earliest = procedure_date + timedelta(days=los_min)
    discharge_latest = procedure_date + timedelta(days=los_max)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[procedure_date],
        y=[1],
        mode='markers+text',
        marker=dict(size=20, color='#140F4B', symbol='star'),
        text=['TAVI Procedure'],
        textposition="top center",
        name='Procedure',
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=[discharge_earliest, discharge_latest],
        y=[1, 1],
        mode='markers+lines+text',
        line=dict(color='#005195', width=8),
        marker=dict(size=15, color='#005195'),
        text=[f'Expected<br>Discharge<br>{discharge_earliest.strftime("%b %d")}',
              f'Latest<br>Expected<br>{discharge_latest.strftime("%b %d")}'],
        textposition="top center",
        name='Discharge Window',
        showlegend=False
    ))
    fig.update_layout(
        title="<b>Procedure and Expected Discharge Timeline</b>",
        xaxis_title="Date",
        yaxis=dict(visible=False, range=[0.5, 1.5]),
        height=250,
        paper_bgcolor="white"
    )
    return fig

# --------------------------
# Tab Navigation Simulation
# --------------------------
tabs = ["Assessment", "Results", "Disclaimer"]
selected_tab = st.session_state.active_tab

# --------------------------
# Patient Assessment Tab
# --------------------------
if selected_tab == "Assessment":
    st.subheader("👤 Patient Demographics")
    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input("Age (years)", min_value=50, max_value=100,
                              value=st.session_state.age, key="age")
        sex = st.radio("Sex", ("Male", "Female"),
                       index=0 if st.session_state.sex == "Male" else 1,
                       key="sex")
    with col2:
        bmi = st.number_input("BMI (kg/m²)", min_value=15.0, max_value=50.0,
                              value=st.session_state.bmi, step=0.1, key="bmi")  # ✅ only one widget
        if bmi < 18.5:
            bmi_cat = "Underweight"
        elif bmi < 25:
            bmi_cat = "Normal"
        elif bmi < 30:
            bmi_cat = "Overweight"
        else:
            bmi_cat = "Obese"
        st.caption(f"BMI Category: {bmi_cat}")
    with col3:
        cfs = st.slider("Clinical Frailty Score", 1, 9,
                        st.session_state.cfs, key="cfs")
        if cfs <= 3:
            cfs_desc = "Fit"
        elif cfs <= 6:
            cfs_desc = "Vulnerable to mildly frail"
        else:
            cfs_desc = "Severely frail"
        st.caption(f"Frailty Status: {cfs_desc}")

    st.subheader("💓 Cardiac Function")
    lvef = st.slider("LVEF (%)", min_value=15, max_value=70,
                     value=st.session_state.lvef, key="lvef")
    if lvef < 40:
        lvef_desc = "Reduced"
    elif lvef < 50:
        lvef_desc = "Mildly reduced"
    else:
        lvef_desc = "Normal"
    st.caption(f"LVEF Classification: {lvef_desc}")

    st.subheader("🩺 Comorbidities")
    col1, col2, col3 = st.columns(3)
    with col1:
        diabetes = st.checkbox("Diabetes Mellitus", value=st.session_state.diabetes, key="diabetes")
        copd = st.checkbox("COPD / Chronic Lung Disease", value=st.session_state.copd, key="copd")
        af = st.checkbox("Atrial Fibrillation", value=st.session_state.af, key="af")
    with col2:
        ckd = st.checkbox("Chronic Kidney Disease (Stage 3–5)", value=st.session_state.ckd, key="ckd")
        prior_cabg = st.checkbox("Prior CABG", value=st.session_state.prior_cabg, key="prior_cabg")
        prior_pci = st.checkbox("Prior PCI", value=st.session_state.prior_pci, key="prior_pci")
    with col3:
        prior_stroke = st.checkbox("Previous Stroke/TIA", value=st.session_state.prior_stroke, key="prior_stroke")
        pulm_hypertension = st.checkbox("Pulmonary Hypertension", value=st.session_state.pulm_hypertension, key="pulm_hypertension")

    st.subheader("🩻 Procedural Details")
    approach = st.radio("Planned TAVI Approach",
                        ("Transfemoral", "Transapical", "Subclavian/Axillary", "Other"),
                        index=["Transfemoral", "Transapical", "Subclavian/Axillary", "Other"].index(st.session_state.approach),
                        key="approach")

    # Calculate Button
    if st.button("🔮 Calculate Predicted Length of Stay", use_container_width=True):
        st.session_state.result = calculate_los_risk(
            st.session_state.age, st.session_state.sex, st.session_state.bmi,
            st.session_state.diabetes, st.session_state.ckd, st.session_state.copd,
            st.session_state.af, st.session_state.prior_cabg, st.session_state.prior_pci,
            st.session_state.prior_stroke, st.session_state.lvef,
            st.session_state.pulm_hypertension, st.session_state.cfs,
            st.session_state.approach
        )
        st.session_state.active_tab = "Results"
        st.rerun()

# --------------------------
# Results Tab
# --------------------------
elif selected_tab == "Results":
    if "result" in st.session_state:
        # ✅ Unpack the full set of returned values
        score, category, los, color, color_code, contributing_factors, los_min, los_max = st.session_state.result

        st.subheader("📊 Risk Prediction Results")
        st.markdown(f"""
        <div style="
            background: linear-gradient(90deg, {color_code}, #f8f9fa);
            padding: 20px; border-radius: 10px; margin-bottom: 20px;
            color: white; text-align: center;
        ">
            <h2>Risk Category: {color} {category}</h2>
            <h3>Predicted Length of Stay: {los}</h3>
            <p style="font-size: 1.2em;">Total Risk Score: {score}/20</p>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("📊 Risk Assessment Visualizations")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(create_risk_gauge(score, category, color_code), use_container_width=True)
        with col2:
            st.plotly_chart(create_los_distribution(los_min, los_max, category, color_code), use_container_width=True)

        st.subheader("🔎 Contributing Risk Factors")
        risk_factors_chart = create_risk_factors_chart(contributing_factors)
        if risk_factors_chart:
            st.plotly_chart(risk_factors_chart, use_container_width=True)
        else:
            st.info("No significant risk factors contributed to the score.")

        st.subheader("📅 Timeline to Expected Discharge")
        st.plotly_chart(create_timeline_visual(los_min, los_max), use_container_width=True)

        if st.button("⬅️ Back to Assessment", use_container_width=True):
            st.session_state.active_tab = "Assessment"
            st.rerun()
    else:
        st.warning("Please complete the assessment first.")

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
