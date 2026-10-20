// One-time idempotent XUYI metadata promotion from known source/CMS copy into
// canonical product SEO rows. Uses exact, reviewed allowlist in private repo.
// Never changes existing manual edits or blindly overwrites new D1 values.
import {authorizedProductSeoPromotionRequest} from "../../_shared/build-auth.js";
import {ensureProductSeo,normalizeProductSeo} from "../../_shared/product-seo.js";
import {bumpPublishRevision} from "../../_shared/site-settings.js";
import {REVIEWED_SEO_SOURCE} from "../../_shared/reviewed-product-seo-20261020.js";

const reply=(value,status=200)=>Response.json(value,{status,headers:{
 "cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
const LIMIT=15;
export const REVIEWED_COUNT=REVIEWED_SEO_SOURCE.length;
const chunkCount=Math.ceil(REVIEWED_COUNT/LIMIT);

export function expectedReviewedRows(){
 const seen=new Set();
 for(const r of REVIEWED_SEO_SOURCE){
  const entry=normalizeProductSeo({slug:r.slug,locale:r.locale,seoTitle:r.newTitle,
   metaDescription:r.newDescription});
  const key=entry.slug+"/"+entry.locale;
  if(seen.has(key))throw Error("Duplicate reviewed source key");
  seen.add(key);
  if(!["verified_ml_oz","reviewed_no_capacity","official_source_default"].includes(r.source))
    throw Error("Unreviewed SEO source");
 }
 if(seen.size!==505||REVIEWED_COUNT!==505)throw Error("Wrong one-time reviewed SKU count");
 return seen;
}
expectedReviewedRows();

async function prepare(c){
 if(!await authorizedProductSeoPromotionRequest(c.request,c.env))
  return {error:reply({error:"Unauthorized"},401)};
 if(!c.env.XUYI_DB)return {error:reply({error:"Missing D1 binding"},503)};
 const db=c.env.XUYI_DB;await ensureProductSeo(db);return {db};
}
async function currentLegacy(db,record){
 const route="/products/"+record.slug+"/";
 const possible=[route,...(record.ownerRoute&&record.ownerRoute!==route?[record.ownerRoute]:[])];
 for(const target of possible){
  if(record.locale==="en"){
   const row=await db.prepare("SELECT seo_title,meta_description FROM site_pages WHERE route=?").bind(target).first();
   if(row)return {route:target,title:row.seo_title,description:row.meta_description,kind:"page"};
  }else{
   const row=await db.prepare("SELECT translated_json FROM xuyi_translation_overrides WHERE resource_id=? AND locale=?")
    .bind("page:"+target,record.locale).first();
   if(row){
    let content;try{content=JSON.parse(row.translated_json)}catch{return {invalid:true}}
    return {route:target,title:content.title,description:content.description,kind:"translation",raw:row.translated_json,content};
   }
  }
 }
 return null;
}
export function selectAuthorizedCopy(record,owner){
 if(owner?.invalid)return {skip:"Invalid owner JSON"};
 if(!owner){
  if(record.ownerRoute)return {skip:"Previously recorded D1 source missing"};
  return {title:record.newTitle,description:record.newDescription,source:"official"};
 }
 const matched=owner.title===record.oldTitle&&owner.description===record.oldDescription;
 const title=matched?record.newTitle:owner.title;
 const description=matched?record.newDescription:owner.description;
 try{normalizeProductSeo({slug:record.slug,locale:record.locale,seoTitle:title,metaDescription:description})}
 catch{return {skip:"Owner-edited SEO needs manual validation"}}
 return {title,description,source:matched?"reviewed":"owner",matched};
}
async function existingMap(db){
 const items=(await db.prepare("SELECT slug,locale FROM xuyi_product_seo ORDER BY slug,locale LIMIT 4000").all()).results||[];
 return new Set(items.map(x=>x.slug+"/"+x.locale));
}
export async function onRequestGet(c){
 const {db,error}=await prepare(c);if(error)return error;
 const present=await existingMap(db);
 const missing=REVIEWED_SEO_SOURCE.filter(r=>!present.has(r.slug+"/"+r.locale));
 return reply({reviewed:REVIEWED_COUNT,batchCount:chunkCount,persisted:REVIEWED_COUNT-missing.length,
  missing:missing.map(r=>r.slug+"/"+r.locale)});
}
export async function onRequestPost(c){
 const {db,error}=await prepare(c);if(error)return error;
 let input;try{input=await c.request.json()}catch{return reply({error:"Invalid JSON"},400)}
 if(input?.action==="finalize"){
  const present=await existingMap(db);
  const missing=REVIEWED_SEO_SOURCE.filter(r=>!present.has(r.slug+"/"+r.locale));
  if(missing.length)return reply({error:"Missing vetted product SEO rows",remaining:missing.length},409);
  const prior=await db.prepare("SELECT value FROM site_state WHERE key='product_seo_promotion_20261020_complete'").first();
  if(prior?.value==="505"){
    const current=await db.prepare("SELECT value FROM site_state WHERE key='publish_revision'").first();
    return reply({complete:true,alreadyFinalized:true,reviewed:REVIEWED_COUNT,
      revision:Number(current?.value||0)});
  }
  // Only finalization queues the release; no unexpected content revisions
  // while a 34-batch import is in progress.
  const revision=await bumpPublishRevision(db);
  await db.prepare("INSERT INTO site_state(key,value,updated_at) VALUES('product_seo_promotion_20261020_complete','505',CURRENT_TIMESTAMP) "+
    "ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=CURRENT_TIMESTAMP").run();
  return reply({complete:true,reviewed:REVIEWED_COUNT,...revision});
 }
 if(input?.action!=="batch"||!Number.isInteger(input.batchIndex)||
    input.batchIndex<0||input.batchIndex>=chunkCount)
  return reply({error:"Invalid fixed-source batch"},400);
 const segment=REVIEWED_SEO_SOURCE.slice(input.batchIndex*LIMIT,(input.batchIndex+1)*LIMIT);
 const present=await existingMap(db);
 let skipped=0,kept=0,planned=0;
 const queries=[];
 for(const row of segment){
  if(present.has(row.slug+"/"+row.locale)){skipped++;continue}
  const owner=await currentLegacy(db,row);
  const selected=selectAuthorizedCopy(row,owner);
  if(selected.skip){skipped++;continue}
  // Conditional INSERT and conditional owner UPDATE are in the same D1
  // atomic batch; a simultaneous editor update cannot be overwritten.
  if(owner?.kind==="page"){
   queries.push(db.prepare("INSERT INTO xuyi_product_seo(slug,locale,seo_title,meta_description) "+
      "SELECT ?,?,?,? WHERE EXISTS (SELECT 1 FROM site_pages WHERE route=? AND seo_title=? AND meta_description=?) "+
      "ON CONFLICT(slug,locale) DO NOTHING")
    .bind(row.slug,row.locale,selected.title,selected.description,owner.route,owner.title,owner.description));
   if(selected.matched){
    queries.push(db.prepare("UPDATE site_pages SET seo_title=?,meta_description=?,updated_at=CURRENT_TIMESTAMP "+
      "WHERE route=? AND seo_title=? AND meta_description=?")
      .bind(selected.title,selected.description,owner.route,owner.title,owner.description));
   }
  }else if(owner?.kind==="translation"){
   queries.push(db.prepare("INSERT INTO xuyi_product_seo(slug,locale,seo_title,meta_description) "+
     "SELECT ?,?,?,? WHERE EXISTS (SELECT 1 FROM xuyi_translation_overrides WHERE resource_id=? AND locale=? AND translated_json=?) "+
     "ON CONFLICT(slug,locale) DO NOTHING")
    .bind(row.slug,row.locale,selected.title,selected.description,"page:"+owner.route,row.locale,owner.raw));
   if(selected.matched){
    // Preserve mainHtml, editorial metadata and custom fields exactly.
    const next=JSON.stringify({...owner.content,title:selected.title,description:selected.description});
    queries.push(db.prepare("UPDATE xuyi_translation_overrides SET translated_json=?,reviewed_at=CURRENT_TIMESTAMP "+
      "WHERE resource_id=? AND locale=? AND translated_json=?")
      .bind(next,"page:"+owner.route,row.locale,owner.raw));
   }
  }else{
   // Missing legacy rows (LO/G) use only reviewed existing source content.
   // Never replace a newly created editor record at the canonical route.
   queries.push(db.prepare("INSERT INTO xuyi_product_seo(slug,locale,seo_title,meta_description) "+
    "SELECT ?,?,?,? WHERE NOT EXISTS (SELECT 1 FROM site_pages WHERE route=?) "+
    "AND NOT EXISTS (SELECT 1 FROM xuyi_translation_overrides WHERE resource_id=? AND locale=?) "+
    "ON CONFLICT(slug,locale) DO NOTHING")
    .bind(row.slug,row.locale,selected.title,selected.description,"/products/"+row.slug+"/",
       "page:/products/"+row.slug+"/",row.locale));
  }
  if(selected.source==="owner")kept++;
  planned++;
 }
 if(queries.length)await db.batch(queries);
 const finalMap=await existingMap(db);
 const persisted=segment.filter(r=>finalMap.has(r.slug+"/"+r.locale)).length;
 return reply({batchIndex:input.batchIndex,rows:segment.length,persisted,
    skipped,ownerEditsPreserved:kept,attempted:planned});
}
