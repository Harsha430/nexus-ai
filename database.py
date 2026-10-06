"""
Nexus - Meridian Financial Group
SQLite database schema creation only.

Creates:
    data/meridian.db

Usage:
    python database.py
"""

from pathlib import Path
import sqlite3


# ============================================================
# Configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "meridian.db"


# ============================================================
# Database Connection
# ============================================================

def get_connection() -> sqlite3.Connection:
    """
    Create and configure a SQLite connection.
    """

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=30,
    )

    connection.row_factory = sqlite3.Row

    # Enforce foreign-key constraints.
    connection.execute("PRAGMA foreign_keys = ON;")

    # WAL mode as required by the Nexus architecture.
    connection.execute("PRAGMA journal_mode = WAL;")

    # Good balance between durability and performance.
    connection.execute("PRAGMA synchronous = NORMAL;")

    return connection


# ============================================================
# Schema
# ============================================================

SCHEMA_SQL = """

-- ============================================================
-- CONCIERGE OPERATIONS
-- Owned by concierge_ops_server
-- ============================================================

CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,

    full_name TEXT NOT NULL,

    email TEXT,

    phone TEXT,

    customer_tier TEXT NOT NULL
        CHECK (
            customer_tier IN (
                'standard',
                'premium',
                'private'
            )
        ),

    kyc_status TEXT NOT NULL
        CHECK (
            kyc_status IN (
                'verified',
                'pending',
                'expired',
                'failed'
            )
        ),

    created_at TEXT NOT NULL,

    updated_at TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS interaction_log (
    interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,

    customer_id TEXT NOT NULL,

    request_id TEXT NOT NULL,

    product_line TEXT NOT NULL,

    request_type TEXT NOT NULL,

    customer_message TEXT,

    response_summary TEXT,

    escalation_category TEXT,

    escalated INTEGER NOT NULL DEFAULT 0
        CHECK (escalated IN (0, 1)),

    created_at TEXT NOT NULL,

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);


CREATE TABLE IF NOT EXISTS escalation_flags (
    escalation_id INTEGER PRIMARY KEY AUTOINCREMENT,

    customer_id TEXT NOT NULL,

    request_id TEXT NOT NULL,

    request_category TEXT NOT NULL,

    escalation_reason TEXT NOT NULL,

    hard_escalation INTEGER NOT NULL DEFAULT 0
        CHECK (hard_escalation IN (0, 1)),

    confidence_score REAL,

    status TEXT NOT NULL
        CHECK (
            status IN (
                'open',
                'assigned',
                'resolved'
            )
        ),

    created_at TEXT NOT NULL,

    resolved_at TEXT,

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);


CREATE TABLE IF NOT EXISTS audit_log (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,

    timestamp TEXT NOT NULL,

    action_type TEXT NOT NULL,

    performed_by TEXT NOT NULL,

    customer_id TEXT,

    outcome TEXT NOT NULL,

    details TEXT
);


-- ============================================================
-- BANKING
-- Owned by banking_server
-- ============================================================

CREATE TABLE IF NOT EXISTS accounts (
    account_id TEXT PRIMARY KEY,

    customer_id TEXT NOT NULL,

    account_type TEXT NOT NULL
        CHECK (
            account_type IN (
                'savings',
                'current',
                'checking'
            )
        ),

    currency TEXT NOT NULL DEFAULT 'INR',

    balance NUMERIC NOT NULL DEFAULT 0
        CHECK (balance >= 0),

    account_status TEXT NOT NULL
        CHECK (
            account_status IN (
                'active',
                'restricted',
                'closed',
                'frozen'
            )
        ),

    auto_debit_enabled INTEGER NOT NULL DEFAULT 0
        CHECK (auto_debit_enabled IN (0, 1)),

    auto_debit_restriction_reason TEXT,

    opened_at TEXT NOT NULL,

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);


CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,

    account_id TEXT NOT NULL,

    transaction_type TEXT NOT NULL
        CHECK (
            transaction_type IN (
                'credit',
                'debit',
                'transfer',
                'payment',
                'refund'
            )
        ),

    amount NUMERIC NOT NULL
        CHECK (amount >= 0),

    currency TEXT NOT NULL DEFAULT 'INR',

    description TEXT,

    transaction_status TEXT NOT NULL
        CHECK (
            transaction_status IN (
                'completed',
                'pending',
                'failed',
                'reversed'
            )
        ),

    transaction_date TEXT NOT NULL,

    FOREIGN KEY (account_id)
        REFERENCES accounts(account_id)
);


-- ============================================================
-- INSURANCE
-- Owned by insurance_server
-- ============================================================

CREATE TABLE IF NOT EXISTS policies (
    policy_id TEXT PRIMARY KEY,

    customer_id TEXT NOT NULL,

    policy_type TEXT NOT NULL,

    policy_status TEXT NOT NULL
        CHECK (
            policy_status IN (
                'active',
                'expired',
                'cancelled',
                'suspended'
            )
        ),

    premium_amount NUMERIC NOT NULL
        CHECK (premium_amount >= 0),

    premium_frequency TEXT NOT NULL
        CHECK (
            premium_frequency IN (
                'monthly',
                'quarterly',
                'half_yearly',
                'annual'
            )
        ),

    payment_method TEXT,

    payment_terms TEXT,

    start_date TEXT NOT NULL,

    end_date TEXT NOT NULL,

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);


CREATE TABLE IF NOT EXISTS policy_clauses (
    clause_id INTEGER PRIMARY KEY AUTOINCREMENT,

    policy_id TEXT NOT NULL,

    scenario_tag TEXT NOT NULL,

    clause_type TEXT NOT NULL,

    covered INTEGER NOT NULL
        CHECK (covered IN (0, 1)),

    clause_text TEXT NOT NULL,

    FOREIGN KEY (policy_id)
        REFERENCES policies(policy_id),

    UNIQUE (
        policy_id,
        scenario_tag
    )
);


CREATE TABLE IF NOT EXISTS claims (
    claim_id TEXT PRIMARY KEY,

    policy_id TEXT NOT NULL,

    claim_type TEXT NOT NULL,

    claim_status TEXT NOT NULL
        CHECK (
            claim_status IN (
                'submitted',
                'under_review',
                'approved',
                'rejected',
                'settled'
            )
        ),

    claim_amount NUMERIC
        CHECK (
            claim_amount IS NULL
            OR claim_amount >= 0
        ),

    incident_date TEXT,

    submitted_at TEXT NOT NULL,

    last_updated_at TEXT NOT NULL,

    FOREIGN KEY (policy_id)
        REFERENCES policies(policy_id)
);


-- ============================================================
-- WEALTH
-- Owned by wealth_server
-- ============================================================

CREATE TABLE IF NOT EXISTS portfolios (
    portfolio_id TEXT PRIMARY KEY,

    customer_id TEXT NOT NULL,

    portfolio_name TEXT NOT NULL,

    risk_profile TEXT NOT NULL
        CHECK (
            risk_profile IN (
                'conservative',
                'moderate',
                'aggressive'
            )
        ),

    total_value NUMERIC NOT NULL DEFAULT 0
        CHECK (total_value >= 0),

    currency TEXT NOT NULL DEFAULT 'INR',

    portfolio_status TEXT NOT NULL
        CHECK (
            portfolio_status IN (
                'active',
                'restricted',
                'closed'
            )
        ),

    created_at TEXT NOT NULL,

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);


CREATE TABLE IF NOT EXISTS investment_products (
    product_id TEXT PRIMARY KEY,

    product_name TEXT NOT NULL,

    product_type TEXT NOT NULL,

    risk_level TEXT NOT NULL
        CHECK (
            risk_level IN (
                'low',
                'medium',
                'high'
            )
        ),

    minimum_investment NUMERIC NOT NULL
        CHECK (minimum_investment >= 0),

    expected_return_description TEXT,

    liquidity TEXT,

    product_status TEXT NOT NULL
        CHECK (
            product_status IN (
                'active',
                'suspended',
                'closed'
            )
        )
);


-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_accounts_customer
ON accounts(customer_id);


CREATE INDEX IF NOT EXISTS idx_transactions_account
ON transactions(account_id);


CREATE INDEX IF NOT EXISTS idx_transactions_date
ON transactions(transaction_date);


CREATE INDEX IF NOT EXISTS idx_policies_customer
ON policies(customer_id);


CREATE INDEX IF NOT EXISTS idx_policy_clauses_policy
ON policy_clauses(policy_id);


CREATE INDEX IF NOT EXISTS idx_claims_policy
ON claims(policy_id);


CREATE INDEX IF NOT EXISTS idx_portfolios_customer
ON portfolios(customer_id);


CREATE INDEX IF NOT EXISTS idx_interaction_customer
ON interaction_log(customer_id);


CREATE INDEX IF NOT EXISTS idx_interaction_request
ON interaction_log(request_id);


CREATE INDEX IF NOT EXISTS idx_escalation_customer
ON escalation_flags(customer_id);


CREATE INDEX IF NOT EXISTS idx_escalation_request
ON escalation_flags(request_id);


CREATE INDEX IF NOT EXISTS idx_audit_customer
ON audit_log(customer_id);


CREATE INDEX IF NOT EXISTS idx_audit_timestamp
ON audit_log(timestamp);

"""


# ============================================================
# Create Database
# ============================================================

def create_database() -> None:
    """
    Create the Nexus SQLite database and all tables.
    """

    connection = get_connection()

    try:
        connection.executescript(SCHEMA_SQL)
        connection.commit()

        print("Nexus database created successfully.")
        print(f"Database: {DATABASE_PATH}")

    finally:
        connection.close()


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    create_database()