[GRUPI NIMI] — [PROJEKTI PEALKIRI]
Juhend: Asenda kõik nurksulgudes vormid oma sisuga enne esitamist. Kustuta see juhendrida.

Äriküsimus
[Kirjelda ühe-kahe lausega, millise andmetega seotud probleemi te lahendate ja kes sellest kasu saab.]

Mõõdikud:

[Esimene KPI või mõõdik — näiteks: päevane müük poe kohta]
[Teine KPI või mõõdik]
[Kolmas KPI või mõõdik — vabatahtlik]
Arhitektuur
flowchart LR
    source[Andmeallikas] --> ingest[Sissevõtt]
    ingest --> staging[(staging)]
    staging --> transform[Transformatsioon]
    transform --> mart[(mart)]
    mart --> dashboard[Näidikulaud]
Täpsem kirjeldus: docs/arhitektuur.md

Andmestik
Allikas	Tüüp	Ajas muutuv?	Roll
[Andmeallika nimi]	[API / fail / andmebaas]	Jah, [iga tund / päevas / muu]	Põhiandmevoog
[Teise allika nimi]	[seed / dim-tabel]	Ei, staatiline	Kõrvaltabel
Stack
Komponent	Tööriist
Sissevõtt	[Python / Airflow / muu]
Transformatsioon	[SQL / dbt / muu]
Andmehoidla	PostgreSQL
Näidikulaud	[Superset / Streamlit / muu]
Orkestreerimine	[Airflow / cron / muu]
Käivitamine
# 1. Klooni repo ja liigu kausta
git clone <repo-url>
cd <projekti-kaust>

# 2. Kopeeri keskkonnamuutujad
cp .env.example .env
# Muuda .env failis paroolid ja muud seaded vastavalt vajadusele

# 3. Käivita teenused
docker compose up -d --build

# 4. [Vabatahtlik: käivita sissevõtt käsitsi esimesel korral]
# docker compose exec pipeline python scripts/run_pipeline.py run-all
Airflow (kui kasutatakse): http://localhost:8080 (kasutaja: airflow / parool: airflow) Näidikulaud: http://localhost:[PORT]

Saladused ja konfiguratsioon
Kõik saladused (paroolid, API võtmed, andmebaasi URL-id) on .env failis. Repos on ainult .env.example, mis näitab vajalike muutujate struktuuri ilma tegelike väärtusteta. Päris .env faili ei tohi GitHubi panna - see on .gitignore-s.

Vajalikud muutujad:

Muutuja	Tähendus	Näide
DB_PASSWORD	PostgreSQL parool	(saladus)
[teised]	...	...
Andmevoog lühidalt
Sissevõtt — [Kirjelda, kuidas andmed allikast kätte saadakse]
Laadimine — Andmed laaditakse staging kihti
Transformatsioon — [Kirjelda peamised arvutused ja mudelid]
Testimine — [Mitu] andmekvaliteedi testi kontrollivad korrektsust
Näidikulaud — [Kirjelda lühidalt, mida näidikulaud näitab]
Andmekvaliteedi testid
Projekt kontrollib järgmist:

[Test 1 - nt: kasutajate ID on unikaalne]
[Test 2 - nt: tellimuse summa pole null]
[Test 3 - nt: kuupäev jääb vahemikku 2020-2026] [Lisa rohkem, kui sul on]
Testide tulemused: [kuhu salvestatakse / kuidas vaadata]

Projekti struktuur
.
├── README.md
├── compose.yml
├── .env.example
├── .gitignore
├── docs/
│   ├── arhitektuur.md      ← nädal 1 väljund
│   └── progress.md         ← nädal 2 väljund
└── ...                     ← ülejäänud projektifailid
Kokkuvõte, puudused ja võimalikud edasiarendused
Kokkuvõte:

[Loetle, mis on lõpule viidud, mis töötab hästi]
Puudused:

[Loetle ausalt, mis jäi tegemata - see ei mõjuta hinnet negatiivselt, vaid aitab hinnata]
Mis edasi:

[Mida tahaksid edasi teha, kui aega oleks rohkem]
Meeskond
Nimi	Roll
[Nimi 1]	[Roll]
[Nimi 2]	[Roll]
[Nimi 3]	[Roll]
[Nimi 4]	[Roll — vabatahtlik]
