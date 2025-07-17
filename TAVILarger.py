import streamlit as st
import numpy as np
import pandas as pd

# Title
st.title("🫀 TAVI Length of Stay (LOS) Predictor")
st.markdown("""
Predict the estimated hospital length of stay (LOS) after Transcatheter Aortic Valve Implantation (TAVI) using key clinical and procedural inputs.
""")

# Sidebar inputs
st.sidebar.header("🧍 Patient Characteristics")
age = st.sidebar.slider("Age", 50, 100, 75)
sex = st.sidebar.selectbox("Sex", ["Male", "Female"])
sts_score = st.sidebar.slider("STS Risk Score (%)", 0.1, 20.0, 3.0)
creatinine = st.sidebar.slider("Serum Creatinine (mg/dL)", 0.5, 3.0, 1.0)
afib = st.sidebar.selectbox("Atrial Fibrillation", ["No", "Yes"])

st.sidebar.header("🛠️ Procedural Factors")
anesthesia = st.sidebar.selectbox("Anesthesia Type", ["Local/Conscious Sedation", "General Anesthesia"])
vascular_complication = st.sidebar.selectbox("Vascular Complications", ["No", "Yes"])
blood_transfusion = st.sidebar.selectbox("Blood Transfusion Required", ["No", "Yes"])
valve_type = st.sidebar.selectbox("Valve Type", ["Balloon-Expandable", "Self-Expanding"])
ep_study_done = st.sidebar.selectbox("EP Study Done", ["Yes", "No"])

# Encode input
def encode_inputs():
    return pd.DataFrame({
        'Age': [age],
        'Sex': [1 if sex == "Female" else 0],
        'STS': [sts_score],
        'Creatinine': [creatinine],
        'AFib': [1 if afib == "Yes" else 0],
        'Anesthesia': [1 if anesthesia == "General Anesthesia" else 0],
        'VascularComp': [1 if vascular_complication == "Yes" else 0],
        'Transfusion': [1 if blood_transfusion == "Yes" else 0],
        'ValveType': [1 if valve_type == "Self-Expanding" else 0],
        'EPStudy': [1 if ep_study_done == "Yes" else 0],
    })

X_input = encode_inputs()

# Risk scoring function
def calculate_risk_score(inputs):
    score = 0
    score += (inputs['Age'][0] - 70) * 0.1
    score += inputs['Sex'][0] * 1            # Female = +1
    score += inputs['STS'][0] * 0.2
    score += inputs['Creatinine'][0] * 0.5
    score += inputs['AFib'][0] * 1
    score += inputs['Anesthesia'][0] * 2     # General = +2
    score += inputs['VascularComp'][0] * 2
    score += inputs['Transfusion'][0] * 2
    score += inputs['ValveType'][0] * 1
    score -= inputs['EPStudy'][0] * 1        # EP study reduces risk

    return score

# Calculate and categorize
risk_score = calculate_risk_score(X_input)

if risk_score < 3:
    category = "< 2 days"
    message = "🟢 Likely very early discharge (same/next day)."
    color = "success"
elif 3 <= risk_score <= 6:
    category = "2–4 days"
    message = "🟡 Expected moderate stay (routine recovery)."
    color = "warning"
else:
    category = "> 4 days"
    message = "🔴 Likely prolonged hospitalization."
    color = "error"

# Output
st.subheader("📊 Prediction Result")
st.markdown(f"### 🏥 **Predicted LOS:** {category}")
st.info(message)

# Optional details
with st.expander("🔍 Risk Score & Input Summary"):
    st.write(f"**Calculated Risk Score:** `{risk_score:.2f}`")
    st.write("**Encoded Inputs:**")
    st.write(X_input)
