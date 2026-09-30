# FinGuard AI Architecture

```text
Incoming Transaction
    ↓
Validation and Data Quality Checks
    ↓
Feature Engineering
    ↓
Preprocessing Pipeline
    ↓
XGBoost Fraud Model
    ↓
Fraud Probability + Risk Classification
    ↓
SHAP Explainability
    ↓
PostgreSQL Transaction Storage
    ↓
React Dashboard
```

## Pipeline Overview

1. A transaction enters the system via the FastAPI API.
2. Basic validation and data-quality flags are generated.
3. Behavioral and anomaly features are engineered.
4. The saved preprocessor transforms the features to model input.
5. The XGBoost classifier returns a fraud probability.
6. The probability is mapped to LOW, MEDIUM, or HIGH risk.
7. SHAP highlights the top feature drivers for investigation.
8. Results are stored in PostgreSQL for dashboard and audit use.

## Components

- Frontend: Vite + React + TypeScript dashboard
- Backend: FastAPI service with transaction prediction and investigation endpoints
- ML: Feature engineering and XGBoost classification with SHAP explanation
- Storage: PostgreSQL for transactions, predictions, and alerts

This repository is designed as a demonstration platform and is not a production banking deployment.
