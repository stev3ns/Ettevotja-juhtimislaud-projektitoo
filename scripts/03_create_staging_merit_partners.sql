CREATE SCHEMA IF NOT EXISTS staging;

DROP TABLE IF EXISTS staging.merit_customers_raw;
DROP TABLE IF EXISTS staging.merit_vendors_raw;

CREATE TABLE IF NOT EXISTS staging.merit_customers_raw (
    batch_id TEXT NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT now(),
    source_system TEXT NOT NULL DEFAULT 'merit',
    endpoint TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    reg_no TEXT,
    changed_date TIMESTAMP NULL,
    raw_payload JSONB NOT NULL,
    PRIMARY KEY (customer_id)
);

CREATE TABLE IF NOT EXISTS staging.merit_vendors_raw (
    batch_id TEXT NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT now(),
    source_system TEXT NOT NULL DEFAULT 'merit',
    endpoint TEXT NOT NULL,
    vendor_id TEXT NOT NULL,
    reg_no TEXT,
    changed_date TIMESTAMP NULL,
    raw_payload JSONB NOT NULL,
    PRIMARY KEY (vendor_id)
);