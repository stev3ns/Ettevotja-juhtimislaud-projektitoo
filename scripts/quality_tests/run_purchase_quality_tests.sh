#!/usr/bin/env bash
set -e

echo "Running NOT NULL test..."
cat scripts/quality_tests/test_purchase_pih_id_not_null.sql | docker compose exec -T db psql -U praktikum -d praktikum

echo "Running UNIQUE test..."
cat scripts/quality_tests/test_purchase_pih_id_unique_latest_batch.sql | docker compose exec -T db psql -U praktikum -d praktikum

echo "Running FRESHNESS test..."
cat scripts/quality_tests/test_purchase_freshness_24h.sql | docker compose exec -T db psql -U praktikum -d praktikum

echo "All purchase staging quality tests PASSED"
