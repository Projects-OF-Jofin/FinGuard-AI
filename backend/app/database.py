import os
import psycopg2
from psycopg2.extras import RealDictCursor, Json


DB_HOST = (
    os.getenv("FINGUARD_DB_HOST")
    or os.getenv("FINGuard_DB_HOST")
    or "localhost"
)
DB_PORT = (
    os.getenv("FINGUARD_DB_PORT")
    or os.getenv("FINGuard_DB_PORT")
    or "5432"
)
DB_NAME = (
    os.getenv("FINGUARD_DB_NAME")
    or os.getenv("FINGuard_DB_NAME")
    or "finguard"
)
DB_USER = (
    os.getenv("FINGUARD_DB_USER")
    or os.getenv("FINGuard_DB_USER")
    or "postgres"
)
DB_PASSWORD = (
    os.getenv("FINGUARD_DB_PASSWORD")
    or os.getenv("FINGuard_DB_PASSWORD")
    or "postgres"
)


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def initialize_database():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                transaction_id VARCHAR(100) UNIQUE NOT NULL,
                user_id VARCHAR(100),
                timestamp TIMESTAMP,
                amount DOUBLE PRECISION,
                merchant_id VARCHAR(100),
                merchant_category VARCHAR(100),
                location VARCHAR(100),
                device_id VARCHAR(100),
                ip_address VARCHAR(100),
                payment_method VARCHAR(50),
                account_age DOUBLE PRECISION,
                transaction_count_24h DOUBLE PRECISION,
                avg_transaction_amount DOUBLE PRECISION,
                distance_from_home DOUBLE PRECISION,
                is_new_device INTEGER,
                is_new_location INTEGER,
                fraud_probability DOUBLE PRECISION,
                risk_score DOUBLE PRECISION,
                is_fraud INTEGER,
                risk_level VARCHAR(20),
                reasons JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        cursor.execute(
            """
            ALTER TABLE transactions
            ADD COLUMN IF NOT EXISTS reasons JSONB;
            """
        )

        connection.commit()
    finally:
        connection.close()


# ==========================================================
# SAVE TRANSACTION
# ==========================================================

def save_transaction(transaction, prediction):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO transactions (
                transaction_id,
                user_id,
                timestamp,
                amount,
                merchant_id,
                merchant_category,
                location,
                device_id,
                ip_address,
                payment_method,
                account_age,
                transaction_count_24h,
                avg_transaction_amount,
                distance_from_home,
                is_new_device,
                is_new_location,

                fraud_probability,
                risk_score,
                is_fraud,
                risk_level,
                reasons
            )

            VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,

                %s, %s, %s, %s, %s
            )

            ON CONFLICT (transaction_id)

            DO UPDATE SET

                fraud_probability = EXCLUDED.fraud_probability,
                risk_score = EXCLUDED.risk_score,
                is_fraud = EXCLUDED.is_fraud,
                risk_level = EXCLUDED.risk_level,
                reasons = EXCLUDED.reasons;

        """, (

            transaction.transaction_id,
            transaction.user_id,
            transaction.timestamp,
            transaction.amount,
            transaction.merchant_id,
            transaction.merchant_category,
            transaction.location,
            transaction.device_id,
            transaction.ip_address,
            transaction.payment_method,
            transaction.account_age,
            transaction.transaction_count_24h,
            transaction.avg_transaction_amount,
            transaction.distance_from_home,
            transaction.is_new_device,
            transaction.is_new_location,

            prediction["fraud_probability"],
            prediction["risk_score"],
            prediction["is_fraud"],
            prediction["risk_level"],

            Json(prediction.get("reasons", []))
        ))

        connection.commit()

        cursor.close()

    finally:

        connection.close()


# ==========================================================
# RECENT TRANSACTIONS
# ==========================================================

def get_recent_transactions(limit=50):

    connection = get_connection()

    try:

        cursor = connection.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute("""
            SELECT
                transaction_id,
                user_id,
                timestamp,
                amount,
                merchant_category,
                location,
                payment_method,
                fraud_probability,
                risk_score,
                is_fraud,
                risk_level,
                created_at
            FROM transactions
            ORDER BY created_at DESC
            LIMIT %s;
        """, (limit,))

        results = cursor.fetchall()

        cursor.close()

        return results

    finally:

        connection.close()


# ==========================================================
# SINGLE TRANSACTION
# ==========================================================

def get_transaction(transaction_id):

    connection = get_connection()

    try:

        cursor = connection.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute("""
            SELECT *
            FROM transactions
            WHERE transaction_id = %s;
        """, (transaction_id,))

        result = cursor.fetchone()

        cursor.close()

        return result

    finally:

        connection.close()


# ==========================================================
# FRAUD ALERTS
# ===========================================================

def get_fraud_alerts(limit=50):

    connection = get_connection()

    try:

        cursor = connection.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute("""
            SELECT
                transaction_id,
                user_id,
                timestamp,
                amount,
                merchant_category,
                location,
                fraud_probability,
                risk_score,
                risk_level,
                created_at
            FROM transactions

            WHERE is_fraud = 1

            ORDER BY created_at DESC

            LIMIT %s;
        """, (limit,))

        results = cursor.fetchall()

        cursor.close()

        return results

    finally:

        connection.close()


# ==========================================================
# DASHBOARD STATISTICS
# ==========================================================

def get_dashboard_stats():

    connection = get_connection()

    try:

        cursor = connection.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute("""
            SELECT

                COUNT(*) AS total_transactions,

                COUNT(*)
                FILTER (
                    WHERE is_fraud = 1
                ) AS fraud_transactions,

                COUNT(*)
                FILTER (
                    WHERE risk_level = 'HIGH'
                ) AS high_risk_transactions,

                COUNT(*)
                FILTER (
                    WHERE risk_level = 'MEDIUM'
                ) AS medium_risk_transactions,

                COUNT(*)
                FILTER (
                    WHERE risk_level = 'LOW'
                ) AS low_risk_transactions,

                COALESCE(
                    AVG(amount),
                    0
                ) AS average_transaction_amount,

                COALESCE(
                    AVG(fraud_probability),
                    0
                ) AS average_fraud_probability

            FROM transactions;
        """)

        result = cursor.fetchone()

        cursor.close()

        return result

    finally:

        connection.close()