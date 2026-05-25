// =============================================================
// Merit Aktiva — masstest-andmete generaator
// =============================================================
// Genereerib ja laadib Meritisse:
//   • N testklienti
//   • N testtarnijat
//   • M müügiarvet (juhuslike kuupäevade, summade, kaupade ja klientidega)
//   • M ostuarvet (juhuslike kuupäevade, summade, kaupade ja tarnijatega)
//
// Käivitamiseks:
//   export MERIT_API_ID="..."
//   export MERIT_API_KEY="..."
//   node merit-bulk-load.js
//
// PEA MEELES: trial-litsents lubab ainult 100 dokumenti!
//             Skript väldib seda piiri vaikimisi.
// =============================================================

const crypto = require('crypto');
const fs = require('fs');

// --- KONFIGURATSIOON -----------------------------------------------------
const API_ID  = process.env.MERIT_API_ID  || 'PANE_SIIA';
const API_KEY = process.env.MERIT_API_KEY || 'PANE_SIIA';
const BASE_URL = 'https://aktiva.merit.ee/api/v1/';

// Mitu objekti luuakse — alusta väikeselt, suurenda kui töötab
const NUM_CUSTOMERS = 5;
const NUM_VENDORS   = 5;
const NUM_SALES_INVOICES    = 20;
const NUM_PURCHASE_INVOICES = 20;

// Kuupäevavahemik (viimased 90 päeva)
const DATE_RANGE_DAYS = 90;

// Päringute vahel paus (ms) — Merit rate-limit'ib liiga kiireid päringuid
const DELAY_MS = 300;

// Logifail, kuhu salvestatakse kõik loodud GUID-id (et oskaksid hiljem
// neid pärida või kustutada)
const LOG_FILE = 'merit-created.json';

// --- TESTANDMETE BLUEPRINT'ID --------------------------------------------
const CUSTOMER_NAMES = [
  'Päikese Kohvik OÜ', 'Sinine Maja AS', 'Tark Kassi OÜ',
  'Põhjala Tarkvara OÜ', 'Roheline Aed OÜ', 'Kiire Käru AS',
  'Vana Veski OÜ', 'Mereäärne Pood AS', 'Linnumetsa OÜ',
  'Talve Tuuled OÜ',
];

const VENDOR_NAMES = [
  'Bürootarbed OÜ', 'IT Lahendused AS', 'Transport Eesti OÜ',
  'Puhastusteenused OÜ', 'Reklaam24 AS', 'Energiamüük OÜ',
  'Telefoniside AS', 'Raamatupidamine OÜ', 'Juriidika Partner OÜ',
  'Renditeenused AS',
];

const SALES_ITEMS = [
  { desc: 'Konsultatsiooniteenus, tund',     price: [60,  120] },
  { desc: 'Projektijuhtimine, päev',         price: [400, 800] },
  { desc: 'Tarkvara arendus, tund',          price: [70,  130] },
  { desc: 'Disainiteenus, tund',             price: [50,  100] },
  { desc: 'Koolitus, osaleja',               price: [150, 400] },
  { desc: 'Hooldus kuus',                    price: [80,  300] },
];

const PURCHASE_ITEMS = [
  { desc: 'Kontoritarbed',                   price: [20,  150] },
  { desc: 'Tarkvara litsents kuus',          price: [10,  80]  },
  { desc: 'Telefoniside teenus',             price: [15,  60]  },
  { desc: 'Transporditeenused',              price: [30,  200] },
  { desc: 'Reklaam ja turundus',             price: [100, 500] },
  { desc: 'Renditasu',                       price: [200, 800] },
  { desc: 'Kütusekulu',                      price: [40,  120] },
];

// --- ABIFUNKTSIOONID -----------------------------------------------------
const sleep = ms => new Promise(r => setTimeout(r, ms));
const rand  = (min, max) => Math.random() * (max - min) + min;
const randInt = (min, max) => Math.floor(rand(min, max + 1));
const pick = arr => arr[randInt(0, arr.length - 1)];
const round2 = n => Math.round(n * 100) / 100;

