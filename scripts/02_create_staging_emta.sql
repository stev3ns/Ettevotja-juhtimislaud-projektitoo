CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE IF NOT EXISTS staging.emta_tax_debt_raw (
    batch_id TEXT NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT now(),
    source_system TEXT NOT NULL DEFAULT 'emta',
    source_dataset TEXT NOT NULL,
    source_file TEXT NOT NULL,
    row_num INTEGER NOT NULL,
    raw_payload JSONB NOT NULL,
    PRIMARY KEY (batch_id, row_num)
);

CREATE TABLE IF NOT EXISTS staging.emta_paid_taxes_raw (
    batch_id TEXT NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT now(),
    source_system TEXT NOT NULL DEFAULT 'emta',
    source_dataset TEXT NOT NULL,
    source_file TEXT NOT NULL,
    row_num INTEGER NOT NULL,
    raw_payload JSONB NOT NULL,
    PRIMARY KEY (batch_id, row_num)
);