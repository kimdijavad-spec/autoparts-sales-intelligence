from datetime import date
from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_FOLDER = PROJECT_ROOT / "data" / "raw"


# ============================================================
# CAMPAIGN DEFINITIONS
# ============================================================

CAMPAIGNS = [
    {
        "campaign_id": "CMP001",
        "campaign_name": "Autumn Brake Safety",
        "channel": "SMS",
        "start_date": date(2024, 9, 10),
        "end_date": date(2024, 9, 30),
        "budget": 1_500_000_000,
        "target_customer_type": "Auto Parts Retailer",
        "target_product_category": "Brake System",
        "offered_discount": 7,
    },
    {
        "campaign_id": "CMP002",
        "campaign_name": "Filter Restock Program",
        "channel": "Email",
        "start_date": date(2024, 11, 5),
        "end_date": date(2024, 11, 25),
        "budget": 1_200_000_000,
        "target_customer_type": "Repair Shop",
        "target_product_category": "Filters",
        "offered_discount": 6,
    },
    {
        "campaign_id": "CMP003",
        "campaign_name": "Winter Fleet Maintenance",
        "channel": "Sales Call",
        "start_date": date(2025, 1, 5),
        "end_date": date(2025, 1, 31),
        "budget": 2_500_000_000,
        "target_customer_type": "Fleet Service Company",
        "target_product_category": "Engine Parts",
        "offered_discount": 8,
    },
    {
        "campaign_id": "CMP004",
        "campaign_name": "Nowruz Retail Growth",
        "channel": "Multi-channel",
        "start_date": date(2025, 3, 1),
        "end_date": date(2025, 3, 25),
        "budget": 4_000_000_000,
        "target_customer_type": "Auto Parts Retailer",
        "target_product_category": "All Categories",
        "offered_discount": 10,
    },
    {
        "campaign_id": "CMP005",
        "campaign_name": "Workshop Engine Upgrade",
        "channel": "WhatsApp",
        "start_date": date(2025, 5, 10),
        "end_date": date(2025, 5, 31),
        "budget": 1_800_000_000,
        "target_customer_type": "Repair Shop",
        "target_product_category": "Engine Parts",
        "offered_discount": 7,
    },
    {
        "campaign_id": "CMP006",
        "campaign_name": "Summer Cooling Campaign",
        "channel": "SMS",
        "start_date": date(2025, 7, 1),
        "end_date": date(2025, 7, 25),
        "budget": 2_000_000_000,
        "target_customer_type": "All Customer Types",
        "target_product_category": "Cooling System",
        "offered_discount": 8,
    },
    {
        "campaign_id": "CMP007",
        "campaign_name": "Wholesale Transmission Deal",
        "channel": "Email",
        "start_date": date(2025, 9, 5),
        "end_date": date(2025, 9, 30),
        "budget": 2_200_000_000,
        "target_customer_type": "Regional Wholesaler",
        "target_product_category": "Transmission",
        "offered_discount": 12,
    },
    {
        "campaign_id": "CMP008",
        "campaign_name": "Brake Customer Retention",
        "channel": "WhatsApp",
        "start_date": date(2025, 11, 5),
        "end_date": date(2025, 11, 25),
        "budget": 1_700_000_000,
        "target_customer_type": "Auto Parts Retailer",
        "target_product_category": "Brake System",
        "offered_discount": 7,
    },
    {
        "campaign_id": "CMP009",
        "campaign_name": "Fleet Reliability Program",
        "channel": "Sales Call",
        "start_date": date(2026, 1, 5),
        "end_date": date(2026, 1, 31),
        "budget": 3_000_000_000,
        "target_customer_type": "Fleet Service Company",
        "target_product_category": "Suspension",
        "offered_discount": 9,
    },
    {
        "campaign_id": "CMP010",
        "campaign_name": "Nowruz Multi-Category Sale",
        "channel": "Multi-channel",
        "start_date": date(2026, 3, 1),
        "end_date": date(2026, 3, 25),
        "budget": 5_000_000_000,
        "target_customer_type": "All Customer Types",
        "target_product_category": "All Categories",
        "offered_discount": 10,
    },
    {
        "campaign_id": "CMP011",
        "campaign_name": "Electrical Parts Activation",
        "channel": "Email",
        "start_date": date(2026, 5, 5),
        "end_date": date(2026, 5, 28),
        "budget": 1_600_000_000,
        "target_customer_type": "Repair Shop",
        "target_product_category": "Electrical",
        "offered_discount": 6,
    },
    {
        "campaign_id": "CMP012",
        "campaign_name": "Summer Cooling Plus",
        "channel": "Multi-channel",
        "start_date": date(2026, 7, 1),
        "end_date": date(2026, 7, 31),
        "budget": 3_500_000_000,
        "target_customer_type": "All Customer Types",
        "target_product_category": "Cooling System",
        "offered_discount": 9,
    },
]


# ============================================================
# VALIDATION
# ============================================================

def validate_campaigns(campaigns: pd.DataFrame) -> None:
    """Validate campaign definitions before saving."""

    assert len(campaigns) == 12
    assert campaigns["campaign_id"].is_unique
    assert campaigns["campaign_name"].is_unique
    assert not campaigns.isna().any().any()

    assert (campaigns["budget"] > 0).all()

    assert campaigns["offered_discount"].between(
        0,
        100,
        inclusive="both",
    ).all()

    assert (
        campaigns["start_date"] <= campaigns["end_date"]
    ).all()


# ============================================================
# MAIN PROGRAM
# ============================================================

def main() -> None:
    """Create, validate, and save campaign data."""

    RAW_DATA_FOLDER.mkdir(parents=True, exist_ok=True)

    campaigns = pd.DataFrame(CAMPAIGNS)

    validate_campaigns(campaigns)

    output_file = RAW_DATA_FOLDER / "campaigns.csv"

    campaigns.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig",
    )

    print("Campaign data generation completed successfully.")
    print(f"Campaigns: {len(campaigns)}")
    print(f"Total budget: {campaigns['budget'].sum():,.0f} IRR")
    print(f"Output file: {output_file}")

    print("\nCampaigns by channel:")
    print(campaigns["channel"].value_counts().to_string())

    print("\nCampaign timeline:")
    print(
        campaigns[
            [
                "campaign_id",
                "campaign_name",
                "start_date",
                "end_date",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()