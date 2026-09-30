"""
FinGuard AI - SHAP Model Explainability
"""

import os
import joblib
import numpy as np
import pandas as pd
import shap


# ============================================================
# PROJECT PATH
# ============================================================

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


# ============================================================
# LOAD MODEL
# ============================================================

model = joblib.load(MODEL_PATH)

preprocessor = joblib.load(
    PREPROCESSOR_PATH
)


# ============================================================
# SHAP EXPLAINER
# ============================================================

explainer = shap.TreeExplainer(model)


# ============================================================
# HUMAN-READABLE FEATURE NAMES
# ============================================================

def clean_feature_name(feature):

    name = feature.replace(
        "numeric__",
        ""
    )

    name = name.replace(
        "categorical__",
        ""
    )

    replacements = {

        "transaction_count_24h":
            "Transaction velocity (24h)",

        "is_new_device":
            "New device",

        "is_new_location":
            "New location",

        "amount":
            "Transaction amount",

        "avg_transaction_amount":
            "Average transaction amount",

        "distance_from_home":
            "Distance from home",

        "account_age":
            "Account age",

        "amount_deviation_ratio":
            "Amount deviation",

        "amount_zscore":
            "Amount z-score",

        "seconds_since_previous":
            "Time since previous transaction",

        "rapid_transaction":
            "Rapid transaction",

        "user_transaction_history":
            "Transaction history",

        "long_distance_transaction":
            "Long-distance transaction",

        "day_of_week":
            "Day of week",

        "hour":
            "Transaction hour",

        "is_weekend":
            "Weekend transaction",

        "day":
            "Day of month",

        "month":
            "Month",

        "data_quality_issue":
            "Data quality issue",

        "flag_missing_amount":
            "Missing amount",

        "flag_negative_amount":
            "Negative amount",

        "flag_missing_user":
            "Missing user",

        "flag_missing_merchant":
            "Missing merchant",

        "flag_negative_distance":
            "Negative distance",

        "flag_duplicate_transaction":
            "Duplicate transaction",

        "flag_invalid_timestamp":
            "Invalid timestamp",

        "flag_unknown_category":
            "Unknown category"
    }


    if name in replacements:
        return replacements[name]


    if name.startswith(
        "merchant_category_"
    ):

        category = name.replace(
            "merchant_category_",
            ""
        )

        return (
            f"Merchant category: {category}"
        )


    if name.startswith("location_"):

        location = name.replace(
            "location_",
            ""
        )

        return (
            f"Location: {location}"
        )


    if name.startswith(
        "payment_method_"
    ):

        method = name.replace(
            "payment_method_",
            ""
        )

        return (
            f"Payment method: {method}"
        )


    return name.replace(
        "_",
        " "
    ).title()


# ============================================================
# EXPLAIN TRANSACTION
# ============================================================

def explain_transaction(
    features: pd.DataFrame,
    top_n: int = 5
):
    """
    Generate SHAP-based explanation
    for a single transaction.

    Parameters
    ----------
    features : pd.DataFrame
        Feature-engineered model input.

    top_n : int
        Number of important factors to return.
    """

    # --------------------------------------------------------
    # Transform using the SAME preprocessor used in training
    # --------------------------------------------------------

    X_processed = preprocessor.transform(
        features
    )


    # --------------------------------------------------------
    # Feature names
    # --------------------------------------------------------

    feature_names = (
        preprocessor
        .get_feature_names_out()
    )


    # --------------------------------------------------------
    # Calculate SHAP values
    # --------------------------------------------------------

    shap_values = explainer.shap_values(
        X_processed
    )


    # --------------------------------------------------------
    # Handle SHAP output formats
    # --------------------------------------------------------

    if isinstance(
        shap_values,
        list
    ):

        shap_values = shap_values[-1]


    shap_values = np.asarray(
        shap_values
    )


    # --------------------------------------------------------
    # First / only transaction
    # --------------------------------------------------------

    values = shap_values[0]


    # --------------------------------------------------------
    # Get top absolute contributors
    # --------------------------------------------------------

    top_indices = np.argsort(
        np.abs(values)
    )[::-1][:top_n]


    reasons = []


    for index in top_indices:

        impact = float(
            values[index]
        )


        # Ignore negligible effects
        if abs(impact) < 0.01:
            continue


        feature_name = clean_feature_name(
            feature_names[index]
        )


        if impact > 0:

            direction = (
                "increases_fraud_risk"
            )

        else:

            direction = (
                "decreases_fraud_risk"
            )


        reasons.append({

            "feature": feature_name,

            "impact": round(
                impact,
                4
            ),

            "direction": direction

        })


    return reasons