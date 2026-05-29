# Ettevõtja juhtimislaud projektitöö

## Mart layer (staging -> mart)

Eelda, et `staging` tabelid on juba loodud ja täidetud (`scripts/01_create_staging_merit.sql`, `scripts/02_create_staging_emta.sql`, `scripts/03_create_staging_merit_partners.sql` + loader-skriptid).

Mart layeri loomiseks käivita:

```bash
python scripts/run_mart.py
```

See käivitab järjekorras SQL failid:

1. `scripts/08_create_mart_schema.sql`
2. `scripts/09_mart_from_emta.sql`
3. `scripts/10_mart_from_merit.sql`
4. `scripts/11_mart_kpis.sql`

Võid sama teha ka käsitsi psql-iga samas järjekorras.

Tulemuseks tekivad `mart` skeemi dashboard-ready vaated, sh:
- `mart.emta_tax_debt`, `mart.emta_paid_taxes`, `mart.emta_competitor_summary`
- `mart.merit_sales_invoices`, `mart.merit_purchase_invoices`, `mart.merit_payments`
- `mart.kpi_daily`, `mart.kpi_monthly`, `mart.kpi_last_30_days`, `mart.kpi_runway`
