import os
import sys

import joblib
import numpy as np
import onnxruntime as ort
import pandas as pd

from src.utils.exception import CustomException


class PredictPipeline:
    def __init__(self):
        # --- PATH ---
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "../../"))

        self.model_path = os.path.join(project_root, "models", "churn_model.onnx")
        self.preprocessor_path = os.path.join(project_root, "models", "preprocessor.pkl")

        # Control Mechanism
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"MODEL NOT FOUND! Checked path: {self.model_path}")
        if not os.path.exists(self.preprocessor_path):
            raise FileNotFoundError(
                f"PREPROCESSOR NOT FOUND! Checked path: {self.preprocessor_path}"
            )

        # Load the Model and Preprocessor ONLY ONCE (Load the disk only initially)
        self.session = ort.InferenceSession(self.model_path)
        self.preprocessor = joblib.load(self.preprocessor_path)

    def predict(self, features):
        try:
            # 1. Data Preparation
            df = pd.DataFrame([features])

            if "TotalCharges" in df.columns:
                df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0)
            if "MonthlyCharges" in df.columns:
                df["MonthlyCharges"] = pd.to_numeric(df["MonthlyCharges"], errors="coerce").fillna(
                    0
                )
            if "tenure" in df.columns:
                df["tenure"] = pd.to_numeric(df["tenure"], errors="coerce").fillna(0)

            # 2. Use the preprocessor that is already in RAM (it doesn't go to disk, it's very fast)
            data_scaled = self.preprocessor.transform(df)

            # 3. Use the ONNX model already stored in RAM.
            input_name = self.session.get_inputs()[0].name
            label_name = self.session.get_outputs()[0].name
            pred_onx = self.session.run([label_name], {input_name: data_scaled.astype(np.float32)})[
                0
            ]

            return pred_onx[0]

        except Exception as e:
            print(f"Prediction Error: {str(e)}")
            raise CustomException(e, sys)
