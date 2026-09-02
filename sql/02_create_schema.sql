USE [autoparts_sales_intelligence];
GO

SET NOCOUNT ON;
SET XACT_ABORT ON;
GO


/* ============================================================
   CREATE DATABASE SCHEMAS
   ============================================================ */

IF SCHEMA_ID(N'sales') IS NULL
    EXEC(N'CREATE SCHEMA [sales]');
GO

IF SCHEMA_ID(N'inventory') IS NULL
    EXEC(N'CREATE SCHEMA [inventory]');
GO

IF SCHEMA_ID(N'marketing') IS NULL
    EXEC(N'CREATE SCHEMA [marketing]');
GO

IF SCHEMA_ID(N'finance') IS NULL
    EXEC(N'CREATE SCHEMA [finance]');
GO


/* ============================================================
   SALES REPRESENTATIVES
   ============================================================ */

IF OBJECT_ID(N'[sales].[sales_representatives]', N'U') IS NULL
BEGIN
    CREATE TABLE [sales].[sales_representatives]
    (
        sales_rep_id      VARCHAR(5)      NOT NULL,
        sales_rep_name    NVARCHAR(120)   NOT NULL,
        region            NVARCHAR(60)    NOT NULL,
        hire_date         DATE            NOT NULL,
        monthly_target    DECIMAL(18, 0)  NOT NULL,
        status            NVARCHAR(20)    NOT NULL,
        loaded_at_utc     DATETIME2(0)    NOT NULL
            CONSTRAINT DF_sales_representatives_loaded_at
            DEFAULT SYSUTCDATETIME(),

        CONSTRAINT PK_sales_representatives
            PRIMARY KEY (sales_rep_id),

        CONSTRAINT CK_sales_representatives_monthly_target
            CHECK (monthly_target >= 0)
    );
END;
GO


/* ============================================================
   CUSTOMERS
   ============================================================ */

IF OBJECT_ID(N'[sales].[customers]', N'U') IS NULL
BEGIN
    CREATE TABLE [sales].[customers]
    (
        customer_id       VARCHAR(7)      NOT NULL,
        customer_name     NVARCHAR(150)   NOT NULL,
        customer_type     NVARCHAR(60)    NOT NULL,
        province          NVARCHAR(60)    NOT NULL,
        city              NVARCHAR(80)    NOT NULL,
        registration_date DATE            NOT NULL,
        credit_limit      DECIMAL(18, 0)  NOT NULL,
        sales_rep_id      VARCHAR(5)      NOT NULL,
        status            NVARCHAR(20)    NOT NULL,
        loaded_at_utc     DATETIME2(0)    NOT NULL
            CONSTRAINT DF_customers_loaded_at
            DEFAULT SYSUTCDATETIME(),

        CONSTRAINT PK_customers
            PRIMARY KEY (customer_id),

        CONSTRAINT FK_customers_sales_representatives
            FOREIGN KEY (sales_rep_id)
            REFERENCES [sales].[sales_representatives](sales_rep_id),

        CONSTRAINT CK_customers_credit_limit
            CHECK (credit_limit >= 0)
    );
END;
GO


/* ============================================================
   PRODUCTS
   ============================================================ */

IF OBJECT_ID(N'[inventory].[products]', N'U') IS NULL
BEGIN
    CREATE TABLE [inventory].[products]
    (
        product_id         VARCHAR(7)      NOT NULL,
        sku                VARCHAR(30)     NOT NULL,
        product_name       NVARCHAR(200)   NOT NULL,
        category           NVARCHAR(60)    NOT NULL,
        brand              NVARCHAR(80)    NOT NULL,
        compatible_vehicle NVARCHAR(100)   NOT NULL,
        unit_cost          DECIMAL(18, 0)  NOT NULL,
        list_price         DECIMAL(18, 0)  NOT NULL,
        reorder_point      INT             NOT NULL,
        status             NVARCHAR(20)    NOT NULL,
        loaded_at_utc      DATETIME2(0)    NOT NULL
            CONSTRAINT DF_products_loaded_at
            DEFAULT SYSUTCDATETIME(),

        CONSTRAINT PK_products
            PRIMARY KEY (product_id),

        CONSTRAINT UQ_products_sku
            UNIQUE (sku),

        CONSTRAINT CK_products_unit_cost
            CHECK (unit_cost >= 0),

        CONSTRAINT CK_products_list_price
            CHECK (list_price >= 0),

        CONSTRAINT CK_products_reorder_point
            CHECK (reorder_point >= 0)
    );
