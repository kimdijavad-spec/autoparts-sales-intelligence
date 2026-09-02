from __future__ import annotations

import csv
import os
import sys
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import pyodbc


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_FOLDER = PROJECT_ROOT / "data" / "raw"

SQL_DRIVER = os.getenv(
    "AUTOPARTS_SQL_DRIVER",
    "ODBC Driver 18 for SQL Server",
)
SQL_SERVER = os.getenv("AUTOPARTS_SQL_SERVER", "localhost")
SQL_DATABASE = os.getenv(
    "AUTOPARTS_SQL_DATABASE",
    "autoparts_sales_intelligence",
)

CONNECTION_STRING = (
    f"DRIVER={{{SQL_DRIVER}}};"
    f"SERVER={SQL_SERVER};"
    f"DATABASE={SQL_DATABASE};"
    "Trusted_Connection=yes;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)


TABLE_CONFIGS = [
    {
        "file_name": "sales_representatives.csv",
        "table_name": "sales.sales_representatives",
        "columns": (
            "sales_rep_id",
            "sales_rep_name",
            "region",
            "hire_date",
            "monthly_target",
            "status",
        ),
        "nullable": set(),
    },
    {
        "file_name": "customers.csv",
        "table_name": "sales.customers",
        "columns": (
            "customer_id",
            "customer_name",
            "customer_type",
            "province",
            "city",
            "registration_date",
            "credit_limit",
            "sales_rep_id",
            "status",
        ),
        "nullable": set(),
    },
    {
        "file_name": "products.csv",
        "table_name": "inventory.products",
        "columns": (
            "product_id",
            "sku",
            "product_name",
            "category",
            "brand",
            "compatible_vehicle",
            "unit_cost",
            "list_price",
            "reorder_point",
            "status",
        ),
        "nullable": set(),
    },
    {
        "file_name": "campaigns.csv",
        "table_name": "marketing.campaigns",
        "columns": (
            "campaign_id",
            "campaign_name",
            "channel",
            "start_date",
            "end_date",
            "budget",
            "target_customer_type",
            "target_product_category",
            "offered_discount",
        ),
        "nullable": set(),
    },
    {
        "file_name": "campaign_targets.csv",
        "table_name": "marketing.campaign_targets",
        "columns": (
            "campaign_id",
            "customer_id",
            "contact_date",
            "message_delivered",
            "customer_engaged",
            "sales_followup",
            "converted",
        ),
        "nullable": set(),
    },
    {
        "file_name": "sales_orders.csv",
        "table_name": "sales.sales_orders",
        "columns": (
            "order_id",
            "order_date",
            "customer_id",
            "sales_rep_id",
            "campaign_id",
            "payment_method",
        ),
        "nullable": {"campaign_id"},
    },
    {
        "file_name": "sales_order_lines.csv",
        "table_name": "sales.sales_order_lines",
        "columns": (
            "order_line_id",
            "order_id",
            "product_id",
            "quantity",
            "unit_price",
            "discount_percent",
            "returned_quantity",
        ),
        "nullable": set(),
    },
    {
        "file_name": "payments.csv",
        "table_name": "finance.payments",
        "columns": (
            "payment_id",
            "order_id",
            "customer_id",
            "invoice_amount",
            "invoice_date",
            "due_date",
            "paid_date",
            "payment_status",
        ),
        "nullable": {"paid_date"},
    },
]

DELETE_ORDER = [
    "finance.payments",
    "sales.sales_order_lines",
    "sales.sales_orders",
    "marketing.campaign_targets",
    "marketing.campaigns",
    "inventory.products",
    "sales.customers",
    "sales.sales_representatives",
]

DATE_COLUMNS = {
    "hire_date",
    "registration_date",
    "start_date",
    "end_date",
    "contact_date",
    "order_date",
    "invoice_date",
    "due_date",
    "paid_date",
}

INTEGER_COLUMNS = {
    "reorder_point",
    "quantity",
    "returned_quantity",
}

DECIMAL_COLUMNS = {
    "monthly_target",
    "credit_limit",
    "unit_cost",
    "list_price",
    "budget",
    "offered_discount",
    "unit_price",
    "discount_percent",
    "invoice_amount",
}

BOOLEAN_COLUMNS = {
    "message_delivered",
    "customer_engaged",
    "sales_followup",
    "converted",
}


# ============================================================
# CSV PREPARATION
# ============================================================

def convert_value(
    value: str,
    column: str,
    nullable_columns: set[str],
) -> Any:
    """Convert one CSV value to a SQL Server-compatible Python value."""

    cleaned_value = value.strip()

    if cleaned_value == "":
        if column in nullable_columns:
            return None

        raise ValueError(f"Column '{column}' contains an empty value.")

    if column in DATE_COLUMNS:
        return date.fromisoformat(cleaned_value)

    if column in INTEGER_COLUMNS:
        return int(cleaned_value)

    if column in DECIMAL_COLUMNS:
        try:
            return Decimal(cleaned_value)
        except InvalidOperation as error:
            raise ValueError(
                f"Column '{column}' contains an invalid number: "
                f"{cleaned_value!r}"
            ) from error

    if column in BOOLEAN_COLUMNS:
        normalized_value = cleaned_value.lower()

        if normalized_value == "true":
            return True

        if normalized_value == "false":
            return False

        raise ValueError(
            f"Column '{column}' contains an invalid Boolean value: "
            f"{cleaned_value!r}"
        )

    return cleaned_value


def read_csv_rows(config: dict[str, Any]) -> list[tuple[Any, ...]]:
    """Read and convert all rows from one configured CSV file."""

    csv_path = RAW_DATA_FOLDER / config["file_name"]
    expected_columns = list(config["columns"])

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open(
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        if reader.fieldnames != expected_columns:
            raise ValueError(
                f"Unexpected columns in {config['file_name']}.\n"
                f"Expected: {expected_columns}\n"
                f"Actual:   {reader.fieldnames}"
            )

        rows = []

        for row_number, row in enumerate(reader, start=2):
            try:
                converted_row = tuple(
                    convert_value(
                        value=row[column],
                        column=column,
                        nullable_columns=config["nullable"],
                    )
                    for column in config["columns"]
                )
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"Invalid data in {config['file_name']} "
                    f"at CSV row {row_number}: {error}"
                ) from error

            rows.append(converted_row)

    return rows


def prepare_source_data() -> dict[str, list[tuple[Any, ...]]]:
    """Load and validate every source CSV before modifying the database."""

    prepared_data = {}

    print("Preparing CSV source data...")

    for config in TABLE_CONFIGS:
        rows = read_csv_rows(config)
        prepared_data[config["table_name"]] = rows

        print(
            f"  {config['file_name']:<30} "
            f"{len(rows):>8,} rows"
        )

    return prepared_data


# ============================================================
# SQL SERVER LOAD
# ============================================================

def build_insert_statement(config: dict[str, Any]) -> str:
    """Build a parameterized INSERT statement for one table."""

    column_list = ", ".join(
        f"[{column}]" for column in config["columns"]
    )
    placeholders = ", ".join("?" for _ in config["columns"])

    return (
        f"INSERT INTO {config['table_name']} ({column_list}) "
        f"VALUES ({placeholders});"
    )


def clear_existing_data(cursor: pyodbc.Cursor) -> None:
    """Delete existing rows in reverse dependency order."""

    print("\nClearing existing table data...")

    for table_name in DELETE_ORDER:
        cursor.execute(f"DELETE FROM {table_name};")
        print(f"  Cleared {table_name}")


def insert_prepared_data(
    cursor: pyodbc.Cursor,
    prepared_data: dict[str, list[tuple[Any, ...]]],
) -> None:
    """Insert prepared rows in foreign-key dependency order."""

    print("\nLoading data into SQL Server...")
    # Standard execution avoids fast_executemany string-buffer truncation
    # when later rows contain longer text than the first parameter batch.
    cursor.fast_executemany = False

    for config in TABLE_CONFIGS:
        table_name = config["table_name"]
        rows = prepared_data[table_name]

        cursor.executemany(
            build_insert_statement(config),
            rows,
        )

        print(f"  {table_name:<36} {len(rows):>8,} rows loaded")


def verify_loaded_counts(
    cursor: pyodbc.Cursor,
    prepared_data: dict[str, list[tuple[Any, ...]]],
) -> None:
    """Compare every SQL Server table count with its source CSV count."""

    print("\nVerifying loaded row counts...")

    mismatches = []

    for config in TABLE_CONFIGS:
        table_name = config["table_name"]
        expected_count = len(prepared_data[table_name])

        cursor.execute(f"SELECT COUNT_BIG(*) FROM {table_name};")
        actual_count = int(cursor.fetchone()[0])

        status = "PASS" if actual_count == expected_count else "FAIL"

        print(
            f"  {table_name:<36} "
            f"CSV: {expected_count:>8,}  "
            f"SQL: {actual_count:>8,}  "
            f"{status}"
        )

        if actual_count != expected_count:
            mismatches.append(
                f"{table_name}: expected {expected_count}, "
                f"loaded {actual_count}"
            )

    if mismatches:
        raise RuntimeError(
            "Row-count verification failed:\n"
            + "\n".join(mismatches)
        )


def main() -> None:
    """Replace SQL Server table data with the validated source CSV data."""

    print("=" * 70)
    print("AUTOPARTS SQL SERVER DATA LOAD")
    print("=" * 70)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"SQL Server:   {SQL_SERVER}")
    print(f"Database:     {SQL_DATABASE}")
    print(f"ODBC driver:  {SQL_DRIVER}")

    connection = None

    try:
        prepared_data = prepare_source_data()

        print("\nConnecting to SQL Server...")
        connection = pyodbc.connect(
            CONNECTION_STRING,
            autocommit=False,
            timeout=30,
        )
        cursor = connection.cursor()

        clear_existing_data(cursor)
        insert_prepared_data(cursor, prepared_data)
        verify_loaded_counts(cursor, prepared_data)

        connection.commit()

    except Exception as error:
        if connection is not None:
            connection.rollback()

        print("\n" + "!" * 70)
        print("DATA LOAD FAILED")
        print(f"Reason: {error}")
        print("All database changes were rolled back.")
        print("!" * 70)

        raise SystemExit(1) from error

    finally:
        if connection is not None:
            connection.close()

    print("\n" + "=" * 70)
    print("DATA LOAD COMPLETED SUCCESSFULLY")
    print("All CSV and SQL Server row counts match.")
    print("=" * 70)


if __name__ == "__main__":
    main()
