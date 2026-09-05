USE [autoparts_sales_intelligence];
GO

CREATE OR ALTER VIEW [analytics].[vw_monthly_sales]
AS
SELECT
    d.order_month,
    YEAR(d.order_month) AS order_year,
    MONTH(d.order_month) AS order_month_number,
    COUNT(DISTINCT d.order_id) AS order_count,
    COUNT(DISTINCT d.customer_id) AS unique_customer_count,
    COUNT(DISTINCT CASE WHEN d.campaign_id IS NOT NULL THEN d.order_id END)
        AS campaign_order_count,
    COUNT(DISTINCT CASE WHEN d.campaign_id IS NULL THEN d.order_id END)
        AS organic_order_count,
    COUNT(DISTINCT CASE WHEN d.returned_quantity > 0 THEN d.order_id END)
        AS return_order_count,
    SUM(CAST(d.quantity AS BIGINT)) AS ordered_units,
    SUM(CAST(d.returned_quantity AS BIGINT)) AS returned_units,
    SUM(CAST(d.net_quantity AS BIGINT)) AS net_units,
    SUM(d.gross_sales_amount) AS gross_sales_amount,
    SUM(d.discount_amount) AS discount_amount,
    SUM(d.return_amount) AS return_amount,
    SUM(d.net_sales_amount) AS net_sales_amount,
    CAST(
        SUM(CAST(d.net_quantity * p.unit_cost AS DECIMAL(28, 2)))
        AS DECIMAL(38, 2)
    ) AS net_cost_amount,
    CAST(
        SUM(d.net_sales_amount)
        - SUM(CAST(d.net_quantity * p.unit_cost AS DECIMAL(28, 2)))
        AS DECIMAL(38, 2)
    ) AS gross_profit_amount,
    CAST(
        SUM(d.net_sales_amount) / NULLIF(COUNT(DISTINCT d.order_id), 0)
        AS DECIMAL(28, 2)
    ) AS average_order_value,
    CAST(
        100.0 * SUM(d.discount_amount)
        / NULLIF(SUM(d.gross_sales_amount), 0)
        AS DECIMAL(9, 2)
    ) AS discount_rate_percent,
    CAST(
        100.0 * SUM(d.return_amount)
        / NULLIF(SUM(d.net_sales_amount) + SUM(d.return_amount), 0)
        AS DECIMAL(9, 2)
    ) AS return_rate_percent,
    CAST(
        100.0 *
        (
            SUM(d.net_sales_amount)
            - SUM(CAST(d.net_quantity * p.unit_cost AS DECIMAL(28, 2)))
        )
        / NULLIF(SUM(d.net_sales_amount), 0)
        AS DECIMAL(9, 2)
    ) AS gross_margin_percent
FROM [analytics].[vw_sales_detail] AS d
INNER JOIN [inventory].[products] AS p
    ON p.product_id = d.product_id
GROUP BY d.order_month;
GO

CREATE OR ALTER VIEW [analytics].[vw_customer_performance]
AS
WITH customer_sales AS
(
    SELECT
        d.customer_id,
        COUNT(DISTINCT d.order_id) AS order_count,
        MIN(d.order_date) AS first_order_date,
        MAX(d.order_date) AS last_order_date,
        SUM(CAST(d.quantity AS BIGINT)) AS ordered_units,
        SUM(CAST(d.returned_quantity AS BIGINT)) AS returned_units,
        SUM(d.gross_sales_amount) AS gross_sales_amount,
        SUM(d.discount_amount) AS discount_amount,
        SUM(d.return_amount) AS return_amount,
        SUM(d.net_sales_amount) AS net_sales_amount,
        SUM(CAST(d.net_quantity * p.unit_cost AS DECIMAL(28, 2)))
            AS net_cost_amount
    FROM [analytics].[vw_sales_detail] AS d
    INNER JOIN [inventory].[products] AS p
        ON p.product_id = d.product_id
    GROUP BY d.customer_id
),
customer_receivables AS
(
    SELECT
        customer_id,
        SUM(
            CASE WHEN payment_status = N'Overdue'
                THEN invoice_amount ELSE 0 END
        ) AS overdue_amount,
        SUM(
            CASE WHEN payment_status = N'Outstanding'
                THEN invoice_amount ELSE 0 END
        ) AS outstanding_amount,
        SUM(
            CASE WHEN payment_status = N'Overdue'
                THEN CAST(1 AS BIGINT) ELSE 0 END
        ) AS overdue_order_count
    FROM [analytics].[vw_order_summary]
    GROUP BY customer_id
)
SELECT
    c.customer_id,
    c.customer_name,
    c.customer_type,
    c.province,
    c.city,
    c.registration_date,
    c.credit_limit,
    c.sales_rep_id,
    sr.sales_rep_name,
    c.status,
    COALESCE(cs.order_count, 0) AS order_count,
    cs.first_order_date,
    cs.last_order_date,
    COALESCE(cs.ordered_units, 0) AS ordered_units,
    COALESCE(cs.returned_units, 0) AS returned_units,
    COALESCE(cs.gross_sales_amount, 0) AS gross_sales_amount,
    COALESCE(cs.discount_amount, 0) AS discount_amount,
    COALESCE(cs.return_amount, 0) AS return_amount,
    COALESCE(cs.net_sales_amount, 0) AS net_sales_amount,
    COALESCE(cs.net_cost_amount, 0) AS net_cost_amount,
    COALESCE(cs.net_sales_amount - cs.net_cost_amount, 0)
        AS gross_profit_amount,
    CAST(
        COALESCE(cs.net_sales_amount, 0)
        / NULLIF(cs.order_count, 0)
        AS DECIMAL(28, 2)
    ) AS average_order_value,
    COALESCE(cr.overdue_amount, 0) AS overdue_amount,
    COALESCE(cr.outstanding_amount, 0) AS outstanding_amount,
    COALESCE(cr.overdue_order_count, 0) AS overdue_order_count,
    CAST(
        100.0 * (COALESCE(cr.overdue_amount, 0) + COALESCE(cr.outstanding_amount, 0))
        / NULLIF(c.credit_limit, 0)
        AS DECIMAL(12, 2)
    ) AS open_receivables_to_credit_limit_percent
