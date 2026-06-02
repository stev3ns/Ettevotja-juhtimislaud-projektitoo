DO $$
BEGIN
    IF EXISTS (
        WITH latest_batch AS (
            SELECT batch_id
            FROM staging.merit_purchase_invoices_raw
            ORDER BY loaded_at DESC
            LIMIT 1
        )
        SELECT pih_id
        FROM staging.merit_purchase_invoices_raw
        WHERE batch_id = (SELECT batch_id FROM latest_batch)
        GROUP BY pih_id
        HAVING COUNT(*) > 1
    ) THEN
        RAISE EXCEPTION 'FAIL: latest batch sisaldab duplikaatseid pih_id väärtusi';
    ELSE
        RAISE NOTICE 'PASS: latest batchi pih_id väärtused on unikaalsed';
    END IF;
END $$;
