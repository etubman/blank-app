import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def calculate_los_risk(age, sex_male, bmi, diabetes, ckd, copd, af, prior_cabg, 
                      prior_pci, prior_stroke, lvef, pulm_hypertension, cfs, 
                      approach):
    """
    Calculate TAVI length of stay based on pre-procedural risk factors
    """
    risk_score = 0
    contributing_factors = []
    
    # Age factors
    if age >= 85:
        risk_score += 2
        contributing_factors.append(("Age ≥85 years", 2))
    elif age >= 75:
        risk_score += 1
        contributing_factors.append(("Age 75-84 years", 1))
    
    # Comorbidity factors
    if diabetes:
        risk_score += 1
        contributing_factors.append(("Diabetes mellitus", 1))
    if ckd:  # CKD stage 3-5
        risk_score += 2
        contributing_factors.append(("Chronic kidney disease", 2))
    if copd:
        risk_score += 1
        contributing_factors.append(("COPD/Chronic lung disease", 1))
    if af:
        risk_score += 1
        contributing_factors.append(("Atrial fibrillation", 1))
    if prior_cabg:
        risk_score += 1
        contributing_factors.append(("Previous CABG", 1))
    if prior_stroke:
        risk_score += 1
        contributing_factors.append(("Previous stroke/TIA", 1))
    if pulm_hypertension:
        risk_score += 1
        contributing_factors.append(("Pulmonary hypertension", 1))
    
    # Functional factors (LVEF)
    if lvef < 40:
        risk_score += 2
        contributing_factors.append(("LVEF <40%", 2))
    elif lvef < 50:
        risk_score += 1
        contributing_factors.append(("LVEF 40-49%", 1))
    
    # Frailty
    if cfs >= 7:
        risk_score += 3
        contributing_factors.append(("Clinical Frailty Score ≥7", 3))
    elif cfs >= 5:
        risk_score += 2
        contributing_factors.append(("Clinical Frailty Score 5-6", 2))
    elif cfs >= 4:
        risk_score += 1
        contributing_factors.append(("Clinical Frailty Score 4", 1))
    
    # Access approach
    if approach == "Non-transfemoral":
        risk_score += 2
        contributing_factors.append(("Non-transfemoral access", 2))
    
    # BMI extremes
    if bmi < 20:
        risk_score += 1
        contributing_factors.append(("BMI <20 kg/m²", 1))
    elif bmi >= 35:
        risk_score += 1
        contributing_factors.append(("BMI ≥35 kg/m²", 1))
    
    # Gender (females tend to have longer stays)
    if not sex_male:
        risk_score += 1
        contributing_factors.append(("Female sex", 1))
    
    # Determine risk category and predicted LOS
    if risk_score <= 4:
        risk_category = "Low"
        predicted_los_min = 2
        predicted_los_max = 3
        predicted_los = "2-3 days"
        discharge_advice = "Early discharge candidate"
        color = "🟢"
        color_code = "green"
    elif risk_score <= 8:
        risk_category = "Intermediate"
        predicted_los_min = 4
        predicted_los_max = 6
        predicted_los = "4-6 days"
        discharge_advice = "Standard monitoring required"
        color = "🟡"
        color_code = "orange"
    elif risk_score <= 12:
        risk_category = "High"
        predicted_los_min = 7
        predicted_los_max = 10
        predicted_los = "7-10 days"
        discharge_advice = "Extended monitoring likely needed"
        color = "🟠"
        color_code = "red"
    else:
        risk_category = "Very High"
        predicted_los_min = 10
        predicted_los_max = 15
        predicted_los = ">10 days"
        discharge_advice = "Prolonged hospitalization expected"
        color = "🔴"
        color_code = "darkred"
    
    return (risk_score, risk_category, predicted_los, discharge_advice, color, 
            color_code, contributing_factors, predicted_los_min, predicted_los_max)

