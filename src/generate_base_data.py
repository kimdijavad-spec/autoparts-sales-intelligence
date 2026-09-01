from datetime import date, timedelta
from pathlib import Path
import random

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_SEED = 42
NUMBER_OF_CUSTOMERS = 500
NUMBER_OF_SALES_REPS = 12

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_FOLDER = PROJECT_ROOT / "data" / "raw"

random.seed(RANDOM_SEED)


# ============================================================
# BUSINESS DATA
# ============================================================

PROVINCES_AND_CITIES = {
    "Tehran": ["Tehran", "Shahriar", "Eslamshahr"],
    "Isfahan": ["Isfahan", "Kashan", "Najafabad"],
    "Razavi Khorasan": ["Mashhad", "Neyshabur", "Sabzevar"],
    "Fars": ["Shiraz", "Marvdasht", "Jahrom"],
    "East Azerbaijan": ["Tabriz", "Maragheh", "Marand"],
    "Alborz": ["Karaj", "Fardis", "Nazarabad"],
    "Khuzestan": ["Ahvaz", "Abadan", "Dezful"],
    "Qom": ["Qom"],
    "Mazandaran": ["Sari", "Babol", "Amol"],
    "Kerman": ["Kerman", "Sirjan", "Rafsanjan"],
}

SALES_REP_NAMES = [
    "Arman Ahmadi",
    "Nima Karimi",
    "Sara Mohammadi",
    "Reza Hosseini",
    "Mina Rahimi",
    "Ali Moradi",
    "Parsa Ebrahimi",
    "Neda Jafari",
    "Amir Ghasemi",
    "Shiva Kazemi",
    "Saman Rezaei",
    "Maryam Heidari",
]

CUSTOMER_TYPES = [
    "Auto Parts Retailer",
    "Repair Shop",
    "Regional Wholesaler",
    "Fleet Service Company",
]

CUSTOMER_TYPE_WEIGHTS = [0.45, 0.30, 0.15, 0.10]

CREDIT_LIMIT_RANGES = {
    "Auto Parts Retailer": (500_000_000, 5_000_000_000),
    "Repair Shop": (300_000_000, 3_000_000_000),
    "Regional Wholesaler": (5_000_000_000, 20_000_000_000),
    "Fleet Service Company": (2_000_000_000, 10_000_000_000),
}

CUSTOMER_NAME_PREFIXES = [
    "Arman",
    "Pars",
    "Kavian",
    "Arian",
    "Atlas",
    "Sepahan",
    "Shayan",
    "Alborz",
    "Paytakht",
    "Pishro",
    "Shahin",
    "Negin",
]

