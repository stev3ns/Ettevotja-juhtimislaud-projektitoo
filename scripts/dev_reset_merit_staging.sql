-- DEVELOPMENT ONLY!
-- This script deletes Merit staging tables.
-- Do not use this in regular or production loads.

DROP TABLE IF EXISTS staging.merit_payments_raw;
DROP TABLE IF EXISTS staging.merit_sales_invoices_raw;
DROP TABLE IF EXISTS staging.merit_purchase_invoices_raw;
DROP TABLE IF EXISTS staging.merit_vendors_raw;
DROP TABLE IF EXISTS staging.merit_customers_raw;