# Sprint 2 flow check
# Quick verification for team / instructor review

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================"
Write-Host "Sprint 2 flow check"
Write-Host "========================================"
Write-Host ""

Write-Host "1. Starting Docker database..."
docker compose up -d db

Write-Host ""
Write-Host "2. Checking database connection..."
docker compose exec db psql -U praktikum -d juhtimislaud -c "SELECT 1;"

Write-Host ""
Write-Host "3. Checking Merit staging counts..."
docker compose exec db psql -U praktikum -d juhtimislaud -P pager=off -c "
SELECT 'purchase_invoices' AS table_name, COUNT(*) AS row_count
FROM staging.merit_purchase_invoices_raw
UNION ALL
SELECT 'sales_invoices', COUNT(*)
FROM staging.merit_sales_invoices_raw
UNION ALL
SELECT 'payments', COUNT(*)
FROM staging.merit_payments_raw
UNION ALL
SELECT 'customers', COUNT(*)
FROM staging.merit_customers_raw
UNION ALL
SELECT 'vendors', COUNT(*)
FROM staging.merit_vendors_raw;
"

Write-Host ""
Write-Host "4. Running Merit staging quality checks..."
Get-Content .\scripts\check_merit_staging_quality.sql | docker compose exec -T db psql -U praktikum -d juhtimislaud

Write-Host ""
Write-Host "5. Running mart layer..."
python .\scripts\run_mart.py

Write-Host ""
Write-Host "6. Checking mart KPI output..."
docker compose exec db psql -U praktikum -d juhtimislaud -P pager=off -c "
SELECT *
FROM mart.kpi_last_30_days;
"

Write-Host ""
Write-Host "7. Exporting mart CSV files..."
.\scripts\export_mart_csv.ps1

Write-Host ""
Write-Host "========================================"
Write-Host "Sprint 2 flow check completed."
Write-Host "Expected KPI example:"
Write-Host "sales_last_30d_eur:        8207.00"
Write-Host "costs_last_30d_eur:        1237.00"
Write-Host "net_cashflow_last_30d_eur: 1716.94"
Write-Host "========================================"