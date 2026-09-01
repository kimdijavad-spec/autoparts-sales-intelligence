from pathlib import Path

import pandas as pd


# ============================================================
# FILE PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_FOLDER = PROJECT_ROOT / "data" / "raw"

CUSTOMERS_FILE = RAW_DATA_FOLDER / "customers.csv"
SALES_REPRESENTATIVES_FILE = (
    RAW_DATA_FOLDER / "sales_representatives.csv"
)


# ============================================================
# EXPECTED STRUCTURE
# ============================================================

EXPECTED_CUSTOMER_COLUMNS = [
    "customer_id",
    "customer_name",
    "customer_type",
    "province",
    "city",
    "registration_date",
    "credit_limit",
    "sales_rep_id",
    "status",
]

EXPECTED_SALES_REP_COLUMNS = [
    "sales_rep_id",
    "sales_rep_name",
    "region",
    "hire_date",
    "monthly_target",
    "status",
]


# ============================================================
# VALIDATION HELPER
# ============================================================

def require(condition: bool, error_message: str) -> None:
    """Raise a readable error when a validation rule fails."""

    if not condition:
        raise ValueError(error_message)


# ============================================================
# MAIN VALIDATION
# ============================================================

def main() -> None:
    """Load and validate the generated base datasets."""

    require(
        CUSTOMERS_FILE.exists(),
        f"Customers file not found: {CUSTOMERS_FILE}",
    )

    require(
        SALES_REPRESENTATIVES_FILE.exists(),
        (
            "Sales representatives file not found: "
            f"{SALES_REPRESENTATIVES_FILE}"
        ),
    )

    customers = pd.read_csv(
        CUSTOMERS_FILE,
        parse_dates=["registration_date"],
    )

    sales_representatives = pd.read_csv(
        SALES_REPRESENTATIVES_FILE,
        parse_dates=["hire_date"],
    )

    # Validate columns.
    require(
        customers.columns.tolist() == EXPECTED_CUSTOMER_COLUMNS,
        "Customers file has unexpected columns.",
    )

    require(
        sales_representatives.columns.tolist()
        == EXPECTED_SALES_REP_COLUMNS,
        "Sales representatives file has unexpected columns.",
    )

    # Validate row counts.
    require(
        len(customers) == 500,
        f"Expected 500 customers, found {len(customers)}.",
    )

    require(
        len(sales_representatives) == 12,
        (
            "Expected 12 sales representatives, found "
            f"{len(sales_representatives)}."
        ),
    )

    # Validate unique identifiers.
    require(
        customers["customer_id"].is_unique,
        "Duplicate customer IDs were found.",
    )

    require(
        customers["customer_name"].is_unique,
        "Duplicate customer names were found.",
    )

    require(
        sales_representatives["sales_rep_id"].is_unique,
        "Duplicate sales representative IDs were found.",
    )

    # Validate missing values.
    require(
        not customers.isna().any().any(),
        "Missing values were found in customers data.",
    )

    require(
        not sales_representatives.isna().any().any(),
        "Missing values were found in sales representatives data.",
    )

    # Validate numeric values.
    require(
        (customers["credit_limit"] > 0).all(),
        "Customer credit limits must be greater than zero.",
    )

    require(
        (sales_representatives["monthly_target"] > 0).all(),
        "Monthly sales targets must be greater than zero.",
    )

    # Validate the relationship between customers and sales reps.
    customer_assignments = customers.merge(
        sales_representatives[
            ["sales_rep_id", "region"]
        ],
        on="sales_rep_id",
        how="left",
        validate="many_to_one",
    )

    require(
        customer_assignments["region"].notna().all(),
        "Some customers reference an unknown sales representative.",
    )

    require(
        (
            customer_assignments["province"]
            == customer_assignments["region"]
        ).all(),
        "Some customers are assigned to a different sales region.",
    )

    print("All base data validation checks passed.")
    print(f"Customers checked: {len(customers)}")
    print(
        "Sales representatives checked: "
        f"{len(sales_representatives)}"
    )

    print("\nCustomer types:")
    print(customers["customer_type"].value_counts().to_string())

    print("\nCustomer statuses:")
    print(customers["status"].value_counts().to_string())


if __name__ == "__main__":
    main()