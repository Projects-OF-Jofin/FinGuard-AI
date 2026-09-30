"""Validation utilities for transaction data."""
import pandas as pd
import numpy as np


BOOLEAN_MAP = {
    True: 1,
    False: 0,

    "True": 1,
    "False": 0,

    "true": 1,
    "false": 0,

    "TRUE": 1,
    "FALSE": 0,

    "yes": 1,
    "no": 0,

    "YES": 1,
    "NO": 0,
}


def clean_boolean_column(series: pd.Series) -> pd.Series:

    # Convert everything to string only after preserving
    # actual Python booleans.
    cleaned = series.copy()

    # Handle actual boolean values
    cleaned = cleaned.map(
        lambda x: (
            1 if x is True else
            0 if x is False else
            str(x).strip()
        )
    )

    # Normalize strings
    cleaned = cleaned.map(
        lambda x: BOOLEAN_MAP.get(
            x,
            np.nan
        )
    )

    return cleaned.astype("Float64")