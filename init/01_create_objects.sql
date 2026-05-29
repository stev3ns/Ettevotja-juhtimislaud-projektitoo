CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE IF NOT EXISTS staging.emta_tax_debt_raw (
  batch_id        text        NOT NULL,
  source_system   text        NOT NULL,
  source_dataset  text        NOT NULL,
  source_file     text        NOT NULL,
  row_num         integer     NOT NULL,
  raw_payload     jsonb       NOT NULL
);

CREATE TABLE IF NOT EXISTS staging.emta_paid_taxes_raw (
  batch_id        text        NOT NULL,
  source_system   text        NOT NULL,
  source_dataset  text        NOT NULL,
  source_file     text        NOT NULL,
  row_num         integer     NOT NULL,
  raw_payload     jsonb       NOT NULL
);

CREATE INDEX IF NOT EXISTS emta_tax_debt_raw_batch_id_idx
  ON staging.emta_tax_debt_raw (batch_id);

CREATE INDEX IF NOT EXISTS emta_paid_taxes_raw_batch_id_idx
  ON staging.emta_paid_taxes_raw (batch_id);