from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, Query

app = FastAPI(
    title="Fake Merit API",
    description="Sünteetilise ettevõtte Merit-laadne demo API",
    version="0.1.0",
)

DATA_DIR = Path("data/synthetic/source")
API_KEY = "demo-api-key"


def check_api_key(api_key: Optional[str]):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Vale või puuduv API võti")


def read_csv_file(filename: str) -> pd.DataFrame:
    file_path = DATA_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Faili ei leitud: {file_path}")

    return pd.read_csv(file_path, dtype=str, keep_default_na=False).fillna("")


@app.get("/")
def root():
    return {
        "message": "Fake Merit API töötab",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "source": "fake_merit_api",
        "data_dir": str(DATA_DIR),
    }


@app.get("/api/customers")
def get_customers(api_key: Optional[str] = Query(default=None)):
    check_api_key(api_key)
    df = read_csv_file("customers.csv")
    return df.to_dict(orient="records")


@app.get("/api/suppliers")
def get_suppliers(api_key: Optional[str] = Query(default=None)):
    check_api_key(api_key)
    df = read_csv_file("suppliers.csv")
    return df.to_dict(orient="records")


@app.get("/api/sales-invoices")
def get_sales_invoices(api_key: Optional[str] = Query(default=None)):
    check_api_key(api_key)
    df = read_csv_file("sales_invoices.csv")
    return df.to_dict(orient="records")


@app.get("/api/purchase-invoices")
def get_purchase_invoices(api_key: Optional[str] = Query(default=None)):
    check_api_key(api_key)
    df = read_csv_file("purchase_invoices.csv")
    return df.to_dict(orient="records")


@app.get("/api/bank-transactions")
def get_bank_transactions(api_key: Optional[str] = Query(default=None)):
    check_api_key(api_key)
    df = read_csv_file("bank_transactions.csv")
    return df.to_dict(orient="records")


@app.get("/api/payroll-obligations")
def get_payroll_obligations(api_key: Optional[str] = Query(default=None)):
    check_api_key(api_key)
    df = read_csv_file("payroll_obligations.csv")
    return df.to_dict(orient="records")


@app.get("/api/vat-obligations")
def get_vat_obligations(api_key: Optional[str] = Query(default=None)):
    check_api_key(api_key)
    df = read_csv_file("vat_obligations.csv")
    return df.to_dict(orient="records")

@app.get("/api/own-annual-reports")
def get_own_annual_reports(api_key: Optional[str] = Query(default=None)):
    check_api_key(api_key)
    df = read_csv_file("own_annual_reports.csv")
    df = df.fillna("").astype(str)
    return df.to_dict(orient="records")


@app.get("/api/sales-payments")
def get_sales_payments(api_key: Optional[str] = Query(default=None)):
    check_api_key(api_key)
    df = read_csv_file("sales_payments.csv")
    return df.to_dict(orient="records")


@app.get("/api/purchase-payments")
def get_purchase_payments(api_key: Optional[str] = Query(default=None)):
    check_api_key(api_key)
    df = read_csv_file("purchase_payments.csv")
    return df.to_dict(orient="records")

@app.get("/api/purchase-payments")
def get_purchase_payments(api_key: Optional[str] = Query(default=None)):
    check_api_key(api_key)
    df = read_csv_file("purchase_payments.csv")
    return df.to_dict(orient="records")