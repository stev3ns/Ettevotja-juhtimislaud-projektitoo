DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM staging.merit_sales_invoices_raw
        WHERE sih_id IS NULL
    ) THEN
        RAISE EXCEPTION 'FAIL: staging.merit_sales_invoices_raw sisaldab NULL sih_id väärtusi';
    ELSE
        RAISE NOTICE 'PASS: kõik sih_id väärtused on olemas';
    END IF;
END $$;
