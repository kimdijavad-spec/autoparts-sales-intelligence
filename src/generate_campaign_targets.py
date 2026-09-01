from datetime import date, timedelta
from pathlib import Path
import random

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_SEED = 45

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_FOLDER = PROJECT_ROOT / "data" / "raw"

CUSTOMERS_FILE = RAW_DATA_FOLDER / "customers.csv"
CAMPAIGNS_FILE = RAW_DATA_FOLDER / "campaigns.csv"
OUTPUT_FILE = RAW_DATA_FOLDER / "campaign_targets.csv"

random.seed(RANDOM_SEED)


# ============================================================
# CHANNEL PERFORMANCE ASSUMPTIONS
# ============================================================

CHANNEL_CONFIG = {
    "Email": {
        "target_rate": 0.60,
        "delivery_rate": 0.93,
        "engagement_rate": 0.28,
        "followup_rate": 0.35,
        "conversion_rate": 0.12,
    },
    "SMS": {
        "target_rate": 0.65,
        "delivery_rate": 0.97,
        "engagement_rate": 0.18,
        "followup_rate": 0.25,
        "conversion_rate": 0.09,
    },
    "WhatsApp": {
        "target_rate": 0.55,
        "delivery_rate": 0.95,
        "engagement_rate": 0.42,
        "followup_rate": 0.50,
        "conversion_rate": 0.17,
    },
    "Sales Call": {
        "target_rate": 0.45,
        "delivery_rate": 0.88,
        "engagement_rate": 0.65,
        "followup_rate": 0.85,
        "conversion_rate": 0.24,
    },
    "Multi-channel": {
        "target_rate": 0.70,
        "delivery_rate": 0.98,
        "engagement_rate": 0.55,
        "followup_rate": 0.65,
        "conversion_rate": 0.22,
    },
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def random_date_between(
    start_date: date,
    end_date: date,
) -> date:
    """Return a random date inside a campaign period."""

    number_of_days = (end_date - start_date).days
    random_days = random.randint(0, number_of_days)

    return start_date + timedelta(days=random_days)


def choose_campaign_audience(
    customers: pd.DataFrame,
    campaign: pd.Series,
    target_rate: float,
) -> pd.DataFrame:
    """Select eligible customers for a campaign."""

    eligible_customers = customers[
        customers["registration_date"]
        <= campaign["start_date"]
    ].copy()

    target_customer_type = campaign["target_customer_type"]

    if target_customer_type != "All Customer Types":
        eligible_customers = eligible_customers[
            eligible_customers["customer_type"]
            == target_customer_type
        ]

    target_count = round(
        len(eligible_customers) * target_rate
    )

    target_count = max(1, target_count)

    selected_customer_ids = random.sample(
        eligible_customers["customer_id"].tolist(),
        target_count,
    )

    return eligible_customers[
        eligible_customers["customer_id"].isin(
            selected_customer_ids
        )
    ]


# ============================================================
# CAMPAIGN TARGET GENERATION
# ============================================================

def create_campaign_targets(
    customers: pd.DataFrame,
    campaigns: pd.DataFrame,
) -> pd.DataFrame:
    """Create targeting and response records for all campaigns."""

    records = []

    for _, campaign in campaigns.iterrows():
        channel = campaign["channel"]
        channel_config = CHANNEL_CONFIG[channel]

        selected_customers = choose_campaign_audience(
            customers=customers,
            campaign=campaign,
            target_rate=channel_config["target_rate"],
        )

        campaign_start = campaign["start_date"].date()
        campaign_end = campaign["end_date"].date()

        for customer_id in selected_customers["customer_id"]:
            message_delivered = (
                random.random()
                < channel_config["delivery_rate"]
            )

            customer_engaged = (
                message_delivered
                and random.random()
                < channel_config["engagement_rate"]
            )

            sales_followup = (
                customer_engaged
                and random.random()
                < channel_config["followup_rate"]
            )

            converted = (
                customer_engaged
                and random.random()
                < channel_config["conversion_rate"]
            )

            records.append(
                {
                    "campaign_id": campaign["campaign_id"],
                    "customer_id": customer_id,
                    "contact_date": random_date_between(
                        campaign_start,
                        campaign_end,
                    ),
                    "message_delivered": message_delivered,
                    "customer_engaged": customer_engaged,
                    "sales_followup": sales_followup,
                    "converted": converted,
                }
            )

    return pd.DataFrame(records)


# ============================================================
# VALIDATION
# ============================================================

def validate_campaign_targets(
    campaign_targets: pd.DataFrame,
    customers: pd.DataFrame,
    campaigns: pd.DataFrame,
) -> None:
    """Validate campaign audience and funnel logic."""

    assert not campaign_targets.empty
    assert not campaign_targets.isna().any().any()

    assert not campaign_targets.duplicated(
        subset=["campaign_id", "customer_id"]
    ).any()

    valid_customer_ids = set(customers["customer_id"])
    valid_campaign_ids = set(campaigns["campaign_id"])

    assert set(
        campaign_targets["customer_id"]
    ).issubset(valid_customer_ids)

    assert set(
        campaign_targets["campaign_id"]
    ).issubset(valid_campaign_ids)

    assert not (
        campaign_targets["customer_engaged"]
        & ~campaign_targets["message_delivered"]
    ).any()

    assert not (
        campaign_targets["sales_followup"]
        & ~campaign_targets["customer_engaged"]
    ).any()

    assert not (
        campaign_targets["converted"]
        & ~campaign_targets["customer_engaged"]
    ).any()

    validation_data = campaign_targets.merge(
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

    validation_data["contact_date"] = pd.to_datetime(
        validation_data["contact_date"]
    )

    assert (
        validation_data["contact_date"]
        >= validation_data["start_date"]
    ).all()

    assert (
        validation_data["contact_date"]
        <= validation_data["end_date"]
    ).all()


# ============================================================
# REPORTING
# ============================================================

def create_campaign_summary(
    campaign_targets: pd.DataFrame,
) -> pd.DataFrame:
    """Create a simple funnel summary for every campaign."""

    summary = campaign_targets.groupby(
        "campaign_id",
        as_index=False,
    ).agg(
        targeted_customers=("customer_id", "count"),
        delivered=("message_delivered", "sum"),
        engaged=("customer_engaged", "sum"),
        followed_up=("sales_followup", "sum"),
        converted=("converted", "sum"),
    )

    summary["conversion_rate_percent"] = (
        summary["converted"]
        / summary["targeted_customers"]
        * 100
    ).round(2)

    return summary


# ============================================================
# MAIN PROGRAM
# ============================================================

def main() -> None:
    """Generate, validate, and save campaign targets."""

    customers = pd.read_csv(
        CUSTOMERS_FILE,
        parse_dates=["registration_date"],
    )

    campaigns = pd.read_csv(
        CAMPAIGNS_FILE,
        parse_dates=["start_date", "end_date"],
    )

    campaign_targets = create_campaign_targets(
        customers,
        campaigns,
    )

    validate_campaign_targets(
        campaign_targets,
        customers,
        campaigns,
    )

    campaign_targets.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    campaign_summary = create_campaign_summary(
        campaign_targets
    )

    print("Campaign target generation completed successfully.")
    print(f"Target records: {len(campaign_targets)}")
    print(
        "Unique targeted customers: "
        f"{campaign_targets['customer_id'].nunique()}"
    )

    print("\nCampaign funnel summary:")
    print(campaign_summary.to_string(index=False))

    print(f"\nOutput file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()