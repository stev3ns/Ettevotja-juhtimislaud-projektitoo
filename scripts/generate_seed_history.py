from pathlib import Path
from datetime import date, timedelta
import random
import pandas as pd

# ---------------------------------------
# 1. Üldseadistus
# ---------------------------------------

random.seed(42)

OUTPUT_DIR = Path("data/synthetic/source")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VAT_RATE = 0.24
START_CASH = 35000

START_YEAR = 2024
MONTHS = range(1, 13)

# ---------------------------------------
# 2. Ettevõtte põhiandmed
# ---------------------------------------

company = [
    {
        "company_id": "demo_haldus",
        "company_name": "DemoHaldus OÜ",
        "registry_code": "90000001",
        "industry": "Kinnisvara haldus",
        "county": "Harjumaa",
        "vat_registered": True,
        "starting_cash_balance": START_CASH,
        "credit_limit": 20000,
    }
]

# ---------------------------------------
# 3. Kliendid
# ---------------------------------------

customers = [
    {
        "customer_id": "C001",
        "customer_name": "KÜ Tamme 12",
        "payment_terms_days": 14,
        "average_delay_days": 3,
        "monthly_fee": 1200,
    },
    {
        "customer_id": "C002",
        "customer_name": "KÜ Pargi 8",
        "payment_terms_days": 14,
        "average_delay_days": 7,
        "monthly_fee": 1500,
    },
    {
        "customer_id": "C003",
        "customer_name": "Ärimaja Keskus OÜ",
        "payment_terms_days": 30,
        "average_delay_days": 18,
        "monthly_fee": 2800,
    },
    {
        "customer_id": "C004",
        "customer_name": "KÜ Metsa 5",
        "payment_terms_days": 14,
        "average_delay_days": 2,
        "monthly_fee": 950,
    },
]

# ---------------------------------------
# 4. Tarnijad
# ---------------------------------------

suppliers = [
    {
        "supplier_id": "S001",
        "supplier_name": "Remondipartner OÜ",
        "category": "repair",
        "payment_terms_days": 14,
        "critical_supplier": True,
    },
    {
        "supplier_id": "S002",
        "supplier_name": "Puhastuspartner OÜ",
        "category": "cleaning",
        "payment_terms_days": 14,
        "critical_supplier": True,
    },
    {
        "supplier_id": "S003",
        "supplier_name": "Tarkvara OÜ",
        "category": "software",
        "payment_terms_days": 30,
        "critical_supplier": False,
    },
    {
        "supplier_id": "S004",
        "supplier_name": "Kontorikulud OÜ",
        "category": "office",
        "payment_terms_days": 30,
        "critical_supplier": False,
    },
]

# ---------------------------------------
# 5. Tühjad tabelid
# ---------------------------------------

sales_invoices = []
sales_payments = []
purchase_invoices = []
purchase_payments = []
bank_transactions = []
payroll_obligations = []
vat_obligations = []

bank_balance = START_CASH

sales_counter = 1
purchase_counter = 1
bank_counter = 1

# ---------------------------------------
# 6. Aasta kuude kaupa genereerimine
# ---------------------------------------

