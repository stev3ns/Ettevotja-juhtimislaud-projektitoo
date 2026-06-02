DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM staging.merit_purchase_invoices_raw
        WHERE pih_id IS NULL
    ) THEN
        RAISE EXCEPTION 'FAIL: staging.merit_purchase_invoices_raw sisaldab NULL pih_id väärtusi';
    ELSE
        RAISE NOTICE 'PASS: kõik pih_id väärtused on olemas';
    END IF;
END $$;
