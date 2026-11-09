// Unified, owner-editable product SEO and localized body records in the existing D1 CMS.
import {authorizeAdminRequest} from "../../_shared/admin-security.js";
import {MANAGED_MODELS} from "../../_shared/xuyi-routes.js";
import {bumpPublishRevision,defaultLanguageConfig,loadSiteSetting,normalizeLanguageConfig,publicLanguages} from "../../_shared/site-settings.js";
import {ensureProductSeo,canonicalProductSlug,normalizeProductSeo,upsertProductSeo,configuredProductSeoLocales} from "../../_shared/product-seo.js";
import {ensureTranslationSchema} from "../../_shared/translation.js";

const respond=(body,status=200)=>Response.json(body,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
const BLOCKED_HTML=/<\s*(?:script|iframe|object|embed|form|style|link|base|meta|svg|math|template)\b|\bon[a-z-]+\s*=|\bsrcdoc\s*=|(?:javascript|vbscript|data)\s*:/i;
const clean=(value,max=4000)=>String(value??"").replace(/\0/g,"").trim().slice(0,max);
const parseJson=(value,fallback={})=>{try{const parsed=JSON.parse(String(value||""));return parsed&&typeof parsed==="object"&&!Array.isArray(parsed)?parsed:fallback}catch{return fallback}};
const safeProductHtml=html=>html.length>=120&&html.length<=250000&&/<(?:section|article|div|h1)\b/i.test(html)&&!BLOCKED_HTML.test(html);
async function ready(c){
 if(!c.env.ADMIN_TOKEN)return {error:respond({error:"Admin not configured"},503)};
 if(!(await authorizeAdminRequest(c.request,c.env)))return {error:respond({error:"Unauthorized"},401)};
 if(!c.env.XUYI_DB)return {error:respond({error:"XUYI_DB unavailable"},503)};
 const db=c.env.XUYI_DB;await ensureProductSeo(db);return {db};
}
async function hasProduct(db,slug){
 if([...MANAGED_MODELS].some(model=>canonicalProductSlug(model)===slug))return true;
 let product;try{product=await db.prepare("SELECT content_json FROM xuyi_product_content WHERE model=?").bind(slug).first()}catch{return false}
 try{return parseJson(product?.content_json).newProduct===true}catch{return false}
}
export async function onRequestGet(c){
 const {db,error}=await ready(c);if(error)return error;
 const saved=await loadSiteSetting(db,"language_config",defaultLanguageConfig());
 const languageConfig=normalizeLanguageConfig(saved.value);
 const requestUrl=new URL(c.request.url);
 const requestedSlug=String(requestUrl.searchParams.get("slug")||"").trim();
 const requestedLocale=String(requestUrl.searchParams.get("locale")||"").trim().toLowerCase();
 if(requestedSlug||requestedLocale){
  if(!requestedSlug||!requestedLocale)return respond({error:"Product content requires slug and locale"},400);
  const slug=canonicalProductSlug(requestedSlug);
  if(!await hasProduct(db,slug))return respond({error:"产品型号不属于当前 XUYI D1 目录"},400);
  const language=languageConfig.languages.find(item=>item.code===requestedLocale);
  if(!language)return respond({error:"Locale must exist in the D1 language registry"},400);
  if(requestedLocale===languageConfig.sourceLocale)
   return respond({slug,locale:requestedLocale,sourceManaged:true,content:null,hasContent:false});
  if(!language.enabled||!language.publishReady)return respond({error:"Locale is not publish-ready in D1"},409);
  await ensureTranslationSchema(db);
  const row=await db.prepare("SELECT translated_json FROM xuyi_translation_overrides WHERE resource_id=? AND locale=?").bind("page:/products/"+slug+"/",requestedLocale).first();
  const content=parseJson(row?.translated_json);
  return respond({slug,locale:requestedLocale,sourceManaged:false,content,hasContent:Boolean(content.mainHtml)});
 }
 const rows=(await db.prepare("SELECT slug,locale,seo_title,meta_description,updated_at FROM xuyi_product_seo ORDER BY slug,locale").all()).results||[];
 let newModels=[];try{newModels=(await db.prepare("SELECT model FROM xuyi_product_content ORDER BY model").all()).results||[];}catch{}
 const models=[...new Set([...MANAGED_MODELS].map(canonicalProductSlug),...newModels.map(row=>canonicalProductSlug(row.model)))].sort();
 const languages=languageConfig.languages.map(language=>({code:language.code,name:language.nativeName||language.displayName||language.code,
  displayName:language.displayName,nativeName:language.nativeName,enabled:language.enabled,publishReady:language.publishReady,pathPrefix:language.pathPrefix}));
 return respond({models,productCount:models.length,sourceLocale:languageConfig.sourceLocale,defaultLocale:languageConfig.defaultLocale,
  publishableLocales:publicLanguages(languageConfig).map(language=>language.code),languages,
  items:rows.map(r=>({slug:r.slug,locale:r.locale,seoTitle:r.seo_title,metaDescription:r.meta_description,updatedAt:r.updated_at}))});
}
export async function onRequestPost(c){
 const {db,error}=await ready(c);if(error)return error;
 let input;try{input=await c.request.json()}catch{return respond({error:"Invalid JSON"},400)}
 if(input?.action!=="save")return respond({error:"Unknown action"},400);
 const localeConfig=await configuredProductSeoLocales(db);
 let value;try{value=normalizeProductSeo(input,localeConfig.locales)}catch(e){return respond({error:e.message},400)}
 if(!await hasProduct(db,value.slug))return respond({error:"产品型号不属于当前 XUYI D1 目录"},400);
 const hasBodyField=Object.prototype.hasOwnProperty.call(input,"mainHtml");
 const mainHtml=hasBodyField?clean(input.mainHtml,250000):"";
 if(hasBodyField&&mainHtml&&value.locale===localeConfig.sourceLocale)return respond({error:"来源语言正文必须在产品商详入口维护"},409);
 const statements=[upsertProductSeo(db,{slug:value.slug,locale:value.locale,seoTitle:value.title,metaDescription:value.description})];
 let contentSaved=false;
 if(value.locale!==localeConfig.sourceLocale){
  await ensureTranslationSchema(db);
  const resourceId="page:/products/"+value.slug+"/";
  const existing=await db.prepare("SELECT translated_json FROM xuyi_translation_overrides WHERE resource_id=? AND locale=?").bind(resourceId,value.locale).first();
  const previous=parseJson(existing?.translated_json);
  const merged={...previous,title:value.title,description:value.description};
  if(mainHtml)merged.mainHtml=mainHtml;
  if(existing||mainHtml){
   if(mainHtml&&!safeProductHtml(mainHtml))return respond({error:"目标语种正文必须是完整且安全的 Main HTML"},400);
   statements.push(db.prepare("INSERT INTO xuyi_translation_overrides(resource_id,locale,translated_json,reviewed_at) VALUES(?,?,?,CURRENT_TIMESTAMP) ON CONFLICT(resource_id,locale) DO UPDATE SET translated_json=excluded.translated_json,reviewed_at=CURRENT_TIMESTAMP").bind(resourceId,value.locale,JSON.stringify(merged)));
   contentSaved=Boolean(mainHtml)||Boolean(existing);
  }
 }
 await db.batch(statements);
 const revision=await bumpPublishRevision(db);
 return respond({saved:true,contentSaved,slug:value.slug,locale:value.locale,...revision});
}