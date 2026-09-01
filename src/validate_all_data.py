"""Run project-wide data quality checks for all generated raw CSV files."""

from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_FOLDER = PROJECT_ROOT / "data" / "raw"
AS_OF_DATE = pd.Timestamp("2026-08-31")


SCHEMAS = {
    "campaign_targets.csv": [
        "campaign_id", "customer_id", "contact_date", "message_delivered",
        "customer_engaged", "sales_followup", "converted",
    ],
    "campaigns.csv": [
        "campaign_id", "campaign_name", "channel", "start_date", "end_date",
        "budget", "target_customer_type", "target_product_category",
        "offered_discount",
    ],
    "customers.csv": [
        "customer_id", "customer_name", "customer_type", "province", "city",
        "registration_date", "credit_limit", "sales_rep_id", "status",
    ],
    "payments.csv": [
        "payment_id", "order_id", "customer_id", "invoice_amount",
        "invoice_date", "due_date", "paid_date", "payment_status",
    ],
    "products.csv": [
        "product_id", "sku", "product_name", "category", "brand",
        "compatible_vehicle", "unit_cost", "list_price", "reorder_point",
        "status",
    ],
    "sales_order_lines.csv": [
        "order_line_id", "order_id", "product_id", "quantity", "unit_price",
        "discount_percent", "returned_quantity",
    ],
    "sales_orders.csv": [
        "order_id", "order_date", "customer_id", "sales_rep_id",
        "campaign_id", "payment_method",
    ],
    "sales_representatives.csv": [
        "sales_rep_id", "sales_rep_name", "region", "hire_date",
        "monthly_target", "status",
    ],
}


PRIMARY_KEYS = {
    "campaigns": "campaign_id",
    "customers": "customer_id",
    "payments": "payment_id",
    "products": "product_id",
    "sales_order_lines": "order_line_id",
    "sales_orders": "order_id",
    "sales_representatives": "sales_rep_id",
}


DATE_COLUMNS = {
    "campaign_targets": ["contact_date"],
    "campaigns": ["start_date", "end_date"],
    "customers": ["registration_date"],
    "payments": ["invoice_date", "due_date", "paid_date"],
    "sales_orders": ["order_date"],
    "sales_representatives": ["hire_date"],
}


def add_check(condition: bool, message: str, failures: list[str]) -> None:
    """Collect every failed check instead of stopping at the first one."""
    if not bool(condition):
        failures.append(message)


def missing_references(child: pd.Series, parent: pd.Series) -> set[str]:
    """Return non-null foreign-key values missing from the parent table."""
    child_values = set(child.dropna().astype(str))
    parent_values = set(parent.dropna().astype(str))
    return child_values - parent_values


def load_data(failures: list[str]) -> dict[str, pd.DataFrame]:
    """Load files, validate schemas, and parse date columns."""
    data: dict[str, pd.DataFrame] = {}

    for filename, required_columns in SCHEMAS.items():
        path = RAW_DATA_FOLDER / filename
        table_name = path.stem

        if not path.exists():
            failures.append(f"Missing file: {filename}")
            continue

        frame = pd.read_csv(path)
        missing_columns = sorted(set(required_columns) - set(frame.columns))
        if missing_columns:
            failures.append(
                f"{filename}: missing columns {missing_columns}"
            )
            continue

        frame = frame[required_columns].copy()

        for column in DATE_COLUMNS.get(table_name, []):
            original_non_null = frame[column].notna()
            frame[column] = pd.to_datetime(frame[column], errors="coerce")
            invalid_count = int((original_non_null & frame[column].isna()).sum())
            if invalid_count:
                failures.append(
                    f"{filename}.{column}: {invalid_count} invalid date value(s)"
                )

        data[table_name] = frame

    return data


def validate_basic_quality(
    data: dict[str, pd.DataFrame], failures: list[str]
) -> None:
    """Validate row presence, primary keys, duplicates, and required values."""
    nullable_columns = {
        ("sales_orders", "campaign_id"),
        ("payments", "paid_date"),
    }

    for table_name, frame in data.items():
        add_check(not frame.empty, f"{table_name}: table is empty", failures)
        add_check(
            not frame.duplicated().any(),
            f"{table_name}: fully duplicated row(s) found",
            failures,
        )

        for column in frame.columns:
            if (table_name, column) not in nullable_columns:
                null_count = int(frame[column].isna().sum())
                add_check(
                    null_count == 0,
                    f"{table_name}.{column}: {null_count} missing value(s)",
                    failures,
                )

        primary_key = PRIMARY_KEYS.get(table_name)
        if primary_key:
            add_check(
                frame[primary_key].notna().all(),
                f"{table_name}.{primary_key}: null primary key found",
                failures,
            )
            add_check(
                frame[primary_key].is_unique,
                f"{table_name}.{primary_key}: duplicate primary key found",
                failures,
            )


