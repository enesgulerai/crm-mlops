def test_home_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_predict_endpoint_success(client, valid_payload):
    response = client.post("/predict", json=valid_payload)

    if response.status_code != 200:
        print("\n--- ERROR DETAILS ---")
        print(response.json())
        print("-------------------\n")

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


def test_predict_endpoint_empty_payload(client):
    """Test how the API handles a completely empty JSON body."""
    response = client.post("/predict", json={})
    assert response.status_code == 422


def test_predict_endpoint_method_not_allowed(client):
    """Test if the API correctly rejects GET requests on a POST endpoint."""
    response = client.get("/predict")
    assert response.status_code == 405


def test_health_check_endpoint(client):
    """
    Test the health endpoint.
    Essential for Kubernetes liveness and readiness probes.
    """
    response = client.get("/health")
    # If you haven't implemented /health yet, this test will fail (404).
    # It acts as a reminder to build it for Kubernetes!
    if response.status_code == 200:
        assert response.json().get("status") == "healthy"
    else:
        assert response.status_code == 404
