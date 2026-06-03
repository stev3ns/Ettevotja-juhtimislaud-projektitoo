CREATE OR REPLACE VIEW mart.monthly_sales_costs AS
WITH sales AS (
    SELECT
        date_trunc('month', invoice_date)::date AS month_start,
        SUM(COALESCE(amount_with_tax_eur, 0)) AS sales_eur
    FROM mart.merit_sales_invoices
    WHERE invoice_date IS NOT NULL
    GROUP BY 1
),
costs AS (
    SELECT
        date_trunc('month', invoice_date)::date AS month_start,
        SUM(COALESCE(amount_with_tax_eur, 0)) AS costs_eur
    FROM mart.merit_purchase_invoices
    WHERE invoice_date IS NOT NULL
    GROUP BY 1
),
months AS (
    SELECT month_start FROM sales
    UNION
    SELECT month_start FROM costs
)
SELECT
    to_char(m.month_start, 'YYYY-MM') AS month,
    m.month_start,
    ROUND(COALESCE(s.sales_eur, 0)::numeric, 2) AS sales_eur,
    ROUND(COALESCE(c.costs_eur, 0)::numeric, 2) AS costs_eur,
    ROUND((COALESCE(s.sales_eur, 0) - COALESCE(c.costs_eur, 0))::numeric, 2) AS net_eur
FROM months m
LEFT JOIN sales s ON s.month_start = m.month_start
LEFT JOIN costs c ON c.month_start = m.month_start
ORDER BY m.month_start;