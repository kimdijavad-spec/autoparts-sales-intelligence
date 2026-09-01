from pathlib import Path
import random

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_SEED = 47
NUMBER_OF_ORDER_LINES = 25_000

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_FOLDER = PROJECT_ROOT / "data" / "raw"

SALES_ORDERS_FILE = RAW_DATA_FOLDER / "sales_orders.csv"
CUSTOMERS_FILE = RAW_DATA_FOLDER / "customers.csv"
PRODUCTS_FILE = RAW_DATA_FOLDER / "products.csv"
CAMPAIGNS_FILE = RAW_DATA_FOLDER / "campaigns.csv"

OUTPUT_FILE = RAW_DATA_FOLDER / "sales_order_lines.csv"

random.seed(RANDOM_SEED)


# ============================================================
# BUSINESS ASSUMPTIONS
# ============================================================

LINE_COUNT_VALUES = [1, 2, 3, 4, 5]
LINE_COUNT_WEIGHTS = [0.12, 0.22, 0.30, 0.22, 0.14]

QUANTITY_RANGES = {
    "Auto Parts Retailer": (2, 20),
    "Repair Shop": (1, 8),
    "Regional Wholesaler": (10, 80),
    "Fleet Service Company": (3, 25),
}

DISCOUNT_RANGES = {
    "Auto Parts Retailer": (0, 8),
    "Repair Shop": (0, 5),
    "Regional Wholesaler": (5, 15),
    "Fleet Service Company": (3, 12),
}

CATEGORY_PREFERENCES = {
    "Auto Parts Retailer": {
        "Brake System": 0.18,
        "Filters": 0.18,
        "Engine Parts": 0.15,
        "Suspension": 0.13,
        "Electrical": 0.14,
        "Cooling System": 0.12,
        "Transmission": 0.10,
    },
    "Repair Shop": {
        "Brake System": 0.20,
        "Filters": 0.25,
        "Engine Parts": 0.20,
        "Suspension": 0.10,
        "Electrical": 0.15,
        "Cooling System": 0.06,
        "Transmission": 0.04,
    },
    "Regional Wholesaler": {
        "Brake System": 0.16,
        "Filters": 0.16,
        "Engine Parts": 0.15,
        "Suspension": 0.14,
        "Electrical": 0.14,
        "Cooling System": 0.13,
        "Transmission": 0.12,
    },
    "Fleet Service Company": {
        "Brake System": 0.22,
        "Filters": 0.22,
        "Engine Parts": 0.10,
        "Suspension": 0.18,
        "Electrical": 0.08,
        "Cooling System": 0.15,
        "Transmission": 0.05,
    },
}

RETURN_PROBABILITY = 0.03


# ============================================================
# VALIDATION HELPER
# ============================================================

def require(condition: bool, error_message: str) -> None:
    """Raise a readable validation error."""

    if not condition:
        raise ValueError(error_message)


# ============================================================
# ORDER-LINE COUNTS
# ============================================================

def create_order_line_counts(
    number_of_orders: int,
) -> list[int]:
    """Assign between one and five lines to every order."""

    line_counts = random.choices(
        LINE_COUNT_VALUES,
        weights=LINE_COUNT_WEIGHTS,
        k=number_of_orders,
    )

    current_total = sum(line_counts)

    while current_total < NUMBER_OF_ORDER_LINES:
        selected_index = random.randrange(number_of_orders)

        if line_counts[selected_index] < 5:
            line_counts[selected_index] += 1
            current_total += 1

    while current_total > NUMBER_OF_ORDER_LINES:
        selected_index = random.randrange(number_of_orders)

        if line_counts[selected_index] > 1:
            line_counts[selected_index] -= 1
            current_total -= 1

    return line_counts


# ============================================================
# PRODUCT SELECTION
# ============================================================

def get_category_weights(
    customer_type: str,
    order_month: int,
) -> tuple[list[str], list[float]]:
    """Return product-category preferences with seasonality."""

    preferences = CATEGORY_PREFERENCES[
        customer_type
    ].copy()

    # Summer cooling demand.
    if order_month in [6, 7, 8]:
        preferences["Cooling System"] *= 2.20

    # Autumn maintenance demand.
    if order_month in [9, 10, 11]:
        preferences["Brake System"] *= 1.35
        preferences["Filters"] *= 1.25

    categories = list(preferences.keys())
    weights = list(preferences.values())

    return categories, weights


