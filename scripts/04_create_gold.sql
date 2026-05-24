-- Fake data silver -> gold transformation
-- This script creates dashboard-ready KPI tables from silver tables.

CREATE SCHEMA IF NOT EXISTS gold;

-- 1. Cashflow overview by month
DROP TABLE IF EXISTS gold.cashflow_monthly;
CREATE TABLE gold.cashflow_monthly AS
SELECT
    DATE_TRUNC('month', event_date)::date AS month,
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS cash_in,
    SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) AS cash_out,
    SUM(amount) AS net_cashflow,
    COUNT(*) AS event_count
FROM silver.cash_events
GROUP BY DATE_TRUNC('month', event_date)::date
ORDER BY month;


-- 2. Overdue receivables
DROP TABLE IF EXISTS gold.overdue_receivables;
CREATE TABLE gold.overdue_receivables AS
SELECT
    invoice_id,
    customer_id,
    customer_name,
    invoice_date,
    due_date,
    gross_amount,
    payment_date,
    paid_amount,
    days_late,
    status,
    CASE
        WHEN payment_date IS NULL AND due_date < CURRENT_DATE THEN TRUE
        WHEN days_late > 0 THEN TRUE
        ELSE FALSE
    END AS is_overdue,
    CASE
        WHEN payment_date IS NULL THEN gross_amount
        ELSE GREATEST(gross_amount - COALESCE(paid_amount, 0), 0)
    END AS open_amount
FROM silver.sales_invoices
WHERE
    payment_date IS NULL
    OR days_late > 0;


-- 3. Next 30 days obligations
DROP TABLE IF EXISTS gold.next_30_days_obligations;
CREATE TABLE gold.next_30_days_obligations AS
SELECT
    obligation_id,
    obligation_type,
    due_date,
    counterparty,
    amount,
    must_pay_on_time,
    status,
    due_date - CURRENT_DATE AS days_until_due,
    CASE
        WHEN due_date < CURRENT_DATE THEN 'overdue'
        WHEN due_date <= CURRENT_DATE + INTERVAL '7 days' THEN 'next_7_days'
        WHEN due_date <= CURRENT_DATE + INTERVAL '30 days' THEN 'next_30_days'
        ELSE 'later'
    END AS due_bucket
FROM silver.obligations
WHERE due_date <= CURRENT_DATE + INTERVAL '30 days'
ORDER BY due_date;


-- 4. Customer payment behaviour
DROP TABLE IF EXISTS gold.customer_payment_behaviour;
CREATE TABLE gold.customer_payment_behaviour AS
SELECT
    customer_id,
    customer_name,
    COUNT(*) AS invoice_count,
    SUM(gross_amount) AS total_invoiced,
    SUM(COALESCE(paid_amount, 0)) AS total_paid,
    AVG(days_late) FILTER (WHERE days_late IS NOT NULL) AS avg_days_late,
    COUNT(*) FILTER (WHERE days_late > 0) AS late_invoice_count,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE days_late > 0) / NULLIF(COUNT(*), 0),
        2
    ) AS late_invoice_percent
FROM silver.sales_invoices
GROUP BY customer_id, customer_name
ORDER BY total_invoiced DESC;


-- 5. Supplier obligations summary
DROP TABLE IF EXISTS gold.supplier_obligations_summary;
CREATE TABLE gold.supplier_obligations_summary AS
SELECT
    supplier_id,
    supplier_name,
    category,
    COUNT(*) AS invoice_count,
    SUM(gross_amount) AS total_purchase_amount,
    SUM(COALESCE(paid_amount, 0)) AS total_paid,
    SUM(gross_amount - COALESCE(paid_amount, 0)) AS open_amount,
    COUNT(*) FILTER (WHERE must_pay_on_time = TRUE) AS must_pay_on_time_count
FROM silver.purchase_invoices
GROUP BY supplier_id, supplier_name, category
ORDER BY total_purchase_amount DESC;


-- 6. Simple runway estimate
DROP TABLE IF EXISTS gold.runway_estimate;
CREATE TABLE gold.runway_estimate AS
WITH latest_cash AS (
    SELECT
        event_date,
        balance_after
    FROM silver.cash_events
    WHERE balance_after IS NOT NULL
    ORDER BY event_date DESC
    LIMIT 1
),
monthly_outflow AS (
    SELECT
        AVG(monthly_cash_out) AS avg_monthly_cash_out
    FROM (
        SELECT
            DATE_TRUNC('month', event_date)::date AS month,
            SUM(ABS(amount)) AS monthly_cash_out
        FROM silver.cash_events
        WHERE amount < 0
        GROUP BY DATE_TRUNC('month', event_date)::date
    ) x
),
next_obligations AS (
    SELECT
        SUM(amount) AS next_30_days_obligations
    FROM silver.obligations
    WHERE due_date <= CURRENT_DATE + INTERVAL '30 days'
)
SELECT
    lc.event_date AS latest_cash_date,
    lc.balance_after AS latest_cash_balance,
    mo.avg_monthly_cash_out,
    no.next_30_days_obligations,
    CASE
        WHEN mo.avg_monthly_cash_out > 0
        THEN ROUND(lc.balance_after / mo.avg_monthly_cash_out, 2)
        ELSE NULL
    END AS runway_months,
    CASE
        WHEN no.next_30_days_obligations > lc.balance_after THEN 'high_risk'
        WHEN mo.avg_monthly_cash_out > 0 AND lc.balance_after / mo.avg_monthly_cash_out < 1 THEN 'medium_risk'
        ELSE 'low_risk'
    END AS liquidity_risk_level
FROM latest_cash lc
CROSS JOIN monthly_outflow mo
CROSS JOIN next_obligations no;


-- 7. Dashboard summary cards
DROP TABLE IF EXISTS gold.dashboard_summary;
CREATE TABLE gold.dashboard_summary AS
SELECT
    (SELECT COUNT(*) FROM silver.sales_invoices) AS sales_invoice_count,
    (SELECT COUNT(*) FROM silver.purchase_invoices) AS purchase_invoice_count,
    (SELECT SUM(open_amount) FROM gold.overdue_receivables WHERE is_overdue = TRUE) AS overdue_receivables_amount,
    (SELECT SUM(amount) FROM gold.next_30_days_obligations) AS next_30_days_obligations_amount,
    (SELECT latest_cash_balance FROM gold.runway_estimate LIMIT 1) AS latest_cash_balance,
    (SELECT runway_months FROM gold.runway_estimate LIMIT 1) AS runway_months,
    (SELECT liquidity_risk_level FROM gold.runway_estimate LIMIT 1) AS liquidity_risk_level;