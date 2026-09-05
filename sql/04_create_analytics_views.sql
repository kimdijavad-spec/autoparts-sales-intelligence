-- Updated version: includes sales detail and order summary analytical views.
USE [autoparts_sales_intelligence];
GO

IF SCHEMA_ID('analytics') IS NULL
BEGIN
    EXEC('CREATE SCHEMA [analytics]');
END;
GO

CREATE OR ALTER VIEW [analytics].[vw_sales_detail]
AS
SELECT
    sol.order_line_id,
    so.order_id,
    so.order_date,
    DATEFROMPARTS(YEAR(so.order_date), MONTH(so.order_date), 1) AS order_month,

    so.customer_id,
    c.customer_name,
    c.customer_type,
    c.province,
    c.city,

    so.sales_rep_id,
    sr.sales_rep_name,
    sr.region AS sales_region,

    so.campaign_id,
    mc.campaign_name,
    mc.channel AS campaign_channel,

    sol.product_id,
    p.sku,
    p.product_name,
    p.category AS product_category,
    p.brand AS product_brand,

    so.payment_method,
    sol.quantity,
    sol.returned_quantity,
    sol.quantity - sol.returned_quantity AS net_quantity,
    sol.unit_price,
    sol.discount_percent,

    CAST(sol.quantity * sol.unit_price AS DECIMAL(28, 2))
        AS gross_sales_amount,

    CAST(
        sol.quantity * sol.unit_price * sol.discount_percent / 100.0
        AS DECIMAL(28, 2)
    ) AS discount_amount,

    CAST(
        sol.quantity * sol.unit_price * (1 - sol.discount_percent / 100.0)
        AS DECIMAL(28, 2)
    ) AS sales_amount_before_returns,

    CAST(
        sol.returned_quantity * sol.unit_price * (1 - sol.discount_percent / 100.0)
        AS DECIMAL(28, 2)
    ) AS return_amount,

    CAST(
        (sol.quantity - sol.returned_quantity)
        * sol.unit_price
        * (1 - sol.discount_percent / 100.0)
        AS DECIMAL(28, 2)
    ) AS net_sales_amount
FROM [sales].[sales_order_lines] AS sol
INNER JOIN [sales].[sales_orders] AS so
    ON so.order_id = sol.order_id
INNER JOIN [sales].[customers] AS c
    ON c.customer_id = so.customer_id
INNER JOIN [sales].[sales_representatives] AS sr
    ON sr.sales_rep_id = so.sales_rep_id
INNER JOIN [inventory].[products] AS p
    ON p.product_id = sol.product_id
LEFT JOIN [marketing].[campaigns] AS mc
    ON mc.campaign_id = so.campaign_id;
GO

CREATE OR ALTER VIEW [analytics].[vw_order_summary]
AS
WITH order_totals AS
(
    SELECT
        order_id,
        COUNT_BIG(*) AS order_line_count,
        SUM(CAST(quantity AS BIGINT)) AS ordered_units,
        SUM(CAST(returned_quantity AS BIGINT)) AS returned_units,
        SUM(CAST(net_quantity AS BIGINT)) AS net_units,
        SUM(gross_sales_amount) AS gross_sales_amount,
        SUM(discount_amount) AS discount_amount,
        SUM(return_amount) AS return_amount,
        SUM(net_sales_amount) AS net_sales_amount
    FROM [analytics].[vw_sales_detail]
    GROUP BY order_id
)
SELECT
    so.order_id,
    so.order_date,
    DATEFROMPARTS(YEAR(so.order_date), MONTH(so.order_date), 1) AS order_month,

    so.customer_id,
    c.customer_name,
    c.customer_type,
    c.province,
    c.city,

    so.sales_rep_id,
    sr.sales_rep_name,
    sr.region AS sales_region,

    so.campaign_id,
    mc.campaign_name,
    mc.channel AS campaign_channel,
    CASE
        WHEN so.campaign_id IS NULL THEN N'Organic'
        ELSE N'Campaign'
    END AS sales_source,

    so.payment_method,
    pay.invoice_amount,
    pay.invoice_date,
    pay.due_date,
    pay.paid_date,
    pay.payment_status,
    CASE
        WHEN pay.paid_date IS NULL THEN NULL
        ELSE DATEDIFF(DAY, pay.invoice_date, pay.paid_date)
    END AS days_to_payment,

    totals.order_line_count,
    totals.ordered_units,
    totals.returned_units,
    totals.net_units,
    totals.gross_sales_amount,
    totals.discount_amount,
    totals.return_amount,
    totals.net_sales_amount,
    CAST(
        CAST(pay.invoice_amount AS DECIMAL(38, 2)) - totals.net_sales_amount
        AS DECIMAL(38, 2)
    ) AS invoice_variance_amount,
    CAST(
        CASE WHEN totals.returned_units > 0 THEN 1 ELSE 0 END
        AS BIT
    ) AS has_return
FROM [sales].[sales_orders] AS so
INNER JOIN order_totals AS totals
    ON totals.order_id = so.order_id
INNER JOIN [sales].[customers] AS c
    ON c.customer_id = so.customer_id
INNER JOIN [sales].[sales_representatives] AS sr
    ON sr.sales_rep_id = so.sales_rep_id
LEFT JOIN [marketing].[campaigns] AS mc
    ON mc.campaign_id = so.campaign_id
INNER JOIN [finance].[payments] AS pay
    ON pay.order_id = so.order_id
    AND pay.customer_id = so.customer_id;
GO
