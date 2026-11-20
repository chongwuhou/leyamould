import {authorizedDailyProductReviewRequest} from "../../_shared/build-auth.js";
import {MANAGED_MODELS} from "../../_shared/xuyi-routes.js";
import {ensureProductReviews} from "../../_shared/product-reviews.js";
import {bumpPublishRevision} from "../../_shared/site-settings.js";
import {ensurePublishScheduler} from "../../_shared/publish-scheduler.js";

const json=(body,status=200)=>Response.json(body,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
const LEGACY_SQL=[
 "CREATE TABLE IF NOT EXISTS xuyi_review_publication_ledger (",
 "model TEXT PRIMARY KEY, source_row INTEGER NOT NULL UNIQUE,",
 "source_model TEXT NOT NULL, source_fingerprint TEXT NOT NULL UNIQUE,",
 "published_date TEXT NOT NULL, review_id TEXT NOT NULL UNIQUE,",
 "recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
].join(" ");
const LEDGER_V2_SQL=[
 "CREATE TABLE IF NOT EXISTS xuyi_review_publication_ledger_v2 (",
 "review_id TEXT PRIMARY KEY, model TEXT NOT NULL, source_file TEXT NOT NULL,",
 "source_row INTEGER NOT NULL, source_model TEXT NOT NULL, source_fingerprint TEXT NOT NULL UNIQUE,",
 "published_date TEXT NOT NULL, recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,",
 "UNIQUE(source_file,source_row))"
].join(" ");
const SOURCE_FILES=new Set(["101-zhenshipingjia.xlsx","101-additional-reviews-only.xlsx"]);
const TRANSPARENT={"2306-transparent":"2306透明款","2307-transparent":"2307透明款","2308-transparent":"2308透明款","2400-transparent":"2400透明款","2401-transparent":"2401透明款"};

export function beijingDate(now=new Date()){
 const p=Object.fromEntries(new Intl.DateTimeFormat("en-GB",{timeZone:"Asia/Shanghai",year:"numeric",month:"2-digit",day:"2-digit"}).formatToParts(now).map(x=>[x.type,x.value]));
 return p.year+"-"+p.month+"-"+p.day;
}
const dayOK=v=>/^\d{4}-\d{2}-\d{2}$/.test(v)&&new Date(v+"T00:00:00Z").toISOString().slice(0,10)===v;
async function ensureLedger(db){
 await db.prepare(LEGACY_SQL).run();
 await db.prepare(LEDGER_V2_SQL).run();
 await db.prepare("INSERT OR IGNORE INTO xuyi_review_publication_ledger_v2 "+
  "(review_id,model,source_file,source_row,source_model,source_fingerprint,published_date) "+
  "SELECT review_id,model,'legacy-unmapped',source_row,source_model,source_fingerprint,published_date FROM xuyi_review_publication_ledger").run();
 const check=await db.prepare("SELECT COUNT(*) AS missing FROM xuyi_review_publication_ledger old "+
  "LEFT JOIN xuyi_review_publication_ledger_v2 v2 ON v2.review_id=old.review_id "+
  "WHERE v2.review_id IS NULL OR v2.model<>old.model OR v2.source_row<>old.source_row "+
  "OR v2.source_model<>old.source_model OR v2.source_fingerprint<>old.source_fingerprint OR v2.published_date<>old.published_date").first();
 if(Number(check?.missing||0)!==0)throw Error("Legacy review ledger migration incomplete");
}
async function requireDb(c){
 if(!c.env.ADMIN_TOKEN)return {error:json({error:"Admin not configured"},503)};
 if(!(await authorizedDailyProductReviewRequest(c.request,c.env)))return {error:json({error:"Unauthorized"},401)};
 if(!c.env.LEYA_DB)return {error:json({error:"Database unavailable"},503)};
 const db=c.env.LEYA_DB;
  try{await ensureProductReviews(db);await ensureLedger(db);await ensurePublishScheduler(db);}
  catch{return {error:json({error:"Review ledger migration failed; no publication was attempted"},503)};} return {db};
}
async function fingerprint(r){
 const raw=r.model+"\n"+r.rating+"\n"+r.author+"\n"+r.content;
 const digest=await crypto.subtle.digest("SHA-256",new TextEncoder().encode(raw));
 return Array.from(new Uint8Array(digest),x=>x.toString(16).padStart(2,"0")).join("");
}
async function getExisting(db){
 const [ledger,reviews,published]=await Promise.all([
  db.prepare("SELECT review_id,model,source_file,source_row,source_model,source_fingerprint,published_date FROM xuyi_review_publication_ledger_v2 ORDER BY published_date,source_file,source_row,review_id").all(),
  db.prepare("SELECT DISTINCT model FROM xuyi_product_reviews").all(),
  db.prepare("SELECT model,rating,author,content FROM xuyi_product_reviews WHERE status='published'").all()
 ]);
 const publishedFingerprints=await Promise.all((published.results||[]).map(fingerprint));
 return {ledger:ledger.results||[],models:new Set((reviews.results||[]).map(x=>x.model)),publishedFingerprints:[...new Set(publishedFingerprints)]};
}
export async function validateDailyInput(input,today=beijingDate()){
 if(input?.date!==today||!dayOK(today))throw Error("发布日期必须是北京时间今天");
 if(input.confirmedAuthentic!==true)throw Error("只能上传已核实且获公开授权的真实客户评价");
 if(!Array.isArray(input.items)||input.items.length<1||input.items.length>20)throw Error("每批只允许 1–20 条客户评价"); const rows=new Set(),fingerprints=new Set();
 for(const r of input.items){
  if(!r||typeof r!=="object")throw Error("Invalid review");
  if(!SOURCE_FILES.has(r.sourceFile))throw Error("评价必须来自已确认的两个 Excel 源文件");
  if(!Number.isInteger(r.sourceRow)||r.sourceRow<2||r.sourceRow>102)throw Error("源表行号无效");
  const key=r.sourceFile+"\n"+r.sourceRow;
  if(rows.has(key))throw Error("同一源文件的行号不能重复");
  rows.add(key);
  if(!MANAGED_MODELS.has(r.model))throw Error("产品型号不存在");
  if((TRANSPARENT[r.sourceModel]||r.sourceModel)!==r.model)throw Error("源表产品型号不对应官网正式型号");
  if(!Number.isInteger(r.rating)||r.rating<1||r.rating>5)throw Error("星级无效");
  if(typeof r.author!=="string"||r.author.trim()!==r.author||r.author.length<2||r.author.length>99)throw Error("客户姓名无效");
  if(typeof r.content!=="string"||r.content.trim()!==r.content||r.content.length<12||r.content.length>3000)throw Error("客户评价原文无效");
  if(!/^[a-f0-9]{64}$/.test(r.sourceFingerprint)||await fingerprint(r)!==r.sourceFingerprint)throw Error("源Excel评价内容与指纹不一致");
  if(fingerprints.has(r.sourceFingerprint))throw Error("同一条评价不能在一批中重复");
  fingerprints.add(r.sourceFingerprint);
 }
 return input.items;
}
export async function onRequestGet(c){
 const {db,error}=await requireDb(c);if(error)return error;
  const state=await getExisting(db);
  const tasks=(await db.prepare("SELECT daily_limit FROM xuyi_publish_tasks WHERE content_type='reviews' AND enabled=1").all()).results||[];
  const maxPerDay=tasks.reduce((sum,x)=>sum+Number(x.daily_limit||0),0);
  return json({today:beijingDate(),recorded:state.ledger,existingModels:[...state.models].sort(),publishedFingerprints:state.publishedFingerprints,maxPerDay,publicationSchema:2});}
export async function onRequestPost(c){
 const {db,error}=await requireDb(c);if(error)return error;
 let input;try{input=await c.request.json()}catch{return json({error:"Invalid JSON"},400)}
 let records;try{records=await validateDailyInput(input)}catch(e){return json({error:e.message},400)}
  const state=await getExisting(db),today=beijingDate();
  const tasks=(await db.prepare("SELECT daily_limit FROM xuyi_publish_tasks WHERE content_type='reviews' AND enabled=1").all()).results||[];
  const maxPerDay=tasks.reduce((sum,x)=>sum+Number(x.daily_limit||0),0);
  if(maxPerDay<1)return json({error:"产品评价自动发布任务当前已暂停"},409);
  const todayCount=state.ledger.filter(x=>x.published_date===today).length;
  const used=new Set([...state.ledger.map(x=>x.source_fingerprint),...state.publishedFingerprints]);
  const candidates=records.filter(x=>!used.has(x.sourceFingerprint));
  if(todayCount+candidates.length>maxPerDay)return json({error:"已达到后台设置的每日评价发布上限 "+maxPerDay,todayCount,maxPerDay},409); if(!candidates.length)return json({success:true,inserted:0,skipped:records.length,todayCount,recorded:state.ledger});
 const statements=[];
 for(const r of candidates){
  const id=crypto.randomUUID();
  statements.push(db.prepare("INSERT INTO xuyi_product_reviews (id,model,rating,author,review_date,content,status) VALUES(?,?,?,?,?,?,'published')").bind(id,r.model,r.rating,r.author,today,r.content));
  statements.push(db.prepare("INSERT INTO xuyi_review_publication_ledger_v2 (review_id,model,source_file,source_row,source_model,source_fingerprint,published_date) VALUES(?,?,?,?,?,?,?)").bind(id,r.model,r.sourceFile,r.sourceRow,r.sourceModel,r.sourceFingerprint,today));
 }
 const result=await db.batch(statements);
 if(!Array.isArray(result)||result.length!==statements.length||result.some(x=>x.meta?.changes!==1))return json({error:"Unexpected insert result; inspect the D1 ledger before retry"},500);
 const revision=await bumpPublishRevision(db),finalState=await getExisting(db);
 return json({success:true,date:today,inserted:candidates.length,skipped:records.length-candidates.length,
  todayCount:finalState.ledger.filter(x=>x.published_date===today).length,recorded:finalState.ledger,...revision});
}