from locust import HttpUser, task, between
import random


class ChurnPredictionUser(HttpUser):
    wait_time = between(1, 3)

    @task(1)
    def check_health(self):
        """A simple homepage request that checks if the API is up and running."""
        self.client.get("/", name="Health Check (/)")

    @task(5)
    def predict_churn(self):
        """The POST request (@task(5) is what will really strain the model and Redis, so it will run 5 times more frequently)."""

        payload = {
            "gender": "Female",
            "SeniorCitizen": 0,
            "Partner": "Yes",
            "Dependents": "No",
            "tenure": random.randint(1, 72),
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

        with self.client.post(
            "/predict",
            json=payload,
            catch_response=True,
            name="Predict Churn (/predict)",
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Error Code: {response.status_code}")
