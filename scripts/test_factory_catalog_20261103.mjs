import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {normalizeNewProduct} from "../functions/_shared/new-product.js";
import {normalizeAltMap} from "../functions/_shared/media-alt.js";

const bundle=JSON.parse(readFileSync(new URL("./fixtures/factory-catalog-import-2026-11-03.json",import.meta.url),"utf8"));
const manifest=JSON.parse(readFileSync(new URL("../data/factory-catalog-manifest-2026-11-03.json",import.meta.url),"utf8"));
const languages=["en","es","pt","ru","tr"];
assert.equal(bundle.records.length,58);
assert.equal(manifest.recordCount,58);
assert.equal(bundle.sourceSha256,manifest.sourceSha256);
const models=new Set();
for(const record of bundle.records){
  assert.ok(!models.has(record.model), "duplicate model "+record.model);
  models.add(record.model);
  const image="/media/product/"+record.imageSha256.slice(0,32)+".webp";
  const normalized=normalizeNewProduct(record.model,{...record.content,image},"published");
  assert.equal(normalized.sourceSha256,manifest.sourceSha256);
  assert.equal(normalized.image,image);
  const alt=normalizeAltMap(record.imageAlt);
  for(const language of languages)assert.ok(alt[language],record.model+" missing ALT "+language);
}
assert.equal(models.size,58);
console.log("PASS: 58 factory records satisfy the production product-content normalizer and five-language ALT schema.");