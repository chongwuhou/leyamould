import { authorizedReviewedBlogBatchRequest } from "../../_shared/build-auth.js";
import { ensureBlogSchema } from "../../_shared/blog-cms.js";
import { bumpPublishRevision } from "../../_shared/site-settings.js";

const SLUGS=[
 "trade-show-promotional-water-bottle-deadline-procurement",
 "supplement-brand-shaker-bottle-bundle-oem-sourcing",
 "outdoor-tour-operator-group-water-bottle-wholesale"
];
const LANGS=["es","pt","ru","tr"];
const DAY="2026-10-24",TAIL="</div></div></section>";
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
// One-time exact-model cover repair; accepts NO caller-chosen URL, slug or SQL.
// Checks original D1 values so CMS owner artwork stays authoritative.
const COVER_REPAIRS=[
 ["trade-show-promotional-water-bottle-deadline-procurement",
  "/assets/products/sports-alt.webp",
  "/assets/blog/water-bottle-sample-approval-20261017.webp"],
 ["supplement-brand-shaker-bottle-bundle-oem-sourcing",
  "/assets/products/shaker-alt.webp",
  "/assets/blog/replacement-water-bottle-lids-20261017.webp"],
 ["outdoor-tour-operator-group-water-bottle-wholesale",
  "/assets/products/jug-alt.webp",
  "/assets/blog/water-bottle-capacity-guide-20261017.webp"]
];
function reviewedIndexCover(source){
 const marker='<article class="news-card">';
 const parts=source.split(marker);
 for(const [slug,previous,approved] of COVER_REPAIRS){
  let countCards=0;
  for(let i=1;i<parts.length;i++){
   const sep=parts[i].indexOf("</article>");
   if(sep<0)throw Error("Unexpected unclosed blog card");
   let card=parts[i].slice(0,sep);
   if(!card.includes('href="/blog/'+slug+'/"'))continue;
   countCards++;
   const oldImg='src="'+previous+'"',newImg='src="'+approved+'"';
   if(card.includes(oldImg))card=card.replace(oldImg,newImg);
   else if(!card.includes(newImg))throw Error("Owner updated an index cover; manual review required");
   parts[i]=card+parts[i].slice(sep);
  }
  if(countCards!==1)throw Error("Expected one approved index card for "+slug);
 }
 return parts.join(marker);
}
async function repairReviewedCovers(db){
 try{
  await ensureBlogSchema(db);
  const posts=(await db.prepare("SELECT slug,status,content_json FROM xuyi_blog_posts WHERE slug IN (?,?,?)").bind(...SLUGS).all()).results||[];
  if(posts.length!==3||posts.some(p=>p.status!=="published"))throw Error("Reviewed posts missing from D1");
  const statements=[],slugsUpdated=[];
  for(const [slug,oldCover,newCover] of COVER_REPAIRS){
   const row=posts.find(x=>x.slug===slug);
   if(!row)throw Error("Unrecognized post");
   const body=JSON.parse(row.content_json);
   if(body.cover!==oldCover&&body.cover!==newCover)throw Error("Owner-edited Blog hero takes priority: "+slug);
   if(body.cover===oldCover){
    statements.push(db.prepare("UPDATE xuyi_blog_posts SET content_json=?,updated_at=CURRENT_TIMESTAMP WHERE slug=? AND content_json=?").bind(JSON.stringify({...body,cover:newCover}),slug,row.content_json));
    slugsUpdated.push(slug);
   }
  }
  const refs=["page:/blog/",...SLUGS.map(s=>"page:/blog/"+s+"/")];
  const pages=(await db.prepare("SELECT resource_id,locale,translated_json FROM xuyi_translation_overrides WHERE resource_id IN (?,?,?,?) AND locale IN (?,?,?,?)").bind(...refs,...LANGS).all()).results||[];
  if(pages.length!==16)throw Error("Incomplete reviewed Blog locales");
  let changedArticles=0,changedIndexes=0;
  for(const row of pages){
   const copy=JSON.parse(row.translated_json),oldBody=copy.mainHtml;
   if(typeof oldBody!=="string")throw Error("Invalid translated CMS content");
   let after=oldBody;
   if(row.resource_id==="page:/blog/"){
    after=reviewedIndexCover(oldBody);
    if(after!==oldBody)changedIndexes++;
   }else{
    const tuple=COVER_REPAIRS.find(v=>row.resource_id==="page:/blog/"+v[0]+"/");
    if(!tuple)throw Error("Unexpected Blog route");
    const [,oldCover,newCover]=tuple;
    const oldHero='<div class="blog-detail__cover"><img src="'+oldCover+'"';
    const newHero='<div class="blog-detail__cover"><img src="'+newCover+'"';
    if(after.includes(oldHero))after=after.replace(oldHero,newHero);
    else if(!after.includes(newHero))throw Error("Owner-edited localized hero takes priority");
    if(after!==oldBody)changedArticles++;
   }
   if(after!==oldBody)statements.push(db.prepare("UPDATE xuyi_translation_overrides SET translated_json=?,reviewed_at=? WHERE resource_id=? AND locale=? AND translated_json=?").bind(JSON.stringify({...copy,mainHtml:after}),DAY,row.resource_id,row.locale,row.translated_json));
  }
  if(statements.length===0)return response({success:true,alreadyFixed:true,updatedSlugs:[],translatedRows:0,indexRows:0});
  const results=await db.batch(statements);
  if(results.some(r=>Number(r?.meta?.changes||0)!==1))throw Error("Concurrent D1 CMS edits; no automatic overwrite");
  const revision=await bumpPublishRevision(db);
  return response({success:true,updatedSlugs:slugsUpdated,translatedRows:changedArticles,indexRows:changedIndexes,publishRevision:revision.revision});
 }catch(error){return response({error:"Reviewed cover repair refused: "+String(error?.message||"unknown").slice(0,200)},409);}
}

export async function onRequestPost(context){
 if(!(await authorizedReviewedBlogBatchRequest(context.request,context.env)))return response({error:"Unauthorized"},401);
 const db=context.env.XUYI_DB;
 if(!db)return response({error:"D1 binding unavailable"},503);
 let p;try{p=await context.request.json();}catch(e){return response({error:"Invalid JSON"},400);}
 if(p?.fixReviewedCovers===true && Object.keys(p).length===1)return repairReviewedCovers(db);
 try{validatePayload(p);}catch(e){return response({error:String(e.message||"Invalid payload").slice(0,240)},400);}
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
