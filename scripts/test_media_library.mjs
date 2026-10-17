import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
const base=(file)=>new URL("../"+file,import.meta.url);
const uri=s=>"data:text/javascript;base64,"+Buffer.from(s).toString("base64");
const imageHelper=readFileSync(base("functions/_shared/media-image.js"),"utf8");
const usageHelper=readFileSync(base("functions/_shared/r2-usage.js"),"utf8");
const altHelper=readFileSync(base("functions/_shared/media-alt.js"),"utf8");
const raw=readFileSync(base("functions/api/admin/media.js"),"utf8")
 .replace('import {authorizeAdminRequest} from "../../_shared/admin-security.js";',
   'const authorizeAdminRequest=async(request)=>request.headers.get("x-test-admin")==="yes";')
 .replace('import {KINDS,readUsageIndex,findMediaUsage,imageKey} from "../../_shared/r2-usage.js";',
   'import {KINDS,readUsageIndex,findMediaUsage,imageKey} from "'+uri(usageHelper)+'";')
 .replace('import {checkedImage} from "../../_shared/media-image.js";',
   'import { checkedImage } from "'+uri(imageHelper)+'";')
 .replace('import {normalizeAltMap,ensureMediaAlt,upsertMediaAlt} from "../../_shared/media-alt.js";',
   'import {normalizeAltMap,ensureMediaAlt,upsertMediaAlt} from "'+uri(altHelper)+'";')
 .replace('import {bumpPublishRevision} from "../../_shared/site-settings.js";',
   'const bumpPublishRevision=async()=>({revision:++globalThis.__testMediaRevision.value});');
const {onRequestGet,onRequestPost,onRequestDelete}=await import(uri(raw));
const objects=new Map();
const storage={
 put:async(key,body,options)=>{objects.set(key,{body,options})},
 list:async({prefix})=>({objects:[...objects.keys()].filter(x=>x.startsWith(prefix)).map(key=>({key,size:objects.get(key).body.byteLength,uploaded:new Date("2026-10-09")})),truncated:false}),
 get:async(key)=>objects.has(key)?{body:objects.get(key).body}:null,
 head:async(key)=>objects.has(key)?{size:objects.get(key).body.byteLength}:null,
 delete:async(key)=>{objects.delete(key)}
};
let staticRefs={},liveRefs=new Set(),mediaAlts=new Map();
globalThis.__testMediaRevision={value:8};
const env={ADMIN_TOKEN:"a-test-admin",XUYI_ASSETS:storage,
 ASSETS:{fetch:async()=>Response.json({site:"xuyi-drinkware-site",schemaVersion:1,publishRevision:8,references:staticRefs})},
 XUYI_DB:{prepare:sql=>{
   let args=[];
   const q={
     bind:(...params)=>{args=params;return q},
     run:async()=>{
       if(sql.includes("INSERT INTO xuyi_media_alt"))mediaAlts.set(args[0],args[1]);
       if(sql.includes("DELETE FROM xuyi_media_alt"))mediaAlts.delete(args[0]);
       return {success:true}
     },
     first:async()=>sql.includes("site_state")?{value:sql.includes("language_config")?
        JSON.stringify({languages:[{code:"en",nativeName:"English"},{code:"es",nativeName:"Español"}]}):"8"}:null,
     all:async()=>({results:sql.includes("FROM xuyi_media_alt")?[...mediaAlts].map(([path,alt_json])=>({path,alt_json})):
       liveRefs.has(args[0])&&sql.includes("xuyi_product_content")?[{ref:"2501"}]:[]})
   };return q
 }}
};
const context=(request)=>({request,env});
let response=await onRequestGet(context(new Request("https://xuyibottles.com/api/admin/media")));
assert.equal(response.status,401,"media list must reject unauthenticated users");
let req=new Request("https://xuyibottles.com/api/admin/media?kind=product",{headers:{"x-test-admin":"yes"}});
response=await onRequestGet(context(req));assert.equal(response.status,200);
assert.deepEqual((await response.json()).items,[]);
const png=Uint8Array.from([137,80,78,71,...Array(240).fill(0)]);
const submit=async(file,kind="product")=>{
 const data=new FormData();data.append("kind",kind);data.append("image",file);
 data.append("altByLocale",JSON.stringify({en:"Plastic sports water bottle model 2501, catalog photo",es:"Botella deportiva de plástico modelo 2501"}));
 return onRequestPost(context(new Request("https://xuyibottles.com/api/admin/media",{
   method:"POST",headers:{"x-test-admin":"yes"},body:data})));
};
response=await submit(new File([png],"bottle.png",{type:"image/png"}));
assert.equal(response.status,201);
const data=await response.json();
assert.match(data.path,/^\/media\/product\/[a-f0-9]{32}\.png$/);
assert.equal(objects.size,1);
assert.equal(mediaAlts.size,1);
let listData=await onRequestGet(context(new Request("https://xuyibottles.com/api/admin/media?kind=product",{headers:{"x-test-admin":"yes"}})));
assert.equal((await listData.json()).items[0].altByLocale.es,"Botella deportiva de plástico modelo 2501");
const altEditRequest=new Request("https://xuyibottles.com/api/admin/media",{
 method:"POST",headers:{"x-test-admin":"yes","content-type":"application/json"},
 body:JSON.stringify({action:"save_alt",path:data.path,altByLocale:{en:"Reusable plastic bottle model 2501, product photo",es:"Botella deportiva modelo 2501"}})});
