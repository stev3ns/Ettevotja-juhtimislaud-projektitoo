CREATE SCHEMA IF NOT EXISTS silver;

DROP TABLE IF EXISTS silver.customers;
CREATE TABLE silver.customers AS
SELECT
    customer_id,
    customer_name,
    CAST(payment_terms_days AS INTEGER) AS payment_terms_days,
    CAST(average_delay_days AS INTEGER) AS average_delay_days,
    CAST(monthly_fee AS NUMERIC) AS monthly_fee
FROM bronze.customers;

DROP TABLE IF EXISTS silver.suppliers;
CREATE TABLE silver.suppliers AS
SELECT
    supplier_id,
    supplier_name,
    category,
    CAST(payment_terms_days AS INTEGER) AS payment_terms_days,
    CASE
        WHEN critical_supplier IN ('True', 'true', '1') THEN TRUE
        ELSE FALSE
    END AS critical_supplier
FROM bronze.suppliers;

DROP TABLE IF EXISTS silver.sales_invoices;
CREATE TABLE silver.sales_invoices AS
SELECT
    si.invoice_id,
    si.customer_id,
    c.customer_name,
    CAST(si.invoice_date AS DATE) AS invoice_date,
    CAST(si.due_date AS DATE) AS due_date,
    CAST(si.net_amount AS NUMERIC) AS net_amount,
    CAST(si.vat_amount AS NUMERIC) AS vat_amount,
    CAST(si.gross_amount AS NUMERIC) AS gross_amount,
    si.status,
    CAST(sp.payment_date AS DATE) AS payment_date,
    CAST(sp.amount AS NUMERIC) AS paid_amount,
    CASE
        WHEN sp.payment_date IS NOT NULL
        THEN CAST(sp.payment_date AS DATE) - CAST(si.due_date AS DATE)
        ELSE NULL
    END AS days_late
FROM bronze.sales_invoices si
LEFT JOIN bronze.sales_payments sp
    ON si.invoice_id = sp.invoice_id
LEFT JOIN silver.customers c
    ON si.customer_id = c.customer_id;

DROP TABLE IF EXISTS silver.purchase_invoices;
CREATE TABLE silver.purchase_invoices AS
SELECT
    pi.invoice_id,
    pi.supplier_id,
    s.supplier_name,
    pi.category,
    CAST(pi.invoice_date AS DATE) AS invoice_date,
    CAST(pi.due_date AS DATE) AS due_date,
    CAST(pi.net_amount AS NUMERIC) AS net_amount,
    CAST(pi.vat_amount AS NUMERIC) AS vat_amount,
    CAST(pi.gross_amount AS NUMERIC) AS gross_amount,
    pi.status,
    CASE
        WHEN pi.must_pay_on_time IN ('True', 'true', '1') THEN TRUE
        ELSE FALSE
    END AS must_pay_on_time,
    CAST(pp.payment_date AS DATE) AS payment_date,
    CAST(pp.amount AS NUMERIC) AS paid_amount
FROM bronze.purchase_invoices pi
LEFT JOIN bronze.purchase_payments pp
    ON pi.invoice_id = pp.invoice_id
LEFT JOIN silver.suppliers s
    ON pi.supplier_id = s.supplier_id;

DROP TABLE IF EXISTS silver.cash_events;
CREATE TABLE silver.cash_events AS
SELECT
    transaction_id AS event_id,
    CAST(transaction_date AS DATE) AS event_date,
    type AS event_type,
    counterparty,
    description,
    CAST(amount AS NUMERIC) AS amount,
    CAST(balance_after AS NUMERIC) AS balance_after,
    linked_invoice_id,
    'bank_transaction' AS source_type
FROM bronze.bank_transactions;

DROP TABLE IF EXISTS silver.obligations;
CREATE TABLE silver.obligations AS

SELECT
    'PAYROLL-' || period AS obligation_id,
    CAST(payment_date AS DATE) AS due_date,
    'payroll' AS obligation_type,
    'Palk ja tööjõumaksud' AS counterparty,
    CAST(total_cash_out AS NUMERIC) AS amount,
    TRUE AS must_pay_on_time,
    status
FROM bronze.payroll_obligations

UNION ALL

SELECT
    'VAT-' || period AS obligation_id,
    CAST(due_date AS DATE) AS due_date,
    'vat' AS obligation_type,
    'Maksu- ja Tolliamet' AS counterparty,
    CAST(vat_payable AS NUMERIC) AS amount,
    TRUE AS must_pay_on_time,
    status
FROM bronze.vat_obligations
WHERE CAST(vat_payable AS NUMERIC) > 0

UNION ALL

SELECT
    invoice_id AS obligation_id,
    CAST(due_date AS DATE) AS due_date,
    'purchase_invoice' AS obligation_type,
    supplier_id AS counterparty,
    CAST(gross_amount AS NUMERIC) AS amount,
    CASE
        WHEN must_pay_on_time IN ('True', 'true', '1') THEN TRUE
        ELSE FALSE
    END AS must_pay_on_time,
    status
FROM bronze.purchase_invoices;

DROP TABLE IF EXISTS silver.company_annual_reports;
CREATE TABLE silver.company_annual_reports AS
SELECT
    company_id,
    CAST(report_year AS INTEGER) AS report_year,
    CAST(revenue AS NUMERIC) AS revenue,
    CAST(profit AS NUMERIC) AS profit,
    CAST(assets AS NUMERIC) AS assets,
    CAST(liabilities AS NUMERIC) AS liabilities,
    CAST(equity AS NUMERIC) AS equity,
    CAST(cash AS NUMERIC) AS cash,
    CAST(employees AS INTEGER) AS employees
FROM bronze.own_annual_reports;