from src.pipeline.predict_pipeline import PredictPipeline

def test_predict_pipeline_returns_expected_format(valid_payload):
    """
    Tests the ML engine directly, passing a raw dictionary just like the API does.
    """
    # Initialize the engine
    pipeline = PredictPipeline()
    
    # Run the prediction by passing the raw dictionary directly
    prediction = pipeline.predict(valid_payload)
    
    # Assertions for the ML logic
    assert prediction is not None, "Prediction should not be None"
    
    # The output must be either 0 (No Churn) or 1 (Churn)
    # Cast to int to handle numpy.int64 gracefully
    assert int(prediction) in [0, 1], f"Unexpected prediction value: {prediction}"