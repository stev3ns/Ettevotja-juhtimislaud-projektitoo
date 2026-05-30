DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM staging.merit_payments_raw
    ) THEN
        RAISE EXCEPTION 'FAIL: staging.merit_payments_raw on tühi';
    ELSIF (
        SELECT MAX(loaded_at)
        FROM staging.merit_payments_raw
    ) < NOW() - INTERVAL '24 hours' THEN
        RAISE EXCEPTION 'FAIL: payments andmed ei ole viimase 24 tunni jooksul värskendatud';
    ELSE
        RAISE NOTICE 'PASS: payments andmed on värsked (loaded_at viimase 24h jooksul)';
    END IF;
END $$;
