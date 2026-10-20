import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {validatePayload} from "../functions/api/admin/blog-batch-20261020.js";

// Test the actual JSON posted by the GitHub publishing step, not an unrelated
// idealized fixture. This catches API gate drift before any D1 mutation.
const payload=JSON.parse(readFileSync("_local_ops/blog-batch-20261020/payload.json","utf8"));
assert.doesNotThrow(()=>validatePayload(payload),"CMS must accept the reviewed batch");
const modified=edit=>{
  const copy=structuredClone(payload);
  edit(copy);
  assert.throws(()=>validatePayload(copy),"Tampered or unsafe batch must be rejected");
};
modified(p=>{p.posts[0].post.cover="/assets/blog/../outside.webp";});
modified(p=>{p.posts[0].post.sections=[];});
modified(p=>{p.translations[0].mainHtml="<script>alert(1)</script>";});
modified(p=>{p.translations[0].mainHtml=p.translations[0].mainHtml.replace('class="blog-editorial__product-link"','class="plain-link"');});
modified(p=>{p.indexCards[0].html=p.indexCards[0].html.replace('href="/blog/','href="//evil.example/');});
const cmsSource=readFileSync("functions/api/admin/blog-batch-20261020.js","utf8");
assert.match(cmsSource,/ON CONFLICT\(slug\) DO NOTHING/,"Existing editor post is authoritative");
assert.match(cmsSource,/ON CONFLICT\(resource_id,locale\) DO NOTHING/,"Existing editor translation is authoritative");
assert.match(cmsSource,/instr\(json_extract\(translated_json,'\$\.mainHtml'\),\?\)=0/,"Localized index append is idempotent");
console.log("XUYI_20261020_B2B_D1_PAYLOAD_RUNTIME_VALIDATION_PASSED");
