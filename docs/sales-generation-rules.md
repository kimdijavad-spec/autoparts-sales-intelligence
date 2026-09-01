# Sales Data Generation Rules

## Purpose

This document defines the business assumptions used to generate
synthetic B2B automotive parts sales data.

The rules are documented to make the dataset reproducible,
explainable, and suitable for analytical validation.

## Observation Period

- Start date: 2024-09-01
- End date: 2026-08-31
- Duration: 24 months
- Target number of orders: approximately 8,000
- Target number of order lines: approximately 25,000

## Sales Order Grain

One row in `sales_order_lines.csv` represents one product line
inside one customer order.

One order can contain multiple products. Therefore, `order_id` can
appear in multiple rows, while `order_line_id` must remain unique.

## Customer Eligibility

- A customer cannot place an order before its registration date.
- The order must fall inside the observation period.
- The order uses the sales representative assigned to the customer.
- Current customer status influences purchase frequency.

## Customer Status Effect

The current customer status affects simulated order frequency:

- Active: normal purchase frequency
- On Hold: reduced purchase frequency
- Inactive: strongly reduced purchase frequency

The status represents the customer's condition near the end of the
observation period. Therefore, inactive customers can still have
historical purchases.

## Purchase Frequency by Customer Type

Expected relative purchase frequency:

- Regional Wholesaler: highest
- Auto Parts Retailer: high
- Fleet Service Company: medium
- Repair Shop: lower

The final dataset should include realistic variation between
customers of the same type.

## Order Size

Each order contains between 1 and 5 product lines.

Expected order-line distribution:

- 1 line: 12%
- 2 lines: 22%
- 3 lines: 30%
- 4 lines: 22%
- 5 lines: 14%

## Quantity by Customer Type

Expected quantity ranges per order line:

- Auto Parts Retailer: 2 to 20 units
- Repair Shop: 1 to 8 units
- Regional Wholesaler: 10 to 80 units
- Fleet Service Company: 3 to 25 units

## Product Selection

Product selection depends partly on customer type:

- Repair shops purchase more filters, engine, brake, and electrical parts.
- Retailers purchase from all major categories.
- Regional wholesalers purchase higher quantities across all categories.
- Fleet companies purchase more filters, brakes, suspension, and cooling parts.

Duplicate products are not allowed inside the same order.

## Pricing

- All monetary values are represented in Iranian rials.
- `unit_price` starts from the product list price.
- Discounts vary by customer type.
- Regional wholesalers usually receive larger discounts.
- Campaign orders can receive the campaign's offered discount.
- The raw sales file does not store calculated revenue or profit.

## Derived Sales Measures

The following fields will be calculated later during data processing:

- gross_sales = quantity × unit_price
- discount_amount = gross_sales × discount_percent
- net_sales = gross_sales - discount_amount
- total_cost = quantity × product unit cost
- gross_profit = net_sales - total_cost
- profit_margin_percent = gross_profit ÷ net_sales

## Campaign Attribution

- Every converted campaign target receives at least one related order.
- A campaign order occurs between the campaign start and end dates.
- When a campaign targets a product category, the attributed order
  contains at least one product from that category.
- Campaign orders contain the relevant `campaign_id`.
- Organic orders have an empty `campaign_id`.
- Customers not selected for a campaign can still purchase organically
  during the campaign period.

Campaign-attributed revenue is not automatically treated as causal
incremental revenue. Targeted and non-targeted customers will later
be compared.

## Payment Methods

Possible payment methods:

- Cash
- Bank Transfer
- Credit 30 Days
- Credit 60 Days

Customer type affects the probability of each payment method.

## Returns

- Most order lines have no returns.
- A small percentage of lines contain returned units.
- Returned quantity cannot exceed sold quantity.

## Seasonality

The dataset includes business seasonality:

- Increased sales near Nowruz
- Increased cooling-system demand during summer
- Increased maintenance demand during autumn
- Monthly sales contain natural random variation

## Reproducibility

Random generation uses a fixed seed so that the same source code
produces the same dataset on every run.

## Data Quality Strategy

The first generated dataset is a clean reference dataset.

In a later ETL stage, controlled data-quality problems will be added,
including:

- Missing values
- Duplicate rows
- Inconsistent text values
- Invalid numeric values
- Incorrect date formats

The cleaning pipeline will detect, report, and correct these issues.
