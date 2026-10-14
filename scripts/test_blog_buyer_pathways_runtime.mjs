import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {blogHtml} from "../functions/_shared/blog-cms.js";
import mapping from "../data/blog-buyer-pathways.json" with {type:"json"};
import featurePaths from "../data/blog-feature-pathways.json" with {type:"json"};

assert.equal(Object.keys(mapping).length,9);
const section={heading:"Check the sample",paragraph:"Check components for the chosen plastic bottle before buying."};
for(const [slug,target] of Object.entries(mapping)){
 const post={slug,title:"XUYI plastic bottle buyer guidance",description:"Plastic bottle buying guide",intro:"Review the required bottle details.",sections:[section],faqs:[],checklist:[],related:[],cover:"/media/ppt/slide-030.webp"};
 const html=blogHtml(post);
 assert.equal(html.match(/class="seo-next-buyer"/g)?.length,1,slug);
 assert(html.includes('href="/'+target+'/"'),slug);
 assert(!html.includes('href="/undefined/"'),slug);
 const staticArticle=readFileSync(new URL("../dist/blog/"+slug+"/index.html",import.meta.url),"utf8");
 assert(staticArticle.includes('href="/'+target+'/"'),"Static/D1 links must agree: "+slug);
}
const unrelated=blogHtml({slug:"new-approved-article",title:"New article",description:"New article",intro:"New article",sections:[section],faqs:[],checklist:[]});
assert(!unrelated.includes('seo-next-buyer'),"Do not insert arbitrary backlinks into later D1 posts");
assert(!unrelated.includes('buyer-pathways'),"Unreviewed D1 posts should not get curated feature links");
assert.equal(Object.keys(featurePaths).length,6);
for(const [route,targets] of Object.entries(featurePaths)){
 const slug=route.replace(/^blog\//,"");
 const post={slug,title:"XUYI plastic bottle buyer guidance",description:"Plastic bottle buying guide",intro:"Review the required bottle details.",sections:[section],faqs:[],checklist:[],related:[],cover:"/media/ppt/slide-030.webp"};
 const dynamic=blogHtml(post);
 const staticArticle=readFileSync(new URL("../dist/blog/"+slug+"/index.html",import.meta.url),"utf8");
 assert.equal(dynamic.match(/class="section buyer-pathways"/g)?.length,1,slug);
 for(const target of targets){
  assert(dynamic.includes('href="/'+target+'/"'),"D1 reader link absent: "+route+" -> "+target);
  assert(staticArticle.includes('href="/'+target+'/"'),"Static reader link absent: "+route+" -> "+target);
 }
}
console.log("XUYI_RUNTIME_BLOG_CURATED_PATHWAYS_PASSED 9 buyer guide targets + 6 feature routes, static/D1 consistent");