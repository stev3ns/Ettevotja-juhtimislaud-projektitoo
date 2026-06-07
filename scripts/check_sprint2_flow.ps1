# Sprint 2 flow check
# Quick verification for team / instructor review

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================"
Write-Host "Sprint 2 flow check"
Write-Host "========================================"
Write-Host ""

Write-Host "1. Checking database connection & staging counts..."
python .\scripts\check_db_connection.py

Write-Host ""
Write-Host "2. Running mart layer..."
python .\scripts\run_mart.py

Write-Host ""
Write-Host "3. Running quality checks..."
python .\scripts\run_quality_checks.py

Write-Host ""
Write-Host "========================================"
Write-Host "Sprint 2 flow check completed."
Write-Host "========================================"