FROM [sales].[customers] AS c
INNER JOIN [sales].[sales_representatives] AS sr
    ON sr.sales_rep_id = c.sales_rep_id
LEFT JOIN customer_sales AS cs
    ON cs.customer_id = c.customer_id
LEFT JOIN customer_receivables AS cr
    ON cr.customer_id = c.customer_id;
GO

CREATE OR ALTER VIEW [analytics].[vw_product_performance]
AS
SELECT
    p.product_id,
    p.sku,
    p.product_name,
    p.category,
    p.brand,
    p.compatible_vehicle,
    p.unit_cost,
    p.list_price,
    p.reorder_point,
    p.status,
    COUNT_BIG(d.order_line_id) AS order_line_count,
    COUNT(DISTINCT d.order_id) AS order_count,
    COUNT(DISTINCT d.customer_id) AS unique_customer_count,
    COALESCE(SUM(CAST(d.quantity AS BIGINT)), 0) AS ordered_units,
    COALESCE(SUM(CAST(d.returned_quantity AS BIGINT)), 0) AS returned_units,
    COALESCE(SUM(CAST(d.net_quantity AS BIGINT)), 0) AS net_units,
    COALESCE(SUM(d.gross_sales_amount), 0) AS gross_sales_amount,
    COALESCE(SUM(d.discount_amount), 0) AS discount_amount,
    COALESCE(SUM(d.return_amount), 0) AS return_amount,
    COALESCE(SUM(d.net_sales_amount), 0) AS net_sales_amount,
    COALESCE(
        SUM(CAST(d.net_quantity * p.unit_cost AS DECIMAL(28, 2))),
        0
    ) AS net_cost_amount,
    COALESCE(
        SUM(d.net_sales_amount)
        - SUM(CAST(d.net_quantity * p.unit_cost AS DECIMAL(28, 2))),
        0
    ) AS gross_profit_amount,
    CAST(
        100.0 *
        (
            SUM(d.net_sales_amount)
            - SUM(CAST(d.net_quantity * p.unit_cost AS DECIMAL(28, 2)))
        )
        / NULLIF(SUM(d.net_sales_amount), 0)
        AS DECIMAL(9, 2)
    ) AS gross_margin_percent,
    CAST(
        100.0 * SUM(CAST(d.returned_quantity AS DECIMAL(28, 2)))
        / NULLIF(SUM(CAST(d.quantity AS DECIMAL(28, 2))), 0)
        AS DECIMAL(9, 2)
    ) AS unit_return_rate_percent
FROM [inventory].[products] AS p
LEFT JOIN [analytics].[vw_sales_detail] AS d
    ON d.product_id = p.product_id
GROUP BY
    p.product_id,
    p.sku,
    p.product_name,
    p.category,
    p.brand,
    p.compatible_vehicle,
    p.unit_cost,
    p.list_price,
    p.reorder_point,
    p.status;
GO

CREATE OR ALTER VIEW [analytics].[vw_sales_rep_performance]
AS
SELECT
    sr.sales_rep_id,
    sr.sales_rep_name,
    sr.region,
    sr.hire_date,
    sr.monthly_target,
    sr.status,
    COUNT(DISTINCT d.order_month) AS active_month_count,
    COUNT(DISTINCT d.order_id) AS order_count,
    COUNT(DISTINCT d.customer_id) AS unique_customer_count,
    COALESCE(SUM(CAST(d.quantity AS BIGINT)), 0) AS ordered_units,
    COALESCE(SUM(CAST(d.returned_quantity AS BIGINT)), 0) AS returned_units,
    COALESCE(SUM(d.net_sales_amount), 0) AS net_sales_amount,
    COALESCE(SUM(d.return_amount), 0) AS return_amount,
    COALESCE(
        SUM(d.net_sales_amount)
        - SUM(CAST(d.net_quantity * p.unit_cost AS DECIMAL(28, 2))),
        0
    ) AS gross_profit_amount,
    CAST(
        COALESCE(SUM(d.net_sales_amount), 0)
        / NULLIF(COUNT(DISTINCT d.order_month), 0)
        AS DECIMAL(28, 2)
    ) AS average_monthly_net_sales,
    CAST(
        100.0 *
        (
            COALESCE(SUM(d.net_sales_amount), 0)
            / NULLIF(COUNT(DISTINCT d.order_month), 0)
        )
        / NULLIF(sr.monthly_target, 0)
        AS DECIMAL(12, 2)
    ) AS average_target_attainment_percent
