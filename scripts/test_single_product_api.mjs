import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
const source=path=>readFileSync(new URL("../"+path,import.meta.url),"utf8");
const url=contents=>"data:text/javascript;base64,"+Buffer.from(contents).toString("base64");
const usage=source("functions/_shared/r2-usage.js");
const productSource=source("functions/_shared/new-product.js")
 .replace('import {MANAGED_MODELS} from "./xuyi-routes.js";','const MANAGED_MODELS=new Set(["2095"]);')
 .replace('import {imageKey} from "./r2-usage.js";','import {imageKey} from "'+url(usage)+'";');
const norm=await import(url(productSource));
const img="/media/product/"+"a".repeat(32)+".webp";
const good={category:"Plastic Sports Water Bottles",name:"QA Bottle",material:"PP",capacity:"750ml",
 description:"Only used to test manual product flow.",image:img,seoTitle:"QA | XUYI",seoDescription:"QA test"};
assert.equal(norm.normalizeNewProduct("bottle-qa-9001",good,"published").newProduct,true);
assert.throws(()=>norm.normalizeNewProduct("2095",good),"must not override existing original model");
assert.throws(()=>norm.normalizeNewProduct("other/route",good));
assert.throws(()=>norm.normalizeNewProduct("bottle-q",{}, "published"));
assert.throws(()=>norm.normalizeNewProduct("bottle-q",{...good,image:"https://example.org/a.jpg"},"published"));
assert.equal(norm.normalizeNewProduct("bottle-q",{...good,image:""},"draft").image,"");
let allowed=false,dbRows=new Map(),revision=5,assetFound=false,hasR2=true;
const apiText=source("functions/api/admin/product-content.js")
 .replace('import { authorizedBuildRequest } from "../../_shared/build-auth.js";','const authorizedBuildRequest=async()=>true;')
 .replace('import { bumpPublishRevision } from "../../_shared/site-settings.js";','const bumpPublishRevision=async()=>({revision:++globalThis.__rev.value});')
 .replace('import { MANAGED_MODELS } from "../../_shared/xuyi-routes.js";','const MANAGED_MODELS=new Set(["2095","LO-008"]);')
 .replace('import { authorizeAdminRequest } from "../../_shared/admin-security.js";','const authorizeAdminRequest=async()=>globalThis.__allowed.value;')
 .replace('import { normalizeNewProduct,CATEGORY_OPTIONS } from "../../_shared/new-product.js";','import {normalizeNewProduct,CATEGORY_OPTIONS} from "'+url(productSource)+'";')
 .replace('import { imageKey } from "../../_shared/r2-usage.js";','import {imageKey} from "'+url(usage)+'";');
globalThis.__allowed={value:false};globalThis.__rev={value:revision};
const api=await import(url(apiText));
const db={
 prepare(sql){
  const plan={bind(...args){
   return {first:async()=>{
    const row=dbRows.get(args[0]);return row?{content_json:row.content,publication_status:row.status}:null;
   },run:async()=>{
    if(sql.includes("INSERT INTO xuyi_product_content"))dbRows.set(args[0],{content:args[1],status:args[2]});
    return {success:true}
   }};
  },run:async()=>({success:true}),all:async()=>({results:[...dbRows].map(([model,row])=>({
   model,content_json:row.content,publication_status:row.status,updated_at:"2026-10-10"
  }))})};return plan;
 }
};
const env={ADMIN_TOKEN:"test-admin",XUYI_DB:db,
 XUYI_ASSETS:{head:async()=>assetFound?{size:15200}:null}};
const ctx=(body)=>({request:new Request("https://xuyibottles.com/api/admin/product-content",{
 method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify(body)}),env});
const payload=(model,status,content)=>({action:"create_product",model,status,content});
let res=await api.onRequestPost(ctx(payload("bottle-qa-9001","published",good)));
assert.equal(res.status,401,"Build token must not be able to create new products");
globalThis.__allowed.value=true;
res=await api.onRequestPost(ctx(payload("2095","draft",good)));
assert.equal(res.status,400,"Legacy model collisions rejected");
res=await api.onRequestPost(ctx(payload("bottle-qa-9001","published",good)));
assert.equal(res.status,409,"Missing R2 image rejects publication");
assetFound=true;
res=await api.onRequestPost(ctx(payload("bottle-qa-9001","draft",{...good,image:""})));
assert.equal(res.status,200,"New product draft may save without image");
assert.equal(dbRows.get("bottle-qa-9001").status,"draft");
res=await api.onRequestPost(ctx(payload("bottle-qa-9001","published",good)));
assert.equal(res.status,200,"New product publishes with verified R2 image");
const output=await res.json();
assert.equal(output.route,"/products/bottle-qa-9001/");
assert.equal(output.revision,7);
assert.equal(dbRows.get("bottle-qa-9001").status,"published");
const list=await (await api.onRequestGet({
 request:new Request("https://xuyibottles.com/api/admin/product-content"),env
})).json();
assert.equal(list.items.length,1);
assert.equal(list.categories.length,4);
assert.equal(list.items[0].content.newProduct,true);
assert.deepEqual(list.catalogModels,["2095","LO-008"],"All source catalog models must be searchable without saved D1 overrides");
console.log("XUYI_SINGLE_PRODUCT_CMS_API_TESTS_PASSED",17,"checks; isolated mock, no remote D1 writes");