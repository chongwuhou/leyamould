import { ensureBlogSchema, listBlogPosts, findBlogPost, esc, blogCard, blogHtml, composePage } from "../_shared/blog-cms.js";
import {englishAltFor} from "../_shared/media-alt.js";
async function assetHtml(context,path){
 const url=new URL(path,context.request.url);
 const res=await context.env.ASSETS.fetch(new Request(url.toString()));
 if(!res.ok)throw Error("Asset template is unavailable: "+res.status);
 return await res.text();
}
function response(html,status=200){
 // The live D1 route must obey the release's robots gate. It previously
 // returned noindex regardless of the published page indexing setting.
 const canIndex=status===200&&/<meta name="robots" content="index,follow">/i.test(html);
 return new Response(html,{status,headers:{"content-type":"text/html; charset=UTF-8","cache-control":"public, max-age=90","x-robots-tag":canIndex?"index,follow":"noindex,follow","x-content-type-options":"nosniff"}});
}
export async function onRequestGet(context){
 if(!context.env.XUYI_DB)return context.next();
 const pathname=new URL(context.request.url).pathname;
 const tail=pathname.replace(/^\/blog\/?/,"").replace(/\/$/,"");
 if(tail&&(!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(tail)))return context.next();
 const db=context.env.XUYI_DB;
 try{
  await ensureBlogSchema(db);
  if(tail){
   const post=await findBlogPost(db,tail);
   if(!post)return context.next(); // older catalog articles remain in immutable static build
   if(post.status!=="published")return response("<!doctype html><html lang='en'><head><meta name='robots' content='noindex'><title>Article unavailable</title></head><body><p>Article unavailable.</p><a href='/blog/'>Back to Blog</a></body></html>",404);
   // Use THIS article's static shell so the live D1 article preserves the
   // exact five-language hreflang cluster, not the /blog/ index alternates.
   // D1-only articles with no approved translations intentionally get no
   // alternate links until localized pages are actually published.
   let shell;
   try{
    shell=await assetHtml(context,"/blog/"+tail+"/index.html");
    if(!shell.includes('<link rel="canonical" href="https://xuyibottles.com/blog/'+tail+'/">'))
     throw Error("Article shell missing or mismatched");
   }catch{
    shell=(await assetHtml(context,"/blog/index.html"))
      .replace(/<link rel="alternate"\s+hreflang="[^"]+"\s+href="[^"]+">/g,"");
   }
   // The route slug, not an editable content_json field, identifies which
   // article is published and which source-reviewed notes belong to it.
   const published={...post,slug:tail,coverAlt:await englishAltFor(db,post.cover)};
   return response(composePage(shell,blogHtml(published),published,"/blog/"+tail+"/"));
  }
  const posts=await listBlogPosts(db,"published");
  if(!posts.length)return context.next();
  for(const post of posts)post.coverAlt=await englishAltFor(db,post.cover);
  const template=await assetHtml(context,"/blog/index.html");
  let body='<section class="page-intro"><div class="shell"><div class="breadcrumb"><a href="/">Home</a> / Blog</div><span class="eyebrow">XUYI · PLASTIC DRINKWARE</span><h1>Water Bottle Buying Guides</h1><p>Practical guides to material choice, wholesale sourcing, OEM customization and quality assurance.</p></div></section>';
  body+='<section class="section blog-listing"><div class="shell"><div class="section__head"><div><span class="eyebrow">BUYER RESOURCES</span><h2 class="section__title">Sourcing Knowledge Center</h2><p>Explore '+posts.length+' buying guides written for B2B customers.</p></div></div>';
  body+='<div class="blog-listing__grid">'+posts.map(blogCard).join('')+'</div></div></section>';
  return response(composePage(template,body,null,"/blog/"));
 }catch(error){
  // Availability of the site must not depend on D1; untouched static pages stay accessible.
  return context.next();
 }
}