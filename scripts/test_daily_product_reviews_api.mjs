import assert from "node:assert/strict";
import {createHash} from "node:crypto";
import {beijingDate,validateDailyInput,onRequestGet,onRequestPost} from "../functions/api/admin/daily-product-reviews.js";
import {authorizedDailyProductReviewRequest} from "../functions/_shared/build-auth.js";
const today=beijingDate();
// Validate the exact Pages-project deployment-token exception offline;
// no CI test may depend on an external Cloudflare request.
const originalFetch=globalThis.fetch;
globalThis.fetch=async (url,options)=>{
 assert.equal(url,
  "https://api.cloudflare.com/client/v4/accounts/a4032d0251103d6ef680b2aaddce1afc/pages/projects/xuyi-drinkware-site");
 const ok=options.headers.authorization==="Bearer cloudflare-review-ci-test";
 return Response.json({success:ok,result:{name:ok?"xuyi-drinkware-site":"other-site"}},
  {status:ok?200:403});
};
const special=new Request("https://xuyibottles.com/api/admin/daily-product-reviews",
 {method:"GET",headers:{authorization:"Bearer cloudflare-review-ci-test"}});
assert.equal(await authorizedDailyProductReviewRequest(special,{ADMIN_TOKEN:"not-the-project-token"}),true);
assert.match(today,/^\d{4}-\d{2}-\d{2}$/);
assert.equal(beijingDate(new Date("2026-10-20T01:00:00Z")),"2026-10-20");
assert.equal(beijingDate(new Date("2026-10-20T16:01:00Z")),"2026-10-21");
const make=(model,index=2,rating=5,original=model)=>({
 model,sourceModel:original,sourceRow:index,rating,
 author:"Real Buyer "+model,content:"Original feedback for "+model+" was delivered in this product order.",
});
const fingerprint=r=>createHash("sha256").update(
 r.model+"\n"+r.rating+"\n"+r.author+"\n"+r.content).digest("hex");
const records=[make("LO-001"),make("LO-002",3,4),make("LO-003",4),make("LO-004",5)];
for(const r of records)r.sourceFingerprint=fingerprint(r);
const payload={date:today,confirmedAuthentic:true,items:records.slice(0,3)};
assert.deepEqual(await validateDailyInput(payload),payload.items);
// Owner explicitly approved FOUR on this one Beijing date only. Normal 3-limit remains.
const ownerFour={date:"2026-10-28",confirmedAuthentic:true,
  ownerBatch:"xuyi-owner-random-four-20261028",items:records};
assert.deepEqual(await validateDailyInput(ownerFour,"2026-10-28"),records);
await assert.rejects(()=>validateDailyInput({...ownerFour,ownerBatch:"wrong"},"2026-10-28"));
await assert.rejects(()=>validateDailyInput(ownerFour,"2026-10-29"));

for(const changed of [
 {...payload,date:"2020-01-01"},
 {...payload,confirmedAuthentic:false},
 {...payload,items:records},
 {...payload,items:[{...records[0],model:"LO-002"}]},
 {...payload,items:[{...records[0],rating:1}]},
 {...payload,items:[records[0],records[0]]},
 {...payload,items:[{...records[0],sourceModel:"OTHER"}]},
])await assert.rejects(()=>validateDailyInput(changed));
const transparent=make("2306透明款",75,4,"2306-transparent");
transparent.sourceFingerprint=fingerprint(transparent);
assert.deepEqual(await validateDailyInput({...payload,items:[transparent]}),[transparent]);

