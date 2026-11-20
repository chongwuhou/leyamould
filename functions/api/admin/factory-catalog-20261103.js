import {authorizedReviewedFactoryCatalogCommitRequest} from "../../_shared/build-auth.js";
import {normalizeNewProduct} from "../../_shared/new-product.js";
import {normalizeAltMap,ensureMediaAlt} from "../../_shared/media-alt.js";
import {imageKey} from "../../_shared/r2-usage.js";
import {bumpPublishRevision,loadLanguageConfig,publicLanguages} from "../../_shared/site-settings.js";
import manifest from "../../../data/factory-catalog-manifest-2026-11-03.json" with {type:"json"};

const json=(value,status=200)=>Response.json(value,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
const byModel=new Map((manifest.models||[]).map(item=>[item.model,item]));
const stable=value=>{
  if(Array.isArray(value))return "["+value.map(stable).join(",")+"]";
  if(value&&typeof value==="object")return "{"+Object.keys(value).sort().map(key=>JSON.stringify(key)+":"+stable(value[key])).join(",")+"}";
  return JSON.stringify(value);
};
async function ensureProductTable(db){
  await db.prepare(`CREATE TABLE IF NOT EXISTS xuyi_product_content(
    model TEXT PRIMARY KEY,
    content_json TEXT NOT NULL DEFAULT '{}',
    publication_status TEXT NOT NULL DEFAULT 'draft' CHECK(publication_status IN ('draft','published')),
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  )`).run();
}
async function selectIn(db,table,column,values,fields){
  const placeholders=values.map(()=>"?").join(",");
  return (await db.prepare("SELECT "+fields+" FROM "+table+" WHERE "+column+" IN ("+placeholders+")").bind(...values).all()).results||[];
}
export async function onRequestGet(){return json({error:"Unauthorized"},401);}

export async function onRequestPost(context){
  if(!(await authorizedReviewedFactoryCatalogCommitRequest(context.request,context.env)))return json({error:"Unauthorized"},401);
  const env=context.env,db=env.LEYA_DB;
  if(!db||!env.LEYA_ASSETS)return json({error:"LEYA D1 or R2 binding unavailable"},503);
  const languages=publicLanguages(await loadLanguageConfig(db)).map(item=>item.code);
  let payload;
  try{payload=await context.request.json()}catch{return json({error:"Invalid JSON"},400);}
  if(payload?.site!=="leyamould"||
     payload?.sourceDocument!==manifest.sourceDocument||
     payload?.sourceSha256!==manifest.sourceSha256||
     !Array.isArray(payload?.records)||
     payload.records.length!==manifest.recordCount||
     manifest.recordCount!==58||
     manifest.models?.length!==58){
    return json({error:"Batch does not match the owner-reviewed 58-model manifest"},409);
  }
  const seen=new Set(),items=[];
  try{
    for(const record of payload.records){
      const model=String(record?.model||"");
      const expected=byModel.get(model);
      if(!expected||seen.has(model))throw Error("Unknown or duplicate model: "+model);
      seen.add(model);
      if(record.status!=="published"||record.imageSha256!==expected.imageSha256)throw Error("Model status or image SHA mismatch: "+model);
      const source=record.content;
      if(!source||source.newProduct!==true||
         source.factoryModel!==expected.factoryModel||
         source.category!==expected.category||
         String(source.sourcePage)!==String(expected.sourcePage)||
         source.sourceDocument!==manifest.sourceDocument||
         source.sourceSha256!==manifest.sourceSha256||
         source.sourceImageSha256!==expected.imageSha256||
         source.imageReviewStatus!=="visually_reviewed_source_crop"||
         !["source_read","needs_confirmation"].includes(source.qcStatus)){
        throw Error("Source-backed product fields do not match manifest: "+model);
      }
      const filename=expected.imageSha256.slice(0,32)+".webp";
      const imagePath="/media/product/"+filename;
      if(source.image&&source.image!==imagePath)throw Error("Unexpected image path: "+model);
      const content=normalizeNewProduct(model,{...source,image:imagePath},"published");
      const alt=normalizeAltMap(record.imageAlt);
      if(!languages.every(language=>alt[language]))throw Error("Reviewed image ALT is missing for a configured language: "+model);
      const key=imageKey("product",filename);
      if(!key)throw Error("Invalid R2 image key: "+model);
      items.push({model,content,alt,imagePath,key,sha256:expected.imageSha256});
    }
  }catch(error){return json({error:String(error.message||error)},400);}
  if(seen.size!==58||manifest.models.some(item=>!seen.has(item.model)))return json({error:"The batch must contain each reviewed model exactly once"},409);

  await ensureProductTable(db);
  await ensureMediaAlt(db);
  await db.prepare(`CREATE TABLE IF NOT EXISTS site_state(
    key TEXT PRIMARY KEY,value TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  )`).run();

  const models=items.map(item=>item.model);
  const paths=items.map(item=>item.imagePath);
  let existingProducts,existingAlts;
  try{
    [existingProducts,existingAlts]=await Promise.all([
      selectIn(db,"xuyi_product_content","model",models,"model,content_json,publication_status"),
      selectIn(db,"xuyi_media_alt","path",paths,"path,alt_json")
    ]);
  }catch{return json({error:"Could not preflight the existing LEYA D1 catalog"},503);}
  const productMap=new Map(existingProducts.map(row=>[row.model,row]));
  const altMap=new Map(existingAlts.map(row=>[row.path,row]));
  for(const item of items){
    const prior=productMap.get(item.model);
    if(prior){
      let old;
      try{old=JSON.parse(prior.content_json)}catch{return json({error:"Existing product JSON is invalid: "+item.model},409);}
      if(prior.publication_status!=="published"||stable(old)!==stable(item.content)){
        return json({error:"Existing model is different or still a draft; create-only import will not overwrite: "+item.model},409);
      }
    }
    const priorAlt=altMap.get(item.imagePath);
    if(priorAlt){
      let oldAlt;
      try{oldAlt=normalizeAltMap(JSON.parse(priorAlt.alt_json))}catch{return json({error:"Existing image ALT JSON is invalid: "+item.model},409);}
      if(stable(oldAlt)!==stable(item.alt))return json({error:"Existing image ALT differs; no overwrite attempted: "+item.model},409);
    }
  }

  try{
    const imageChecks=await Promise.all(items.map(async item=>{
      const object=await env.LEYA_ASSETS.head(item.key);
      if(!object||object.customMetadata?.sha256!==item.sha256||
         object.customMetadata?.model!==item.model||
         object.customMetadata?.sourceSha256!==manifest.sourceSha256){
        throw Error("Reviewed R2 image is missing or mismatched: "+item.model);
      }
      return item.model;
    }));
    if(imageChecks.length!==58)throw Error("R2 verification count mismatch");
  }catch(error){return json({error:String(error.message||error)},409);}

  const statements=[];
  let insertedProducts=0,insertedAlts=0;
  for(const item of items){
    if(!productMap.has(item.model)){
      statements.push(db.prepare(`INSERT OR IGNORE INTO xuyi_product_content(model,content_json,publication_status,updated_at)
        VALUES(?,?,'published',CURRENT_TIMESTAMP)`).bind(item.model,JSON.stringify(item.content)));
      insertedProducts++;
    }
    if(!altMap.has(item.imagePath)){
      statements.push(db.prepare(`INSERT OR IGNORE INTO xuyi_media_alt(path,alt_json,updated_at)
        VALUES(?,?,CURRENT_TIMESTAMP)`).bind(item.imagePath,JSON.stringify(item.alt)));
      insertedAlts++;
    }
  }
  try{
    if(statements.length)await db.batch(statements);
    let revision=null;
    if(statements.length)revision=await bumpPublishRevision(db);
    const finalProducts=await selectIn(db,"xuyi_product_content","model",models,"model,content_json,publication_status");
    const finalAlts=await selectIn(db,"xuyi_media_alt","path",paths,"path,alt_json");
    const finalProductMap=new Map(finalProducts.map(row=>[row.model,row]));
    const finalAltMap=new Map(finalAlts.map(row=>[row.path,row]));
    for(const item of items){
      const row=finalProductMap.get(item.model),altRow=finalAltMap.get(item.imagePath);
      if(!row||row.publication_status!=="published"||stable(JSON.parse(row.content_json))!==stable(item.content))
        throw Error("D1 product read-back mismatch: "+item.model);
      if(!altRow||stable(normalizeAltMap(JSON.parse(altRow.alt_json)))!==stable(item.alt))
        throw Error("D1 image ALT read-back mismatch: "+item.model);
    }
    if(!revision){
      const revisionRow=await db.prepare("SELECT value FROM site_state WHERE key='publish_revision'").first();
      revision={revision:Number(revisionRow?.value||0)};
    }
    return json({saved:true,unchanged:!statements.length,sourceSha256:manifest.sourceSha256,
      requested:58,publishedProducts:finalProducts.length,insertedProducts,
      existingProducts:58-insertedProducts,insertedAlts,existingAlts:58-insertedAlts,
      publishRevision:revision.revision});
  }catch(error){return json({error:String(error.message||error)},503);}
}
