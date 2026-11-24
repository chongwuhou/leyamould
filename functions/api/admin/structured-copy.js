// Structured page copy editor for the LEYA MOULD shared renderer.
// This endpoint stores text/arrays only; HTML, CSS and layout remain template-owned.
import { authorizedBuildRequest } from "../../_shared/build-auth.js";
import { bumpPublishRevision, loadLanguageConfig, publicLanguages } from "../../_shared/site-settings.js";
import { MOULD_ROUTES } from "../../_shared/mould-routes.js";

const respond=(body,status=200)=>Response.json(body,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
const clean=(value,limit)=>String(value??"").trim().slice(0,limit);
const PAGE_KEYS=new Set(["eyebrow","title","subtitle","quickAnswers","groups","sections"]);
async function deny(c){
  if(!c.env.ADMIN_TOKEN)return respond({error:"Admin not configured"},503);
  if(!(await authorizedBuildRequest(c.request,c.env)))return respond({error:"Unauthorized"},401);
  if(!c.env.LEYA_DB)return respond({error:"LEYA_DB missing"},503);
  return null;
}
async function ensure(db){await db.prepare("CREATE TABLE IF NOT EXISTS site_state(key TEXT PRIMARY KEY,value TEXT NOT NULL DEFAULT '',updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)").run();}
function parse(value){try{const x=JSON.parse(String(value||"{}"));return x&&typeof x==="object"&&!Array.isArray(x)?x:{};}catch{return {};}}
function answers(value){
  if(!Array.isArray(value)||value.length>8)throw Error("quickAnswers must contain 1–8 items");
  return value.map(row=>{const question=clean(row?.question,240),answer=clean(row?.answer,1800);if(!question||!answer)throw Error("Each quick answer needs a question and answer");return {question,answer};});
}
function groups(value){
  if(!Array.isArray(value)||value.length>8)throw Error("groups must contain 1–8 groups");
  return value.map(group=>{const title=clean(group?.title,180),items=Array.isArray(group?.items)?group.items:[];if(!title||!items.length||items.length>12)throw Error("Each FAQ group needs 1–12 items");return {title,items:items.map(row=>{const question=clean(row?.question,240),answer=clean(row?.answer,1800);if(!question||!answer)throw Error("Each FAQ item needs a question and answer");return {question,answer};})};});
}
function validate(input){
  if(!input||typeof input!=="object"||Array.isArray(input))throw Error("Structured copy must be an object");
  const out={};
  for(const key of PAGE_KEYS){
    if(!Object.hasOwn(input,key))continue;
    if(["quickAnswers","groups","sections"].includes(key)){
      if(key==="quickAnswers")out[key]=answers(input[key]);
      else if(key==="groups")out[key]=groups(input[key]);
      else if(!Array.isArray(input[key])&&(!input[key]||typeof input[key]!=="object"||Array.isArray(input[key])))throw Error("sections must be an array or keyed object");
      if(key==="sections"){
        if(Array.isArray(input[key])){
          if(input[key].length>12)throw Error("sections must contain at most 12 items");
          out[key]=input[key].map(row=>{const id=clean(row?.id,80),eyebrow=clean(row?.eyebrow,180),title=clean(row?.title,180),body=clean(row?.body,1800),bullets=Array.isArray(row?.bullets)?row.bullets.map(x=>clean(x,240)).filter(Boolean).slice(0,8):[];if(!id||!title||!body)throw Error("Each section needs id, title and body");return {id,eyebrow,title,body,bullets};});
        }else{
          const keyed={};for(const [id,row] of Object.entries(input[key]).slice(0,24)){const title=clean(row?.title,180),body=clean(row?.body,1800),eyebrow=clean(row?.eyebrow,180);if(!title)continue;keyed[clean(id,80)]={eyebrow,title,body,bullets:Array.isArray(row?.bullets)?row.bullets.map(x=>clean(x,240)).filter(Boolean).slice(0,8):[]};}if(!Object.keys(keyed).length)throw Error("sections object is empty");out[key]=keyed;
        }
      }
    }else{
      const value=clean(input[key],2000);if(value)out[key]=value;
    }
  }
  if(!Object.keys(out).length)throw Error("No editable structured fields supplied");
  return out;
}
export async function onRequestGet(c){
  const blocked=await deny(c);if(blocked)return blocked;const db=c.env.LEYA_DB;await ensure(db);
  const languageConfig=await loadLanguageConfig(db),locales=publicLanguages(languageConfig).map(row=>row.code);
  const row=await db.prepare("SELECT value,updated_at FROM site_state WHERE key='page_copy'").first();
  return respond({pageCopy:parse(row?.value),updatedAt:row?.updated_at||"",locales,routes:[...MOULD_ROUTES].filter(route=>route.endsWith("/")).sort()});
}
export async function onRequestPost(c){
  const blocked=await deny(c);if(blocked)return blocked;let payload;try{payload=await c.request.json()}catch{return respond({error:"Invalid JSON"},400)}
  if(payload?.action!=="save_page_copy")return respond({error:"Unknown action"},400);
  const locale=clean(payload.locale,12),route=clean(payload.route,250);const languageConfig=await loadLanguageConfig(c.env.LEYA_DB),locales=new Set(publicLanguages(languageConfig).map(row=>row.code));if(!locales.has(locale))return respond({error:"Locale is not enabled for public publishing"},400);if(!MOULD_ROUTES.has(route))return respond({error:"Route is not a configured LEYA route"},400);
  let content;try{content=validate(payload.content)}catch(error){return respond({error:String(error.message||error)},400)}
  const db=c.env.LEYA_DB;await ensure(db);const row=await db.prepare("SELECT value FROM site_state WHERE key='page_copy'").first();const state=parse(row?.value);if(!state[locale]||typeof state[locale]!=="object")state[locale]={};state[locale][route]=content;
  await db.prepare("INSERT INTO site_state(key,value,updated_at) VALUES('page_copy',?,CURRENT_TIMESTAMP) ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=CURRENT_TIMESTAMP").bind(JSON.stringify(state)).run();
  return respond({saved:true,locale,route,...(await bumpPublishRevision(db))});
}