def validate_relationships(
    data: dict[str, pd.DataFrame], failures: list[str]
) -> None:
    """Validate foreign keys and important cross-table relationships."""
    required_tables = set(SCHEMAS_FILE.removesuffix(".csv") for SCHEMAS_FILE in SCHEMAS)
    if not required_tables.issubset(data):
        return

    targets = data["campaign_targets"]
    campaigns = data["campaigns"]
    customers = data["customers"]
    payments = data["payments"]
    products = data["products"]
    lines = data["sales_order_lines"]
    orders = data["sales_orders"]
    reps = data["sales_representatives"]

    relationships = [
        ("customers.sales_rep_id", customers["sales_rep_id"], reps["sales_rep_id"]),
        ("campaign_targets.campaign_id", targets["campaign_id"], campaigns["campaign_id"]),
        ("campaign_targets.customer_id", targets["customer_id"], customers["customer_id"]),
        ("sales_orders.customer_id", orders["customer_id"], customers["customer_id"]),
        ("sales_orders.sales_rep_id", orders["sales_rep_id"], reps["sales_rep_id"]),
        ("sales_orders.campaign_id", orders["campaign_id"], campaigns["campaign_id"]),
        ("sales_order_lines.order_id", lines["order_id"], orders["order_id"]),
        ("sales_order_lines.product_id", lines["product_id"], products["product_id"]),
        ("payments.order_id", payments["order_id"], orders["order_id"]),
        ("payments.customer_id", payments["customer_id"], customers["customer_id"]),
    ]

    for relationship_name, child, parent in relationships:
        missing = missing_references(child, parent)
        add_check(
            not missing,
            f"{relationship_name}: {len(missing)} orphan foreign-key value(s)",
            failures,
        )

    add_check(
        not targets.duplicated(["campaign_id", "customer_id"]).any(),
        "campaign_targets: duplicate campaign/customer pair found",
        failures,
    )
    add_check(
        set(lines["order_id"]) == set(orders["order_id"]),
        "sales_order_lines: every order must have at least one line",
        failures,
    )
    add_check(
        payments["order_id"].is_unique,
        "payments: every order must have no more than one payment record",
        failures,
    )
    add_check(
        set(payments["order_id"]) == set(orders["order_id"]),
        "payments: every order must have exactly one payment record",
        failures,
    )

    payment_customer = payments[["order_id", "customer_id"]].merge(
        orders[["order_id", "customer_id"]],
        on="order_id",
        suffixes=("_payment", "_order"),
        validate="one_to_one",
    )
    add_check(
        payment_customer["customer_id_payment"].eq(
            payment_customer["customer_id_order"]
        ).all(),
        "payments: payment customer does not match order customer",
        failures,
    )

    attributed_orders = orders[orders["campaign_id"].notna()]
    converted_targets = targets[targets["converted"].astype(bool)][
        ["campaign_id", "customer_id"]
    ].drop_duplicates()
    attributed_match = attributed_orders.merge(
        converted_targets,
        on=["campaign_id", "customer_id"],
        how="left",
        indicator=True,
    )
    add_check(
        attributed_match["_merge"].eq("both").all(),
        "sales_orders: campaign-attributed order without a converted target",
        failures,
    )


