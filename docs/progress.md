# Sprint 2 progress

## Mis on valmis

Sprint 2 jooksul valmis esimene töötav otsast-otsani andmevoog:

```text
Merit API / Meriti demoandmed
→ staging/bronze
→ quality check
→ mart view’d ja KPI-d
→ CSV eksport
→ Lovable dashboard
```

Valmis on:

* Meriti andmete laadimine staging-tabelitesse: ostuarved, müügiarved, maksed/laekumised, kliendid ja tarnijad.
* Korratav ja idempotentne laadimine.
* Staging quality check.
* Mart-kiht dashboardi jaoks.
* KPI view’d.
* Mart CSV eksport.
* `demo_data` failid Lovable dashboardi jaoks.
* Lovable dashboardi CSV import ja KPI vaated.
* Meriti päevaraamatu põhine vastavuskontroll.

Olulisemad failid:

```text
scripts/run_merit_daily_load.py
scripts/check_merit_staging_quality.sql
scripts/run_mart.py
scripts/export_mart_csv.ps1
scripts/check_sprint2_flow.ps1
demo_data/
```

## Kontrollpunkt juhendajale

Sprint 2 töövoogu saab kontrollida käsuga:

```powershell
.\scripts\check_sprint2_flow.ps1
```

Skript:

1. käivitab Docker Postgres andmebaasi;
2. kontrollib andmebaasiühendust;
3. kuvab Meriti staging tabelite ridade arvud;
4. käivitab staging quality checki;
5. käivitab mart-kihi;
6. kuvab `mart.kpi_last_30_days` tulemuse;
7. ekspordib mart-vaated CSV failideks.

Oodatav KPI näide:

```text
sales_last_30d_eur:          8207.00
costs_last_30d_eur:          1237.00
net_cashflow_last_30d_eur:   1716.94
```

Need summad on võrreldud Meriti päevaraamatu kontrollsummadega ja klapivad kogu imporditud perioodi lõikes.

## Visuaal

Lovable dashboard kasutab MVP-s CSV importi:

```text
Postgres mart view’d
→ CSV eksport
→ demo_data/
→ Lovable import
→ dashboard
```

Dashboardis on nähtavad:

* Ülevaade
* Andmete import
* Merit andmed
* EMTA andmed
* KPI vaated
* Andmete kontroll
* Esitlus

## Järgmised sammud

* Täpsustada `kpi_last_30_days` loogika.
* Viimistleda Lovable dashboardi kujundus.
* Peita tehnilised väljad vaikimisi.
* Laiendada EMTA vaateid.
* Valmistada lõplik demo.

## Mis takistab

Blokeerivaid probleeme praegu ei ole.

Teadaolevad piirangud:

* Meriti live API vajab `.env` failis ligipääsuvõtmeid.
* Lovable ei ole MVP-s otse Postgresiga ühendatud, vaid kasutab CSV importi.
* EMTA täisfailid on suured, dashboardi demos kasutatakse sample-faile.
* `kpi_last_30_days` nimetus vajab täpsustamist: praegune väärtus klapib kogu perioodiga, mitte päris viimase 30 päevaga.