def choose_product_id(
    customer_type: str,
    order_month: int,
    product_pools: dict[str, list[str]],
    selected_product_ids: set[str],
) -> str:
    """Choose a non-duplicate product for an order."""

    categories, weights = get_category_weights(
        customer_type,
        order_month,
    )

    for _ in range(100):
        selected_category = random.choices(
            categories,
            weights=weights,
            k=1,
        )[0]

        candidate_product_id = random.choice(
            product_pools[selected_category]
        )

        if candidate_product_id not in selected_product_ids:
            return candidate_product_id

    raise ValueError(
        "Could not select a unique product for an order."
    )


# ============================================================
# PRICE, DISCOUNT, QUANTITY, AND RETURNS
# ============================================================

def choose_quantity(customer_type: str) -> int:
    """Generate a quantity based on customer type."""

    minimum, maximum = QUANTITY_RANGES[customer_type]

    return random.randint(minimum, maximum)


def choose_discount(
    customer_type: str,
    campaign_discount: float | None,
) -> int:
    """Generate normal or campaign-adjusted discount."""

    minimum, maximum = DISCOUNT_RANGES[customer_type]

    normal_discount = random.randint(minimum, maximum)

    if campaign_discount is None:
        return normal_discount

    return max(
        normal_discount,
        int(campaign_discount),
    )


def choose_returned_quantity(quantity: int) -> int:
    """Generate a small number of returned units."""

    if random.random() >= RETURN_PROBABILITY:
        return 0

    maximum_return = max(
        1,
        min(quantity, round(quantity * 0.50)),
    )

    return random.randint(1, maximum_return)


# ============================================================
# ORDER-LINE GENERATION
# ============================================================

def create_sales_order_lines(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
    products: pd.DataFrame,
    campaigns: pd.DataFrame,
) -> pd.DataFrame:
    """Create all product lines for all sales orders."""

    order_line_counts = create_order_line_counts(
        len(orders)
    )

    customer_types = customers.set_index(
        "customer_id"
    )["customer_type"].to_dict()

    product_lookup = products.set_index(
        "product_id"
    ).to_dict(orient="index")

    active_products = products[
        products["status"] == "Active"
    ]

    product_pools = (
        active_products.groupby("category")["product_id"]
        .apply(list)
        .to_dict()
    )

    campaign_lookup = campaigns.set_index(
        "campaign_id"
    ).to_dict(orient="index")

    records = []
    line_number = 1

    for order_position, order in orders.iterrows():
        order_id = order["order_id"]
        customer_id = order["customer_id"]
        customer_type = customer_types[customer_id]
        order_month = order["order_date"].month

        number_of_lines = order_line_counts[
            order_position
        ]

        campaign_id = order["campaign_id"]

        campaign_discount = None
        target_product_category = None

        if pd.notna(campaign_id):
            campaign = campaign_lookup[campaign_id]

            campaign_discount = campaign[
                "offered_discount"
            ]

            target_product_category = campaign[
                "target_product_category"
            ]

        selected_product_ids = set()

        # A category-specific campaign must contain at least
        # one product from the promoted category.
        if (
            target_product_category is not None
            and target_product_category != "All Categories"
        ):
            forced_product_id = random.choice(
                product_pools[target_product_category]
            )

            selected_product_ids.add(forced_product_id)

        while len(selected_product_ids) < number_of_lines:
            selected_product_id = choose_product_id(
                customer_type=customer_type,
                order_month=order_month,
                product_pools=product_pools,
                selected_product_ids=selected_product_ids,
            )

            selected_product_ids.add(
                selected_product_id
            )

        for product_id in selected_product_ids:
            product = product_lookup[product_id]

            quantity = choose_quantity(customer_type)

            discount_percent = choose_discount(
                customer_type,
                campaign_discount,
            )

            returned_quantity = (
                choose_returned_quantity(quantity)
            )

            records.append(
                {
                    "order_line_id": (
                        f"OL{line_number:07d}"
                    ),
                    "order_id": order_id,
                    "product_id": product_id,
                    "quantity": quantity,
                    "unit_price": int(
                        product["list_price"]
                    ),
                    "discount_percent": (
                        discount_percent
                    ),
                    "returned_quantity": (
                        returned_quantity
                    ),
                }
            )

            line_number += 1

    return pd.DataFrame(records)


# ============================================================
# VALIDATION
# ============================================================

