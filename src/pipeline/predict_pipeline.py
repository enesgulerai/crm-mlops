import sys
import os
import pandas as pd
import joblib
import onnxruntime as rt
import numpy as np

from src.utils.exception import CustomException

class PredictPipeline:
    def __init__(self):
        # --- PATH ---
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
        
        self.model_path = os.path.join(root_dir, "models", "churn_model.onnx")
        
        self.preprocessor_path = os.path.join(root_dir, "models", "preprocessor.pkl")
        
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"MODEL STILL NOT FOUND! Location being searched: {self.model_path}")

    def predict(self, features):
        try:
            # 1. Load Preprocessor 
            preprocessor = joblib.load(self.preprocessor_path)
            
            # 2. Load ONNX Model 
            sess = rt.InferenceSession(self.model_path)
            
            # 3. Data Preparation
            df = pd.DataFrame([features])
            
            if 'TotalCharges' in df.columns:
                df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce').fillna(0)
            if 'MonthlyCharges' in df.columns:
                df['MonthlyCharges'] = pd.to_numeric(df['MonthlyCharges'], errors='coerce').fillna(0)
            if 'tenure' in df.columns:
                df['tenure'] = pd.to_numeric(df['tenure'], errors='coerce').fillna(0)

            data_scaled = preprocessor.transform(df)
            
            # 4. Predict
            input_name = sess.get_inputs()[0].name
            label_name = sess.get_outputs()[0].name
            pred_onx = sess.run([label_name], {input_name: data_scaled.astype(np.float32)})[0]
            
            return pred_onx[0]

        except Exception as e:
            print(f"Prediction Error: {str(e)}")
            raise CustomException(e, sys)