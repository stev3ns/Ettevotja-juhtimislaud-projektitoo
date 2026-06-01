CREATE SCHEMA IF NOT EXISTS mart;

-- Counterparty activity from Merit sales and purchase invoices.
-- Purpose:
-- - identify customers/vendors that actually have business activity
-- - calculate document counts and related amounts
-- - prepare data for EMTA tax debt risk checks

CREATE OR REPLACE VIEW mart.counterparty_activity AS
WITH customer_activity AS (
    SELECT
        'customer' AS counterparty_role,
        customer_id AS counterparty_id,
        customer_name AS counterparty_name,
        COUNT(*) AS document_count,
        SUM(COALESCE(amount_with_tax_eur, 0)) AS amount_eur
    FROM mart.merit_sales_invoices
    GROUP BY customer_id, customer_name
),
vendor_activity AS (
    SELECT
        'vendor' AS counterparty_role,
        vendor_id AS counterparty_id,
        vendor_name AS counterparty_name,
        COUNT(*) AS document_count,
        SUM(COALESCE(amount_with_tax_eur, 0)) AS amount_eur
    FROM mart.merit_purchase_invoices
    GROUP BY vendor_id, vendor_name
)
SELECT * FROM customer_activity
UNION ALL
SELECT * FROM vendor_activity;


-- Merit counterparties that have a usable registry code.
-- Only these can be checked against EMTA tax debt data.

CREATE OR REPLACE VIEW mart.counterparties_with_reg_code AS
SELECT
    'customer' AS counterparty_role,
    c.customer_id AS counterparty_id,
    c.customer_name AS counterparty_name,
    c.reg_no AS reg_code,
    regexp_replace(COALESCE(c.reg_no, ''), '\D', '', 'g') AS reg_code_norm,
    COALESCE(a.document_count, 0) AS document_count,
    COALESCE(a.amount_eur, 0) AS amount_eur
FROM mart.merit_customers c
LEFT JOIN mart.counterparty_activity a
    ON a.counterparty_role = 'customer'
   AND a.counterparty_id = c.customer_id
WHERE NULLIF(TRIM(COALESCE(c.reg_no, '')), '') IS NOT NULL

UNION ALL

SELECT
    'vendor' AS counterparty_role,
    v.vendor_id AS counterparty_id,
    v.vendor_name AS counterparty_name,
    v.reg_no AS reg_code,
    regexp_replace(COALESCE(v.reg_no, ''), '\D', '', 'g') AS reg_code_norm,
    COALESCE(a.document_count, 0) AS document_count,
    COALESCE(a.amount_eur, 0) AS amount_eur
FROM mart.merit_vendors v
LEFT JOIN mart.counterparty_activity a
    ON a.counterparty_role = 'vendor'
   AND a.counterparty_id = v.vendor_id
WHERE NULLIF(TRIM(COALESCE(v.reg_no, '')), '') IS NOT NULL;


-- EMTA tax debt matched only to Merit customers/vendors by registry code.
-- This avoids showing the whole EMTA dataset in the business dashboard.

CREATE OR REPLACE VIEW mart.emta_counterparty_tax_risk AS
WITH emta_tax_debt_latest AS (
    SELECT DISTINCT ON (regexp_replace(COALESCE(reg_code, ''), '\D', '', 'g'))
        regexp_replace(COALESCE(reg_code, ''), '\D', '', 'g') AS reg_code_norm,
        reg_code,
        company_name,
        COALESCE(tax_debt_eur, 0) AS tax_debt_eur,
        debt_as_of_date
    FROM mart.emta_tax_debt
    WHERE NULLIF(TRIM(COALESCE(reg_code, '')), '') IS NOT NULL
    ORDER BY
        regexp_replace(COALESCE(reg_code, ''), '\D', '', 'g'),
        debt_as_of_date DESC NULLS LAST,
        COALESCE(tax_debt_eur, 0) DESC
)
SELECT
    cp.counterparty_role,
    cp.counterparty_id,
    cp.counterparty_name,
    cp.reg_code,
    cp.document_count,
    cp.amount_eur AS related_amount_eur,
    COALESCE(td.tax_debt_eur, 0) AS tax_debt_eur,
    td.debt_as_of_date,
    CASE
        WHEN COALESCE(td.tax_debt_eur, 0) > 0 THEN 'risk'
        ELSE 'ok'
    END AS risk_status
FROM mart.counterparties_with_reg_code cp
LEFT JOIN emta_tax_debt_latest td
    ON td.reg_code_norm = cp.reg_code_norm;


-- Active Merit customers/vendors that cannot be checked against EMTA
-- because registry code is missing.

CREATE OR REPLACE VIEW mart.counterparties_missing_reg_code AS
SELECT
    'customer' AS counterparty_role,
    c.customer_id AS counterparty_id,
    c.customer_name AS counterparty_name,
    c.reg_no AS reg_code,
    COALESCE(a.document_count, 0) AS document_count,
    COALESCE(a.amount_eur, 0) AS related_amount_eur,
    'missing_reg_code' AS warning_type,
    'EMTA kontrolli ei saa teha, sest Meriti partneri kaardil puudub registrikood.' AS warning_message
FROM mart.merit_customers c
JOIN mart.counterparty_activity a
    ON a.counterparty_role = 'customer'
   AND a.counterparty_id = c.customer_id
WHERE NULLIF(TRIM(COALESCE(c.reg_no, '')), '') IS NULL
  AND COALESCE(a.document_count, 0) > 0

UNION ALL

SELECT
    'vendor' AS counterparty_role,
    v.vendor_id AS counterparty_id,
    v.vendor_name AS counterparty_name,
    v.reg_no AS reg_code,
    COALESCE(a.document_count, 0) AS document_count,
    COALESCE(a.amount_eur, 0) AS related_amount_eur,
    'missing_reg_code' AS warning_type,
    'EMTA kontrolli ei saa teha, sest Meriti partneri kaardil puudub registrikood.' AS warning_message
FROM mart.merit_vendors v
JOIN mart.counterparty_activity a
    ON a.counterparty_role = 'vendor'
   AND a.counterparty_id = v.vendor_id
WHERE NULLIF(TRIM(COALESCE(v.reg_no, '')), '') IS NULL
  AND COALESCE(a.document_count, 0) > 0;