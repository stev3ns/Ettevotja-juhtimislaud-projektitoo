import csv
import io
import json
import os
import uuid
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


load_dotenv(override=True)

RAW_DIR = Path("data/raw/emta")


def get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or str(value).strip() == "":
        raise RuntimeError(f"Puudub keskkonnamuutuja: {name}")
    return str(value).strip()


POSTGRES_HOST = get_env("POSTGRES_HOST")
POSTGRES_PORT = get_env("POSTGRES_PORT")
POSTGRES_DB = get_env("POSTGRES_DB")
POSTGRES_USER = get_env("POSTGRES_USER")
POSTGRES_PASSWORD = get_env("POSTGRES_PASSWORD")


def get_db_connection():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )


def find_latest_file(pattern: str) -> Path:
    files = sorted(RAW_DIR.glob(pattern), reverse=True)

    if not files:
        raise FileNotFoundError(f"Ei leidnud faili mustriga: {pattern}")

    return files[0]


def detect_delimiter(file_path: Path) -> str:
    sample = file_path.read_text(encoding="utf-8-sig", errors="replace")[:5000]
    sniffer = csv.Sniffer()
    dialect = sniffer.sniff(sample, delimiters=";,")
    return dialect.delimiter


def load_csv_to_staging(
    file_path: Path,
    table_name: str,
    source_dataset: str,
    batch_id: str,
    delimiter: str = ";",
) -> int:
    row_count = 0
    buf = io.StringIO()

    with file_path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        for row_num, row in enumerate(reader, start=1):
            cleaned_row = {
                key.strip() if key else key: value.strip() if isinstance(value, str) else value
                for key, value in row.items()
            }
            payload = json.dumps(cleaned_row, ensure_ascii=False).replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")
            buf.write(f"{batch_id}\temta\t{source_dataset}\t{file_path}\t{row_num}\t{payload}\n")
            row_count += 1

    buf.seek(0)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            print(f"Puhastan tabeli: {table_name}")
            cur.execute(f"TRUNCATE TABLE {table_name};")
            cur.copy_expert(
                f"COPY {table_name} (batch_id, source_system, source_dataset, source_file, row_num, raw_payload) FROM STDIN",
                buf,
            )
        conn.commit()

    return row_count

def main():
    batch_id = str(uuid.uuid4())

    print(f"batch_id: {batch_id}")

    tax_debt_file = find_latest_file("tax_debt_*.csv")
    print(f"Laen stagingusse: {tax_debt_file}")

    tax_debt_rows = load_csv_to_staging(
        file_path=tax_debt_file,
        table_name="staging.emta_tax_debt_raw",
        source_dataset="emta_tax_debt",
        batch_id=batch_id,
    )

    print(f"Maksuvõlgade ridu laaditud: {tax_debt_rows}")

    paid_taxes_file = find_latest_file("paid_taxes_*.csv")
    print(f"Laen stagingusse: {paid_taxes_file}")

    paid_taxes_rows = load_csv_to_staging(
        file_path=paid_taxes_file,
        table_name="staging.emta_paid_taxes_raw",
        source_dataset="emta_paid_taxes",
        batch_id=batch_id,
    )

    print(f"Tasutud maksude ridu laaditud: {paid_taxes_rows}")

    print("EMTA staging laadimine valmis.")


if __name__ == "__main__":
    main()
