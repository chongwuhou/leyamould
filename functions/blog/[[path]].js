import { ensureBlogSchema, listBlogPosts, findBlogPost, esc, blogCard, blogHtml, composePage } from "../_shared/blog-cms.js";
import {englishAltFor} from "../_shared/media-alt.js";
import COVER_OVERRIDES from "../../data/blog-cover-overrides.json" with {type:"json"};
import PHOTO_CORRECTIONS from "../../data/blog-photo-corrections-20261024.json" with {type:"json"};
import SHAKER_IMAGES from "../../data/gpt-reviewed-shaker-hd-20261013.json" with {type:"json"};
import SEARCH_ROLES from "../../data/search-intent-three-landing-roles.json" with {type:"json"};

// D1 text is authoritative. Only the original reviewed article headline and
// description acquire the new informational search intent.
export function withInformationalIntent(post){
 if(post?.slug!=="sports-water-bottle-customization")return post;
 const role=SEARCH_ROLES.languages.en.blog;
 if(post.title!==role.baseline.title || post.description!==role.baseline.description)return post;
 return {...post,title:role.preferred.title,description:role.preferred.description};
}

// Keep D1 as the source of published article text/status and preserve future
// editor-chosen photos. Only the eight known, duplicated legacy image paths
// receive an approved presentation-only override; never write to D1.
const ORIGINAL_COVERS=Object.freeze({
 "plastic-bottle-material-selection":"/media/ppt/slide-066.webp",
 "custom-logo-water-bottle-checklist":"/media/ppt/slide-061.webp",
 "tritan-vs-pp-petg-pc":"/media/ppt/slide-037.webp",
 "water-bottle-lid-leakproof-testing":"/media/ppt/slide-055.webp",
 "custom-water-bottle-moq-pricing":"/media/ppt/slide-061.webp",
 "water-bottle-quality-control-checklist":"/media/ppt/slide-030.webp",
 "custom-water-bottle-export-packaging":"/media/ppt/slide-059.webp",
 "how-to-start-private-label-water-bottle-brand":"/media/ppt/slide-049.webp"
});
export function withReviewedCover(post){
 // Five reviewed actual-photo selections: only upgrade the specific image
 // present when the defect was reported. Future owner CMS covers always win.
 const approved=PHOTO_CORRECTIONS[post.slug];
 if(approved && post.cover===approved.baseline)return {...post,cover:approved.photo};
 const old=ORIGINAL_COVERS[post.slug],newCover=COVER_OVERRIDES[post.slug];
 if(old && newCover && post.cover===old)return {...post,cover:newCover};
 // Only this originally unique shaker-guide cover uses the same approved
 // 6-bottle source as model 501. Respect new images chosen through D1 CMS.
 if(post.slug==="shaker-bottle-wholesale"){
  const photo=SHAKER_IMAGES.approved.find(x=>x.old==="/media/ppt/slide-091.webp");
  if(photo && post.cover===photo.old)return {...post,cover:photo.new};
 }
 return post;
}
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
   const published=withInformationalIntent(withReviewedCover({...post,slug:tail}));
   published.coverAlt=await englishAltFor(db,published.cover);
   return response(composePage(shell,blogHtml(published),published,"/blog/"+tail+"/"));
  }
  const posts=(await listBlogPosts(db,"published")).map(withReviewedCover).map(withInformationalIntent);
  if(!posts.length)return context.next();
  for(const post of posts)post.coverAlt=await englishAltFor(db,post.cover);
  const template=await assetHtml(context,"/blog/index.html");
  let body='<section class="page-intro"><div class="shell"><div class="breadcrumb"><a href="/">Home</a> / Blog</div><span class="eyebrow">XUYI · PLASTIC DRINKWARE</span><h1>Water Bottle Buying Guides</h1><p>Practical guides to material choice, wholesale sourcing, OEM customization and quality assurance.</p></div></section>';
  // One shared page header, followed directly by the D1-owned article grid.
  body+='<section class="section blog-listing"><div class="shell">';
  body+='<div class="blog-listing__grid">'+posts.map(blogCard).join('')+'</div></div></section>';
  return response(composePage(template,body,null,"/blog/"));
 }catch(error){
  // Availability of the site must not depend on D1; untouched static pages stay accessible.
  return context.next();
 }
}