END;
GO


/* ============================================================
   CAMPAIGNS
   ============================================================ */

IF OBJECT_ID(N'[marketing].[campaigns]', N'U') IS NULL
BEGIN
    CREATE TABLE [marketing].[campaigns]
    (
        campaign_id            VARCHAR(6)      NOT NULL,
        campaign_name          NVARCHAR(150)   NOT NULL,
        channel                NVARCHAR(30)    NOT NULL,
        start_date             DATE            NOT NULL,
        end_date               DATE            NOT NULL,
        budget                 DECIMAL(18, 0)  NOT NULL,
        target_customer_type   NVARCHAR(60)    NOT NULL,
        target_product_category NVARCHAR(60)   NOT NULL,
        offered_discount      DECIMAL(5, 2)   NOT NULL,
        loaded_at_utc         DATETIME2(0)    NOT NULL
            CONSTRAINT DF_campaigns_loaded_at
            DEFAULT SYSUTCDATETIME(),

        CONSTRAINT PK_campaigns
            PRIMARY KEY (campaign_id),

        CONSTRAINT CK_campaigns_date_range
            CHECK (end_date >= start_date),

        CONSTRAINT CK_campaigns_budget
            CHECK (budget >= 0),

        CONSTRAINT CK_campaigns_offered_discount
            CHECK (offered_discount BETWEEN 0 AND 100)
    );
END;
GO


/* ============================================================
   CAMPAIGN TARGETS
   ============================================================ */

IF OBJECT_ID(N'[marketing].[campaign_targets]', N'U') IS NULL
BEGIN
    CREATE TABLE [marketing].[campaign_targets]
    (
        campaign_id       VARCHAR(6)    NOT NULL,
        customer_id       VARCHAR(7)    NOT NULL,
        contact_date      DATE          NOT NULL,
        message_delivered BIT           NOT NULL,
        customer_engaged  BIT           NOT NULL,
        sales_followup    BIT           NOT NULL,
        converted         BIT           NOT NULL,
        loaded_at_utc     DATETIME2(0)  NOT NULL
            CONSTRAINT DF_campaign_targets_loaded_at
            DEFAULT SYSUTCDATETIME(),

        CONSTRAINT PK_campaign_targets
            PRIMARY KEY (campaign_id, customer_id),

        CONSTRAINT FK_campaign_targets_campaigns
            FOREIGN KEY (campaign_id)
            REFERENCES [marketing].[campaigns](campaign_id),

        CONSTRAINT FK_campaign_targets_customers
            FOREIGN KEY (customer_id)
            REFERENCES [sales].[customers](customer_id)
    );
END;
GO


/* ============================================================
   SALES ORDERS
   ============================================================ */

IF OBJECT_ID(N'[sales].[sales_orders]', N'U') IS NULL
BEGIN
    CREATE TABLE [sales].[sales_orders]
    (
        order_id          VARCHAR(9)     NOT NULL,
        order_date        DATE           NOT NULL,
        customer_id       VARCHAR(7)     NOT NULL,
        sales_rep_id      VARCHAR(5)     NOT NULL,
        campaign_id       VARCHAR(6)     NULL,
        payment_method    NVARCHAR(50)   NOT NULL,
        loaded_at_utc     DATETIME2(0)   NOT NULL
            CONSTRAINT DF_sales_orders_loaded_at
            DEFAULT SYSUTCDATETIME(),

        CONSTRAINT PK_sales_orders
            PRIMARY KEY (order_id),

        CONSTRAINT UQ_sales_orders_order_customer
            UNIQUE (order_id, customer_id),

        CONSTRAINT FK_sales_orders_customers
            FOREIGN KEY (customer_id)
            REFERENCES [sales].[customers](customer_id),

        CONSTRAINT FK_sales_orders_sales_representatives
            FOREIGN KEY (sales_rep_id)
            REFERENCES [sales].[sales_representatives](sales_rep_id),

        CONSTRAINT FK_sales_orders_campaigns
            FOREIGN KEY (campaign_id)
            REFERENCES [marketing].[campaigns](campaign_id)
    );
