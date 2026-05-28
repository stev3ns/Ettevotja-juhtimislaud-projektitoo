import os
import json
import hmac
import hashlib
import base64
import uuid
import psycopg2
import requests
from psycopg2.extras import Json
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv(override=True)


def get_env(name, default=None):
    value = os.getenv(name, default)
    if value is None or str(value).strip() == "":
        raise RuntimeError(f"Puudub keskkonnamuutuja: {name}")
    return str(value).strip()


MERIT_API_ID = get_env("MERIT_API_ID")
MERIT_API_KEY = get_env("MERIT_API_KEY")
MERIT_API_BASE_URL = get_env("MERIT_API_BASE_URL", "https://aktiva.merit.ee")

POSTGRES_HOST = get_env("POSTGRES_HOST", "localhost")
POSTGRES_PORT = get_env("POSTGRES_PORT", "55432")
POSTGRES_DB = get_env("POSTGRES_DB", "juhtimislaud")
POSTGRES_USER = get_env("POSTGRES_USER", "praktikum")
POSTGRES_PASSWORD = get_env("POSTGRES_PASSWORD", "praktikum")


def merit_post(endpoint, payload):
    url = f"{MERIT_API_BASE_URL}{endpoint}"

    http_body = json.dumps(payload, separators=(",", ":"))
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    data_to_sign = MERIT_API_ID + timestamp + http_body

    signature = base64.b64encode(
        hmac.new(
            MERIT_API_KEY.encode("ascii"),
            data_to_sign.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode("utf-8")

    params = {
        "apiId": MERIT_API_ID,
        "timestamp": timestamp,
        "signature": signature,
    }

    response = requests.post(
        url,
        params=params,
        data=http_body,
        headers={"Content-Type": "application/json"},
    )

    if response.status_code != 200:
        raise RuntimeError(f"Merit API viga {response.status_code}: {response.text}")

    return response.json()


def get_db_connection():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )


def save_customers(customers, batch_id):
    sql = """
        INSERT INTO staging.merit_customers_raw (
            batch_id,
            source_system,
            endpoint,
            customer_id,
            reg_no,
            changed_date,
            raw_payload
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (batch_id, customer_id)
        DO UPDATE SET
            loaded_at = now(),
            reg_no = EXCLUDED.reg_no,
            changed_date = EXCLUDED.changed_date,
            raw_payload = EXCLUDED.raw_payload;
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for customer in customers:
                customer_id = customer.get("CustomerId") or customer.get("Id")
                reg_no = customer.get("RegNo")
                changed_date = customer.get("ChangedDate")

                if not customer_id:
                    continue

                cur.execute(
                    sql,
                    (
                        batch_id,
                        "merit",
                        "/api/v1/getcustomers",
                        customer_id,
                        reg_no,
                        changed_date,
                        Json(customer),
                    ),
                )

        conn.commit()


def save_vendors(vendors, batch_id):
    sql = """
        INSERT INTO staging.merit_vendors_raw (
            batch_id,
            source_system,
            endpoint,
            vendor_id,
            reg_no,
            changed_date,
            raw_payload
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (batch_id, vendor_id)
        DO UPDATE SET
            loaded_at = now(),
            reg_no = EXCLUDED.reg_no,
            changed_date = EXCLUDED.changed_date,
            raw_payload = EXCLUDED.raw_payload;
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for vendor in vendors:
                vendor_id = vendor.get("VendorId") or vendor.get("Id")
                reg_no = vendor.get("RegNo")
                changed_date = vendor.get("ChangedDate")

                if not vendor_id:
                    continue

                cur.execute(
                    sql,
                    (
                        batch_id,
                        "merit",
                        "/api/v1/getvendors",
                        vendor_id,
                        reg_no,
                        changed_date,
                        Json(vendor),
                    ),
                )

        conn.commit()


def main():
    batch_id = str(uuid.uuid4())

    print(f"batch_id: {batch_id}")

    payload = {
        "ChangedDate": "20260101"
    }

    print("Küsin Meritist kliente...")
    customers = merit_post("/api/v1/getcustomers", payload)
    print(f"Meritist tuli {len(customers)} klienti.")

    print("Salvestan kliendid stagingusse...")
    save_customers(customers, batch_id)

    print("Küsin Meritist hankijaid...")
    vendors = merit_post("/api/v1/getvendors", payload)
    print(f"Meritist tuli {len(vendors)} hankijat.")

    print("Salvestan hankijad stagingusse...")
    save_vendors(vendors, batch_id)

    print("Meriti kliendid ja hankijad salvestatud staging tabelitesse.")


if __name__ == "__main__":
    main()