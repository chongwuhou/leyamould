import assert from "node:assert/strict";
import DEPTH from "../data/blog-depth-evidence-en.json" with {type:"json"};
import {renderDepthEvidence,blogHtml,composePage,normalizeBlogPost} from "../functions/_shared/blog-cms.js";
const item=DEPTH.articles["tritan-vs-pp-petg-pc"];
assert(item.sections.length===6);
const words=item.sections.map(s=>s.paragraph.split(" ").length).reduce((a,b)=>a+b,0);
assert(words>=850);
assert(renderDepthEvidence({slug:"tritan-vs-pp-petg-pc",intro:item.baselineIntro}).includes("source-reviewed-deep-dive"));
assert(!renderDepthEvidence({slug:"tritan-vs-pp-petg-pc",intro:"CMS edited version"}));
const person={name:"Mock Editorial Person",jobTitle:"Product Manager",url:"https://xuyibottles.com/about/",verified:true};
const raw={
 slug:"tritan-vs-pp-petg-pc",title:"Plastic bottle material sourcing guide",
 description:"An independent explanation of sourcing resin grades and components",
 intro:item.baselineIntro,cover:"/media/ppt/slide-030.webp",
 sections:[
 {heading:"First research checkpoint",paragraph:"A real product model needs individual component records for its bottle and lid assembly."},
 {heading:"Second research checkpoint",paragraph:"Final physical samples should be approved with identified materials before production."}
 ],faqs:[],checklist:[],related:[],authorPerson:person,depthEvidence:false
};
const saved=normalizeBlogPost(raw);
assert(saved.authorPerson?.name===person.name&&saved.depthEvidence===false);
const template='<html><head><title>Page</title></head><body><main id="main-content">Body</main></body></html>';
const full=composePage(template,blogHtml(saved),saved,"/blog/tritan-vs-pp-petg-pc/");
assert(full.includes("Mock Editorial Person"));
const parts=Array.from(full.matchAll(/application\/ld\+json">([\s\S]*?)<\/script>/g));
const graph=JSON.parse(parts[0][1]);
assert(graph.author["@type"]==="Person");
const org=composePage(template,blogHtml({...saved,authorPerson:{...person,verified:false}}),{...saved,authorPerson:{...person,verified:false}},"/blog/tritan-vs-pp-petg-pc/");
const fallback=JSON.parse(Array.from(org.matchAll(/application\/ld\+json">([\s\S]*?)<\/script>/g))[0][1]);
assert(fallback.author["@type"]==="Organization");
console.log("XUYI_DEPTH_SIX_SECTIONS_VALID");