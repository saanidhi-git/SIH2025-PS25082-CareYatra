# app.py
import streamlit as st
import pandas as pd
import joblib
import numpy as np


def app():
    st.set_page_config(page_title="Insurance Need Predictor", layout="centered")

    st.title("Insurance Need Predictor")
    st.write("Predict expected annual medical cost and suggest a recommended insurance cover.")

    # Load model (pipeline)
    @st.cache_resource
    # def load_model(path="C:\Users\as\Desktop\care_yatra\backend_1\TEST\insurance_pipeline.joblib"):
    def load_model(path="C:/Users/as/Desktop/care_yatra/backend_1/TEST/insurance_pipeline.joblib"):

        return joblib.load(path)

    model = load_model()

    # User inputs
    age = st.number_input("Age", min_value=0, max_value=120, value=30, step=1)
    sex = st.selectbox("Sex", ["male", "female"])
    bmi = st.number_input("BMI", min_value=10.0, max_value=60.0, value=25.0, step=0.1)
    children = st.number_input("Number of children", min_value=0, max_value=10, value=0, step=1)
    smoker = st.selectbox("Smoker?", ["no", "yes"])
    region = st.selectbox("Region", ["southwest", "southeast", "northwest", "northeast"])

    # Disease input (not in original dataset) — we use illustrative multipliers
    st.markdown("**Known chronic conditions (optional)** — used to adjust predicted cost (illustrative only).")
    disease_selection = st.multiselect(
        "Choose disease(s)", 
        ["Diabetes", "Hypertension", "Heart disease", "Asthma", "Cancer", "None"]
    )

    # Example disease-to-added-risk mapping (illustrative; must be calibrated with domain/actuary data)
    disease_risk_map = {
        "Diabetes": 0.25,
        "Hypertension": 0.18,
        "Heart disease": 0.50,
        "Asthma": 0.12,
        "Cancer": 0.75,
        "None": 0.0
    }

    # compute additive disease risk (excluding None)
    disease_risk = 0.0
    for d in disease_selection:
        if d != "None":
            disease_risk += disease_risk_map.get(d, 0.2)

    safety_margin = st.slider("Safety margin (conservativeness)", min_value=1.0, max_value=3.0, value=1.5, step=0.1,
                            help="Multiply predicted cost by this to recommend coverage beyond expected expenses.")

    if st.button("Predict"):
        # Build input DataFrame matching training features
        data = pd.DataFrame([{
            "age": int(age),
            "sex": sex,
            "bmi": float(bmi),
            "children": int(children),
            "smoker": smoker,
            "region": region
        }])
        pred = model.predict(data)[0]          # predicted annual medical cost (USD in dataset)
        adjusted = pred * (1.0 + disease_risk) * safety_margin

        st.metric("Predicted annual medical cost (model)", f"${pred:,.2f}")
        st.metric("Recommended annual insurance cover (suggested)", f"${adjusted:,.2f}")

        st.markdown("**Details & notes**")
        st.write(f"- Disease adjustment (additive percentage): {disease_risk*100:.1f}%")
        st.write(f"- Safety margin: ×{safety_margin}")
        st.info("These disease multipliers are illustrative. For production use, calibrate them with claims data or actuarial inputs.")
