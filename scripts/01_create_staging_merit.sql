CREATE SCHEMA IF NOT EXISTS staging;

DROP TABLE IF EXISTS staging.merit_purchase_invoices_raw;
DROP TABLE IF EXISTS staging.merit_sales_invoices_raw;
DROP TABLE IF EXISTS staging.merit_payments_raw;

CREATE TABLE IF NOT EXISTS staging.merit_purchase_invoices_raw (
    batch_id TEXT NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT now(),
    source_system TEXT NOT NULL DEFAULT 'merit',
    endpoint TEXT NOT NULL,
    pih_id TEXT NOT NULL,
    changed_date TIMESTAMP NULL,
    raw_payload JSONB NOT NULL,
    PRIMARY KEY (pih_id)
);
CREATE TABLE IF NOT EXISTS staging.merit_sales_invoices_raw (
    batch_id TEXT NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT now(),
    source_system TEXT NOT NULL DEFAULT 'merit',
    endpoint TEXT NOT NULL,
    sih_id TEXT NOT NULL,
    changed_date TIMESTAMP NULL,
    raw_payload JSONB NOT NULL,
    PRIMARY KEY (sih_id)
);

CREATE TABLE IF NOT EXISTS staging.merit_payments_raw (
    batch_id TEXT NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT now(),
    source_system TEXT NOT NULL DEFAULT 'merit',
    endpoint TEXT NOT NULL,
    payment_id TEXT NOT NULL,
    changed_date TIMESTAMP NULL,
    raw_payload JSONB NOT NULL,
    PRIMARY KEY (payment_id)
);
