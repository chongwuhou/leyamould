import { authorizedBuildRequest, authorizedExplicitPublishRequest } from "../../_shared/build-auth.js";
import { ensureBlogSchema, normalizeBlogPost, listBlogPosts, findEditableBlogPost } from "../../_shared/blog-cms.js";
import {scheduleBlogPost,cancelBlogSchedule,ensurePublishScheduler} from "../../_shared/publish-scheduler.js";
import {MANAGED_MODELS} from "../../_shared/mould-routes.js";
import {canonicalProductSlug} from "../../_shared/product-seo.js";
const clean=x=>String(x??'').trim();
const reply=(x,status=200)=>Response.json(x,{status,headers:{"Cache-Control":"no-store","X-Robots-Tag":"noindex,nofollow"}});
// Blog editorial links use the LEYA public mould detail route.  The legacy
// water-cup /products/<sku>/ syntax is deliberately not accepted for new posts.
const productLinks=post=>[...new Set(post.sections.flatMap(section=>[
  ...String(section.paragraph||"").matchAll(/\]\(\/product\/([A-Za-z0-9_-]+)\.html\)/g)
].map(match=>String(match[1]).toLowerCase())))];
async function publishedProductSlugs(db){
 const known=new Set([...MANAGED_MODELS].map(model=>canonicalProductSlug(model).toLowerCase()));
 try{
  const rows=(await db.prepare("SELECT model,publication_status,content_json FROM xuyi_product_content WHERE publication_status='published'").all()).results||[];
  for(const row of rows){if(row.publication_status!=="published")continue;known.add(canonicalProductSlug(row.model).toLowerCase());try{const content=JSON.parse(row.content_json||"{}");if(content?.factoryModel)known.add(canonicalProductSlug(content.factoryModel).toLowerCase())}catch{}}
 }catch{}
 return known;
}
async function editorialError(db,post){
 const links=productLinks(post);
 if(links.length<2||links.length>5)return "正文必须包含 2–5 个不同的真实产品型号链接";
 const known=await publishedProductSlugs(db);
 const missing=links.filter(slug=>!known.has(slug));
 if(missing.length)return "产品内链必须指向已发布的 D1 产品："+missing.join(", ");
 if(!Array.isArray(post.related)||post.related.length<2||post.related.length>3)return "必须选择 2–3 篇相关阅读";
 const related=[...new Set(post.related)];
 if(related.length!==post.related.length)return "相关阅读不能重复";
 const relatedRows=(await db.prepare("SELECT slug FROM xuyi_blog_posts WHERE status='published' AND slug IN ("+related.map(()=>"?").join(",")+")").bind(...related).all()).results||[];
 if(new Set(relatedRows.map(row=>row.slug)).size!==related.length)return "相关阅读必须全部指向已发布文章";
 return "";
}
async function authorized(context){
 if(!clean(context.env.ADMIN_TOKEN))return reply({error:"ADMIN_TOKEN not configured"},503);
 if(!(await authorizedBuildRequest(context.request,context.env)))return reply({error:"Unauthorized"},401);
 if(!context.env.LEYA_DB)return reply({error:"LEYA_DB binding missing"},503);
 return null;
}
export async function onRequestGet(context){
 const denied=await authorized(context);if(denied)return denied;
 const url=new URL(context.request.url);
  if(url.searchParams.has("slug")){
   const slug=url.searchParams.get("slug");
   const post=await findEditableBlogPost(context.env.LEYA_DB,slug);
   if(!post)return reply({error:"Article not found"},404);
   await ensurePublishScheduler(context.env.LEYA_DB);
   const q=await context.env.LEYA_DB.prepare("SELECT scheduled_at,status FROM xuyi_blog_schedule WHERE slug=?").bind(slug).first();
   return reply({post:{...post,scheduled_at:q?.scheduled_at||"",schedule_status:q?.status||""}});
  }
  await ensureBlogSchema(context.env.LEYA_DB);const posts=await listBlogPosts(context.env.LEYA_DB);await ensurePublishScheduler(context.env.LEYA_DB);
  const queued=(await context.env.LEYA_DB.prepare("SELECT slug,scheduled_at,status FROM xuyi_blog_schedule").all()).results||[];
  const scheduleBySlug=new Map(queued.map(x=>[x.slug,x]));
  return reply({posts:posts.map(p=>{const q=scheduleBySlug.get(p.slug);return {slug:p.slug,title:p.title,status:p.status,has_draft:p.has_draft,group:p.group,updated_at:p.updated_at,published_at:p.published_at,cover:p.cover,scheduled_at:q?.scheduled_at||"",schedule_status:q?.status||""}}),count:posts.length});}