def create_risk_chart(risk_score, risk_category, color_code):
    """Create a visual risk gauge"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = risk_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Risk Score"},
        delta = {'reference': 10},
        gauge = {
            'axis': {'range': [None, 20]},
            'bar': {'color': color_code},
            'steps': [
                {'range': [0, 4], 'color': "lightgreen"},
                {'range': [4, 8], 'color': "yellow"},
                {'range': [8, 12], 'color': "orange"},
                {'range': [12, 20], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 15
            }
        }
    ))
    fig.update_layout(height=300)
    return fig

def create_timeline_chart(predicted_los_min, predicted_los_max, procedure_date):
    """Create a timeline showing expected discharge window"""
    discharge_min = procedure_date + timedelta(days=predicted_los_min)
    discharge_max = procedure_date + timedelta(days=predicted_los_max)
    
    fig = go.Figure()
    
    # Add procedure date
    fig.add_trace(go.Scatter(
        x=[procedure_date],
        y=[1],
        mode='markers+text',
        marker=dict(size=15, color='blue', symbol='star'),
        text=['TAVI Procedure'],
        textposition="top center",
        name='Procedure Date'
    ))
    
    # Add discharge window
    fig.add_trace(go.Scatter(
        x=[discharge_min, discharge_max],
        y=[1, 1],
        mode='markers+lines+text',
        line=dict(color='green', width=8),
        marker=dict(size=12, color='green'),
        text=['Earliest Discharge', 'Latest Expected'],
        textposition="top center",
        name='Expected Discharge Window'
    ))
    
    fig.update_layout(
        title="Expected Discharge Timeline",
        xaxis_title="Date",
        yaxis=dict(visible=False),
        height=200,
        showlegend=False
    )
    
    return fig

def main():
    # Configure page
    st.set_page_config(
        page_title="TAVI LOS Calculator",
        page_icon="🫀",
        layout="wide"
    )
    
    # Header
    st.markdown("""
    <div style="background: linear-gradient(90deg, #FF6B6B, #4ECDC4); padding: 1rem; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; text-align: center; margin: 0;">
            🫀 TAVI Pre-Procedure Length of Stay Calculator
        </h1>
        <p style="color: white; text-align: center; margin: 0;">
            Predict length of stay based on pre-procedural patient characteristics
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar info
    with st.sidebar:
        st.header("📋 Patient Summary")
        if 'calculated' not in st.session_state:
            st.info("Complete the form and calculate to see patient summary")
        
        st.header("📚 Risk Categories")
        st.success("🟢 **Low Risk (≤4 points)**\n- 2-3 days LOS\n- Early discharge candidate")
        st.warning("🟡 **Intermediate Risk (5-8 points)**\n- 4-6 days LOS\n- Standard monitoring")
        st.error("🟠 **High Risk (9-12 points)**\n- 7-10 days LOS\n- Extended monitoring")
        st.error("🔴 **Very High Risk (>12 points)**\n- >10 days LOS\n- Prolonged hospitalization")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Patient Assessment", "📈 Results & Analytics", "📖 Information"])
    
    with tab1:
        # Patient Demographics
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
            cfs = st.slider(
                "Clinical Frailty Score",
                min_value=1,
                max_value=9,
                value=4,
                help="1-3: Fit, 4-6: Vulnerable to mildly frail, 7-9: Severely frail to terminally ill"
            )
            if cfs <= 3:
                cfs_desc = "Fit"
            elif cfs <= 6:
                cfs_desc = "Vulnerable to mildly frail"
            else:
                cfs_desc = "Severely frail"
            st.caption(f"Frailty Status: {cfs_desc}")
        
        # 💓 Cardiac Function
        st.subheader("💓 Cardiac Function")
        lvef = st.slider("LVEF (%)", min_value=15, max_value=70, value=55)
        if lvef < 40:
            lvef_desc = "Reduced"
        elif lvef < 50:
            lvef_desc = "Mildly reduced"
        else:
            lvef_desc = "Normal"
        st.caption(f"LVEF Classification: {lvef_desc}")
        
        # Comorbidities
        st.subheader("🏥 Comorbidities")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            diabetes = st.checkbox("Diabetes mellitus")
            ckd = st.checkbox("Chronic kidney disease (Stage 3-5)")
            copd = st.checkbox("COPD/Chronic lung disease")
        
        with col2:
            af = st.checkbox("Atrial fibrillation")
            prior_cabg = st.checkbox("Previous CABG")
            prior_pci = st.checkbox("Previous PCI")
        
        with col3:
            prior_stroke = st.checkbox("Previous stroke/TIA")
            pulm_hypertension = st.checkbox("Pulmonary hypertension")
        
        # Procedural Approach
        st.subheader("🔧 Planned Approach")
        col1, col2 = st.columns(2)
        
        with col1:
            approach = st.selectbox(
                "Access route",
                ("Transfemoral", "Non-transfemoral"),
                help="Transfemoral approach typically associated with shorter stays"
            )
        
        with col2:
            procedure_date = st.date_input("Planned procedure date", value=datetime.now().date())
        
        st.markdown("---")
        
        # Calculate button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔮 Calculate Predicted Length of Stay", type="primary", use_container_width=True):
                st.session_state.calculated = True
                
                result = calculate_los_risk(
                    age, sex == "Male", bmi, diabetes, ckd, copd, af, prior_cabg,
                    prior_pci, prior_stroke, lvef, pulm_hypertension, cfs, approach
                )
                
                (risk_score, risk_category, predicted_los, discharge_advice, color, 
                 color_code, contributing_factors, predicted_los_min, predicted_los_max) = result
                
                st.session_state.result = result
                st.session_state.patient_data = {
                    'age': age, 'sex': sex, 'bmi': bmi, 'cfs': cfs,
                    'procedure_date': procedure_date
                }
    
    with tab2:
        if 'calculated' in st.session_state and st.session_state.calculated:
            result = st.session_state.result
            patient_data = st.session_state.patient_data
            
            (risk_score, risk_category, predicted_los, discharge_advice, color, 
             color_code, contributing_factors, predicted_los_min, predicted_los_max) = result
            
            # Results header
            st.markdown("## 📊 Assessment Results")
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Risk Score", f"{risk_score}/20")
            with col2:
                st.metric("Risk Category", f"{color} {risk_category}")
            with col3:
                st.metric("Predicted LOS", predicted_los)
            with col4:
                discharge_min = patient_data['procedure_date'] + timedelta(days=predicted_los_min)
                st.metric("Expected Discharge", discharge_min.strftime("%b %d"))
            
            st.markdown("---")
            
            # Charts
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(create_risk_chart(risk_score, risk_category, color_code), use_container_width=True)
            with col2:
                st.plotly_chart(create_timeline_chart(predicted_los_min, predicted_los_max, 
                                                     patient_data['procedure_date']), 
                               use_container_width=True)
            
            # Category explanation
            if risk_category == "Low":
                st.success(f"✅ **Low Risk Patient** - {discharge_advice}")
            elif risk_category == "Intermediate":
                st.warning(f"⚠️ **Intermediate Risk Patient** - {discharge_advice}")
            elif risk_category == "High":
                st.error(f"🚨 **High Risk Patient** - {discharge_advice}")
            else:
                st.error(f"🚨 **Very High Risk Patient** - {discharge_advice}")
            
            # Contributing factors
            with st.expander("📋 Risk Factors Contributing to Score", expanded=True):
                if contributing_factors:
                    df_factors = pd.DataFrame(contributing_factors, columns=['Risk Factor', 'Points'])
                    fig = px.bar(df_factors, x='Points', y='Risk Factor', orientation='h',
                                title="Risk Factor Breakdown",
                                color='Points', color_continuous_scale='Reds')
                    st.plotly_chart(fig, use_container_width=True)
                    st.dataframe(df_factors, use_container_width=True)
                else:
                    st.success("✅ No significant risk factors identified - excellent prognosis!")
            
            # Sidebar update
            with st.sidebar:
                st.success("✅ **Assessment Complete**")
                st.write(f"**Patient:** {patient_data['sex']}, Age {patient_data['age']}")
                st.write(f"**BMI:** {patient_data['bmi']:.1f} kg/m²")
                st.write(f"**Frailty Score:** {patient_data['cfs']}")
                st.write(f"**Risk Category:** {color} {risk_category}")
                st.write(f"**Predicted LOS:** {predicted_los}")
                
                if st.button("📄 Generate Report"):
                    st.info("Report generation feature coming soon!")
        else:
            st.info("👈 Please complete the patient assessment in the first tab to see results here.")
    
    with tab3:
        st.markdown("""
        ## 📖 About This Calculator
        
        This TAVI Length of Stay Calculator is designed to help healthcare professionals predict post-procedural 
        hospital stay duration based on pre-procedural patient risk factors.
        
        ### 🎯 Purpose
        - **Resource Planning:** Optimize bed allocation and staffing
        - **Patient Counseling:** Set appropriate expectations for patients and families
        - **Care Coordination:** Plan discharge resources and follow-up care
        
        ### 🔬 Methodology
        Weighted scoring system based on:
        - Demographics (Age, sex, BMI)
        - Comorbidities (Diabetes, CKD, COPD, AF, prior procedures)
        - Cardiac Function (LVEF)
        - Frailty (CFS)
        - Procedural factors (access approach)
        
        ### ⚠️ Important Considerations
        - Estimates only — clinical judgment always takes precedence
        - Complications & institutional protocols strongly influence LOS
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 1rem; background-color: #f0f2f6; border-radius: 10px;">
        <p><strong>⚠️ Medical Disclaimer:</strong> This calculator is for educational and clinical decision support purposes only. 
        It should not replace clinical judgment or comprehensive patient assessment.</p>
        <p><small>© 2024 TAVI LOS Calculator | For healthcare professional use only</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
