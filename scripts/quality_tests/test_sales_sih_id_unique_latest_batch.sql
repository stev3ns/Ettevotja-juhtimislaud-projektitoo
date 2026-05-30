DO $$
BEGIN
    IF EXISTS (
        WITH latest_batch AS (
            SELECT batch_id
            FROM staging.merit_sales_invoices_raw
            ORDER BY loaded_at DESC
            LIMIT 1
        )
        SELECT sih_id
        FROM staging.merit_sales_invoices_raw
        WHERE batch_id = (SELECT batch_id FROM latest_batch)
        GROUP BY sih_id
        HAVING COUNT(*) > 1
    ) THEN
        RAISE EXCEPTION 'FAIL: latest batch sisaldab duplikaatseid sih_id väärtusi';
    ELSE
        RAISE NOTICE 'PASS: latest batchi sih_id väärtused on unikaalsed';
    END IF;
END $$;
