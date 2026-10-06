"""
NEXUS - LARGE FAKER DATABASE SEEDER

Creates a fresh Meridian Financial Group database.

Dataset:
    10,000 customers
    15,000 accounts
    120,000 transactions
    10,000 policies
    ~35,000 policy clauses
    5,001 claims
    6,000 portfolios
    50 investment products
    20,000 interaction logs
    5,001 escalation flags
    20,000 audit logs

IMPORTANT:
    Existing Nexus data is completely removed before seeding.

Run:
    python seed_database.py
"""

from __future__ import annotations

import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "meridian.db"

SEED = 20261005

CUSTOMER_COUNT = 10_000
ACCOUNT_COUNT = 15_000
TRANSACTION_COUNT = 120_000
POLICY_COUNT = 10_000
CLAIM_COUNT = 5_000
PORTFOLIO_COUNT = 6_000
INVESTMENT_PRODUCT_COUNT = 50
INTERACTION_COUNT = 20_000
ESCALATION_COUNT = 5_000
AUDIT_COUNT = 20_000

BATCH_SIZE = 1_000

random.seed(SEED)

fake = Faker("en_IN")
Faker.seed(SEED)


# ============================================================
# SHOWCASE / STRESS TEST IDS
# ============================================================

SHOWCASE_CUSTOMER = "CUS-20077"
SHOWCASE_ACCOUNT = "ACC-20077"
SHOWCASE_POLICY = "POL-IN-30091"
SHOWCASE_CLAIM = "CLM 30091"
SHOWCASE_PORTFOLIO = "PORT-20077"

STRESS_CUSTOMER = "CUS-10002"
STRESS_ACCOUNT = "ACC-10002"
STRESS_POLICY = "POL-IN-10002"

HARD_ESCALATION_CUSTOMER = "CUS-10004"


# ============================================================
# RESERVED IDS
# ============================================================

RESERVED_CUSTOMER_IDS = {
    SHOWCASE_CUSTOMER,
    STRESS_CUSTOMER,
    HARD_ESCALATION_CUSTOMER,
}

RESERVED_ACCOUNT_IDS = {
    SHOWCASE_ACCOUNT,
    STRESS_ACCOUNT,
}

RESERVED_POLICY_IDS = {
    SHOWCASE_POLICY,
    STRESS_POLICY,
}

RESERVED_PORTFOLIO_IDS = {
    SHOWCASE_PORTFOLIO,
}


# ============================================================
# ENUM / RANDOM DATA
# ============================================================

CUSTOMER_TIERS = [
    "standard",
    "premium",
    "private",
]

KYC_STATUSES = [
    "verified",
    "verified",
    "verified",
    "pending",
    "expired",
    "failed",
]

ACCOUNT_TYPES = [
    "savings",
    "savings",
    "current",
    "checking",
]

ACCOUNT_STATUSES = [
    "active",
    "active",
    "active",
    "active",
    "restricted",
    "frozen",
    "closed",
]

CURRENCIES = [
    "INR",
    "INR",
    "INR",
    "USD",
]

TRANSACTION_TYPES = [
    "credit",
    "debit",
    "transfer",
    "payment",
    "refund",
]

TRANSACTION_STATUSES = [
    "completed",
    "completed",
    "completed",
    "completed",
    "pending",
    "failed",
    "reversed",
]

POLICY_TYPES = [
    "health",
    "life",
    "motor",
    "home",
    "travel",
]

POLICY_STATUSES = [
    "active",
    "active",
    "active",
    "active",
    "expired",
    "cancelled",
    "suspended",
]

PREMIUM_FREQUENCIES = [
    "monthly",
    "quarterly",
    "half_yearly",
    "annual",
]

PAYMENT_METHODS = [
    "bank_transfer",
    "credit_card",
    "debit_card",
    "auto_debit",
    "upi",
]

CLAIM_TYPES = [
    "medical",
    "accident",
    "vehicle_damage",
    "property_damage",
    "travel_delay",
    "life_event",
]

CLAIM_STATUSES = [
    "submitted",
    "under_review",
    "approved",
    "rejected",
    "settled",
]

RISK_PROFILES = [
    "conservative",
    "moderate",
    "aggressive",
]

PORTFOLIO_STATUSES = [
    "active",
    "active",
    "active",
    "restricted",
    "closed",
]

PRODUCT_TYPES = [
    "mutual_fund",
    "fixed_deposit",
    "government_bond",
    "corporate_bond",
    "equity_fund",
    "index_fund",
    "etf",
]

PRODUCT_RISK_LEVELS = [
    "low",
    "medium",
    "high",
]

LIQUIDITY_OPTIONS = [
    "high",
    "medium",
    "low",
]

PRODUCT_STATUSES = [
    "active",
    "active",
    "active",
    "suspended",
    "closed",
]

PRODUCT_LINES = [
    "banking",
    "insurance",
    "wealth",
    "cross_product",
]

REQUEST_TYPES = [
    "balance_inquiry",
    "transaction_query",
    "coverage_question",
    "claim_query",
    "payment_terms",
    "portfolio_query",
    "investment_product_query",
    "suitability_query",
    "auto_debit_setup",
    "complaint",
    "other",
]

ESCALATION_CATEGORIES = [
    "none",
    "none",
    "none",
    "none",
    "financial_hardship",
    "safeguarding_concern",
    "compliance_override_request",
]

