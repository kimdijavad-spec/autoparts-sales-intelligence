USE [autoparts_sales_intelligence];
GO

SET NOCOUNT ON;
SET XACT_ABORT ON;
GO


/* ============================================================
   EXPAND PRODUCT STATUS COLUMN
   ============================================================ */

IF OBJECT_ID(N'[inventory].[products]', N'U') IS NULL
BEGIN
    THROW 50001, 'Required table inventory.products does not exist.', 1;
END;
GO

IF COL_LENGTH(N'inventory.products', N'status') < 60
BEGIN
    ALTER TABLE [inventory].[products]
        ALTER COLUMN [status] NVARCHAR(30) NOT NULL;
END;
GO
