DO $$
BEGIN
    IF EXISTS (
        WITH latest_batch AS (
            SELECT batch_id
            FROM staging.merit_payments_raw
            ORDER BY loaded_at DESC
            LIMIT 1
        )
        SELECT payment_id
        FROM staging.merit_payments_raw
        WHERE batch_id = (SELECT batch_id FROM latest_batch)
        GROUP BY payment_id
        HAVING COUNT(*) > 1
    ) THEN
        RAISE EXCEPTION 'FAIL: latest batch sisaldab duplikaatseid payment_id väärtusi';
    ELSE
        RAISE NOTICE 'PASS: latest batchi payment_id väärtused on unikaalsed';
    END IF;
END $$;
