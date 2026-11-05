const ORIGIN = 'https://xuyibottles.com';
const REPOSITORY = 'chongwuhou/xuyi-drinkware-site';
const TOKEN = process.env.CLOUDFLARE_API_TOKEN;
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;

if (!TOKEN) throw new Error('Missing CLOUDFLARE_API_TOKEN');
if (!GITHUB_TOKEN) throw new Error('Missing GITHUB_TOKEN');

async function callSite(path, method = 'GET', body) {
  const response = await fetch(ORIGIN + path, {
    method,
    headers: {
      authorization: 'Bearer ' + TOKEN,
      accept: 'application/json',
      'content-type': 'application/json',
      'cache-control': 'no-store',
      'user-agent': 'XUYI-D1-SEO-Maintenance/1.8'
    },
    body: body === undefined ? undefined : JSON.stringify(body)
  });
  const text = await response.text();
  let payload;
  try {
    payload = JSON.parse(text);
  } catch {
    throw new Error('Invalid JSON from ' + path + ': ' + text.slice(0, 300));
  }
  if (!response.ok || payload.error) {
    throw new Error('HTTP ' + response.status + ' from ' + path + ': ' + JSON.stringify(payload).slice(0, 1000));
  }
  return payload;
}

async function runFixedMigration(path, label, expectedCount) {
  const initial = await callSite(path);
  if (initial.reviewed !== expectedCount) {
    throw new Error(label + ' source count mismatch: ' + JSON.stringify(initial));
  }

  const hasMissing = Array.isArray(initial.missing)
    ? initial.missing.length > 0
    : Array.isArray(initial.missingRows) && initial.missingRows.length > 0;

  const needsBatches = hasMissing ||
    Number(initial.titleEligible || 0) > 0 ||
    Number(initial.descriptionEligible || 0) > 0;
  if (needsBatches) {
    for (let index = 0; index < initial.batchCount; index += 1) {
      const result = await callSite(path, 'POST', {action: 'batch', batchIndex: index});
      if (result.missingRows && result.missingRows.length) {
        throw new Error(label + ' lost rows during batch ' + index);
      }
      if (index % 8 === 0 || index + 1 === initial.batchCount) {
        console.log(label + '_BATCH', index + 1, '/', initial.batchCount, JSON.stringify(result));
      }
    }
  }

  const finalState = await callSite(path);
  const finalMissing = Array.isArray(finalState.missing)
    ? finalState.missing.length
    : Array.isArray(finalState.missingRows) ? finalState.missingRows.length : 0;
  if (finalMissing || finalState.persisted !== undefined && finalState.persisted !== expectedCount) {
    throw new Error(label + ' did not account for every reviewed row: ' + JSON.stringify(finalState));
  }

  const finalized = await callSite(path, 'POST', {action: 'finalize'});
  if (!finalized.complete) {
    throw new Error(label + ' finalization failed: ' + JSON.stringify(finalized));
  }
  console.log(label + '_COMPLETE', JSON.stringify({
    reviewed: expectedCount,
    revision: finalized.revision,
    persisted: finalState.persisted,
    titleEligible: finalState.titleEligible,
    descriptionEligible: finalState.descriptionEligible
  }));
  return finalized;
}

await runFixedMigration(
  '/api/admin/product-seo-promotion-20261020',
  'PRODUCT_SEO_SOURCE_BACKFILL',
  505
);
await runFixedMigration(
  '/api/admin/product-seo-refresh-20261104',
  'PRODUCT_SEO_REVIEWED_REFRESH',
  505
);

const snapshot = await callSite('/api/build-snapshot');
const productSeo = Array.isArray(snapshot.productSeo) ? snapshot.productSeo : [];
if (productSeo.length < 505) {
  throw new Error('Live D1 snapshot still exposes fewer than 505 product SEO rows: ' + productSeo.length);
}
const failingMaterialRows = productSeo.filter(row => {
  const description = String(row.meta_description ?? row.metaDescription ?? '');
  return ['2505', '2506', '2507'].includes(String(row.slug)) &&
    (!description.includes('Tritan') || !description.includes('BPA-free'));
});
if (failingMaterialRows.length) {
  throw new Error('Material-language verification failed after D1 refresh: ' + JSON.stringify(failingMaterialRows));
}


async function migrateCollections() {
  const routes = [
    '/collections/kids-water-bottles/',
    '/collections/large-capacity-water-jugs/',
    '/collections/plastic-shaker-bottles/',
    '/collections/sports-water-bottles/',
    '/collections/spray-water-bottles/',
    '/collections/two-way-drinking-cups/',
    '/collections/titanium-vacuum-cups/'
  ];
  for (const route of routes) {
    const response = await fetch(ORIGIN + route, {
      headers: {
        accept: 'text/html',
        'cache-control': 'no-store',
        'user-agent': 'XUYI-D1-SEO-Maintenance/1.5'
      }
    });
    if (!response.ok) {
      throw new Error('Cannot read published collection ' + route + ': HTTP ' + response.status);
    }
    const html = await response.text();
    const match = html.match(/<main id="main-content">([\s\S]*?)<\/main>/i);
    if (!match || match[1].length < 500) {
      throw new Error('Published collection has no usable main body: ' + route);
    }
    const result = await callSite(
      '/api/admin/collection-seo-refresh-20261105',
      'POST',
      {action: 'seed', route, sourceHtml: match[1]}
    );
    console.log('COLLECTION_D1_SEED', route, JSON.stringify(result));
  }
  const state = await callSite('/api/admin/collection-seo-refresh-20261105');
  if (state.englishBodies < routes.length || state.expectedMissingLocalized > 0) {
    throw new Error('Collection D1 migration incomplete: ' + JSON.stringify(state));
  }
  console.log('COLLECTION_D1_LOCALES_VERIFIED', JSON.stringify(state));
}

await migrateCollections();

const dispatch = await fetch(
  'https://api.github.com/repos/' + REPOSITORY + '/actions/workflows/publish-xuyi.yml/dispatches',
  {
    method: 'POST',
    headers: {
      authorization: 'Bearer ' + GITHUB_TOKEN,
      accept: 'application/vnd.github+json',
      'x-github-api-version': '2022-11-28',
      'content-type': 'application/json',
      'user-agent': 'XUYI-D1-SEO-Maintenance/1.0'
    },
    body: JSON.stringify({ref: 'main'})
  }
);
if (!dispatch.ok) {
  throw new Error('Cannot dispatch publisher: HTTP ' + dispatch.status + ' ' + (await dispatch.text()).slice(0, 500));
}
console.log('PRODUCT_SEO_D1_REFRESH_VERIFIED');
console.log('PUBLISH_DISPATCHED');
