// LEYA MOULD category copy/SEO CMS. Only the allow-listed mould categories are editable.
import { authorizedBuildRequest } from "../../_shared/build-auth.js";
import { bumpPublishRevision,loadLanguageConfig } from "../../_shared/site-settings.js";
import { MANAGED_MODELS, MOULD_PUBLIC_ROUTES, mouldRoute } from "../../_shared/mould-routes.js";
import { authorizeAdminRequest } from "../../_shared/admin-security.js";
import { normalizeNewProduct,CATEGORY_OPTIONS } from "../../_shared/new-product.js";
import { imageKey } from "../../_shared/r2-usage.js";
import {ensureProductSeo,canonicalProductSlug,normalizeProductSeo,upsertProductSeo} from "../../_shared/product-seo.js";
const respond=(body,status=200)=>Response.json(body,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
const clean=(v,n=500)=>String(v??"").trim().slice(0,n);
function structuredSections(value){
  if(!Array.isArray(value)||value.length>8||value.some(row=>!row||typeof row!=="object"||Array.isArray(row)))throw Error("Invalid structured sections");
  return value.map(row=>{
    const title=clean(row.title,180),body=clean(row.body,1800),bullets=Array.isArray(row.bullets)?row.bullets.map(x=>clean(x,240)).filter(Boolean).slice(0,8):[];
    if(!title||!body)return null;
    return {title,body,bullets};
  }).filter(Boolean);
}
function structuredFaqs(value){
  if(!Array.isArray(value)||value.length>12||value.some(row=>!row||typeof row!=="object"||Array.isArray(row)))throw Error("Invalid product FAQs");
  return value.map(row=>{const question=clean(row.question,240),answer=clean(row.answer,1800);if(!question||!answer)return null;return {question,answer};}).filter(Boolean);
}
function categoryCopy(value){
  if(!value||typeof value!=="object"||Array.isArray(value))throw Error("Invalid category copy");
  if(JSON.stringify(value).length>120000)throw Error("Category copy is too large");
  const text=(x,n=1800)=>clean(x,n);
  const media=x=>{const v=text(x,500);if(v&&!(/^(?:\/|https?:\/\/)/.test(v)))throw Error("Category media must be a site path or HTTPS URL");return v;};
  const rows=(input,limit,mapper)=>{
    if(!Array.isArray(input)||input.length>limit)throw Error("Invalid category list");
    return input.map(mapper).filter(Boolean);
  };
  const out={};
  const hero=value.hero;
  if(hero&&typeof hero==="object"&&!Array.isArray(hero)){
    out.hero={title:text(hero.title,180),accent:text(hero.accent,180),subtitle:text(hero.subtitle,180),image:media(hero.image),stats:rows(hero.stats||[],8,row=>{
      const number=text(row?.number,40),label=text(row?.label,120);
      return number||label?{number,label}:null;
    })};
  }
  out.products=rows(value.products||[],12,row=>({title:text(row?.title,240),image:media(row?.image),body:text(row?.body,1800)}));
  out.advantages=rows(value.advantages||[],12,row=>({title:text(row?.title,240),body:text(row?.body,1800)}));
  const tech=value.technology;
  if(tech&&typeof tech==="object"&&!Array.isArray(tech))out.technology={title:text(tech.title,240),items:rows(tech.items||[],8,row=>({title:text(row?.title,240),body:text(row?.body,1800),image:media(row?.image),bullets:Array.isArray(row?.bullets)?row.bullets.map(x=>text(x,240)).filter(Boolean).slice(0,8):[]}))};
  out.samples=rows(value.samples||[],24,row=>({image:media(row?.image),alt:text(row?.alt,240)}));
  out.quality=rows(value.quality||[],12,row=>({label:text(row?.label,40),title:text(row?.title,240),body:text(row?.body,1800)}));
  out.testimonials=rows(value.testimonials||[],12,row=>({quote:text(row?.quote,1800),author:text(row?.author,160),country:text(row?.country,100)}));
  out.videos=rows(value.videos||[],24,row=>({videoId:/^[A-Za-z0-9_-]{11}$/.test(String(row?.videoId||""))?String(row.videoId):"",title:text(row?.title,240)}));
  return out;
}
async function ensure(db){await db.prepare(`CREATE TABLE IF NOT EXISTS xuyi_product_content(
  model TEXT PRIMARY KEY,
  content_json TEXT NOT NULL DEFAULT '{}',
  publication_status TEXT NOT NULL DEFAULT 'draft' CHECK(publication_status IN ('draft','published')),
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)`).run();}
async function auth(c){
  if(!c.env.ADMIN_TOKEN)return respond({error:"Admin not configured"},503);
  if(!(await authorizedBuildRequest(c.request,c.env)))return respond({error:"Unauthorized"},401);
  if(!c.env.LEYA_DB)return respond({error:"LEYA_DB unavailable"},503);
  return null;
}
export async function onRequestGet(context){
  const denied=await auth(context);if(denied)return denied;
  const db=context.env.LEYA_DB;await ensure(db);
  const rows=(await db.prepare("SELECT model,content_json,publication_status,updated_at FROM xuyi_product_content ORDER BY model LIMIT 1000").all()).results||[];
  // D1 stores reviewed category overrides, not the checked-in catalogue.
  return respond({categories:CATEGORY_OPTIONS,catalogModels:[...MANAGED_MODELS].sort(),
    modelRoutes:Object.fromEntries(MOULD_PUBLIC_ROUTES),
    items:rows.map(r=>({model:r.model,route:mouldRoute(r.model),content:JSON.parse(r.content_json),status:r.publication_status,updatedAt:r.updated_at}))});
}
export async function onRequestPost(context){
  const denied=await auth(context);if(denied)return denied;
  let p;try{p=await context.request.json()}catch{return respond({error:"Invalid JSON"},400)}
  if(p?.action==="create_product"){
    // New products may only be authored by authenticated humans, not CI.
    if(!(await authorizeAdminRequest(context.request,context.env)))return respond({error:"Admin authorization required"},401);
    const model=clean(p.model,80);
    const status=p.status==="published"?"published":"draft";
    // The frozen public renderer currently exposes only the registered mould
    // categories. A new D1 row may be prepared as a draft, but claiming it is
    // published before its route/detail specification is registered would
    // leave a successful CMS write with no public page.
    if(status==="published"&&!MANAGED_MODELS.has(model))
      return respond({error:"This mould category is draft-only until its LEYA route and detail template are registered"},409);
    let content;
    try{content=normalizeNewProduct(model,p.content,status)}
    catch(error){return respond({error:String(error.message||error)},400)}
    const db=context.env.LEYA_DB;await ensure(db);
    const prior=await db.prepare("SELECT content_json FROM xuyi_product_content WHERE model=?").bind(model).first();
    if(prior){
      if(p.createOnly===true)return respond({error:"Model already exists; create-only import will not overwrite"},409);
      let previous;
      try{previous=JSON.parse(prior.content_json)}catch{return respond({error:"Existing product JSON invalid"},409)}
      if(previous.newProduct!==true)return respond({error:"Model already owned by legacy catalog"},409);
    }
    if(status==="published"){
      const match=/^\/media\/([a-z]+)\/([a-zA-Z0-9._-]+)$/.exec(content.image);
      const key=match?imageKey(match[1],match[2]):null;
      if(!key||!context.env.LEYA_ASSETS)return respond({error:"A verified R2 image is required before publication"},409);
      let object;
      try{object=await context.env.LEYA_ASSETS.head(key)}
      catch{return respond({error:"Could not verify product photo in LEYA R2"},503)}
      if(!object)return respond({error:"Product image not present in LEYA R2"},409);
    }
    const saveSql=p.createOnly===true
      ? `INSERT INTO xuyi_product_content(model,content_json,publication_status,updated_at)
         VALUES(?,?,?,CURRENT_TIMESTAMP) ON CONFLICT(model) DO NOTHING`
      : `INSERT INTO xuyi_product_content(model,content_json,publication_status,updated_at)
         VALUES(?,?,?,CURRENT_TIMESTAMP)
         ON CONFLICT(model) DO UPDATE SET content_json=excluded.content_json,
         publication_status=excluded.publication_status,updated_at=CURRENT_TIMESTAMP`;
    const saved=await db.prepare(saveSql).bind(model,JSON.stringify(content),status).run();
    // The preflight SELECT improves the normal UX; this atomic insert is the real
    // no-overwrite guard when two admins import the same model concurrently.
    if(p.createOnly===true&&Number(saved?.meta?.changes??0)!==1)
      return respond({error:"Model already exists; create-only import will not overwrite"},409);
    const revision=await bumpPublishRevision(db);
    return respond({saved:true,model,status,newProduct:true,route:"/product/"+model+".html",
       locales:"Source language only until each translation is reviewed",...revision});
  }
  if(p?.action!=="save_product")return respond({error:"Unknown action"},400);
  const model=clean(p.model,80),v=p.content||{},status=p.status==="published"?"published":"draft";
  if(!/^[a-z0-9][a-z0-9-]{1,80}$/.test(model))return respond({error:"Invalid mould category slug"},400);
  if(!MANAGED_MODELS.has(model))return respond({error:"Mould category not found in the current LEYA catalog"},400);
  if(!v||typeof v!=="object"||Array.isArray(v))return respond({error:"Invalid product content"},400);
  const db=c.env.LEYA_DB;await ensure(db);
  const allowed=["title","navTitle","name","description","short","detail","meta","route","checks","capacity","material","colors","packing","dimensions","carton_quantity","carton_size","image","seoTitle","seoDescription","body","bodyEs","sections","sectionsEs","faqs","faqsEs","category"];
  let content={};
  const previousRow=await db.prepare("SELECT content_json FROM xuyi_product_content WHERE model=?").bind(model).first();
  try{content=previousRow?.content_json?JSON.parse(previousRow.content_json):{};}catch{return respond({error:"Existing product JSON invalid"},409)}
  for(const key of allowed)if(Object.hasOwn(v,key)){
    if(key==="checks"){
      if(!Array.isArray(v[key])||v[key].length>12||v[key].some(item=>typeof item!=="string"||item.length>240))return respond({error:"Invalid checks"},400);
      content[key]=v[key].map(item=>item.trim()).filter(Boolean); continue;
    }
    if(key==="sections"||key==="sectionsEs"){try{content[key]=structuredSections(v[key]);}catch(error){return respond({error:String(error.message||error)},400)};continue;}
    if(key==="faqs"||key==="faqsEs"){try{content[key]=structuredFaqs(v[key]);}catch(error){return respond({error:String(error.message||error)},400)};continue;}
    if(key==="category"){try{content[key]=categoryCopy(v[key]);}catch(error){return respond({error:String(error.message||error)},400)};continue;}
    if(typeof v[key]!=="string"||v[key].length>3000)return respond({error:"Invalid "+key},400);
    content[key]=v[key].trim();
  }
  if(status==="published"&&(!content.title&&!content.name||!content.description))return respond({error:"Published mould category requires title and description"},400);
  if(content.seoTitle||content.seoDescription){
    await ensureProductSeo(db);
    const slug=canonicalProductSlug(model);
     const sourceLocale=(await loadLanguageConfig(db)).sourceLocale;
     const previous=await db.prepare("SELECT seo_title,meta_description FROM xuyi_product_seo WHERE slug=? AND locale=?")
       .bind(slug,sourceLocale).first();
    const title=content.seoTitle||previous?.seo_title;
    const desc=content.seoDescription||previous?.meta_description;
    if(!title||!desc)return respond({error:"SEO title and description must both be provided for a new record"},400);
     try{normalizeProductSeo({slug,locale:sourceLocale,seoTitle:title,metaDescription:desc})}
    catch(err){return respond({error:String(err.message||err)},400)}
     await upsertProductSeo(db,{slug,locale:sourceLocale,seoTitle:title,metaDescription:desc});
  }
  await db.prepare(`INSERT INTO xuyi_product_content(model,content_json,publication_status,updated_at) VALUES(?,?,?,CURRENT_TIMESTAMP)
    ON CONFLICT(model) DO UPDATE SET content_json=excluded.content_json,publication_status=excluded.publication_status,updated_at=CURRENT_TIMESTAMP`)
    .bind(model,JSON.stringify(content),status).run();
  const revision=await bumpPublishRevision(db);
  return respond({saved:true,model,status,route:mouldRoute(model),...revision});
}



