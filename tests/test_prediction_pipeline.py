import os
import sys
from unittest.mock import patch

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.main import app
from fastapi.testclient import TestClient
from src.explain import explain_transaction
from src.feature_engineering import create_features
from src.predict import predict_transaction


def build_sample_transaction():
    return pd.DataFrame([
        {
            "transaction_id": "TEST001",
            "user_id": "USER000001",
            "timestamp": "2026-09-30 18:30:00",
            "amount": 45000.00,
            "merchant_id": "MERCHANT000001",
            "merchant_category": "electronics",
            "location": "Kozhikode",
            "device_id": "DEVICE000001",
            "ip_address": "192.0.2.10",
            "payment_method": "upi",
            "account_age": 500,
            "transaction_count_24h": 25,
            "avg_transaction_amount": 2500,
            "distance_from_home": 1200,
            "is_new_device": 1,
            "is_new_location": 1,
        }
    ])


def test_feature_engineering_creates_expected_columns():
    df = build_sample_transaction()
    features = create_features(df)

    assert "amount_deviation_ratio" in features.columns
    assert "data_quality_issue" in features.columns
    assert features.shape[0] == 1


def test_prediction_returns_expected_schema():
    df = build_sample_transaction()
    features = create_features(df)
    drop_columns = [
        "transaction_id",
        "id",
        "user_id",
        "merchant_id",
        "device_id",
        "ip_address",
        "timestamp",
        "previous_timestamp",
        "device_user_count",
        "device_transaction_count",
        "location_transaction_count",
        "user_location_transaction_count",
        "user_merchant_transaction_count",
        "user_category_transaction_count",
        "new_merchant_for_user",
        "is_fraud",
    ]
    model_features = features[[col for col in features.columns if col not in drop_columns]]

    prediction = predict_transaction(model_features)[0]

    assert set(prediction) == {"fraud_probability", "risk_score", "is_fraud", "risk_level"}
    assert 0.0 <= prediction["fraud_probability"] <= 1.0
    assert prediction["risk_score"] >= 0
    assert prediction["risk_level"] in {"LOW", "MEDIUM", "HIGH"}


def test_risk_classification_is_consistent():
    df = build_sample_transaction()
    features = create_features(df)
    drop_columns = [
        "transaction_id",
        "id",
        "user_id",
        "merchant_id",
        "device_id",
        "ip_address",
        "timestamp",
        "previous_timestamp",
        "device_user_count",
        "device_transaction_count",
        "location_transaction_count",
        "user_location_transaction_count",
        "user_merchant_transaction_count",
        "user_category_transaction_count",
        "new_merchant_for_user",
        "is_fraud",
    ]
    model_features = features[[col for col in features.columns if col not in drop_columns]]
    prediction = predict_transaction(model_features)[0]

    if prediction["risk_level"] == "HIGH":
        assert prediction["fraud_probability"] >= 0.75
    elif prediction["risk_level"] == "MEDIUM":
        assert 0.25 <= prediction["fraud_probability"] < 0.75
    else:
        assert prediction["fraud_probability"] < 0.25


def test_explain_transaction_returns_feature_reasons():
    df = build_sample_transaction()
    features = create_features(df)
    drop_columns = [
        "transaction_id",
        "id",
        "user_id",
        "merchant_id",
        "device_id",
        "ip_address",
        "timestamp",
        "previous_timestamp",
        "device_user_count",
        "device_transaction_count",
        "location_transaction_count",
        "user_location_transaction_count",
        "user_merchant_transaction_count",
        "user_category_transaction_count",
        "new_merchant_for_user",
        "is_fraud",
    ]
    model_features = features[[col for col in features.columns if col not in drop_columns]]

    reasons = explain_transaction(model_features, top_n=3)

    assert isinstance(reasons, list)
    assert len(reasons) > 0
    assert set(reasons[0]) == {"feature", "impact", "direction"}


def test_predict_endpoint_is_available():
    client = TestClient(app)
    payload = {
        "transaction_id": "TEST_API_001",
        "user_id": "USER000002",
        "timestamp": "2026-09-30 18:30:00",
        "amount": 45000.0,
        "merchant_id": "MERCHANT000002",
        "merchant_category": "electronics",
        "location": "Kozhikode",
        "device_id": "DEVICE000002",
        "ip_address": "192.0.2.11",
        "payment_method": "upi",
        "account_age": 500,
        "transaction_count_24h": 25,
        "avg_transaction_amount": 2500,
        "distance_from_home": 1200,
        "is_new_device": 1,
        "is_new_location": 1,
    }

    with patch("backend.app.main.save_transaction") as mock_save:
        response = client.post("/predict", json=payload)

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "prediction" in response.json()
    mock_save.assert_called_once()


def test_health_endpoint_is_available():
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
