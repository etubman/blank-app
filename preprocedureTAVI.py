import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

# --------------------------
# Password Check
# --------------------------
def check_password():
    def password_entered():
        if st.session_state["password"] == "TAVI2025":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Incorrect password")
        return False
    else:
        return True

# --------------------------
# Page Config
# --------------------------
st.set_page_config(page_title="TAVI LOS Calculator", layout="wide")
if not check_password():
    st.stop()

# --------------------------
# Default Patient Values
# --------------------------
DEFAULTS = {
    "age": 82,
    "sex": "Male",
    "bmi": 25.0,
    "cfs": 4,
    "care_needs": "No",  # default string matching radio options ("No" / "Yes")
    "lvef": 55,
    "diabetes": False,
    "ckd": False,
    "copd": False,
    "af": False,
    "lbbb": False,
    "prior_cabg": False,
    "prior_pci": False,
    "prior_stroke": False,
    "pulm_hypertension": False,
    "approach": "Transfemoral",
}

# --------------------------
# Styling
# --------------------------
st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #140F4B;
    color: white;
}
[data-testid="stSidebar"] * {
    color: white !important;
}
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
.stRadio label, .stCheckbox label {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# --------------------------
# Header
# --------------------------
st.markdown(f"""
<div style="
    background: linear-gradient(90deg, #140F4B, #005195);
    padding: 1rem; border-radius: 10px; margin-bottom: 2rem;
    display: flex; align-items: center;
">
    <img src="https://s3.eu-north-1.amazonaws.com/cdn-site.mediaplanet.com/app/uploads/sites/42/2021/11/07145553/P3-Full-Medtronic-logo.png"
         style="height: 100px; margin-right: 1rem;" alt="Medtronic Logo">
    <h1 style="color: white; margin: 0; font-family: sans-serif;">
        🫀 TAVI Pre-Procedure Length of Stay Calculator
    </h1>
</div>
""", unsafe_allow_html=True
