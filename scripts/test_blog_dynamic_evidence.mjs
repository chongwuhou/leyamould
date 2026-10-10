import assert from "node:assert/strict";
import {blogHtml,composePage} from "../functions/_shared/blog-cms.js";
import EVIDENCE from "../data/editorial-evidence.json" with {type:"json"};

const template='<html lang="en"><head><title>Blog</title><meta name="description" content="Old"><link rel="canonical" href="https://xuyibottles.com/blog/"><meta property="og:url" content="https://xuyibottles.com/blog/"></head><body><main id="main-content">old static content</main></body></html>';
for(const [slug,evidence] of Object.entries(EVIDENCE)){
 const post={
  slug,title:"A Model-Specific Plastic Water Bottle Buyer Guide",
  description:"Check current requirements for a reusable plastic bottle order.",cover:"/media/ppt/slide-030.webp",
  intro:"This buyer guide links relevant primary rules to supplier sourcing decisions.",
  updated:"2026-10-09",sections:[{heading:"Define the SKU",paragraph:"Specify materials and destination market for this SKU."}],
  checklist:["Confirm the assembled bottle"],faqs:[],related:[]
 };
 const body=blogHtml(post);
 assert.equal(body.match(/id="primary-sources"/g)?.length,1,slug);
 assert(body.includes("SOURCE-CHECKED BUYER NOTES"),slug);
 assert(body.includes("Updated 2026-10-10"),slug);
 assert(body.includes("This buyer guide links relevant primary"),slug);
 for(const ref of evidence.sources)assert(body.includes(ref.url),slug+" "+ref.url);
 const page=composePage(template,body,post,"/blog/"+slug+"/");
 assert(page.includes('dateModified":"2026-10-10"'),slug);
 const data=JSON.parse(page.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/)?.[1]||"{}");
 assert.equal(data.citation?.length,evidence.sources.length,slug);
 assert.equal(data.mainEntityOfPage,"https://xuyibottles.com/blog/"+slug+"/");
}
const other=blogHtml({slug:"independent-buyer-guide",title:"Unrelated Blog",description:"Other content",cover:"/media/ppt/slide-030.webp",intro:"Original text",updated:"2026-10-08",sections:[],checklist:[],faqs:[]});
assert(!other.includes("id=\"primary-sources\""));
console.log("XUYI_DYNAMIC_BLOG_EVIDENCE_PASSED",Object.keys(EVIDENCE).length,"D1 articles; originals preserved; schema citations consistent");