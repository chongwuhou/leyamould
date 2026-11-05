import fs from 'node:fs';
import {readFileSync} from 'node:fs';

const ORIGIN = 'https://xuyibottles.com';
const ACCOUNT = 'a4032d0251103d6ef680b2aaddce1afc';
const TOKEN = process.env.CLOUDFLARE_API_TOKEN;
if (!TOKEN) throw new Error('Missing CLOUDFLARE_API_TOKEN');

async function jsonFetch(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      accept: 'application/json',
      'user-agent': 'XUYI-D1-SEO-Maintenance/1.0',
      ...(options.headers || {})
    }
  });
  const text = await response.text();
  let payload;
  try { payload = JSON.parse(text); } catch { throw new Error('Invalid JSON from ' + url + ': ' + text.slice(0, 300)); }
  if (!response.ok || payload.success === false) {
    throw new Error('HTTP ' + response.status + ' from ' + url + ': ' + JSON.stringify(payload).slice(0, 800));
  }
  return payload;
}

async function siteSnapshot() {
  return jsonFetch(ORIGIN + '/api/build-snapshot', {
    headers: {authorization: 'Bearer ' + TOKEN, 'cache-control': 'no-store'}
  });
}

async function cloudflare(path, method = 'GET', body = undefined) {
  return jsonFetch('https://api.cloudflare.com/client/v4/accounts/' + ACCOUNT + path, {
    method,
    headers: {authorization: 'Bearer ' + TOKEN, ...(body ? {'content-type': 'application/json'} : {})},
    body: body ? JSON.stringify(body) : undefined
  });
}

function loadExportArray(path) {
  const source = readFileSync(path, 'utf8');
  const start = source.indexOf('[');
  const end = source.lastIndexOf('];');
  if (start < 0 || end < start) throw new Error('Cannot parse reviewed source: ' + path);
  return JSON.parse(source.slice(start, end + 1));
}

