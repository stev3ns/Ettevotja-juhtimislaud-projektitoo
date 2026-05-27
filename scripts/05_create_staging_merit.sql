CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE IF NOT EXISTS staging.merit_purchase_invoices_raw (
    batch_id TEXT NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT now(),
    source_system TEXT NOT NULL DEFAULT 'merit',
    endpoint TEXT NOT NULL,
    pih_id TEXT NOT NULL,
    changed_date TIMESTAMP NULL,
    raw_payload JSONB NOT NULL,
    PRIMARY KEY (batch_id, pih_id)
);