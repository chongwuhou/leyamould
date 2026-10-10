import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
const base=(file)=>new URL("../"+file,import.meta.url);
const uri=s=>"data:text/javascript;base64,"+Buffer.from(s).toString("base64");
const imageHelper=readFileSync(base("functions/_shared/media-image.js"),"utf8");
const raw=readFileSync(base("functions/api/admin/media.js"),"utf8")
 .replace('import {authorizeAdminRequest} from "../../_shared/admin-security.js";',
   'const authorizeAdminRequest=async(request)=>request.headers.get("x-test-admin")==="yes";')
 .replace('import {checkedImage} from "../../_shared/media-image.js";',
   'import { checkedImage } from "'+uri(imageHelper)+'";');
const {onRequestGet,onRequestPost,onRequestDelete}=await import(uri(raw));
const objects=new Map();
const storage={
 put:async(key,body,options)=>{objects.set(key,{body,options})},
 list:async({prefix})=>({objects:[...objects.keys()].filter(x=>x.startsWith(prefix)).map(key=>({key,size:objects.get(key).body.byteLength,uploaded:new Date("2026-10-09")})),truncated:false}),
 get:async(key)=>objects.has(key)?{body:objects.get(key).body}:null,
 head:async(key)=>objects.has(key)?{size:objects.get(key).body.byteLength}:null,
 delete:async(key)=>{objects.delete(key)}
};
const env={ADMIN_TOKEN:"a-test-admin",XUYI_ASSETS:storage};
const context=(request)=>({request,env});
let response=await onRequestGet(context(new Request("https://xuyibottles.com/api/admin/media")));
assert.equal(response.status,401,"media list must reject unauthenticated users");
let req=new Request("https://xuyibottles.com/api/admin/media?kind=product",{headers:{"x-test-admin":"yes"}});
response=await onRequestGet(context(req));assert.equal(response.status,200);
assert.deepEqual((await response.json()).items,[]);
const png=Uint8Array.from([137,80,78,71,...Array(240).fill(0)]);
const submit=async(file,kind="product")=>{
 const data=new FormData();data.append("kind",kind);data.append("image",file);
 return onRequestPost(context(new Request("https://xuyibottles.com/api/admin/media",{
   method:"POST",headers:{"x-test-admin":"yes"},body:data})));
};
response=await submit(new File([png],"bottle.png",{type:"image/png"}));
assert.equal(response.status,201);
const data=await response.json();
assert.match(data.path,/^\/media\/product\/[a-f0-9]{32}\.png$/);
assert.equal(objects.size,1);
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
const removed=await onRequestDelete(context(new Request("https://xuyibottles.com/api/admin/media?kind=product&filename="+filename,{method:"DELETE",headers:{"x-test-admin":"yes"}})));
assert.equal(removed.status,200);
assert.equal(objects.size,0);
console.log("XUYI_R2_SHARED_MEDIA_REGRESSION_PASSED",14,"assertions, no remote writes");