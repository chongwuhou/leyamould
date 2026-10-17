import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import vm from "node:vm";

// Exercise the browser's actual request-wrapper, not a copy of its logic.
const source=readFileSync(new URL("../assets/admin-media.js",import.meta.url),"utf8")
  .replace("})();","globalThis.__testMediaApi=api;})();");
const requests=[];
const context={
 document:{getElementById:()=>null,querySelector:()=>null},
 sessionStorage:{getItem:key=>key==="xuyiAdminToken"?"test-admin-secret":""},
 fetch:async(path,options)=>{
   requests.push({path,options});
   return {ok:true,json:async()=>({saved:true})};
 }
};
vm.runInNewContext(source,context);
assert.equal(typeof context.__testMediaApi,"function");
await context.__testMediaApi("/api/admin/media");
await context.__testMediaApi("/api/admin/media",{
 method:"POST",body:JSON.stringify({action:"save_alt",path:"/media/product/example.webp"}),
 headers:{"content-type":"application/json"}
});
await context.__testMediaApi("/api/admin/media",{
 method:"POST",body:new FormData()
});
for(const req of requests){
 assert.equal(req.options.headers.authorization,"Bearer test-admin-secret",
   "The media request must preserve authentication on EVERY operation");
 assert.equal(req.options.cache,"no-store");
}
assert.equal(requests[1].options.headers["content-type"],"application/json");
assert.equal(requests[1].options.method,"POST");
assert.equal(requests[2].options.method,"POST");
console.log("XUYI_ADMIN_MEDIA_AUTH_HEADERS_PASSED GET, JSON ALT edit, multipart upload");
