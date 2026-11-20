import assert from "node:assert/strict";
import {createHash} from "node:crypto";
import {beijingDate,validateDailyInput,onRequestGet,onRequestPost} from "../functions/api/admin/daily-product-reviews.js";
import {authorizedDailyProductReviewRequest} from "../functions/_shared/build-auth.js";
const FILE_A="101-zhenshipingjia.xlsx",FILE_B="101-additional-reviews-only.xlsx",today=beijingDate();
const originalFetch=globalThis.fetch;
globalThis.fetch=async(url,options)=>{
 assert.equal(url,"https://api.cloudflare.com/client/v4/accounts/a4032d0251103d6ef680b2aaddce1afc/pages/projects/leyamould");
 const ok=options.headers.authorization==="Bearer cloudflare-review-ci-test";
 return Response.json({success:ok,result:{name:ok?"leyamould":"other-site"}},{status:ok?200:403});
};
const special=new Request("https://leyamould.com/api/admin/daily-product-reviews",{method:"GET",headers:{authorization:"Bearer cloudflare-review-ci-test"}});
assert.equal(await authorizedDailyProductReviewRequest(special,{ADMIN_TOKEN:"not-the-project-token"}),true);
assert.equal(beijingDate(new Date("2026-10-20T16:01:00Z")),"2026-10-21");
const make=(model,row,rating,file,author)=>({model,sourceModel:model,sourceRow:row,sourceFile:file,rating,author,
 content:"Original feedback from "+author+" for "+model+" was delivered in this product order."});
const fp=r=>createHash("sha256").update(r.model+"\n"+r.rating+"\n"+r.author+"\n"+r.content).digest("hex");
const records=[make("LO-001",2,5,FILE_A,"Buyer A"),make("LO-001",2,4,FILE_B,"Buyer B"),make("LO-002",3,5,FILE_A,"Buyer C"),make("LO-004",4,5,FILE_A,"Buyer D")];
for(const r of records)r.sourceFingerprint=fp(r);
const payload={date:today,confirmedAuthentic:true,items:records.slice(0,3)};
assert.deepEqual(await validateDailyInput(payload),payload.items,"Two different buyers may review the same SKU");
assert.deepEqual(await validateDailyInput({...payload,items:records}),records,"Batch validation permits more than three; the configured daily cap is enforced against D1 at publish time");
for(const changed of [
 {...payload,date:"2020-01-01"},{...payload,confirmedAuthentic:false}, {...payload,items:[records[0],{...records[1],sourceFile:FILE_A,sourceRow:2}]},
 {...payload,items:[records[0],{...records[0],sourceFile:FILE_B,sourceRow:2}]},
 {...payload,items:[{...records[0],sourceFile:"third-source.xlsx"}]},
 {...payload,items:[{...records[0],rating:1}]},{...payload,items:[{...records[0],sourceModel:"OTHER"}]}
])await assert.rejects(()=>validateDailyInput(changed));
const transparent=make("2306透明款",75,4,FILE_A,"Transparent Buyer");
transparent.sourceModel="2306-transparent";transparent.sourceFingerprint=fp(transparent);
assert.deepEqual(await validateDailyInput({...payload,items:[transparent]}),[transparent]);

