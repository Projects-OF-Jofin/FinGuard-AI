import pandas as pd
import numpy as np


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create production features compatible with the
    FinGuard trained model.
    """

    df = df.copy()

    # ==========================================
    # DATA QUALITY FLAGS
    # ==========================================

    # Missing values
    df["flag_missing_amount"] = (
        df["amount"].isna().astype(int)
    )

    df["flag_missing_user"] = (
        df["user_id"].isna().astype(int)
    )

    df["flag_missing_merchant"] = (
        df["merchant_id"].isna().astype(int)
    )

    # Negative values
    df["flag_negative_amount"] = (
        df["amount"].lt(0).fillna(False).astype(int)
    )

    df["flag_negative_distance"] = (
        df["distance_from_home"].lt(0)
        .fillna(False)
        .astype(int)
    )

    # Invalid timestamp
    parsed_timestamp = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    df["flag_invalid_timestamp"] = (
        parsed_timestamp.isna().astype(int)
    )

    # Unknown category
    df["flag_unknown_category"] = (
        df["merchant_category"]
        .astype("string")
        .str.strip()
        .str.lower()
        .isin([
            "unknown",
            "unknown_category"
        ])
        .astype(int)
    )

    # Duplicate transaction
    # For a single incoming transaction this is 0.
    # The database/API layer can later perform real duplicate detection.
    if "transaction_id" in df.columns:
        df["flag_duplicate_transaction"] = (
            df["transaction_id"].duplicated(
                keep=False
            ).astype(int)
        )
    else:
        df["flag_duplicate_transaction"] = 0

    # Overall data quality flag
    quality_columns = [
        "flag_missing_amount",
        "flag_negative_amount",
        "flag_missing_user",
        "flag_missing_merchant",
        "flag_negative_distance",
        "flag_duplicate_transaction",
        "flag_invalid_timestamp",
        "flag_unknown_category"
    ]

    df["data_quality_issue"] = (
        df[quality_columns]
        .sum(axis=1)
        .gt(0)
        .astype(int)
    )

    # ==========================================
    # CLEAN VALUES AFTER FLAGGING
    # ==========================================

    # Preserve the anomaly through the flag,
    # but don't feed negative values to the model.
    df.loc[
        df["flag_negative_amount"] == 1,
        "amount"
    ] = np.nan

    df.loc[
        df["flag_negative_distance"] == 1,
        "distance_from_home"
    ] = np.nan

    # Normalize unknown category
    df["merchant_category"] = (
        df["merchant_category"]
        .astype("string")
        .str.strip()
        .str.lower()
        .replace(
            "unknown_category",
            "unknown"
        )
    )

    # Use parsed timestamp
    df["timestamp"] = parsed_timestamp

    # ==========================================
    # SORT BY USER + TIME
    # ==========================================

    if "user_id" in df.columns:

        df = df.sort_values(
            ["user_id", "timestamp"]
        ).reset_index(drop=True)

    # ==========================================
    # TEMPORAL FEATURES
    # ==========================================

    df["hour"] = df["timestamp"].dt.hour

    df["day_of_week"] = (
        df["timestamp"].dt.dayofweek
    )

    df["is_weekend"] = (
        df["day_of_week"] >= 5
    ).astype(int)

    df["day"] = df["timestamp"].dt.day

    df["month"] = df["timestamp"].dt.month

    # ==========================================
    # PREVIOUS TRANSACTION
    # ==========================================

    if "user_id" in df.columns:

        df["previous_timestamp"] = (
            df.groupby("user_id")["timestamp"]
            .shift(1)
        )

        df["seconds_since_previous"] = (
            df["timestamp"]
            - df["previous_timestamp"]
        ).dt.total_seconds()

        df["rapid_transaction"] = (
            df["seconds_since_previous"] <= 300
        ).astype(int)

        df["user_transaction_history"] = (
            df.groupby("user_id")
            .cumcount()
        )

    else:

        df["previous_timestamp"] = pd.NaT

        df["seconds_since_previous"] = np.nan

        df["rapid_transaction"] = 0

        df["user_transaction_history"] = 0

    # ==========================================
    # HISTORICAL SPENDING FEATURES
    # ==========================================

    if "user_id" in df.columns:

        df["user_previous_avg_amount"] = (
            df.groupby("user_id")["amount"]
            .transform(
                lambda x:
                x.shift(1)
                .expanding()
                .mean()
            )
        )

        df["user_previous_std_amount"] = (
            df.groupby("user_id")["amount"]
            .transform(
                lambda x:
                x.shift(1)
                .expanding()
                .std()
            )
        )

    else:

        df["user_previous_avg_amount"] = np.nan

        df["user_previous_std_amount"] = np.nan

    # ==========================================
    # AMOUNT BEHAVIOR
    # ==========================================

    df["amount_deviation_ratio"] = (
        df["amount"]
        /
        (df["user_previous_avg_amount"] + 1e-6)
    )

    df["amount_zscore"] = (
        (
            df["amount"]
            -
            df["user_previous_avg_amount"]
        )
        /
        (df["user_previous_std_amount"] + 1e-6)
    )

    df["amount_deviation_ratio"] = (
        df["amount_deviation_ratio"]
        .replace([np.inf, -np.inf], np.nan)
    )

    df["amount_zscore"] = (
        df["amount_zscore"]
        .replace([np.inf, -np.inf], np.nan)
    )

    # ==========================================
    # DISTANCE
    # ==========================================

    df["long_distance_transaction"] = (
        df["distance_from_home"] > 500
    ).astype(int)

    return df