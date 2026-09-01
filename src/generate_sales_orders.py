from datetime import date, timedelta
from pathlib import Path
import random

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_SEED = 46
NUMBER_OF_ORDERS = 8_000

OBSERVATION_START = date(2024, 9, 1)
OBSERVATION_END = date(2026, 8, 31)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_FOLDER = PROJECT_ROOT / "data" / "raw"

CUSTOMERS_FILE = RAW_DATA_FOLDER / "customers.csv"
CAMPAIGNS_FILE = RAW_DATA_FOLDER / "campaigns.csv"
CAMPAIGN_TARGETS_FILE = RAW_DATA_FOLDER / "campaign_targets.csv"

OUTPUT_FILE = RAW_DATA_FOLDER / "sales_orders.csv"

random.seed(RANDOM_SEED)


# ============================================================
# BUSINESS ASSUMPTIONS
# ============================================================

CUSTOMER_TYPE_WEIGHTS = {
    "Auto Parts Retailer": 1.00,
    "Repair Shop": 0.65,
    "Regional Wholesaler": 1.60,
    "Fleet Service Company": 0.85,
}

CUSTOMER_STATUS_WEIGHTS = {
    "Active": 1.00,
    "On Hold": 0.45,
    "Inactive": 0.25,
}

PAYMENT_METHOD_CONFIG = {
    "Auto Parts Retailer": {
        "methods": [
            "Cash",
            "Bank Transfer",
            "Credit 30 Days",
            "Credit 60 Days",
        ],
        "weights": [0.15, 0.35, 0.35, 0.15],
    },
    "Repair Shop": {
        "methods": [
            "Cash",
            "Bank Transfer",
            "Credit 30 Days",
            "Credit 60 Days",
        ],
        "weights": [0.30, 0.40, 0.25, 0.05],
    },
    "Regional Wholesaler": {
        "methods": [
            "Cash",
            "Bank Transfer",
            "Credit 30 Days",
            "Credit 60 Days",
        ],
        "weights": [0.05, 0.25, 0.35, 0.35],
    },
    "Fleet Service Company": {
        "methods": [
            "Cash",
            "Bank Transfer",
            "Credit 30 Days",
            "Credit 60 Days",
        ],
        "weights": [0.05, 0.20, 0.35, 0.40],
    },
}