def validate_sales_order_lines(
    order_lines: pd.DataFrame,
    orders: pd.DataFrame,
    products: pd.DataFrame,
    campaigns: pd.DataFrame,
) -> None:
    """Validate order-line business rules."""

    require(
        len(order_lines) == NUMBER_OF_ORDER_LINES,
        (
            f"Expected {NUMBER_OF_ORDER_LINES} lines, "
            f"found {len(order_lines)}."
        ),
    )

    require(
        order_lines["order_line_id"].is_unique,
        "Duplicate order-line IDs were found.",
    )

    require(
        not order_lines.duplicated(
            subset=["order_id", "product_id"]
        ).any(),
        "An order contains the same product more than once.",
    )

    require(
        set(order_lines["order_id"])
        == set(orders["order_id"]),
        "Some orders have no lines or unknown orders exist.",
    )

    require(
        set(order_lines["product_id"]).issubset(
            set(products["product_id"])
        ),
        "Some order lines reference unknown products.",
    )

    lines_per_order = order_lines.groupby(
        "order_id"
    ).size()

    require(
        lines_per_order.between(
            1,
            5,
            inclusive="both",
        ).all(),
        "An order has fewer than 1 or more than 5 lines.",
    )

    require(
        (order_lines["quantity"] > 0).all(),
        "Order quantity must be greater than zero.",
    )

    require(
        (order_lines["unit_price"] > 0).all(),
        "Unit price must be greater than zero.",
    )

    require(
        order_lines["discount_percent"].between(
            0,
            100,
            inclusive="both",
        ).all(),
        "An invalid discount percentage was found.",
    )

    require(
        (
            order_lines["returned_quantity"] >= 0
        ).all(),
        "Returned quantity cannot be negative.",
    )

    require(
        (
            order_lines["returned_quantity"]
            <= order_lines["quantity"]
        ).all(),
        "Returned quantity exceeds sold quantity.",
    )

    campaign_requirements = (
        orders[orders["campaign_id"].notna()]
        .merge(
            campaigns[
                [
                    "campaign_id",
                    "target_product_category",
                ]
            ],
            on="campaign_id",
            how="left",
            validate="many_to_one",
        )
    )

    category_specific_orders = campaign_requirements[
        campaign_requirements[
            "target_product_category"
        ]
        != "All Categories"
    ]

    line_categories = order_lines.merge(
        products[["product_id", "category"]],
        on="product_id",
        how="left",
        validate="many_to_one",
    )

    campaign_category_check = (
        category_specific_orders[
            [
                "order_id",
                "target_product_category",
            ]
        ]
        .merge(
            line_categories[
                ["order_id", "category"]
            ],
            on="order_id",
            how="left",
            validate="one_to_many",
        )
    )

    matching_orders = set(
        campaign_category_check[
            campaign_category_check["category"]
            == campaign_category_check[
                "target_product_category"
            ]
        ]["order_id"]
    )

    required_orders = set(
        category_specific_orders["order_id"]
    )

    require(
        required_orders.issubset(matching_orders),
        (
            "A campaign order is missing a product "
            "from its promoted category."
        ),
    )


# ============================================================
# MAIN PROGRAM
# ============================================================

def main() -> None:
    """Generate, validate, and save order lines."""

    orders = pd.read_csv(
        SALES_ORDERS_FILE,
        parse_dates=["order_date"],
    )

    customers = pd.read_csv(CUSTOMERS_FILE)
    products = pd.read_csv(PRODUCTS_FILE)
    campaigns = pd.read_csv(CAMPAIGNS_FILE)

    order_lines = create_sales_order_lines(
        orders,
        customers,
        products,
        campaigns,
    )

    validate_sales_order_lines(
        order_lines,
        orders,
        products,
        campaigns,
    )

    order_lines.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    line_distribution = (
        order_lines.groupby("order_id")
        .size()
        .value_counts()
        .sort_index()
    )

    product_category_summary = (
        order_lines.merge(
            products[["product_id", "category"]],
            on="product_id",
            how="left",
        )["category"]
        .value_counts()
    )

    print(
        "Sales order-line generation completed successfully."
    )
    print(f"Order lines: {len(order_lines)}")
    print(
        "Average lines per order: "
        f"{len(order_lines) / len(orders):.3f}"
    )

    print("\nOrders by number of lines:")
    print(line_distribution.to_string())

    print("\nOrder lines by product category:")
    print(product_category_summary.to_string())

    print(
        "\nLines containing returns: "
        f"{(order_lines['returned_quantity'] > 0).sum()}"
    )
    print(
        "Total returned units: "
        f"{order_lines['returned_quantity'].sum()}"
    )

    print(f"\nOutput file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()