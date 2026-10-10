import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
const read=path=>readFileSync(new URL("../"+path,import.meta.url),"utf8");
const uri=s=>"data:text/javascript;base64,"+Buffer.from(s).toString("base64");
const helper=read("functions/_shared/home-banners.js");
const mod=await import(uri(helper));
const config=JSON.parse(read("assets/home-banner-defaults.json"));
assert.equal(mod.normalizeBanners(config).slides.length,3);
assert.equal(mod.safeBannerLink("/products/"),true);
assert.equal(mod.safeBannerLink("https://example.com/offer?ref=abc"),true);
assert.equal(mod.safeBannerLink("javascript:alert(1)"),false);
assert.equal(mod.safeBannerLink("//example.com"),false);
assert.equal(mod.safeBannerPath("/assets/curated-hd/gradient-sports.webp"),true);
assert.equal(mod.safeBannerPath("/media/product/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.webp"),true);
assert.equal(mod.safeBannerPath("/../../admin/"),false);
assert.throws(()=>mod.normalizeBanners({...config,slides:[...config.slides.slice(0,2),{...config.slides[2],link:"javascript:alert(1)"}]}));
assert.throws(()=>mod.normalizeBanners({...config,slides:[...config.slides.slice(0,2),{...config.slides[2],title:"<img onerror=alert(1)>"}]}));
assert.throws(()=>mod.normalizeBanners({...config,slides:config.slides.slice(0,2)}));
assert.throws(()=>mod.normalizeBanners({...config,slides:[...config.slides.slice(0,2),{...config.slides[2],translations:{}}]}));
let authorized=false,revision=9,stored=null,mediaPresent=false;
const db={
 prepare(sql){
  return {
   bind(...args){return {run:async()=>{
    if(sql.includes("home_banner_config"))stored=String(args[0]);
    return {success:true};
   }}},
   first:async()=>stored?{value:stored,updated_at:"2026-10-10"}:null
  };
 }
};
const apiSource=read("functions/api/admin/home-banners.js")
 .replace('import {authorizedBuildRequest} from "../../_shared/build-auth.js";','const authorizedBuildRequest=async()=>true;')
 .replace('import {authorizeAdminRequest} from "../../_shared/admin-security.js";','const authorizeAdminRequest=async()=>globalThis.__adminAllowed.value;')
 .replace('import {bumpPublishRevision} from "../../_shared/site-settings.js";','const bumpPublishRevision=async()=>({revision:++globalThis.__rev.value});')
 .replace('import {normalizeBanners} from "../../_shared/home-banners.js";','import {normalizeBanners} from "'+uri(helper)+'";');
globalThis.__adminAllowed={value:false};
globalThis.__rev={value:revision};
const api=await import(uri(apiSource));
const env={ADMIN_TOKEN:"example",XUYI_DB:db,XUYI_ASSETS:{head:async()=>mediaPresent?{size:1000}:null},ASSETS:{fetch:async()=>new Response("",{status:200})}};
const request=(payload)=>({request:new Request("https://xuyibottles.com/api/admin/home-banners",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({config:payload})}),env});
assert.equal((await api.onRequestPost(request(config))).status,401,"CI cannot publish home banners");
globalThis.__adminAllowed.value=true;
assert.equal((await api.onRequestPost(request(config))).status,200,"Approved default configuration can save");
const saved=await (await api.onRequestGet({request:new Request("https://xuyibottles.com/api/admin/home-banners"),env})).json();
assert.equal(saved.config.slides.length,3);
assert.equal(saved.config.slides[0].link,"/products/");
const changed=structuredClone(config);
changed.slides[0].img="/media/product/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.webp";
assert.equal((await api.onRequestPost(request(changed))).status,409,"Missing R2 image rejects saving");
mediaPresent=true;
assert.equal((await api.onRequestPost(request(changed))).status,200,"Existing R2 image accepted");
assert.equal(globalThis.__rev.value,11);
console.log("XUYI_HOME_BANNERS_API_TESTS_PASSED",18,"assertions, mock D1/R2 only");