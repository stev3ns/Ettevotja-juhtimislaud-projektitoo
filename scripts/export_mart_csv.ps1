# Export mart layer views to CSV files
# This is meant for dashboard prototype, reconciliation checks and manual review.

$ErrorActionPreference = "Stop"

$ExportDir = "exports"

New-Item -ItemType Directory -Force -Path $ExportDir | Out-Null

Write-Host "Exporting mart views to CSV..."
Write-Host "Output directory: $ExportDir"
Write-Host ""

function Export-MartView {
    param (
        [string]$ViewName,
        [string]$FileName
    )

    $OutputPath = Join-Path $ExportDir $FileName

    Write-Host "Exporting $ViewName -> $OutputPath"

    docker compose exec -T db psql `
        -U praktikum `
        -d juhtimislaud `
        -c "\copy (SELECT * FROM $ViewName) TO STDOUT WITH CSV HEADER" `
        > $OutputPath
}

# KPI views
Export-MartView "mart.kpi_last_30_days" "mart_kpi_last_30_days.csv"
Export-MartView "mart.kpi_daily" "mart_kpi_daily.csv"
Export-MartView "mart.kpi_monthly" "mart_kpi_monthly.csv"
Export-MartView "mart.kpi_runway" "mart_kpi_runway.csv"
Export-MartView "mart.counterparty_activity" "mart_counterparty_activity.csv"
Export-MartView "mart.counterparties_with_reg_code" "mart_counterparties_with_reg_code.csv"
Export-MartView "mart.emta_counterparty_tax_risk" "mart_emta_counterparty_tax_risk.csv"
Export-MartView "mart.counterparties_missing_reg_code" "mart_counterparties_missing_reg_code.csv"

# Merit views
Export-MartView "mart.merit_sales_invoices" "mart_merit_sales_invoices.csv"
Export-MartView "mart.merit_purchase_invoices" "mart_merit_purchase_invoices.csv"
Export-MartView "mart.merit_payments" "mart_merit_payments.csv"
Export-MartView "mart.merit_customers" "mart_merit_customers.csv"
Export-MartView "mart.merit_vendors" "mart_merit_vendors.csv"

# EMTA views
Export-MartView "mart.emta_tax_debt" "mart_emta_tax_debt.csv"
Export-MartView "mart.emta_paid_taxes" "mart_emta_paid_taxes.csv"
Export-MartView "mart.emta_competitor_summary" "mart_emta_competitor_summary.csv"

Write-Host ""
Write-Host "Mart CSV export valmis."
Write-Host "Failid asuvad kaustas: $ExportDir"