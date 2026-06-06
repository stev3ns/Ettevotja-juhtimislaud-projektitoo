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

SCRIPT_DIR = Path(__file__).resolve().parent

SQL_FILES = [
    "01_create_staging_merit.sql",
    "02_create_staging_emta.sql",
    "08_create_mart_schema.sql",
]


def get_db_connection():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )


def execute_sql_file(conn, sql_file):
    sql_path = SCRIPT_DIR / sql_file
    sql_text = sql_path.read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(sql_text)
    conn.commit()
    print(f"OK: {sql_file}")


def main():
    print("Ühendan andmebaasiga...")
    conn = get_db_connection()
    print("Ühendus õnnestus.\n")
    for sql_file in SQL_FILES:
        print(f"Käivitan: {sql_file}")
        execute_sql_file(conn, sql_file)
    conn.close()
    print("\nAndmebaas initsialiseeritud.")


if __name__ == "__main__":
    main()