FROM [sales].[sales_representatives] AS sr
LEFT JOIN [analytics].[vw_sales_detail] AS d
    ON d.sales_rep_id = sr.sales_rep_id
LEFT JOIN [inventory].[products] AS p
    ON p.product_id = d.product_id
GROUP BY
    sr.sales_rep_id,
    sr.sales_rep_name,
    sr.region,
    sr.hire_date,
    sr.monthly_target,
    sr.status;
GO

CREATE OR ALTER VIEW [analytics].[vw_campaign_performance]
AS
WITH funnel AS
(
    SELECT
        campaign_id,
        COUNT_BIG(*) AS targeted_customers,
        SUM(CASE WHEN message_delivered = 1 THEN CAST(1 AS BIGINT) ELSE 0 END)
            AS delivered_customers,
        SUM(CASE WHEN customer_engaged = 1 THEN CAST(1 AS BIGINT) ELSE 0 END)
            AS engaged_customers,
        SUM(CASE WHEN sales_followup = 1 THEN CAST(1 AS BIGINT) ELSE 0 END)
            AS followed_up_customers,
        SUM(CASE WHEN converted = 1 THEN CAST(1 AS BIGINT) ELSE 0 END)
            AS converted_customers
    FROM [marketing].[campaign_targets]
    GROUP BY campaign_id
),
campaign_sales AS
(
    SELECT
        campaign_id,
        COUNT_BIG(*) AS attributed_order_count,
        COUNT(DISTINCT customer_id) AS purchasing_customer_count,
        SUM(net_sales_amount) AS attributed_net_sales_amount,
        SUM(CASE WHEN has_return = 1 THEN CAST(1 AS BIGINT) ELSE 0 END)
            AS returned_order_count
    FROM [analytics].[vw_order_summary]
    WHERE campaign_id IS NOT NULL
    GROUP BY campaign_id
)
SELECT
    c.campaign_id,
    c.campaign_name,
    c.channel,
    c.start_date,
    c.end_date,
    c.budget,
    c.target_customer_type,
    c.target_product_category,
    c.offered_discount,
    COALESCE(f.targeted_customers, 0) AS targeted_customers,
    COALESCE(f.delivered_customers, 0) AS delivered_customers,
    COALESCE(f.engaged_customers, 0) AS engaged_customers,
    COALESCE(f.followed_up_customers, 0) AS followed_up_customers,
    COALESCE(f.converted_customers, 0) AS converted_customers,
    COALESCE(cs.attributed_order_count, 0) AS attributed_order_count,
    COALESCE(cs.purchasing_customer_count, 0) AS purchasing_customer_count,
    COALESCE(cs.attributed_net_sales_amount, 0) AS attributed_net_sales_amount,
    COALESCE(cs.returned_order_count, 0) AS returned_order_count,
    CAST(
        100.0 * f.delivered_customers / NULLIF(f.targeted_customers, 0)
        AS DECIMAL(9, 2)
    ) AS delivery_rate_percent,
    CAST(
        100.0 * f.engaged_customers / NULLIF(f.delivered_customers, 0)
        AS DECIMAL(9, 2)
    ) AS engagement_rate_percent,
    CAST(
        100.0 * f.converted_customers / NULLIF(f.targeted_customers, 0)
        AS DECIMAL(9, 2)
    ) AS conversion_rate_percent,
    CAST(
        cs.attributed_net_sales_amount / NULLIF(c.budget, 0)
        AS DECIMAL(18, 2)
    ) AS return_on_ad_spend,
    CAST(
        c.budget / NULLIF(f.converted_customers, 0)
        AS DECIMAL(28, 2)
    ) AS cost_per_conversion
FROM [marketing].[campaigns] AS c
LEFT JOIN funnel AS f
    ON f.campaign_id = c.campaign_id
LEFT JOIN campaign_sales AS cs
    ON cs.campaign_id = c.campaign_id;
GO

CREATE OR ALTER VIEW [analytics].[vw_payment_status_summary]
AS
SELECT
    payment_status,
    COUNT_BIG(*) AS payment_count,
    COUNT(DISTINCT customer_id) AS customer_count,
    SUM(invoice_amount) AS invoice_amount,
    CAST(AVG(CAST(invoice_amount AS DECIMAL(28, 2))) AS DECIMAL(28, 2))
        AS average_invoice_amount,
    MIN(invoice_date) AS first_invoice_date,
    MAX(invoice_date) AS last_invoice_date,
    MIN(due_date) AS earliest_due_date,
    MAX(due_date) AS latest_due_date
FROM [finance].[payments]
GROUP BY payment_status;
GO