response=await onRequestPost(context(altEditRequest));
assert.equal(response.status,200);
assert.equal((await response.json()).altByLocale.en,"Reusable plastic bottle model 2501, product photo");
response=await submit(new File([Uint8Array.from(Array(240).fill(0))],"invalid.png",{type:"image/png"}));
assert.equal(response.status,400,"wrong image magic must be refused");
response=await submit(new File([png],"bottle.png",{type:"image/png"}),"unexpected");
assert.equal(response.status,400,"unapproved media group refused");
req=new Request("https://xuyibottles.com/api/admin/media?kind=product",{headers:{"x-test-admin":"yes"}});
response=await onRequestGet(context(req));
assert.equal((await response.json()).items.length,1);
const proxy=await import(base("functions/media/[kind]/[filename].js"));
const filename=data.path.split("/").pop();
response=await proxy.onRequestGet({params:{kind:"product",filename},env});
assert.equal(response.status,200,"existing R2 media proxy must deliver new assets");
assert.equal(response.headers.get("Content-Type"),"image/png");
response=await proxy.onRequestGet({params:{kind:"product",filename:"../secret.txt"},env});
assert.equal(response.status,404);
const used=await onRequestGet(context(new Request("https://xuyibottles.com/api/admin/media?kind=product",{headers:{"x-test-admin":"yes"}})));
assert.equal((await used.json()).usageObjects,1);
const deleteRequest=()=>context(new Request("https://xuyibottles.com/api/admin/media?kind=product&filename="+filename,{method:"DELETE",headers:{"x-test-admin":"yes"}}));
staticRefs[data.path]=["/ru/products/2501/"];
assert.equal((await onRequestDelete(deleteRequest())).status,409,"referenced static image must be protected");
let checked=await onRequestGet(context(new Request("https://xuyibottles.com/api/admin/media?kind=product&filename="+filename,{headers:{"x-test-admin":"yes"}})));
assert.equal((await checked.json()).usageStatus,"used");
delete staticRefs[data.path];
liveRefs.add(data.path);
assert.equal((await onRequestDelete(deleteRequest())).status,409,"referenced live D1 image must be protected");
liveRefs.delete(data.path);
const removed=await onRequestDelete(deleteRequest());
assert.equal(removed.status,200);
assert.equal(objects.size,0);
assert.equal(mediaAlts.size,0);
objects.set("catalog-staging/ppt/slide-059.webp",{body:png});
const archive=await onRequestGet(context(new Request("https://xuyibottles.com/api/admin/media?kind=ppt",{headers:{"x-test-admin":"yes"}})));
const archiveData=await archive.json();
assert.equal(archiveData.readOnly,true);
assert.equal(archiveData.items.length,1);
const archiveAltRequest=new Request("https://xuyibottles.com/api/admin/media",{
 method:"POST",headers:{"x-test-admin":"yes","content-type":"application/json"},
 body:JSON.stringify({action:"save_alt",path:"/media/ppt/slide-059.webp",
   altByLocale:{en:"Colorful plastic sports bottle assortment photographed for XUYI's catalog"}})});
response=await onRequestPost(context(archiveAltRequest));
assert.equal(response.status,200,"Protect legacy image bytes but allow editing its text description");
assert.equal((await response.json()).altByLocale.en,
 "Colorful plastic sports bottle assortment photographed for XUYI's catalog");
assert.equal(objects.get("catalog-staging/ppt/slide-059.webp").body,png,
 "Editing ALT must never modify the original R2 image");
assert.equal((await onRequestDelete(context(new Request("https://xuyibottles.com/api/admin/media?kind=ppt&filename=slide-059.webp",{method:"DELETE",headers:{"x-test-admin":"yes"}})))).status,403);
objects.delete("catalog-staging/ppt/slide-059.webp");
const savedAssets=env.ASSETS;delete env.ASSETS;
assert.equal((await onRequestDelete(deleteRequest())).status,503,"missing released reference index must fail closed");
env.ASSETS=savedAssets;
console.log("XUYI_R2_SHARED_MEDIA_REGRESSION_PASSED",14,"assertions, no remote writes");