for month in MONTHS:
    year = START_YEAR
    month_start = date(year, month, 1)

    monthly_sales_vat = 0
    monthly_purchase_vat = 0

    # -----------------------------------
    # 6.1 Müügiarved klientidele
    # -----------------------------------

    for customer in customers:
        invoice_date = month_start
        due_date = invoice_date + timedelta(days=customer["payment_terms_days"])

        net_amount = round(customer["monthly_fee"] * random.uniform(0.95, 1.10), 2)

        # Mõnikord tekib lisatöö
        if random.random() < 0.25:
            net_amount += round(random.uniform(500, 2500), 2)

        vat_amount = round(net_amount * VAT_RATE, 2)
        gross_amount = round(net_amount + vat_amount, 2)

        monthly_sales_vat += vat_amount

        invoice_id = f"SI-{year}{month:02d}-{sales_counter:04d}"

        delay_days = max(0, int(random.gauss(customer["average_delay_days"], 3)))
        payment_date = due_date + timedelta(days=delay_days)

        sales_invoices.append(
            {
                "invoice_id": invoice_id,
                "customer_id": customer["customer_id"],
                "invoice_date": invoice_date,
                "due_date": due_date,
                "net_amount": net_amount,
                "vat_amount": vat_amount,
                "gross_amount": gross_amount,
                "status": "paid",
            }
        )

        sales_payments.append(
            {
                "payment_id": f"SP-{year}{month:02d}-{sales_counter:04d}",
                "invoice_id": invoice_id,
                "payment_date": payment_date,
                "amount": gross_amount,
            }
        )

        bank_balance += gross_amount

        bank_transactions.append(
            {
                "transaction_id": f"BT-{bank_counter:06d}",
                "transaction_date": payment_date,
                "type": "inflow",
                "counterparty": customer["customer_name"],
                "description": f"Müügiarve {invoice_id} laekumine",
                "amount": gross_amount,
                "balance_after": round(bank_balance, 2),
                "linked_invoice_id": invoice_id,
            }
        )

        sales_counter += 1
        bank_counter += 1

    # -----------------------------------
    # 6.2 Ostuarved tarnijatelt
    # -----------------------------------

    for supplier in suppliers:
        purchase_date = date(year, month, random.randint(3, 12))
        due_date = purchase_date + timedelta(days=supplier["payment_terms_days"])

        if supplier["category"] == "repair":
            net_amount = round(random.uniform(800, 3500), 2)
        elif supplier["category"] == "cleaning":
            net_amount = round(random.uniform(900, 1800), 2)
        elif supplier["category"] == "software":
            net_amount = round(random.uniform(250, 600), 2)
        else:
            net_amount = round(random.uniform(200, 900), 2)

        vat_amount = round(net_amount * VAT_RATE, 2)
        gross_amount = round(net_amount + vat_amount, 2)

        monthly_purchase_vat += vat_amount

        invoice_id = f"PI-{year}{month:02d}-{purchase_counter:04d}"

        purchase_invoices.append(
            {
                "invoice_id": invoice_id,
                "supplier_id": supplier["supplier_id"],
                "invoice_date": purchase_date,
                "due_date": due_date,
                "category": supplier["category"],
                "net_amount": net_amount,
                "vat_amount": vat_amount,
                "gross_amount": gross_amount,
                "status": "paid",
                "must_pay_on_time": supplier["critical_supplier"],
            }
        )

        purchase_payments.append(
            {
                "payment_id": f"PP-{year}{month:02d}-{purchase_counter:04d}",
                "invoice_id": invoice_id,
                "payment_date": due_date,
                "amount": gross_amount,
            }
        )

        bank_balance -= gross_amount

        bank_transactions.append(
            {
                "transaction_id": f"BT-{bank_counter:06d}",
                "transaction_date": due_date,
                "type": "outflow",
                "counterparty": supplier["supplier_name"],
                "description": f"Ostuarve {invoice_id} tasumine",
                "amount": -gross_amount,
                "balance_after": round(bank_balance, 2),
                "linked_invoice_id": invoice_id,
            }
        )

        purchase_counter += 1
        bank_counter += 1

    # -----------------------------------
    # 6.3 Palgad ja tööjõumaksud
    # -----------------------------------

    payroll_payment_date = date(year, month, 5)

    gross_salary = 14000
    net_salary = round(gross_salary * 0.78, 2)
    payroll_taxes = round(gross_salary * 0.34, 2)
    total_cash_out = round(net_salary + payroll_taxes, 2)

    payroll_obligations.append(
        {
            "period": f"{year}-{month:02d}",
            "payment_date": payroll_payment_date,
            "gross_salary": gross_salary,
            "net_salary": net_salary,
            "payroll_taxes": payroll_taxes,
            "total_cash_out": total_cash_out,
            "must_pay_on_time": True,
            "status": "paid",
        }
    )

    bank_balance -= total_cash_out

    bank_transactions.append(
        {
            "transaction_id": f"BT-{bank_counter:06d}",
            "transaction_date": payroll_payment_date,
            "type": "outflow",
            "counterparty": "Töötajad ja Maksu- ja Tolliamet",
            "description": f"Palk ja tööjõumaksud {year}-{month:02d}",
            "amount": -total_cash_out,
            "balance_after": round(bank_balance, 2),
            "linked_invoice_id": "",
        }
    )

    bank_counter += 1

    # -----------------------------------
    # 6.4 Käibemaks
    # -----------------------------------

    vat_payable = round(monthly_sales_vat - monthly_purchase_vat, 2)

    if month == 12:
        vat_due_date = date(year + 1, 1, 20)
    else:
        vat_due_date = date(year, month + 1, 20)

    vat_obligations.append(
        {
            "period": f"{year}-{month:02d}",
            "sales_vat": round(monthly_sales_vat, 2),
            "purchase_vat": round(monthly_purchase_vat, 2),
            "vat_payable": vat_payable,
            "due_date": vat_due_date,
            "status": "paid",
            "must_pay_on_time": True,
        }
    )

    if vat_payable > 0:
        bank_balance -= vat_payable

        bank_transactions.append(
            {
                "transaction_id": f"BT-{bank_counter:06d}",
                "transaction_date": vat_due_date,
                "type": "outflow",
                "counterparty": "Maksu- ja Tolliamet",
                "description": f"Käibemaks {year}-{month:02d}",
                "amount": -vat_payable,
                "balance_after": round(bank_balance, 2),
                "linked_invoice_id": "",
            }
        )

        bank_counter += 1

