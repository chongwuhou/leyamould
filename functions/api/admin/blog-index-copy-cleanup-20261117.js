import { authorizedReviewedBlogIndexCopyCleanupRequest } from "../../_shared/build-auth.js";
import { bumpPublishRevision } from "../../_shared/site-settings.js";

const BATCH_ID="2026-11-17-blog-index-copy-cleanup";
const ORIGIN_ROUTES=[
  "/blog/how-can-importers-source-replacement-lids-and-spare-parts-for-wholesale-water-bottles/",
  "/blog/how-should-wholesalers-build-a-multi-capacity-water-bottle-assortment-for-retail-shelves/",
  "/blog/what-should-buyers-verify-before-using-dishwasher-safe-plastic-water-bottle-claims/"
];
const LOCALES=["es","pt","ru","tr"];
const CAPACITY={es:"Guía de capacidades",pt:"Guia de capacidades",ru:"Руководство по ёмкостям",tr:"Kapasite rehberi"};
const FAQ_PREFIX={pt:"O que o comprador deve confirmar? ",ru:"Что должен подтвердить покупатель? ",tr:"Alıcı neyi doğrulamalı? "};
const json=(body,status=200)=>Response.json(body,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
const navPattern=/<nav\b[^>]*class="[^"]*\bblog-buyer-matrix__links\b[^"]*"[^>]*>[\s\S]*?<\/nav>/gi;
const hash=async value=>{const bytes=new TextEncoder().encode(value);const digest=await crypto.subtle.digest("SHA-256",bytes);return [...new Uint8Array(digest)].map(x=>x.toString(16).padStart(2,"0")).join("")};
function parse(row){try{const payload=JSON.parse(row?.translated_json||"{}");return payload&&typeof payload==="object"&&typeof payload.mainHtml==="string"?payload:null}catch{return null}}
function hrefCounts(body){
 const counts=new Map();
 for(const match of String(body).matchAll(/href="\/(?:[a-z]{2}\/)?blog\/([a-z0-9]+(?:-[a-z0-9]+)*)\/"/g)){const slug=match[1];counts.set(slug,(counts.get(slug)||0)+1)}
 return counts;
}
function transform(body,locale,route){
 let next=String(body).replace(navPattern,"");
 if((route===ORIGIN_ROUTES[0]||route===ORIGIN_ROUTES[1])&&CAPACITY[locale])next=next.replaceAll("Capacity guide",CAPACITY[locale]);
 if((route===ORIGIN_ROUTES[0]||route===ORIGIN_ROUTES[2])&&locale==="es")next=next.replaceAll("Quality control checklist","Lista de control de calidad");
 if((route===ORIGIN_ROUTES[0]||route===ORIGIN_ROUTES[2])&&locale==="tr")next=next.replaceAll("Kontrol kalite kontrol listesi","Kalite kontrol listesi");
 if(FAQ_PREFIX[locale])next=next.replaceAll("<summary>"+FAQ_PREFIX[locale],"<summary>");
 return next;
}
function validate(body,locale){
 const forbidden=["Capacity guide","Quality control checklist","Kontrol kalite kontrol listesi",FAQ_PREFIX[locale]||""].filter(Boolean);
 for(const item of forbidden)if(body.includes(item))return "Legacy fragment remains: "+item;
 if(/class="[^"]*\bblog-buyer-matrix__links\b/.test(body))return "Duplicate buyer-matrix link navigation remains";
 const counts=hrefCounts(body);
 for(const [slug,total] of counts)if(total>1)return "Duplicate localized Blog URL remains: "+slug+"="+total;
 return "";
}
export async function onRequestPost(context){
 if(!(await authorizedReviewedBlogIndexCopyCleanupRequest(context.request,context.env)))return json({error:"Unauthorized reviewed Blog cleanup request"},401);
 const db=context.env.XUYI_DB;if(!db)return json({error:"XUYI_DB binding missing"},503);
 try{
  const rows=(await db.prepare("SELECT resource_id,locale,translated_json FROM xuyi_translation_overrides WHERE locale IN (?,?,?,?) AND resource_id LIKE 'page:/blog/%'").bind(...LOCALES).all()).results||[];
  const normalizeResourceId=value=>{
   const raw=String(value||"");
   if(!raw.startsWith("page:/blog/"))return raw;
   const route=raw.slice(5).replace(/\\/+$/,"")+"/";
   return "page:"+route;
  };
  const lookup=new Map(rows.map(row=>[normalizeResourceId(row.resource_id)+"|"+row.locale,row]));
  const plans=[];
  for(const route of ORIGIN_ROUTES)for(const locale of LOCALES){
   const resourceId="page:"+route,row=lookup.get(resourceId+"|"+locale),payload=parse(row);
   if(!payload)return json({error:"Missing or invalid D1 Blog translation: "+resourceId+"|"+locale},409);
   const before=payload.mainHtml,after=transform(before,locale,route);
   plans.push({resourceId,actualResourceId:row.resource_id,locale,before,after,changed:before!==after});
  }
  const now=new Date().toISOString(),statements=[];
  for(const plan of plans)if(plan.changed){
   const original=parse(lookup.get(plan.resourceId+"|"+plan.locale));
   const payload={...original,mainHtml:plan.after};
   statements.push(db.prepare("UPDATE xuyi_translation_overrides SET translated_json=?,reviewed_at=? WHERE resource_id=? AND locale=? AND translated_json=?").bind(JSON.stringify(payload),now,plan.actualResourceId,plan.locale,JSON.stringify(original)));
  }
  const results=statements.length?await db.batch(statements):[];
  if(results.some(result=>Number(result?.meta?.changes||0)!==1))return json({error:"D1 cleanup compare-and-swap failed; no safe final state claimed"},409);
  const afterRows=(await db.prepare("SELECT resource_id,locale,translated_json FROM xuyi_translation_overrides WHERE locale IN (?,?,?,?) AND resource_id LIKE 'page:/blog/%'").bind(...LOCALES).all()).results||[];
  const afterLookup=new Map(afterRows.map(row=>[normalizeResourceId(row.resource_id)+"|"+row.locale,row]));
  for(const plan of plans){
   const body=parse(afterLookup.get(plan.resourceId+"|"+plan.locale))?.mainHtml||"";
   const error=validate(body,plan.locale);
   if(error)return json({error:"Final D1 cleanup check failed: "+plan.resourceId+"|"+plan.locale+" "+error},409);
  }
  const publishRevision=statements.length?(await bumpPublishRevision(db)).revision:Number((await db.prepare("SELECT value FROM site_state WHERE key='publish_revision'").first())?.value||0);
  return json({success:true,batchId:BATCH_ID,checkedRecords:plans.length,updatedRecords:plans.filter(x=>x.changed).length,remainingLegacyFragments:0,publishRevision});
 }catch(error){return json({error:"D1 Blog cleanup failed: "+String(error?.message||"unknown").slice(0,240)},500)}
}
