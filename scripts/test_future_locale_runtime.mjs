import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {modelKey} from "../functions/_shared/model-overflow.js";
const load=path=>readFileSync(new URL("../"+path,import.meta.url),"utf8");
const encoded="data:text/javascript;base64,"+
  Buffer.from(load("functions/_shared/home-banners.js")).toString("base64");
const {normalizeBanners}=await import(encoded);
const current=JSON.parse(load("assets/home-banner-defaults.json"));
const future=structuredClone(current);
for(const slide of future.slides)
  slide.translations.fr={...slide.translations.es,title:"Isolated future-locale QA"};
const preserved=normalizeBanners(future,{requiredLocales:["en","es","pt","ru","tr","fr"]});
assert.equal(preserved.slides.length,3);
assert.equal(preserved.slides[2].translations.fr.title,"Isolated future-locale QA");
const incomplete=structuredClone(future);
delete incomplete.slides[1].translations.fr;
assert.throws(()=>normalizeBanners(incomplete,{requiredLocales:["fr"]}));
const malicious=structuredClone(future);
malicious.slides[0].translations["../fr"]=malicious.slides[0].translations.fr;
assert.throws(()=>normalizeBanners(malicious));
assert.equal(modelKey("/fr/products/2501/"),"models/2501.json");
assert.equal(modelKey("/pt-br/products/2501/"),"models/2501.json");
assert.equal(modelKey("/fr/private/2501/"),"");
assert.equal(modelKey("/admin/products/2501/"),"");
assert(!load("assets/site-settings.js").includes("^(en|es|pt|ru|tr)$"),
  "Front-end selector must derive supported locales dynamically");
assert(!load("assets/admin-content.js").includes(
  '<option value="es">Español</option><option value="pt">'),
  "New locales must be editable in the D1 CMS without hardcoded selectors");
console.log("XUYI_FUTURE_LOCALE_RUNTIME_TEST_PASSED dynamic banner and R2/JS language handling");
