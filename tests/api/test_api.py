# --- TESTS ---


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
