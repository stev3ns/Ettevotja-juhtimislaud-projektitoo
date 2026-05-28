import os
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

import psycopg2
import streamlit as st
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

PIPELINE_LOG = LOG_DIR / "emta_admin.log"

load_dotenv(PROJECT_ROOT / ".env", override=True)


def get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or str(value).strip() == "":
        raise RuntimeError(f"Puudub keskkonnamuutuja: {name}")
    return str(value).strip()


def get_db_connection():
    return psycopg2.connect(
        host=get_env("POSTGRES_HOST", "localhost"),
        port=get_env("POSTGRES_PORT", "55432"),
        dbname=get_env("POSTGRES_DB", "juhtimislaud"),
        user=get_env("POSTGRES_USER", "praktikum"),
        password=get_env("POSTGRES_PASSWORD", "praktikum"),
    )


def query_one(sql: str):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchone()[0]


def get_table_count(table_name: str) -> int:
    return query_one(f"SELECT COUNT(*) FROM {table_name};")


def get_latest_loaded_at(table_name: str):
    return query_one(f"SELECT MAX(loaded_at) FROM {table_name};")


def format_dt(value) -> str:
    if value is None:
        return "puudub"
    return str(value).split(".")[0]

def clear_merit_staging():
    sql = """
        TRUNCATE TABLE
            staging.merit_purchase_invoices_raw,
            staging.merit_sales_invoices_raw,
            staging.merit_payments_raw,
            staging.merit_customers_raw,
            staging.merit_vendors_raw;
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)


def get_merit_counts():
    sql = """
        SELECT 'Ostuarved' AS name, COUNT(*) AS row_count
        FROM staging.merit_purchase_invoices_raw

        UNION ALL

        SELECT 'Müügiarved', COUNT(*)
        FROM staging.merit_sales_invoices_raw

        UNION ALL

        SELECT 'Maksed/laekumised', COUNT(*)
        FROM staging.merit_payments_raw

        UNION ALL

        SELECT 'Kliendid', COUNT(*)
        FROM staging.merit_customers_raw

        UNION ALL

        SELECT 'Tarnijad', COUNT(*)
        FROM staging.merit_vendors_raw;
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()

def run_command(command: list[str]) -> tuple[int, str]:
    started_at = datetime.now().isoformat(timespec="seconds")

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        shell=False,
    )

    finished_at = datetime.now().isoformat(timespec="seconds")
    output = result.stdout + "\n" + result.stderr

    log_text = (
        f"\n\n===== START {started_at} =====\n"
        f"COMMAND: {' '.join(command)}\n"
        f"RETURN CODE: {result.returncode}\n"
        f"----- OUTPUT -----\n{output}\n"
        f"===== END {finished_at} =====\n"
    )

    old_log = PIPELINE_LOG.read_text(encoding="utf-8") if PIPELINE_LOG.exists() else ""
    PIPELINE_LOG.write_text(old_log + log_text, encoding="utf-8")

    return result.returncode, output


