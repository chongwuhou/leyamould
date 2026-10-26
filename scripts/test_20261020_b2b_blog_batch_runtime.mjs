import assert from "node:assert/strict";
import {existsSync,readFileSync} from "node:fs";
import {validatePayload} from "../functions/api/admin/blog-batch-20261020.js";

// The real release payload is generated in the credentialed push workflow and
// intentionally lives under ignored _local_ops/. Scheduled builds must not
// assume that ephemeral, private file exists in a clean checkout.
const payloadPath="_local_ops/blog-batch-20261020/payload.json";
if (existsSync(payloadPath)) {
  const payload=JSON.parse(readFileSync(payloadPath,"utf8"));
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
  console.log("XUYI_20261020_B2B_D1_ACTUAL_RELEASE_PAYLOAD_VALIDATION_PASSED");
} else {
  // On scheduled builds, still exercise the API's fail-closed shape check.
  // The actual reviewed payload is fully validated when the push workflow
  // generates it before publication.
  assert.throws(()=>validatePayload({}),/reviewed batch must contain 3 posts/i);
  console.log("XUYI_20261020_B2B_D1_RELEASE_PAYLOAD_ABSENT_EXPECTED_ON_CLEAN_SCHEDULED_CHECKOUT");
}

const cmsSource=readFileSync("functions/api/admin/blog-batch-20261020.js","utf8");
assert.match(cmsSource,/ON CONFLICT\\(slug\\) DO NOTHING/,"Existing editor post is authoritative");
assert.match(cmsSource,/ON CONFLICT\\(resource_id,locale\\) DO NOTHING/,"Existing editor translation is authoritative");
assert.match(cmsSource,/instr\\(json_extract\\(translated_json,'\\$\\.mainHtml'\\),\\?\\)=0/,"Localized index append is idempotent");
console.log("XUYI_20261020_B2B_CMS_RUNTIME_GUARDS_PASSED");
