import os
import hashlib
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv(override=True)

RAW_DIR = Path("data/raw/emta")
RAW_DIR.mkdir(parents=True, exist_ok=True)

DATASETS = {
    "tax_debt": os.getenv("EMTA_TAX_DEBT_URL"),
    "paid_taxes": os.getenv("EMTA_PAID_TAXES_URL"),
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)

    return h.hexdigest()


def download_file(dataset_name: str, url: str) -> None:
    if not url:
        print(f"Jätan vahele: {dataset_name}, URL puudub .env failist")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    out_path = RAW_DIR / f"{dataset_name}_{today}.csv"

    print(f"Laen alla: {dataset_name}")
    print(f"URL: {url}")

    response = requests.get(url, timeout=120)
    response.raise_for_status()

    out_path.write_bytes(response.content)

    file_hash = sha256_file(out_path)

    print(f"Salvestatud: {out_path}")
    print(f"Suurus: {out_path.stat().st_size} baiti")
    print(f"SHA256: {file_hash}")
    print("-" * 60)


def main() -> None:
    for dataset_name, url in DATASETS.items():
        download_file(dataset_name, url)


if __name__ == "__main__":
    main()