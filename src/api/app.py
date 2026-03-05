import sys
import os
import json
import hashlib
import redis
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# --- PATH ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.pipeline.predict_pipeline import PredictPipeline

# --- REDIS ---
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

ml_models = {}


# --- LIFESPAN ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # When starting the application: Upload the model ONLY ONCE.
    print("Loading ML Model into RAM... Please wait.")
    ml_models["pipeline"] = PredictPipeline()
    print("The model has been uploaded and the API is ready to receive requests!")
    yield
    # Clear RAM when the application closes.
    ml_models.clear()
    print("API closed, memory cleared.")


app = FastAPI(title="CRM Churn Prediction API", version="2.0", lifespan=lifespan)


# --- DATA VERIFICATION (Pydantic) ---
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
    TotalCharges: float


# --- AUXILIARY FUNCTION: Request Hashing ---
def generate_cache_key(data_dict: dict) -> str:
    """It converts the incoming JSON data into a unique hash."""
    data_str = json.dumps(data_dict, sort_keys=True)
    return hashlib.md5(data_str.encode()).hexdigest()


@app.get("/")
def home():
    return {"message": "API is Running with Redis Cache"}


@app.post("/predict")
def predict_churn(data: CustomerData):
    try:
        input_data = data.model_dump()

        # STEP 1: Check on Redis if this customer has been requested before.
        cache_key = f"churn_pred:{generate_cache_key(input_data)}"
        cached_result = redis_client.get(cache_key)

        if cached_result:
            # If it exists in Redis, just spin it directly without running the model at all.
            response = json.loads(cached_result)
            response["source"] = "Redis Cache"  # Let it show us where it came from
            return response

        # STEP 2: If it's not in Redis, use a pre-existing model in RAM and make a prediction.
        pipeline = ml_models["pipeline"]
        prediction = pipeline.predict(input_data)

        result = "Churn" if prediction == 1 else "Not Churn"

        response_data = {
            "prediction": int(prediction),
            "status": result,
            "source": "ML Model",
        }

        # STEP 3: Save the result to Redis (For example: store for 1 hour = 3600 seconds)
        redis_client.setex(cache_key, 3600, json.dumps(response_data))

        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("src.api.app:app", host="127.0.0.1", port=8000, reload=True)
