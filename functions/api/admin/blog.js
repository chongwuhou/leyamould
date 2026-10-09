import { authorizedBuildRequest } from "../../_shared/build-auth.js";
import { ensureBlogSchema, normalizeBlogPost, listBlogPosts, findBlogPost } from "../../_shared/blog-cms.js";
const clean=x=>String(x??'').trim();
const reply=(x,status=200)=>Response.json(x,{status,headers:{"Cache-Control":"no-store","X-Robots-Tag":"noindex,nofollow"}});
async function authorized(context){
 if(!clean(context.env.ADMIN_TOKEN))return reply({error:"ADMIN_TOKEN not configured"},503);
 if(!(await authorizedBuildRequest(context.request,context.env)))return reply({error:"Unauthorized"},401);
 if(!context.env.XUYI_DB)return reply({error:"XUYI_DB binding missing"},503);
 return null;
}
export async function onRequestGet(context){
 const denied=await authorized(context);if(denied)return denied;
 const url=new URL(context.request.url);
 if(url.searchParams.has("slug")){
  const slug=url.searchParams.get("slug");
  const post=await findBlogPost(context.env.XUYI_DB,slug);
  return post?reply({post}):reply({error:"Article not found"},404);
 }
 const posts=await listBlogPosts(context.env.XUYI_DB);
 return reply({posts:posts.map(p=>({slug:p.slug,title:p.title,status:p.status,group:p.group,updated_at:p.updated_at,published_at:p.published_at,cover:p.cover})),count:posts.length});
}
export async function onRequestPost(context){
 const denied=await authorized(context);if(denied)return denied;
 let payload;try{payload=await context.request.json()}catch{return reply({error:"Invalid JSON"},400)}
 const db=context.env.XUYI_DB;
 await ensureBlogSchema(db);
 const action=clean(payload.action);
 if(action==="save"||action==="publish"){
  let post;try{post=normalizeBlogPost(payload.post)}catch(error){return reply({error:String(error.message||error)},400)}
  const exists=await db.prepare("SELECT status FROM xuyi_blog_posts WHERE slug=?").bind(post.slug).first();
  if(exists?.status==="retired"&&action==="publish")return reply({error:"Restore the retired post to draft first."},409);
  const status=action==="publish"?"published":"draft";
  if(status==="published"&&!post.sections.some(s=>s.paragraph.length>=120))return reply({error:"Cannot publish without substantive article content."},400);
  const content=JSON.stringify(post);
  if(content.length>100000)return reply({error:"Article content is too large"},413);
  await db.prepare("INSERT INTO xuyi_blog_posts(slug,status,content_json,published_at) VALUES(?,?,?,?) ON CONFLICT(slug) DO UPDATE SET status=excluded.status,content_json=excluded.content_json,updated_at=CURRENT_TIMESTAMP,published_at=CASE WHEN excluded.status='published' THEN COALESCE(xuyi_blog_posts.published_at,excluded.published_at) ELSE xuyi_blog_posts.published_at END")
    .bind(post.slug,status,content,status==="published"?new Date().toISOString():null).run();
  return reply({saved:true,status,slug:post.slug,url:status==="published"?"/blog/"+post.slug+"/":null});
 }
 if(action==="retire"){
  const slug=clean(payload.slug);
  if(!/^[a-z0-9-]{2,120}$/.test(slug))return reply({error:"Invalid slug"},400);
  const result=await db.prepare("UPDATE xuyi_blog_posts SET status='retired',updated_at=CURRENT_TIMESTAMP WHERE slug=?").bind(slug).run();
  return reply({retired:Number(result.meta?.changes||0)===1,slug});
 }
 return reply({error:"Unknown action"},400);
}