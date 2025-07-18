import streamlit as st

def predict_los_fast(age, sex_male, local_anaesthesia, no_aki, no_conduction, no_bleeding):
    score = sum([
        1 if age < 85 else 0,
        1 if sex_male else 0,
        1 if local_anaesthesia else 0,
        1 if no_aki else 0,
        1 if no_conduction else 0,
        1 if no_bleeding else 0,
    ])
    return 3 if score >= 5 else 4 if score >= 3 else 5

def main():
    st.title("FAST‑TAVI II Early Discharge Predictor")

    age = st.number_input("Age (years)", min_value=18, max_value=120, value=82)
    sex = st.radio("Sex", ("Male", "Female"))
    local_anaesthesia = st.checkbox("Procedure under local anaesthesia")
    aki = st.checkbox("Acute kidney injury during admission")  # invert later
    conduction = st.checkbox("New conduction disturbance / pre-existing RBBB / pacemaker requirement")
    bleeding = st.checkbox("Bleeding or vascular complication")

    if st.button("Predict Length of Stay"):
        los = predict_los_fast(
            age,
            sex == "Male",
            local_anaesthesia,
            not aki,
            not conduction,
            not bleeding
        )
        st.success(f"Predicted LOS: **{los} days** (FAST‑TAVI II)")        

if __name__ == "__main__":
    main()
