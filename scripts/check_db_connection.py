import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(override=True)

conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)
cur = conn.cursor()
cur.execute("SELECT 1")
print("  Andmebaas: OK")

tables = [
    "merit_sales_invoices_raw",
    "merit_purchase_invoices_raw",
    "merit_payments_raw",
    "merit_customers_raw",
    "merit_vendors_raw",
    "emta_tax_debt_raw",
    "emta_paid_taxes_raw",
]
for t in tables:
    cur.execute(f"SELECT COUNT(*) FROM staging.{t}")
    print(f"  staging.{t}: {cur.fetchone()[0]} rida")

conn.close()
