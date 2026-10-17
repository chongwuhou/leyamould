import assert from "node:assert/strict";
import BLOGS from "../data/blog-guides.json" with {type:"json"};
import PART1 from "../data/blog-deep-research-part1.json" with {type:"json"};
import PART2 from "../data/blog-deep-research-part2.json" with {type:"json"};
import PART3 from "../data/blog-deep-research-part3.json" with {type:"json"};
import {esc,blogHtml,renderDepthEvidence,composePage,normalizeBlogPost} from "../functions/_shared/blog-cms.js";
const parts=[PART1,PART2,PART3];
const all={...PART1.articles,...PART2.articles,...PART3.articles};
assert.equal(Object.keys(all).length,15);
const template='<html><head><title>Buyer guide</title></head><body><main id="main-content">Original</main></body></html>';
let count=0;
for(const post of BLOGS){
 const html=blogHtml(post);
 assert.equal(html.match(/id="source-reviewed-deep-dive"/g)?.length,1,post.slug);
 const supplement=renderDepthEvidence(post);
 assert(supplement.length>2000,post.slug);
 if(all[post.slug]){
  count++;
  assert(supplement.includes("Research references from official authorities"),post.slug);
  assert(supplement.includes(esc(all[post.slug].title)),post.slug);
  assert.equal(supplement.match(/blog-deep-dive__section/g)?.length,6,post.slug);
  assert(!renderDepthEvidence({...post,intro:"A substantive CMS-edited introduction replaces the initial factory guide."}),post.slug);
  assert(!renderDepthEvidence({...post,depthEvidence:false}),post.slug);
  for(const source of all[post.slug].sources)assert(supplement.includes(source.url),[post.slug,source.url]);
 }
 const full=composePage(template,html,post,"/blog/"+post.slug+"/");
 const node=JSON.parse(full.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/)[1]);
 assert.equal(node["@type"],"BlogPosting");
 assert.equal(node.author["@type"],"Organization");
 assert.equal(node.dateModified,"2026-10-14",post.slug);
}
assert.equal(count,15);
const a=BLOGS.find(post=>post.slug==="custom-water-bottle-moq-pricing");
assert(a);
const custom={...a,intro:"This article was rewritten by the business owner and is now authoritative."};
assert(!blogHtml(custom).includes('id="source-reviewed-deep-dive"'));
assert(!blogHtml({...a,depthEvidence:false}).includes('id="source-reviewed-deep-dive"'));
const updated=normalizeBlogPost({...a,cover:"/media/ppt/"+a.cover,depthEvidence:false});
assert.equal(updated.depthEvidence,false);
console.log("XUYI_D1_RESEARCHED_16_BLOGS_EDITOR_OVERRIDES_PASSED",count);
