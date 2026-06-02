#!/usr/bin/env bash
set -e

echo "========================================"
echo "Running ALL staging quality tests"
echo "========================================"

echo ""
echo "---- PURCHASE TESTS ----"
cat scripts/quality_tests/test_purchase_pih_id_not_null.sql | docker compose exec -T db psql -U praktikum -d praktikum
cat scripts/quality_tests/test_purchase_pih_id_unique_latest_batch.sql | docker compose exec -T db psql -U praktikum -d praktikum
cat scripts/quality_tests/test_purchase_freshness_24h.sql | docker compose exec -T db psql -U praktikum -d praktikum

echo ""
echo "---- SALES TESTS ----"
cat scripts/quality_tests/test_sales_sih_id_not_null.sql | docker compose exec -T db psql -U praktikum -d praktikum
cat scripts/quality_tests/test_sales_sih_id_unique_latest_batch.sql | docker compose exec -T db psql -U praktikum -d praktikum
cat scripts/quality_tests/test_sales_freshness_24h.sql | docker compose exec -T db psql -U praktikum -d praktikum

echo ""
echo "---- PAYMENTS TESTS ----"
cat scripts/quality_tests/test_payments_payment_id_not_null.sql | docker compose exec -T db psql -U praktikum -d praktikum
cat scripts/quality_tests/test_payments_payment_id_unique_latest_batch.sql | docker compose exec -T db psql -U praktikum -d praktikum
cat scripts/quality_tests/test_payments_freshness_24h.sql | docker compose exec -T db psql -U praktikum -d praktikum

echo ""
echo "========================================"
echo "All staging quality tests PASSED"
echo "========================================"
