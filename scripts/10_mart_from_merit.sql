CREATE SCHEMA IF NOT EXISTS mart;

CREATE OR REPLACE VIEW mart.merit_sales_invoices AS
WITH latest AS (
    SELECT DISTINCT ON (sih_id)
        sih_id,
        batch_id,
        loaded_at,
        changed_date,
        raw_payload
    FROM staging.merit_sales_invoices_raw
    ORDER BY sih_id, loaded_at DESC, batch_id DESC
)
SELECT
    l.sih_id AS invoice_id,
    l.batch_id,
    l.loaded_at,
    l.changed_date,
    COALESCE(
        l.raw_payload ->> 'InvoiceNo',
        l.raw_payload ->> 'InvNo',
        l.raw_payload ->> 'DocNo',
        l.raw_payload ->> 'Number'
    ) AS invoice_no,
    mart.parse_date(
        COALESCE(
            l.raw_payload ->> 'InvoiceDate',
            l.raw_payload ->> 'InvDate',
            l.raw_payload ->> 'Date',
            l.raw_payload ->> 'DocDate'
        )
    ) AS invoice_date,
    mart.parse_date(
        COALESCE(
            l.raw_payload ->> 'DueDate',
            l.raw_payload ->> 'PaymentDueDate'
        )
    ) AS due_date,
    COALESCE(
        l.raw_payload ->> 'CustomerId',
        l.raw_payload ->> 'ClientId',
        l.raw_payload ->> 'Customer'
    ) AS customer_id,
    COALESCE(
        l.raw_payload ->> 'CustomerName',
        l.raw_payload ->> 'Name'
    ) AS customer_name,
    mart.parse_numeric(
        COALESCE(
            l.raw_payload ->> 'TotalNoTax',
            l.raw_payload ->> 'Sum',
            l.raw_payload ->> 'Total'
        )
    ) AS amount_without_tax_eur,
    mart.parse_numeric(
        COALESCE(
            l.raw_payload ->> 'VATSum',
            l.raw_payload ->> 'VatSum',
            l.raw_payload ->> 'TaxAmount',
            l.raw_payload ->> 'VAT'
        )
    ) AS vat_amount_eur,
    COALESCE(
        mart.parse_numeric(
            COALESCE(
                l.raw_payload ->> 'TotalAmount',
                l.raw_payload ->> 'Amount',
                l.raw_payload ->> 'TotalAmountWithTax'
            )
        ),
        COALESCE(
            mart.parse_numeric(COALESCE(l.raw_payload ->> 'TotalNoTax', l.raw_payload ->> 'Sum', l.raw_payload ->> 'Total')),
            0
        ) + COALESCE(
            mart.parse_numeric(COALESCE(l.raw_payload ->> 'VATSum', l.raw_payload ->> 'VatSum', l.raw_payload ->> 'TaxAmount', l.raw_payload ->> 'VAT')),
            0
        )
    ) AS amount_with_tax_eur,
    COALESCE(l.raw_payload ->> 'CurrencyCode', l.raw_payload ->> 'Currency', 'EUR') AS currency_code,
    COALESCE(l.raw_payload ->> 'Status', l.raw_payload ->> 'InvoiceStatus') AS invoice_status,
    mart.parse_numeric(
        COALESCE(
            l.raw_payload ->> 'Balance',
            l.raw_payload ->> 'ToPay',
            l.raw_payload ->> 'Debt'
        )
    ) AS outstanding_amount_eur,
    l.raw_payload
FROM latest l;

