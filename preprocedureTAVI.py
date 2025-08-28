import streamlit as st

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
    "bmi": 25,
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
    <img src="https://static.cdnlogo.com/logos/m/8/medtronic.svg"
         style="height: 50px; margin-right: 1rem;" alt="Medtronic Logo">
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

    # Age
    if age >= 85:
        score += 2
    elif age >= 75:
        score += 1

    # Sex
    if sex == "Female":
        score += 1

    # BMI extremes
    if bmi < 20:
        score += 1
    elif bmi >= 35:
        score += 1

    # Comorbidities
    if diabetes: score += 1
    if ckd: score += 2
    if copd: score += 1
    if af: score += 1
    if prior_cabg: score += 1
    if prior_stroke: score += 1
    if pulm_hypertension: score += 1

    # Cardiac function
    if lvef < 40:
        score += 2
    elif lvef < 50:
        score += 1

    # Frailty
    if cfs >= 7:
        score += 3
    elif cfs >= 5:
        score += 2
    elif cfs == 4:
        score += 1

    # Procedural approach
    if approach != "Transfemoral":
        score += 2

    # Categorize risk
    if score <= 4:
        category = "Low"
        los = "2–3 days"
        color = "🟢"
    elif score <= 8:
        category = "Intermediate"
        los = "4–6 days"
        color = "🟡"
    elif score <= 12:
        category = "High"
        los = "7–10 days"
        color = "🟠"
    else:
        category = "Very High"
        los = ">10 days"
        color = "🔴"

    return score, category, los, color

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
        age = st.number_input("Age (years)", min_value=50, max_value=100, value=st.session_state.age, key="age")
        sex = st.radio("Sex", ("Male", "Female"), index=0 if st.session_state.sex == "Male" else 1, key="sex")
    with col2:
        bmi = st.number_input("BMI (kg/m²)", min_value=15, max_value=50,
                              value=int(st.session_state.bmi), step=1, key="bmi")
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
        cfs = st.slider("Clinical Frailty Score", 1, 9, st.session_state.cfs, key="cfs")
        if cfs <= 3:
            cfs_desc = "Fit"
        elif cfs <= 6:
            cfs_desc = "Vulnerable to mildly frail"
        else:
            cfs_desc = "Severely frail"
        st.caption(f"Frailty Status: {cfs_desc}")

    st.subheader("💓 Cardiac Function")
    lvef = st.slider("LVEF (%)", min_value=15, max_value=70, value=st.session_state.lvef, key="lvef")
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
        score, category, los, color = st.session_state.result
        st.subheader("📊 Risk Prediction Results")
        st.markdown(f"""
        <div style="
            background-color:#005195; padding:20px;
            border-radius:10px; color:white; text-align:center;
        ">
            <h2>Risk Category: {color} {category}</h2>
            <h3>Predicted Length of Stay: {los}</h3>
            <p>Total Risk Score: {score}</p>
        </div>
        """, unsafe_allow_html=True)

        # 🔄 New Patient Button
        if st.button("➕ New Patient Entry", use_container_width=True):
            for key, val in DEFAULTS.items():
                st.session_state[key] = val
            st.session_state.pop("result", None)
            st.session_state.active_tab = "Assessment"
            st.rerun()

    else:
        st.warning("Please complete the patient assessment and calculate risk first.")

# --------------------------
# Disclaimer Tab
# --------------------------
elif selected_tab == "Disclaimer":
    st.subheader("⚠️ Disclaimer")
    st.info("This calculator is intended for research and educational purposes only. "
            "It is not a substitute for professional clinical judgment.")
