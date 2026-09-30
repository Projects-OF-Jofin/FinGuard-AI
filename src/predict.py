import os
import joblib
import pandas as pd


# ==========================================
# PATH CONFIGURATION
# ==========================================

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "xgboost_model.pkl"
)

PREPROCESSOR_PATH = os.path.join(
    BASE_DIR,
    "models",
    "preprocessor.pkl"
)

CONFIG_PATH = os.path.join(
    BASE_DIR,
    "models",
    "model_config.pkl"
)


# ==========================================
# LOAD TRAINED ARTIFACTS
# ==========================================

model = joblib.load(MODEL_PATH)
preprocessor = joblib.load(PREPROCESSOR_PATH)
model_config = joblib.load(CONFIG_PATH)

THRESHOLD = model_config["threshold"]


# ==========================================
# PREDICT TRANSACTION
# ==========================================

def predict_transaction(features: pd.DataFrame):

    # Transform using the SAME preprocessor
    X_processed = preprocessor.transform(features)

    # Fraud probability
    fraud_probability = model.predict_proba(
        X_processed
    )[:, 1]

    results = []

    for probability in fraud_probability:

        # Final fraud decision
        is_fraud = int(
            probability >= THRESHOLD
        )

        # Risk level
        if probability >= 0.75:
            risk_level = "HIGH"
        elif probability >= 0.25:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        results.append({
            "fraud_probability": round(
                float(probability), 6
            ),
            "risk_score": round(
                float(probability * 100), 2
            ),
            "is_fraud": is_fraud,
            "risk_level": risk_level
        })

    return results