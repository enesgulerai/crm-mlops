import streamlit as st
import requests
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="CRM Churn Predictor | MLOps",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        font-weight: bold;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)


# --- API CONNECTION ---
API_URL = os.getenv("API_URL", "http://localhost:8000")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3256/3256114.png", width=100)
    st.title("System Status")
    st.markdown("---")
    
    try:
        test_url = f"{API_URL}/docs"
        response = requests.get(test_url, timeout=2)
        if response.status_code == 200:
            st.success("🟢 API Online", icon="✅")
            st.caption(f"Connected to: {API_URL}")
        else:
            st.error("🔴 API Offline", icon="🚨")
    except Exception:
        st.error("🔴 Connection Failed", icon="🚨")
        
    st.markdown("---")
    st.markdown("""
        **Model Info:**
        - Engine: XGBoost
        - Format: ONNX
        - Deployment: Helm
    """)

# --- HEADER SECTION ---
st.title("Customer Churn Analysis")
st.markdown("""
    Evaluate customer retention probability using our advanced MLOps pipeline. 
    Adjust the parameters below to run real-time predictions.
""")
st.divider()

# --- INPUT SECTIONS (TABS) ---
tab1, tab2, tab3 = st.tabs(["👤 Demographics", "⚙️ Services", "💳 Billing & Contracts"])

with tab1:
    st.subheader("Personal Information")
    col1, col2 = st.columns(2)
    with col1:
        gender = st.radio("Gender", ["Female", "Male"], horizontal=True)
        partner = st.selectbox("Has Partner?", ["Yes", "No"])
    with col2:
        senior_citizen = st.selectbox("Senior Citizen (>65)?", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
        dependents = st.selectbox("Has Dependents?", ["Yes", "No"])

with tab2:
    st.subheader("Active Subscriptions")
    col1, col2, col3 = st.columns(3)
    with col1:
        phone_service = st.selectbox("Phone Service", ["Yes", "No"])
        multiple_lines = st.selectbox("Multiple Lines", ["Yes", "No", "No phone service"])
        internet_service = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])
    with col2:
        online_security = st.selectbox("Online Security", ["Yes", "No", "No internet service"])
        online_backup = st.selectbox("Online Backup", ["Yes", "No", "No internet service"])
        device_protection = st.selectbox("Device Protection", ["Yes", "No", "No internet service"])
    with col3:
        tech_support = st.selectbox("Tech Support", ["Yes", "No", "No internet service"])
        streaming_tv = st.selectbox("Streaming TV", ["Yes", "No", "No internet service"])
        streaming_movies = st.selectbox("Streaming Movies", ["Yes", "No", "No internet service"])

with tab3:
    st.subheader("Financial Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        tenure = st.slider("Tenure (Months)", min_value=0, max_value=100, value=12)
        contract = st.selectbox("Contract Type", ["Month-to-month", "One year", "Two year"])
    with col2:
        paperless_billing = st.radio("Paperless Billing", ["Yes", "No"], horizontal=True)
        payment_method = st.selectbox("Payment Method", ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"])
    with col3:
        monthly_charges = st.number_input("Monthly Charges ($)", min_value=0.0, value=50.0, step=5.0)
        total_charges = st.number_input("Total Charges ($)", min_value=0.0, value=500.0, step=50.0)

st.markdown("<br>", unsafe_allow_html=True)

# --- ACTION SECTION ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    predict_button = st.button("🚀 Analyze Churn Risk", type="primary", use_container_width=True)

if predict_button:
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
        "TotalCharges": str(total_charges),
    }

    try:
        with st.spinner("Analyzing risk factors..."):
            response = requests.post(f"{API_URL}/predict", json=input_data, timeout=5)

        if response.status_code == 200:
            result = response.json()
            prediction = result["prediction"]
            status = result["status"]
            
            st.divider()
            
            # --- RESULTS DASHBOARD ---
            res_col1, res_col2 = st.columns(2)
            
            if prediction == 1:
                with res_col1:
                    st.error("🚨 HIGH CHURN RISK DETECTED")
                    st.markdown(f"**Status:** {status}")
                    st.markdown("Immediate retention action is required for this customer.")
                with res_col2:
                    st.metric(label="Risk Assessment", value="Critical", delta="-Retention Action Needed", delta_color="inverse")
            else:
                with res_col1:
                    st.success("✅ LOW CHURN RISK")
                    st.markdown(f"**Status:** {status}")
                    st.markdown("Customer exhibits stable engagement patterns.")
                with res_col2:
                    st.metric(label="Risk Assessment", value="Stable", delta="Customer is Safe", delta_color="normal")
                    
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")

    except requests.exceptions.Timeout:
         st.error("Timeout Error: The API took too long to respond.")
    except Exception as e:
        st.error(f"System Error: {str(e)}")