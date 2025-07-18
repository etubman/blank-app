import streamlit as st

def predict_los_fast(age, sex_male, local_anaesthesia, egfr, no_conduction, no_bleeding):
    score = sum([
        1 if age < 85 else 0,
        1 if sex_male else 0,
        1 if local_anaesthesia else 0,
        1 if egfr >= 33 else 0,
        1 if no_conduction else 0,
        1 if no_bleeding else 0,
    ])
    if score >= 5:
        los = 3
        risk = "Low"
    elif score >= 3:
        los = 4
        risk = "Medium"
    else:
        los = 5
        risk = "High"
    return los, risk, score

def main():
    # Create two columns: one for the logo, one for the title
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("freeman_logo.png", width=50)
    with col2:
        st.title("Freeman Hospital TAVI Length of Stay and Risk Calculator")

    # Inputs
    age = st.number_input("Age (years)", min_value=18, max_value=120, value=82)
    sex = st.radio("Sex", ("Male", "Female"))

    egfr = st.slider(
        "eGFR (mL/min/1.73 m²) on admission",
        min_value=5,
        max_value=90,
        value=60,
        help="eGFR < 33 indicates renal dysfunction and higher risk"
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
            not bleeding
        )

        st.success(f"Predicted LOS: **{los} days**")
        st.info(f"Risk category: **{risk} Risk** (Score: {score}/6)")

        if risk == "Low":
            st.markdown("🟢 **Low Risk** – likely candidate for early discharge (≤ 3 days)")
        elif risk == "Medium":
            st.markdown("🟠 **Medium Risk** – consider close monitoring (LOS ~4 days)")
        else:
            st.markdown("🔴 **High Risk** – prolonged hospitalization likely (≥ 5 days)")

if __name__ == "__main__":
    main()
