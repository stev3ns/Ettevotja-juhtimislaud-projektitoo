import requests
import pandas as pd
from sqlalchemy import create_engine, text

# ---------------------------------------
# 1. Seadistus
# ---------------------------------------

API_BASE_URL = "http://localhost:8001/api"
API_KEY = "demo-api-key"

POSTGRES_URL = "postgresql+psycopg2://postgres:postgres@localhost:5436/juhtimislaud"

engine = create_engine(POSTGRES_URL)


# ---------------------------------------
# 2. Küsi andmed fake Merit API-st
# ---------------------------------------

def fetch_from_api(endpoint: str):
    url = f"{API_BASE_URL}/{endpoint}"
    params = {"api_key": API_KEY}

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    return response.json()


# ---------------------------------------
# 3. Loo PostgreSQL bronze skeem
# ---------------------------------------

def create_bronze_schema():
    with engine.begin() as connection:
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS bronze;"))


# ---------------------------------------
# 4. Lae üks API endpoint PostgreSQL tabelisse
# ---------------------------------------

def load_endpoint_to_postgres(endpoint: str, table_name: str):
    print(f"Küsin API-st: {endpoint}")

    data = fetch_from_api(endpoint)

    if not data:
        print(f"Endpoint {endpoint} ei tagastanud andmeid.")
        return

    df = pd.DataFrame(data)

    print(f"Laen tabelisse bronze.{table_name}: {len(df)} rida")

    df.to_sql(
        name=table_name,
        con=engine,
        schema="bronze",
        if_exists="replace",
        index=False,
    )


# ---------------------------------------
# 5. Käivita kogu ETL
# ---------------------------------------

def main():
    print("Alustan ETL-i")

    create_bronze_schema()

    endpoints = {
        "customers": "customers",
        "suppliers": "suppliers",
        "sales-invoices": "sales_invoices",
        "sales-payments": "sales_payments",
        "purchase-invoices": "purchase_invoices",
        "purchase-payments": "purchase_payments",
        "bank-transactions": "bank_transactions",
        "payroll-obligations": "payroll_obligations",
        "vat-obligations": "vat_obligations",
        "own-annual-reports": "own_annual_reports",
    }

    for endpoint, table_name in endpoints.items():
        load_endpoint_to_postgres(endpoint, table_name)

    print("ETL valmis. Andmed on PostgreSQL bronze skeemis.")


if __name__ == "__main__":
    main()