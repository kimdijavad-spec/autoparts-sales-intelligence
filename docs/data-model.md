# Data Model

## Overview

The project simulates the operations of a fictional B2B automotive
parts wholesale distributor.

The initial dataset contains seven related business entities:

1. Customers
2. Products
3. Sales representatives
4. Sales order lines
5. Marketing campaigns
6. Campaign targets
7. Customer payments

## 1. Customers

File: `customers.csv`

One row represents one business customer.

Examples of customer types:

- Auto parts retailer
- Repair shop
- Regional wholesaler
- Fleet service company

Planned fields:

- customer_id
- customer_name
- customer_type
- province
- city
- registration_date
- credit_limit
- sales_rep_id
- status

## 2. Products

File: `products.csv`

One row represents one automotive part.

Planned fields:

- product_id
- sku
- product_name
- category
- brand
- compatible_vehicle
- unit_cost
- list_price
- reorder_point
- status

## 3. Sales Representatives

File: `sales_representatives.csv`

One row represents one sales representative.

Planned fields:

- sales_rep_id
- sales_rep_name
- region
- hire_date
- monthly_target
- status

## 4. Sales Order Lines

File: `sales_order_lines.csv`

One row represents one product line inside a customer order.

An order can contain multiple products and therefore multiple rows.

Planned fields:

- order_id
- order_line_id
- order_date
- customer_id
- product_id
- sales_rep_id
- quantity
- unit_price
- discount_percent
- campaign_id
- payment_method
- returned_quantity

Calculated during data processing:

- gross_sales
- discount_amount
- net_sales
- total_cost
- gross_profit
- profit_margin_percent

## 5. Marketing Campaigns

File: `campaigns.csv`

One row represents one marketing campaign.

Planned fields:

- campaign_id
- campaign_name
- channel
- start_date
- end_date
- budget
- target_customer_type
- target_product_category
- offered_discount

## 6. Campaign Targets

File: `campaign_targets.csv`

One row represents one customer targeted by one campaign.

Planned fields:

- campaign_id
- customer_id
- contact_date
- message_delivered
- customer_engaged
- sales_followup
- converted

Campaign revenue will be calculated from related sales orders instead
of being manually stored in this file.

## 7. Customer Payments

File: `payments.csv`

One row represents one payment obligation associated with one order.

Planned fields:

- payment_id
- order_id
- customer_id
- invoice_amount
- invoice_date
- due_date
- paid_date
- payment_status

## Table Relationships

- One customer can have many sales orders.
- One product can appear in many order lines.
- One sales representative can manage many customers and orders.
- One campaign can target many customers.
- One customer can be targeted by many campaigns.
- One order can optionally be associated with one campaign.
- One order can have one payment record.

## Currency

All monetary values in the synthetic dataset are represented in
Iranian rials (IRR).

## Data Period

The initial dataset will simulate 24 months of business operations.

## Initial Data Volume

- 500 customers
- 300 products
- 12 sales representatives
- Approximately 8,000 orders
- Approximately 25,000 order lines
- 12 marketing campaigns
- Campaign targeting and response records
- Payment records for all orders
