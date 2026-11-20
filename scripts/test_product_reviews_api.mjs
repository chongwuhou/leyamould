import assert from "node:assert/strict";
import {normalizeProductReview,REVIEW_TABLE} from "../functions/_shared/product-reviews.js";
import {onRequestGet,onRequestPost} from "../functions/api/admin/product-reviews.js";
const sample={model:"2305",rating:4,author:"Maria Chen",reviewDate:"2026-10-09",content:"The order arrived in good condition and matched our approved sample.",status:"published",confirmedAuthentic:true};
assert.deepEqual(normalizeProductReview(sample),{model:"2305",rating:4,author:"Maria Chen",reviewDate:"2026-10-09",content:sample.content,status:"published"});
for(const x of [{...sample,rating:0},{...sample,rating:6},{...sample,rating:2.5},{...sample,rating:""},{...sample,reviewDate:"2026-02-30"},{...sample,author:"A"},{...sample,content:"short"},{...sample,status:"published",confirmedAuthentic:false},{...sample,model:"not/a/model"}])assert.throws(()=>normalizeProductReview(x));
assert.match(REVIEW_TABLE,/CHECK\(rating BETWEEN 1 AND 5\)/);
assert.match(REVIEW_TABLE,/status IN \('draft','published'\)/);
class MemoryD1{
 constructor(){this.rows=new Map();this.revision=13}
 prepare(sql){const db=this;return {params:[],bind(...v){this.params=v;return this},
  async first(){if(sql.startsWith("SELECT value FROM site_state"))return {value:String(db.revision)};if(sql.startsWith("SELECT id FROM xuyi_product_reviews"))return db.rows.has(this.params[0])?{id:this.params[0]}:null;if(sql.startsWith("SELECT publication_status"))return null;return null;},
  async all(){if(sql.includes("FROM xuyi_product_reviews"))return {results:[...db.rows.values()].map(x=>({...x,review_date:x.reviewDate,updated_at:"now"}))};return {results:[]};},
  async run(){if(sql.startsWith("CREATE TABLE"))return {meta:{changes:0}};if(sql.startsWith("DELETE FROM xuyi_product_reviews")){const ok=db.rows.delete(this.params[0]);return {meta:{changes:ok?1:0}};}if(sql.startsWith("INSERT INTO xuyi_product_reviews")){const [id,model,rating,author,reviewDate,content,status]=this.params;db.rows.set(id,{id,model,rating,author,reviewDate,content,status});return {meta:{changes:1}};}if(sql.startsWith("INSERT INTO site_state")){if(this.params[0].match(/^\d+$/))db.revision=Number(this.params[0]);return {meta:{changes:1}};}throw Error("Unexpected SQL "+sql);}
 };}
 async batch(stmts){return Promise.all(stmts.map(x=>x.run()));}
}
const db=new MemoryD1(),env={ADMIN_TOKEN:"review-test-secret",XUYI_DB:db};
const ctx=(body,secret="review-test-secret")=>({env,request:new Request("https://leyamould.com/api/admin/product-reviews",{method:body?"POST":"GET",headers:{authorization:"Bearer "+secret,"content-type":"application/json"},body:body?JSON.stringify(body):undefined})});
assert.equal((await onRequestGet(ctx(undefined,"wrong"))).status,401);
let r=await onRequestPost(ctx({action:"save",...sample,confirmedAuthentic:false}));assert.equal(r.status,400);assert.equal(db.rows.size,0);
r=await onRequestPost(ctx({action:"save",...sample,status:"draft",confirmedAuthentic:false}));assert.equal(r.status,200);
let result=await r.json(),id=result.id;assert.equal(result.status,"draft");assert.equal(db.rows.size,1);
let listing=await (await onRequestGet(ctx())).json();assert.equal(listing.items.length,1);assert(listing.models.includes("2305"));
r=await onRequestPost(ctx({action:"save",id,...sample}));assert.equal(r.status,200);assert.equal((await r.json()).status,"published");assert.equal(db.rows.get(id).rating,4);
const second={...sample,author:"Another Real Buyer",reviewDate:"2026-10-10",content:"A second buyer confirmed the cap fit and the cartons arrived intact."};
r=await onRequestPost(ctx({action:"save",...second}));assert.equal(r.status,200);const secondId=(await r.json()).id;assert.notEqual(secondId,id);
listing=await (await onRequestGet(ctx())).json();assert.equal(listing.items.filter(x=>x.model==="2305").length,2);
r=await onRequestPost(ctx({action:"save",id,...sample,status:"draft",confirmedAuthentic:false}));assert.equal(r.status,200);assert.equal(db.rows.get(id).status,"draft");
r=await onRequestPost(ctx({action:"delete",id}));assert.equal(r.status,200);assert.equal(db.rows.size,1);assert(db.rows.has(secondId));
assert.equal((await onRequestPost(ctx({action:"delete",id}))).status,404);
assert(db.revision>=18);console.log("XUYI_D1_PRODUCT_REVIEW_ADMIN_MULTI_REVIEW_AUTH_VALIDATION_CRUD_AND_REVISION_PASS");