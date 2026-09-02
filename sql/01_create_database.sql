USE [master];
GO

IF DB_ID('autoparts_sales_intelligence') IS NULL
BEGIN
    CREATE DATABASE [autoparts_sales_intelligence];
END;
GO