CREATE OR REPLACE VIEW mart.merit_purchase_invoices AS
WITH latest AS (
    SELECT DISTINCT ON (pih_id)
        pih_id,
        batch_id,
        loaded_at,
        changed_date,
        raw_payload
    FROM staging.merit_purchase_invoices_raw
    ORDER BY pih_id, loaded_at DESC, batch_id DESC
)
SELECT
    l.pih_id AS invoice_id,
    l.batch_id,
    l.loaded_at,
    l.changed_date,
    COALESCE(
        l.raw_payload ->> 'InvoiceNo',
        l.raw_payload ->> 'InvNo',
        l.raw_payload ->> 'DocNo',
        l.raw_payload ->> 'Number'
    ) AS invoice_no,
    mart.parse_date(
        COALESCE(
            l.raw_payload ->> 'InvoiceDate',
            l.raw_payload ->> 'InvDate',
            l.raw_payload ->> 'Date',
            l.raw_payload ->> 'DocDate'
        )
    ) AS invoice_date,
    mart.parse_date(
        COALESCE(
            l.raw_payload ->> 'DueDate',
            l.raw_payload ->> 'PaymentDueDate'
        )
    ) AS due_date,
    COALESCE(
        l.raw_payload ->> 'VendorId',
        l.raw_payload ->> 'SupplierId',
        l.raw_payload ->> 'Vendor'
    ) AS vendor_id,
    COALESCE(
        l.raw_payload ->> 'VendorName',
        l.raw_payload ->> 'SupplierName',
        l.raw_payload ->> 'Name'
    ) AS vendor_name,
    mart.parse_numeric(
        COALESCE(
            l.raw_payload ->> 'TotalNoTax',
            l.raw_payload ->> 'Sum',
            l.raw_payload ->> 'Total'
        )
    ) AS amount_without_tax_eur,
    mart.parse_numeric(
        COALESCE(
            l.raw_payload ->> 'VATSum',
            l.raw_payload ->> 'VatSum',
            l.raw_payload ->> 'TaxAmount',
            l.raw_payload ->> 'VAT'
        )
    ) AS vat_amount_eur,
    COALESCE(
        mart.parse_numeric(
            COALESCE(
                l.raw_payload ->> 'TotalAmount',
                l.raw_payload ->> 'Amount',
                l.raw_payload ->> 'TotalAmountWithTax'
            )
        ),
        COALESCE(
            mart.parse_numeric(COALESCE(l.raw_payload ->> 'TotalNoTax', l.raw_payload ->> 'Sum', l.raw_payload ->> 'Total')),
            0
        ) + COALESCE(
            mart.parse_numeric(COALESCE(l.raw_payload ->> 'VATSum', l.raw_payload ->> 'VatSum', l.raw_payload ->> 'TaxAmount', l.raw_payload ->> 'VAT')),
            0
        )
    ) AS amount_with_tax_eur,
    COALESCE(l.raw_payload ->> 'CurrencyCode', l.raw_payload ->> 'Currency', 'EUR') AS currency_code,
    COALESCE(l.raw_payload ->> 'Status', l.raw_payload ->> 'InvoiceStatus') AS invoice_status,
    mart.parse_numeric(
        COALESCE(
            l.raw_payload ->> 'Balance',
            l.raw_payload ->> 'ToPay',
            l.raw_payload ->> 'Debt'
        )
    ) AS outstanding_amount_eur,
    l.raw_payload
FROM latest l;

CREATE OR REPLACE VIEW mart.merit_payments AS
WITH latest AS (
    SELECT DISTINCT ON (payment_id)
        payment_id,
        batch_id,
        loaded_at,
        changed_date,
        raw_payload
    FROM staging.merit_payments_raw
    ORDER BY payment_id, loaded_at DESC, batch_id DESC
)
SELECT
    l.payment_id,
    l.batch_id,
    l.loaded_at,
    l.changed_date,
    mart.parse_date(
        COALESCE(
            l.raw_payload ->> 'PaymentDate',
            l.raw_payload ->> 'Date',
            l.raw_payload ->> 'DocDate'
        )
    ) AS payment_date,
    COALESCE(
        l.raw_payload ->> 'CustomerId',
        l.raw_payload ->> 'VendorId',
        l.raw_payload ->> 'PartnerId'
    ) AS partner_id,
    COALESCE(
        l.raw_payload ->> 'CustomerName',
        l.raw_payload ->> 'VendorName',
        l.raw_payload ->> 'PartnerName'
    ) AS partner_name,
    COALESCE(l.raw_payload ->> 'Type', l.raw_payload ->> 'PaymentType') AS payment_type,
    mart.parse_numeric(
        COALESCE(
            l.raw_payload ->> 'Amount',
            l.raw_payload ->> 'Sum',
            l.raw_payload ->> 'PaidAmount'
        )
    ) AS amount_eur,
    COALESCE(l.raw_payload ->> 'CurrencyCode', l.raw_payload ->> 'Currency', 'EUR') AS currency_code,
    l.raw_payload
FROM latest l;

CREATE OR REPLACE VIEW mart.merit_customers AS
WITH latest AS (
    SELECT DISTINCT ON (customer_id)
        customer_id,
        reg_no,
        batch_id,
        loaded_at,
        changed_date,
        raw_payload
    FROM staging.merit_customers_raw
    ORDER BY customer_id, loaded_at DESC, batch_id DESC
)
SELECT
    customer_id,
    reg_no,
    batch_id,
    loaded_at,
    changed_date,
    COALESCE(raw_payload ->> 'Name', raw_payload ->> 'CustomerName') AS customer_name,
    raw_payload
FROM latest;

CREATE OR REPLACE VIEW mart.merit_vendors AS
WITH latest AS (
    SELECT DISTINCT ON (vendor_id)
        vendor_id,
        reg_no,
        batch_id,
        loaded_at,
        changed_date,
        raw_payload
    FROM staging.merit_vendors_raw
    ORDER BY vendor_id, loaded_at DESC, batch_id DESC
)
SELECT
    vendor_id,
    reg_no,
    batch_id,
    loaded_at,
    changed_date,
    COALESCE(raw_payload ->> 'Name', raw_payload ->> 'VendorName') AS vendor_name,
    raw_payload
FROM latest;
