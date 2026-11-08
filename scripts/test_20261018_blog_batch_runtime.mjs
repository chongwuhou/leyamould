import assert from "node:assert/strict";
import GUIDES from "../data/blog-guides.json" with {type:"json"};
import EVIDENCE from "../data/editorial-evidence.json" with {type:"json"};
import {blogHtml,composePage} from "../functions/_shared/blog-cms.js";
const slugs=[
 "plastic-water-bottle-food-contact-compliance-checklist",
 "custom-water-bottle-mold-cost-lead-time",
 "custom-water-bottle-color-matching-pantone-guide"
];
const shell='<html><head><title>old</title><meta name="description" content="old"><link rel="canonical" href="https://xuyibottles.com/blog/"><meta property="og:url" content="old"></head><body><main id="main-content"></main></body></html>';
for(const slug of slugs){
 const post=GUIDES.find(p=>p.slug===slug);
 assert(post,slug);
 const body=blogHtml(post);
 assert.equal((body.match(/class="blog-editorial__product-link"/g)||[]).length,3,slug);
 assert.equal((body.match(/class="blog-related__item"/g)||[]).length,3,slug);
 assert.equal((body.match(/class="blog-buyer-matrix"/g)||[]).length,1,slug);
 assert.equal((body.match(/<details>/g)||[]).length,4,slug);
 assert.equal((body.match(/id="primary-sources"/g)||[]).length,1,slug);
 for(const note of post.product_notes)assert(body.includes('/products/'+note.sku+'/'),slug+': '+note.sku);
 for(const ref of EVIDENCE[slug].sources)assert(body.includes(ref.url),slug+': '+ref.url);
 const full=composePage(shell,body,post,'/blog/'+slug+'/');
 assert(full.includes('<title>'+post.title+'</title>'),slug+' title');
 assert(full.includes('dateModified":"2026-10-18'),slug+' schema date');
 assert(full.includes('https://xuyibottles.com'+post.cover),slug+' social image');
 for(const ref of EVIDENCE[slug].sources)assert(full.includes('"url":"'+ref.url+'"'),slug+' schema citation '+ref.url);
 const edited={...post,intro:'OWNER-APPROVED CONTENT MUST REMAIN AUTHORITATIVE',product_notes:false,relatedReading:false,
   sections:post.sections.map((s,i)=>i===0?{...s,paragraph:'OWNER-APPROVED PARAGRAPH, DO NOT REPLACE'}:s)};
 const after=blogHtml(edited);
 assert(after.includes('OWNER-APPROVED CONTENT MUST REMAIN AUTHORITATIVE'),slug+' intro');
 assert(after.includes('OWNER-APPROVED PARAGRAPH, DO NOT REPLACE'),slug+' paragraph');
 assert.equal((after.match(/class="blog-editorial__product-link"/g)||[]).length,0,slug+' owner product notes');
 assert.equal((after.match(/class="blog-related__item"/g)||[]).length,0,slug+' owner related-reading flag');
}
console.log("XUYI_20261018_D1_BLOG_EVIDENCE_SCHEMA_AND_OWNER_EDIT_POLICY_PASSED");