function key(row) { return row.slug + '/' + row.locale; }
function sqlString(value) { return String(value).replace(/'/g, "''"); }

const refresh = loadExportArray('functions/_shared/reviewed-product-seo-refresh-20261104.js');
const previous = loadExportArray('functions/_shared/reviewed-product-seo-20261020.js');
if (refresh.length !== 505 || previous.length !== 505) throw new Error('Unexpected reviewed product SEO source count');

const suffix = {
  en: '. B2B OEM factory. Ask about custom Tritan/BPA-free materials, logo, colors and bulk packing; confirm by SKU.',
  es: '. Fabricante OEM B2B. Consulte Tritan/BPA-free, plástico, logo, colores y embalaje; confirme el SKU.',
  pt: '. Fabricante OEM B2B. Consulte Tritan/BPA-free, plástico, cores e embalagem; confirme o SKU.',
  ru: '. OEM-производитель B2B. Уточните Tritan/BPA-free, полимеры, логотип, цвет и упаковку по SKU.',
  tr: '. B2B OEM üreticisi. Özel Tritan/BPA-free plastik, logo, renk ve koli seçeneklerini sorun; SKU ile doğrulayın.'
};

const target = refresh.map(row => ({
  ...row,
  metaDescription: row.newTitle.replace(/\s+\|\s+XUYI\s*$/, '') + suffix[row.locale]
}));
for (const row of target) {
  if (row.newTitle.length > 60 || row.metaDescription.length > 180) {
    throw new Error('SEO field exceeds limit: ' + key(row));
  }
}
const previousMap = new Map(previous.map(row => [key(row), row]));
const refreshMap = new Map(refresh.map(row => [key(row), row]));

const snapshot = await siteSnapshot();
const currentSeo = new Map((snapshot.productSeo || []).map(row => [row.slug + '/' + row.locale, row]));
const currentPages = new Map((snapshot.pages || []).map(row => [row.route, row]));
const currentBodies = new Map((snapshot.pageBodies || []).map(row => [row.route, row]));
const currentTranslations = new Set((snapshot.translations || []).map(row => row.resourceId + '|' + row.locale));

const databases = await cloudflare('/d1/database?per_page=100');
const database = (databases.result || []).find(row => row.name === 'xuyi-drinkware-d1' || row.name === 'xuyi-drinkware-site');
if (!database?.uuid) throw new Error('XUYI D1 database was not found');
const dbPath = '/d1/database/' + database.uuid + '/query';

async function query(sql, params = []) {
  const result = await cloudflare(dbPath, 'POST', {sql, params});
  return result.result;
}

let insertedSeo = 0;
let updatedSeo = 0;
let preservedSeo = 0;
let unchangedSeo = 0;
const workers = 8;
let cursor = 0;
async function seoWorker() {
  while (true) {
    const index = cursor++;
    if (index >= target.length) return;
    const row = target[index];
    const k = key(row);
    const current = currentSeo.get(k);
    if (!current) {
      await query(
        'INSERT INTO xuyi_product_seo(slug,locale,seo_title,meta_description,updated_at) VALUES(?,?,?,?,CURRENT_TIMESTAMP) ON CONFLICT(slug,locale) DO NOTHING',
        [row.slug, row.locale, row.newTitle, row.metaDescription]
      );
      insertedSeo++;
      continue;
    }
    if (current.seo_title === row.newTitle && current.meta_description === row.metaDescription) {
      unchangedSeo++;
      continue;
    }
    const old = previousMap.get(k);
    const oldRefresh = refreshMap.get(k);
    const editable = [
      [old?.newTitle, old?.newDescription],
      [old?.oldTitle, old?.oldDescription],
      [oldRefresh?.newTitle, oldRefresh?.newDescription]
    ].some(pair => pair[0] && pair[1] && current.seo_title === pair[0] && current.meta_description === pair[1]);
    if (!editable) {
      preservedSeo++;
      continue;
    }
    await query(
      'UPDATE xuyi_product_seo SET seo_title=?,meta_description=?,updated_at=CURRENT_TIMESTAMP WHERE slug=? AND locale=? AND seo_title=? AND meta_description=?',
      [row.newTitle, row.metaDescription, row.slug, row.locale, current.seo_title, current.meta_description]
    );
    updatedSeo++;
  }
}
await Promise.all(Array.from({length: workers}, () => seoWorker()));

const category = {
  '/collections/kids-water-bottles/': {
    h1: {
      en: 'B2B Kids Plastic Water Bottles Manufacturer — OEM Factory',
      es: 'Fabricante B2B de botellas infantiles de plástico — Fábrica OEM',
      pt: 'Fabricante B2B de garrafas infantis de plástico — Fábrica OEM',
      ru: 'B2B-производитель детских пластиковых бутылок — OEM-завод',
      tr: 'B2B çocuk plastik mataraları üreticisi — OEM fabrika'
    },
    intro: {
      en: 'Wholesale kids plastic water bottles with straw, carry-strap and color options for private label, school and promotional programs. Custom plastic materials, logo and packing can be reviewed by model.',
      es: 'Botellas infantiles de plástico al por mayor con pajita, correa y opciones de color para marca privada, colegios y promociones. Los materiales plásticos, el logo y el embalaje se revisan por modelo.',
      pt: 'Garrafas infantis de plástico para atacado com palhinha, alça e opções de cor para marca própria, escolas e promoções. Materiais plásticos, logo e embalagem podem ser avaliados por modelo.',
      ru: 'Детские пластиковые бутылки оптом с трубочкой, ремешком и вариантами цвета для private label, школ и промо-программ. Полимеры, логотип и упаковка согласуются по модели.',
      tr: 'Özel marka, okul ve promosyon programları için pipetli, askılı ve renk seçenekli toptan çocuk plastik mataraları. Özel plastik malzeme, logo ve koli seçenekleri modele göre görüşülür.'
    }
  },
  '/collections/large-capacity-water-jugs/': {
    h1: {
      en: 'B2B Large-Capacity Plastic Water Jugs Manufacturer — OEM Factory',
      es: 'Fabricante B2B de jarras de agua grandes de plástico — Fábrica OEM',
      pt: 'Fabricante B2B de jarras de água grandes de plástico — Fábrica OEM',
      ru: 'B2B-производитель пластиковых бутылок большого объёма — OEM-завод',
      tr: 'B2B büyük hacimli plastik su mataraları üreticisi — OEM fabrika'
    },
    intro: {
      en: 'Large-capacity plastic water jugs for fitness, outdoor, team and promotional buyers. Confirm each model’s factory ml capacity, approximate oz size class, colors, handle, lid, custom plastic material and bulk packing.',
      es: 'Jarras de agua grandes de plástico para fitness, exterior, equipos y promociones. Confirme por modelo la capacidad de fábrica en ml, la clase oz aproximada, los colores, el asa, la tapa, el plástico a medida y el embalaje.',
      pt: 'Jarras de água grandes de plástico para fitness, exterior, equipas e promoções. Confirme por modelo a capacidade de fábrica em ml, a classe oz aproximada, cores, asa, tampa, plástico sob medida e embalagem.',
      ru: 'Пластиковые бутылки большого объёма для фитнеса, улицы, команд и промо-заказов. По каждой модели уточняйте заводской объём в мл, примерный класс oz, цвет, ручку, крышку, полимер и упаковку.',
      tr: 'Fitness, outdoor, takım ve promosyon alıcıları için büyük hacimli plastik su mataraları. Her modelin fabrika ml kapasitesini, yaklaşık oz sınıfını, renk, tutamak, kapak, özel plastik ve koli seçeneklerini doğrulayın.'
    }
  },
  '/collections/plastic-shaker-bottles/': {
    h1: {
      en: 'B2B Plastic Shaker Bottles Manufacturer — OEM Factory',
      es: 'Fabricante B2B de botellas shaker de plástico — Fábrica OEM',
      pt: 'Fabricante B2B de coqueteleiras de plástico — Fábrica OEM',
      ru: 'B2B-производитель пластиковых шейкеров — OEM-завод',
      tr: 'B2B plastik shaker şişesi üreticisi — OEM fabrika'
    },
    intro: {
      en: 'Wholesale plastic shaker bottles for gym, protein, fitness and sports-nutrition programs. Review factory ml capacity, approximate oz size class, mixing components, custom plastic material, logo, colors and packing by model.',
      es: 'Botellas shaker de plástico al por mayor para gimnasio, proteína, fitness y nutrición deportiva. Revise por modelo la capacidad ml, la clase oz aproximada, los componentes de mezcla, el plástico a medida, el logo, los colores y el embalaje.',
      pt: 'Coqueteleiras de plástico para atacado destinadas a ginásio, proteína, fitness e nutrição desportiva. Avalie por modelo a capacidade ml, a classe oz aproximada, os componentes, o plástico sob medida, logo, cores e embalagem.',
      ru: 'Пластиковые шейкеры оптом для залов, протеиновых, фитнес- и спортивных программ. По модели проверьте объём в мл, примерный класс oz, компоненты, полимер, логотип, цвет и упаковку.',
      tr: 'Spor salonu, protein, fitness ve spor beslenme programları için toptan plastik shaker şişeleri. Model bazında ml kapasitesini, yaklaşık oz sınıfını, karıştırma bileşenlerini, özel plastiği, logoyu, renkleri ve koliyi inceleyin.'
    }
  },
  '/collections/sports-water-bottles/': {
    h1: {
      en: 'B2B Plastic Sports Water Bottles Manufacturer — OEM Factory',
      es: 'Fabricante B2B de botellas deportivas de plástico — Fábrica OEM',
      pt: 'Fabricante B2B de garrafas esportivas de plástico — Fábrica OEM',
      ru: 'B2B-производитель пластиковых спортивных бутылок — OEM-завод',
      tr: 'B2B plastik spor mataraları üreticisi — OEM fabrika'
    },
    intro: {
      en: 'Wholesale plastic sports water bottles for active, outdoor and promotional collections. Confirm factory ml capacity, approximate oz size class, source-confirmed material, colors, logo, lid components and bulk packing by model.',
      es: 'Botellas deportivas de plástico al por mayor para colecciones activas, exteriores y promocionales. Confirme por modelo la capacidad ml, la clase oz aproximada, el material de origen, los colores, el logo, la tapa y el embalaje.',
      pt: 'Garrafas esportivas de plástico para atacado em coleções ativas, outdoor e promocionais. Confirme por modelo a capacidade ml, a classe oz aproximada, o material de origem, cores, logo, tampa e embalagem.',
      ru: 'Пластиковые спортивные бутылки оптом для активных, outdoor- и промо-коллекций. По модели уточняйте заводской объём в мл, примерный класс oz, материал, цвет, логотип, крышку и упаковку.',
      tr: 'Aktif yaşam, outdoor ve promosyon koleksiyonları için toptan plastik spor mataraları. Model bazında fabrika ml kapasitesini, yaklaşık oz sınıfını, kaynağı doğrulanmış malzemeyi, renkleri, logoyu, kapağı ve koliyi onaylayın.'
    }
  },
  '/collections/spray-water-bottles/': {
    h1: {
      en: 'B2B Spray Water Bottles Manufacturer — OEM Factory',
      es: 'Fabricante B2B de botellas de agua con pulverizador — Fábrica OEM',
      pt: 'Fabricante B2B de garrafas com borrifador — Fábrica OEM',
      ru: 'B2B-производитель бутылок с распылителем — OEM-завод',
      tr: 'B2B spreyli su matarası üreticisi — OEM fabrika'
    },
    intro: {
      en: 'Wholesale spray water bottles for outdoor, cooling, promotional and retail programs. Confirm factory ml capacity, approximate oz size class, nozzle, trigger, custom plastic material, colors, logo and packing by model.',
      es: 'Botellas con pulverizador al por mayor para exterior, refrigeración, promociones y retail. Confirme por modelo la capacidad ml, la clase oz aproximada, la boquilla, el gatillo, el plástico a medida, los colores, el logo y el embalaje.',
      pt: 'Garrafas com borrifador para atacado em programas outdoor, de arrefecimento, promocionais e retail. Confirme por modelo a capacidade ml, a classe oz aproximada, bico, gatilho, plástico sob medida, cores, logo e embalagem.',
      ru: 'Бутылки с распылителем оптом для улицы, охлаждения, промо и розницы. По модели уточняйте объём в мл, примерный класс oz, распылитель, курок, полимер, цвет, логотип и упаковку.',
      tr: 'Outdoor, serinletme, promosyon ve perakende programları için toptan spreyli su mataraları. Model bazında ml kapasitesini, yaklaşık oz sınıfını, nozulu, tetiği, özel plastiği, renkleri, logoyu ve koliyi doğrulayın.'
    }
  },
  '/collections/two-way-drinking-cups/': {
    h1: {
      en: 'B2B Dual-Mode Two-Way Drinking Cups Manufacturer — OEM Factory',
      es: 'Fabricante B2B de vasos de doble modo — Fábrica OEM',
      pt: 'Fabricante B2B de copos de dupla função — Fábrica OEM',
      ru: 'B2B-производитель кружек с двумя способами питья — OEM-завод',
      tr: 'B2B iki içim seçenekli bardak üreticisi — OEM fabrika'
    },
    intro: {
      en: 'Wholesale dual-mode two-way drinking cups for travel, retail and promotional collections. Review model-specific ml capacity and approximate oz class, lid seal design, custom plastic materials, colors, logo and bulk packing.',
      es: 'Vasos de doble modo al por mayor para viaje, retail y promociones. Revise por modelo la capacidad ml y la clase oz aproximada, el sellado de la tapa, los plásticos a medida, los colores, el logo y el embalaje.',
      pt: 'Copos de dupla função para atacado em viagens, retail e promoções. Avalie por modelo a capacidade ml e a classe oz aproximada, a vedação da tampa, os plásticos sob medida, cores, logo e embalagem.',
      ru: 'Кружки с двумя способами питья оптом для путешествий, розницы и промо. По модели проверьте объём в мл и примерный класс oz, уплотнение крышки, полимеры, цвет, логотип и упаковку.',
      tr: 'Seyahat, perakende ve promosyon koleksiyonları için toptan iki içim seçenekli bardaklar. Model bazında ml kapasitesini ve yaklaşık oz sınıfını, kapak conta tasarımını, özel plastikleri, renkleri, logoyu ve koliyi inceleyin.'
    }
  },
  '/collections/titanium-vacuum-cups/': {
    h1: {
      en: 'B2B Titanium Vacuum Cups Manufacturer — OEM Factory',
      es: 'Fabricante B2B de vasos térmicos al vacío de titanio — Fábrica OEM',
      pt: 'Fabricante B2B de copos térmicos a vácuo de titânio — Fábrica OEM',
      ru: 'B2B-производитель вакуумных термокружек из титана — OEM-завод',
      tr: 'B2B titanyum vakumlu termos bardak üreticisi — OEM fabrika'
    },
    intro: {
      en: 'Wholesale titanium vacuum cups for insulated drinkware sourcing. Confirm factory ml capacity, approximate oz class, titanium grade, lid and seal materials, finish, logo and test documents by SKU.',
      es: 'Vasos térmicos al vacío de titanio al por mayor. Confirme por SKU la capacidad ml, la clase oz aproximada, el grado de titanio, los materiales de tapa y junta, el acabado, el logo y los documentos de prueba.',
      pt: 'Copos térmicos a vácuo de titânio para atacado. Confirme por SKU a capacidade ml, a classe oz aproximada, o grau de titânio, materiais da tampa e vedação, acabamento, logo e documentos de teste.',
      ru: 'Титановые вакуумные термокружки оптом для закупки теплоизолированной посуды. По SKU уточняйте объём в мл, примерный класс oz, марку титана, материалы крышки и уплотнителя, отделку, логотип и документы.',
      tr: 'Yalıtımlı içecek ürünleri tedariki için toptan titanyum vakumlu termos bardaklar. SKU bazında ml kapasitesini, yaklaşık oz sınıfını, titanyum kalitesini, kapak ve conta malzemelerini, yüzeyi, logoyu ve test belgelerini doğrulayın.'
    }
  }
};

const englishMeta = {
  '/collections/kids-water-bottles/': ['Kids Plastic Water Bottles Wholesale OEM Manufacturer | XUYI', 'B2B kids plastic water bottles with straw and carry-strap options. Ask the XUYI OEM factory about custom plastic materials, colors, logos and bulk packing.'],
  '/collections/large-capacity-water-jugs/': ['Large-Capacity Plastic Water Jugs Wholesale OEM | XUYI', 'B2B large-capacity plastic water jugs for fitness and outdoor buyers. Confirm factory ml, approximate oz size class, materials, colors, lids, logos and packing by model.'],
  '/collections/plastic-shaker-bottles/': ['Plastic Shaker Bottles Wholesale OEM Factory | XUYI', 'B2B plastic shaker bottles for gym, protein and fitness programs. Confirm ml capacity, approximate oz class, mixing components, custom plastic, logo and bulk packing by model.'],
  '/collections/sports-water-bottles/': ['Plastic Sports Water Bottles Wholesale OEM | XUYI', 'B2B plastic sports water bottles for active and promotional collections. Confirm factory ml, approximate oz class, materials, colors, lid components, logo and packing by model.'],
  '/collections/spray-water-bottles/': ['Spray Water Bottles Wholesale OEM Factory | XUYI', 'B2B spray water bottles for outdoor, cooling and promotional programs. Confirm factory ml, approximate oz class, nozzle, custom plastic, colors, logo and packing by model.'],
  '/collections/two-way-drinking-cups/': ['Dual-Mode Two-Way Drinking Cups Wholesale OEM | XUYI', 'B2B dual-mode two-way drinking cups for travel, retail and promotions. Confirm model ml, approximate oz class, lid seal, custom plastic materials, colors, logo and packing.'],
  '/collections/titanium-vacuum-cups/': ['Titanium Vacuum Cups Wholesale OEM Factory | XUYI', 'B2B titanium vacuum cups for insulated drinkware sourcing. Confirm factory ml, approximate oz class, titanium grade, lid and seal materials, finish, logo and test documents by SKU.']
};

function innerMain(html) {
  const match = html.match(/<main id="main-content">([\s\S]*?)<\/main>/i);
  if (!match) throw new Error('English collection page has no main content');
  return match[1];
}
async function liveMain(route) {
  const response = await fetch(ORIGIN + route, {headers: {'user-agent': 'XUYI-D1-SEO-Maintenance/1.0'}});
  if (!response.ok) throw new Error('Cannot read ' + route + ': HTTP ' + response.status);
  return innerMain(await response.text());
}
function replaceOne(body, pattern, replacement) {
  const next = body.replace(pattern, replacement);
  if (next === body) throw new Error('Expected collection markup not found');
  return next;
}
function makeBody(route, locale, source) {
  const copy = category[route];
  let body = source;
  const h1 = copy.h1[locale];
  const intro = copy.intro[locale];
  body = body.replace(/<h1\b[^>]*>[\s\S]*?<\/h1>/i, '<h1>' + h1 + '</h1>');
  body = body.replace(/(<section class="page-intro">[\s\S]*?<h1>[\s\S]*?<\/h1>\s*<p>)[\s\S]*?(<\/p>)/i, '$1' + intro + '$2');
  const labels = {
    es: {'>Home<': '>Inicio<', '>Products<': '>Productos<', '>All products<': '>Todos los productos<', '>View product ↗<': '>Ver producto ↗<'},
    pt: {'>Home<': '>Início<', '>Products<': '>Produtos<', '>All products<': '>Todos os produtos<', '>View product ↗<': '>Ver produto ↗<'},
    ru: {'>Home<': '>Главная<', '>Products<': '>Товары<', '>All products<': '>Все товары<', '>View product ↗<': '>Подробнее ↗<'},
    tr: {'>Home<': '>Ana sayfa<', '>Products<': '>Ürünler<', '>All products<': '>Tüm ürünler<', '>View product ↗<': '>Ürünü görüntüle ↗<'}
  }[locale] || {};
  for (const [from, to] of Object.entries(labels)) body = body.split(from).join(to);
  return body;
}

const sourceBodies = new Map();
for (const route of Object.keys(category)) sourceBodies.set(route, await liveMain(route));

for (const route of Object.keys(category)) {
  const copy = category[route];
  const page = currentPages.get(route);
  const meta = englishMeta[route];
  if (page && !/OEM|Manufacturer|Factory/i.test(page.seo_title || '')) {
    await query(
      'UPDATE site_pages SET seo_title=?,meta_description=?,updated_at=CURRENT_TIMESTAMP WHERE route=? AND seo_title=? AND meta_description=?',
      [meta[0], meta[1], route, page.seo_title, page.meta_description]
    );
  }
  if (!currentBodies.has(route)) {
    const body = makeBody(route, 'en', sourceBodies.get(route));
    await query(
      'INSERT INTO xuyi_page_content(route,main_html,publication_status,updated_at) VALUES(?,?,?,CURRENT_TIMESTAMP) ON CONFLICT(route) DO NOTHING',
      [route, body, 'published']
    );
  }
}

const missingCollections = [
  '/collections/spray-water-bottles/',
  '/collections/two-way-drinking-cups/',
  '/collections/titanium-vacuum-cups/'
];
const locales = ['es', 'pt', 'ru', 'tr'];
let insertedTranslations = 0;
for (const route of missingCollections) {
  const source = sourceBodies.get(route);
  for (const locale of locales) {
    const id = 'page:' + route;
    if (currentTranslations.has(id + '|' + locale)) continue;
    const copy = category[route];
    const title = locale === 'es'
      ? (route.includes('spray') ? 'Botellas con Pulverizador B2B al por Mayor OEM | XUYI' : route.includes('two-way') ? 'Vasos de Doble Modo B2B al por Mayor OEM | XUYI' : 'Vasos Térmicos de Titanio B2B al por Mayor OEM | XUYI')
      : locale === 'pt'
        ? (route.includes('spray') ? 'Garrafas com Borrifador B2B para Atacado OEM | XUYI' : route.includes('two-way') ? 'Copos de Dupla Função B2B para Atacado OEM | XUYI' : 'Copos Térmicos de Titânio B2B para Atacado OEM | XUYI')
        : locale === 'ru'
          ? (route.includes('spray') ? 'Бутылки с распылителем B2B оптом OEM | XUYI' : route.includes('two-way') ? 'Кружки с двумя способами питья B2B оптом OEM | XUYI' : 'Титановые вакуумные термокружки B2B оптом OEM | XUYI')
          : (route.includes('spray') ? 'B2B Spreyli Su Mataraları Toptan OEM | XUYI' : route.includes('two-way') ? 'B2B İki İçim Seçenekli Bardaklar Toptan OEM | XUYI' : 'B2B Titanyum Vakumlu Termos Bardaklar Toptan OEM | XUYI');
    const description = copy.intro[locale];
    const body = makeBody(route, locale, source);
    await query(
      'INSERT INTO xuyi_translation_overrides(resource_id,locale,translated_json,reviewed_at) VALUES(?,?,?,CURRENT_TIMESTAMP) ON CONFLICT(resource_id,locale) DO NOTHING',
      ['page:' + route, locale, JSON.stringify({title, description, mainHtml: body})]
    );
    insertedTranslations++;
  }
}

await query("UPDATE site_state SET value=CAST(value AS INTEGER)+1,updated_at=CURRENT_TIMESTAMP WHERE key='publish_revision'");
console.log(JSON.stringify({
  database: database.name,
  revisionBefore: snapshot.publishRevision,
  seo: {inserted: insertedSeo, updated: updatedSeo, preserved: preservedSeo, unchanged: unchangedSeo},
  englishCollections: Object.keys(category).length,
  insertedTranslations,
  missingBefore: missingCollections.flatMap(route => locales.map(locale => 'page:' + route + '|' + locale)).filter(id => !currentTranslations.has(id))
}, null, 2));

const ghToken = process.env.GITHUB_TOKEN;
if (!ghToken) throw new Error('Missing GITHUB_TOKEN');
const dispatch = await fetch('https://api.github.com/repos/chongwuhou/xuyi-drinkware-site/actions/workflows/publish-xuyi.yml/dispatches', {
  method: 'POST',
  headers: {
    authorization: 'Bearer ' + ghToken,
    accept: 'application/vnd.github+json',
    'x-github-api-version': '2022-11-28',
    'content-type': 'application/json',
    'user-agent': 'XUYI-D1-SEO-Maintenance/1.0'
  },
  body: JSON.stringify({ref: 'main'})
});
if (!dispatch.ok) throw new Error('Cannot dispatch publisher: HTTP ' + dispatch.status + ' ' + (await dispatch.text()).slice(0, 500));
console.log('PUBLISH_DISPATCHED');