MONTH_WEIGHTS = {
    1: 0.90,
    2: 0.95,
    3: 1.25,
    4: 0.90,
    5: 0.95,
    6: 1.00,
    7: 1.15,
    8: 1.12,
    9: 1.08,
    10: 1.12,
    11: 1.18,
    12: 1.05,
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def require(condition: bool, error_message: str) -> None:
    """Raise a readable validation error."""

    if not condition:
        raise ValueError(error_message)


def random_date_between(
    start_date: date,
    end_date: date,
) -> date:
    """Return a random date between two dates."""

    day_count = (end_date - start_date).days

    return start_date + timedelta(
        days=random.randint(0, day_count)
    )


def weighted_order_date(
    start_date: date,
    end_date: date,
) -> date:
    """Generate an order date with monthly seasonality."""

    maximum_weight = max(MONTH_WEIGHTS.values())

    while True:
        candidate = random_date_between(
            start_date,
            end_date,
        )

        acceptance_probability = (
            MONTH_WEIGHTS[candidate.month]
            / maximum_weight
        )

        if random.random() <= acceptance_probability:
            return candidate


def choose_payment_method(customer_type: str) -> str:
    """Select a payment method based on customer type."""

    config = PAYMENT_METHOD_CONFIG[customer_type]

    return random.choices(
        config["methods"],
        weights=config["weights"],
        k=1,
    )[0]


def prepare_customer_weights(
    customers: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate purchase probability weights."""

    prepared_customers = customers.copy()

    prepared_customers["eligible_start"] = (
        prepared_customers["registration_date"].apply(
            lambda registration_date: max(
                registration_date.date(),
                OBSERVATION_START,
            )
        )
    )

    total_observation_days = (
        OBSERVATION_END - OBSERVATION_START
    ).days + 1

    prepared_customers["exposure_ratio"] = (
        prepared_customers["eligible_start"].apply(
            lambda eligible_start: (
                (OBSERVATION_END - eligible_start).days + 1
            )
            / total_observation_days
        )
    )

    prepared_customers["purchase_weight"] = (
        prepared_customers["customer_type"].map(
            CUSTOMER_TYPE_WEIGHTS
        )
        * prepared_customers["status"].map(
            CUSTOMER_STATUS_WEIGHTS
        )
        * prepared_customers["exposure_ratio"]
    )

    return prepared_customers


# ============================================================
# CAMPAIGN ORDERS
# ============================================================

def create_campaign_orders(
    customers: pd.DataFrame,
    campaigns: pd.DataFrame,
    campaign_targets: pd.DataFrame,
) -> list[dict]:
    """Create one attributed order for every conversion."""

    converted_targets = campaign_targets[
        campaign_targets["converted"]
    ].copy()

    campaign_details = converted_targets.merge(
        campaigns,
        on="campaign_id",
        how="left",
        validate="many_to_one",
    )

    customer_lookup = customers.set_index("customer_id")

    records = []

    for _, target in campaign_details.iterrows():
        customer = customer_lookup.loc[
            target["customer_id"]
        ]

        order_date = random_date_between(
            target["contact_date"].date(),
            target["end_date"].date(),
        )

        records.append(
            {
                "order_date": order_date,
                "customer_id": target["customer_id"],
                "sales_rep_id": customer["sales_rep_id"],
                "campaign_id": target["campaign_id"],
                "payment_method": choose_payment_method(
                    customer["customer_type"]
                ),
            }
        )

    return records


# ============================================================
# ORGANIC ORDERS
# ============================================================

def create_organic_orders(
    customers: pd.DataFrame,
    number_of_orders: int,
) -> list[dict]:
    """Create orders not directly attributed to campaigns."""

    customer_ids = customers["customer_id"].tolist()
    customer_weights = customers["purchase_weight"].tolist()

    customer_lookup = customers.set_index("customer_id")

    records = []

    for _ in range(number_of_orders):
        customer_id = random.choices(
            customer_ids,
            weights=customer_weights,
            k=1,
        )[0]

        customer = customer_lookup.loc[customer_id]

        order_date = weighted_order_date(
            customer["eligible_start"],
            OBSERVATION_END,
        )

        records.append(
            {
                "order_date": order_date,
                "customer_id": customer_id,
                "sales_rep_id": customer["sales_rep_id"],
                "campaign_id": None,
                "payment_method": choose_payment_method(
                    customer["customer_type"]
                ),
            }
        )

    return records


# ============================================================
# ORDER ASSEMBLY
# ============================================================

def create_sales_orders(
    customers: pd.DataFrame,
    campaigns: pd.DataFrame,
    campaign_targets: pd.DataFrame,
) -> pd.DataFrame:
    """Create campaign and organic sales orders."""

    campaign_orders = create_campaign_orders(
        customers,
        campaigns,
        campaign_targets,
    )

    organic_order_count = (
        NUMBER_OF_ORDERS - len(campaign_orders)
    )

    require(
        organic_order_count >= 0,
        "Campaign conversions exceed total order target.",
    )

    organic_orders = create_organic_orders(
        customers,
        organic_order_count,
    )

    all_orders = campaign_orders + organic_orders

    orders = pd.DataFrame(all_orders)

    orders = orders.sort_values(
        ["order_date", "customer_id"],
        ignore_index=True,
    )

    orders.insert(
        0,
        "order_id",
        [
            f"ORD{index:06d}"
            for index in range(1, len(orders) + 1)
        ],
    )

    return orders


# ============================================================
# VALIDATION
# ============================================================

def validate_sales_orders(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
    campaigns: pd.DataFrame,
    campaign_targets: pd.DataFrame,
) -> None:
    """Validate order dates and table relationships."""

    require(
        len(orders) == NUMBER_OF_ORDERS,
        (
            f"Expected {NUMBER_OF_ORDERS} orders, "
            f"found {len(orders)}."
        ),
    )

    require(
        orders["order_id"].is_unique,
        "Duplicate order IDs were found.",
    )

    require(
        orders["order_date"].between(
            pd.Timestamp(OBSERVATION_START),
            pd.Timestamp(OBSERVATION_END),
            inclusive="both",
        ).all(),
        "Some orders are outside the observation period.",
    )

    order_customer_check = orders.merge(
        customers[
            [
                "customer_id",
                "sales_rep_id",
                "registration_date",
            ]
        ],
        on="customer_id",
        how="left",
        suffixes=("_order", "_customer"),
        validate="many_to_one",
    )

    require(
        order_customer_check[
            "registration_date"
        ].notna().all(),
        "Some orders reference an unknown customer.",
    )

    require(
        (
            order_customer_check["sales_rep_id_order"]
            == order_customer_check["sales_rep_id_customer"]
        ).all(),
        "Some orders use the wrong sales representative.",
    )

    require(
        (
            order_customer_check["order_date"]
            >= order_customer_check["registration_date"]
        ).all(),
        "Some orders occurred before customer registration.",
    )

    campaign_orders = orders[
        orders["campaign_id"].notna()
    ].copy()

    converted_targets = campaign_targets[
        campaign_targets["converted"]
    ][
        [
            "campaign_id",
            "customer_id",
            "contact_date",
        ]
    ]

    campaign_order_check = campaign_orders.merge(
        converted_targets,
        on=["campaign_id", "customer_id"],
        how="left",
        validate="many_to_one",
    ).merge(
        campaigns[
            [
                "campaign_id",
                "start_date",
                "end_date",
            ]
        ],
        on="campaign_id",
        how="left",
        validate="many_to_one",
    )

    require(
        campaign_order_check["contact_date"].notna().all(),
        "A campaign order has no converted campaign target.",
    )

    require(
        (
            campaign_order_check["order_date"]
            >= campaign_order_check["contact_date"]
        ).all(),
        "A campaign order occurred before customer contact.",
    )

    require(
        (
            campaign_order_check["order_date"]
            <= campaign_order_check["end_date"]
        ).all(),
        "A campaign order occurred after the campaign ended.",
    )

    converted_pairs = set(
        zip(
            converted_targets["campaign_id"],
            converted_targets["customer_id"],
        )
    )

    order_pairs = set(
        zip(
            campaign_orders["campaign_id"],
            campaign_orders["customer_id"],
        )
    )

    require(
        converted_pairs.issubset(order_pairs),
        "Some campaign conversions do not have an order.",
    )


# ============================================================
# MAIN PROGRAM
# ============================================================

def main() -> None:
    """Generate, validate, and save sales orders."""

    customers = pd.read_csv(
        CUSTOMERS_FILE,
        parse_dates=["registration_date"],
    )

    campaigns = pd.read_csv(
        CAMPAIGNS_FILE,
        parse_dates=["start_date", "end_date"],
    )

    campaign_targets = pd.read_csv(
        CAMPAIGN_TARGETS_FILE,
        parse_dates=["contact_date"],
    )

    if campaign_targets["converted"].dtype != bool:
        campaign_targets["converted"] = (
            campaign_targets["converted"]
            .astype(str)
            .str.lower()
            .eq("true")
        )

    customers = prepare_customer_weights(customers)

    orders = create_sales_orders(
        customers,
        campaigns,
        campaign_targets,
    )

    orders["order_date"] = pd.to_datetime(
        orders["order_date"]
    )

    validate_sales_orders(
        orders,
        customers,
        campaigns,
        campaign_targets,
    )

    orders.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
        date_format="%Y-%m-%d",
    )

    campaign_order_count = (
        orders["campaign_id"].notna().sum()
    )

    print("Sales order generation completed successfully.")
    print(f"Total orders: {len(orders)}")
    print(f"Campaign-attributed orders: {campaign_order_count}")
    print(
        "Organic orders: "
        f"{len(orders) - campaign_order_count}"
    )
    print(
        "Unique purchasing customers: "
        f"{orders['customer_id'].nunique()}"
    )
    print(
        "Order period: "
        f"{orders['order_date'].min().date()} to "
        f"{orders['order_date'].max().date()}"
    )

    print("\nPayment methods:")
    print(
        orders["payment_method"]
        .value_counts()
        .to_string()
    )

    print(f"\nOutput file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()