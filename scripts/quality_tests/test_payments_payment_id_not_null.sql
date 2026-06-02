DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM staging.merit_payments_raw
        WHERE payment_id IS NULL
    ) THEN
        RAISE EXCEPTION 'FAIL: staging.merit_payments_raw sisaldab NULL payment_id väärtusi';
    ELSE
        RAISE NOTICE 'PASS: kõik payment_id väärtused on olemas';
    END IF;
END $$;
