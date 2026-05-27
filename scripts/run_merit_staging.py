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
            hashlib.sha256
        ).digest()
    ).decode("utf-8")

    params = {
        "apiId": MERIT_API_ID,
        "timestamp": timestamp,
        "signature": signature
    }

    response = requests.post(
        url,
        params=params,
        data=http_body,
        headers={"Content-Type": "application/json"}
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


def save_purchase_invoices(invoices, batch_id):
    sql = """
        INSERT INTO staging.merit_purchase_invoices_raw (
            batch_id,
            source_system,
            endpoint,
            pih_id,
            changed_date,
            raw_payload
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (batch_id, pih_id)
        DO UPDATE SET
            loaded_at = now(),
            changed_date = EXCLUDED.changed_date,
            raw_payload = EXCLUDED.raw_payload;
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for invoice in invoices:
                cur.execute(
                    sql,
                    (
                        batch_id,
                        "merit",
                        "/api/v2/getpurchorders",
                        invoice.get("PIHId"),
                        invoice.get("ChangedDate"),
                        Json(invoice),
                    )
                )
        conn.commit()


def main():
    batch_id = str(uuid.uuid4())

    payload = {
        "PeriodStart": "20260501",
        "PeriodEnd": "20260531",
        "UnPaid": False,
        "DateType": 0
    }

    print("Küsin Meritist ostuarveid...")
    invoices = merit_post("/api/v2/getpurchorders", payload)

    print(f"Meritist tuli {len(invoices)} ostuarvet.")
    print(f"batch_id: {batch_id}")

    save_purchase_invoices(invoices, batch_id)

    print("Salvestatud tabelisse staging.merit_purchase_invoices_raw")


if __name__ == "__main__":
    main()