import streamlit as st
import pandas as pd

def calculate_los_risk(age, sex_male, bmi, diabetes, ckd, copd, af, prior_cabg, 
                      prior_pci, prior_stroke, lvef, pulm_hypertension, cfs, 
                      eurocore_log, sts_score, approach):
    """
    Calculate TAVI length of stay based on pre-procedural risk factors
    """
    risk_score = 0
    
    # Age factors
    if age >= 85:
        risk_score += 2
    elif age >= 75:
        risk_score += 1
    
    # Comorbidity factors
    if diabetes:
        risk_score += 1
    if ckd:  # CKD stage 3-5
        risk_score += 2
    if copd:
        risk_score += 1
    if af:
        risk_score += 1
    if prior_cabg:
        risk_score += 1
    if prior_stroke:
        risk_score += 1
    if pulm_hypertension:
        risk_score += 1
    
    # Functional factors
    if lvef < 40:
        risk_score += 2
    elif lvef < 50:
        risk_score += 1
    
    # Frailty
    if cfs >= 7:
        risk_score += 3
    elif cfs >= 5:
        risk_score += 2
    elif cfs >= 4:
        risk_score += 1
    
    # Surgical risk scores
    if sts_score >= 8:
        risk_score += 2
    elif sts_score >= 4:
        risk_score += 1
    
    if eurocore_log >= 20:
        risk_score += 2
    elif eurocore_log >= 10:
        risk_score += 1
    
    # Access approach
    if approach == "Non-transfemoral":
        risk_score += 2
    
    # BMI extremes
    if bmi < 20 or bmi >= 35:
        risk_score += 1
    
    # Gender (females tend to have longer stays)
    if not sex_male:
        risk_score += 1
    
    # Determine risk category and predicted LOS
    if risk_score <= 4:
        risk_category = "Low"
        predicted_los = "2-3 days"
        discharge_advice = "Early discharge candidate"
        color = "🟢"
    elif risk_score <= 8:
        risk_category = "Intermediate"
        predicted_los = "4-6 days"
        discharge_advice = "Standard monitoring required"
        color = "🟡"
    elif risk_score <= 12:
        risk_category = "High"
        predicted_los = "7-10 days"
        discharge_advice = "Extended monitoring likely needed"
        color = "🟠"
    else:
        risk_category = "Very High"
        predicted_los = ">10 days"
        discharge_advice = "Prolonged hospitalization expected"
        color = "🔴"
    
    return risk_score, risk_category, predicted_los, discharge_advice, color

