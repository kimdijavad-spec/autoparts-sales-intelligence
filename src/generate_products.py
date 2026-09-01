from pathlib import Path
import random

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_SEED = 43
NUMBER_OF_PRODUCTS = 300

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_FOLDER = PROJECT_ROOT / "data" / "raw"

random.seed(RANDOM_SEED)


# ============================================================
# PRODUCT MASTER DATA
# ============================================================

CATEGORY_CONFIG = {
    "Brake System": {
        "code": "BRK",
        "parts": [
            "Front Brake Pad Set",
            "Rear Brake Pad Set",
            "Brake Disc",
            "Brake Master Cylinder",
            "Wheel Cylinder",
        ],
        "cost_range": (3_000_000, 35_000_000),
        "reorder_range": (15, 70),
    },
    "Filters": {
        "code": "FLT",
        "parts": [
            "Oil Filter",
            "Air Filter",
            "Fuel Filter",
            "Cabin Filter",
        ],
        "cost_range": (1_000_000, 8_000_000),
        "reorder_range": (30, 120),
    },
    "Engine Parts": {
        "code": "ENG",
        "parts": [
            "Timing Belt Kit",
            "Piston Ring Set",
            "Cylinder Head Gasket",
            "Engine Mount",
            "Oil Pump",
        ],
        "cost_range": (5_000_000, 90_000_000),
        "reorder_range": (8, 40),
    },
    "Suspension": {
        "code": "SUS",
        "parts": [
            "Front Shock Absorber",
            "Rear Shock Absorber",
            "Control Arm",
            "Ball Joint",
            "Tie Rod End",
        ],
        "cost_range": (4_000_000, 45_000_000),
        "reorder_range": (10, 50),
    },
    "Electrical": {
        "code": "ELC",
        "parts": [
            "Spark Plug Set",
            "Ignition Coil",
            "Alternator",
            "Starter Motor",
            "Crankshaft Sensor",
        ],
        "cost_range": (2_000_000, 80_000_000),
        "reorder_range": (10, 60),
    },
    "Cooling System": {
        "code": "COL",
        "parts": [
            "Radiator",
            "Thermostat",
            "Cooling Fan",
            "Expansion Tank",
            "Coolant Hose Set",
        ],
        "cost_range": (3_000_000, 55_000_000),
        "reorder_range": (8, 45),
    },
    "Transmission": {
        "code": "TRN",
        "parts": [
            "Clutch Kit",
            "Gearbox Mount",
            "CV Joint",
            "Clutch Cable",
            "Release Bearing",
        ],
        "cost_range": (4_000_000, 100_000_000),
        "reorder_range": (6, 35),
    },
}

CATEGORY_WEIGHTS = [
    0.18,
    0.17,
    0.16,
    0.14,
    0.14,
    0.11,
    0.10,
]

BRANDS = [
    "Bosch",
    "Valeo",
    "Denso",
    "NGK",
    "SKF",
    "Sachs",
    "Mahle",
    "Brembo",
    "Gates",
    "Mann-Filter",
    "Isaco",
    "Saipa Yadak",
]

COMPATIBLE_VEHICLES = [
    "Peugeot 206",
    "Peugeot 405",
    "Peugeot Pars",
    "Peugeot 207",
    "Samand",
    "Dena",
    "Pride",
    "Tiba",
    "Quick",
    "Shahin",
    "Renault L90",
    "Renault Sandero",
    "Hyundai Accent",
    "Kia Cerato",
    "Toyota Corolla",
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def round_to_hundred_thousand(value: float) -> int:
    """Round a monetary value to the nearest 100,000 IRR."""

    return round(value / 100_000) * 100_000


def create_products() -> pd.DataFrame:
    """Create the synthetic automotive products dataset."""

    records = []
    categories = list(CATEGORY_CONFIG.keys())

    for index in range(1, NUMBER_OF_PRODUCTS + 1):
        category = random.choices(
            categories,
            weights=CATEGORY_WEIGHTS,
            k=1,
        )[0]

        category_details = CATEGORY_CONFIG[category]

        part_name = random.choice(category_details["parts"])
        brand = random.choice(BRANDS)
        compatible_vehicle = random.choice(COMPATIBLE_VEHICLES)

        minimum_cost, maximum_cost = category_details["cost_range"]

        unit_cost = round_to_hundred_thousand(
            random.randint(minimum_cost, maximum_cost)
        )

        markup_multiplier = random.uniform(1.20, 1.65)

        list_price = round_to_hundred_thousand(
            unit_cost * markup_multiplier
        )

        minimum_reorder, maximum_reorder = (
            category_details["reorder_range"]
        )

        reorder_point = random.randint(
            minimum_reorder,
            maximum_reorder,
        )

        product_status = random.choices(
            [
                "Active",
                "Temporarily Unavailable",
                "Discontinued",
            ],
            weights=[0.94, 0.04, 0.02],
            k=1,
        )[0]

        category_code = category_details["code"]

        records.append(
            {
                "product_id": f"PRD{index:04d}",
                "sku": f"{category_code}-{index:04d}",
                "product_name": (
                    f"{brand} {part_name} for "
                    f"{compatible_vehicle}"
                ),
                "category": category,
                "brand": brand,
                "compatible_vehicle": compatible_vehicle,
                "unit_cost": unit_cost,
                "list_price": list_price,
                "reorder_point": reorder_point,
                "status": product_status,
            }
        )

    return pd.DataFrame(records)


def validate_products(products: pd.DataFrame) -> None:
    """Run basic checks before saving the products file."""

    assert len(products) == NUMBER_OF_PRODUCTS
    assert products["product_id"].is_unique
    assert products["sku"].is_unique

    assert not products.isna().any().any()

    assert (products["unit_cost"] > 0).all()
    assert (products["list_price"] > products["unit_cost"]).all()
    assert (products["reorder_point"] > 0).all()


# ============================================================
# MAIN PROGRAM
# ============================================================

def main() -> None:
    """Generate, validate, and save product data."""

    RAW_DATA_FOLDER.mkdir(parents=True, exist_ok=True)

    products = create_products()

    validate_products(products)

    products_output = RAW_DATA_FOLDER / "products.csv"

    products.to_csv(
        products_output,
        index=False,
        encoding="utf-8-sig",
    )

    print("Product data generation completed successfully.")
    print(f"Products: {len(products)}")
    print(f"Output file: {products_output}")

    print("\nProducts by category:")
    print(products["category"].value_counts().to_string())

    print("\nProduct statuses:")
    print(products["status"].value_counts().to_string())


if __name__ == "__main__":
    main()