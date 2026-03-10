import os
import pandas as pd
import pytest
from src.components.data_transformation import DataTransformation

@pytest.fixture
def dummy_raw_data():
    """
    A complete simulation of the Telco Churn dataset containing all required 19 columns.
    """
    data = {
        "gender": ["Female", "Male", "Male"],
        "SeniorCitizen": [0, 1, 0],
        "Partner": ["Yes", "No", "Yes"],
        "Dependents": ["No", "Yes", "No"],
        "tenure": [1, 34, 2],
        "PhoneService": ["No", "Yes", "Yes"],
        "MultipleLines": ["No phone service", "Yes", "No"],
        "InternetService": ["DSL", "Fiber optic", "No"],
        "OnlineSecurity": ["No", "Yes", "No internet service"],
        "OnlineBackup": ["Yes", "No", "No internet service"],
        "DeviceProtection": ["No", "Yes", "No internet service"],
        "TechSupport": ["No", "No", "No internet service"],
        "StreamingTV": ["No", "Yes", "No internet service"],
        "StreamingMovies": ["No", "No", "No internet service"],
        "Contract": ["Month-to-month", "One year", "Month-to-month"],
        "PaperlessBilling": ["Yes", "No", "No"],
        "PaymentMethod": ["Electronic check", "Mailed check", "Bank transfer (automatic)"],
        "MonthlyCharges": [29.85, 56.95, 53.85],
        "TotalCharges": ["29.85", "1889.5", "108.15"],
        "Churn": ["No", "No", "Yes"]
    }
    return pd.DataFrame(data)

def test_data_transformation_pipeline(dummy_raw_data, tmp_path):
    """
    Tests if the DataTransformation class correctly builds the preprocessor,
    applies scaling/encoding, and changes the shape of the dataframe as expected.
    """
    # 1. Initialize the transformer component
    transformer = DataTransformation()
    
    # Override the save path to a temporary directory using pytest's built-in tmp_path
    # This ensures we don't accidentally overwrite our production preprocessor.pkl during tests
    if hasattr(transformer, "data_transformation_config"):
        transformer.data_transformation_config.preprocessor_obj_file_path = os.path.join(
            tmp_path, "test_preprocessor.pkl"
        )
    
    # 2. Separate features from the target
    X = dummy_raw_data.drop(columns=["Churn"])
    
    # Simulate the raw string-to-numeric conversion if it happens before the transformer
    if "TotalCharges" in X.columns:
        X["TotalCharges"] = pd.to_numeric(X["TotalCharges"], errors="coerce").fillna(0)
        
    # 3. Get the preprocessor object (ColumnTransformer)
    # Note: Adjust the method name 'get_data_transformer_object' if it differs in your codebase
    preprocessor = transformer.get_data_transformer_object()
    
    # 4. Apply the transformation
    X_transformed = preprocessor.fit_transform(X)
    
    # --- ASSERTIONS ---
    
    # Check that the output is not empty
    assert X_transformed is not None, "Transformed data should not be None"
    
    # Check that the number of rows remained exactly the same
    assert X_transformed.shape[0] == X.shape[0], "Row count mismatch after transformation"
    
    # Check that the number of columns increased due to One-Hot Encoding
    assert X_transformed.shape[1] > X.shape[1], "Column count should increase after OHE"