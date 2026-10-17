import assert from "node:assert/strict";
import DATA from "../data/blog-buyer-decision-tables.json" with {type:"json"};
import {esc,blogHtml,renderBuyerDecisionTable,normalizeBlogPost,composePage} from "../functions/_shared/blog-cms.js";

const titles=new Set();
for(const [slug,row] of Object.entries(DATA.articles)){
 assert.equal(row.rows.length,4,slug);
 assert(!titles.has(row.title),"Decision tables need distinct buyer intent");
 titles.add(row.title);
 const module=renderBuyerDecisionTable({slug});
 assert(module.includes('id="buyer-decision-table"'),slug);
 assert(module.includes(esc(row.title)),slug);
 assert.equal(module.match(/<tr>/g)?.length,5,slug);
 assert(module.includes(row.links[0][1]),slug);
 assert.equal(renderBuyerDecisionTable({slug,buyerDecisionTable:false}),"","CMS opt-out must win");
 const edited={
   title:"Editor-authored review of a real procurement request",
   intro:"This tailored purchasing decision table belongs to the updated D1 CMS post.",
   head:["Decision","Risk","Mitigation"],
   rows:[
     ["Specific SKU","A selected cap can be different from a brochure photo","Obtain a signed sample"],
     ["Color proof","Colors can differ between screen and molded resin","Approve the physical reference"],
     ["Packing cost","Carton dimensions affect delivery economics","Measure the actual packed carton"],
     ["Inspection","The buyer needs a clear lot acceptance method","Agree the inspection procedure"]
   ],
   links:[["Model reference","/products/2095/"]]
 };
 const newMatrix=renderBuyerDecisionTable({slug,buyerDecisionTable:edited});
 assert(newMatrix.includes("Editor-authored review")&&!newMatrix.includes(row.title),
  "D1 editor must own their replacement instead of being reset to baseline");
 const fake={slug,title:"Wholesale buyers compare bottle models",description:"Practical buyer checks for the specified SKU.",
   intro:"An original, model-focused explanation edited by the D1 owner.",
   cover:"/media/ppt/slide-030.webp",sections:[{heading:"Unique CMS section",
    paragraph:"An owner-authored procurement detail describing the physical sample and its assembly."}],
   checklist:[],faqs:[{question:"Can I confirm my samples?",
    answer:"Yes, request the model-specific parts and inspection details."}]};
 const rendered=blogHtml(fake);
 assert(rendered.includes('id="buyer-decision-table"') && rendered.includes(fake.intro));
 assert(!blogHtml({...fake,buyerDecisionTable:false}).includes('id="buyer-decision-table"'));
}
const base={slug:"tritan-vs-pp-petg-pc",title:"Factory materials comparison reference",
 description:"A detailed sourcing comparison of plastic bottle components and market needs.",
 intro:"This D1 article contains original, owner-approved material selection information.",
 cover:"/media/ppt/slide-030.webp",sections:[{heading:"Actual model suitability",
 paragraph:"Supplier confirmations must be tied to the resin, lid, gasket and finished article."}],
 faqs:[{question:"Is this a certified factory product?",answer:"Only model-specific documents support certification claims."}]};
const custom={...base,buyerDecisionTable:false};
assert.equal(renderBuyerDecisionTable(custom),"");
const normalized=normalizeBlogPost({...base,sections:[...base.sections,{heading:"Secondary model check",paragraph:"A buyer must record an approved carton and a second physical sample before releasing a purchase order."}],checklist:[],related:[],buyerDecisionTable:false});
assert.equal(normalized.buyerDecisionTable,false,"CMS saves must retain editorial opt-out");
const template='<html><head><title>Existing Blog</title><link rel="canonical" href="https://xuyibottles.com/blog/"></head><body><main id="main-content">Old</main></body></html>';
const page=composePage(template,blogHtml(base),base,"/blog/tritan-vs-pp-petg-pc/");
const graphs=[...page.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)]
  .map(m=>JSON.parse(m[1]));
assert(graphs.some(x=>x["@type"]==="BlogPosting"));
const faq=graphs.find(x=>x["@type"]==="FAQPage");
assert.equal(faq.mainEntity.length,1);
assert.equal(faq.mainEntity[0].name,base.faqs[0].question);
assert.equal(faq.mainEntity[0].acceptedAnswer.text,base.faqs[0].answer);
console.log("XUYI_BLOG_BUYER_DECISIONS_RUNTIME_PASSED",Object.keys(DATA.articles).length,
 "CMS original/override/opt-out; actual FAQ text; no invented price/review");
