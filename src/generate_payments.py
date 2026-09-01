from datetime import date, timedelta
from pathlib import Path
import random

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_SEED = 48
AS_OF_DATE = date(2026, 8, 31)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_FOLDER = PROJECT_ROOT / "data" / "raw"

SALES_ORDERS_FILE = RAW_DATA_FOLDER / "sales_orders.csv"
ORDER_LINES_FILE = RAW_DATA_FOLDER / "sales_order_lines.csv"
CUSTOMERS_FILE = RAW_DATA_FOLDER / "customers.csv"

OUTPUT_FILE = RAW_DATA_FOLDER / "payments.csv"

random.seed(RANDOM_SEED)


# ============================================================
# PAYMENT ASSUMPTIONS
# ============================================================

PAYMENT_TERM_DAYS = {
    "Cash": 0,
    "Bank Transfer": 0,
    "Credit 30 Days": 30,
    "Credit 60 Days": 60,
}

UNPAID_PROBABILITY = {
    "Active": 0.04,
    "On Hold": 0.16,
    "Inactive": 0.30,
}

PAYMENT_TIMING_WEIGHTS = {
    "Active": [0.60, 0.30, 0.10],
    "On Hold": [0.35, 0.35, 0.30],
    "Inactive": [0.20, 0.30, 0.50],
}


# ============================================================
# VALIDATION HELPER
# ============================================================

def require(condition: bool, error_message: str) -> None:
    """Raise a readable validation error."""

    if not condition:
        raise ValueError(error_message)


# ============================================================
# INVOICE CALCULATION
# ============================================================

