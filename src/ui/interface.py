import streamlit as st
import requests
import json

# Page Settings
st.set_page_config(
    page_title="CRM Churn Prediction",
    layout="wide"
)

# Title and Desciption
st.title("Customer Churn Estimation System")
st.write("---")
st.markdown("""
This application uses the **XGBoost (ONNX)** model, trained as part of the MLOps project, to

predict whether customers will leave the company.
""")

# Side Menu (API Connection Status)
st.sidebar.header("System Status")
API_URL = "http://127.0.0.1:8000"

try:
    response = requests.get(API_URL)
    if response.status_code == 200:
        st.sidebar.success("API Connection Successful!")
    else:
        st.sidebar.error("API Error!")
except:
    st.sidebar.error("API Unreachable! \nPlease start FastAPI.")

# --- FORM FIELD ---
st.subheader("Customer Information")

col1, col2, col3 = st.columns(3)

with col1:
    gender = st.selectbox("Gender", ["Female", "Male"])
    senior_citizen = st.selectbox("Over 65 years old?", [0, 1], format_func=lambda x: "Evet" if x == 1 else "Hayır")
    partner = st.selectbox("Is he/she married?", ["Yes", "No"])
    dependents = st.selectbox("Does he/she have someone he/she is responsible for taking care of?", ["Yes", "No"])
    tenure = st.number_input("Customer Duration (Months)", min_value=0, max_value=100, value=12)

with col2:
    phone_service = st.selectbox("Is there a phone service?", ["Yes", "No"])
    multiple_lines = st.selectbox("Multiple Lines?", ["Yes", "No", "No phone service"])
    internet_service = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])
    online_security = st.selectbox("Online Security", ["Yes", "No", "No internet service"])
    online_backup = st.selectbox("Backup Service", ["Yes", "No", "No internet service"])

with col3:
    device_protection = st.selectbox("Device Protection", ["Yes", "No", "No internet service"])
    tech_support = st.selectbox("Technical Support", ["Yes", "No", "No internet service"])
    contract = st.selectbox("Contract Type", ["Month-to-month", "One year", "Two year"])
    paperless_billing = st.selectbox("Paperless Invoice?", ["Yes", "No"])
    payment_method = st.selectbox("Payment Method", ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"])
    monthly_charges = st.number_input("Monthly Fee ($)", min_value=0.0, value=50.0)
    total_charges = st.number_input("Total Fee ($)", min_value=0.0, value=500.0)

st.divider()
col4, col5 = st.columns(2)
with col4:
    streaming_tv = st.selectbox("Is there a TV broadcast?", ["Yes", "No", "No internet service"])
with col5:
    streaming_movies = st.selectbox("Is there a movie being shown?", ["Yes", "No", "No internet service"])

# --- PREDICTION BUTTON ---
if st.button("Estimate Customer Status", type="primary"):
    
    # JSON Format Expected by the API
    input_data = {
        "gender": gender,
        "SeniorCitizen": senior_citizen,
        "Partner": partner,
        "Dependents": dependents,
        "tenure": tenure,
        "PhoneService": phone_service,
        "MultipleLines": multiple_lines,
        "InternetService": internet_service,
        "OnlineSecurity": online_security,
        "OnlineBackup": online_backup,
        "DeviceProtection": device_protection,
        "TechSupport": tech_support,
        "StreamingTV": streaming_tv,
        "StreamingMovies": streaming_movies,
        "Contract": contract,
        "PaperlessBilling": paperless_billing,
        "PaymentMethod": payment_method,
        "MonthlyCharges": monthly_charges,
        "TotalCharges": str(total_charges)
    }

    # Send a request to the API.
    try:
        with st.spinner("The model is thinking..."):
            response = requests.post(f"{API_URL}/predict", json=input_data)
            
        if response.status_code == 200:
            result = response.json()
            prediction = result["prediction"]
            status = result["status"]
            
            st.markdown("---")
            if prediction == 1:
                st.error(f"RESULT: {status}")
                st.warning("This customer is high-risk! An urgent campaign must be launched.")
            else:
                st.success(f"RESULT: {status}")
                st.info("The customer seems satisfied.")
        else:
            st.error(f"Error: {response.text}")
            
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")