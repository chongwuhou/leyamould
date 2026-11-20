import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
const raw=readFileSync(new URL("../functions/_shared/model-overflow.js",import.meta.url),"utf8");
const helper=await import("data:text/javascript;base64,"+Buffer.from(raw).toString("base64"));
const {modelKey,serveModelOverflow,overflowHealth}=helper;
assert.equal(modelKey("/products/2501/"),"models/2501.json");
assert.equal(modelKey("/es/products/2501/"),"models/2501.json");
assert.equal(modelKey("/ru/products/2501"),"models/2501.json");
assert.equal(modelKey("/blog/x/"),"");
assert.equal(modelKey("/es/products/../secrets/"),"");
const doc="<html lang='en'><body>R2 XUYI model</body></html>";
const bundle=JSON.stringify({site:"leyamould",schemaVersion:1,
 routes:{"/products/2501/":doc,"/es/products/2501/":"<html lang='es'>XUYI</html>"}});
const store={
 get:async key=>key==="models/2501.json"?{text:async()=>bundle,httpEtag:'"etag"'}:
 key==="__system/manifest.json"?{text:async()=>JSON.stringify({site:"leyamould",bucket:"leyamould-model-pages",mode:"hybrid",modelCount:1,localizedPageCount:1,objects:[{key:"models/2501.json"}]})}:null
};
const req=(url,nextStatus=404,env={XUYI_MODEL_PAGES:store})=>({
 request:new Request(url),env,next:async()=>new Response("Static Pages result",{status:nextStatus})});
let response=await serveModelOverflow(req("https://leyamould.com/products/2501/"));
assert.equal(response.status,200);assert.equal(response.headers.get("x-xuyi-page-storage"),"r2-overflow");
assert.match(await response.text(),/R2 XUYI model/);
response=await serveModelOverflow(req("https://leyamould.com/es/products/2501/"));
assert.equal(response.status,200);
response=await serveModelOverflow(req("https://leyamould.com/products/2501/",200));
assert.equal(await response.text(),"Static Pages result","Static HTML must take priority over R2");
response=await serveModelOverflow(req("https://leyamould.com/products/2502/"));
assert.equal(response.status,404);
response=await serveModelOverflow(req("https://leyamould.com/products/2501/",404,{}));
assert.equal(response.status,404,"Missing binding should not expose other data");
const health=await overflowHealth({XUYI_MODEL_PAGES:store});
assert.equal(health.ready,true);assert.equal(health.modelCount,1);
console.log("XUYI_R2_MODEL_OVERFLOW_HANDLER_TESTS_PASSED",13,"assertions");
