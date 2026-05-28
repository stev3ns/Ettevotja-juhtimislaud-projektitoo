import os
import json
import hmac
import hashlib
import base64
import uuid
from datetime import datetime, timezone

import psycopg2
import requests
from psycopg2.extras import Json
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
        timeout=60,
    )

    if response.status_code != 200:
        raise RuntimeError(f"Merit API viga {response.status_code}: {response.text}")

    data = response.json()

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        # Kui Merit tagastab kunagi objektina wrapperi, siis proovime leida esimese listi.
        for value in data.values():
            if isinstance(value, list):
                return value

    raise RuntimeError(f"Ootamatu Merit API vastuse kuju: {type(data)} {data}")


def get_db_connection():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )


def save_sales_invoices(invoices, batch_id):
    sql = """
        INSERT INTO staging.merit_sales_invoices_raw (
            batch_id,
            source_system,
            endpoint,
            sih_id,
            changed_date,
            raw_payload
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (batch_id, sih_id)
        DO UPDATE SET
            loaded_at = now(),
            changed_date = EXCLUDED.changed_date,
            raw_payload = EXCLUDED.raw_payload;
    """

    saved_count = 0

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for invoice in invoices:
                sih_id = invoice.get("SIHId")

                if not sih_id:
                    print(f"Jätan müügiarve vahele, SIHId puudub: {invoice}")
                    continue

                cur.execute(
                    sql,
                    (
                        batch_id,
                        "merit",
                        "/api/v2/getinvoices",
                        sih_id,
                        invoice.get("ChangedDate"),
                        Json(invoice),
                    ),
                )
                saved_count += 1

        conn.commit()

    return saved_count


def save_payments(payments, batch_id):
    sql = """
        INSERT INTO staging.merit_payments_raw (
            batch_id,
            source_system,
            endpoint,
            payment_id,
            changed_date,
            raw_payload
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (payment_id)
        DO UPDATE SET
            loaded_at = now(),
            changed_date = EXCLUDED.changed_date,
            raw_payload = EXCLUDED.raw_payload;
    """

    saved_count = 0

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for payment in payments:
                payment_id = payment.get("PHId")

                if not payment_id:
                    print(f"Jätan makse/laekumise vahele, PHId puudub: {payment}")
                    continue

                cur.execute(
                    sql,
                    (
                        batch_id,
                        "merit",
                        "/api/v2/getpayments",
                        payment_id,
                        payment.get("ChangedDate"),
                        Json(payment),
                    ),
                )
                saved_count += 1

        conn.commit()

    return saved_count


def main():
    batch_id = str(uuid.uuid4())

    payload = {
        "PeriodStart": "20260501",
        "PeriodEnd": "20260531",
        "UnPaid": False,
        "DateType": 0,
    }

    print(f"batch_id: {batch_id}")

    print("Küsin Meritist müügiarveid...")
    sales_invoices = merit_post("/api/v2/getinvoices", payload)
    print(f"Müügiarveid tuli Meritist: {len(sales_invoices)}")

    if sales_invoices:
        print("Esimene müügiarve näidis:")
        print(json.dumps(sales_invoices[0], ensure_ascii=False, indent=2))

    print("Salvestan müügiarved staging tabelisse...")
    saved_sales = save_sales_invoices(sales_invoices, batch_id)
    print(f"Müügiarveid salvestatud: {saved_sales}")
    print("Tabel: staging.merit_sales_invoices_raw")

    print("Küsin Meritist makseid/laekumisi...")
    payments = merit_post("/api/v2/getpayments", payload)
    print(f"Makseid/laekumisi tuli Meritist: {len(payments)}")

    if payments:
        print("Esimene makse/laekumise näidis:")
        print(json.dumps(payments[0], ensure_ascii=False, indent=2))

    print("Salvestan maksed/laekumised staging tabelisse...")
    saved_payments = save_payments(payments, batch_id)
    print(f"Makseid/laekumisi salvestatud: {saved_payments}")
    print("Tabel: staging.merit_payments_raw")

    print("Meriti müügiarvete ja maksete/laekumiste staging laadimine valmis.")


if __name__ == "__main__":
    main()