import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import {join} from "node:path";
import {onRequestGet} from "../functions/blog/[[path]].js";

const ROOT=process.cwd(),ORIGIN="https://xuyibottles.com";
function requestContext(slug,{index=false}={}){
 const post={
  slug,title:"Plastic Bottle Buying Guide: Verified Materials",
  description:"Know which food-contact material documents to request before ordering.",
  intro:"A practical wholesale buying guide with original content from the D1 CMS.",
  cover:"/media/ppt/slide-066.webp",updated:"2026-10-10",status:"published",
  sections:[{heading:"Check Each Component",paragraph:"Ask for exact model materials and approval evidence."}],
  checklist:[],faqs:[]
 };
 const db={prepare(sql){
  const query={bind(){return this;},async run(){return {success:true};},
    async first(){
      if(sql.includes("FROM xuyi_media_alt"))return {alt_json:JSON.stringify({
        en:"Plastic bottle material choices shown in a wholesale sourcing guide"})};
      return sql.includes("FROM xuyi_blog_posts")?{slug,status:"published",content_json:JSON.stringify(post)}:null;
    },
    async all(){return {results:[]};}};
  return query;
 }};
 const assets={async fetch(req){
  const path=new URL(req.url).pathname;
  let body;
  try{body=await readFile(join(ROOT,"dist",path.slice(1)),"utf8");}
  catch{return new Response("Not Found",{status:404});}
  // Test BOTH source publishing modes, independently of the live rollout flag.
  // Do not let a now-approved site's static shell mask the noindex regression.
  if(index)body=body.replace('<meta name="robots" content="noindex,nofollow">','<meta name="robots" content="index,follow">');
  else body=body.replace('<meta name="robots" content="index,follow">','<meta name="robots" content="noindex,nofollow">');
  return new Response(body,{status:200,headers:{"content-type":"text/html"}});
 }};
 return {request:new Request(ORIGIN+"/blog/"+slug+"/"),env:{XUYI_DB:db,ASSETS:assets},next:()=>{throw Error("Unexpected static fallback")}};
}
const route="plastic-bottle-material-selection";
const res=await onRequestGet(requestContext(route));
assert.equal(res.status,200);
assert.equal(res.headers.get("x-robots-tag"),"noindex,follow");
const html=await res.text();
const slugUrl=ORIGIN+"/blog/"+route+"/";
assert(html.includes('<link rel="canonical" href="'+slugUrl+'">'));
assert(html.includes('<link rel="alternate" hreflang="es" href="'+ORIGIN+'/es/blog/'+route+'/">'));
assert(html.includes('<link rel="alternate" hreflang="x-default" href="'+slugUrl+'">'));
assert(!html.includes('<link rel="alternate" hreflang="en" href="'+ORIGIN+'/blog/">'));
assert(html.includes('<meta property="og:title" content="Plastic Bottle Buying Guide: Verified Materials">'));
assert(html.includes("A practical wholesale buying guide with original content from the D1 CMS"));
assert(html.includes('alt="Plastic bottle material choices shown in a wholesale sourcing guide"'),
  "Dynamic D1 Blog must use edited R2 image ALT, not only the post headline");
const newer=await onRequestGet(requestContext("buyer-guide-only-in-d1"));
const newerHtml=await newer.text();
assert(newerHtml.includes('href="'+ORIGIN+'/blog/buyer-guide-only-in-d1/"'));
assert(!newerHtml.includes('rel="alternate" hreflang='),"Never invent translations for new D1 blog");
const approved=await onRequestGet(requestContext(route,{index:true}));
assert.equal(approved.headers.get("x-robots-tag"),"index,follow");
assert((await approved.text()).includes('content="index,follow"'));
console.log("XUYI_BLOG_LIVE_HREFLANG_ROBOTS_GATE_PASSED published, D1-only and launch-ready modes");