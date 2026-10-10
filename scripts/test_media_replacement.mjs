import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";
const file=name=>new URL("../"+name,import.meta.url);
const uri=s=>"data:text/javascript;base64,"+Buffer.from(s).toString("base64");
const dims=await import(uri(readFileSync(file("functions/_shared/image-dimensions.js"),"utf8")));
const usage=readFileSync(file("functions/_shared/r2-usage.js"),"utf8");
const checked=readFileSync(file("functions/_shared/media-image.js"),"utf8");
let src=readFileSync(file("functions/api/admin/media-replace.js"),"utf8");
src=src.replace('import {authorizeAdminRequest} from "../../_shared/admin-security.js";',
  'const authorizeAdminRequest=async(request)=>request.headers.get("x-test-admin")==="yes";')
 .replace('import {checkedImage} from "../../_shared/media-image.js";',
  'import {checkedImage} from "'+uri(checked)+'";')
 .replace('import {KINDS,imageKey} from "../../_shared/r2-usage.js";',
  'import {KINDS,imageKey} from "'+uri(usage)+'";')
 .replace('import {imageDimensions,mimeOfName} from "../../_shared/image-dimensions.js";',
  'import {imageDimensions,mimeOfName} from "'+uri(readFileSync(file("functions/_shared/image-dimensions.js"),"utf8"))+'";');
const api=await import(uri(src));
function png(width,height){
 const x=Buffer.alloc(260,0);
 x.set([137,80,78,71,13,10,26,10],0);
 x.set(Buffer.from("IHDR"),12);
 x.writeUInt32BE(width,16);
 x.writeUInt32BE(height,20);
 return x;
}
const pngOld=png(420,420),pngNew=png(1500,1500);
assert.deepEqual(dims.imageDimensions(pngOld,"image/png"),{width:420,height:420});
const realWebp=readFileSync(file("assets/curated-hd/gradient-sports.webp"));
assert.deepEqual(dims.imageDimensions(realWebp,"image/webp"),{width:1500,height:1500});
let faults={backup:false};
const objects=new Map();
const digest=b=>createHash("sha1").update(b).digest("hex");
const store=(key,body)=>objects.set(key,{buffer:Buffer.from(body),etag:digest(Buffer.from(body)),uploaded:new Date()});
const filename="a".repeat(32)+".png";
const key="site-media/product/"+filename;
store(key,pngOld);
const bucket={
 get:async key=>objects.has(key)?{size:objects.get(key).buffer.length,etag:objects.get(key).etag,
   arrayBuffer:async()=>Uint8Array.from(objects.get(key).buffer).buffer}:null,
 head:async key=>objects.has(key)?{size:objects.get(key).buffer.length,etag:objects.get(key).etag}:null,
 put:async (key,body)=>{
  if(key.startsWith("site-image-versions/")&&faults.backup)throw Error("simulated backup failure");
  store(key,body);
 },
 list:async ({prefix})=>({objects:[...objects].filter(([k])=>k.startsWith(prefix))
  .map(([key,obj])=>({key,size:obj.buffer.length,uploaded:obj.uploaded})),truncated:false})
};
const env={ADMIN_TOKEN:"test-admin",XUYI_ASSETS:bucket};
const base="https://xuyibottles.com/api/admin/media-replace?kind=product&filename="+filename;
const url=(kind,name)=>"https://xuyibottles.com/api/admin/media-replace?kind="+kind+"&filename="+name;
const ctx=(request)=>({request,env});
const headers={"x-test-admin":"yes"};
async function put(image,etag,params={}){
 const form=new FormData();
 form.set("image",image);
 form.set("etag",etag);
 form.set("confirm",params.confirm??"same-subject");
 return api.onRequestPut(ctx(new Request(params.url||base,{method:"PUT",headers:params.headers||headers,body:form})));
}
const pngFile=b=>new File([b],"new-bottle.png",{type:"image/png"});
let response=await put(pngFile(pngNew),objects.get(key).etag,{headers:{}});
assert.equal(response.status,401,"Only admin can replace");
const before=objects.get(key).etag;
response=await put(pngFile(pngNew),"out-of-date");
assert.equal(response.status,409,"Reject stale R2 etags");
assert.equal(objects.get(key).etag,before);
response=await put(pngFile(png(300,300)),before);
assert.equal(response.status,409,"Reject lower-resolution replacements");
response=await put(pngFile(pngNew),before,{confirm:"no"});
assert.equal(response.status,400,"Require explicit confirmation");
faults.backup=true;
response=await put(pngFile(pngNew),before);
assert.equal(response.status,503,"Failed backup must block overwriting live path");
assert.equal(objects.get(key).etag,before,"Original must be unchanged");
faults.backup=false;
response=await put(pngFile(pngNew),before);
assert.equal(response.status,200,await response.text());
const updated=objects.get(key);
assert.equal(updated.etag,digest(pngNew),"Expected new pixels at SAME R2 key");
assert.equal((await api.onRequestGet(ctx(new Request(base)))).status,401);
response=await api.onRequestGet(ctx(new Request(base,{headers})));
assert.equal(response.status,200);
const history=await response.json();
assert.equal(history.versions.length,1,"Original must be retained as private backup");
const version=history.versions[0].version;
assert.match(version,/^\d{13}-[a-f0-9]{32}$/);
assert.ok(objects.has("site-image-versions/product/"+filename+"/"+version));
response=await api.onRequestPost(ctx(new Request(base,{headers,method:"POST",body:JSON.stringify({action:"restore",version,etag:updated.etag,confirm:"restore"})})));
assert.equal(response.status,200,await response.text());
assert.equal(objects.get(key).etag,before,"Restore must return to original pixels");
const after=await (await api.onRequestGet(ctx(new Request(base,{headers})))).json();
assert.equal(after.versions.length,2,"Restore should preserve prior new version too");
const oldVersion=after.versions[0].version;
assert.notEqual(oldVersion,version);
const webpKey="catalog-staging/ppt/slide-059.webp";
store(webpKey,realWebp);
const form=new FormData();
form.set("image",new File([realWebp],"approved-replacement.webp",{type:"image/webp"}));
form.set("etag",objects.get(webpKey).etag);
form.set("confirm","same-subject");
response=await api.onRequestPut(ctx(new Request(url("ppt","slide-059.webp"),{method:"PUT",headers,body:form})));
assert.equal(response.status,200,"Legacy R2 images are replaceable with an approved same-format file");
assert.equal((await api.onRequestPut(ctx(new Request(url("shared","invalid.png"),{method:"PUT",headers,body:form})))).status,400);
assert.equal((await api.onRequestPut(ctx(new Request(url("ppt","slide-059.webp"),{method:"PUT",headers,body:new FormData()})))).status,400);
console.log("XUYI_R2_REPLACE_AND_ROLLBACK_TESTS_PASSED",19,"assertions; mock R2 only");