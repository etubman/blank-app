import streamlit as st

# --------------------------
# Page Config
# --------------------------
st.set_page_config(page_title="TAVI LOS Calculator", layout="wide")

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
    if not sex:  # female
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
        age = st.number_input("Age (years)", min_value=50, max_value=100, value=82)
        sex = st.radio("Sex", ("Male", "Female"))
    with col2:
        bmi = st.number_input("BMI (kg/m²)", min_value=15.0, max_value=50.0, value=25.0, step=0.1)
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
        cfs = st.slider("Clinical Frailty Score", 1, 9, 4)
        if cfs <= 3:
            cfs_desc = "Fit"
        elif cfs <= 6:
            cfs_desc = "Vulnerable to mildly frail"
        else:
            cfs_desc = "Severely frail"
        st.caption(f"Frailty Status: {cfs_desc}")

    st.subheader("💓 Cardiac Function")
    lvef = st.slider("LVEF (%)", min_value=15, max_value=70, value=55)
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
        diabetes = st.checkbox("Diabetes Mellitus")
        copd = st.checkbox("COPD / Chronic Lung Disease")
        af = st.checkbox("Atrial Fibrillation")
    with col2:
        ckd = st.checkbox("Chronic Kidney Disease (Stage 3–5)")
        prior_cabg = st.checkbox("Prior CABG")
        prior_pci = st.checkbox("Prior PCI")
    with col3:
        prior_stroke = st.checkbox("Previous Stroke/TIA")
        pulm_hypertension = st.checkbox("Pulmonary Hypertension")

    st.subheader("🩻 Procedural Details")
    approach = st.radio("Planned TAVI Approach", ("Transfemoral", "Transapical", "Subclavian/Axillary", "Other"))

    # Calculate Button
    if st.button("🔮 Calculate Predicted Length of Stay", use_container_width=True):
        st.session_state.result = calculate_los_risk(
            age, sex == "Male", bmi, diabetes, ckd, copd, af, prior_cabg,
            prior_pci, prior_stroke, lvef, pulm_hypertension, cfs, approach
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
    else:
        st.warning("Please complete the patient assessment and calculate risk first.")

# --------------------------
# Disclaimer Tab
# --------------------------
elif selected_tab == "Disclaimer":
    st.subheader("⚠️ Disclaimer")
    st.info("This predictive tool is in its early stages and is not a substitute for professional clinical judgment.")
