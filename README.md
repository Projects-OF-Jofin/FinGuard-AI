# FinGuard AI

## Real-Time Financial Fraud & Anomaly Detection Platform

FinGuard AI is a full-stack fraud detection platform for transaction monitoring, anomaly detection, explainable ML, and investigation workflows. It combines feature engineering, an XGBoost model, a FastAPI backend, PostgreSQL persistence, and a React dashboard into a single operational prototype.

> The current model was trained and evaluated using synthetic transaction data. Production deployment would require representative real transaction data, institution-specific feature mapping, retraining, calibration, and validation.

## Screenshots

The dashboard includes:

- KPI cards for total transactions, fraud counts, and risk levels
- Activity and risk charts
- Fraud alert feed
- Recent transaction table
- Search and filter tools
- Transaction investigation panel with SHAP reasons

## Architecture

```text
Incoming Transaction
    ↓
Validation
    ↓
Feature Engineering
    ↓
Preprocessing
    ↓
XGBoost Fraud Model
    ↓
Fraud Probability + Risk Classification
    ↓
SHAP Explanation
    ↓
PostgreSQL Storage
    ↓
React Dashboard
```

## Features

- Synthetic transaction ingestion and validation
- Feature engineering for behavioral anomalies
- Risk scoring and fraud classification
- SHAP explainability for transaction investigations
- Transaction history persistence in PostgreSQL
- REST API for real-time scoring and dashboard data
- Dark-mode monitoring dashboard in React and TypeScript

## Dataset

The repository uses a synthetic financial transaction dataset designed to simulate a realistic fraud detection scenario. It contains approximately:

- 1,000,000 synthetic transactions
- 12,000 users
- 5,000 merchants
- ~20,000 devices
- ~30% fraud incidence

The dataset intentionally includes quality problems such as missing values, negative amounts, negative distances, invalid timestamps, unknown categories, duplicate IDs, and missing user/merchant identifiers. Fraud scenarios include amount anomalies, new device behavior, location anomalies, merchant/category anomalies, velocity attacks, and combined attacks.

## Data Validation

The validation utilities clean and normalize booleans and flag data-quality issues before model scoring. This helps keep the pipeline resilient to malformed or partially missing incoming data.

## Feature Engineering

Feature engineering includes:

- temporal patterns such as hour, day, weekend detection, and transaction history
- amount deviation and z-score calculations
- rapid transaction detection using seconds-since-previous logic
- distance-based behavioral indicators
- quality flags for suspicious transaction records

The trained model intentionally excludes obvious leakage signals that were not used for final prediction.

## XGBoost Model

The model artifact is an XGBoost classifier trained on engineered features. The prediction pipeline loads the saved preprocessor and model configuration before generating a fraud probability and risk label.

## Model Metrics

Performance on the synthetic chronological test dataset:

- Accuracy: 96.13%
- Precision: 98.89%
- Recall: 88.07%
- F1: 93.17%
- ROC-AUC: 98.14%
- PR-AUC: 96.98%

Training: January–July 2026
Validation: August 2026
Testing: September 2026

## SHAP Explainability

The project generates SHAP explanations for each scored transaction and highlights the most influential features affecting fraud likelihood. These explanations power the investigation panel and help explain why a given transaction was flagged.

## Technology Stack

- Python
- Pandas
- NumPy
- Scikit-learn
- XGBoost
- SHAP
- FastAPI
- PostgreSQL
- React
- TypeScript
- Vite
- Axios
- Recharts
- Lucide React

## Project Structure

```text
FinGuard-AI/
├── backend/
│   └── app/
│       ├── __init__.py
│       ├── database.py
│       └── main.py
├── data/
│   ├── README.md
│   ├── sample/
│   │   └── sample_transactions.csv
│   └── transactions.csv
├── docs/
│   └── architecture.md
├── frontend/
│   ├── package.json
│   ├── package-lock.json
│   └── src/
├── models/
│   ├── xgboost_model.pkl
│   ├── preprocessor.pkl
│   └── model_config.pkl
├── notebooks/
├── src/
│   ├── __init__.py
│   ├── data_validation.py
│   ├── explain.py
│   ├── feature_engineering.py
│   ├── predict.py
│   └── train.py
├── tests/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
├── requirements.txt
└── ...
```

## Installation

1. Create a virtual environment.
2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Install frontend dependencies:

```bash
cd frontend
npm install
```

## PostgreSQL Setup

Create a local PostgreSQL database and set environment variables before starting the API:

```bash
cp .env.example .env
```

Then adjust the values as needed:

```env
FINGUARD_DB_HOST=localhost
FINGUARD_DB_PORT=5432
FINGUARD_DB_NAME=finguard
FINGUARD_DB_USER=postgres
FINGUARD_DB_PASSWORD=your_password_here
```

## Backend Startup

```bash
uvicorn backend.app.main:app --reload
```

The API exposes the following endpoints:

- GET /
- GET /health
- POST /predict
- GET /transactions
- GET /transactions/{transaction_id}
- GET /fraud-alerts
- GET /stats

## Frontend Startup

```bash
cd frontend
npm run dev
```

The app expects the backend at http://127.0.0.1:8000 and the Vite dev server at http://localhost:5173.

## API Endpoints

### POST /predict

Accepts a transaction payload and returns:

- fraud_probability
- risk_score
- is_fraud
- risk_level
- reasons

### GET /stats

Returns aggregated dashboard metrics including total transactions, fraud counts, and risk distribution.

## Prediction Workflow

1. Incoming transaction is validated.
2. Data quality flags are generated.
3. Feature engineering creates behavioral and anomaly signals.
4. Preprocessor transforms the feature set.
5. XGBoost predicts a fraud probability.
6. Risk is classified as LOW, MEDIUM, or HIGH.
7. SHAP identifies the strongest reasons.
8. Results are saved to PostgreSQL and shown in the dashboard.

## Risk Classification

- HIGH: probability >= 0.75
- MEDIUM: 0.25 <= probability < 0.75
- LOW: probability < 0.25

## Limitations

- The model is trained on synthetic data only.
- Results should not be interpreted as real-world financial risk forecasts.
- Real deployment requires domain-specific feature engineering and validation on production data.

## Future Improvements

- Connect to real banking transaction feeds
- Add role-based investigation workflows
- Expand monitoring and alerting
- Improve model calibration and threshold tuning
- Add CI/CD and deployment automation

## Author

FinGuard AI is a prototype built for demonstration, experimentation, and analytics in fraud detection workflows.
