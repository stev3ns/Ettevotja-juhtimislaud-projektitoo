DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM mart.merit_sales_invoices
        WHERE invoice_id IS NULL
    ) THEN
        RAISE EXCEPTION 'FAIL: mart.merit_sales_invoices sisaldab NULL invoice_id väärtusi';
    ELSIF EXISTS (
        SELECT invoice_id
        FROM mart.merit_sales_invoices
        GROUP BY invoice_id
        HAVING COUNT(*) > 1
    ) THEN
        RAISE EXCEPTION 'FAIL: mart.merit_sales_invoices sisaldab duplikaatseid invoice_id väärtusi';
    ELSE
        RAISE NOTICE 'PASS: mart.merit_sales_invoices võtmeväljad korras';
    END IF;
END $$;
