#!/usr/bin/env bash
set -e

echo "Running payments NOT NULL test..."
cat scripts/quality_tests/test_payments_payment_id_not_null.sql | docker compose exec -T db psql -U praktikum -d praktikum

echo "Running payments UNIQUE test..."
cat scripts/quality_tests/test_payments_payment_id_unique_latest_batch.sql | docker compose exec -T db psql -U praktikum -d praktikum

echo "Running payments FRESHNESS test..."
cat scripts/quality_tests/test_payments_freshness_24h.sql | docker compose exec -T db psql -U praktikum -d praktikum

echo "All payments staging quality tests PASSED"