export async function onRequestPost(context){
 const denied=await authorized(context);if(denied)return denied;
 let payload;try{payload=await context.request.json()}catch{return reply({error:"Invalid JSON"},400)}
 const db=context.env.LEYA_DB;
 await ensureBlogSchema(db);
 const action=clean(payload.action);
 if(action==="publish"||action==="schedule"){
  if(!(await authorizedExplicitPublishRequest(context.request,context.env))){
   return reply({error:"Explicit owner publish authorization required"},428);
  }
 }
 if(action==="save"||action==="publish"){
  let post;try{post=normalizeBlogPost(payload.post)}catch(error){return reply({error:String(error.message||error)},400)}
  const exists=await db.prepare("SELECT status FROM xuyi_blog_posts WHERE slug=?").bind(post.slug).first();
  if(exists?.status==="retired"&&action==="publish")return reply({error:"Restore the retired post to draft first."},409);
  const status=action==="publish"?"published":"draft";
   if(status==="published"&&!post.sections.some(s=>s.paragraph.length>=120))return reply({error:"Cannot publish without substantive article content."},400);
   if(status==="published"){const editorial=await editorialError(db,post);if(editorial)return reply({error:editorial},400);}
  const content=JSON.stringify(post);
  if(content.length>100000)return reply({error:"Article content is too large"},413);
  if(action==="save"&&exists?.status==="published"){
   // Editing a live article must not unpublish the customer-facing version.
   await db.prepare("INSERT INTO xuyi_blog_drafts(slug,draft_json) VALUES(?,?) ON CONFLICT(slug) DO UPDATE SET draft_json=excluded.draft_json,updated_at=CURRENT_TIMESTAMP")
     .bind(post.slug,content).run();
   return reply({saved:true,status:"draft",slug:post.slug,liveUnchanged:true});
  }
  await db.prepare("INSERT INTO xuyi_blog_posts(slug,status,content_json,published_at) VALUES(?,?,?,?) ON CONFLICT(slug) DO UPDATE SET status=excluded.status,content_json=excluded.content_json,updated_at=CURRENT_TIMESTAMP,published_at=CASE WHEN excluded.status='published' THEN COALESCE(xuyi_blog_posts.published_at,excluded.published_at) ELSE xuyi_blog_posts.published_at END")
    .bind(post.slug,status,content,status==="published"?new Date().toISOString():null).run();
  if(action==="publish"){await db.prepare("DELETE FROM xuyi_blog_drafts WHERE slug=?").bind(post.slug).run();await cancelBlogSchedule(db,post.slug);}  return reply({saved:true,status,slug:post.slug,url:status==="published"?"/blog/"+post.slug+"/":null});
 }
  if(action==="schedule"){
   let post;try{post=normalizeBlogPost(payload.post)}catch(error){return reply({error:String(error.message||error)},400)}
   const existing=await db.prepare("SELECT status FROM xuyi_blog_posts WHERE slug=?").bind(post.slug).first();
   if(existing?.status==="published"||existing?.status==="retired")return reply({error:"只能给尚未发布的草稿安排自动发布时间"},409);
   if(!post.sections.some(s=>s.paragraph.length>=120))return reply({error:"文章正文不够完整，不能安排自动发布"},400);
    const editorial=await editorialError(db,post);if(editorial)return reply({error:editorial},400);
   const content=JSON.stringify(post);if(content.length>100000)return reply({error:"Article content is too large"},413);
   await db.prepare("INSERT INTO xuyi_blog_posts(slug,status,content_json,published_at) VALUES(?,'draft',?,NULL) ON CONFLICT(slug) DO UPDATE SET status='draft',content_json=excluded.content_json,updated_at=CURRENT_TIMESTAMP").bind(post.slug,content).run();
   const scheduled=await scheduleBlogPost(db,{slug:post.slug,scheduledAt:payload.scheduledAt,approved:payload.editorialApproved===true,contentJson:content});
   return reply({scheduled:true,status:"scheduled",...scheduled});
  }
  if(action==="cancel-schedule"){
   const slug=clean(payload.slug);if(!/^[a-z0-9-]{2,120}$/.test(slug))return reply({error:"Invalid slug"},400);
   return reply(await cancelBlogSchedule(db,slug));
  }
  if(action==="retire"){  const slug=clean(payload.slug);
  if(!/^[a-z0-9-]{2,120}$/.test(slug))return reply({error:"Invalid slug"},400);
  const result=await db.prepare("UPDATE xuyi_blog_posts SET status='retired',updated_at=CURRENT_TIMESTAMP WHERE slug=?").bind(slug).run();
  return reply({retired:Number(result.meta?.changes||0)===1,slug});
 }
 return reply({error:"Unknown action"},400);
}