class D1Mock{
 constructor(){this.reviews=new Map();this.legacy=new Map();this.ledger=new Map();this.tasks=new Map();this.revision=13;} prepare(sql){
  const db=this;
  return {sql,params:[],bind(...a){this.params=a;return this},
   async first(){
    if(sql.startsWith("SELECT value FROM site_state"))return {value:String(db.revision)};
    if(sql.startsWith("SELECT COUNT(*) AS missing FROM xuyi_review_publication_ledger old")){
     let n=0;for(const old of db.legacy.values()){const x=db.ledger.get(old.review_id);
      if(!x||x.model!==old.model||x.source_row!==old.source_row||x.source_model!==old.source_model||x.source_fingerprint!==old.source_fingerprint||x.published_date!==old.published_date)n++;}
     return {missing:n};
    }return null;
   },
   async all(){
     if(sql.startsWith("SELECT daily_limit FROM xuyi_publish_tasks"))return {results:[...db.tasks.values()].filter(x=>x.content_type==="reviews"&&x.enabled===1).map(x=>({daily_limit:x.daily_limit}))};
     if(sql.startsWith("SELECT review_id,model,source_file,source_row,source_model,source_fingerprint,published_date FROM xuyi_review_publication_ledger_v2"))     return {results:[...db.ledger.values()]};
    if(sql.startsWith("SELECT DISTINCT model FROM xuyi_product_reviews"))
     return {results:[...new Set([...db.reviews.values()].map(x=>x.model))].map(model=>({model}))};
    if(sql.startsWith("SELECT model,rating,author,content FROM xuyi_product_reviews WHERE status='published'"))
     return {results:[...db.reviews.values()].filter(x=>x.status==="published").map(({model,rating,author,content})=>({model,rating,author,content}))};
    throw Error("Unrecognized query "+sql);
   },
   async run(){
     if(sql.startsWith("CREATE TABLE")||sql.startsWith("CREATE INDEX"))return {meta:{changes:0}};
     if(sql.startsWith("INSERT OR IGNORE INTO xuyi_publish_tasks")){const [id,content_type,name,enabled,timezone,schedule_time,daily_limit]=this.params;if(!db.tasks.has(id))db.tasks.set(id,{id,content_type,name,enabled,timezone,schedule_time,daily_limit});return {meta:{changes:1}};}    if(sql.startsWith("INSERT OR IGNORE INTO xuyi_review_publication_ledger_v2")){
     for(const old of db.legacy.values())if(!db.ledger.has(old.review_id))db.ledger.set(old.review_id,{...old,source_file:"legacy-unmapped"});
     return {meta:{changes:db.legacy.size}};
    }
    if(sql.startsWith("INSERT INTO xuyi_product_reviews")){
     const [id,model,rating,author,date,content]=this.params;
     db.reviews.set(id,{id,model,rating,author,review_date:date,content,status:"published"});return {meta:{changes:1}};
    }
    if(sql.startsWith("INSERT INTO xuyi_review_publication_ledger_v2")){
     const [review_id,model,source_file,source_row,source_model,source_fingerprint,published_date]=this.params;
     if([...db.ledger.values()].some(x=>x.review_id===review_id||x.source_fingerprint===source_fingerprint||(x.source_file===source_file&&x.source_row===source_row)))throw Error("Duplicate ledger identity");
     db.ledger.set(review_id,{review_id,model,source_file,source_row,source_model,source_fingerprint,published_date});return {meta:{changes:1}};
    }
    if(sql.startsWith("INSERT INTO site_state")){if(this.params[0].match(/^\d+$/))db.revision=Number(this.params[0]);return {meta:{changes:1}};}
    throw Error("Unexpected statement "+sql);
   }
  };
 }
 async batch(stmts){
  const a=new Map(this.reviews),b=new Map(this.ledger),rev=this.revision;
  try{const out=[];for(const s of stmts)out.push(await s.run());return out;}
  catch(e){this.reviews=a;this.ledger=b;this.revision=rev;throw e;}
 }
}
const db=new D1Mock(),env={ADMIN_TOKEN:"xuyi-test-admin",XUYI_DB:db};
const ctx=(body,token=env.ADMIN_TOKEN)=>({env,request:new Request("https://leyamould.com/api/admin/daily-product-reviews",{
 method:body?"POST":"GET",headers:{authorization:"Bearer "+token,"content-type":"application/json"},body:body?JSON.stringify(body):undefined})});
assert.equal((await onRequestGet(ctx(undefined,"wrong"))).status,401);
assert.equal(await authorizedDailyProductReviewRequest(new Request("https://leyamould.com/api/admin/product-reviews",{method:"GET",headers:{authorization:"Bearer xuyi-test-admin"}}),env),false);
const legacyId="d55abf0c-71ca-4dd2-a3ab-a4107e62fd83";
const legacy={id:legacyId,model:"LO-004",rating:5,author:"Legacy Buyer",content:"A legacy published review must survive the v2 migration.",status:"published"};
db.reviews.set(legacyId,legacy);
db.legacy.set("LO-004",{model:"LO-004",source_row:8,source_model:"LO-004",source_fingerprint:fp({...legacy}),published_date:"2026-11-01",review_id:legacyId});
let reply=await onRequestGet(ctx());assert.equal(reply.status,200);
let migrated=await reply.json();assert.equal(migrated.publicationSchema,2);assert.equal(migrated.recorded.length,1);
assert.equal(migrated.recorded[0].source_file,"legacy-unmapped");
assert.equal((await (await onRequestGet(ctx())).json()).recorded.length,1,"Legacy migration is idempotent");
reply=await onRequestPost(ctx(payload));assert.equal(reply.status,200);
let result=await reply.json();assert.equal(result.inserted,3);assert.equal(result.todayCount,3);
assert.equal(db.reviews.size,4);assert.equal(db.ledger.size,4);
assert.equal([...db.reviews.values()].filter(x=>x.model==="LO-001").length,2);
const revision=db.revision;
reply=await onRequestPost(ctx(payload));result=await reply.json();
assert.equal(result.inserted,0);assert.equal(db.revision,revision);assert.equal(db.reviews.size,4);
const first=[...db.ledger.values()].find(x=>x.source_fingerprint===records[0].sourceFingerprint);
db.reviews.delete(first.review_id);
reply=await onRequestPost(ctx({...payload,items:[records[0]]}));
assert.equal((await reply.json()).inserted,0);assert.equal(db.reviews.size,3);assert.equal(db.ledger.size,4);
reply=await onRequestPost(ctx({...payload,items:[records[3]]}));
assert.equal(reply.status,409);assert.equal(db.ledger.size,4);
db.tasks.get("reviews-daily").daily_limit=5;
reply=await onRequestGet(ctx());assert.equal((await reply.json()).maxPerDay,5,"The daily limit is read from the D1 scheduler task.");
reply=await onRequestPost(ctx({...payload,items:[records[3]]}));
assert.equal(reply.status,200,"Increasing the backend daily limit permits the additional authentic review.");
assert.equal((await reply.json()).todayCount,4);
globalThis.fetch=originalFetch;
console.log("XUYI_D1_V2_MULTI_REVIEW_PER_SKU_LEGACY_MIGRATION_FINGERPRINT_IDEMPOTENCE_DAILY_LIMIT_PASS");