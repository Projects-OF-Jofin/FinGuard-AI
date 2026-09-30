"""FinGuard AI - FastAPI backend."""

import sys
import os
import pandas as pd

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# ==========================================================
# PROJECT PATH
# ==========================================================

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)


# ==========================================================
# ML
# ==========================================================

from src.feature_engineering import create_features
from src.predict import predict_transaction
from src.explain import explain_transaction


# ==========================================================
# DATABASE
# ==========================================================

from backend.app.database import (
    initialize_database,
    save_transaction,
    get_recent_transactions,
    get_transaction,
    get_fraud_alerts,
    get_dashboard_stats
)


# ==========================================================
# FASTAPI
# ==========================================================

app = FastAPI(
    title="FinGuard AI",
    description="Real-Time Financial Fraud & Anomaly Detection Platform",
    version="1.0.0"
)


# ==========================================================
# CORS
# ==========================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ==========================================================
# STARTUP
# ==========================================================

@app.on_event("startup")
def startup_event():
    try:
        initialize_database()
    except Exception as exc:  # pragma: no cover - env-specific startup warning
        print(f"Database startup warning: {exc}")


# ==========================================================
# REQUEST MODEL
# ==========================================================

class TransactionRequest(BaseModel):

    transaction_id: str = Field(
        ...,
        example="TXN_TEST_001"
    )

    user_id: str = Field(
        ...,
        example="USER000001"
    )

    timestamp: str = Field(
        ...,
        example="2026-09-30 18:30:00"
    )

    amount: float = Field(
        ...,
        example=45000.00
    )

    merchant_id: str = Field(
        ...,
        example="MERCHANT000001"
    )

    merchant_category: str = Field(
        ...,
        example="electronics"
    )

    location: str = Field(
        ...,
        example="Kozhikode"
    )

    device_id: str = Field(
        ...,
        example="DEVICE000001"
    )

    ip_address: str = Field(
        ...,
        example="192.0.2.10"
    )

    payment_method: str = Field(
        ...,
        example="upi"
    )

    account_age: float = Field(
        ...,
        example=500
    )

    transaction_count_24h: float = Field(
        ...,
        example=25
    )

    avg_transaction_amount: float = Field(
        ...,
        example=2500
    )

    distance_from_home: float = Field(
        ...,
        example=1200
    )

    is_new_device: int = Field(
        ...,
        example=1
    )

    is_new_location: int = Field(
        ...,
        example=1
    )


# ==========================================================
# ROOT
# ==========================================================

@app.get("/")
def root():

    return {
        "application": "FinGuard AI",
        "status": "running",
        "version": "1.0.0"
    }


# ==========================================================
# HEALTH
# ==========================================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "model": "XGBoost",
        "database": "PostgreSQL",
        "service": "Fraud Detection API"
    }


# ==========================================================
# PREDICT
# ==========================================================

@app.post("/predict")
def predict(transaction: TransactionRequest):

    try:

        # Convert request into DataFrame
        payload = (
            transaction.model_dump()
            if hasattr(transaction, "model_dump")
            else transaction.dict()
        )
        transaction_data = pd.DataFrame([payload])


        # --------------------------------------------------
        # FEATURE ENGINEERING
        # --------------------------------------------------

        engineered_data = create_features(
            transaction_data
        )


        # --------------------------------------------------
        # REMOVE NON-MODEL COLUMNS
        # --------------------------------------------------

        columns_to_drop = [

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

            "new_merchant_for_user"
        ]


        model_features = engineered_data.drop(
            columns=[
                column
                for column in columns_to_drop
                if column in engineered_data.columns
            ],
            errors="ignore"
        )


        # --------------------------------------------------
        # XGBOOST PREDICTION
        # --------------------------------------------------

        prediction = predict_transaction(
            model_features
        )[0]


        # --------------------------------------------------
        # SHAP EXPLANATION
        # --------------------------------------------------

        reasons = explain_transaction(
            model_features,
            top_n=5
        )


        prediction["reasons"] = reasons


        # --------------------------------------------------
        # SAVE TO POSTGRESQL
        # --------------------------------------------------

        save_transaction(
            transaction,
            prediction
        )


        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------

        return {

            "success": True,

            "transaction_id":
                transaction.transaction_id,

            "prediction":
                prediction,

            "database_saved":
                True
        }


    except Exception as e:

        print(
            "Prediction error:",
            repr(e)
        )

        raise HTTPException(

            status_code=500,

            detail={

                "success": False,

                "error": str(e)
            }
        )


# ==========================================================
# RECENT TRANSACTIONS
# ==========================================================

@app.get("/transactions")
def transactions(limit: int = 50):

    try:

        limit = min(
            max(limit, 1),
            500
        )


        results = get_recent_transactions(
            limit
        )


        return {

            "success": True,

            "count": len(results),

            "transactions":
                results
        }


    except Exception as e:

        print(
            "Transactions error:",
            repr(e)
        )

        raise HTTPException(

            status_code=500,

            detail={

                "success": False,

                "error": str(e)
            }
        )


# ==========================================================
# SINGLE TRANSACTION
# ==========================================================

@app.get("/transactions/{transaction_id}")
def transaction_details(
    transaction_id: str
):

    try:

        result = get_transaction(
            transaction_id
        )


        if result is None:

            raise HTTPException(
                status_code=404,
                detail="Transaction not found"
            )


        return {

            "success": True,

            "transaction":
                result
        }


    except HTTPException:

        raise


    except Exception as e:

        print(
            "Transaction detail error:",
            repr(e)
        )

        raise HTTPException(

            status_code=500,

            detail={

                "success": False,

                "error": str(e)
            }
        )


# ==========================================================
# FRAUD ALERTS
# ==========================================================

@app.get("/fraud-alerts")
def fraud_alerts(limit: int = 50):

    try:

        limit = min(
            max(limit, 1),
            500
        )


        results = get_fraud_alerts(
            limit
        )


        return {

            "success": True,

            "count": len(results),

            "alerts":
                results
        }


    except Exception as e:

        print(
            "Fraud alerts error:",
            repr(e)
        )

        raise HTTPException(

            status_code=500,

            detail={

                "success": False,

                "error": str(e)
            }
        )


# ==========================================================
# DASHBOARD STATISTICS
# ==========================================================

@app.get("/stats")
def dashboard_stats():

    try:

        stats = get_dashboard_stats()


        return {

            "success": True,

            "statistics":
                stats
        }


    except Exception as e:

        print(
            "Stats error:",
            repr(e)
        )

        raise HTTPException(

            status_code=500,

            detail={

                "success": False,

                "error": str(e)
            }
        )