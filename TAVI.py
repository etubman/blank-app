import streamlit as st

def predict_los_score(sex, comorbid1, comorbid2, comorbid3, gfr, cfs):
    score = sum([
        1 if sex == "Female" else 0,
        1 if comorbid1 else 0,  # PAD
        1 if comorbid2 else 0,  # CHF on admission
        1 if comorbid3 else 0,  # Atrial Fibrillation
        1 if gfr < 33 else 0,
        1 if cfs >= 3 else 0,
    ])
    return 5 if score == 0 else 8 if score >= 3 else 6

def main():
    st.title("TAVI Length‑of‑Stay Predictor")
    st.markdown("**Fill in the clinical inputs below and click Predict**")

    sex = st.radio("Gender", ("Male", "Female"))

    st.markdown("**Comorbidities**")
    comorbid1 = st.checkbox("Peripheral arterial disease (PAD)")
    comorbid2 = st.checkbox("Congestive heart failure on admission")
    comorbid3 = st.checkbox("Atrial Fibrillation")

    gfr = st.number_input("GFR (mL/min/1.73 m²)", min_value=0, max_value=150, value=60)
    cfs = st.select_slider("Clinical Frailty Scale (1–9)", options=list(range(1,10)), value=2)

    if st.button("Predict Length of Stay"):
        los = predict_los_score(sex, comorbid1, comorbid2, comorbid3, gfr, cfs)
        st.success(f"Predicted hospital stay: **{los} days**")

if __name__ == "__main__":
    main()
