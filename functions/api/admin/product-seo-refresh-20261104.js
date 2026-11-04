// Narrow, one-time refresh of the previously reviewed 505 product/locale SEO rows.
// Each field updates only while it still equals the prior source-approved value.
// An owner edit made before or during the migration is retained independently.
import {authorizedProductSeoPromotionRequest} from "../../_shared/build-auth.js";
import {ensureProductSeo,normalizeProductSeo} from "../../_shared/product-seo.js";
import {bumpPublishRevision} from "../../_shared/site-settings.js";
import {REVIEWED_SEO_REFRESH_SOURCE} from "../../_shared/reviewed-product-seo-refresh-20261104.js";
import {REVIEWED_SEO_SOURCE} from "../../_shared/reviewed-product-seo-20261020.js";

const reply=(value,status=200)=>Response.json(value,{status,headers:{
  "cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"
}});
const LIMIT=15;
const COMPLETE_KEY="product_seo_refresh_20261104_complete";
export const REVIEWED_COUNT=REVIEWED_SEO_REFRESH_SOURCE.length;
const PRIOR_SEO_SOURCE=new Map(REVIEWED_SEO_SOURCE.map(row=>[row.slug+"/"+row.locale,row]));

export function expectedReviewedRows(){
  const seen=new Set();
  const locales=new Map();
  for(const row of REVIEWED_SEO_REFRESH_SOURCE){
    const next=normalizeProductSeo({
      slug:row.slug,locale:row.locale,
      seoTitle:row.newTitle,metaDescription:row.newDescription
    });
    const key=next.slug+"/"+next.locale;
    if(seen.has(key))throw Error("Duplicate reviewed product SEO refresh key");
    seen.add(key);
    locales.set(next.locale,1+(locales.get(next.locale)||0));
    const prior=PRIOR_SEO_SOURCE.get(key);
    if(!prior?.newTitle||!prior?.newDescription||
       prior.newTitle===row.newTitle&&prior.newDescription===row.newDescription)
      throw Error("Invalid previous SEO source comparison");
    if(typeof row.hasCapacity!=="boolean"||typeof row.twoWay!=="boolean")
      throw Error("Missing reviewed product source flags");
  }
  if(seen.size!==505||REVIEWED_COUNT!==505)throw Error("Wrong reviewed SEO refresh count");
  for(const locale of ["en","es","pt","ru","tr"]){
    if(locales.get(locale)!==101)throw Error("Wrong locale coverage: "+locale);
  }
  return seen;
}
expectedReviewedRows();

function fieldState(current,expected,next){
  if(current===next)return "updated";
  if(current===expected)return "eligible";
  return "preserved";
}
export function classifyReviewedRow(source,current){
  const prior=PRIOR_SEO_SOURCE.get(source.slug+"/"+source.locale);
  if(!current||!prior)return {title:"missing",description:"missing"};
  return {
    title:fieldState(current.seo_title,prior.newTitle,source.newTitle),
    description:fieldState(current.meta_description,prior.newDescription,source.newDescription)
  };
}

async function prepare(c){
  if(!await authorizedProductSeoPromotionRequest(c.request,c.env))
    return {error:reply({error:"Unauthorized"},401)};
  if(!c.env.XUYI_DB)return {error:reply({error:"Missing XUYI D1 binding"},503)};
  const db=c.env.XUYI_DB;
  await ensureProductSeo(db);
  return {db};
}
async function currentRows(db){
  const rows=(await db.prepare(
    "SELECT slug,locale,seo_title,meta_description FROM xuyi_product_seo ORDER BY slug,locale LIMIT 4000"
  ).all()).results||[];
  return new Map(rows.map(row=>[row.slug+"/"+row.locale,row]));
}
function summarize(rows){
  const result={
    reviewed:REVIEWED_COUNT,batchCount:Math.ceil(REVIEWED_COUNT/LIMIT),
    titleEligible:0,titleUpdated:0,titlePreserved:0,
    descriptionEligible:0,descriptionUpdated:0,descriptionPreserved:0,
    missingRows:[]
  };
  for(const source of REVIEWED_SEO_REFRESH_SOURCE){
    const key=source.slug+"/"+source.locale;
    const state=classifyReviewedRow(source,rows.get(key));
    if(state.title==="missing"||state.description==="missing"){
      result.missingRows.push(key);
      continue;
    }
    result["title"+state.title[0].toUpperCase()+state.title.slice(1)]++;
    result["description"+state.description[0].toUpperCase()+state.description.slice(1)]++;
  }
  return result;
}
async function stateRecord(db){
  return await db.prepare("SELECT value FROM site_state WHERE key=?").bind(COMPLETE_KEY).first();
}
export async function onRequestGet(c){
  const {db,error}=await prepare(c);if(error)return error;
  const [rows,marker]=await Promise.all([currentRows(db),stateRecord(db)]);
  return reply({...summarize(rows),finalized:marker?.value==="505"});
}
export async function onRequestPost(c){
  const {db,error}=await prepare(c);if(error)return error;
  let input;try{input=await c.request.json()}catch{return reply({error:"Invalid JSON"},400)};

  if(input?.action==="finalize"){
    const [rows,marker]=await Promise.all([currentRows(db),stateRecord(db)]);
    const summary=summarize(rows);
    if(summary.missingRows.length||summary.titleEligible||summary.descriptionEligible)
      return reply({error:"Reviewed SEO refresh is incomplete",...summary},409);
    if(marker?.value==="505"){
      const current=await db.prepare("SELECT value FROM site_state WHERE key='publish_revision'").first();
      return reply({complete:true,alreadyFinalized:true,...summary,revision:Number(current?.value||0)});
    }
    const revision=await bumpPublishRevision(db);
    await db.prepare(
      "INSERT INTO site_state(key,value,updated_at) VALUES(?, '505', CURRENT_TIMESTAMP) "+
      "ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=CURRENT_TIMESTAMP"
    ).bind(COMPLETE_KEY).run();
    return reply({complete:true,...summary,...revision});
  }

  if(input?.action!=="batch"||!Number.isInteger(input.batchIndex)||
     input.batchIndex<0||input.batchIndex>=Math.ceil(REVIEWED_COUNT/LIMIT))
    return reply({error:"Invalid fixed-source batch"},400);

  const segment=REVIEWED_SEO_REFRESH_SOURCE.slice(input.batchIndex*LIMIT,(input.batchIndex+1)*LIMIT);
  const rows=await currentRows(db);
  const queries=[];
  for(const source of segment){
    const current=rows.get(source.slug+"/"+source.locale);
    const status=classifyReviewedRow(source,current);
    if(status.title==="eligible"){
      queries.push(db.prepare(
        "UPDATE xuyi_product_seo SET seo_title=?,updated_at=CURRENT_TIMESTAMP "+
        "WHERE slug=? AND locale=? AND seo_title=?"
      ).bind(source.newTitle,source.slug,source.locale,PRIOR_SEO_SOURCE.get(source.slug+"/"+source.locale).newTitle));
    }
    if(status.description==="eligible"){
      queries.push(db.prepare(
        "UPDATE xuyi_product_seo SET meta_description=?,updated_at=CURRENT_TIMESTAMP "+
        "WHERE slug=? AND locale=? AND meta_description=?"
      ).bind(source.newDescription,source.slug,source.locale,PRIOR_SEO_SOURCE.get(source.slug+"/"+source.locale).newDescription));
    }
  }
  if(queries.length)await db.batch(queries);
  const after=await currentRows(db);
  return reply({batchIndex:input.batchIndex,rows:segment.length,...summarize(after)});
}
