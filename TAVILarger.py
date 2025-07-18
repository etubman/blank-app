import streamlit as st

def predict_los_fast(age, sex_male, local_anaesthesia, egfr, no_conduction, no_bleeding):
    score = sum([
        1 if age < 85 else 0,
        1 if sex_male else 0,
        1 if local_anaesthesia else 0,
        1 if egfr >= 33 else 0,         # eGFR < 33 = risk
        1 if no_conduction else 0,
        1 if no_bleeding else 0,
    ])
    return 3 if score >= 5 else 4 if score >= 3 else 5

def main():
    st.title("FAST‑TAVI II Early Discharge Predictor")

    age = st.number_input("Age (years)", min_value=18, max_value=120, value=82)
    sex = st.radio("Sex", ("Male", "Female"))
    local_anaesthesia = st.checkbox("Procedure under local anaesthesia")

    egfr = st.slider(
        "eGFR (mL/min/1.73 m²)",
        min_value=5,
        max_value=120,
        value=60,
        help="eGFR < 33 indicates renal dysfunction and higher risk"
    )

    conduction = st.checkbox("Conduction disturbance or pacemaker requirement")
    bleeding = st.checkbox("Bleeding or vascular complication")

    if st.button("Predict Length of Stay"):
        los = predict_los_fast(
            age,
            sex == "Male",
            local_anaesthesia,
            egfr,
            not conduction,
            not bleeding
        )
        st.success(f"Predicted LOS: **{los} days** (FAST‑TAVI II model)")

if __name__ == "__main__":
    main()
