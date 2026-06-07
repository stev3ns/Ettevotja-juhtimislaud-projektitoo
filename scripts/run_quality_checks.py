import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv(override=True)


def get_env(name, default=None):
    value = os.getenv(name, default)
    if value is None or str(value).strip() == "":
        raise RuntimeError(f"Puudub keskkonnamuutuja: {name}")
    return str(value).strip()


POSTGRES_HOST = get_env("POSTGRES_HOST")
POSTGRES_PORT = get_env("POSTGRES_PORT")
POSTGRES_DB = get_env("POSTGRES_DB")
POSTGRES_USER = get_env("POSTGRES_USER")
POSTGRES_PASSWORD = get_env("POSTGRES_PASSWORD")

SCRIPTS_DIR = Path(__file__).resolve().parent
QUALITY_DIR = SCRIPTS_DIR / "quality_tests"

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
WARN = "\033[93mWARN\033[0m"


def get_db_connection():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )


def run_check(cur, label, sql, expect_zero=True):
    cur.execute(sql)
    rows = cur.fetchall()
    value = rows[0][0] if rows else None
    if expect_zero:
        status = PASS if value == 0 else FAIL
    else:
        status = PASS if value and value > 0 else FAIL
    print(f"  [{status}] {label}: {value}")
    return value


def main():
    print("\n========================================")
    print("Andmekvaliteedi kontroll")
    print("Dashboard loeb andmeid otse Supabase mart vaadetest.")
    print("========================================\n")

    conn = get_db_connection()
    cur = conn.cursor()

    # --- STAGING: Merit ---
    print("STAGING: Merit arved ja maksed")

    run_check(cur, "staging.merit_sales_invoices_raw ridu", "SELECT COUNT(*) FROM staging.merit_sales_invoices_raw", expect_zero=False)
    run_check(cur, "staging.merit_purchase_invoices_raw ridu", "SELECT COUNT(*) FROM staging.merit_purchase_invoices_raw", expect_zero=False)
    run_check(cur, "staging.merit_payments_raw ridu", "SELECT COUNT(*) FROM staging.merit_payments_raw", expect_zero=False)
    run_check(cur, "staging.merit_customers_raw ridu", "SELECT COUNT(*) FROM staging.merit_customers_raw", expect_zero=False)
    run_check(cur, "staging.merit_vendors_raw ridu", "SELECT COUNT(*) FROM staging.merit_vendors_raw", expect_zero=False)

    run_check(cur, "puuduv sih_id (müügiarved)", "SELECT COUNT(*) FROM staging.merit_sales_invoices_raw WHERE sih_id IS NULL OR sih_id = ''")
    run_check(cur, "puuduv pih_id (ostuarved)", "SELECT COUNT(*) FROM staging.merit_purchase_invoices_raw WHERE pih_id IS NULL OR pih_id = ''")
    run_check(cur, "puuduv payment_id", "SELECT COUNT(*) FROM staging.merit_payments_raw WHERE payment_id IS NULL OR payment_id = ''")

    run_check(cur, "duplikaadid sih_id", "SELECT COUNT(*) FROM (SELECT sih_id FROM staging.merit_sales_invoices_raw GROUP BY sih_id HAVING COUNT(*) > 1) x")
    run_check(cur, "duplikaadid pih_id", "SELECT COUNT(*) FROM (SELECT pih_id FROM staging.merit_purchase_invoices_raw GROUP BY pih_id HAVING COUNT(*) > 1) x")
    run_check(cur, "duplikaadid payment_id", "SELECT COUNT(*) FROM (SELECT payment_id FROM staging.merit_payments_raw GROUP BY payment_id HAVING COUNT(*) > 1) x")

    # --- STAGING: EMTA ---
    print("\nSTAGING: EMTA andmed")

    run_check(cur, "staging.emta_tax_debt_raw ridu", "SELECT COUNT(*) FROM staging.emta_tax_debt_raw", expect_zero=False)
    run_check(cur, "staging.emta_paid_taxes_raw ridu", "SELECT COUNT(*) FROM staging.emta_paid_taxes_raw", expect_zero=False)
    run_check(cur, "puuduv raw_payload (maksuvõlg)", "SELECT COUNT(*) FROM staging.emta_tax_debt_raw WHERE raw_payload IS NULL")
    run_check(cur, "puuduv raw_payload (tasutud maksud)", "SELECT COUNT(*) FROM staging.emta_paid_taxes_raw WHERE raw_payload IS NULL")

    # --- MART ---
    print("\nMART: KPI-d ja vaated")

    run_check(cur, "mart.kpi_last_30_days ridu", "SELECT COUNT(*) FROM mart.kpi_last_30_days", expect_zero=False)
    run_check(cur, "mart.merit_sales_invoices ridu", "SELECT COUNT(*) FROM mart.merit_sales_invoices", expect_zero=False)
    run_check(cur, "mart.merit_purchase_invoices ridu", "SELECT COUNT(*) FROM mart.merit_purchase_invoices", expect_zero=False)
    run_check(cur, "mart.merit_payments ridu", "SELECT COUNT(*) FROM mart.merit_payments", expect_zero=False)
    run_check(cur, "mart.emta_counterparty_tax_risk ridu", "SELECT COUNT(*) FROM mart.emta_counterparty_tax_risk", expect_zero=False)

    run_check(cur, "müügiarved ilma ärikuupäevata", "SELECT COUNT(*) FROM mart.merit_sales_invoices WHERE invoice_date IS NULL")
    run_check(cur, "ostuarved ilma ärikuupäevata", "SELECT COUNT(*) FROM mart.merit_purchase_invoices WHERE invoice_date IS NULL")

    # --- EMTA vastaspooled ---
    print("\nEMTA vastaspoolte risk")

    run_check(cur, "vastaspooled registrikoodiga", "SELECT COUNT(*) FROM mart.counterparties_with_reg_code", expect_zero=False)
    run_check(cur, "vastaspooled ilma registrikoodita", "SELECT COUNT(*) FROM mart.counterparties_missing_reg_code")

    # --- KPI väärtused ---
    print("\nKPI väärtused (viimased 30 päeva)")
    cur.execute("SELECT sales_last_30d_eur, costs_last_30d_eur, net_cashflow_last_30d_eur FROM mart.kpi_last_30_days LIMIT 1")
    row = cur.fetchone()
    if row:
        print(f"  Müük:        {row[0]} EUR")
        print(f"  Kulud:       {row[1]} EUR")
        print(f"  Kasum/kahjum:    {row[2]} EUR")
    else:
        print(f"  [{FAIL}] KPI vaade ei tagasta tulemust")

    cur.close()
    conn.close()
    print("\n========================================")
    print("Kontroll lõpetatud.")
    print("========================================\n")


if __name__ == "__main__":
    main()
