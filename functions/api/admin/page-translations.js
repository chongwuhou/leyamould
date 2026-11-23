// Reviewed full-page HTML translations, stored in LEYA MOULD's translation
// override table. Translation drafts must be reviewed before publication.
import { authorizedBuildRequest } from "../../_shared/build-auth.js";
import { bumpPublishRevision,loadSiteSetting,defaultLanguageConfig,normalizeLanguageConfig } from "../../_shared/site-settings.js";
import { MANAGED_ROUTES, mouldModelFromRoute } from "../../_shared/xuyi-routes.js";
import {ensureProductSeo,canonicalProductSlug} from "../../_shared/product-seo.js";
import {blogCard,esc,listBlogPosts,sortLocalizedBlogIndexByD1Order} from "../../_shared/blog-cms.js";
const respond=(body,status=200)=>Response.json(body,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
const clean=(v,n)=>String(v??"").trim().slice(0,n);
async function requireAdmin(c){
  if(!c.env.ADMIN_TOKEN)return respond({error:"Admin not configured"},503);
  if(!(await authorizedBuildRequest(c.request,c.env)))return respond({error:"Unauthorized"},401);
  if(!c.env.LEYA_DB)return respond({error:"LEYA_DB missing"},503);
  return null;
}
async function configuredRoutes(db){
  try{return ((await db.prepare("SELECT route FROM site_pages ORDER BY route LIMIT 500").all()).results||[])
    .map(row=>String(row.route||"")).filter(Boolean)}catch{return []}
}

async function saveBlogTranslationBatch(c,items){
  if(!Array.isArray(items)||!items.length||items.length>250)return respond({error:"Bulk translation batch must contain 1-250 items"},400);
  const db=c.env.LEYA_DB;
  const languageRow=await loadSiteSetting(db,"language_config",defaultLanguageConfig());
  const languageConfig=normalizeLanguageConfig(languageRow.value);
  const allowedLocales=new Set(languageConfig.languages.filter(lang=>lang.code!==languageConfig.sourceLocale).map(lang=>lang.code));
  let publishedRows;
  try{publishedRows=(await db.prepare("SELECT slug FROM xuyi_blog_posts WHERE status='published' LIMIT 5000").all()).results||[]}
  catch{return respond({error:"Unable to read published D1 Blog source"},503)}
  const published=new Set(publishedRows.map(row=>String(row.slug||"")));
  const seen=new Set(),statements=[];
  for(const item of items){
    const route=clean(item?.route,250),locale=clean(item?.locale,12).toLowerCase();
    const title=clean(item?.title,180),description=clean(item?.description,450),html=clean(item?.mainHtml,250000);
    const blogMatch=/^\/blog\/([a-z0-9][a-z0-9-]{1,119})\/$/.exec(route);
    if(!blogMatch||!allowedLocales.has(locale))return respond({error:"Bulk item must target a published Blog detail route and configured non-source locale",route,locale},400);
    const key=locale+"|"+route;
    if(seen.has(key))return respond({error:"Duplicate bulk translation item",route,locale},400);
    seen.add(key);
    if(!published.has(blogMatch[1]))return respond({error:"Blog article must be published in English before translating",route},409);
    if(!title||!description||html.length<120||!/<(?:section|article|div|h1)\b/i.test(html))
      return respond({error:"Full translated title, description and main HTML required",route,locale},400);
    if(/<\s*(?:script|iframe|object|embed|form|style|link|base|meta|svg|math|template)\b|\bon[a-z-]+\s*=|\bsrcdoc\s*=|(?:javascript|vbscript|data)\s*:/i.test(html))
      return respond({error:"Unsafe HTML in translated content",route,locale},400);
    statements.push(db.prepare(`INSERT INTO xuyi_translation_overrides(resource_id,locale,translated_json,reviewed_at)
      VALUES(?,?,?,CURRENT_TIMESTAMP)
      ON CONFLICT(resource_id,locale) DO UPDATE SET translated_json=excluded.translated_json,reviewed_at=CURRENT_TIMESTAMP`)
      .bind("page:"+route,locale,JSON.stringify({title,description,mainHtml:html})));
  }
  let results;
  try{results=await db.batch(statements)}
  catch{return respond({error:"Bulk translation write failed"},503)}
  const failed=results.filter(result=>Number(result?.meta?.changes||0)!==1);
  if(failed.length)return respond({error:"Bulk translation write was not confirmed",failed:failed.length},409);
  const revision=await bumpPublishRevision(db);
  return respond({saved:true,reviewed:true,bulk:true,count:items.length,...revision});
}

export async function onRequestGet(c){
  const denied=await requireAdmin(c);if(denied)return denied;
  const rows=(await c.env.LEYA_DB.prepare(
    "SELECT resource_id,locale,translated_json,reviewed_at FROM xuyi_translation_overrides WHERE resource_id LIKE 'page:%' ORDER BY locale,resource_id LIMIT 12000"
  ).all()).results||[];
  return respond({items:rows.map(x=>({route:x.resource_id.slice(5),locale:x.locale,
    content:JSON.parse(x.translated_json),reviewedAt:x.reviewed_at}))});
}
export async function onRequestPost(c){
  const denied=await requireAdmin(c);if(denied)return denied;
  let p;try{p=await c.request.json()}catch{return respond({error:"Invalid JSON"},400)}
  if(p?.action==="bulk-update")return saveBlogTranslationBatch(c,p.items);
  const route=clean(p.route,250),locale=clean(p.locale,12).toLowerCase();
  const title=clean(p.title,180),description=clean(p.description,450),html=clean(p.mainHtml,250000);
  if(!(route==="/"||/^\/(?:[A-Za-z0-9_-]+\/)+$/.test(route)||/^\/[A-Za-z0-9_-]+(?:\/[A-Za-z0-9_-]+)*\.html$/.test(route)))
    return respond({error:"Invalid LEYA route"},400);
  const db=c.env.LEYA_DB;
  const languageRow=await loadSiteSetting(db,"language_config",defaultLanguageConfig());
  const languageConfig=normalizeLanguageConfig(languageRow.value);
  // Translation may be prepared while a language remains disabled/draft.
  // Publication is gated separately by publishReady and the build registry.
  if(locale===languageConfig.sourceLocale||
     !languageConfig.languages.some(lang=>lang.code===locale))
    return respond({error:"Locale must exist in the LEYA MOULD language registry and differ from the source language"},400);
  if(!title||!description||html.length<120||!/<(?:section|article|div|h1)\b/i.test(html))
    return respond({error:"Full translated title, description and main HTML required"},400);
  if(/<\s*(?:script|iframe|object|embed|form|style|link|base|meta|svg|math|template)\b|\bon[a-z-]+\s*=|\bsrcdoc\s*=|(?:javascript|vbscript|data)\s*:/i.test(html))
    return respond({error:"Unsafe HTML in translated content"},400);
  const configured=new Set(await configuredRoutes(db));
  const blogMatch=/^\/blog\/([a-z0-9][a-z0-9-]{1,119})\/$/.exec(route);
  const productMatch=/^\/product\/([A-Za-z0-9][A-Za-z0-9-]{1,80})\.html$/.exec(route);
  if(blogMatch){
    let blogRow;
    try{blogRow=await db.prepare("SELECT status FROM xuyi_blog_posts WHERE slug=?")
      .bind(blogMatch[1]).first()}
    catch{return respond({error:"Unable to validate D1 Blog route"},503)}
    if(blogRow?.status!=="published")
      return respond({error:"Blog article must be published in English before translating"},409);
  }else if(productMatch){
    // Product eligibility comes from D1. The static route manifest is only a
    // compatibility index and cannot authorize a product translation.
    const rawSlug=productMatch[1],model=mouldModelFromRoute(route)||rawSlug.toLowerCase();
    const aliases=[model];
    const marks=aliases.map(()=>"?").join(",");
    let record;
    try{record=await db.prepare("SELECT publication_status FROM xuyi_product_content WHERE model IN ("+marks+") LIMIT 1")
      .bind(...aliases).first()}
    catch{return respond({error:"Unable to validate D1 product route"},503)}
    if(record?.publication_status!=="published")
      return respond({error:"Product must be published in English before translating"},409);
  }else if(!MANAGED_ROUTES.has(route)&&!configured.has(route)){
    return respond({error:"Unknown LEYA MOULD route"},400);
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
    if(matched.length>1)return respond({error:"Target language Blog index contains duplicate cards"},409);
    let nextIndex=current;
    if(matched.length===1){
      const oldCard=matched[0][0];
      const updatedCard=oldCard
        .replace(/(<h3><a[^>]*>)[\s\S]*?(<\/a><\/h3>)/i,"$1"+esc(title)+"$2")
        .replace(/(<p>)[\s\S]*?(<\/p>)/i,"$1"+esc(description)+"$2");
      nextIndex=current.replace(oldCard,updatedCard);
    }else{
      const card=blogCard({...sourcePost,slug,title,description});
      const tail="</div></div></section>";
      if(!current.endsWith(tail))return respond({error:"Target language Blog index has an unexpected structure"},409);
      nextIndex=current.slice(0,-tail.length)+card+tail;
    }
    let ordered;try{ordered=sortLocalizedBlogIndexByD1Order(nextIndex,d1Order)}catch(error){return respond({error:"Target language Blog index failed D1 order validation: "+String(error.message||error)},409)}
    const nextIndexJson=JSON.stringify({...index,mainHtml:ordered});
    indexStatement=db.prepare("UPDATE xuyi_translation_overrides SET translated_json=?,reviewed_at=CURRENT_TIMESTAMP WHERE resource_id='page:/blog/' AND locale=? AND translated_json=?").bind(nextIndexJson,locale,indexRow.translated_json);
    statements.push(indexStatement);
  }
  if(route.startsWith("/product/")){
    await ensureProductSeo(db);
    const slug=canonicalProductSlug(route.split("/")[2].replace(/\.html$/,""));
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