function getTimestamp() {
  const d = new Date();
  const pad = n => String(n).padStart(2, '0');
  return d.getUTCFullYear() + pad(d.getUTCMonth()+1) + pad(d.getUTCDate())
       + pad(d.getUTCHours()) + pad(d.getUTCMinutes()) + pad(d.getUTCSeconds());
}

// Juhuslik kuupäev viimaste N päeva seest, formaadis yyyyMMdd
function randomDate(daysAgo = DATE_RANGE_DAYS) {
  const d = new Date();
  d.setUTCDate(d.getUTCDate() - randInt(0, daysAgo));
  const pad = n => String(n).padStart(2, '0');
  return d.getUTCFullYear() + pad(d.getUTCMonth()+1) + pad(d.getUTCDate());
}

// Lisab kuupäevale päevi (formaadis yyyyMMdd → yyyyMMdd)
function addDays(yyyymmdd, days) {
  const y = parseInt(yyyymmdd.slice(0, 4));
  const m = parseInt(yyyymmdd.slice(4, 6)) - 1;
  const d = parseInt(yyyymmdd.slice(6, 8));
  const date = new Date(Date.UTC(y, m, d));
  date.setUTCDate(date.getUTCDate() + days);
  const pad = n => String(n).padStart(2, '0');
  return date.getUTCFullYear() + pad(date.getUTCMonth()+1) + pad(date.getUTCDate());
}

function sign(apiId, timestamp, body, apiKey) {
  return crypto.createHmac('sha256', apiKey)
    .update(apiId + timestamp + body, 'utf8')
    .digest('base64');
}

async function meritCall(endpoint, payload, silent = false) {
  const timestamp = getTimestamp();
  const body = JSON.stringify(payload);
  const signature = sign(API_ID, timestamp, body, API_KEY);

  const url = `${BASE_URL}${endpoint}`
    + `?ApiId=${API_ID}&timestamp=${timestamp}`
    + `&signature=${encodeURIComponent(signature)}`;

  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
    body
  });

  const text = await res.text();
  let data;
  try { data = JSON.parse(text); } catch { data = text; }

  if (!res.ok) {
    if (!silent) console.error(`  ✗ ${endpoint} → HTTP ${res.status}:`, data);
    throw new Error(`Merit ${endpoint} → ${res.status}`);
  }

  await sleep(DELAY_MS);
  return data;
}

// --- 0. LEIA STANDARDNE KÄIBEMAKSU ID ------------------------------------
let STANDARD_TAX_ID = null;

async function findStandardTaxId() {
  console.log('\n→ Otsin standardset käibemaksu (22%) ID-d...');
  const taxes = await meritCall('gettaxes', {});

  if (!Array.isArray(taxes)) {
    throw new Error('Maksumäärade nimekiri ei tagastanud massiivi: ' + JSON.stringify(taxes));
  }

  // Eelistame 22%, kui pole, siis 20% (vana määr) või suurim
  const tax22 = taxes.find(t => t.TaxPct === 22 || t.TaxPct === 22.0);
  const tax20 = taxes.find(t => t.TaxPct === 20 || t.TaxPct === 20.0);
  const chosen = tax22 || tax20 || taxes.reduce((a, b) => (a.TaxPct > b.TaxPct ? a : b));

  console.log(`  Valitud: ${chosen.Name} (${chosen.TaxPct}%) → ${chosen.Id}`);
  return chosen.Id;
}