st.set_page_config(
    page_title="EMTA andmete haldus",
    layout="wide",
)

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }

        h1, h2, h3 {
            margin-top: 0.3rem;
            margin-bottom: 0.3rem;
        }

        [data-testid="stMetric"] {
            background-color: #f8f9fa;
            padding: 0.4rem 0.6rem;
            border-radius: 0.6rem;
            border: 1px solid #e5e7eb;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.75rem;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.25rem;
        }

        div[data-testid="stVerticalBlock"] {
            gap: 0.4rem;
        }

        hr {
            margin-top: 0.7rem;
            margin-bottom: 0.7rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("## EMTA andmete haldus")
st.caption("MVP admin-vaade EMTA andmete uuendamiseks ja stagingu kontrollimiseks.")

st.divider()

st.subheader("Andmete seis")

try:
    tax_debt_count = get_table_count("staging.emta_tax_debt_raw")
    paid_taxes_count = get_table_count("staging.emta_paid_taxes_raw")

    tax_debt_latest = get_latest_loaded_at("staging.emta_tax_debt_raw")
    paid_taxes_latest = get_latest_loaded_at("staging.emta_paid_taxes_raw")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Maksuvõlgade ridu", f"{tax_debt_count:,}".replace(",", " "))

    with col2:
        st.metric("Käibe/töötajate ridu", f"{paid_taxes_count:,}".replace(",", " "))

    with col3:
        st.metric("Maksuvõlgade viimane laadimine", format_dt(tax_debt_latest))

    with col4:
        st.metric("Käibe/töötajate viimane laadimine", format_dt(paid_taxes_latest))

except Exception as e:
    st.error("Andmebaasi seisu lugemine ebaõnnestus.")
    st.code(str(e))

st.divider()

st.markdown("### Käsitsi käivitused")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Maksuvõlglaste nimekiri")
    st.write("Igapäevane andmestik")

    if st.button("Uuenda EMTA maksuvõlad", use_container_width=True):
        with st.spinner("Uuendan EMTA maksuvõlgade andmeid..."):
            code, output = run_command(
                [sys.executable, "scripts/run_emta_tax_debt_pipeline.py"]
            )

        if code == 0:
            st.success("Maksuvõlgade uuendus õnnestus.")
        else:
            st.error("Maksuvõlgade uuendus ebaõnnestus.")

        with st.expander("Vaata tehnilist väljundit"):
            st.code(output[-4000:])
       

with col2:
    st.markdown("### Tasutud maksud, käive ja töötajad")
    st.write("Kvartali andmestik")

    if st.button("Uuenda EMTA käive/töötajad", use_container_width=True):
        with st.spinner("Uuendan EMTA käibe/töötajate andmeid..."):
            code, output = run_command(
                [sys.executable, "scripts/run_emta_paid_taxes_pipeline.py"]
            )

        if code == 0:
            st.success("Käibe/töötajate uuendus õnnestus.")
        else:
            st.error("Käibe/töötajate uuendus ebaõnnestus.")

        with st.expander("Vaata tehnilist väljundit"):
            st.code(output[-4000:])

st.divider()

st.divider()

st.markdown("### Merit ajaloo laadimine")
st.caption(
    "Laeb Merit API-st ostuarved, müügiarved ja maksed/laekumised staging-tabelitesse."
)

try:
    merit_counts = get_merit_counts()
    merit_cols = st.columns(len(merit_counts))

    for col, (name, row_count) in zip(merit_cols, merit_counts):
        with col:
            st.metric(name, f"{row_count:,}".replace(",", " "))

except Exception as e:
    st.warning("Meriti staging seisu lugemine ebaõnnestus.")
    st.code(str(e))

col1, col2 = st.columns(2)

with col1:
    merit_start_date = st.date_input(
        "Merit alguskuupäev",
        value=date(2025, 1, 1),
        key="merit_backfill_start_date",
    )

with col2:
    merit_end_date = st.date_input(
        "Merit lõppkuupäev",
        value=date.today(),
        key="merit_backfill_end_date",
    )

if st.button("Käivita Merit ajaloo laadimine", use_container_width=True):
    if merit_start_date > merit_end_date:
        st.error("Alguskuupäev ei tohi olla hilisem kui lõppkuupäev.")
    else:
        with st.spinner("Meriti ajaloo laadimine käib..."):
            code, output = run_command(
                [
                    sys.executable,
                    "scripts/run_merit_backfill.py",
                    "--start-date",
                    merit_start_date.isoformat(),
                    "--end-date",
                    merit_end_date.isoformat(),
                ]
            )

        if code == 0:
            st.success("Meriti ajaloo laadimine õnnestus.")
        else:
            st.error("Meriti ajaloo laadimine ebaõnnestus.")

        with st.expander("Vaata tehnilist väljundit"):
            st.code(output[-4000:])


st.markdown("#### Ohtlik tegevus")

st.warning(
    "See kustutab Meriti staging-tabelite sisu, kuid jätab tabelid alles. "
    "Kasuta ainult arenduses või enne uut täielikku ajaloo laadimist."
)

confirm_delete_merit = st.checkbox(
    "Kinnitan, et soovin Meriti staging ajaloo kustutada",
    key="confirm_delete_merit_history",
)

if st.button(
    "Kustuta Merit staging ajalugu",
    use_container_width=True,
    disabled=not confirm_delete_merit,
):
    with st.spinner("Kustutan Meriti staging andmeid..."):
        try:
            clear_merit_staging()
            st.success("Meriti staging ajalugu kustutati.")
        except Exception as e:
            st.error("Meriti staging ajaloo kustutamine ebaõnnestus.")
            st.code(str(e))

st.markdown("### Viimane logi")

with st.expander("Viimane tehniline logi"):
    if PIPELINE_LOG.exists():
        log_text = PIPELINE_LOG.read_text(encoding="utf-8")
        st.text_area("logs/emta_admin.log", log_text[-8000:], height=260)
    else:
        st.info("Logifaili veel ei ole.")