CUSTOMER_NAME_SUFFIXES = {
    "Auto Parts Retailer": ["Auto Parts", "Parts Center", "Yadak"],
    "Repair Shop": ["Auto Service", "Service Center", "Garage"],
    "Regional Wholesaler": ["Parts Distribution", "Wholesale Parts"],
    "Fleet Service Company": ["Fleet Services", "Transport Services"],
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def generate_random_date(start_date: date, end_date: date) -> date:
    """Return a random date between start_date and end_date."""

    number_of_days = (end_date - start_date).days
    random_days = random.randint(0, number_of_days)

    return start_date + timedelta(days=random_days)


def generate_credit_limit(customer_type: str) -> int:
    """Generate a realistic credit limit based on customer type."""

    minimum, maximum = CREDIT_LIMIT_RANGES[customer_type]

    raw_credit_limit = random.randint(minimum, maximum)

    # Round the value to the nearest 100 million IRR.
    rounded_credit_limit = round(raw_credit_limit / 100_000_000) * 100_000_000

    return rounded_credit_limit


def generate_customer_name(customer_type: str, customer_number: int) -> str:
    """Generate a unique synthetic business name."""

    prefix = random.choice(CUSTOMER_NAME_PREFIXES)
    suffix = random.choice(CUSTOMER_NAME_SUFFIXES[customer_type])

    return f"{prefix} {suffix} {customer_number:04d}"


# ============================================================
# SALES REPRESENTATIVES
# ============================================================

def create_sales_representatives() -> pd.DataFrame:
    """Create the sales representatives dataset."""

    provinces = list(PROVINCES_AND_CITIES.keys())

    # Tehran and Isfahan receive two representatives.
    assigned_regions = provinces + ["Tehran", "Isfahan"]

    records = []

    for index in range(NUMBER_OF_SALES_REPS):
        monthly_target = random.randrange(
            20_000_000_000,
            80_000_000_001,
            1_000_000_000,
        )

        records.append(
            {
                "sales_rep_id": f"SR{index + 1:03d}",
                "sales_rep_name": SALES_REP_NAMES[index],
                "region": assigned_regions[index],
                "hire_date": generate_random_date(
                    date(2018, 1, 1),
                    date(2025, 12, 31),
                ),
                "monthly_target": monthly_target,
                "status": random.choices(
                    ["Active", "Inactive"],
                    weights=[0.95, 0.05],
                    k=1,
                )[0],
            }
        )

    return pd.DataFrame(records)


# ============================================================
# CUSTOMERS
# ============================================================

def create_customers(
    sales_representatives: pd.DataFrame,
) -> pd.DataFrame:
    """Create the business customers dataset."""

    records = []

    for index in range(1, NUMBER_OF_CUSTOMERS + 1):
        province = random.choice(list(PROVINCES_AND_CITIES.keys()))
        city = random.choice(PROVINCES_AND_CITIES[province])

        customer_type = random.choices(
            CUSTOMER_TYPES,
            weights=CUSTOMER_TYPE_WEIGHTS,
            k=1,
        )[0]

        regional_representatives = sales_representatives[
            sales_representatives["region"] == province
        ]

        assigned_sales_rep = random.choice(
            regional_representatives["sales_rep_id"].tolist()
        )

        customer_status = random.choices(
            ["Active", "On Hold", "Inactive"],
            weights=[0.90, 0.04, 0.06],
            k=1,
        )[0]

        records.append(
            {
                "customer_id": f"CUS{index:04d}",
                "customer_name": generate_customer_name(
                    customer_type,
                    index,
                ),
                "customer_type": customer_type,
                "province": province,
                "city": city,
                "registration_date": generate_random_date(
                    date(2018, 1, 1),
                    date(2026, 7, 31),
                ),
                "credit_limit": generate_credit_limit(customer_type),
                "sales_rep_id": assigned_sales_rep,
                "status": customer_status,
            }
        )

    return pd.DataFrame(records)


# ============================================================
# VALIDATION
# ============================================================

def validate_data(
    sales_representatives: pd.DataFrame,
    customers: pd.DataFrame,
) -> None:
    """Run basic data-quality checks before saving files."""

    assert len(sales_representatives) == NUMBER_OF_SALES_REPS
    assert sales_representatives["sales_rep_id"].is_unique

    assert len(customers) == NUMBER_OF_CUSTOMERS
    assert customers["customer_id"].is_unique
    assert customers["customer_name"].is_unique

    valid_sales_rep_ids = set(sales_representatives["sales_rep_id"])
    customer_sales_rep_ids = set(customers["sales_rep_id"])

    assert customer_sales_rep_ids.issubset(valid_sales_rep_ids)


# ============================================================
# MAIN PROGRAM
# ============================================================

def main() -> None:
    """Generate, validate, and save the base datasets."""

    RAW_DATA_FOLDER.mkdir(parents=True, exist_ok=True)

    sales_representatives = create_sales_representatives()
    customers = create_customers(sales_representatives)

    validate_data(sales_representatives, customers)

    sales_representatives_output = (
        RAW_DATA_FOLDER / "sales_representatives.csv"
    )
    customers_output = RAW_DATA_FOLDER / "customers.csv"

    sales_representatives.to_csv(
        sales_representatives_output,
        index=False,
        encoding="utf-8-sig",
    )

    customers.to_csv(
        customers_output,
        index=False,
        encoding="utf-8-sig",
    )

    print("Base data generation completed successfully.")
    print(f"Sales representatives: {len(sales_representatives)}")
    print(f"Customers: {len(customers)}")
    print(f"Output folder: {RAW_DATA_FOLDER}")


if __name__ == "__main__":
    main()