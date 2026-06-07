# Ettevõtja juhtimislaud

## Sisukord

1. [Projekti eesmärk](#projekti-eesmärk)
2. [Äriküsimus](#äriküsimus)
3. [Lahenduse ülevaade](#lahenduse-ülevaade)
4. [Arhitektuur](#arhitektuur)
5. [Andmeallikad](#andmeallikad)
6. [Andmevoog](#andmevoog)
7. [Repo struktuur](#repo-struktuur)
8. [Käivitusjuhend](#käivitusjuhend)
9. [Olulisemad skriptid](#olulisemad-skriptid)
10. [Mart-vaated ja KPI-d](#mart-vaated-ja-kpi-d)
11. [Andmekvaliteedi testid](#andmekvaliteedi-testid)
12. [Dashboard](#dashboard)
13. [Esitluse ja video plaan](#esitluse-ja-video-plaan)
14. [Turve ja tundlikud andmed](#turve-ja-tundlikud-andmed)
15. [Puudused](#puudused)
16. [Edasiarendused](#edasiarendused)
17. [Esituse info](#esituse-info)
18. [Lühikokkuvõte](#lühikokkuvõte)

---

## Projekti eesmärk

Projekti eesmärk on luua väikeettevõtjale lihtne juhtimislaud, mis aitab jälgida rahavoogu, viimase perioodi müüki ja kulusid, kasumit/kahjumit ning Meriti vastaspooltega seotud EMTA maksuriski.

Projekt on tehtud andmeinseneeria projektitööna. Fookus ei ole täieliku raamatupidamistarkvara ehitamisel, vaid tervikliku andmevoo demonstreerimisel:

```text
andmeallikad → staging / bronze → kvaliteedikontroll → mart / gold → Lovable dashboard
```

Lahendus on MVP ehk minimaalne töötav prototüüp. Projekti eesmärk on näidata, kuidas raamatupidamise andmetest ja avalikest maksuandmetest saab luua juhtimisotsuseid toetava andmekihi ja näidikulaua.

---

## Äriküsimus

**Kuidas aidata väikeettevõtjal jälgida rahajääki, lähiaja kohustusi, klientide maksekäitumist, üle tähtaja nõudeid, runway’d ja likviidsusriski?**

Projektis keskendutakse MVP mahus järgmistele küsimustele:

* kui suur on müük viimase 30 päeva jooksul;
* kui suured on kulud viimase 30 päeva jooksul;
* milline on kasum või kahjum;
* milline on indikatiivne KM näitaja;
* kas Meriti aktiivsetel klientidel ja tarnijatel on EMTA maksuvõla risk;
* kas andmetes on kvaliteediprobleeme, näiteks puuduvaid ärikuupäevi või registrikoode;
* kas dashboardi jaoks vajalikud mart andmebaasi tabelid on olemas ja loetavad.

---

## Lahenduse ülevaade

Lahendus koosneb kahest põhiosast.

### 1. Andmeinseneeria osa

Andmeinseneeria osa eesmärk on näidata andmetoru:

```text
lähteandmed → staging → quality checks → mart
```

Selles osas:

* luuakse staging-kihi tabelid;
* laaditakse demoandmed staging andmebaasi;
* tehakse kvaliteedikontrollid;
* luuakse mart-kihi vaated;
* arvutatakse KPI-d.

### 2. Dashboardi demo

Dashboard on loodud Lovable’is ja selle eesmärk on näidata:

* viimase 30 päeva KPI-sid;
* Meriti müügi-, ostu- ja makseandmeid;
* EMTA vastaspoolte riskikontrolli;
* lihtsat juhtimisvaadet ettevõtjale.

Lovable on selles MVP-s ühendatud Supabase andmebaasiga, kus dashboardi jaoks kasutatakse mart schema tabeleid.

---

## Arhitektuur

```text
Merit / EMTA
        │
        ▼
staging / bronze
        │
        ▼
quality checks
        │
        ▼
mart / gold
        │
        ▼
Lovable dashboard
```

EMTA andmeid kasutatakse Meriti klientide ja tarnijate riskikontrolliks registrikoodi alusel.
See tähendab, et dashboard ei kuva vaikimisi kogu EMTA avaandmestikku, vaid ainult seda osa, mis on seotud Meriti aktiivsete vastaspooltega.

---

## Andmeallikad

| Andmeallikas              | Roll projektis                                    |
| ------------------------- | ------------------------------------------------- |
| Merit Aktiva API          | Müügiarved, ostuarved, maksed, kliendid, tarnijad |
| EMTA avaandmed            | Maksuvõla ja tasutud maksude info                 |
| Mart andmebaas            | Dashboardi sisend                                 |

---

## Andmevoog

Andmevoog koosneb järgmistest sammudest:

1. lähteandmed laaditakse staging-kihi tabelitesse;
2. käivitatakse kvaliteedikontrollid;
3. luuakse mart-kihi vaated;
4. arvutatakse KPI-d;
5. Mart-vaated kuvatakse Lovable dashboardil.

Oluline äriloogika:

```text
loaded_at      = millal pipeline rea laadis
changed_date   = millal allikas / Merit rida muutis
invoice_date   = millal majandustehing tegelikult toimus
```

KPI-d kasutavad majandustehingu kuupäeva, mitte laadimiskuupäeva.
Projekti käigus parandati probleem, kus 30 päeva KPI võis alguses kasutada tehnilisi kuupäevi. Paranduse järel kasutatakse Meriti tehingu kuupäeva välju, näiteks:

```text
DocumentDate
TransactionDate
InvoiceDate
InvDate
Date
DocDate
```

Kui Merit annab kuupäeva kujul `2025-08-01T00:00:00`, lõigatakse see mart-kihis kujule `YYYY-MM-DD`.

---

## Repo struktuur

Olulisemad kaustad ja failid:

```text
.
├── admin/                         # admini / tehnilise vaate materjalid
├── data/
│   └── raw/
│       └── emta/                  # EMTA toorandmed / lähtefailid
├── docs/                          # dokumentatsioon ja progressi failid
├── scripts/                       # laadimise, transformatsiooni ja ekspordi skriptid
│   ├── quality_tests/             # andmekvaliteedi testid
│   ├── 01_create_staging_merit.sql
│   ├── 02_create_staging_emta.sql
│   ├── 08_create_mart_schema.sql
│   ├── 09_mart_from_emta.sql
│   ├── 10_mart_from_merit.sql
│   ├── 11_mart_kpis.sql
│   ├── 12_mart_counterparty_risk.sql
│   ├── 13_mart_monthly_sales_costs.sql
│   ├── init_db.py
│   ├── run_merit_backfill.py
│   ├── run_merit_partners_staging.py
│   ├── download_emta_files.py
│   ├── load_emta_staging.py
│   ├── run_mart.py
│   └── check_sprint2_flow.ps1
├── .env.example
├── compose.yml
├── requirements.txt
└── README.md
```

---

## Käivitusjuhend

### 1. Eeldused

Vajalikud tööriistad:

* Python 3;
* PostgreSQL või Docker Compose põhine andmebaas;
* PowerShell;
* Git;
* vajalikud Python paketid failist `requirements.txt`.

### 2. Keskkonna seadistamine

Paigalda Python sõltuvused:

```powershell
pip install -r requirements.txt
```

Kontrolli, et andmebaasi ühenduse seaded oleksid määratud `.env` failis. Näidis on failis:

```text
.env.example
```

Tabelite loomine Supabase andmebaasi:

```powershell
python scripts/init_db.py
```

### 3. Meritist andmete import Staging-kihti

Käivita andmete import andes ette alguskuupäeva:

```powershell
python scripts/run_merit_backfill.py --start-date 2025-01-01
```

Partnerite (kliendid + tarnijad) laadimine:

```powershell
python scripts/run_merit_partners_staging.py
```

### 4. EMTA-st andmete import Staging-kihti

CSV failide alla laadimine:
```powershell
python scripts/download_emta_files.py
```

Andmete laadimine tabelitesse:
```powershell
python scripts/load_emta_staging.py
```

### 5. Mart-kihi käivitamine

Mart-kihi SQL-id käivitatakse käsuga:

```powershell
python scripts/run_mart.py
```

`run_mart.py` käivitab järjest järgmised SQL-failid:
```text
08_create_mart_schema.sql
09_mart_from_emta.sql
10_mart_from_merit.sql
11_mart_kpis.sql
12_mart_counterparty_risk.sql
13_mart_monthly_sales_costs.sql
```

### 6. Lovable dashboard

Mart-vaated kuvatakse Lovable dashboardil kasutades Supabase andmebaasis olevaid tabeleid.

---

## Olulisemad skriptid

| Fail                                      | Otstarve                                     |
| ----------------------------------------- | -------------------------------------------- |
| `scripts/run_mart.py`                     | Käivitab mart-kihi SQL-id õiges järjekorras  |     |              |
| `scripts/check_merit_staging_quality.sql` | Kontrollib Meriti staging-andmete kvaliteeti |
| `scripts/08_create_mart_schema.sql`       | Loob mart skeemi ja abifunktsioonid          |
| `scripts/09_mart_from_emta.sql`           | Loob EMTA mart-vaated                        |
| `scripts/10_mart_from_merit.sql`          | Loob Meriti mart-vaated                      |
| `scripts/11_mart_kpis.sql`                | Arvutab KPI-d                                |
| `scripts/12_mart_counterparty_risk.sql`   | Loob EMTA vastaspoolte riskivaated           |

---

## Mart-vaated ja KPI-d

Peamised mart-vaated:

```text
mart.merit_sales_invoices
mart.merit_purchase_invoices
mart.merit_payments
mart.merit_customers
mart.merit_vendors
mart.kpi_last_30_days
mart.counterparty_activity
mart.counterparties_with_reg_code
mart.emta_counterparty_tax_risk
mart.counterparties_missing_reg_code
```

Peamised KPI-d:

| KPI                                 | Selgitus                                                              |
| ----------------------------------- | --------------------------------------------------------------------- |
| Müük viimase 30 päeva jooksul       | Müügiarvete põhjal arvutatud perioodi müük                            |
| Kulud viimase 30 päeva jooksul      | Ostuarvete / kulude põhjal arvutatud summa                            |
| Kasum/kahjum                        | Laekumiste ja väljamaksete vahe                                       |
| KM (käibemaks)                      | Indikatiivne tasumisele kuuluv või enammakstud käibemaksu näitaja     |
| Kuupõhine tulude ja kulude ülevaade | Pikema perioodi kohta tulude ja kulude graafik                        |
| Rahaline puhver (Runway)            | Hinnanguline päevade arv kui kauaks raha jätkub ilma juurde teenimata |
| Vastaspoolte risk                   | EMTA maksuvõla kontroll Meriti klientide ja tarnijate kohta           |

---

## EMTA vastaspoolte riskiloogika

EMTA osa ei ole MVP-s eraldi suur maksuandmete dashboard. EMTA andmeid kasutatakse Meriti aktiivsete klientide ja tarnijate riskikontrolliks.

Riskiloogika põhineb neljal mart-vaatel:

```text
mart.counterparty_activity
mart.counterparties_with_reg_code
mart.emta_counterparty_tax_risk
mart.counterparties_missing_reg_code
```

Vaadete roll:

| Vaade                                  | Selgitus                                                      |
| -------------------------------------- | ------------------------------------------------------------- |
| `mart.counterparty_activity`           | Meriti klientide ja tarnijate tegelik aktiivsus arvete põhjal |
| `mart.counterparties_with_reg_code`    | Meriti vastaspooled, kellel on registrikood olemas            |
| `mart.emta_counterparty_tax_risk`      | EMTA maksuvõla info Meriti vastaspoolte kohta                 |
| `mart.counterparties_missing_reg_code` | Aktiivsed vastaspooled, kellel puudub registrikood            |

---

## Andmekvaliteedi testid

Projektis kasutatakse andmekvaliteedi kontrollide loogikat, mis aitab tuvastada olulisemaid probleeme enne andmete kuvamist dashboardis.

Näited kvaliteeditestidest:

| Test                    | Mida kontrollib                                                        | Miks oluline                                          |
| ----------------------- | ---------------------------------------------------------------------- | ----------------------------------------------------- |
| Ärikuupäeva olemasolu   | Müügi- ja ostuarvetel peab olema ärikuupäev                            | KPI ei tohi tugineda laadimiskuupäevale               |
| KPI vaate olemasolu     | `mart.kpi_last_30_days` peab andma tulemuse                            | Dashboard peab saama KPI väärtused                    |
| Registrikoodi olemasolu | Aktiivsetel vastaspooltel peab olema registrikood                      | EMTA kontroll toimub registrikoodi alusel             |
| Mart-vaadete olemasolu  | Vajalikud mart-vaated peavad olema loodud                              | Dashboard ei tohi toetuda käsitsi arvutatud failidele |

Oluline erand:

```text
0 andmereaga riskifail ei ole automaatselt viga.
```

Näiteks `mart.counterparties_missing_reg_code` võib olla tühi, kui kõigil aktiivsetel vastaspooltel on registrikood olemas. Samuti võib `mart.emta_counterparty_tax_risk` olla tühi, kui maksuvõlaga vastaspooli ei leitud.

---

## Dashboard

Dashboard on loodud Lovable’is.

Avalik demo:

```text
https://ettevotja-toolaua-vaade.lovable.app
```

Demo parool:

```text
sprint2-demo-2026
```

Dashboardi vaated:

| Vaade            | Sisu                                              |
| ---------------- | ------------------------------------------------- |
| Ülevaade         | Peamised KPI-d                                    |
| Merit andmed     | Müügiarved, ostuarved, maksed, kliendid, tarnijad |
| EMTA andmed      | Meriti vastaspoolte EMTA riskikontroll            |

Dashboard kasutab mart-kihi vaateid, mis asuvad Supabase andmebaasis.

---

## Turve ja tundlikud andmed

Projekt on demo- ja õppeotstarbeline.

Turve MVP-s:

* päris API võtmeid ei hoita repos;
* `.env` faili ei commit’ida;
* näidis on `.env.example` failis;
* dashboard on kaitstud demo-parooliga;
* andmed on demoandmed või avalikud andmed.

Tootmislahenduses tuleks lisada:

* serveripoolne autentimine;
* rollipõhine ligipääs;
* secrets management;
* auditlogid;
* automaatne ajastus;
* eraldi arendus- ja tootmiskeskkond.

---

## Puudused

Projekti MVP-l on järgmised piirangud:

1. **Automaatne ajastus puudub**

   * Andmevoog käivitatakse käsitsi skriptidega.
   * Tootmises tuleks kasutada cron’i, Windows Task Schedulerit, GitHub Actionsit või muud schedulerit.

2. **Päevaraamatu väline KPI kontroll jäi edasiarenduseks**

   * Projekti käigus ilmnes, et KPI valideerimine peab kasutama sama perioodi, kuupäevavälja ja summa definitsiooni.
   * Lovable’i UI-s tehtud arvutus ei olnud selleks piisavalt usaldusväärne.
   * Edasiarendusena tuleks teha andmekihis eraldi `mart_kpi_validation_30_days` vaade.

3. **EMTA kontroll sõltub registrikoodist**

   * Kui Meriti partneril puudub registrikood, ei saa tema maksuriski automaatselt kontrollida.

4. **Demoandmed ei kata kõiki päriselulisi olukordi**

   * Näiteks osamaksed, keerulised kreeditarved, maksegraafikud ja perioodide ületused vajaksid täiendavat loogikat.

5. **Mobiilivaade on MVP tasemel**

   * Dashboard on eelkõige optimeeritud desktop-demo jaoks.
   * Mobiilivaates on põhiloogika kasutatav, kuid see vajaks tootmislahenduses täiendavat viimistlust.

---

## Edasiarendused

Võimalikud järgmised sammud:

1. EMTA andmete automaatne uuendamine;
2. cron / scheduler põhine igapäevane andmelaadimine;
3. `mart_kpi_validation_30_days` vaade välise KPI kontrolli jaoks;
4. täpsem runway ja likviidsusprognoos;
5. klientide maksekäitumise analüüs;
6. rollipõhine autentimine;
7. põhjalikum Streamlit admin-vaade;
8. dashboardi mobiilivaate täiustamine;
9. krediitarvete, osamaksete ja maksegraafikute parem käsitlus;
10. täpsem kliendi- ja tarnijapõhine rahavoo prognoos.

---


## Lühikokkuvõte

Projekt näitab terviklikku andmeinseneeria MVP-d, kus raamatupidamise demoandmed ja EMTA avaandmed liiguvad staging-kihist mart-kihini ning sealt Lovable dashboardi.

Kõige olulisem õppetund oli, et KPI-de puhul tuleb täpselt määratleda:

```text
periood + kuupäevaväli + summa definitsioon
```

Ilma selleta võivad viimase 30 päeva KPI-d anda eksitava tulemuse, eriti ajaloo laadimisel või andmete hilisemal muutmisel.

Projektis jõuti töötava MVP-ni, kus on olemas:

* mart-kiht;
* KPI-d;
* andmekvaliteedi kontrollid;
* EMTA vastaspoolte riskiloogika;
* Lovable dashboard;
* lõppesitluseks sobiv demoandmete põhine töövoog.
