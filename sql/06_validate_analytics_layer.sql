USE [autoparts_sales_intelligence];
GO

SET NOCOUNT ON;

DECLARE @checks TABLE
(
    check_id       INT IDENTITY(1, 1) PRIMARY KEY,
    check_name     NVARCHAR(160) NOT NULL,
    expected_value DECIMAL(38, 2) NOT NULL,
    actual_value   DECIMAL(38, 2) NOT NULL,
    check_status   VARCHAR(4) NOT NULL
);

DECLARE @source_order_line_count BIGINT =
    (SELECT COUNT_BIG(*) FROM [sales].[sales_order_lines]);
DECLARE @detail_row_count BIGINT =
    (SELECT COUNT_BIG(*) FROM [analytics].[vw_sales_detail]);

INSERT INTO @checks (check_name, expected_value, actual_value, check_status)
VALUES
(
    N'Sales detail row count matches source order lines',
    @source_order_line_count,
    @detail_row_count,
    CASE WHEN @source_order_line_count = @detail_row_count THEN 'PASS' ELSE 'FAIL' END
);

DECLARE @source_order_count BIGINT =
    (SELECT COUNT_BIG(*) FROM [sales].[sales_orders]);
DECLARE @summary_order_count BIGINT =
    (SELECT COUNT_BIG(*) FROM [analytics].[vw_order_summary]);

INSERT INTO @checks (check_name, expected_value, actual_value, check_status)
VALUES
(
    N'Order summary row count matches source orders',
    @source_order_count,
    @summary_order_count,
    CASE WHEN @source_order_count = @summary_order_count THEN 'PASS' ELSE 'FAIL' END
);

DECLARE @source_customer_count BIGINT =
    (SELECT COUNT_BIG(*) FROM [sales].[customers]);
DECLARE @customer_view_count BIGINT =
    (SELECT COUNT_BIG(*) FROM [analytics].[vw_customer_performance]);

INSERT INTO @checks (check_name, expected_value, actual_value, check_status)
VALUES
(
    N'Customer performance includes every customer',
    @source_customer_count,
    @customer_view_count,
    CASE WHEN @source_customer_count = @customer_view_count THEN 'PASS' ELSE 'FAIL' END
);

DECLARE @source_product_count BIGINT =
    (SELECT COUNT_BIG(*) FROM [inventory].[products]);
DECLARE @product_view_count BIGINT =
    (SELECT COUNT_BIG(*) FROM [analytics].[vw_product_performance]);

INSERT INTO @checks (check_name, expected_value, actual_value, check_status)
VALUES
(
    N'Product performance includes every product',
    @source_product_count,
    @product_view_count,
    CASE WHEN @source_product_count = @product_view_count THEN 'PASS' ELSE 'FAIL' END
);

DECLARE @source_sales_rep_count BIGINT =
    (SELECT COUNT_BIG(*) FROM [sales].[sales_representatives]);
DECLARE @sales_rep_view_count BIGINT =
    (SELECT COUNT_BIG(*) FROM [analytics].[vw_sales_rep_performance]);

INSERT INTO @checks (check_name, expected_value, actual_value, check_status)
VALUES
(
    N'Sales representative performance includes every representative',
    @source_sales_rep_count,
    @sales_rep_view_count,
    CASE WHEN @source_sales_rep_count = @sales_rep_view_count THEN 'PASS' ELSE 'FAIL' END
);

DECLARE @source_campaign_count BIGINT =
    (SELECT COUNT_BIG(*) FROM [marketing].[campaigns]);
DECLARE @campaign_view_count BIGINT =
    (SELECT COUNT_BIG(*) FROM [analytics].[vw_campaign_performance]);

INSERT INTO @checks (check_name, expected_value, actual_value, check_status)
VALUES
(
    N'Campaign performance includes every campaign',
    @source_campaign_count,
    @campaign_view_count,
    CASE WHEN @source_campaign_count = @campaign_view_count THEN 'PASS' ELSE 'FAIL' END
);

DECLARE @source_payment_status_count BIGINT =
    (SELECT COUNT_BIG(DISTINCT payment_status) FROM [finance].[payments]);
DECLARE @payment_status_view_count BIGINT =
    (SELECT COUNT_BIG(*) FROM [analytics].[vw_payment_status_summary]);

INSERT INTO @checks (check_name, expected_value, actual_value, check_status)
VALUES
(
    N'Payment summary includes every payment status',
    @source_payment_status_count,
    @payment_status_view_count,
    CASE WHEN @source_payment_status_count = @payment_status_view_count THEN 'PASS' ELSE 'FAIL' END
);

DECLARE @source_month_count BIGINT =
    (
        SELECT COUNT_BIG(DISTINCT DATEFROMPARTS(YEAR(order_date), MONTH(order_date), 1))
        FROM [sales].[sales_orders]
    );
DECLARE @monthly_view_count BIGINT =
    (SELECT COUNT_BIG(*) FROM [analytics].[vw_monthly_sales]);

