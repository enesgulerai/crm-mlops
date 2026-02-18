import sys
import os
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import pandas as pd

# --- PATH ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.pipeline.predict_pipeline import PredictPipeline

app = FastAPI(title="CRM Churn Prediction API", version="1.0")

class CustomerData(BaseModel):
    gender: str
    SeniorCitizen: int
    Partner: str
    Dependents: str
    tenure: int
    PhoneService: str
    MultipleLines: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    Contract: str
    PaperlessBilling: str
    PaymentMethod: str
    MonthlyCharges: float
    TotalCharges: object 

@app.get("/")
def home():
    return {"message": "API is Running"}

@app.post("/predict")
def predict_churn(data: CustomerData):
    try:
        input_data = data.model_dump()
        
        pipeline = PredictPipeline()
        prediction = pipeline.predict(input_data)
        
        result = "Churn" if prediction == 1 else "Not Churn"
        return {"prediction": int(prediction), "status": result}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)