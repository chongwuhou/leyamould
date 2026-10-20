// Authenticated D1 source ledger: maximum three unique SKU publications per
// Asia/Shanghai date; no repeat even after a public review is later removed.
import {authorizedDailyProductReviewRequest} from "../../_shared/build-auth.js";
import {MANAGED_MODELS} from "../../_shared/xuyi-routes.js";
import {ensureProductReviews} from "../../_shared/product-reviews.js";
import {bumpPublishRevision} from "../../_shared/site-settings.js";

const json=(body,status=200)=>Response.json(body,{status,headers:{
 "cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"
}});
const LEDGER_SQL=[
 "CREATE TABLE IF NOT EXISTS xuyi_review_publication_ledger (",
 "model TEXT PRIMARY KEY, source_row INTEGER NOT NULL UNIQUE,",
 "source_model TEXT NOT NULL, source_fingerprint TEXT NOT NULL UNIQUE,",
 "published_date TEXT NOT NULL, review_id TEXT NOT NULL UNIQUE,",
 "recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
].join(" ");
const TRANSPARENT={
 "2306-transparent":"2306透明款","2307-transparent":"2307透明款",
 "2308-transparent":"2308透明款","2400-transparent":"2400透明款",
 "2401-transparent":"2401透明款"
};

export function beijingDate(now=new Date()){
 const parts=Object.fromEntries(new Intl.DateTimeFormat("en-GB",{timeZone:"Asia/Shanghai",
  year:"numeric",month:"2-digit",day:"2-digit"}).formatToParts(now).map(x=>[x.type,x.value]));
 return parts.year+"-"+parts.month+"-"+parts.day;
}
const dayOK=value=>/^\d{4}-\d{2}-\d{2}$/.test(value)&&
 new Date(value+"T00:00:00Z").toISOString().slice(0,10)===value;
async function requireDb(c){
 if(!c.env.ADMIN_TOKEN)return {error:json({error:"Admin not configured"},503)};
 if(!(await authorizedDailyProductReviewRequest(c.request,c.env)))return {error:json({error:"Unauthorized"},401)};
 if(!c.env.XUYI_DB)return {error:json({error:"Database unavailable"},503)};
 const db=c.env.XUYI_DB;
 await ensureProductReviews(db);
 await db.prepare(LEDGER_SQL).run();
 return {db};
}
const getExisting=async db=>{
 const [ledger,reviews]=await Promise.all([
  db.prepare("SELECT model,source_model,source_row,source_fingerprint,published_date,review_id FROM xuyi_review_publication_ledger ORDER BY source_row").all(),
  db.prepare("SELECT DISTINCT model FROM xuyi_product_reviews").all()
 ]);
 return {ledger:ledger.results||[],models:new Set((reviews.results||[]).map(r=>r.model))};
};
async function verifySignature(r){
 const raw=r.model+"\n"+r.rating+"\n"+r.author+"\n"+r.content;
 const digest=await crypto.subtle.digest("SHA-256",new TextEncoder().encode(raw));
 return Array.from(new Uint8Array(digest),x=>x.toString(16).padStart(2,"0")).join("");
}
export async function validateDailyInput(input,today=beijingDate()){
 if(input?.date!==today||!dayOK(today))throw Error("发布日期必须是北京时间今天");
 if(input.confirmedAuthentic!==true)throw Error("只能上传已核实且获公开授权的真实客户评价");
 if(!Array.isArray(input.items)||input.items.length<1||input.items.length>3)
  throw Error("每批只允许 1–3 个产品");
 const seen=new Set(),rows=new Set();
 for(const r of input.items){
  if(!r||typeof r!=="object")throw Error("Invalid review");
  if(!Number.isInteger(r.sourceRow)||r.sourceRow<2||r.sourceRow>2000||rows.has(r.sourceRow))
   throw Error("源表行号无效或重复");
  rows.add(r.sourceRow);
  if(!MANAGED_MODELS.has(r.model)||seen.has(r.model))throw Error("产品型号不存在或重复");
  seen.add(r.model);
  if((TRANSPARENT[r.sourceModel]||r.sourceModel)!==r.model)
   throw Error("源表产品型号不对应官网正式型号");
  if(!Number.isInteger(r.rating)||r.rating<1||r.rating>5)throw Error("星级无效");
  if(typeof r.author!=="string"||r.author.trim()!==r.author||
    r.author.length<2||r.author.length>99)throw Error("客户姓名无效");
  if(typeof r.content!=="string"||r.content.trim()!==r.content||
    r.content.length<12||r.content.length>3000)throw Error("客户评价原文无效");
  if(!/^[a-f0-9]{64}$/.test(r.sourceFingerprint)||
     await verifySignature(r)!==r.sourceFingerprint)throw Error("源Excel评价内容与指纹不一致");
 }
 return input.items;
}
export async function onRequestGet(c){
 const {db,error}=await requireDb(c);if(error)return error;
 const existing=await getExisting(db);
 return json({today:beijingDate(),recorded:existing.ledger,
   existingModels:[...existing.models].sort(),maxPerDay:3});
}
export async function onRequestPost(c){
 const {db,error}=await requireDb(c);if(error)return error;
 let input;try{input=await c.request.json()}catch{return json({error:"Invalid JSON"},400)}
 let records;try{records=await validateDailyInput(input)}catch(e){return json({error:e.message},400)}
 const existing=await getExisting(db);
 const prior=new Set(existing.ledger.map(r=>r.model));
 const today=beijingDate();
 const todayCount=existing.ledger.filter(r=>r.published_date===today).length;
 const candidates=records.filter(r=>!prior.has(r.model)&&!existing.models.has(r.model));
 if(todayCount+candidates.length>3)
  return json({error:"今天已经达到每天最多3个不同型号的限制",todayCount},409);
 if(!candidates.length)
  return json({success:true,inserted:0,skipped:records.length,todayCount,recorded:existing.ledger});
 const queries=[];
 for(const r of candidates){
  const id=crypto.randomUUID();
  queries.push(db.prepare("INSERT INTO xuyi_product_reviews (id,model,rating,author,review_date,content,status) VALUES(?,?,?,?,?,?,'published')")
   .bind(id,r.model,r.rating,r.author,today,r.content));
  queries.push(db.prepare("INSERT INTO xuyi_review_publication_ledger (model,source_row,source_model,source_fingerprint,published_date,review_id) VALUES(?,?,?,?,?,?)")
   .bind(r.model,r.sourceRow,r.sourceModel,r.sourceFingerprint,today,id));
 }
 const result=await db.batch(queries);
 if(!Array.isArray(result)||result.length!==queries.length||
    result.some(x=>x.meta?.changes!==1))
  return json({error:"Unexpected insert result; inspect ledger before retry"},500);
 const revision=await bumpPublishRevision(db);
 const finalState=await getExisting(db);
 return json({success:true,date:today,inserted:candidates.length,
   skipped:records.length-candidates.length,
   todayCount:finalState.ledger.filter(r=>r.published_date===today).length,
   recorded:finalState.ledger,...revision});
}