// --- 1. KLIENTIDE LOOMINE ------------------------------------------------
async function createCustomers(n) {
  console.log(`\n→ Loon ${n} klienti...`);
  const created = [];

  for (let i = 0; i < n; i++) {
    const name = `${pick(CUSTOMER_NAMES)} #${randInt(1000, 9999)}`;
    const payload = {
      Name: name,
      RegNo: String(randInt(10000000, 99999999)),
      NotTDCustomer: false,
      CurrencyCode: 'EUR',
      Address: `Testitänav ${randInt(1, 99)}`,
      City: pick(['Tallinn', 'Tartu', 'Pärnu', 'Narva']),
      Country: 'Estonia',
      CountryCode: 'EE',
      PostalCode: String(randInt(10000, 99999)),
      Email: `test${i}@example.ee`,
      PaymentDeadLine: pick([7, 14, 21, 30]),
    };

    try {
      const res = await meritCall('sendcustomer', payload);
      const id = res.Id || res.CustomerId || res;
      created.push({ name, id });
      console.log(`  ✓ ${i+1}/${n}  ${name}`);
    } catch (e) {
      console.error(`  ✗ ${name}: ${e.message}`);
    }
  }
  return created;
}

// --- 2. TARNIJATE LOOMINE ------------------------------------------------
async function createVendors(n) {
  console.log(`\n→ Loon ${n} tarnijat...`);
  const created = [];

  for (let i = 0; i < n; i++) {
    const name = `${pick(VENDOR_NAMES)} #${randInt(1000, 9999)}`;
    const payload = {
      Name: name,
      RegNo: String(randInt(10000000, 99999999)),
      NotTDCustomer: false,
      CurrencyCode: 'EUR',
      Address: `Tarnijatänav ${randInt(1, 99)}`,
      City: pick(['Tallinn', 'Tartu', 'Pärnu']),
      Country: 'Estonia',
      CountryCode: 'EE',
      PostalCode: String(randInt(10000, 99999)),
      Email: `vendor${i}@example.ee`,
      PaymentDeadLine: pick([14, 21, 30]),
    };

    try {
      const res = await meritCall('sendvendor', payload);
      const id = res.Id || res.VendorId || res;
      created.push({ name, id });
      console.log(`  ✓ ${i+1}/${n}  ${name}`);
    } catch (e) {
      console.error(`  ✗ ${name}: ${e.message}`);
    }
  }
  return created;
}

// --- 3. MÜÜGIARVETE LOOMINE ----------------------------------------------
async function createSalesInvoices(n, customers) {
  console.log(`\n→ Loon ${n} müügiarvet...`);
  const created = [];

  for (let i = 0; i < n; i++) {
    const customer = pick(customers);
    const docDate  = randomDate();
    const dueDate  = addDays(docDate, 14);

    // 1–4 rida igal arvel
    const numRows = randInt(1, 4);
    const rows = [];
    let totalNet = 0;

    for (let r = 0; r < numRows; r++) {
      const item = pick(SALES_ITEMS);
      const qty  = randInt(1, 10);
      const price = round2(rand(item.price[0], item.price[1]));
      rows.push({
        Item: { Description: item.desc },
        Quantity: qty,
        Price: price,
        TaxId: STANDARD_TAX_ID,
      });
      totalNet += qty * price;
    }

    const totalGross = round2(totalNet * 1.22); // 22% KM

    const payload = {
      Customer: { Name: customer.name },
      DocDate: docDate,
      DueDate: dueDate,
      InvoiceNo: '',           // tühi = Merit genereerib
      CurrencyCode: 'EUR',
      HComment: `Testarve #${i+1}`,
      InvoiceRow: rows,
      TotalAmount: totalGross,
      RoundingAmount: 0,
    };

    try {
      const res = await meritCall('sendinvoice', payload);
      created.push({ customer: customer.name, total: totalGross, response: res });
      console.log(`  ✓ ${i+1}/${n}  ${customer.name}  €${totalGross}  (${numRows} rida)`);
    } catch (e) {
      console.error(`  ✗ ${i+1}/${n}: ${e.message}`);
    }
  }
  return created;
}

