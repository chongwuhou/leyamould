// Reviewed full-page HTML translations, stored in XUYI's existing translation
// override table. Translation drafts must be reviewed before publication.
import { authorizedBuildRequest } from "../../_shared/build-auth.js";
import { bumpPublishRevision,loadSiteSetting,defaultLanguageConfig,normalizeLanguageConfig } from "../../_shared/site-settings.js";
import { MANAGED_ROUTES } from "../../_shared/xuyi-routes.js";
import {ensureProductSeo,canonicalProductSlug} from "../../_shared/product-seo.js";
import {blogCard,esc,listBlogPosts,sortLocalizedBlogIndexByD1Order} from "../../_shared/blog-cms.js";
const respond=(body,status=200)=>Response.json(body,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
const clean=(v,n)=>String(v??"").trim().slice(0,n);
async function requireAdmin(c){
  if(!c.env.ADMIN_TOKEN)return respond({error:"Admin not configured"},503);
  if(!(await authorizedBuildRequest(c.request,c.env)))return respond({error:"Unauthorized"},401);
  if(!c.env.XUYI_DB)return respond({error:"XUYI_DB missing"},503);
  return null;
}
export async function onRequestGet(c){
  const denied=await requireAdmin(c);if(denied)return denied;
  const rows=(await c.env.XUYI_DB.prepare(
    "SELECT resource_id,locale,translated_json,reviewed_at FROM xuyi_translation_overrides WHERE resource_id LIKE 'page:%' ORDER BY locale,resource_id LIMIT 12000"
  ).all()).results||[];
  return respond({items:rows.map(x=>({route:x.resource_id.slice(5),locale:x.locale,
    content:JSON.parse(x.translated_json),reviewedAt:x.reviewed_at}))});
}
export async function onRequestPost(c){
  const denied=await requireAdmin(c);if(denied)return denied;
  let p;try{p=await c.request.json()}catch{return respond({error:"Invalid JSON"},400)}
  const route=clean(p.route,250),locale=clean(p.locale,12).toLowerCase();
  const title=clean(p.title,180),description=clean(p.description,450),html=clean(p.mainHtml,250000);
  if(!(route==="/"||/^\/(?:[a-z0-9_-]+\/)+$/.test(route)))
    return respond({error:"Invalid XUYI route"},400);
  const db=c.env.XUYI_DB;
  const languageRow=await loadSiteSetting(db,"language_config",defaultLanguageConfig());
  const languageConfig=normalizeLanguageConfig(languageRow.value);
  // Translation may be prepared while a language remains disabled/draft.
  // Publication is gated separately by publishReady and the build registry.
  if(locale===languageConfig.sourceLocale||
     !languageConfig.languages.some(lang=>lang.code===locale))
    return respond({error:"Locale must exist in the XUYI language registry and differ from the source language"},400);
  if(!title||!description||html.length<120||!/<(?:section|article|div|h1)\b/i.test(html))
    return respond({error:"Full translated title, description and main HTML required"},400);
  if(/<\s*(?:script|iframe|object|embed|form|style|link|base|meta|svg|math|template)\b|\bon[a-z-]+\s*=|\bsrcdoc\s*=|(?:javascript|vbscript|data)\s*:/i.test(html))
    return respond({error:"Unsafe HTML in translated content"},400);
  let blogMatch=null;
  if(!MANAGED_ROUTES.has(route)){
    // Blog detail routes are D1-owned and grow over time. Validate them from
    // the published Blog CMS rows instead of freezing the translation API to
    // the original checked-in route manifest.
    blogMatch=/^\/blog\/([a-z0-9][a-z0-9-]{1,119})\/$/.exec(route);
    if(blogMatch){
      let blogRow;
      try{blogRow=await db.prepare("SELECT status FROM xuyi_blog_posts WHERE slug=?")
        .bind(blogMatch[1]).first()}
      catch{return respond({error:"Unable to validate D1 Blog route"},503)}
      if(blogRow?.status!=="published")
        return respond({error:"Blog article must be published in English before translating"},409);
    }else{
      // Manual single-product pages enter D1 after the initial 135-page route
      // baseline. Only reviewed/published XUYI products are eligible for locales.
      const match=/^\/products\/([a-z0-9][a-z0-9-]{1,63})\/$/.exec(route);
      if(!match)return respond({error:"Unknown XUYI route"},400);
      let record;
      try{record=await db.prepare("SELECT content_json,publication_status FROM xuyi_product_content WHERE model=?")
        .bind(match[1]).first()}
      catch{return respond({error:"Unable to validate new-product route"},503)}
      let entry;try{entry=record&&JSON.parse(record.content_json)}catch{}
      if(record?.publication_status!=="published"||entry?.newProduct!==true)
        return respond({error:"New product must be published in English before translating"},409);
    }
  }
  const translatedJson=JSON.stringify({title,description,mainHtml:html});
  let indexStatement=null;
  const statements=[db.prepare(`INSERT INTO xuyi_translation_overrides(resource_id,locale,translated_json,reviewed_at)
     VALUES(?,?,?,CURRENT_TIMESTAMP)
     ON CONFLICT(resource_id,locale) DO UPDATE SET translated_json=excluded.translated_json,reviewed_at=CURRENT_TIMESTAMP`)
    .bind("page:"+route,locale,translatedJson)];
  if(blogMatch){
    let sourceRow;try{sourceRow=await db.prepare("SELECT content_json FROM xuyi_blog_posts WHERE slug=? AND status='published'").bind(blogMatch[1]).first()}catch{return respond({error:"Unable to read published D1 Blog source"},503)}
    let sourcePost;try{sourcePost=JSON.parse(sourceRow?.content_json||"")}catch{return respond({error:"Published D1 Blog source JSON is invalid"},409)}
    const indexRow=await db.prepare("SELECT translated_json FROM xuyi_translation_overrides WHERE resource_id='page:/blog/' AND locale=?").bind(locale).first();
    if(!indexRow?.translated_json)return respond({error:"The target language Blog index is not initialized"},409);
    let index;try{index=JSON.parse(indexRow.translated_json)}catch{return respond({error:"Target language Blog index JSON is invalid"},409)}
    const slug=blogMatch[1],localePrefixes=new Set(languageConfig.languages.map(lang=>lang.pathPrefix).filter(Boolean));
    const canonicalBlogPath=href=>{
      const parts=String(href||"").split("?")[0].split("/").filter(Boolean);
      if(parts.length===2&&parts[0]==="blog")return "/blog/"+parts[1]+"/";
      if(parts.length===3&&localePrefixes.has(parts[0])&&parts[1]==="blog")return "/blog/"+parts[2]+"/";
      return "";
    };
    const cardRe=/<article class="news-card">[\s\S]*?<\/article>/g;
    const current=String(index.mainHtml||""),cards=[...current.matchAll(cardRe)],matched=cards.filter(item=>[...item[0].matchAll(/href="([^"]+)"/g)].some(match=>canonicalBlogPath(match[1])==="/blog/"+slug+"/"));
    const d1Order=(await listBlogPosts(db,"published")).map(post=>post.slug);
    if(!d1Order.includes(slug))return respond({error:"Published D1 Blog order does not contain this article"},409);
    let ordered;try{ordered=sortLocalizedBlogIndexByD1Order(nextIndex,d1Order)}catch(error){return respond({error:"Target language Blog index failed D1 order validation: "+String(error.message||error)},409)}
    const nextIndexJson=JSON.stringify({...index,mainHtml:ordered});
    indexStatement=db.prepare("UPDATE xuyi_translation_overrides SET translated_json=?,reviewed_at=CURRENT_TIMESTAMP WHERE resource_id='page:/blog/' AND locale=? AND translated_json=?").bind(nextIndexJson,locale,indexRow.translated_json);
    statements.push(indexStatement);
  }
  if(route.startsWith("/products/")){
    await ensureProductSeo(db);
    const slug=canonicalProductSlug(route.split("/")[2].replace(/---$/,"透明款"));
    statements.push(db.prepare("INSERT INTO xuyi_product_seo(slug,locale,seo_title,meta_description,updated_at) VALUES(?,?,?,?,CURRENT_TIMESTAMP) "+
      "ON CONFLICT(slug,locale) DO UPDATE SET seo_title=excluded.seo_title,meta_description=excluded.meta_description,updated_at=CURRENT_TIMESTAMP")
      .bind(slug,locale,title,description));
  }
  const results=await db.batch(statements);
  if(indexStatement&&Number(results[results.length-1]?.meta?.changes||0)!==1)
    return respond({error:"Target language Blog index changed during save; no overwrite was applied"},409);
  const revision=await bumpPublishRevision(db);
  return respond({saved:true,reviewed:true,route,locale,...revision});
}
