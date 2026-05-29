CREATE SCHEMA IF NOT EXISTS mart;

CREATE OR REPLACE FUNCTION mart.parse_numeric(value_text TEXT)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    cleaned TEXT;
BEGIN
    IF value_text IS NULL OR btrim(value_text) = '' THEN
        RETURN NULL;
    END IF;

    cleaned := replace(value_text, E'\u00A0', ' ');
    cleaned := replace(cleaned, ' ', '');
    cleaned := replace(cleaned, ',', '.');
    cleaned := regexp_replace(cleaned, '[^0-9.+-]', '', 'g');

    IF cleaned = '' OR cleaned = '-' OR cleaned = '+' OR cleaned = '.' THEN
        RETURN NULL;
    END IF;

    RETURN cleaned::NUMERIC;
EXCEPTION
    WHEN others THEN
        RETURN NULL;
END;
$$;

CREATE OR REPLACE FUNCTION mart.parse_date(value_text TEXT)
RETURNS DATE
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
    IF value_text IS NULL OR btrim(value_text) = '' THEN
        RETURN NULL;
    END IF;

    IF value_text ~ '^\d{4}-\d{2}-\d{2}$' THEN
        RETURN to_date(value_text, 'YYYY-MM-DD');
    ELSIF value_text ~ '^\d{2}\.\d{2}\.\d{4}$' THEN
        RETURN to_date(value_text, 'DD.MM.YYYY');
    ELSIF value_text ~ '^\d{8}$' THEN
        RETURN to_date(value_text, 'YYYYMMDD');
    ELSIF value_text ~ '^\d{2}/\d{2}/\d{4}$' THEN
        RETURN to_date(value_text, 'DD/MM/YYYY');
    ELSE
        RETURN NULL;
    END IF;
EXCEPTION
    WHEN others THEN
        RETURN NULL;
END;
$$;

CREATE TABLE IF NOT EXISTS mart.etl_runs (
    run_id BIGSERIAL PRIMARY KEY,
    pipeline_name TEXT NOT NULL,
    executed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    status TEXT NOT NULL DEFAULT 'ok'
);