import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
const read=path=>readFileSync(new URL("../"+path,import.meta.url),"utf8");
const overflowData="data:text/javascript;base64,"+
  Buffer.from(read("functions/_shared/model-overflow.js")).toString("base64");
const rawRouter=read("functions/[[path]].js").replace(
  'import {serveModelOverflow} from "./_shared/model-overflow.js";',
  'import {serveModelOverflow} from "'+overflowData+'";'
);
const routerData="data:text/javascript;base64,"+Buffer.from(rawRouter).toString("base64");
const {onRequest}=await import(routerData);
for(const path of ["/build.py","/site_renderer.py","/data/products.json"]){
  for(const suffix of ["","?bust=123"]){
    const result=await onRequest({
      request:new Request("https://xuyibottles.com"+path+suffix),
      env:{},
      next:async()=>{throw Error("Legacy file must never reach Pages assets")}
    });
    assert.equal(result.status,410,path+suffix);
    assert.equal(result.headers.get("cache-control"),"no-store");
    assert.match(result.headers.get("x-robots-tag"),/noindex/);
    assert.equal(await result.text(),"Gone\n");
  }
}
let forwarded=0;
const other=await onRequest({
  request:new Request("https://xuyibottles.com/products/2501/"),
  env:{},
  next:async()=>{forwarded++;return new Response("OK",{status:200})}
});
assert.equal(other.status,200);
assert.equal(forwarded,1,"Unrelated public product routes must continue normally");
console.log("XUYI_LEGACY_PAGES_SOURCE_TOMBSTONES_PASSED 3 paths, query variants, normal routes");