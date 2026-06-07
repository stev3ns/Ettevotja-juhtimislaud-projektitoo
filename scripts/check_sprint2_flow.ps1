# Sprint 2 flow check
# Quick verification for team / instructor review

$ErrorActionPreference = "Stop"

# Loe .env failist andmebaasi ühenduse andmed
$envFile = Join-Path (Join-Path $PSScriptRoot "..") ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]+)=(.*)$") {
            [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim())
        }
    }
}

$PGHOST     = $env:POSTGRES_HOST
$PGPORT     = $env:POSTGRES_PORT
$PGDATABASE = $env:POSTGRES_DB
$PGUSER     = $env:POSTGRES_USER
$PGPASSWORD = $env:POSTGRES_PASSWORD

$connStr = "postgresql://${PGUSER}:${PGPASSWORD}@${PGHOST}:${PGPORT}/${PGDATABASE}"

Write-Host ""
Write-Host "========================================"
Write-Host "Sprint 2 flow check"
Write-Host "========================================"
Write-Host ""

Write-Host "1. Checking database connection..."
psql $connStr -c "SELECT 1;"

Write-Host ""
Write-Host "2. Checking Merit staging counts..."
psql $connStr -P pager=off -c "
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
Write-Host "3. Running Merit staging quality checks..."
psql $connStr -f .\scripts\check_merit_staging_quality.sql

Write-Host ""
Write-Host "4. Running mart layer..."
python .\scripts\run_mart.py

Write-Host ""
Write-Host "5. Checking mart KPI output..."
psql $connStr -P pager=off -c "SELECT * FROM mart.kpi_last_30_days;"

Write-Host ""
Write-Host "6. Running quality checks..."
python .\scripts\run_quality_checks.py

Write-Host ""
Write-Host "========================================"
Write-Host "Sprint 2 flow check completed."
Write-Host "========================================"
