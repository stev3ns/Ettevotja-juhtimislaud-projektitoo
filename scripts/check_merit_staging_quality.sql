-- Merit staging / bronze quality checks

SELECT 'row_count_purchase_invoices' AS check_name, COUNT(*) AS result
FROM staging.merit_purchase_invoices_raw

UNION ALL
SELECT 'row_count_sales_invoices', COUNT(*)
FROM staging.merit_sales_invoices_raw

UNION ALL
SELECT 'row_count_payments', COUNT(*)
FROM staging.merit_payments_raw

UNION ALL
SELECT 'row_count_customers', COUNT(*)
FROM staging.merit_customers_raw

UNION ALL
SELECT 'row_count_vendors', COUNT(*)
FROM staging.merit_vendors_raw

UNION ALL
SELECT 'missing_purchase_pih_id', COUNT(*)
FROM staging.merit_purchase_invoices_raw
WHERE pih_id IS NULL OR pih_id = ''

UNION ALL
SELECT 'missing_sales_sih_id', COUNT(*)
FROM staging.merit_sales_invoices_raw
WHERE sih_id IS NULL OR sih_id = ''

UNION ALL
SELECT 'missing_payment_id', COUNT(*)
FROM staging.merit_payments_raw
WHERE payment_id IS NULL OR payment_id = ''

UNION ALL
SELECT 'missing_customer_id', COUNT(*)
FROM staging.merit_customers_raw
WHERE customer_id IS NULL OR customer_id = ''

UNION ALL
SELECT 'missing_vendor_id', COUNT(*)
FROM staging.merit_vendors_raw
WHERE vendor_id IS NULL OR vendor_id = ''

UNION ALL
SELECT 'duplicate_purchase_pih_id', COUNT(*)
FROM (
    SELECT pih_id
    FROM staging.merit_purchase_invoices_raw
    GROUP BY pih_id
    HAVING COUNT(*) > 1
) x

UNION ALL
SELECT 'duplicate_sales_sih_id', COUNT(*)
FROM (
    SELECT sih_id
    FROM staging.merit_sales_invoices_raw
    GROUP BY sih_id
    HAVING COUNT(*) > 1
) x

UNION ALL
SELECT 'duplicate_payment_id', COUNT(*)
FROM (
    SELECT payment_id
    FROM staging.merit_payments_raw
    GROUP BY payment_id
    HAVING COUNT(*) > 1
) x

UNION ALL
SELECT 'duplicate_customer_id', COUNT(*)
FROM (
    SELECT customer_id
    FROM staging.merit_customers_raw
    GROUP BY customer_id
    HAVING COUNT(*) > 1
) x

UNION ALL
SELECT 'duplicate_vendor_id', COUNT(*)
FROM (
    SELECT vendor_id
    FROM staging.merit_vendors_raw
    GROUP BY vendor_id
    HAVING COUNT(*) > 1
) x

UNION ALL
SELECT 'missing_purchase_raw_payload', COUNT(*)
FROM staging.merit_purchase_invoices_raw
WHERE raw_payload IS NULL

UNION ALL
SELECT 'missing_sales_raw_payload', COUNT(*)
FROM staging.merit_sales_invoices_raw
WHERE raw_payload IS NULL

UNION ALL
SELECT 'missing_payments_raw_payload', COUNT(*)
FROM staging.merit_payments_raw
WHERE raw_payload IS NULL

UNION ALL
SELECT 'missing_customers_raw_payload', COUNT(*)
FROM staging.merit_customers_raw
WHERE raw_payload IS NULL

UNION ALL
SELECT 'missing_vendors_raw_payload', COUNT(*)
FROM staging.merit_vendors_raw
WHERE raw_payload IS NULL;