import os
import json
import hmac
import hashlib
import base64
import uuid
import argparse
import calendar
from datetime import datetime, date, timedelta, timezone

import requests
import psycopg2
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


def get_db_connection():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )


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

    return response.json()


def add_months(d: date, months: int) -> date:
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def iter_3_month_windows(start_date: date, end_date: date):
    current_start = start_date

    while current_start <= end_date:
        current_end = add_months(current_start, 3) - timedelta(days=1)

        if current_end > end_date:
            current_end = end_date

        yield current_start, current_end

        current_start = current_end + timedelta(days=1)


def merit_date(d: date) -> str:
    return d.strftime("%Y%m%d")


def make_payload(start_date: date, end_date: date):
    return {
        "PeriodStart": merit_date(start_date),
        "PeriodEnd": merit_date(end_date),
        "UnPaid": False,
        "DateType": 0,
    }


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
        ON CONFLICT (pih_id)
        DO UPDATE SET
            loaded_at = now(),
            batch_id = EXCLUDED.batch_id,
            changed_date = EXCLUDED.changed_date,
            raw_payload = EXCLUDED.raw_payload;
    """

    saved_count = 0

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for invoice in invoices:
                pih_id = invoice.get("PIHId")

                if not pih_id:
                    print("HOIATUS: ostuarvel puudub PIHId, jätan vahele")
                    continue

                cur.execute(
                    sql,
                    (
                        batch_id,
                        "merit",
                        "/api/v2/getpurchorders",
                        pih_id,
                        invoice.get("ChangedDate"),
                        Json(invoice),
                    ),
                )
                saved_count += 1

        conn.commit()

    return saved_count


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
        ON CONFLICT (sih_id)
        DO UPDATE SET
            loaded_at = now(),
            batch_id = EXCLUDED.batch_id,
            changed_date = EXCLUDED.changed_date,
            raw_payload = EXCLUDED.raw_payload;
    """

    saved_count = 0

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for invoice in invoices:
                sih_id = invoice.get("SIHId")

                if not sih_id:
                    print("HOIATUS: müügiarvel puudub SIHId, jätan vahele")
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
            batch_id = EXCLUDED.batch_id,
            changed_date = EXCLUDED.changed_date,
            raw_payload = EXCLUDED.raw_payload;
    """

    saved_count = 0

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for payment in payments:
                payment_id = payment.get("PHId")

                if not payment_id:
                    print("HOIATUS: maksel/laekumisel puudub PHId, jätan vahele")
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


def load_window(start_date: date, end_date: date):
    batch_id = str(uuid.uuid4())
    payload = make_payload(start_date, end_date)

    print("")
    print("=" * 80)
    print(f"Laen Meriti akent: {start_date} kuni {end_date}")
    print(f"batch_id: {batch_id}")
    print("=" * 80)

    print("Küsin ostuarveid...")
    purchase_invoices = merit_post("/api/v2/getpurchorders", payload)
    saved_purchase = save_purchase_invoices(purchase_invoices, batch_id)
    print(f"Ostuarveid API-st: {len(purchase_invoices)}, salvestatud/uuendatud: {saved_purchase}")

    print("Küsin müügiarveid...")
    sales_invoices = merit_post("/api/v2/getinvoices", payload)
    saved_sales = save_sales_invoices(sales_invoices, batch_id)
    print(f"Müügiarveid API-st: {len(sales_invoices)}, salvestatud/uuendatud: {saved_sales}")

    print("Küsin makseid/laekumisi...")
    payments = merit_post("/api/v2/getpayments", payload)
    saved_payments = save_payments(payments, batch_id)
    print(f"Makseid/laekumisi API-st: {len(payments)}, salvestatud/uuendatud: {saved_payments}")

    return {
        "purchase_invoices": saved_purchase,
        "sales_invoices": saved_sales,
        "payments": saved_payments,
    }


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def main():
    parser = argparse.ArgumentParser(description="Lae Meriti ajalugu staging tabelitesse 3 kuu akendena.")
    parser.add_argument("--start-date", required=True, help="Alguskuupäev kujul YYYY-MM-DD")
    parser.add_argument("--end-date", default=date.today().isoformat(), help="Lõppkuupäev kujul YYYY-MM-DD")
    args = parser.parse_args()

    start_date = parse_date(args.start_date)
    end_date = parse_date(args.end_date)

    if start_date > end_date:
        raise RuntimeError("start-date ei tohi olla hilisem kui end-date")

    total_purchase = 0
    total_sales = 0
    total_payments = 0

    for window_start, window_end in iter_3_month_windows(start_date, end_date):
        result = load_window(window_start, window_end)

        total_purchase += result["purchase_invoices"]
        total_sales += result["sales_invoices"]
        total_payments += result["payments"]

    print("")
    print("=" * 80)
    print("Meriti backfill valmis.")
    print(f"Ostuarved kokku salvestatud/uuendatud: {total_purchase}")
    print(f"Müügiarved kokku salvestatud/uuendatud: {total_sales}")
    print(f"Maksed/laekumised kokku salvestatud/uuendatud: {total_payments}")
    print("=" * 80)


if __name__ == "__main__":
    main()