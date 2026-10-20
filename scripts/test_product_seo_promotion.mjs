import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {REVIEWED_SEO_SOURCE} from "../functions/_shared/reviewed-product-seo-20261020.js";
import {REVIEWED_COUNT,expectedReviewedRows,selectAuthorizedCopy} from "../functions/api/admin/product-seo-promotion-20261020.js";
import {normalizeProductSeo,canonicalProductSlug} from "../functions/_shared/product-seo.js";
import {onRequestGet} from "../functions/api/admin/product-seo.js";

assert.equal(REVIEWED_COUNT,505);
assert.equal(expectedReviewedRows().size,505);
const categories=new Map();
const locales=new Map();
for(const r of REVIEWED_SEO_SOURCE){
  categories.set(r.source,1+(categories.get(r.source)||0));
  locales.set(r.locale,1+(locales.get(r.locale)||0));
  const cleaned=normalizeProductSeo({slug:r.slug,locale:r.locale,seoTitle:r.newTitle,metaDescription:r.newDescription});
  assert.equal(cleaned.title,r.newTitle);
  assert.equal(cleaned.description,r.newDescription);
  const original=r.ownerRoute?{route:r.ownerRoute,title:r.oldTitle,description:r.oldDescription}:null;
  const selected=selectAuthorizedCopy(r,original);
  assert.equal(selected.title,r.newTitle,"Unedited source must promote approved title");
  assert.equal(selected.description,r.newDescription);
  if(original){
    const owner={...original,title:"Owner edited valid actual SKU title "+r.slug,
      description:"The site owner independently edited this product SEO description for the exact model and locale."};
    const preserved=selectAuthorizedCopy(r,owner);
    assert.equal(preserved.title,owner.title,"Custom editor title wins");
    assert.equal(preserved.description,owner.description,"Custom editor description wins");
    assert.equal(preserved.source,"owner");
    assert.equal(selectAuthorizedCopy(r,null).skip,"Previously recorded D1 source missing");
  }
}
assert.deepEqual(Object.fromEntries(categories),{verified_ml_oz:460,reviewed_no_capacity:5,official_source_default:40});
assert.deepEqual([...locales.values()],[101,101,101,101,101]);
assert.equal(canonicalProductSlug("2306透明款"),"2306-transparent");
assert.equal(canonicalProductSlug("LO-001"),"lo-001");
assert.equal(canonicalProductSlug("G-02"),"g-02");
for(const invalid of [
 {slug:"../../g-01",locale:"pt",seoTitle:"Fake title sufficient",metaDescription:"Fake full description of more than thirty characters"},
 {slug:"lo-001",locale:"fr",seoTitle:"Fake title sufficient",metaDescription:"Fake full description of more than thirty characters"},
 {slug:"lo-001",locale:"en",seoTitle:"x",metaDescription:"Fake full description of more than thirty characters"}
])assert.throws(()=>normalizeProductSeo(invalid));
const pageApi=readFileSync("functions/api/admin/pages.js","utf8");
assert(!pageApi.includes('db.prepare("DELETE FROM site_pages")'),
  "The old bulk editor must never erase future-product or source-approved D1 records");
assert(pageApi.includes("ON CONFLICT(route) DO UPDATE"));
assert(readFileSync("functions/api/admin/page-translations.js","utf8").includes("xuyi_product_seo"));
assert(readFileSync("functions/api/admin/product-content.js","utf8").includes("upsertProductSeo"));
assert(readFileSync("functions/api/build-snapshot.js","utf8").includes("productSeo:productSeo"));
assert.equal((await onRequestGet({request:new Request("https://xuyibottles.com/api/admin/product-seo"),
  env:{ADMIN_TOKEN:"test-admin-secret"}})).status,401);
console.log("XUYI_D1_PRODUCT_SEO_505_EXACT_MODELS_5_LOCALES_APPROVED_SOURCE_ADMIN_PRESERVED_PASS");
