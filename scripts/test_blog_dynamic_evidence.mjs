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
 assert(body.includes("Published 2026-10-09")&&body.includes("Reviewed 2026-10-10"),slug);
 assert(body.includes("This buyer guide links relevant primary"),slug);
 assert(body.includes('class="blog-author-byline"')&&body.includes('rel="author" href="/about/"'),slug);
 for(const ref of evidence.sources)assert(body.includes(ref.url),slug+" "+ref.url);
 const page=composePage(template,body,post,"/blog/"+slug+"/");
 assert(page.includes('dateModified":"2026-10-10"'),slug);
 const data=JSON.parse(page.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/)?.[1]||"{}");
 assert.equal(data.citation?.length,evidence.sources.length,slug);
 assert.equal(data.mainEntityOfPage,"https://xuyibottles.com/blog/"+slug+"/");
 assert.equal(data.author?.name,"XUYI Bottles",slug);
 assert.equal(data.author?.url,"https://xuyibottles.com/about/",slug);
}
const other=blogHtml({slug:"independent-buyer-guide",title:"Unrelated Blog",description:"Other content",cover:"/media/ppt/slide-030.webp",intro:"Original text",updated:"2026-10-08",sections:[],checklist:[],faqs:[]});
assert(!other.includes("id=\"primary-sources\""));

const ownerChangedPost={
 slug:"owner-changed-cover",title:"Independent factory buying guide",description:"Buyer references",
 cover:"/media/ppt/slide-030.webp",updated:"2026-10-09",
 intro:"Original D1 editorial intro",sections:[],checklist:[],faqs:[]
};
const staticCoverShell=template.replace("</head>",'<meta property="og:image" content="https://xuyibottles.com/assets/blog/static-cover.webp"><meta property="og:image:width" content="960"><meta property="og:image:height" content="720"></head>');
const switched=composePage(staticCoverShell,blogHtml(ownerChangedPost),ownerChangedPost,"/blog/owner-changed-cover/");
assert(!switched.includes('property="og:image:width"')&&!switched.includes('property="og:image:height"'),
 "D1-edited cover must not retain misleading dimensions from the old static shell");
assert(switched.includes('property="og:image" content="https://xuyibottles.com/media/ppt/slide-030.webp"'));
console.log("XUYI_DYNAMIC_BLOG_EVIDENCE_PASSED",Object.keys(EVIDENCE).length,"D1 articles; originals preserved; schema citations consistent");