# ---------------------------------------
# 7. Oma aastaaruande näidis
# ---------------------------------------

own_annual_reports = [
    {
        "company_id": "demo_haldus",
        "report_year": 2022,
        "revenue": 320000,
        "profit": 14500,
        "assets": 120000,
        "liabilities": 72000,
        "equity": 48000,
        "cash": 18000,
        "employees": 6,
    },
    {
        "company_id": "demo_haldus",
        "report_year": 2023,
        "revenue": 370000,
        "profit": 19000,
        "assets": 150000,
        "liabilities": 89000,
        "equity": 61000,
        "cash": 26000,
        "employees": 7,
    },
    {
        "company_id": "demo_haldus",
        "report_year": 2024,
        "revenue": 420000,
        "profit": 23500,
        "assets": 195000,
        "liabilities": 115000,
        "equity": 80000,
        "cash": 48500,
        "employees": 8,
    },
]

# ---------------------------------------
# 8. CSV-failide salvestamine
# ---------------------------------------

pd.DataFrame(company).to_csv(OUTPUT_DIR / "company.csv", index=False)
pd.DataFrame(customers).to_csv(OUTPUT_DIR / "customers.csv", index=False)
pd.DataFrame(suppliers).to_csv(OUTPUT_DIR / "suppliers.csv", index=False)
pd.DataFrame(sales_invoices).to_csv(OUTPUT_DIR / "sales_invoices.csv", index=False)
pd.DataFrame(sales_payments).to_csv(OUTPUT_DIR / "sales_payments.csv", index=False)
pd.DataFrame(purchase_invoices).to_csv(OUTPUT_DIR / "purchase_invoices.csv", index=False)
pd.DataFrame(purchase_payments).to_csv(OUTPUT_DIR / "purchase_payments.csv", index=False)
pd.DataFrame(bank_transactions).to_csv(OUTPUT_DIR / "bank_transactions.csv", index=False)
pd.DataFrame(payroll_obligations).to_csv(OUTPUT_DIR / "payroll_obligations.csv", index=False)
pd.DataFrame(vat_obligations).to_csv(OUTPUT_DIR / "vat_obligations.csv", index=False)
pd.DataFrame(own_annual_reports).to_csv(OUTPUT_DIR / "own_annual_reports.csv", index=False)

print("Sünteetilise ettevõtte täielikum andmestik loodud.")
print(f"Lõplik pangajääk: {round(bank_balance, 2)} €")
print(f"Failid asuvad kaustas: {OUTPUT_DIR}")