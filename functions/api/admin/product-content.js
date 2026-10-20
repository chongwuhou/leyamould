// XUYI product copy/SEO CMS. Do not mutate the source-import 151 draft rows.
import { authorizedBuildRequest } from "../../_shared/build-auth.js";
import { bumpPublishRevision } from "../../_shared/site-settings.js";
import { MANAGED_MODELS } from "../../_shared/xuyi-routes.js";
import { authorizeAdminRequest } from "../../_shared/admin-security.js";
import { normalizeNewProduct,CATEGORY_OPTIONS } from "../../_shared/new-product.js";
import { imageKey } from "../../_shared/r2-usage.js";
import {ensureProductSeo,canonicalProductSlug,normalizeProductSeo,upsertProductSeo} from "../../_shared/product-seo.js";
const respond=(body,status=200)=>Response.json(body,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
const clean=(v,n=500)=>String(v??"").trim().slice(0,n);
async function ensure(db){await db.prepare(`CREATE TABLE IF NOT EXISTS xuyi_product_content(
  model TEXT PRIMARY KEY,
  content_json TEXT NOT NULL DEFAULT '{}',
  publication_status TEXT NOT NULL DEFAULT 'draft' CHECK(publication_status IN ('draft','published')),
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)`).run();}
async function auth(c){
  if(!c.env.ADMIN_TOKEN)return respond({error:"Admin not configured"},503);
  if(!(await authorizedBuildRequest(c.request,c.env)))return respond({error:"Unauthorized"},401);
  if(!c.env.XUYI_DB)return respond({error:"XUYI_DB unavailable"},503);
  return null;
}
export async function onRequestGet(context){
  const denied=await auth(context);if(denied)return denied;
  const db=context.env.XUYI_DB;await ensure(db);
  const rows=(await db.prepare("SELECT model,content_json,publication_status,updated_at FROM xuyi_product_content ORDER BY model LIMIT 1000").all()).results||[];
  // D1 stores content overrides, not the original 93 product records.
  // Expose the allowlisted source models to the authenticated CMS picker,
  // including all eight LO models without writing synthetic D1 rows.
  return respond({categories:CATEGORY_OPTIONS,catalogModels:[...MANAGED_MODELS].sort(),
    items:rows.map(r=>({model:r.model,content:JSON.parse(r.content_json),status:r.publication_status,updatedAt:r.updated_at}))});
}
export async function onRequestPost(context){
  const denied=await auth(context);if(denied)return denied;
  let p;try{p=await context.request.json()}catch{return respond({error:"Invalid JSON"},400)}
  if(p?.action==="create_product"){
    // New products may only be authored by authenticated humans, not CI.
    if(!(await authorizeAdminRequest(context.request,context.env)))return respond({error:"Admin authorization required"},401);
    const model=clean(p.model,80);
    const status=p.status==="published"?"published":"draft";
    let content;
    try{content=normalizeNewProduct(model,p.content,status)}
    catch(error){return respond({error:String(error.message||error)},400)}
    const db=context.env.XUYI_DB;await ensure(db);
    const prior=await db.prepare("SELECT content_json FROM xuyi_product_content WHERE model=?").bind(model).first();
    if(prior){
      let previous;
      try{previous=JSON.parse(prior.content_json)}catch{return respond({error:"Existing product JSON invalid"},409)}
      if(previous.newProduct!==true)return respond({error:"Model already owned by legacy catalog"},409);
    }
    if(status==="published"){
      const match=/^\/media\/([a-z]+)\/([a-zA-Z0-9._-]+)$/.exec(content.image);
      const key=match?imageKey(match[1],match[2]):null;
      if(!key||!context.env.XUYI_ASSETS)return respond({error:"A verified R2 image is required before publication"},409);
      let object;
      try{object=await context.env.XUYI_ASSETS.head(key)}
      catch{return respond({error:"Could not verify product photo in XUYI R2"},503)}
      if(!object)return respond({error:"Product image not present in XUYI R2"},409);
    }
    await db.prepare(`INSERT INTO xuyi_product_content(model,content_json,publication_status,updated_at)
      VALUES(?,?,?,CURRENT_TIMESTAMP)
      ON CONFLICT(model) DO UPDATE SET content_json=excluded.content_json,
      publication_status=excluded.publication_status,updated_at=CURRENT_TIMESTAMP`)
      .bind(model,JSON.stringify(content),status).run();
    const revision=await bumpPublishRevision(db);
    return respond({saved:true,model,status,newProduct:true,route:"/products/"+model+"/",
      locales:"English only until each translation is reviewed",...revision});
  }
  if(p?.action!=="save_product")return respond({error:"Unknown action"},400);
  const model=clean(p.model,80),v=p.content||{},status=p.status==="published"?"published":"draft";
  if(!/^[a-zA-Z0-9_\-\u4e00-\u9fff]{1,80}$/.test(model))return respond({error:"Invalid model identifier"},400);
  if(!MANAGED_MODELS.has(model))return respond({error:"Model not found in the current XUYI catalog"},400);
  if(!v||typeof v!=="object"||Array.isArray(v))return respond({error:"Invalid product content"},400);
  const allowed=["name","description","capacity","material","colors","packing","dimensions","carton_quantity","carton_size","image","seoTitle","seoDescription"];
  const content={};
  for(const key of allowed)if(Object.hasOwn(v,key)){
    if(typeof v[key]!=="string"||v[key].length>3000)return respond({error:"Invalid "+key},400);
    content[key]=v[key].trim();
  }
  if(status==="published"&&(!content.name||!content.material))return respond({error:"Published product requires name and material"},400);
  const db=context.env.XUYI_DB;await ensure(db);
  if(content.seoTitle||content.seoDescription){
    await ensureProductSeo(db);
    const slug=canonicalProductSlug(model);
    const previous=await db.prepare("SELECT seo_title,meta_description FROM xuyi_product_seo WHERE slug=? AND locale='en'")
      .bind(slug).first();
    const title=content.seoTitle||previous?.seo_title;
    const desc=content.seoDescription||previous?.meta_description;
    if(!title||!desc)return respond({error:"SEO title and description must both be provided for a new record"},400);
    try{normalizeProductSeo({slug,locale:"en",seoTitle:title,metaDescription:desc})}
    catch(err){return respond({error:String(err.message||err)},400)}
    await upsertProductSeo(db,{slug,locale:"en",seoTitle:title,metaDescription:desc});
  }
  await db.prepare(`INSERT INTO xuyi_product_content(model,content_json,publication_status,updated_at) VALUES(?,?,?,CURRENT_TIMESTAMP)
    ON CONFLICT(model) DO UPDATE SET content_json=excluded.content_json,publication_status=excluded.publication_status,updated_at=CURRENT_TIMESTAMP`)
    .bind(model,JSON.stringify(content),status).run();
  const revision=await bumpPublishRevision(db);
  return respond({saved:true,model,status,...revision});
}