def calculate_invoice_amounts(
    order_lines: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate one invoice amount for every order."""

    calculated_lines = order_lines.copy()

    calculated_lines["net_quantity"] = (
        calculated_lines["quantity"]
        - calculated_lines["returned_quantity"]
    )

    calculated_lines["line_invoice_amount"] = (
        calculated_lines["net_quantity"]
        * calculated_lines["unit_price"]
        * (
            1
            - calculated_lines["discount_percent"]
            / 100
        )
    ).round()

    invoice_amounts = (
        calculated_lines.groupby(
            "order_id",
            as_index=False,
        )["line_invoice_amount"]
        .sum()
        .rename(
            columns={
                "line_invoice_amount": "invoice_amount"
            }
        )
    )

    invoice_amounts["invoice_amount"] = (
        invoice_amounts["invoice_amount"].astype(
            "int64"
        )
    )

    return invoice_amounts


# ============================================================
# PAYMENT BEHAVIOR
# ============================================================

def choose_payment_delay(
    customer_status: str,
) -> int:
    """Choose payment timing relative to the due date."""

    timing_group = random.choices(
        [
            "Early or On Time",
            "Slightly Late",
            "Very Late",
        ],
        weights=PAYMENT_TIMING_WEIGHTS[
            customer_status
        ],
        k=1,
    )[0]

    if timing_group == "Early or On Time":
        return random.randint(-10, 0)

    if timing_group == "Slightly Late":
        return random.randint(1, 15)

    return random.randint(16, 45)


def create_payment_record(
    order: pd.Series,
    payment_number: int,
) -> dict:
    """Create a payment record for one order."""

    invoice_date = order["order_date"].date()
    payment_method = order["payment_method"]
    customer_status = order["customer_status"]
    invoice_amount = int(order["invoice_amount"])

    payment_term = PAYMENT_TERM_DAYS[
        payment_method
    ]

    due_date = invoice_date + timedelta(
        days=payment_term
    )

    # A fully returned order has no remaining balance.
    if invoice_amount == 0:
        return {
            "payment_id": f"PAY{payment_number:06d}",
            "order_id": order["order_id"],
            "customer_id": order["customer_id"],
            "invoice_amount": invoice_amount,
            "invoice_date": invoice_date,
            "due_date": due_date,
            "paid_date": invoice_date,
            "payment_status": "Paid",
        }

    # Cash and bank-transfer orders are paid immediately.
    if payment_method == "Cash":
        paid_date = invoice_date
        payment_status = "Paid"

    elif payment_method == "Bank Transfer":
        candidate_paid_date = (
            invoice_date
            + timedelta(days=random.randint(0, 2))
        )

        if candidate_paid_date <= AS_OF_DATE:
            paid_date = candidate_paid_date
            payment_status = "Paid"

        elif due_date >= AS_OF_DATE:
            paid_date = None
            payment_status = "Outstanding"

        else:
            paid_date = None
            payment_status = "Overdue"

    # Credit invoices that are not due yet remain outstanding.
    elif due_date >= AS_OF_DATE:
        paid_date = None
        payment_status = "Outstanding"

    # Credit invoices already past their due date.
    else:
        remains_unpaid = (
            random.random()
            < UNPAID_PROBABILITY[customer_status]
        )

        if remains_unpaid:
            paid_date = None
            payment_status = "Overdue"

        else:
            payment_delay = choose_payment_delay(
                customer_status
            )

            candidate_paid_date = (
                due_date
                + timedelta(days=payment_delay)
            )

            candidate_paid_date = max(
                candidate_paid_date,
                invoice_date,
            )

            if candidate_paid_date <= AS_OF_DATE:
                paid_date = candidate_paid_date
                payment_status = "Paid"
            else:
                paid_date = None
                payment_status = "Overdue"

    return {
        "payment_id": f"PAY{payment_number:06d}",
        "order_id": order["order_id"],
        "customer_id": order["customer_id"],
        "invoice_amount": invoice_amount,
        "invoice_date": invoice_date,
        "due_date": due_date,
        "paid_date": paid_date,
        "payment_status": payment_status,
    }


def create_payments(
    orders: pd.DataFrame,
    invoice_amounts: pd.DataFrame,
    customers: pd.DataFrame,
) -> pd.DataFrame:
    """Create one payment obligation per order."""

    payment_source = (
        orders.merge(
            invoice_amounts,
            on="order_id",
            how="left",
            validate="one_to_one",
        )
        .merge(
            customers[
                [
                    "customer_id",
                    "status",
                ]
            ],
            on="customer_id",
            how="left",
            validate="many_to_one",
        )
        .rename(
            columns={
                "status": "customer_status"
            }
        )
    )

    records = []

    for index, order in payment_source.iterrows():
        records.append(
            create_payment_record(
                order=order,
                payment_number=index + 1,
            )
        )

    return pd.DataFrame(records)


# ============================================================
# VALIDATION
# ============================================================

def validate_payments(
    payments: pd.DataFrame,
    orders: pd.DataFrame,
) -> None:
    """Validate payment records and statuses."""

    require(
        len(payments) == len(orders),
        "Every order must have one payment record.",
    )

    require(
        payments["payment_id"].is_unique,
        "Duplicate payment IDs were found.",
    )

    require(
        payments["order_id"].is_unique,
        "An order has more than one payment record.",
    )

    require(
        set(payments["order_id"])
        == set(orders["order_id"]),
        "Payment and order IDs do not match.",
    )

    require(
        (payments["invoice_amount"] >= 0).all(),
        "Invoice amount cannot be negative.",
    )

    require(
        (
            payments["due_date"]
            >= payments["invoice_date"]
        ).all(),
        "A due date occurs before its invoice date.",
    )

    paid_payments = payments[
        payments["payment_status"] == "Paid"
    ]

    unpaid_payments = payments[
        payments["payment_status"].isin(
            ["Outstanding", "Overdue"]
        )
    ]

    require(
        paid_payments["paid_date"].notna().all(),
        "A paid invoice has no paid date.",
    )

    require(
        unpaid_payments["paid_date"].isna().all(),
        "An unpaid invoice incorrectly has a paid date.",
    )

    require(
        (
            paid_payments["paid_date"]
            >= paid_payments["invoice_date"]
        ).all(),
        "A payment occurred before its invoice date.",
    )

    require(
        (
            paid_payments["paid_date"]
            <= pd.Timestamp(AS_OF_DATE)
        ).all(),
        "A payment occurred after the analysis date.",
    )

    overdue_payments = payments[
        payments["payment_status"] == "Overdue"
    ]

    outstanding_payments = payments[
        payments["payment_status"] == "Outstanding"
    ]

    require(
        (
            overdue_payments["due_date"]
            < pd.Timestamp(AS_OF_DATE)
        ).all(),
        "An overdue invoice has not reached its due date.",
    )

    require(
        (
            outstanding_payments["due_date"]
            >= pd.Timestamp(AS_OF_DATE)
        ).all(),
        "An outstanding invoice should be overdue.",
    )


# ============================================================
# MAIN PROGRAM
# ============================================================

def main() -> None:
    """Generate, validate, and save customer payments."""

    orders = pd.read_csv(
        SALES_ORDERS_FILE,
        parse_dates=["order_date"],
    )

    order_lines = pd.read_csv(ORDER_LINES_FILE)
    customers = pd.read_csv(CUSTOMERS_FILE)

    invoice_amounts = calculate_invoice_amounts(
        order_lines
    )

    payments = create_payments(
        orders,
        invoice_amounts,
        customers,
    )

    payments["invoice_date"] = pd.to_datetime(
        payments["invoice_date"]
    )

    payments["due_date"] = pd.to_datetime(
        payments["due_date"]
    )

    payments["paid_date"] = pd.to_datetime(
        payments["paid_date"]
    )

    validate_payments(payments, orders)

    payments.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
        date_format="%Y-%m-%d",
    )

    status_summary = (
        payments["payment_status"]
        .value_counts()
    )

    overdue_amount = payments.loc[
        payments["payment_status"] == "Overdue",
        "invoice_amount",
    ].sum()

    outstanding_amount = payments.loc[
        payments["payment_status"] == "Outstanding",
        "invoice_amount",
    ].sum()

    print("Payment generation completed successfully.")
    print(f"Payment records: {len(payments)}")
    print(
        "Total invoiced amount: "
        f"{payments['invoice_amount'].sum():,.0f} IRR"
    )

    print("\nPayment statuses:")
    print(status_summary.to_string())

    print(
        "\nOverdue amount: "
        f"{overdue_amount:,.0f} IRR"
    )

    print(
        "Outstanding amount: "
        f"{outstanding_amount:,.0f} IRR"
    )

    print(f"\nOutput file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
