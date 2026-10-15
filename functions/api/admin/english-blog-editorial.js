// Temporary, owner-authorized, one-time editorial migration of the EXISTING
// 16 English XUYI blog main_html records in D1. Never edits a static template.
// Remove this endpoint after successful D1 migration and production validation.
import { authorizedBuildRequest } from "../../_shared/build-auth.js";
import { bumpPublishRevision } from "../../_shared/site-settings.js";
import GUIDES from "../../../data/blog-guides.json" with { type:"json" };
import PART1 from "../../../data/blog-inline-edits-reviewed-part1.json" with { type:"json" };
import PART2 from "../../../data/blog-inline-edits-reviewed-part2.json" with { type:"json" };

const NOTES={...PART1,...PART2};
const SOURCES=Object.fromEntries(GUIDES.map(x=>[x.slug,x]));
const SLUGS=Object.keys(NOTES).sort();
const MIGRATION="xuyi_blog16_english_body_reviewed_20261015_v1";
const ROOT='<article class="article blog-editorial__body">';
const RELATED='<section class="section section--soft blog-related">';
const END='</article></div></div></section>';
const respond=(body,status=200)=>Response.json(body,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow"}});
async function authorize(c){
 if(!c.env.ADMIN_TOKEN||!c.env.XUYI_DB)return respond({error:"CMS D1 unavailable"},503);
 if(!(await authorizedBuildRequest(c.request,c.env)))return respond({error:"Unauthorized"},401);
 return null;
}
function reviewed(slug,html){
 const notes=NOTES[slug],source=SOURCES[slug];
 if(!source||!Array.isArray(notes)||notes.length!==2)return false;
 if(typeof html!=="string"||html.length<800||html.length>180000)return false;
 if(html.includes("<script")||/\bon[a-z]+\s*=|javascript:/i.test(html))return false;
 if(html.split(ROOT).length!==2||html.split(RELATED).length!==2||!html.includes(END))return false;
 const article=html.split(ROOT,2)[1].split(END,1)[0];
 if((article.match(/data-editorial-model="/g)||[]).length!==2)return false;
 if((article.match(/class="blog-related__item"/g)||[]).length!==3)return false;
 for(const note of notes){
  const sku=note.sku;
  if(!/^[a-z0-9-]+$/.test(sku))return false;
  if(!article.includes('data-editorial-model="'+sku+'"')||!article.includes('href="/products/'+sku+'/"'))return false;
 }
 return source.related.length===3&&source.related.every(x=>x!==slug&&article.includes('href="/blog/'+x+'/"'));
}
export async function onRequestGet(c){
 const denied=await authorize(c);if(denied)return denied;
 return respond({ready:true,scope:"16 source-reviewed English D1 blog bodies"});
}
export async function onRequestPost(c){
 const denied=await authorize(c);if(denied)return denied;
 let payload;try{payload=await c.request.json()}catch{return respond({error:"Invalid JSON"},400)}
 if(payload?.action!=="publish-reviewed-16-english-cms"||!Array.isArray(payload.articles)||
    payload.articles.length!==16||SLUGS.length!==16||SLUGS.some(x=>!SOURCES[x]))
  return respond({error:"Only exact 16 published English articles permitted"},400);
 const db=c.env.XUYI_DB;
 const state=await db.prepare("SELECT value FROM site_state WHERE key=?").bind(MIGRATION).first();
 if(state){
  if(state.value!=="applied")return respond({error:"Unrecognized migration marker"},409);
  return respond({alreadyApplied:true,updated:0});
 }
 const articles=new Map();
 for(const entry of payload.articles){
  if(!entry||typeof entry.slug!=="string"||!SLUGS.includes(entry.slug)||articles.has(entry.slug)||
     typeof entry.original!=="string"||typeof entry.updated!=="string"||!reviewed(entry.slug,entry.updated))
    return respond({error:"Unreviewed article payload; no changes applied"},400);
  articles.set(entry.slug,entry);
 }
 if(articles.size!==16)return respond({error:"Incomplete reviewed CMS set"},400);
 const rows=(await db.prepare("SELECT route,main_html,publication_status FROM xuyi_page_content WHERE route LIKE '/blog/%'").all()).results||[];
 const existing=new Map(rows.map(row=>[row.route,row]));
 const mutations=[];
 for(const slug of SLUGS){
  const route="/blog/"+slug+"/",current=existing.get(route),entry=articles.get(slug);
  if(!current||current.publication_status!=="published"||current.main_html!==entry.original)
   return respond({error:"CMS changed after review; nothing overwritten",slug},409);
  if(entry.original!==entry.updated)mutations.push({route,old:entry.original,value:entry.updated});
 }
 // Validate ALL 16 and CAS each owner-managed D1 row before recording completion.
 for(const row of mutations){
  const changed=await db.prepare(
   "UPDATE xuyi_page_content SET main_html=?,updated_at=CURRENT_TIMESTAMP WHERE route=? AND main_html=? AND publication_status='published'"
  ).bind(row.value,row.route,row.old).run();
  if(Number(changed.meta?.changes||0)!==1)return respond({error:"Concurrent owner edit; stop and investigate",route:row.route},409);
 }
 await db.prepare(
  "INSERT INTO site_state(key,value,updated_at) VALUES(?,?,CURRENT_TIMESTAMP) ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=CURRENT_TIMESTAMP"
 ).bind(MIGRATION,"applied").run();
 const revision=await bumpPublishRevision(db);
 return respond({saved:true,updated:mutations.length,revision:revision.revision});
}