def validate_business_rules(
    data: dict[str, pd.DataFrame], failures: list[str]
) -> None:
    """Validate numerical, date, status, funnel, and invoice rules."""
    required_tables = set(filename.removesuffix(".csv") for filename in SCHEMAS)
    if not required_tables.issubset(data):
        return

    targets = data["campaign_targets"]
    campaigns = data["campaigns"]
    customers = data["customers"]
    payments = data["payments"]
    products = data["products"]
    lines = data["sales_order_lines"]
    orders = data["sales_orders"]
    reps = data["sales_representatives"]

    add_check((customers["credit_limit"] >= 0).all(), "customers: negative credit limit", failures)
    add_check((reps["monthly_target"] > 0).all(), "sales_representatives: non-positive target", failures)
    add_check((campaigns["budget"] > 0).all(), "campaigns: non-positive budget", failures)
    add_check(campaigns["offered_discount"].between(0, 100).all(), "campaigns: discount outside 0..100", failures)
    add_check((campaigns["start_date"] <= campaigns["end_date"]).all(), "campaigns: start date after end date", failures)
    add_check((products["unit_cost"] >= 0).all(), "products: negative unit cost", failures)
    add_check((products["list_price"] > 0).all(), "products: non-positive list price", failures)
    add_check((products["list_price"] >= products["unit_cost"]).all(), "products: list price below unit cost", failures)
    add_check((products["reorder_point"] >= 0).all(), "products: negative reorder point", failures)
    add_check((lines["quantity"] > 0).all(), "sales_order_lines: non-positive quantity", failures)
    add_check((lines["unit_price"] >= 0).all(), "sales_order_lines: negative unit price", failures)
    add_check(lines["discount_percent"].between(0, 100).all(), "sales_order_lines: discount outside 0..100", failures)
    add_check((lines["returned_quantity"] >= 0).all(), "sales_order_lines: negative returned quantity", failures)
    add_check((lines["returned_quantity"] <= lines["quantity"]).all(), "sales_order_lines: returns exceed quantity", failures)
    add_check((orders["order_date"] <= AS_OF_DATE).all(), "sales_orders: order after analysis date", failures)

    target_campaign_dates = targets.merge(
        campaigns[["campaign_id", "start_date", "end_date"]],
        on="campaign_id",
        validate="many_to_one",
    )
    add_check(
        target_campaign_dates["contact_date"].between(
            target_campaign_dates["start_date"], target_campaign_dates["end_date"]
        ).all(),
        "campaign_targets: contact date outside campaign period",
        failures,
    )

    delivered = targets["message_delivered"].astype(bool)
    engaged = targets["customer_engaged"].astype(bool)
    followed_up = targets["sales_followup"].astype(bool)
    converted = targets["converted"].astype(bool)
    add_check((~engaged | delivered).all(), "campaign_targets: engagement without delivery", failures)
    add_check((~followed_up | engaged).all(), "campaign_targets: follow-up without engagement", failures)
    add_check((~converted | engaged).all(), "campaign_targets: conversion without engagement", failures)

    campaign_orders = orders[orders["campaign_id"].notna()].merge(
        campaigns[["campaign_id", "start_date", "end_date"]],
        on="campaign_id",
        validate="many_to_one",
    )
    add_check(
        campaign_orders["order_date"].between(
            campaign_orders["start_date"], campaign_orders["end_date"]
        ).all(),
        "sales_orders: attributed order outside campaign period",
        failures,
    )

    expected_invoices = lines.copy()
    expected_invoices["expected_invoice_amount"] = (
        (expected_invoices["quantity"] - expected_invoices["returned_quantity"])
        * expected_invoices["unit_price"]
        * (1 - expected_invoices["discount_percent"] / 100)
    ).round()
    expected_invoices = expected_invoices.groupby("order_id", as_index=False)[
        "expected_invoice_amount"
    ].sum()
    invoice_check = payments.merge(
        expected_invoices, on="order_id", validate="one_to_one"
    )
    add_check(
        invoice_check["invoice_amount"].eq(
            invoice_check["expected_invoice_amount"]
        ).all(),
        "payments: invoice amount does not match order-line calculation",
        failures,
    )

    add_check((payments["invoice_amount"] >= 0).all(), "payments: negative invoice amount", failures)
    add_check((payments["due_date"] >= payments["invoice_date"]).all(), "payments: due date before invoice date", failures)

    paid = payments[payments["payment_status"] == "Paid"]
    overdue = payments[payments["payment_status"] == "Overdue"]
    outstanding = payments[payments["payment_status"] == "Outstanding"]
    unpaid = payments[payments["payment_status"].isin(["Overdue", "Outstanding"])]

    add_check(paid["paid_date"].notna().all(), "payments: paid invoice without paid date", failures)
    add_check(unpaid["paid_date"].isna().all(), "payments: unpaid invoice with paid date", failures)
    add_check((paid["paid_date"] >= paid["invoice_date"]).all(), "payments: paid date before invoice date", failures)
    add_check((paid["paid_date"] <= AS_OF_DATE).all(), "payments: paid date after analysis date", failures)
    add_check((overdue["due_date"] < AS_OF_DATE).all(), "payments: overdue status before due date", failures)
    add_check((outstanding["due_date"] >= AS_OF_DATE).all(), "payments: outstanding status after due date", failures)

    allowed_values = {
        "customers.status": (customers["status"], {"Active", "Inactive", "On Hold"}),
        "products.status": (products["status"], {"Active", "Temporarily Unavailable", "Discontinued"}),
        "payments.payment_status": (payments["payment_status"], {"Paid", "Outstanding", "Overdue"}),
        "sales_orders.payment_method": (orders["payment_method"], {"Cash", "Bank Transfer", "Credit 30 Days", "Credit 60 Days"}),
    }
    for label, (series, allowed) in allowed_values.items():
        unexpected = set(series.dropna()) - allowed
        add_check(not unexpected, f"{label}: unexpected value(s) {sorted(unexpected)}", failures)


def print_summary(data: dict[str, pd.DataFrame], failures: list[str]) -> None:
    """Print a concise, portfolio-friendly validation report."""
    print("=" * 70)
    print("AUTOPARTS DATA QUALITY REPORT")
    print("=" * 70)

    for table_name in sorted(data):
        print(f"{table_name:25} {len(data[table_name]):>8,} rows")

    print("-" * 70)
    if failures:
        print(f"RESULT: FAILED ({len(failures)} issue(s))")
        for number, failure in enumerate(failures, start=1):
            print(f"{number}. {failure}")
    else:
        print("RESULT: PASSED")
        print("All schema, completeness, relationship, and business-rule checks passed.")
    print("=" * 70)


def main() -> None:
    failures: list[str] = []
    data = load_data(failures)
    validate_basic_quality(data, failures)
    validate_relationships(data, failures)
    validate_business_rules(data, failures)
    print_summary(data, failures)

    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