// --- 4. OSTUARVETE LOOMINE -----------------------------------------------
async function createPurchaseInvoices(n, vendors) {
  console.log(`\n→ Loon ${n} ostuarvet...`);
  const created = [];

  for (let i = 0; i < n; i++) {
    const vendor   = pick(vendors);
    const docDate  = randomDate();
    const dueDate  = addDays(docDate, 21);

    const numRows = randInt(1, 3);
    const rows = [];
    let totalNet = 0;

    for (let r = 0; r < numRows; r++) {
      const item = pick(PURCHASE_ITEMS);
      const qty  = randInt(1, 5);
      const price = round2(rand(item.price[0], item.price[1]));
      rows.push({
        Item: { Description: item.desc },
        Quantity: qty,
        Price: price,
        TaxId: STANDARD_TAX_ID,
        // AccountCode: '5510',  // soovi korral lisa kontoplaani kood
      });
      totalNet += qty * price;
    }

    const totalGross = round2(totalNet * 1.22);

    const payload = {
      Vendor: { Name: vendor.name },
      DocDate: docDate,
      TransactionDate: docDate,
      DueDate: dueDate,
      DocNo: `T-${docDate}-${randInt(100, 999)}`,
      CurrencyCode: 'EUR',
      PurchaseInvoiceRow: rows,
      TotalAmount: totalGross,
      RoundingAmount: 0,
    };

    try {
      const res = await meritCall('sendpurchinvoice', payload);
      created.push({ vendor: vendor.name, total: totalGross, response: res });
      console.log(`  ✓ ${i+1}/${n}  ${vendor.name}  €${totalGross}  (${numRows} rida)`);
    } catch (e) {
      console.error(`  ✗ ${i+1}/${n}: ${e.message}`);
    }
  }
  return created;
}

// --- PEAFUNKTSIOON -------------------------------------------------------
async function main() {
  if (API_ID === 'PANE_SIIA') {
    console.error('VIGA: pane MERIT_API_ID ja MERIT_API_KEY keskkonnamuutujatesse');
    process.exit(1);
  }

  const total = NUM_SALES_INVOICES + NUM_PURCHASE_INVOICES;
  if (total > 90) {
    console.warn(`⚠ Hoiatus: lood ${total} dokumenti. Trial-litsentsi piir on 100.`);
  }

  console.log('=== Merit Aktiva masstest-andmete laadimine ===');
  console.log(`Tegevuse plaan:`);
  console.log(`  • ${NUM_CUSTOMERS} klienti`);
  console.log(`  • ${NUM_VENDORS} tarnijat`);
  console.log(`  • ${NUM_SALES_INVOICES} müügiarvet`);
  console.log(`  • ${NUM_PURCHASE_INVOICES} ostuarvet`);

  const startTime = Date.now();

  try {
    STANDARD_TAX_ID = await findStandardTaxId();

    const customers = await createCustomers(NUM_CUSTOMERS);
    if (customers.length === 0) throw new Error('Ühtegi klienti ei loodud, katkestan');

    const vendors = await createVendors(NUM_VENDORS);
    if (vendors.length === 0) throw new Error('Ühtegi tarnijat ei loodud, katkestan');

    const salesInvoices    = await createSalesInvoices(NUM_SALES_INVOICES, customers);
    const purchaseInvoices = await createPurchaseInvoices(NUM_PURCHASE_INVOICES, vendors);

    // Salvesta log, et oskaksid hiljem need dokumendid leida
    fs.writeFileSync(LOG_FILE, JSON.stringify({
      createdAt: new Date().toISOString(),
      taxId: STANDARD_TAX_ID,
      customers, vendors, salesInvoices, purchaseInvoices,
    }, null, 2));

    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
    console.log(`\n✓ Valmis ${elapsed}s jooksul!`);
    console.log(`  Loodud: ${customers.length} klienti, ${vendors.length} tarnijat,`);
    console.log(`          ${salesInvoices.length} müügiarvet, ${purchaseInvoices.length} ostuarvet`);
    console.log(`  Log salvestatud: ${LOG_FILE}`);
  } catch (e) {
    console.error('\n✗ Skript katkes:', e.message);
    process.exit(1);
  }
}

main();
