import streamlit as st

def predict_los_fast(age, sex_male, local_anaesthesia, egfr, no_conduction, no_bleeding, cfs):
    score = sum([
        1 if age < 85 else 0,
        1 if sex_male else 0,
        1 if local_anaesthesia else 0,
        1 if egfr >= 33 else 0,
        1 if no_conduction else 0,
        1 if no_bleeding else 0,
        1 if cfs < 4 else 0  # CFS ≥ 4 = increased risk
    ])
    if score >= 6:
        los = 3
        risk = "Low"
    elif score >= 4:
        los = 4
        risk = "Medium"
    else:
        los = 5
        risk = "High"
    return los, risk, score

def main():
    # Logo and title on the same row
    col1, col2 = st.columns([1, 4])
    
    with col1:
        st.write("")
        st.write("")
        try:
            st.image("freeman_logo.png", width=70)
        except:
            st.write("🏥")  # Fallback hospital emoji
    
    with col2:
        st.title("Freeman Hospital TAVI Length of Stay and Risk Predictor")
    
    # Inputs
    age = st.number_input("Age (years)", min_value=18, max_value=120, value=82)
    sex = st.radio("Sex", ("Male", "Female"))

    egfr = st.slider(
        "eGFR (mL/min/1.73 m²) on admission",
        min_value=5,
        max_value=90,
        value=60,
        help="eGFR < 33 indicates renal dysfunction and higher risk"
    )

    cfs = st.slider(
        "Clinical Frailty Score (1–9)",
        min_value=1,
        max_value=9,
        value=3,
        help="Higher scores (≥4) indicate increasing frailty and delayed recovery"
    )

    local_anaesthesia = st.checkbox("Procedure under local anaesthesia")
    conduction = st.checkbox("New conduction disturbance or pacemaker requirement")
    bleeding = st.checkbox("Bleeding or vascular complication")
    
    if st.button("Predict Length of Stay"):
        los, risk, score = predict_los_fast(
            age,
            sex == "Male",
            local_anaesthesia,
            egfr,
            not conduction,
            not bleeding,
            cfs
        )
        
        st.success(f"Predicted LOS: **{los} days**")
        st.info(f"Risk category: **{risk} Risk** (Score: {score}/7)")

        if risk == "Low":
            st.markdown("🟢 **Low Risk** – likely candidate for early discharge (≤ 3 days)")
        elif risk == "Medium":
            st.markdown("🟠 **Medium Risk** – consider close monitoring (LOS ~4 days)")
        else:
            st.markdown("🔴 **High Risk** – prolonged hospitalization likely (≥ 5 days)")

if __name__ == "__main__":
    main()