URGENCY_LEVELS = [
    "routine",
    "routine",
    "routine",
    "high",
    "critical",
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def random_date(
    start_days_ago: int = 365,
    end_days_ago: int = 0,
) -> str:
    start = datetime.now() - timedelta(days=start_days_ago)
    end = datetime.now() - timedelta(days=end_days_ago)

    if start > end:
        start, end = end, start

    delta = end - start

    return (
        start
        + timedelta(
            seconds=random.randint(
                0,
                max(1, int(delta.total_seconds())),
            )
        )
    ).isoformat(timespec="seconds")


def money(
    minimum: float = 100,
    maximum: float = 2_000_000,
) -> float:
    return round(
        random.uniform(
            minimum,
            maximum,
        ),
        2,
    )


def batch_insert(
    connection: sqlite3.Connection,
    sql: str,
    rows: list[tuple],
) -> None:
    if not rows:
        return

    connection.executemany(
        sql,
        rows,
    )
    connection.commit()


def print_progress(
    label: str,
    current: int,
    total: int,
) -> None:
    if current % BATCH_SIZE == 0 or current == total:
        percentage = (
            current / total * 100
            if total
            else 100
        )

        print(
            f"{label}: "
            f"{current:,}/{total:,} "
            f"({percentage:.1f}%)"
        )


# ============================================================
# DATABASE RESET
# ============================================================

def reset_database(
    connection: sqlite3.Connection,
) -> None:

    print("\nResetting existing database...")

    connection.execute(
        "PRAGMA foreign_keys = OFF"
    )

    tables = [
        "audit_log",
        "escalation_flags",
        "interaction_log",
        "claims",
        "policy_clauses",
        "policies",
        "transactions",
        "accounts",
        "portfolios",
        "investment_products",
        "customers",
    ]

    for table in tables:
        connection.execute(
            f"DELETE FROM {table}"
        )

    connection.execute(
        "DELETE FROM sqlite_sequence"
    )

    connection.commit()

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    print("Existing data removed.")


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection() -> sqlite3.Connection:

    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        DB_PATH
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    connection.execute(
        "PRAGMA journal_mode = WAL"
    )

    connection.execute(
        "PRAGMA synchronous = NORMAL"
    )

    return connection


# ============================================================
# CUSTOMERS
# ============================================================

def generate_customers(
    connection: sqlite3.Connection,
) -> list[str]:

    print("\nGenerating customers...")

    rows = []
    customer_ids = []

    # --------------------------------------------------------
    # SHOWCASE CUSTOMER
    # --------------------------------------------------------

    rows.append(
        (
            SHOWCASE_CUSTOMER,
            "Arjun Mehta",
            "arjun.mehta@example.com",
            "+919876543210",
            "premium",
            "verified",
            now_iso(),
            now_iso(),
        )
    )

    customer_ids.append(
        SHOWCASE_CUSTOMER
    )

    # --------------------------------------------------------
    # STRESS CUSTOMER
    # --------------------------------------------------------

    rows.append(
        (
            STRESS_CUSTOMER,
            "Stress Test Customer",
            "stress.customer@example.com",
            "+919800000002",
            "standard",
            "verified",
            now_iso(),
            now_iso(),
        )
    )

    customer_ids.append(
        STRESS_CUSTOMER
    )

    # --------------------------------------------------------
    # HARD ESCALATION CUSTOMER
    # --------------------------------------------------------

    rows.append(
        (
            HARD_ESCALATION_CUSTOMER,
            "Hard Escalation Customer",
            "hard.escalation@example.com",
            "+919800000004",
            "premium",
            "verified",
            now_iso(),
            now_iso(),
        )
    )

    customer_ids.append(
        HARD_ESCALATION_CUSTOMER
    )

    batch_insert(
        connection,
        """
        INSERT INTO customers (
            customer_id,
            full_name,
            email,
            phone,
            customer_tier,
            kyc_status,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )

    rows.clear()

    # --------------------------------------------------------
    # NORMAL CUSTOMERS
    # --------------------------------------------------------

    number = 1

    while len(customer_ids) < CUSTOMER_COUNT:

        customer_id = (
            f"CUS-{number:05d}"
        )

        number += 1

        if customer_id in RESERVED_CUSTOMER_IDS:
            continue

        full_name = fake.name()

        email = (
            f"user{number}"
            f"_{random.randint(1000, 9999)}"
            "@example.com"
        )

        phone = (
            "+91"
            + str(
                random.randint(
                    6000000000,
                    9999999999,
                )
            )
        )

        tier = random.choice(
            CUSTOMER_TIERS
        )

        kyc_status = random.choice(
            KYC_STATUSES
        )

        created_at = random_date(
            start_days_ago=1500,
            end_days_ago=100,
        )

        updated_at = random_date(
            start_days_ago=90,
            end_days_ago=0,
        )

        rows.append(
            (
                customer_id,
                full_name,
                email,
                phone,
                tier,
                kyc_status,
                created_at,
                updated_at,
            )
        )

        customer_ids.append(
            customer_id
        )

        if len(rows) >= BATCH_SIZE:

            batch_insert(
                connection,
                """
                INSERT INTO customers (
                    customer_id,
                    full_name,
                    email,
                    phone,
                    customer_tier,
                    kyc_status,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )

            rows.clear()

        print_progress(
            "Customers",
            len(customer_ids),
            CUSTOMER_COUNT,
        )

    if rows:

        batch_insert(
            connection,
            """
            INSERT INTO customers (
                customer_id,
                full_name,
                email,
                phone,
                customer_tier,
                kyc_status,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

    print(
        f"Customers created: "
        f"{len(customer_ids):,}"
    )

    return customer_ids


# ============================================================
# ACCOUNTS
# ============================================================

def generate_accounts(
    connection: sqlite3.Connection,
    customer_ids: list[str],
) -> list[str]:

    print("\nGenerating accounts...")

    rows = []
    account_ids = []

    # --------------------------------------------------------
    # SHOWCASE ACCOUNT
    # --------------------------------------------------------

    rows.append(
        (
            SHOWCASE_ACCOUNT,
            SHOWCASE_CUSTOMER,
            "savings",
            "INR",
            125000.00,
            "active",
            1,
            None,
            random_date(
                start_days_ago=900,
                end_days_ago=300,
            ),
        )
    )

    account_ids.append(
        SHOWCASE_ACCOUNT
    )

    # --------------------------------------------------------
    # STRESS ACCOUNT
    # --------------------------------------------------------

    rows.append(
        (
            STRESS_ACCOUNT,
            STRESS_CUSTOMER,
            "savings",
            "INR",
            50000.00,
            "active",
            0,
            None,
            random_date(
                start_days_ago=500,
                end_days_ago=100,
            ),
        )
    )

    account_ids.append(
        STRESS_ACCOUNT
    )

    batch_insert(
        connection,
        """
        INSERT INTO accounts (
            account_id,
            customer_id,
            account_type,
            currency,
            balance,
            account_status,
            auto_debit_enabled,
            auto_debit_restriction_reason,
            opened_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )

    rows.clear()

    # --------------------------------------------------------
    # NORMAL ACCOUNTS
    # --------------------------------------------------------

    number = 1

    while len(account_ids) < ACCOUNT_COUNT:

        account_id = (
            f"ACC-{number:05d}"
        )

        number += 1

        if account_id in RESERVED_ACCOUNT_IDS:
            continue

        customer_id = random.choice(
            customer_ids
        )

        account_type = random.choice(
            ACCOUNT_TYPES
        )

        currency = random.choice(
            CURRENCIES
        )

        balance = money(
            500,
            2_500_000,
        )

        account_status = random.choice(
            ACCOUNT_STATUSES
        )

        auto_debit_enabled = (
            1
            if (
                account_status == "active"
                and random.random() < 0.30
            )
            else 0
        )

        restriction_reason = None

        if account_status in {
            "restricted",
            "frozen",
        }:

            restriction_reason = random.choice(
                [
                    "KYC review pending",
                    "Suspicious activity review",
                    "Temporary compliance restriction",
                    "Customer verification required",
                ]
            )

            auto_debit_enabled = 0

        opened_at = random_date(
            start_days_ago=1500,
            end_days_ago=30,
        )

        rows.append(
            (
                account_id,
                customer_id,
                account_type,
                currency,
                balance,
                account_status,
                auto_debit_enabled,
                restriction_reason,
                opened_at,
            )
        )

        account_ids.append(
            account_id
        )

        if len(rows) >= BATCH_SIZE:

            batch_insert(
                connection,
                """
                INSERT INTO accounts (
                    account_id,
                    customer_id,
                    account_type,
                    currency,
                    balance,
                    account_status,
                    auto_debit_enabled,
                    auto_debit_restriction_reason,
                    opened_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )

            rows.clear()

        print_progress(
            "Accounts",
            len(account_ids),
            ACCOUNT_COUNT,
        )

    if rows:

        batch_insert(
            connection,
            """
            INSERT INTO accounts (
                account_id,
                customer_id,
                account_type,
                currency,
                balance,
                account_status,
                auto_debit_enabled,
                auto_debit_restriction_reason,
                opened_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

    print(
        f"Accounts created: "
        f"{len(account_ids):,}"
    )

    return account_ids


# ============================================================
# TRANSACTIONS
# ============================================================

def generate_transactions(
    connection: sqlite3.Connection,
    account_ids: list[str],
) -> None:

    print("\nGenerating transactions...")

    rows = []

    for number in range(
        1,
        TRANSACTION_COUNT + 1,
    ):

        transaction_id = (
            f"TXN-{number:08d}"
        )

        account_id = random.choice(
            account_ids
        )

        transaction_type = random.choice(
            TRANSACTION_TYPES
        )

        amount = money(
            100,
            250000,
        )

        currency = random.choice(
            CURRENCIES
        )

        descriptions = {
            "credit": [
                "Salary credit",
                "Cash deposit",
                "Refund received",
                "Interest credit",
            ],
            "debit": [
                "ATM withdrawal",
                "Utility payment",
                "Online purchase",
                "Bill payment",
            ],
            "transfer": [
                "Account transfer",
                "NEFT transfer",
                "IMPS transfer",
                "Internal transfer",
            ],
            "payment": [
                "Insurance premium",
                "Subscription payment",
                "Merchant payment",
                "Loan repayment",
            ],
            "refund": [
                "Merchant refund",
                "Payment reversal",
                "Purchase refund",
            ],
        }

        description = random.choice(
            descriptions[transaction_type]
        )

        transaction_status = random.choice(
            TRANSACTION_STATUSES
        )

        transaction_date = random_date(
            start_days_ago=730,
            end_days_ago=0,
        )

        rows.append(
            (
                transaction_id,
                account_id,
                transaction_type,
                amount,
                currency,
                description,
                transaction_status,
                transaction_date,
            )
        )

        if len(rows) >= BATCH_SIZE:

            batch_insert(
                connection,
                """
                INSERT INTO transactions (
                    transaction_id,
                    account_id,
                    transaction_type,
                    amount,
                    currency,
                    description,
                    transaction_status,
                    transaction_date
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )

            rows.clear()

        print_progress(
            "Transactions",
            number,
            TRANSACTION_COUNT,
        )

    if rows:

        batch_insert(
            connection,
            """
            INSERT INTO transactions (
                transaction_id,
                account_id,
                transaction_type,
                amount,
                currency,
                description,
                transaction_status,
                transaction_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

    print(
        f"Transactions created: "
        f"{TRANSACTION_COUNT:,}"
    )


# ============================================================
# POLICIES
# ============================================================
def generate_policies(
    connection: sqlite3.Connection,
    customer_ids: list[str],
) -> list[str]:

    print("\nGenerating policies...")

    rows = []
    policy_ids = []

    # --------------------------------------------------------
    # SHOWCASE POLICY
    # --------------------------------------------------------

    showcase_start = (
        datetime.now() - timedelta(days=500)
    ).date()

    showcase_end = (
        showcase_start + timedelta(days=365)
    )

    rows.append(
        (
            SHOWCASE_POLICY,
            SHOWCASE_CUSTOMER,
            "health",
            "active",
            4500.00,
            "monthly",
            "bank_transfer",
            (
                "Premium can be paid monthly. "
                "Eligible payment accounts may use "
                "automatic premium debit subject to "
                "account eligibility."
            ),
            showcase_start.isoformat(),
            showcase_end.isoformat(),
        )
    )

    policy_ids.append(
        SHOWCASE_POLICY
    )

    # --------------------------------------------------------
    # STRESS POLICY
    # --------------------------------------------------------

    stress_start = (
        datetime.now() - timedelta(days=300)
    ).date()

    stress_end = (
        stress_start + timedelta(days=365)
    )

    rows.append(
        (
            STRESS_POLICY,
            STRESS_CUSTOMER,
            "motor",
            "active",
            3200.00,
            "monthly",
            "auto_debit",
            (
                "Premium must be paid according "
                "to the agreed payment schedule."
            ),
            stress_start.isoformat(),
            stress_end.isoformat(),
        )
    )

    policy_ids.append(
        STRESS_POLICY
    )

    batch_insert(
        connection,
        """
        INSERT INTO policies (
            policy_id,
            customer_id,
            policy_type,
            policy_status,
            premium_amount,
            premium_frequency,
            payment_method,
            payment_terms,
            start_date,
            end_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )

    rows.clear()

    # --------------------------------------------------------
    # NORMAL POLICIES
    # --------------------------------------------------------

    number = 1

    while len(policy_ids) < POLICY_COUNT:

        policy_id = (
            f"POL-{number:02d}-{number:05d}"
        )

        number += 1

        if policy_id in RESERVED_POLICY_IDS:
            continue

        customer_id = random.choice(
            customer_ids
        )

        policy_type = random.choice(
            POLICY_TYPES
        )

        policy_status = random.choice(
            POLICY_STATUSES
        )

        premium_amount = money(
            1000,
            75000,
        )

        premium_frequency = random.choice(
            PREMIUM_FREQUENCIES
        )

        payment_method = random.choice(
            PAYMENT_METHODS
        )

        payment_terms = (
            "Premium payments must be "
            "made according to the policy "
            "schedule. Late payments may "
            "result in restrictions."
        )

        # ----------------------------------------------------
        # START DATE
        # ----------------------------------------------------

        start_date = (
            datetime.now()
            - timedelta(
                days=random.randint(
                    50,
                    1000,
                )
            )
        ).date()

        # ----------------------------------------------------
        # END DATE
        #
        # IMPORTANT:
        # policies.end_date is NOT NULL in the schema.
        # Therefore every policy must receive an end date.
        # ----------------------------------------------------

        duration_days = random.choice(
            [
                180,
                365,
                730,
                1095,
                1825,
            ]
        )

        end_date = (
            start_date
            + timedelta(
                days=duration_days
            )
        )

        rows.append(
            (
                policy_id,
                customer_id,
                policy_type,
                policy_status,
                premium_amount,
                premium_frequency,
                payment_method,
                payment_terms,
                start_date.isoformat(),
                end_date.isoformat(),
            )
        )

        policy_ids.append(
            policy_id
        )

        if len(rows) >= BATCH_SIZE:

            batch_insert(
                connection,
                """
                INSERT INTO policies (
                    policy_id,
                    customer_id,
                    policy_type,
                    policy_status,
                    premium_amount,
                    premium_frequency,
                    payment_method,
                    payment_terms,
                    start_date,
                    end_date
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )

            rows.clear()

        print_progress(
            "Policies",
            len(policy_ids),
            POLICY_COUNT,
        )

    if rows:

        batch_insert(
            connection,
            """
            INSERT INTO policies (
                policy_id,
                customer_id,
                policy_type,
                policy_status,
                premium_amount,
                premium_frequency,
                payment_method,
                payment_terms,
                start_date,
                end_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

    print(
        f"Policies created: "
        f"{len(policy_ids):,}"
    )

    return policy_ids

# ============================================================
# POLICY CLAUSES
# ============================================================

def generate_policy_clauses(
    connection: sqlite3.Connection,
    policy_ids: list[str],
) -> None:

    print("\nGenerating policy clauses...")

    scenario_templates = {

        "auto_debit": (
            "Automatic premium debit may be enabled "
            "from an eligible active bank account."
        ),

        "premium_payment": (
            "Premium payments must be completed "
            "according to the policy payment schedule."
        ),

        "late_payment": (
            "Late premium payments may result in "
            "policy restrictions or suspension."
        ),

        "claim_submission": (
            "Claims must be submitted with the "
            "required supporting documentation."
        ),

        "hospitalization": (
            "Eligible hospitalization expenses may be "
            "covered subject to policy conditions."
        ),

        "accidental_damage": (
            "Accidental damage may be covered subject "
            "to exclusions and policy limits."
        ),

        "renewal": (
            "Policy renewal is subject to applicable "
            "renewal terms and customer eligibility."
        ),
    }

    clause_types = [
        "coverage",
        "payment",
        "exclusion",
        "condition",
    ]

    rows = []

    # ========================================================
    # GENERATE NORMAL CLAUSES
    # ========================================================

    for policy_id in policy_ids:

        available_scenarios = list(
            scenario_templates.keys()
        )

        # Showcase policy receives its auto_debit
        # clause separately below.
        if policy_id == SHOWCASE_POLICY:
            available_scenarios.remove(
                "auto_debit"
            )

        scenario_count = random.randint(
            2,
            min(
                5,
                len(available_scenarios),
            ),
        )

        selected_scenarios = random.sample(
            available_scenarios,
            scenario_count,
        )

        for scenario_tag in selected_scenarios:

            clause_text = (
                scenario_templates[
                    scenario_tag
                ]
            )

            covered = 1

            if scenario_tag == "late_payment":
                covered = random.choice(
                    [0, 1]
                )

            rows.append(
                (
                    policy_id,
                    scenario_tag,
                    random.choice(
                        clause_types
                    ),
                    covered,
                    clause_text,
                )
            )

            # ------------------------------------------------
            # BATCH INSERT
            # ------------------------------------------------

            if len(rows) >= BATCH_SIZE:

                batch_insert(
                    connection,
                    """
                    INSERT INTO policy_clauses (
                        policy_id,
                        scenario_tag,
                        clause_type,
                        covered,
                        clause_text
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    rows,
                )

                rows.clear()

    # ========================================================
    # INSERT REMAINING NORMAL CLAUSES
    # ========================================================

    if rows:

        batch_insert(
            connection,
            """
            INSERT INTO policy_clauses (
                policy_id,
                scenario_tag,
                clause_type,
                covered,
                clause_text
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            rows,
        )

        rows.clear()

    # ========================================================
    # SHOWCASE AUTO-DEBIT CLAUSE
    # ========================================================

    connection.execute(
        """
        INSERT INTO policy_clauses (
            policy_id,
            scenario_tag,
            clause_type,
            covered,
            clause_text
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            SHOWCASE_POLICY,
            "auto_debit",
            "payment",
            1,
            (
                "Automatic premium debit is permitted "
                "from an eligible active savings account "
                "when the account supports automatic payments."
            ),
        ),
    )

    connection.commit()

    # ========================================================
    # FINAL COUNT
    # ========================================================

    count = connection.execute(
        """
        SELECT COUNT(*)
        FROM policy_clauses
        """
    ).fetchone()[0]

    print(
        f"Policy clauses created: "
        f"{count:,}"
    )


# ============================================================
# CLAIM GENERATION
# ============================================================

def generate_claims(
    connection: sqlite3.Connection,
    policy_ids: list[str],
) -> None:

    print("\nGenerating claims...")

    rows = []

    for number in range(
        1,
        CLAIM_COUNT + 1,
    ):

        claim_id = (
            f"CLM {number:05d}"
        )

        # Reserve showcase claim ID.
        if claim_id == SHOWCASE_CLAIM:
            continue

        policy_id = random.choice(
            policy_ids
        )

        claim_type = random.choice(
            CLAIM_TYPES
        )

        claim_status = random.choice(
            CLAIM_STATUSES
        )

        claim_amount = money(
            5000,
            1_500_000,
        )

        incident_date = random_date(
            start_days_ago=700,
            end_days_ago=30,
        )[:10]

        submitted_at = random_date(
            start_days_ago=650,
            end_days_ago=20,
        )

        last_updated_at = random_date(
            start_days_ago=30,
            end_days_ago=0,
        )

        rows.append(
            (
                claim_id,
                policy_id,
                claim_type,
                claim_status,
                claim_amount,
                incident_date,
                submitted_at,
                last_updated_at,
            )
        )

        if len(rows) >= BATCH_SIZE:

            batch_insert(
                connection,
                """
                INSERT INTO claims (
                    claim_id,
                    policy_id,
                    claim_type,
                    claim_status,
                    claim_amount,
                    incident_date,
                    submitted_at,
                    last_updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )

            rows.clear()

        print_progress(
            "Claims",
            number,
            CLAIM_COUNT,
        )

    if rows:

        batch_insert(
            connection,
            """
            INSERT INTO claims (
                claim_id,
                policy_id,
                claim_type,
                claim_status,
                claim_amount,
                incident_date,
                submitted_at,
                last_updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

    # --------------------------------------------------------
    # SHOWCASE CLAIM
    # --------------------------------------------------------

    connection.execute(
        """
        INSERT INTO claims (
            claim_id,
            policy_id,
            claim_type,
            claim_status,
            claim_amount,
            incident_date,
            submitted_at,
            last_updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            SHOWCASE_CLAIM,
            SHOWCASE_POLICY,
            "medical",
            "under_review",
            125000.00,
            datetime.now()
            .date()
            .isoformat(),
            now_iso(),
            now_iso(),
        ),
    )

    connection.commit()

    count = connection.execute(
        "SELECT COUNT(*) FROM claims"
    ).fetchone()[0]

    print(
        f"Claims created: "
        f"{count:,}"
    )


# ============================================================
# PORTFOLIOS
# ============================================================

def generate_portfolios(
    connection: sqlite3.Connection,
    customer_ids: list[str],
) -> list[str]:

    print("\nGenerating portfolios...")

    rows = []
    portfolio_ids = []

    # --------------------------------------------------------
    # SHOWCASE PORTFOLIO
    # --------------------------------------------------------

    rows.append(
        (
            SHOWCASE_PORTFOLIO,
            SHOWCASE_CUSTOMER,
            "Arjun Growth Portfolio",
            "moderate",
            850000.00,
            "INR",
            "active",
            random_date(
                start_days_ago=700,
                end_days_ago=200,
            ),
        )
    )

    portfolio_ids.append(
        SHOWCASE_PORTFOLIO
    )

    batch_insert(
        connection,
        """
        INSERT INTO portfolios (
            portfolio_id,
            customer_id,
            portfolio_name,
            risk_profile,
            total_value,
            currency,
            portfolio_status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )

    rows.clear()

    # --------------------------------------------------------
    # NORMAL PORTFOLIOS
    # --------------------------------------------------------

    number = 1

    while len(portfolio_ids) < PORTFOLIO_COUNT:

        portfolio_id = (
            f"PORT-{number:05d}"
        )

        number += 1

        if portfolio_id in RESERVED_PORTFOLIO_IDS:
            continue

        customer_id = random.choice(
            customer_ids
        )

        portfolio_name = (
            f"{fake.first_name()} "
            f"Investment Portfolio"
        )

        risk_profile = random.choice(
            RISK_PROFILES
        )

        total_value = money(
            10000,
            10_000_000,
        )

        currency = random.choice(
            CURRENCIES
        )

        portfolio_status = random.choice(
            PORTFOLIO_STATUSES
        )

        created_at = random_date(
            start_days_ago=1000,
            end_days_ago=20,
        )

        rows.append(
            (
                portfolio_id,
                customer_id,
                portfolio_name,
                risk_profile,
                total_value,
                currency,
                portfolio_status,
                created_at,
            )
        )

        portfolio_ids.append(
            portfolio_id
        )

        if len(rows) >= BATCH_SIZE:

            batch_insert(
                connection,
                """
                INSERT INTO portfolios (
                    portfolio_id,
                    customer_id,
                    portfolio_name,
                    risk_profile,
                    total_value,
                    currency,
                    portfolio_status,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )

            rows.clear()

        print_progress(
            "Portfolios",
            len(portfolio_ids),
            PORTFOLIO_COUNT,
        )

    if rows:

        batch_insert(
            connection,
            """
            INSERT INTO portfolios (
                portfolio_id,
                customer_id,
                portfolio_name,
                risk_profile,
                total_value,
                currency,
                portfolio_status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

    print(
        f"Portfolios created: "
        f"{len(portfolio_ids):,}"
    )

    return portfolio_ids


# ============================================================
# INVESTMENT PRODUCTS
# ============================================================

def generate_investment_products(
    connection: sqlite3.Connection,
) -> list[str]:

    print(
        "\nGenerating investment products..."
    )

    rows = []
    product_ids = []

    for number in range(
        1,
        INVESTMENT_PRODUCT_COUNT + 1,
    ):

        product_id = (
            f"PROD-{number:02d}-{number:02d}"
        )

        product_name = (
            f"Meridian "
            f"{random.choice(PRODUCT_TYPES).replace('_', ' ').title()} "
            f"{number}"
        )

        product_type = random.choice(
            PRODUCT_TYPES
        )

        risk_level = random.choice(
            PRODUCT_RISK_LEVELS
        )

        minimum_investment = money(
            500,
            500000,
        )

        expected_return_description = random.choice(
            [
                "Potential returns linked to market performance.",
                "Fixed indicative returns subject to applicable terms.",
                "Market-linked growth potential with moderate volatility.",
                "Long-term growth potential with higher market risk.",
                "Capital preservation focused with lower expected volatility.",
            ]
        )

        liquidity = random.choice(
            LIQUIDITY_OPTIONS
        )

        product_status = random.choice(
            PRODUCT_STATUSES
        )

        rows.append(
            (
                product_id,
                product_name,
                product_type,
                risk_level,
                minimum_investment,
                expected_return_description,
                liquidity,
                product_status,
            )
        )

        product_ids.append(
            product_id
        )

        if len(rows) >= BATCH_SIZE:

            batch_insert(
                connection,
                """
                INSERT INTO investment_products (
                    product_id,
                    product_name,
                    product_type,
                    risk_level,
                    minimum_investment,
                    expected_return_description,
                    liquidity,
                    product_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )

            rows.clear()

    if rows:

        batch_insert(
            connection,
            """
            INSERT INTO investment_products (
                product_id,
                product_name,
                product_type,
                risk_level,
                minimum_investment,
                expected_return_description,
                liquidity,
                product_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

    print(
        f"Investment products created: "
        f"{len(product_ids):,}"
    )

    return product_ids


# ============================================================
# INTERACTION LOGS
# ============================================================

def generate_interaction_logs(
    connection: sqlite3.Connection,
    customer_ids: list[str],
) -> None:

    print(
        "\nGenerating interaction logs..."
    )

    rows = []

    messages = [
        "What is my current account balance?",
        "Can you explain my insurance coverage?",
        "I want to check my recent transactions.",
        "What is the status of my claim?",
        "Can I enable automatic premium payments?",
        "Please explain my portfolio.",
        "Is this investment product suitable for me?",
        "I need help with my policy payment.",
        "I have a complaint about my account.",
        "Can you help me with my insurance policy?",
    ]

    response_summaries = [
        "Account information retrieved successfully.",
        "Insurance policy details retrieved.",
        "Transaction history retrieved.",
        "Claim status retrieved.",
        "Payment information provided.",
        "Portfolio information retrieved.",
        "Investment product information provided.",
        "Request routed for further review.",
    ]

    for number in range(
        1,
        INTERACTION_COUNT + 1,
    ):

        customer_id = random.choice(
            customer_ids
        )

        product_line = random.choice(
            PRODUCT_LINES
        )

        request_type = random.choice(
            REQUEST_TYPES
        )

        customer_message = random.choice(
            messages
        )

        response_summary = random.choice(
            response_summaries
        )

        escalation_category = random.choice(
            ESCALATION_CATEGORIES
        )

        escalated = (
            0
            if escalation_category == "none"
            else random.choice([0, 1])
        )

        request_id = (
            f"REQ-{number:08d}"
        )

        rows.append(
            (
                customer_id,
                request_id,
                product_line,
                request_type,
                customer_message,
                response_summary,
                escalation_category,
                escalated,
                now_iso(),
            )
        )

        if len(rows) >= BATCH_SIZE:

            batch_insert(
                connection,
                """
                INSERT INTO interaction_log (
                    customer_id,
                    request_id,
                    product_line,
                    request_type,
                    customer_message,
                    response_summary,
                    escalation_category,
                    escalated,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )

            rows.clear()

        print_progress(
            "Interaction logs",
            number,
            INTERACTION_COUNT,
        )

    if rows:

        batch_insert(
            connection,
            """
            INSERT INTO interaction_log (
                customer_id,
                request_id,
                product_line,
                request_type,
                customer_message,
                response_summary,
                escalation_category,
                escalated,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

    print(
        f"Interaction logs created: "
        f"{INTERACTION_COUNT:,}"
    )


# ============================================================
# ESCALATION FLAGS
# ============================================================

def generate_escalation_flags(
    connection: sqlite3.Connection,
    customer_ids: list[str],
) -> None:

    print(
        "\nGenerating escalation flags..."
    )

    rows = []

    escalation_reasons = {
        "financial_hardship": [
            "Customer reported financial hardship.",
            "Customer requested assistance due to financial difficulty.",
            "Customer indicated inability to meet payment obligations.",
        ],
        "safeguarding_concern": [
            "Potential safeguarding concern detected.",
            "Customer interaction requires safeguarding review.",
            "Customer may require specialist support.",
        ],
        "compliance_override_request": [
            "Customer requested a compliance override.",
            "Customer requested bypass of a mandatory control.",
            "Compliance exception request requires review.",
        ],
    }

    categories = [
        "financial_hardship",
        "safeguarding_concern",
        "compliance_override_request",
    ]

    for number in range(
        1,
        ESCALATION_COUNT + 1,
    ):

        customer_id = random.choice(
            customer_ids
        )

        request_id = (
            f"REQ-{random.randint(1, INTERACTION_COUNT):08d}"
        )

        request_category = random.choice(
            REQUEST_TYPES
        )

        escalation_reason_category = random.choice(
            categories
        )

        escalation_reason = random.choice(
            escalation_reasons[
                escalation_reason_category
            ]
        )

        hard_escalation = 1

        confidence_score = round(
            random.uniform(
                0.30,
                0.99,
            ),
            3,
        )

        status = random.choice(
            [
                "open",
                "open",
                "assigned",
                "resolved",
            ]
        )

        created_at = random_date(
            start_days_ago=180,
            end_days_ago=0,
        )

        resolved_at = None

        if status == "resolved":

            resolved_at = random_date(
                start_days_ago=90,
                end_days_ago=0,
            )

        rows.append(
            (
                customer_id,
                request_id,
                request_category,
                escalation_reason,
                hard_escalation,
                confidence_score,
                status,
                created_at,
                resolved_at,
            )
        )

        if len(rows) >= BATCH_SIZE:

            batch_insert(
                connection,
                """
                INSERT INTO escalation_flags (
                    customer_id,
                    request_id,
                    request_category,
                    escalation_reason,
                    hard_escalation,
                    confidence_score,
                    status,
                    created_at,
                    resolved_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )

            rows.clear()

        print_progress(
            "Escalation flags",
            number,
            ESCALATION_COUNT,
        )

    if rows:

        batch_insert(
            connection,
            """
            INSERT INTO escalation_flags (
                customer_id,
                request_id,
                request_category,
                escalation_reason,
                hard_escalation,
                confidence_score,
                status,
                created_at,
                resolved_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

    # --------------------------------------------------------
    # GUARANTEED HARD ESCALATION RECORD
    # --------------------------------------------------------

    connection.execute(
        """
        INSERT INTO escalation_flags (
            customer_id,
            request_id,
            request_category,
            escalation_reason,
            hard_escalation,
            confidence_score,
            status,
            created_at,
            resolved_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            HARD_ESCALATION_CUSTOMER,
            "REQ-HARD-0001",
            "complaint",
            (
                "Customer requested a mandatory "
                "compliance control override."
            ),
            1,
            0.99,
            "open",
            now_iso(),
            None,
        ),
    )

    connection.commit()

    count = connection.execute(
        "SELECT COUNT(*) FROM escalation_flags"
    ).fetchone()[0]

    print(
        f"Escalation flags created: "
        f"{count:,}"
    )


# ============================================================
# AUDIT LOGS
# ============================================================

def generate_audit_logs(
    connection: sqlite3.Connection,
    customer_ids: list[str],
) -> None:

    print(
        "\nGenerating audit logs..."
    )

    rows = []

    action_types = [
        "ACCOUNT_VIEW",
        "TRANSACTION_VIEW",
        "POLICY_VIEW",
        "CLAIM_VIEW",
        "PORTFOLIO_VIEW",
        "PRODUCT_VIEW",
        "CUSTOMER_NOTIFICATION",
        "ESCALATION_CREATED",
        "AUDIT_WRITE",
    ]

    performers = [
        "nexus_orchestrator",
        "classifier_agent",
        "retriever_agent",
        "drafting_agent",
        "validation_agent",
        "escalation_agent",
        "banking_server",
        "insurance_server",
        "wealth_server",
        "concierge_ops_server",
    ]

    outcomes = [
        "success",
        "success",
        "success",
        "blocked",
        "escalated",
    ]

    for number in range(
        1,
        AUDIT_COUNT + 1,
    ):

        customer_id = random.choice(
            customer_ids
        )

        action_type = random.choice(
            action_types
        )

        performed_by = random.choice(
            performers
        )

        outcome = random.choice(
            outcomes
        )

        details = (
            f"Action {action_type} performed "
            f"for customer {customer_id}."
        )

        rows.append(
            (
                now_iso(),
                action_type,
                performed_by,
                customer_id,
                outcome,
                details,
            )
        )

        if len(rows) >= BATCH_SIZE:

            batch_insert(
                connection,
                """
                INSERT INTO audit_log (
                    timestamp,
                    action_type,
                    performed_by,
                    customer_id,
                    outcome,
                    details
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                rows,
            )

            rows.clear()

        print_progress(
            "Audit logs",
            number,
            AUDIT_COUNT,
        )

    if rows:

        batch_insert(
            connection,
            """
            INSERT INTO audit_log (
                timestamp,
                action_type,
                performed_by,
                customer_id,
                outcome,
                details
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

    print(
        f"Audit logs created: "
        f"{AUDIT_COUNT:,}"
    )


# ============================================================
# SHOWCASE VALIDATION
# ============================================================

def validate_showcase_records(
    connection: sqlite3.Connection,
) -> None:

    print(
        "\nValidating showcase records..."
    )

    # --------------------------------------------------------
    # CUSTOMER
    # --------------------------------------------------------

    customer = connection.execute(
        """
        SELECT *
        FROM customers
        WHERE customer_id = ?
        """,
        (SHOWCASE_CUSTOMER,),
    ).fetchone()

    assert customer is not None
    assert customer["full_name"] == "Arjun Mehta"

    # --------------------------------------------------------
    # ACCOUNT
    # --------------------------------------------------------

    account = connection.execute(
        """
        SELECT *
        FROM accounts
        WHERE account_id = ?
        """,
        (SHOWCASE_ACCOUNT,),
    ).fetchone()

    assert account is not None
    assert account["customer_id"] == SHOWCASE_CUSTOMER
    assert account["account_type"] == "savings"
    assert account["auto_debit_enabled"] == 1

    # --------------------------------------------------------
    # POLICY
    # --------------------------------------------------------

    policy = connection.execute(
        """
        SELECT *
        FROM policies
        WHERE policy_id = ?
        """,
        (SHOWCASE_POLICY,),
    ).fetchone()

    assert policy is not None
    assert policy["customer_id"] == SHOWCASE_CUSTOMER

    # --------------------------------------------------------
    # AUTO-DEBIT CLAUSE
    # --------------------------------------------------------

    clause = connection.execute(
        """
        SELECT *
        FROM policy_clauses
        WHERE policy_id = ?
          AND scenario_tag = ?
        """,
        (
            SHOWCASE_POLICY,
            "auto_debit",
        ),
    ).fetchone()

    assert clause is not None
    assert clause["covered"] == 1

    # --------------------------------------------------------
    # CLAIM
    # --------------------------------------------------------

    claim = connection.execute(
        """
        SELECT *
        FROM claims
        WHERE claim_id = ?
        """,
        (SHOWCASE_CLAIM,),
    ).fetchone()

    assert claim is not None
    assert claim["policy_id"] == SHOWCASE_POLICY

    # --------------------------------------------------------
    # PORTFOLIO
    # --------------------------------------------------------

    portfolio = connection.execute(
        """
        SELECT *
        FROM portfolios
        WHERE portfolio_id = ?
        """,
        (SHOWCASE_PORTFOLIO,),
    ).fetchone()

    assert portfolio is not None
    assert portfolio["customer_id"] == SHOWCASE_CUSTOMER

    # --------------------------------------------------------
    # STRESS RECORDS
    # --------------------------------------------------------

    stress_customer = connection.execute(
        """
        SELECT *
        FROM customers
        WHERE customer_id = ?
        """,
        (STRESS_CUSTOMER,),
    ).fetchone()

    assert stress_customer is not None

    stress_account = connection.execute(
        """
        SELECT *
        FROM accounts
        WHERE account_id = ?
        """,
        (STRESS_ACCOUNT,),
    ).fetchone()

    assert stress_account is not None

    stress_policy = connection.execute(
        """
        SELECT *
        FROM policies
        WHERE policy_id = ?
        """,
        (STRESS_POLICY,),
    ).fetchone()

    assert stress_policy is not None

    hard_customer = connection.execute(
        """
        SELECT *
        FROM customers
        WHERE customer_id = ?
        """,
        (HARD_ESCALATION_CUSTOMER,),
    ).fetchone()

    assert hard_customer is not None

    hard_escalation = connection.execute(
        """
        SELECT *
        FROM escalation_flags
        WHERE customer_id = ?
          AND hard_escalation = 1
        """,
        (HARD_ESCALATION_CUSTOMER,),
    ).fetchone()

    assert hard_escalation is not None

    print(
        "Showcase validation: PASSED"
    )


# ============================================================
# DATABASE SUMMARY
# ============================================================

def print_database_summary(
    connection: sqlite3.Connection,
) -> None:

    print("\n" + "=" * 70)
    print("NEXUS DATABASE SUMMARY")
    print("=" * 70)

    tables = [
        "customers",
        "accounts",
        "transactions",
        "policies",
        "policy_clauses",
        "claims",
        "portfolios",
        "investment_products",
        "interaction_log",
        "escalation_flags",
        "audit_log",
    ]

    for table in tables:

        count = connection.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

        print(
            f"{table:<25} {count:>12,}"
        )

    print("=" * 70)

    print(
        "\nShowcase records:"
    )

    print(
        f"Customer : {SHOWCASE_CUSTOMER}"
    )

    print(
        f"Account  : {SHOWCASE_ACCOUNT}"
    )

    print(
        f"Policy   : {SHOWCASE_POLICY}"
    )

    print(
        f"Claim    : {SHOWCASE_CLAIM}"
    )

    print(
        f"Portfolio: {SHOWCASE_PORTFOLIO}"
    )

    print(
        f"\nDatabase: {DB_PATH}"
    )


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    print("=" * 70)
    print("NEXUS - MERIDIAN FINANCIAL GROUP")
    print("LARGE DATABASE SEEDER")
    print("=" * 70)

    print(
        f"\nDatabase path:\n{DB_PATH}"
    )

    print(
        "\nTarget dataset:"
    )

    print(
        f"  Customers          : {CUSTOMER_COUNT:,}"
    )

    print(
        f"  Accounts           : {ACCOUNT_COUNT:,}"
    )

    print(
        f"  Transactions       : {TRANSACTION_COUNT:,}"
    )

    print(
        f"  Policies           : {POLICY_COUNT:,}"
    )

    print(
        f"  Claims             : {CLAIM_COUNT + 1:,}"
    )

    print(
        f"  Portfolios         : {PORTFOLIO_COUNT:,}"
    )

    print(
        f"  Investment Products: {INVESTMENT_PRODUCT_COUNT:,}"
    )

    print(
        f"  Interaction Logs   : {INTERACTION_COUNT:,}"
    )

    print(
        f"  Escalation Flags   : {ESCALATION_COUNT + 1:,}"
    )

    print(
        f"  Audit Logs         : {AUDIT_COUNT:,}"
    )

    connection = get_connection()

    try:

        # ----------------------------------------------------
        # RESET
        # ----------------------------------------------------

        reset_database(
            connection
        )

        # ----------------------------------------------------
        # CUSTOMERS
        # ----------------------------------------------------

        customer_ids = generate_customers(
            connection
        )

        # ----------------------------------------------------
        # ACCOUNTS
        # ----------------------------------------------------

        account_ids = generate_accounts(
            connection,
            customer_ids,
        )

        # ----------------------------------------------------
        # TRANSACTIONS
        # ----------------------------------------------------

        generate_transactions(
            connection,
            account_ids,
        )

        # ----------------------------------------------------
        # POLICIES
        # ----------------------------------------------------

        policy_ids = generate_policies(
            connection,
            customer_ids,
        )

        # ----------------------------------------------------
        # POLICY CLAUSES
        # ----------------------------------------------------

        generate_policy_clauses(
            connection,
            policy_ids,
        )

        # ----------------------------------------------------
        # CLAIMS
        # ----------------------------------------------------

        generate_claims(
            connection,
            policy_ids,
        )

        # ----------------------------------------------------
        # PORTFOLIOS
        # ----------------------------------------------------

        generate_portfolios(
            connection,
            customer_ids,
        )

        # ----------------------------------------------------
        # INVESTMENT PRODUCTS
        # ----------------------------------------------------

        generate_investment_products(
            connection,
        )

        # ----------------------------------------------------
        # INTERACTION LOGS
        # ----------------------------------------------------

        generate_interaction_logs(
            connection,
            customer_ids,
        )

        # ----------------------------------------------------
        # ESCALATION FLAGS
        # ----------------------------------------------------

        generate_escalation_flags(
            connection,
            customer_ids,
        )

        # ----------------------------------------------------
        # AUDIT LOGS
        # ----------------------------------------------------

        generate_audit_logs(
            connection,
            customer_ids,
        )

        # ----------------------------------------------------
        # VALIDATE
        # ----------------------------------------------------

        validate_showcase_records(
            connection
        )

        # ----------------------------------------------------
        # FINAL SUMMARY
        # ----------------------------------------------------

        print_database_summary(
            connection
        )

    finally:

        connection.close()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()