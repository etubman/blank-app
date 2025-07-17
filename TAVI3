import streamlit as st
import pandas as pd
import numpy as np

st.title("🩺 FAST‑TAVI II Length-of-Stay Predictor")
st.markdown("""
Predict expected length of stay (LOS) categories following transfemoral TAVI,
using key factors validated in the FAST‑TAVI II trial (Durand et al., Eur Heart J 2024).
""")

# User inputs
st.sidebar.header("Procedure Details")
non_elective = st.sidebar.radio("Non‑elective procedure?", ("No", "Yes"))
conduction = st.sidebar.radio("Post‑TAVI conduction disturbance?", ("No", "Yes"))
complication = st.sidebar.radio("Any in‑hospital complication?", ("No", "Yes"))
program = st.sidebar.radio("Institution with FAST‑TAVI program?", ("No", "Yes"))

def encode(x): return 1 if x == "Yes" else 0

# Encode
data = {
    "NonElective": [encode(non_elective)],
    "Conduction": [encode(conduction)],
    "Complication": [encode(complication)],
    "FASTProgram": [encode(program)]
}
df = pd.DataFrame(data)

# Scoring based on log-odds (using log(OR))
log_odds = (
    np.log(1.88) * df["NonElective"]
    + np.log(3.61) * df["Conduction"]
    + np.log(4.75) * df["Complication"]
    - np.log(1/0.32) * df["FASTProgram"]
)

# Base intercept estimated so that average falls in 3–4 days (~median 3–4)
intercept = np.log(0.4 / (1 - 0.4))  # approx 0.4 baseline early discharge rate

# Compute probability of **early discharge (≤3 days)**
prob_early = 1 / (1 + np.exp(-(intercept + log_odds)[0]))

# Determine LOS category
if prob_early > 0.6:
    category = "<= 3 days"
    msg = "✅ Likely early discharge"
elif prob_early > 0.3:
    category = "3–5 days"
    msg = "⚠️ Moderate length of stay"
else:
    category = "> 5 days"
    msg = "❌ Likely prolonged hospitalization"

# Display results
st.subheader("🏥 Predicted LOS Category")
st.markdown(f"### **{category}** — {msg}")
st.write(f"**Estimated probability of early discharge (≤3 days):** {prob_early:.2f}")

with st.expander("🔍 Model Factors & Scoring"):
    st.write(df)
    st.write(f"Log‑odds sum (inc. intercept): {(intercept + log_odds)[0]:.2f}")
