# Synthetic Dataset Notes

This project uses a synthetic financial transaction dataset for model training, validation, and demonstration. The data is intentionally designed to simulate fraud and anomaly patterns without exposing real customer or financial data.

## Approximate Size

- ~1,000,000 synthetic transactions
- ~30% fraud rate
- ~12,000 users
- ~5,000 merchants
- ~20,000 devices

## Major Fields

- transaction_id
- user_id
- timestamp
- amount
- merchant_id
- merchant_category
- location
- device_id
- ip_address
- payment_method
- account_age
- transaction_count_24h
- avg_transaction_amount
- distance_from_home
- is_new_device
- is_new_location
- is_fraud

## Known Anomaly Types

- missing values
- negative amounts
- negative distances
- invalid timestamps
- unknown categories
- duplicate transaction IDs
- missing user IDs
- missing merchant IDs

## Fraud Scenarios

- transaction amount anomalies
- new device usage patterns
- unusual locations
- rapid velocity attacks
- merchant/category anomalies
- combined attack behaviors

## Why the Full Dataset Is Not Stored Here

The complete synthetic dataset is large and generated for local experimentation. It is intentionally kept out of GitHub to keep the repository lightweight and avoid committing large generated CSV files.

## Model Metrics Disclaimer

The published metrics are specific to this synthetic chronological test dataset. They are not real-world bank fraud performance numbers and should not be used as a production accuracy claim.