INSERT INTO @checks (check_name, expected_value, actual_value, check_status)
VALUES
(
    N'Monthly sales includes every order month',
    @source_month_count,
    @monthly_view_count,
    CASE WHEN @source_month_count = @monthly_view_count THEN 'PASS' ELSE 'FAIL' END
);

DECLARE @formula_mismatch_count BIGINT =
(
    SELECT COUNT_BIG(*)
    FROM [analytics].[vw_sales_detail]
    WHERE ABS(
        gross_sales_amount - discount_amount - return_amount - net_sales_amount
    ) > 0.01
);

INSERT INTO @checks (check_name, expected_value, actual_value, check_status)
VALUES
(
    N'Line-level sales arithmetic has no mismatch',
    0,
    @formula_mismatch_count,
    CASE WHEN @formula_mismatch_count = 0 THEN 'PASS' ELSE 'FAIL' END
);

DECLARE @invoice_mismatch_count BIGINT =
(
    SELECT COUNT_BIG(*)
    FROM [analytics].[vw_order_summary]
    WHERE ABS(invoice_variance_amount) > 0.01
);

INSERT INTO @checks (check_name, expected_value, actual_value, check_status)
VALUES
(
    N'Order net sales matches invoice amount',
    0,
    @invoice_mismatch_count,
    CASE WHEN @invoice_mismatch_count = 0 THEN 'PASS' ELSE 'FAIL' END
);

DECLARE @dimension_null_count BIGINT =
(
    SELECT COUNT_BIG(*)
    FROM [analytics].[vw_sales_detail]
    WHERE customer_id IS NULL
       OR sales_rep_id IS NULL
       OR product_id IS NULL
);

INSERT INTO @checks (check_name, expected_value, actual_value, check_status)
VALUES
(
    N'Sales detail has no missing required dimension key',
    0,
    @dimension_null_count,
    CASE WHEN @dimension_null_count = 0 THEN 'PASS' ELSE 'FAIL' END
);

DECLARE @order_total DECIMAL(38, 2) =
    (SELECT SUM(net_sales_amount) FROM [analytics].[vw_order_summary]);
DECLARE @monthly_total DECIMAL(38, 2) =
    (SELECT SUM(net_sales_amount) FROM [analytics].[vw_monthly_sales]);
DECLARE @customer_total DECIMAL(38, 2) =
    (SELECT SUM(net_sales_amount) FROM [analytics].[vw_customer_performance]);
DECLARE @product_total DECIMAL(38, 2) =
    (SELECT SUM(net_sales_amount) FROM [analytics].[vw_product_performance]);
DECLARE @sales_rep_total DECIMAL(38, 2) =
    (SELECT SUM(net_sales_amount) FROM [analytics].[vw_sales_rep_performance]);
DECLARE @payment_total DECIMAL(38, 2) =
    (SELECT SUM(invoice_amount) FROM [analytics].[vw_payment_status_summary]);

INSERT INTO @checks (check_name, expected_value, actual_value, check_status)
VALUES
    (
        N'Monthly total matches order total',
        @order_total,
        @monthly_total,
        CASE WHEN @order_total = @monthly_total THEN 'PASS' ELSE 'FAIL' END
    ),
    (
        N'Customer total matches order total',
        @order_total,
        @customer_total,
        CASE WHEN @order_total = @customer_total THEN 'PASS' ELSE 'FAIL' END
    ),
    (
        N'Product total matches order total',
        @order_total,
        @product_total,
        CASE WHEN @order_total = @product_total THEN 'PASS' ELSE 'FAIL' END
    ),
    (
        N'Sales representative total matches order total',
        @order_total,
        @sales_rep_total,
        CASE WHEN @order_total = @sales_rep_total THEN 'PASS' ELSE 'FAIL' END
    ),
    (
        N'Payment total matches order total',
        @order_total,
        @payment_total,
        CASE WHEN @order_total = @payment_total THEN 'PASS' ELSE 'FAIL' END
    );

DECLARE @source_attributed_order_count BIGINT =
(
    SELECT COUNT_BIG(*)
    FROM [sales].[sales_orders]
    WHERE campaign_id IS NOT NULL
);
DECLARE @campaign_view_order_count BIGINT =
(
    SELECT SUM(attributed_order_count)
    FROM [analytics].[vw_campaign_performance]
);

INSERT INTO @checks (check_name, expected_value, actual_value, check_status)
VALUES
(
    N'Campaign attributed order count matches source orders',
    @source_attributed_order_count,
    @campaign_view_order_count,
    CASE
        WHEN @source_attributed_order_count = @campaign_view_order_count
            THEN 'PASS'
        ELSE 'FAIL'
    END
);

SELECT
    check_id,
    check_name,
    expected_value,
    actual_value,
    check_status
FROM @checks
ORDER BY check_id;

IF EXISTS (SELECT 1 FROM @checks WHERE check_status = 'FAIL')
BEGIN
    THROW 51000, 'ANALYTICS VALIDATION FAILED. Review failed checks.', 1;
END;

PRINT 'ANALYTICS VALIDATION PASSED: all checks succeeded.';
GO
