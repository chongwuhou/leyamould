import assert from "node:assert/strict";
import GUIDES from "../data/blog-guides.json" with {type:"json"};
import {blogHtml} from "../functions/_shared/blog-cms.js";
const slugs=["water-bottle-sample-approval-checklist","water-bottle-capacity-sizes-wholesale","replacement-water-bottle-lids-bulk"];
for(const slug of slugs){
 const post=GUIDES.find(p=>p.slug===slug);
 assert(post);
 const normal=blogHtml(post);
 assert.equal((normal.match(/class="blog-editorial__product-link"/g)||[]).length,3);
 assert.equal((normal.match(/class="blog-related__item"/g)||[]).length,3);
 for(const note of post.product_notes)assert(normal.includes('/products/'+note.sku+'/'));
 // Real CMS edit simulation: remove note mapping, revise body, disable
 // curated related reading. No old source-derived annotation may return.
 const edited={...post,product_notes:false,relatedReading:false,
   sections:post.sections.map((s,i)=>i===0?{...s,paragraph:"EDITOR APPROVED REPLACEMENT TEXT"}:s)};
 const after=blogHtml(edited);
 assert(after.includes("EDITOR APPROVED REPLACEMENT TEXT"));
 assert(!after.includes('class="blog-editorial__product-link"'));
 assert(!after.includes('class="blog-related__item"'));
}
console.log("XUYI_20261017_BLOG_D1_OWNER_EDITS_PRESERVED");
