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
REDIS_TIMEOUT = float(os.getenv("REDIS_TIMEOUT", 1.0))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=6379,
    db=0,
    decode_responses=True,
    socket_connect_timeout=REDIS_TIMEOUT,
    socket_timeout=REDIS_TIMEOUT,
)

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
    input_data = data.model_dump()
    cache_key = f"churn_pred:{generate_cache_key(input_data)}"

    try:
        cached_result = redis_client.get(cache_key)
        if cached_result:
            response = json.loads(cached_result)
            response["source"] = "Redis Cache"
            return response
    except Exception as e:
        print(f"Warning: Redis read failed (Cache skipped). Details: {e}")

    try:
        pipeline = ml_models["pipeline"]
        prediction = pipeline.predict(input_data)

        pred_value = (
            int(prediction[0])
            if isinstance(prediction, (list, tuple, object)) and hasattr(prediction, "__iter__")
            else int(prediction)
        )

        result = "Churn" if pred_value == 1 else "Not Churn"

        response_data = {
            "prediction": pred_value,
            "status": result,
            "source": "ML Model",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model prediction error: {str(e)}")

    try:
        redis_client.setex(cache_key, 3600, json.dumps(response_data))
    except Exception as e:
        print(f"Warning: Redis write failed. Details: {e}")

    return response_data


if __name__ == "__main__":
    uvicorn.run("src.api.app:app", host="127.0.0.1", port=8000, reload=True)
