// D1 is the product metadata source of truth for every locale and SKU.
import {loadLanguageConfig,publicLanguages} from "./site-settings.js";
export const SEO_TABLE=`CREATE TABLE IF NOT EXISTS xuyi_product_seo (
  slug TEXT NOT NULL,
  locale TEXT NOT NULL,
  seo_title TEXT NOT NULL,
  meta_description TEXT NOT NULL,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(slug,locale)
)`;
export async function ensureProductSeo(db){await db.prepare(SEO_TABLE).run();}
export function canonicalProductSlug(model){
  const raw=String(model??"").trim();
  const transparent=/^(\d{3,4})透明款$/.exec(raw);
  return transparent?transparent[1]+"-transparent":raw.toLowerCase();
}
export function normalizeProductSeo(input,allowedLocales=null){
  const slug=String(input?.slug||"").trim().toLowerCase();
  const locale=String(input?.locale||"").trim().toLowerCase();
  const title=String(input?.seoTitle??"").trim();
  const description=String(input?.metaDescription??"").trim();
  if(!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)||slug.length>80)
    throw Error("Invalid canonical product slug");
 if(!/^[a-z]{2,3}(?:-[a-z0-9]{2,8})*$/.test(locale))throw Error("Invalid product SEO locale");
 if(allowedLocales&&!allowedLocales.has(locale))throw Error("Product SEO locale is not enabled in D1 language configuration");
  if(title.length<12||title.length>90||/[<>]/.test(title))
    throw Error("Product SEO title must have 12–90 safe characters");
  if(description.length<30||description.length>240||/[<>]/.test(description))
    throw Error("Product description must have 30–240 safe characters");
  return {slug,locale,title,description};
}
export async function upsertProductSeo(db,item){
 const config=await loadLanguageConfig(db);
 const allowed=new Set(publicLanguages(config).map(language=>language.code));
 const {slug,locale,title,description}=normalizeProductSeo(item,allowed);
  return db.prepare("INSERT INTO xuyi_product_seo (slug,locale,seo_title,meta_description,updated_at) "+
   "VALUES(?,?,?,?,CURRENT_TIMESTAMP) ON CONFLICT(slug,locale) DO UPDATE SET "+
   "seo_title=excluded.seo_title,meta_description=excluded.meta_description,updated_at=CURRENT_TIMESTAMP")
   .bind(slug,locale,title,description).run();
}

