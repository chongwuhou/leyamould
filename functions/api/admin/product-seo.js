// Unified, owner-editable SEO title/description records in the existing D1
// CMS. Each product × locale is an independent authoritative row.
import {authorizeAdminRequest} from "../../_shared/admin-security.js";
import {MANAGED_MODELS} from "../../_shared/xuyi-routes.js";
import {bumpPublishRevision,defaultLanguageConfig,loadSiteSetting,normalizeLanguageConfig,publicLanguages} from "../../_shared/site-settings.js";
import {ensureProductSeo,canonicalProductSlug,normalizeProductSeo,upsertProductSeo,configuredProductSeoLocales} from "../../_shared/product-seo.js";

const respond=(body,status=200)=>Response.json(body,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
async function ready(c){
 if(!c.env.ADMIN_TOKEN)return {error:respond({error:"Admin not configured"},503)};
 if(!(await authorizeAdminRequest(c.request,c.env)))return {error:respond({error:"Unauthorized"},401)};
 if(!c.env.XUYI_DB)return {error:respond({error:"XUYI_DB unavailable"},503)};
 const db=c.env.XUYI_DB;await ensureProductSeo(db);return {db};
}
async function hasProduct(db,slug){
 if([...MANAGED_MODELS].some(model=>canonicalProductSlug(model)===slug))return true;
 let product;try{product=await db.prepare("SELECT content_json,publication_status FROM xuyi_product_content WHERE model=?")
   .bind(slug).first()}catch{return false}
 try{return product?.publication_status==="published"&&JSON.parse(product.content_json)?.newProduct===true}
 catch{return false}
}
export async function onRequestGet(c){
 const {db,error}=await ready(c);if(error)return error;
 const rows=(await db.prepare("SELECT slug,locale,seo_title,meta_description,updated_at FROM xuyi_product_seo ORDER BY slug,locale LIMIT 2000").all()).results||[];
 const saved=await loadSiteSetting(db,"language_config",defaultLanguageConfig());
 const languageConfig=normalizeLanguageConfig(saved.value);
 let newModels=[];try{newModels=(await db.prepare("SELECT model FROM xuyi_product_content WHERE publication_status='published' ORDER BY model LIMIT 1000").all()).results||[]}catch{}
 const models=[...new Set([...MANAGED_MODELS].map(canonicalProductSlug),...newModels.map(row=>canonicalProductSlug(row.model)))].sort();
 const languages=languageConfig.languages.map(language=>({code:language.code,name:language.nativeName||language.displayName||language.code,
  displayName:language.displayName,nativeName:language.nativeName,enabled:language.enabled,publishReady:language.publishReady,pathPrefix:language.pathPrefix}));
 return respond({models,productCount:models.length,sourceLocale:languageConfig.sourceLocale,defaultLocale:languageConfig.defaultLocale,
  publishableLocales:publicLanguages(languageConfig).map(language=>language.code),languages,
  items:rows.map(r=>({slug:r.slug,locale:r.locale,seoTitle:r.seo_title,
    metaDescription:r.meta_description,updatedAt:r.updated_at}))});
}
export async function onRequestPost(c){
 const {db,error}=await ready(c);if(error)return error;
 let input;try{input=await c.request.json()}catch{return respond({error:"Invalid JSON"},400)}
 if(input?.action!=="save")return respond({error:"Unknown action"},400);
 const localeConfig=await configuredProductSeoLocales(db);
 let value;try{value=normalizeProductSeo(input,localeConfig.locales)}catch(e){return respond({error:e.message},400)}
 if(!await hasProduct(db,value.slug))return respond({error:"产品型号不属于已发布的 XUYI 目录"},400);
 await upsertProductSeo(db,{slug:value.slug,locale:value.locale,seoTitle:value.title,metaDescription:value.description});
 const revision=await bumpPublishRevision(db);
 return respond({saved:true,slug:value.slug,locale:value.locale,...revision});
}
