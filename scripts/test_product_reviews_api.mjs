import assert from "node:assert/strict";
import {normalizeProductReview,REVIEW_TABLE} from "../functions/_shared/product-reviews.js";
import {onRequestGet,onRequestPost} from "../functions/api/admin/product-reviews.js";

const sample={model:"2305",rating:4,author:"Maria Chen",reviewDate:"2026-10-09",
              content:"The order arrived in good condition and matched our approved sample.",
              status:"published",confirmedAuthentic:true};
assert.deepEqual(normalizeProductReview(sample),{
 model:"2305",rating:4,author:"Maria Chen",reviewDate:"2026-10-09",
 content:sample.content,status:"published"
});
for(const edited of [
 {...sample,rating:0},{...sample,rating:6},{...sample,rating:2.5},
 {...sample,rating:""},{...sample,reviewDate:"2026-02-30"},
 {...sample,author:"A"},{...sample,content:"short"},
 {...sample,status:"published",confirmedAuthentic:false},
 {...sample,model:"not/a/model"}
])assert.throws(()=>normalizeProductReview(edited));
assert.match(REVIEW_TABLE,/CHECK\(rating BETWEEN 1 AND 5\)/);
assert.match(REVIEW_TABLE,/status IN \('draft','published'\)/);

class MemoryD1{
 constructor(){this.rows=new Map();this.revision=13}
 prepare(sql){
  const db=this;
  const statement={params:[],bind(...values){this.params=values;return this},
   async first(){
    if(sql.startsWith("SELECT value FROM site_state"))return {value:String(db.revision)};
    if(sql.startsWith("SELECT id FROM xuyi_product_reviews"))return db.rows.has(this.params[0])?{id:this.params[0]}:null;
    if(sql.startsWith("SELECT publication_status"))return null;
    return null;
   },
   async all(){
    if(sql.includes("FROM xuyi_product_reviews")){
     return {results:[...db.rows.values()].map(x=>({id:x.id,model:x.model,rating:x.rating,
       author:x.author,review_date:x.reviewDate,content:x.content,status:x.status,updated_at:"now"}))};
    }
    return {results:[]};
   },
   async run(){
    if(sql.startsWith("CREATE TABLE"))return {meta:{changes:0}};
    if(sql.startsWith("DELETE FROM xuyi_product_reviews")){
     const exists=db.rows.delete(this.params[0]);return {meta:{changes:exists?1:0}};
    }
    if(sql.startsWith("INSERT INTO xuyi_product_reviews")){
     const [id,model,rating,author,reviewDate,content,status]=this.params;
     db.rows.set(id,{id,model,rating,author,reviewDate,content,status});
     return {meta:{changes:1}};
    }
    if(sql.startsWith("INSERT INTO site_state")){
     if(this.params[0].match(/^\d+$/))db.revision=Number(this.params[0]);
     return {meta:{changes:1}};
    }
    throw Error("Unexpected SQL: "+sql);
   }
  };
  return statement;
 }
 async batch(statements){return Promise.all(statements.map(x=>x.run()))}
}
const db=new MemoryD1(),env={ADMIN_TOKEN:"review-test-secret",XUYI_DB:db};
const context=(body,secret="review-test-secret")=>({
 env,request:new Request("https://xuyibottles.com/api/admin/product-reviews",{
  method:body?"POST":"GET",
  headers:{"authorization":"Bearer "+secret,"content-type":"application/json"},
  body:body?JSON.stringify(body):undefined
 })
});
assert.equal((await onRequestGet(context(undefined,"wrong"))).status,401);
let r=await onRequestPost(context({action:"save",...sample,confirmedAuthentic:false}));
assert.equal(r.status,400,"Publishing without authentic review confirmation denied");
assert.equal(db.rows.size,0);
r=await onRequestPost(context({action:"save",...sample,status:"draft",confirmedAuthentic:false}));
assert.equal(r.status,200);
let result=await r.json();
const id=result.id;
assert.equal(result.status,"draft");
assert.equal(db.rows.size,1);
let listing=await (await onRequestGet(context())).json();
assert.equal(listing.items.length,1);
assert(listing.models.includes("2305"),"Real SKU picker must include source models");
r=await onRequestPost(context({action:"save",id,...sample}));
assert.equal(r.status,200);
result=await r.json();
assert.equal(result.status,"published");
assert.equal(db.rows.get(id).rating,4);
assert.equal(db.rows.size,1,"Editing does not create duplicate records");
r=await onRequestPost(context({action:"save",id,...sample,status:"draft",confirmedAuthentic:false}));
assert.equal(r.status,200);
assert.equal(db.rows.get(id).status,"draft","Unpublishing must remove from next build");
r=await onRequestPost(context({action:"delete",id}));
assert.equal(r.status,200);
assert.equal(db.rows.size,0);
assert.equal((await onRequestPost(context({action:"delete",id}))).status,404);
assert(db.revision>=17,"Every edit/delete must enqueue a D1 publish revision");
console.log("XUYI_D1_PRODUCT_REVIEW_ADMIN_AUTH_VALIDATION_CRUD_AND_REVISION_PASS");
