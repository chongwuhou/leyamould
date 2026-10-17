// Guard the shared build credential against escalation into backend writes.
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
const raw=readFileSync(new URL("../functions/_shared/build-auth.js",import.meta.url),"utf8");
const imported=raw.replace('import { authorizeAdminRequest } from "./admin-security.js";',
  'const authorizeAdminRequest=async (request)=>request.headers.get("x-test-admin")==="allowed";');
assert.notEqual(imported,raw);
let cloudflareChecks=0;
globalThis.fetch=async()=>{cloudflareChecks++;return {ok:true,json:async()=>({
  success:true,result:{name:"xuyi-drinkware-site"}})}};
const {authorizedBuildRequest:allow}=await import("data:text/javascript;base64,"+Buffer.from(imported).toString("base64"));
const request=(path,method="GET",admin=false)=>new Request("https://xuyibottles.com"+path,
  {method,headers:{"authorization":"Bearer sample-ci-token","x-test-admin":admin?"allowed":"no"}});
for(const route of ["/api/build-snapshot","/api/publish-state",
  "/api/admin/brand-config","/api/admin/home-banners","/api/admin/site-config","/api/admin/pages",
  "/api/admin/product-content","/api/admin/page-content","/api/admin/page-translations"])
  assert.equal(await allow(request(route),{}),true,"CI GET should remain readable: "+route);
const before=cloudflareChecks;
for(const route of ["/api/admin/smtp","/api/admin/forms","/api/admin/blog",
  "/api/admin/translations","/api/admin/security","/api/admin/publish"])
  assert.equal(await allow(request(route),{}),false,"private/admin GET must not accept CI token: "+route);
for(const path of ["/api/admin/pages","/api/admin/product-content",
  "/api/admin/brand-config","/api/admin/home-banners","/api/admin/forms","/api/admin/smtp",
  "/api/admin/publish","/api/admin/page-translations"])
  assert.equal(await allow(request(path,"POST"),{}),false,"CI POST must never edit: "+path);
assert.equal(cloudflareChecks,before,"Deny unauthorized routes before calling Cloudflare API");
assert.equal(await allow(request("/api/admin/publish","POST",true),{}),true,
  "Authenticated admin must still be able to publish");
assert.equal(await allow(request("/api/admin/smtp","GET",true),{}),true,
  "Authenticated admin must still view sensitive settings");
console.log("XUYI_AUTHORIZATION_REGRESSION_PASSED",cloudflareChecks,"allowed CI read probes");
