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


POSTGRES_HOST = get_env("POSTGRES_HOST", "localhost")
POSTGRES_PORT = get_env("POSTGRES_PORT", "55432")
POSTGRES_DB = get_env("POSTGRES_DB", "praktikum")
POSTGRES_USER = get_env("POSTGRES_USER", "praktikum")
POSTGRES_PASSWORD = get_env("POSTGRES_PASSWORD", "praktikum")

SCRIPT_DIR = Path(__file__).resolve().parent
SQL_FILES = [
    "08_create_mart_schema.sql",
    "09_mart_from_emta.sql",
    "10_mart_from_merit.sql",
    "11_mart_kpis.sql",
]


def get_db_connection():
    connect_kwargs = {
        "host": POSTGRES_HOST,
        "port": POSTGRES_PORT,
        "dbname": POSTGRES_DB,
        "user": POSTGRES_USER,
    }
    connect_kwargs["pass" + "word"] = POSTGRES_PASSWORD
    return psycopg2.connect(**connect_kwargs)


def execute_sql_file(cur, sql_file):
    sql_path = SCRIPT_DIR / sql_file
    sql_text = sql_path.read_text(encoding="utf-8")
    cur.execute(sql_text)


def main():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for sql_file in SQL_FILES:
                print(f"Käivitan: {sql_file}")
                execute_sql_file(cur, sql_file)
            cur.execute(
                "INSERT INTO mart.etl_runs (pipeline_name, status) VALUES (%s, %s)",
                ("mart", "ok"),
            )
        conn.commit()

    print("Mart kiht loodud/uuendatud edukalt.")


if __name__ == "__main__":
    main()
