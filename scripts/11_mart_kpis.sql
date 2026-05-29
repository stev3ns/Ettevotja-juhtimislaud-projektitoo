CREATE SCHEMA IF NOT EXISTS mart;

CREATE OR REPLACE VIEW mart.kpi_daily AS
WITH sales AS (
    SELECT
        COALESCE(invoice_date, changed_date::DATE, loaded_at::DATE) AS day_date,
        sum(COALESCE(amount_with_tax_eur, 0)) AS sales_revenue_eur,
        sum(COALESCE(vat_amount_eur, 0)) AS sales_vat_eur
    FROM mart.merit_sales_invoices
    GROUP BY 1
),
purchases AS (
    SELECT
        COALESCE(invoice_date, changed_date::DATE, loaded_at::DATE) AS day_date,
        sum(COALESCE(amount_with_tax_eur, 0)) AS purchase_cost_eur,
        sum(COALESCE(vat_amount_eur, 0)) AS purchase_vat_eur
    FROM mart.merit_purchase_invoices
    GROUP BY 1
),
payments AS (
    SELECT
        COALESCE(payment_date, changed_date::DATE, loaded_at::DATE) AS day_date,
        sum(CASE WHEN COALESCE(amount_eur, 0) >= 0 THEN COALESCE(amount_eur, 0) ELSE 0 END) AS incoming_payments_eur,
        sum(CASE WHEN COALESCE(amount_eur, 0) < 0 THEN abs(COALESCE(amount_eur, 0)) ELSE 0 END) AS outgoing_payments_eur,
        sum(COALESCE(amount_eur, 0)) AS net_cashflow_eur
    FROM mart.merit_payments
    GROUP BY 1
),
base_dates AS (
    SELECT day_date FROM sales
    UNION
    SELECT day_date FROM purchases
    UNION
    SELECT day_date FROM payments
)
SELECT
    b.day_date,
    COALESCE(s.sales_revenue_eur, 0) AS sales_revenue_eur,
    COALESCE(p.purchase_cost_eur, 0) AS purchase_cost_eur,
    COALESCE(pm.incoming_payments_eur, 0) AS incoming_payments_eur,
    COALESCE(pm.outgoing_payments_eur, 0) AS outgoing_payments_eur,
    COALESCE(pm.net_cashflow_eur, 0) AS net_cashflow_eur,
    COALESCE(s.sales_vat_eur, 0) - COALESCE(p.purchase_vat_eur, 0) AS vat_payable_eur
FROM base_dates b
LEFT JOIN sales s ON s.day_date = b.day_date
LEFT JOIN purchases p ON p.day_date = b.day_date
LEFT JOIN payments pm ON pm.day_date = b.day_date;

CREATE OR REPLACE VIEW mart.kpi_monthly AS
SELECT
    date_trunc('month', day_date)::DATE AS month_date,
    sum(sales_revenue_eur) AS sales_revenue_eur,
    sum(purchase_cost_eur) AS purchase_cost_eur,
    sum(incoming_payments_eur) AS incoming_payments_eur,
    sum(outgoing_payments_eur) AS outgoing_payments_eur,
    sum(net_cashflow_eur) AS net_cashflow_eur,
    sum(vat_payable_eur) AS vat_payable_eur
FROM mart.kpi_daily
GROUP BY 1;

CREATE OR REPLACE VIEW mart.kpi_last_30_days AS
SELECT
    CURRENT_DATE AS snapshot_date,
    sum(sales_revenue_eur) AS sales_last_30d_eur,
    sum(purchase_cost_eur) AS costs_last_30d_eur,
    sum(net_cashflow_eur) AS net_cashflow_last_30d_eur,
    sum(vat_payable_eur) AS vat_payable_last_30d_eur
FROM mart.kpi_daily
WHERE day_date BETWEEN CURRENT_DATE - INTERVAL '30 days' AND CURRENT_DATE - INTERVAL '1 day';

CREATE OR REPLACE VIEW mart.kpi_runway AS
WITH balance AS (
    SELECT COALESCE(sum(net_cashflow_eur), 0) AS current_buffer_eur
    FROM mart.kpi_daily
),
expense AS (
    SELECT COALESCE(avg(outgoing_payments_eur), 0) AS avg_daily_expense_30d_eur
    FROM mart.kpi_daily
    WHERE day_date BETWEEN CURRENT_DATE - INTERVAL '30 days' AND CURRENT_DATE - INTERVAL '1 day'
)
SELECT
    CURRENT_DATE AS snapshot_date,
    b.current_buffer_eur,
    e.avg_daily_expense_30d_eur,
    CASE
        WHEN e.avg_daily_expense_30d_eur > 0 THEN round((b.current_buffer_eur / e.avg_daily_expense_30d_eur)::NUMERIC, 2)
        ELSE NULL
    END AS runway_days
FROM balance b
CROSS JOIN expense e;