class D1Mock{
 constructor(){this.reviews=new Map();this.ledger=new Map();this.revision=13;}
 prepare(sql){
  const db=this;
  return {sql,params:[],bind(...args){this.params=args;return this},
   async first(){
    if(sql.startsWith("SELECT value FROM site_state"))return {value:String(db.revision)};
    return null;
   },
   async all(){
    if(sql.startsWith("SELECT model,source_model,source_row")){
     return {results:[...db.ledger.values()].sort((a,b)=>a.source_row-b.source_row)};
    }
    if(sql.startsWith("SELECT DISTINCT model FROM xuyi_product_reviews")){
     return {results:[...db.reviews.values()].map(x=>({model:x.model}))};
    }
    throw Error("Unrecognized query "+sql);
   },
   async run(){
    if(sql.startsWith("CREATE TABLE"))return {meta:{changes:0}};
    if(sql.startsWith("INSERT INTO xuyi_product_reviews")){
     const [id,model,rating,author,date,content]=this.params;
     if([...db.reviews.values()].some(x=>x.model===model))throw Error("Duplicate model");
     db.reviews.set(id,{id,model,rating,author,review_date:date,content,status:"published"});
     return {meta:{changes:1}};
    }
    if(sql.startsWith("INSERT INTO xuyi_review_publication_ledger")){
     const [model,source_row,source_model,source_fingerprint,published_date,review_id]=this.params;
     if(db.ledger.has(model))throw Error("Duplicate ledger");
     db.ledger.set(model,{model,source_row,source_model,source_fingerprint,published_date,review_id});
     return {meta:{changes:1}};
    }
    if(sql.startsWith("INSERT INTO site_state")){
     if(this.params[0].match(/^\d+$/))db.revision=Number(this.params[0]);
     return {meta:{changes:1}};
    }
    throw Error("Unexpected statement "+sql);
   }
  };
 }
 async batch(statements){
  const snapshotReviews=new Map(this.reviews),snapshotLedger=new Map(this.ledger),oldRev=this.revision;
  try{return await Promise.all(statements.map(async stmt=>stmt.run()))}
  catch(err){this.reviews=snapshotReviews;this.ledger=snapshotLedger;this.revision=oldRev;throw err}
 }
}
const db=new D1Mock();
const env={ADMIN_TOKEN:"xuyi-test-admin",XUYI_DB:db};
const context=(body,token=env.ADMIN_TOKEN)=>({env,request:new Request(
 "https://xuyibottles.com/api/admin/daily-product-reviews",{
  method:body?"POST":"GET",
  headers:{authorization:"Bearer "+token,"content-type":"application/json"},
  body:body?JSON.stringify(body):undefined
 })});
assert.equal((await onRequestGet(context(undefined,"wrong-password"))).status,401);
assert.equal(await authorizedDailyProductReviewRequest(
  new Request("https://xuyibottles.com/api/admin/product-reviews",{method:"GET",
   headers:{authorization:"Bearer xuyi-test-admin"}}),env),false,
 "Special Cloudflare project token cannot authorize arbitrary admin routes");
let reply=await onRequestPost(context(payload));
assert.equal(reply.status,200);
let result=await reply.json();
assert.equal(result.inserted,3);
assert.equal(result.todayCount,3);
assert.equal(db.reviews.size,3);
assert.equal(db.ledger.size,3);
const firstRevision=db.revision;
reply=await onRequestPost(context(payload));
assert.equal(reply.status,200);
result=await reply.json();
assert.equal(result.inserted,0);
assert.equal(db.revision,firstRevision);
assert.equal(db.reviews.size,3);
// The source ledger survives a manual deletion of the publicly visible review.
db.reviews.delete(db.ledger.get("LO-001").review_id);
reply=await onRequestPost(context({...payload,items:[records[0]]}));
assert.equal((await reply.json()).inserted,0);
assert.equal(db.reviews.size,2);
assert.equal(db.ledger.size,3);
// It must be impossible to publish a fourth model on the same Beijing date.
reply=await onRequestPost(context({...payload,items:[records[3]]}));
assert.equal(reply.status,409);
assert.equal(db.ledger.size,3);
globalThis.fetch=originalFetch;
console.log("XUYI_D1_THREE_DAILY_REVIEWS_EXACT_SKU_PERMANENT_LEDGER_SECURITY_PASS");