END;
GO


/* ============================================================
   SALES ORDER LINES
   ============================================================ */

IF OBJECT_ID(N'[sales].[sales_order_lines]', N'U') IS NULL
BEGIN
    CREATE TABLE [sales].[sales_order_lines]
    (
        order_line_id     VARCHAR(9)      NOT NULL,
        order_id          VARCHAR(9)      NOT NULL,
        product_id        VARCHAR(7)      NOT NULL,
        quantity          INT             NOT NULL,
        unit_price        DECIMAL(18, 0)  NOT NULL,
        discount_percent  DECIMAL(5, 2)   NOT NULL,
        returned_quantity INT             NOT NULL,
        loaded_at_utc     DATETIME2(0)    NOT NULL
            CONSTRAINT DF_sales_order_lines_loaded_at
            DEFAULT SYSUTCDATETIME(),

        CONSTRAINT PK_sales_order_lines
            PRIMARY KEY (order_line_id),

        CONSTRAINT FK_sales_order_lines_orders
            FOREIGN KEY (order_id)
            REFERENCES [sales].[sales_orders](order_id),

        CONSTRAINT FK_sales_order_lines_products
            FOREIGN KEY (product_id)
            REFERENCES [inventory].[products](product_id),

        CONSTRAINT CK_sales_order_lines_quantity
            CHECK (quantity > 0),

        CONSTRAINT CK_sales_order_lines_unit_price
            CHECK (unit_price >= 0),

        CONSTRAINT CK_sales_order_lines_discount
            CHECK (discount_percent BETWEEN 0 AND 100),

        CONSTRAINT CK_sales_order_lines_returned_quantity
            CHECK (
                returned_quantity >= 0
                AND returned_quantity <= quantity
            )
    );
END;
GO


/* ============================================================
   PAYMENTS
   ============================================================ */

IF OBJECT_ID(N'[finance].[payments]', N'U') IS NULL
BEGIN
    CREATE TABLE [finance].[payments]
    (
        payment_id        VARCHAR(9)      NOT NULL,
        order_id          VARCHAR(9)      NOT NULL,
        customer_id       VARCHAR(7)      NOT NULL,
        invoice_amount    DECIMAL(18, 0)  NOT NULL,
        invoice_date      DATE            NOT NULL,
        due_date          DATE            NOT NULL,
        paid_date         DATE            NULL,
        payment_status    NVARCHAR(30)    NOT NULL,
        loaded_at_utc     DATETIME2(0)    NOT NULL
            CONSTRAINT DF_payments_loaded_at
            DEFAULT SYSUTCDATETIME(),

        CONSTRAINT PK_payments
            PRIMARY KEY (payment_id),

        CONSTRAINT UQ_payments_order
            UNIQUE (order_id),

        CONSTRAINT FK_payments_order_customer
            FOREIGN KEY (order_id, customer_id)
            REFERENCES [sales].[sales_orders](order_id, customer_id),

        CONSTRAINT CK_payments_invoice_amount
            CHECK (invoice_amount >= 0),

        CONSTRAINT CK_payments_due_date
            CHECK (due_date >= invoice_date),

        CONSTRAINT CK_payments_paid_date
            CHECK (
                paid_date IS NULL
                OR paid_date >= invoice_date
            )
    );
END;
GO