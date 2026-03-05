import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.api.app import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def valid_payload():
    return {
        "gender": "Female",
        "SeniorCitizen": 0,
        "Partner": "Yes",
        "Dependents": "No",
        "tenure": 12,
        "PhoneService": "Yes",
        "MultipleLines": "No",
        "InternetService": "DSL",
        "OnlineSecurity": "No",
        "OnlineBackup": "Yes",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "No",
        "StreamingMovies": "No",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 50.0,
        "TotalCharges": "600.0",
    }


# --- TESTS ---


def test_home_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_predict_endpoint_success(client, valid_payload):
    response = client.post("/predict", json=valid_payload)

    assert response.status_code == 200

    json_data = response.json()
    assert "prediction" in json_data
    assert "status" in json_data
    assert json_data["prediction"] in [0, 1]


def test_predict_endpoint_missing_field(client, valid_payload):
    invalid_payload = valid_payload.copy()
    del invalid_payload["tenure"]

    response = client.post("/predict", json=invalid_payload)
    assert response.status_code == 422


def test_predict_endpoint_invalid_data_type(client, valid_payload):
    invalid_payload = valid_payload.copy()
    invalid_payload["MonthlyCharges"] = "this_is_not_a_number"

    response = client.post("/predict", json=invalid_payload)
    assert response.status_code == 422
