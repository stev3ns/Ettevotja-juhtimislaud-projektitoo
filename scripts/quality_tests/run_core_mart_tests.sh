#!/usr/bin/env bash
set -euo pipefail

echo "Running CORE mart tests..."

cat scripts/quality_tests/test_mart_merit_sales_invoices_key_quality.sql | docker compose exec -T db psql -v ON_ERROR_STOP=1 -U praktikum -d praktikum

cat scripts/quality_tests/test_mart_emta_counterparty_tax_risk_consistency.sql | docker compose exec -T db psql -v ON_ERROR_STOP=1 -U praktikum -d praktikum

cat scripts/quality_tests/test_mart_monthly_sales_costs_consistency.sql | docker compose exec -T db psql -v ON_ERROR_STOP=1 -U praktikum -d praktikum

echo "All CORE mart tests PASSED"