def main():
    # Header with logo
    col1, col2 = st.columns([1, 4])
    
    with col1:
        st.write("")
        st.write("")
        try:
            st.image("freeman_logo.png", width=100)
        except:
            st.write("🏥")
    
    with col2:
        st.title("TAVI Pre-Procedure Length of Stay Calculator")
    
    st.markdown("---")
    st.write("**Predict length of stay based on pre-procedural patient characteristics**")
    
    # Patient Demographics
    st.subheader("📊 Patient Demographics")
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.number_input("Age (years)", min_value=50, max_value=100, value=82)
        sex = st.radio("Sex", ("Male", "Female"))
        bmi = st.number_input("BMI (kg/m²)", min_value=15.0, max_value=50.0, value=25.0, step=0.1)
    
    with col2:
        cfs = st.slider(
            "Clinical Frailty Score",
            min_value=1,
            max_value=9,
            value=4,
            help="1-3: Fit, 4-6: Vulnerable to mildly frail, 7-9: Severely frail to terminally ill"
        )
    
    # Comorbidities
    st.subheader("🫀 Comorbidities")
    col1, col2 = st.columns(2)
    
    with col1:
        diabetes = st.checkbox("Diabetes mellitus")
        ckd = st.checkbox("Chronic kidney disease (Stage 3-5)")
        copd = st.checkbox("COPD/Chronic lung disease")
        af = st.checkbox("Atrial fibrillation")
    
    with col2:
        prior_cabg = st.checkbox("Previous CABG")
        prior_pci = st.checkbox("Previous PCI")
        prior_stroke = st.checkbox("Previous stroke/TIA")
        pulm_hypertension = st.checkbox("Pulmonary hypertension")
    
    # Cardiac Function
    st.subheader("💓 Cardiac Function")
    col1, col2 = st.columns(2)
    
    with col1:
        lvef = st.slider("LVEF (%)", min_value=15, max_value=70, value=55)
    
    # Risk Scores
    st.subheader("📈 Surgical Risk Scores")
    col1, col2 = st.columns(2)
    
    with col1:
        sts_score = st.number_input("STS Score (%)", min_value=1.0, max_value=30.0, value=5.0, step=0.1)
    
    with col2:
        eurocore_log = st.number_input("EuroSCORE II (%)", min_value=1.0, max_value=50.0, value=8.0, step=0.1)
    
    # Procedural Approach
    st.subheader("🔧 Planned Approach")
    approach = st.selectbox(
        "Access route",
        ("Transfemoral", "Non-transfemoral"),
        help="Transfemoral approach typically associated with shorter stays"
    )
    
    st.markdown("---")
    
    # Calculate button
    if st.button("🔮 Calculate Predicted Length of Stay", type="primary"):
        risk_score, risk_category, predicted_los, discharge_advice, color = calculate_los_risk(
            age, sex == "Male", bmi, diabetes, ckd, copd, af, prior_cabg,
            prior_pci, prior_stroke, lvef, pulm_hypertension, cfs,
            eurocore_log, sts_score, approach
        )
        
        # Display results
        st.markdown("## 📊 Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Risk Score", f"{risk_score}/20")
        
        with col2:
            st.metric("Risk Category", f"{color} {risk_category}")
        
        with col3:
            st.metric("Predicted LOS", predicted_los)
        
        # Risk category explanation
        if risk_category == "Low":
            st.success(f"✅ **Low Risk Patient** - {discharge_advice}")
            st.info("Consider same-day discharge protocols or early discharge pathways.")
        elif risk_category == "Intermediate":
            st.warning(f"⚠️ **Intermediate Risk Patient** - {discharge_advice}")
            st.info("Standard post-procedural monitoring. Plan for mid-week procedures when possible.")
        elif risk_category == "High":
            st.error(f"🚨 **High Risk Patient** - {discharge_advice}")
            st.info("Consider enhanced monitoring, early physiotherapy, and discharge planning involvement.")
        else:
            st.error(f"🚨 **Very High Risk Patient** - {discharge_advice}")
            st.info("Multidisciplinary approach recommended. Consider ICU monitoring and early discharge planning.")
        
        # Risk factors breakdown
        with st.expander("📋 Risk Factors Contributing to Score"):
            risk_factors = []
            
            if age >= 85:
                risk_factors.append("Age ≥85 years (+2)")
            elif age >= 75:
                risk_factors.append("Age 75-84 years (+1)")
            
            if diabetes:
                risk_factors.append("Diabetes mellitus (+1)")
            if ckd:
                risk_factors.append("Chronic kidney disease (+2)")
            if copd:
                risk_factors.append("COPD/Chronic lung disease (+1)")
            if af:
                risk_factors.append("Atrial fibrillation (+1)")
            if prior_cabg:
                risk_factors.append("Previous CABG (+1)")
            if prior_stroke:
                risk_factors.append("Previous stroke/TIA (+1)")
            if pulm_hypertension:
                risk_factors.append("Pulmonary hypertension (+1)")
            
            if lvef < 40:
                risk_factors.append("LVEF <40% (+2)")
            elif lvef < 50:
                risk_factors.append("LVEF 40-49% (+1)")
            
            if cfs >= 7:
                risk_factors.append("Clinical Frailty Score ≥7 (+3)")
            elif cfs >= 5:
                risk_factors.append("Clinical Frailty Score 5-6 (+2)")
            elif cfs >= 4:
                risk_factors.append("Clinical Frailty Score 4 (+1)")
            
            if sts_score >= 8:
                risk_factors.append("STS Score ≥8% (+2)")
            elif sts_score >= 4:
                risk_factors.append("STS Score 4-7.9% (+1)")
            
            if eurocore_log >= 20:
                risk_factors.append("EuroSCORE II ≥20% (+2)")
            elif eurocore_log >= 10:
                risk_factors.append("EuroSCORE II 10-19.9% (+1)")
            
            if approach == "Non-transfemoral":
                risk_factors.append("Non-transfemoral access (+2)")
            
            if bmi < 20 or bmi >= 35:
                risk_factors.append("BMI <20 or ≥35 kg/m² (+1)")
            
            if sex == "Female":
                risk_factors.append("Female sex (+1)")
            
            if risk_factors:
                for factor in risk_factors:
                    st.write(f"• {factor}")
            else:
                st.write("No significant risk factors identified")

    # Disclaimer
    st.markdown("---")
    st.caption("⚠️ **Disclaimer:** This calculator is for educational purposes only and should not replace clinical judgment. Actual length of stay may vary based on individual patient factors, procedural complications, and institutional protocols.")

if __name__ == "__main__":
    main()
