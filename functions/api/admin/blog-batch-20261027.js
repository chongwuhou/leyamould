import { authorizedReviewedBlogBatchRequest } from "../../_shared/build-auth.js";
import { ensureBlogSchema } from "../../_shared/blog-cms.js";
import { bumpPublishRevision } from "../../_shared/site-settings.js";

const SLUGS=[
 "apartment-resident-welcome-kit-branded-water-bottles-bulk",
 "summer-camp-reusable-water-bottles-group-order",
 "nonprofit-fundraiser-custom-water-bottles-wholesale"
];
const LANGS=["es","pt","ru","tr"];
const DAY="2026-10-27",TAIL="</div></div></section>";
const response=(x,status=200)=>Response.json(x,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
const count=(s,t)=>String(s).split(t).length-1;
const blocked=/<\s*(?:script|iframe|object|embed|form|style|link|base|meta|svg|math|template)\b|\bon[a-z-]+\s*=|\bsrcdoc\s*=|(?:javascript|vbscript|data)\s*:/i;
export function validatePayload(p){
 if(!p||!Array.isArray(p.posts)||p.posts.length!==3||!Array.isArray(p.translations)||p.translations.length!==12||!Array.isArray(p.indexCards)||p.indexCards.length!==12)throw Error("Batch shape requires 3 posts and 12 translations/cards");
 const allowed=new Set(SLUGS),slugs=new Set(),translations=new Set(),cards=new Set();
 for(const item of p.posts){
  const slug=String(item?.slug||""),post=item?.post;
  if(!allowed.has(slug)||slugs.has(slug)||post?.slug!==slug)throw Error("Duplicate or unapproved article");
  if(post.updated!==DAY||typeof post.title!=="string"||post.title.length<12||typeof post.description!=="string"||post.description.length<25||typeof post.intro!=="string"||post.intro.length<150||!/^\/assets\/(?:blog|editorial|curated-hd|products)\/[a-z0-9-]+\.webp$/.test(String(post.cover||""))||!Array.isArray(post.sections)||post.sections.length!==7||post.sections.some(s=>String(s.paragraph||"").length<650)||!Array.isArray(post.checklist)||post.checklist.length!==10||!Array.isArray(post.faqs)||post.faqs.length!==4||!Array.isArray(post.related)||post.related.length!==3||!Array.isArray(post.product_notes)||post.product_notes.length!==3||JSON.stringify(post).length>100000)throw Error("Unapproved post structure: "+slug);
  slugs.add(slug);
 }
 for(const t of p.translations){
  const slug=String(t?.route||"").match(/^\/blog\/([a-z0-9-]+)\/$/)?.[1],locale=String(t?.locale||""),key=slug+"|"+locale,html=String(t?.mainHtml||"");
  if(!allowed.has(slug)||!LANGS.includes(locale)||translations.has(key)||String(t.title||"").length<12||String(t.description||"").length<25||html.length<5000||html.length>250000||blocked.test(html)||count(html,'class="blog-section"')!==7||count(html,'class="blog-editorial__product-link"')!==3||count(html,'class="blog-related__item"')!==3||count(html,'class="blog-buyer-matrix"')!==1||count(html,"<details>")!==4)throw Error("Unapproved localized body: "+key);
  translations.add(key);
 }
 for(const t of p.indexCards){
  const slug=String(t?.slug||""),loc=String(t?.locale||""),html=String(t?.html||""),key=slug+"|"+loc;
  if(!allowed.has(slug)||!LANGS.includes(loc)||cards.has(key)||html.length<100||html.length>10000||blocked.test(html)||!html.startsWith('<article class="news-card">')||!html.endsWith("</article>")||count(html,'href="/blog/'+slug+'/"')!==3)throw Error("Unapproved index card: "+key);
  cards.add(key);
 }
 for(const slug of SLUGS)for(const lang of LANGS){const key=slug+"|"+lang;if(!translations.has(key)||!cards.has(key))throw Error("Incomplete locale set");}
}
export async function onRequestPost(context){
 if(!(await authorizedReviewedBlogBatchRequest(context.request,context.env)))return response({error:"Unauthorized"},401);
 const db=context.env.XUYI_DB;
 if(!db)return response({error:"D1 binding unavailable"},503);
 let p;try{p=await context.request.json();validatePayload(p);}catch(e){return response({error:String(e.message||"Invalid payload").slice(0,240)},400);}
 try{
  await ensureBlogSchema(db);
  const stmts=[];
  for(const item of p.posts)stmts.push(db.prepare("INSERT INTO xuyi_blog_posts (slug,status,content_json,published_at,updated_at) VALUES(?,'published',?,?,CURRENT_TIMESTAMP) ON CONFLICT(slug) DO NOTHING").bind(item.slug,JSON.stringify(item.post),DAY+"T00:00:00Z"));
  for(const t of p.translations)stmts.push(db.prepare("INSERT INTO xuyi_translation_overrides (resource_id,locale,translated_json,reviewed_at) VALUES(?,?,?,?) ON CONFLICT(resource_id,locale) DO NOTHING").bind("page:"+t.route,t.locale,JSON.stringify({title:t.title,description:t.description,mainHtml:t.mainHtml}),DAY));
  for(const c of p.indexCards)stmts.push(db.prepare("UPDATE xuyi_translation_overrides SET translated_json=json_set(translated_json,'$.mainHtml',substr(json_extract(translated_json,'$.mainHtml'),1,length(json_extract(translated_json,'$.mainHtml'))-length(?))||?||?),reviewed_at=? WHERE resource_id='page:/blog/' AND locale=? AND substr(json_extract(translated_json,'$.mainHtml'),-length(?))=? AND instr(json_extract(translated_json,'$.mainHtml'),?)=0").bind(TAIL,c.html,TAIL,DAY,c.locale,TAIL,TAIL,"/blog/"+c.slug+"/"));
  const done=await db.batch(stmts);
  const changes=(a,b)=>done.slice(a,b).reduce((total,x)=>total+Number(x?.meta?.changes||0),0);
  const postsInserted=changes(0,3),translationsInserted=changes(3,15),indexCardsAdded=changes(15,27);
  const saved=(await db.prepare("SELECT slug,status FROM xuyi_blog_posts WHERE slug IN (?,?,?)").bind(...SLUGS).all()).results||[];
  if(saved.filter(x=>x.status==="published"&&SLUGS.includes(x.slug)).length!==3)return response({error:"Article verification failed"},409);
  const refs=["page:/blog/",...SLUGS.map(s=>"page:/blog/"+s+"/")];
  const rows=(await db.prepare("SELECT resource_id,locale,translated_json FROM xuyi_translation_overrides WHERE resource_id IN (?,?,?,?) AND locale IN (?,?,?,?)").bind(...refs,...LANGS).all()).results||[];
  const lookup=new Map(rows.map(x=>[x.resource_id+"|"+x.locale,JSON.parse(x.translated_json).mainHtml||""]));
  for(const lang of LANGS){
   const index=lookup.get("page:/blog/|"+lang)||"";
   for(const slug of SLUGS){
    const body=lookup.get("page:/blog/"+slug+"/|"+lang)||"";
    if(body.length<5000||count(body,'class="blog-section"')!==7||count(body,'class="blog-editorial__product-link"')!==3||count(body,'class="blog-related__item"')!==3||count(body,'class="blog-buyer-matrix"')!==1||count(body,"<details>")!==4)return response({error:"Incomplete persisted translation"},409);
    const matched=index.split('<article class="news-card">').slice(1).map(x=>x.split("</article>",1)[0]).filter(x=>x.includes('href="/blog/'+slug+'/"'));
    if(matched.length!==1||count(matched[0],'href="/blog/'+slug+'/"')!==3)return response({error:"Incomplete persisted index"},409);
   }
  }
  const revision=await bumpPublishRevision(db);
  return response({success:true,postsInserted,translationsInserted,indexCardsAdded,publishRevision:revision.revision,publishedSlugs:SLUGS});
 }catch(e){return response({error:"D1 batch failed: "+String(e.message||"unknown").slice(0,160)},500);}
}