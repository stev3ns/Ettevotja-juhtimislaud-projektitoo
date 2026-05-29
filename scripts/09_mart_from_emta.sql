CREATE SCHEMA IF NOT EXISTS mart;

CREATE OR REPLACE VIEW mart.emta_tax_debt AS
SELECT
    t.batch_id,
    t.loaded_at,
    t.source_file,
    t.row_num,
    COALESCE(
        t.raw_payload ->> 'Registrikood',
        t.raw_payload ->> 'Reg.kood',
        t.raw_payload ->> 'Reg kood',
        t.raw_payload ->> 'Maksukohustuslase registrikood',
        t.raw_payload ->> 'Maksukohustuslase registrikood või isikukood',
        t.raw_payload ->> 'RegNo'
    ) AS reg_code,
    COALESCE(
        t.raw_payload ->> 'Nimi',
        t.raw_payload ->> 'Maksukohustuslase nimi',
        t.raw_payload ->> 'Name'
    ) AS company_name,
    mart.parse_numeric(
        COALESCE(
            t.raw_payload ->> 'Maksuvõlg',
            t.raw_payload ->> 'Maksuvõlg (eur)',
            t.raw_payload ->> 'Maksuvõlg EUR',
            t.raw_payload ->> 'Maksuvõla summa',
            t.raw_payload ->> 'TaxDebt'
        )
    ) AS tax_debt_eur,
    mart.parse_date(
        COALESCE(
            t.raw_payload ->> 'Seisuga',
            t.raw_payload ->> 'Seis',
            t.raw_payload ->> 'Kuupäev',
            t.raw_payload ->> 'Date'
        )
    ) AS debt_as_of_date,
    t.raw_payload
FROM staging.emta_tax_debt_raw t;

CREATE OR REPLACE VIEW mart.emta_paid_taxes AS
SELECT
    t.batch_id,
    t.loaded_at,
    t.source_file,
    t.row_num,
    COALESCE(
        t.raw_payload ->> 'Registrikood',
        t.raw_payload ->> 'Reg.kood',
        t.raw_payload ->> 'Reg kood',
        t.raw_payload ->> 'Maksukohustuslase registrikood',
        t.raw_payload ->> 'Maksukohustuslase registrikood või isikukood',
        t.raw_payload ->> 'RegNo'
    ) AS reg_code,
    COALESCE(
        t.raw_payload ->> 'Nimi',
        t.raw_payload ->> 'Maksukohustuslase nimi',
        t.raw_payload ->> 'Name'
    ) AS company_name,
    mart.parse_numeric(
        COALESCE(
            t.raw_payload ->> 'Tasuti riiklikke makse kokku',
            t.raw_payload ->> 'Tasutud maksud kokku',
            t.raw_payload ->> 'Riiklikud maksud kokku',
            t.raw_payload ->> 'PaidTaxes'
        )
    ) AS paid_taxes_eur,
    mart.parse_date(
        COALESCE(
            t.raw_payload ->> 'Perioodi algus',
            t.raw_payload ->> 'Periood algus',
            t.raw_payload ->> 'PeriodStart'
        )
    ) AS period_start_date,
    mart.parse_date(
        COALESCE(
            t.raw_payload ->> 'Perioodi lõpp',
            t.raw_payload ->> 'Periood lõpp',
            t.raw_payload ->> 'PeriodEnd'
        )
    ) AS period_end_date,
    t.raw_payload
FROM staging.emta_paid_taxes_raw t;

CREATE OR REPLACE VIEW mart.emta_competitor_summary AS
WITH latest_debt AS (
    SELECT
        d.reg_code,
        d.company_name,
        d.tax_debt_eur,
        d.debt_as_of_date,
        row_number() OVER (
            PARTITION BY d.reg_code
            ORDER BY d.debt_as_of_date DESC NULLS LAST, d.loaded_at DESC
        ) AS rn
    FROM mart.emta_tax_debt d
    WHERE COALESCE(d.reg_code, '') <> ''
),
paid_taxes AS (
    SELECT
        p.reg_code,
        max(p.company_name) AS company_name,
        sum(COALESCE(p.paid_taxes_eur, 0)) AS paid_taxes_total_eur,
        max(p.period_end_date) AS last_paid_period_end
    FROM mart.emta_paid_taxes p
    WHERE COALESCE(p.reg_code, '') <> ''
    GROUP BY p.reg_code
)
SELECT
    COALESCE(ld.reg_code, pt.reg_code) AS reg_code,
    COALESCE(NULLIF(ld.company_name, ''), NULLIF(pt.company_name, '')) AS company_name,
    ld.tax_debt_eur,
    ld.debt_as_of_date,
    pt.paid_taxes_total_eur,
    pt.last_paid_period_end
FROM latest_debt ld
FULL OUTER JOIN paid_taxes pt ON pt.reg_code = ld.reg_code
WHERE COALESCE(ld.rn, 1) = 1;