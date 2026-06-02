# Sprint 2 progress

## Mis on valmis

Sprint 2 jooksul valmis esimene töötav otsast-otsani andmevoog:

```text
Merit API / Meriti demoandmed
→ staging / bronze
→ quality check
→ mart view’d ja KPI-d
→ CSV eksport
→ Lovable dashboard
```

Valmis on:

* Meriti andmete laadimine staging-tabelitesse: ostuarved, müügiarved, maksed/laekumised, kliendid ja tarnijad.
* Korratav ja idempotentne andmete laadimise loogika.
* Staging quality check.
* Mart-kiht dashboardi jaoks.
* KPI vaated:

  * `mart.kpi_daily`
  * `mart.kpi_monthly`
  * `mart.kpi_last_30_days`
  * `mart.kpi_runway`
* Mart-vaadete CSV eksport.
* `demo_data/` kaust Lovable dashboardi importimiseks.
* Lovable dashboardi demo:

  * Ülevaade
  * Andmete import
  * Merit andmed
  * EMTA andmed
  * KPI vaated
  * Andmete kontroll
  * Esitlus
* Lovable demo on publishitud.

Lovable dashboard kasutab MVP-s CSV importi. Otsest ühendust Postgresi, Meriti ega EMTA API-ga Lovable demos ei ole.

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
7. ekspordib mart-vaated CSV failideks kausta `exports/`.

Töötav haru:

```text
test/mart-layer
```

## Tehniline käivitus

Peamised skriptid:

```text
scripts/run_merit_daily_load.py
scripts/check_merit_staging_quality.sql
scripts/run_mart.py
scripts/export_mart_csv.ps1
scripts/check_sprint2_flow.ps1
```

Peamised mart SQL failid:

```text
scripts/08_create_mart_schema.sql
scripts/09_mart_from_emta.sql
scripts/10_mart_from_merit.sql
scripts/11_mart_kpis.sql
```

## Sprint 2 järelkontroll: Meriti ärikuupäevad

Sprint 2 lõpus tehti täiendav äriloogika kontroll Meriti andmete põhjal.

Kontrolli käigus selgus, et `mart.kpi_last_30_days` näitas algselt kogu imporditud perioodi summasid, mitte päris viimase 30 päeva näitajaid.

Põhjus oli selles, et Meriti arve kuupäev ei tulnud mart-kihis `invoice_date` väljale õigesti sisse. `invoice_date` jäi tühjaks ning KPI arvutus kasutas varuvariandina tehnilisi kuupäevi (`changed_date` või `loaded_at`). Ajaloo laadimise puhul ei ole need sobivad ärikuupäevad, sest vana arve võib olla hiljuti laaditud või muudetud.

Parandus tehti failis:

```text
scripts/10_mart_from_merit.sql
```

Meriti arve kuupäeva parsimisel kasutatakse nüüd eelkõige ärikuupäeva välju:

```text
DocumentDate
TransactionDate
InvoiceDate
InvDate
Date
DocDate
```

Kuupäevad võetakse kujul `YYYY-MM-DD`, et Meriti väärtused kujul `2025-08-01T00:00:00` oleksid korrektselt parsitavad.

Pärast parandust näitas kontroll, et müügiarvete kuupäevad tulevad mart-vaatesse korrektselt:

```text
mart.merit_sales_invoices:
total_rows = 14
rows_with_invoice_date = 14
rows_missing_invoice_date = 0
```

Parandatud `mart.kpi_last_30_days` näide:

```text
sales_last_30d_eur:        579.53
costs_last_30d_eur:         50.20
net_cashflow_last_30d_eur: 529.33
vat_payable_last_30d_eur:    0.00
```

Oluline äriloogika järeldus:

```text
loaded_at = millal pipeline rea laadis
changed_date = millal allikas rida muutis
DocumentDate / TransactionDate = millal majandustehing tegelikult toimus
```

Dashboardi KPI-d peavad kasutama ärikuupäeva, mitte laadimiskuupäeva. See kehtib nii ajaloo laadimise kui ka igapäevase laadimise puhul.

Pärast parandust eksporditi KPI CSV failid uuesti ja uuendati Lovable demo andmed. Lovable Ülevaate ja KPI vaated näitavad nüüd samu parandatud 30 päeva KPI väärtusi.

## Lovable demo

Lovable demo kasutab failipõhist MVP lahendust:

```text
Postgres mart view’d
→ CSV eksport
→ demo_data
→ Lovable import
→ dashboard
```

Demo andmed imporditakse Lovable’isse CSV failidest.

Oluline teada:

* Lovable demo ei küsi otse Meriti API-st andmeid.
* Lovable demo ei ole otse ühendatud lokaalse Postgres andmebaasiga.
* Import ja dashboard on mõeldud MVP demonstratsiooniks.
* Demo kasutab paroolikaitset.

## Mis takistab

Blokeerivaid probleeme praegu ei ole.

Teadaolevad piirangud:

* Meriti live API kasutamiseks on vaja `.env` failis ligipääsuvõtmeid.
* Lovable MVP kasutab CSV importi, mitte otsest andmebaasiühendust.
* EMTA täisfailid on suured; dashboardi demos kasutatakse sample-faile.
* Väline kontroll Meriti päevaraamatu vastu vajab Sprint 3-s selgemat vormistust.

## Järgmised sammud

* Täpsustada välist kontrolli Meriti päevaraamatu CSV põhjal.
* Lisada või kirjeldada `external_control_merit.csv` kontrollfail.
* Eristada Lovable “Andmete kontroll” lehel:

  * kogu imporditud perioodi kontrollsummad;
  * viimase 30 päeva KPI-d.
* Viimistleda Lovable dashboardi kujundust.
* Peita tehnilised veerud vaikimisi.
* Laiendada EMTA vaateid.
* Valmistada lõplik demo ja esitlus.
