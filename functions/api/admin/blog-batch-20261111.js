import { authorizedReviewedBlogBatchRequest } from "../../_shared/build-auth.js";
import { ensureBlogSchema,listBlogPosts,sortLocalizedBlogIndexByD1Order } from "../../_shared/blog-cms.js";
import { bumpPublishRevision } from "../../_shared/site-settings.js";

const SLUGS=[
  "custom-water-bottle-logo-printing-methods-bulk-order",
  "which-water-bottle-closure-type-best-wholesale-order",
  "corporate-wellness-water-bottle-capacity-bulk-order"
];
const LANGS=["es","pt","ru","tr"];
const DAY="2026-11-11",TAIL="</div></div></section>";
const RFQ_MIGRATION=Object.freeze({
 slug:"wholesale-water-bottle-rfq-oem-pricing-checklist",
 oldCover:"/media/blog/wholesale-water-bottle-rfq-20261110.webp",
 newCover:"/media/blog/wholesale-water-bottle-rfq-photo-20261111.webp",
 alt:{
  en:"Natural product photograph of a reusable bottle sample, cap components and quotation review materials for a wholesale RFQ; confirm the exact SKU before ordering.",
  es:"Fotografía natural de una muestra de botella reutilizable, componentes de tapa y materiales de revisión de una RFQ mayorista; confirme el SKU exacto antes de comprar.",
  pt:"Fotografia natural de uma amostra de garrafa reutilizável, componentes da tampa e materiais de revisão de uma RFQ no atacado; confirme o SKU exato antes da compra.",
  ru:"Натуральная фотография образца многоразовой бутылки, компонентов крышки и материалов для проверки оптового RFQ; подтвердите точный SKU перед заказом.",
  tr:"Toptan RFQ incelemesi için yeniden kullanılabilir matara numunesi, kapak bileşenleri ve teklif malzemelerinin doğal ürün fotoğrafı; siparişten önce kesin SKU'yu doğrulayın."
 }
});
const response=(x,status=200)=>Response.json(x,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
const count=(s,t)=>String(s).split(t).length-1;
const replaceCoverMarkup=(html,oldCover,newCover,alt)=>String(html||"").replace(new RegExp('<img src="'+oldCover.replaceAll(".","\\.")+'" alt="[^"]*"','g'),'<img src="'+newCover+'" alt="'+alt+'"');
const cardFor=(cards,locale,slug)=>cards.find(card=>card.locale===locale&&card.slug===slug)?.html||"";
const blocked=/<\s*(?:script|iframe|object|embed|form|style|link|base|meta|svg|math|template)\b|\bon[a-z-]+\s*=|\bsrcdoc\s*=|(?:javascript|vbscript|data)\s*:/i;export function validatePayload(p){
 if(!p||!Array.isArray(p.posts)||p.posts.length!==3||!Array.isArray(p.translations)||p.translations.length!==12||!Array.isArray(p.indexCards)||p.indexCards.length!==12)throw Error("Batch shape requires 3 posts and 12 translations/cards");
 const allowed=new Set(SLUGS),slugs=new Set(),translations=new Set(),cards=new Set();
 for(const item of p.posts){
  const slug=String(item?.slug||""),post=item?.post;
  if(!allowed.has(slug)||slugs.has(slug)||post?.slug!==slug)throw Error("Duplicate or unapproved article");
  if(post.updated!==DAY||typeof post.title!=="string"||post.title.length<12||typeof post.description!=="string"||post.description.length<25||typeof post.intro!=="string"||post.intro.length<150||!/^\/(?:assets\/(?:blog|editorial|curated-hd|products)|media\/blog)\/[a-z0-9-]+\.webp$/.test(String(post.cover||""))||!Array.isArray(post.sections)||post.sections.length!==7||post.sections.some(s=>String(s.paragraph||"").length<650)||!Array.isArray(post.checklist)||post.checklist.length!==10||!Array.isArray(post.faqs)||post.faqs.length!==4||!Array.isArray(post.related)||post.related.length!==3||!Array.isArray(post.product_notes)||post.product_notes.length!==3||JSON.stringify(post).length>100000)throw Error("Unapproved post structure: "+slug);
  if(!post.cover.endsWith("-20261111.webp"))throw Error("New cover not reviewed: "+slug);
  slugs.add(slug);
 }
 for(const t of p.translations){
  const slug=String(t?.route||"").match(/^\/blog\/([a-z0-9-]+)\/$/)?.[1],locale=String(t?.locale||""),key=slug+"|"+locale,html=String(t?.mainHtml||"");
  if(!allowed.has(slug)||!LANGS.includes(locale)||translations.has(key)||String(t.title||"").length<12||String(t.description||"").length<25||html.length<5000||html.length>250000||blocked.test(html)||count(html,'class="blog-section"')!==7||count(html,'class="blog-editorial__product-link"')!==3||count(html,'class="blog-related__item"')!==3||count(html,'class="blog-buyer-matrix"')!==1||count(html,"<details>")!==4)throw Error("Unapproved localized body: "+key);
  const expectedCover=p.posts.find(item=>item.slug===slug)?.post?.cover;
  if(!expectedCover||!html.includes('src="'+expectedCover+'"'))throw Error("Localized hero cover mismatch: "+key);
  translations.add(key);
 }
 for(const t of p.indexCards){
  const slug=String(t?.slug||""),loc=String(t?.locale||""),html=String(t?.html||""),key=slug+"|"+loc;
  if(!allowed.has(slug)||!LANGS.includes(loc)||cards.has(key)||html.length<100||html.length>10000||blocked.test(html)||!html.startsWith('<article class="news-card">')||!html.endsWith("</article>")||count(html,'href="/blog/'+slug+'/"')!==3)throw Error("Unapproved index card: "+key);
  const expectedCover=p.posts.find(item=>item.slug===slug)?.post?.cover;
  if(!expectedCover||!html.includes('src="'+expectedCover+'"'))throw Error("Localized list cover mismatch: "+key);
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
  for(const item of p.posts)stmts.push(db.prepare("INSERT INTO xuyi_blog_posts (slug,status,content_json,published_at,updated_at) VALUES(?,'published',?,?,CURRENT_TIMESTAMP) ON CONFLICT(slug) DO UPDATE SET status=excluded.status,content_json=excluded.content_json,published_at=excluded.published_at,updated_at=CURRENT_TIMESTAMP").bind(item.slug,JSON.stringify(item.post),DAY+"T00:00:00Z"));
  for(const t of p.translations)stmts.push(db.prepare("INSERT INTO xuyi_translation_overrides (resource_id,locale,translated_json,reviewed_at) VALUES(?,?,?,?) ON CONFLICT(resource_id,locale) DO UPDATE SET translated_json=excluded.translated_json,reviewed_at=excluded.reviewed_at").bind("page:"+t.route,t.locale,JSON.stringify({title:t.title,description:t.description,mainHtml:t.mainHtml}),DAY));
  const done=await db.batch(stmts);
  const changes=(a,b)=>done.slice(a,b).reduce((total,x)=>total+Number(x?.meta?.changes||0),0);
  const postsInserted=changes(0,3),translationsInserted=changes(3,15);  const saved=(await db.prepare("SELECT slug,status FROM xuyi_blog_posts WHERE slug IN (?,?,?)").bind(...SLUGS).all()).results||[];
  if(saved.filter(x=>x.status==="published"&&SLUGS.includes(x.slug)).length!==3)return response({error:"Article verification failed"},409);

  // The English live route uses listBlogPosts() (updated_at DESC). Use that
  // complete D1 result as the sole ordering source for every localized index.
  // Do not append today's cards as a final order or hardcode any batch slugs.
  const d1Posts=await listBlogPosts(db,"published");
  const d1Order=d1Posts.map(post=>post.slug);
  if(!d1Order.length||new Set(d1Order).size!==d1Order.length
     ||SLUGS.some(slug=>!d1Order.includes(slug)))
   return response({error:"D1 published Blog order is incomplete or duplicated"},409);
  const orderWrites=[];let indexCardsUpdated=0;
  for(const lang of LANGS){
   const row=await db.prepare("SELECT translated_json FROM xuyi_translation_overrides WHERE resource_id='page:/blog/' AND locale=?").bind(lang).first();
   if(!row?.translated_json)return response({error:"Localized Blog index override missing: "+lang},409);
   let index;try{index=JSON.parse(row.translated_json);}catch{return response({error:"Localized Blog index JSON invalid: "+lang},409);}
   let current=String(index.mainHtml||"");
   const replacements=new Map();
   for(const slug of SLUGS){
    const card=cardFor(p.indexCards,lang,slug);
    if(!card)return response({error:"Localized Blog card missing: "+lang+"|"+slug},409);
    replacements.set(slug,card);indexCardsUpdated++;
   }
   // Rebuild the complete grid from balanced leaf cards. This repairs old
   // nested-card records and prevents a replacement from spanning adjacent
   // cards when a localized URL contains /blog/.
   const ordered=sortLocalizedBlogIndexByD1Order(current,d1Order,replacements);
   if(ordered!==current){
    const updated={...index,mainHtml:ordered};
    orderWrites.push({locale:lang,statement:db.prepare("UPDATE xuyi_translation_overrides SET translated_json=? WHERE resource_id='page:/blog/' AND locale=? AND translated_json=?").bind(JSON.stringify(updated),lang,row.translated_json)});
   }
  }  const orderResults=orderWrites.length?await db.batch(orderWrites.map(item=>item.statement)):[];
  const localizedIndexesReordered=orderResults.reduce((total,item)=>total+Number(item?.meta?.changes||0),0);
  if(localizedIndexesReordered!==orderWrites.length)
   return response({error:"Localized Blog index changed during the conditional D1-order update"},409);
  const indexRows=(await db.prepare("SELECT locale,translated_json FROM xuyi_translation_overrides WHERE resource_id='page:/blog/' AND locale IN (?,?,?,?)").bind(...LANGS).all()).results||[];
  const indexByLocale=new Map(indexRows.map(row=>[row.locale,JSON.parse(row.translated_json).mainHtml||""]));
  for(const lang of LANGS){
   const html=indexByLocale.get(lang)||"";
   if(!html||sortLocalizedBlogIndexByD1Order(html,d1Order)!==html)
    return response({error:"Localized Blog index does not match the D1 published order: "+lang},409);
  }

  // Fixed owner-approved migration for the RFQ cover shown in the defect
  // report. It updates D1 post/detail/index records together and never
  // replaces a cover that an editor has already changed to another path.
  const rfqRow=await db.prepare("SELECT status,content_json FROM xuyi_blog_posts WHERE slug=?").bind(RFQ_MIGRATION.slug).first();
  if(!rfqRow||rfqRow.status!=="published")return response({error:"RFQ article is not published in D1"},409);
  let rfqPost;try{rfqPost=JSON.parse(rfqRow.content_json||"{}")}catch{return response({error:"RFQ D1 content JSON invalid"},409)}
  if(![RFQ_MIGRATION.oldCover,RFQ_MIGRATION.newCover].includes(rfqPost.cover))
   return response({error:"RFQ cover was changed by an editor; migration preserved it"},409);
  const migrationWrites=[];let rfqChanged=0;
  if(rfqPost.cover===RFQ_MIGRATION.oldCover){
   const next={...rfqPost,cover:RFQ_MIGRATION.newCover,coverAlt:RFQ_MIGRATION.alt.en};
   migrationWrites.push(db.prepare("UPDATE xuyi_blog_posts SET content_json=? WHERE slug=? AND status='published' AND content_json=?").bind(JSON.stringify(next),RFQ_MIGRATION.slug,rfqRow.content_json));
   rfqChanged++;
  }
  for(const lang of LANGS){
   const detailId="page:/blog/"+RFQ_MIGRATION.slug+"/";
   const detail=await db.prepare("SELECT translated_json FROM xuyi_translation_overrides WHERE resource_id=? AND locale=?").bind(detailId,lang).first();
   const index=await db.prepare("SELECT translated_json FROM xuyi_translation_overrides WHERE resource_id='page:/blog/' AND locale=?").bind(lang).first();
   if(!detail?.translated_json||!index?.translated_json)return response({error:"RFQ localized D1 record missing: "+lang},409);
   let detailJson,indexJson;try{detailJson=JSON.parse(detail.translated_json);indexJson=JSON.parse(index.translated_json)}catch{return response({error:"RFQ localized D1 JSON invalid: "+lang},409)}
   for(const [kind,row,json,id] of [["detail",detail,detailJson,detailId],["index",index,indexJson,"page:/blog/"]]){
    const current=String(json.mainHtml||"");
    if(!current.includes(RFQ_MIGRATION.oldCover)&&!current.includes(RFQ_MIGRATION.newCover))return response({error:"RFQ "+kind+" cover was changed by an editor; migration preserved it: "+lang},409);
    const nextHtml=current.includes(RFQ_MIGRATION.oldCover)?replaceCoverMarkup(current,RFQ_MIGRATION.oldCover,RFQ_MIGRATION.newCover,RFQ_MIGRATION.alt[lang]):current;
    if(nextHtml!==current){
     const next={...json,mainHtml:nextHtml};
     migrationWrites.push(db.prepare("UPDATE xuyi_translation_overrides SET translated_json=?,reviewed_at=CURRENT_TIMESTAMP WHERE resource_id=? AND locale=? AND translated_json=?").bind(JSON.stringify(next),id,lang,row.translated_json));
     rfqChanged++;
    }
   }
  }
  if(migrationWrites.length){
   const migrationResults=await db.batch(migrationWrites);
   if(migrationResults.some(item=>Number(item?.meta?.changes||0)!==1))return response({error:"RFQ cover migration changed during the conditional D1 update"},409);
  }

  const refs=["page:/blog/",...SLUGS.map(s=>"page:/blog/"+s+"/")];
  const rows=(await db.prepare("SELECT resource_id,locale,translated_json FROM xuyi_translation_overrides WHERE resource_id IN (?,?,?,?) AND locale IN (?,?,?,?)").bind(...refs,...LANGS).all()).results||[];
  const lookup=new Map(rows.map(x=>[x.resource_id+"|"+x.locale,JSON.parse(x.translated_json).mainHtml||""]));
  for(const lang of LANGS){
   const index=lookup.get("page:/blog/|"+lang)||"";
   for(const slug of SLUGS){
    const body=lookup.get("page:/blog/"+slug+"/|"+lang)||"";
    if(body.length<5000||count(body,'class="blog-section"')!==7||count(body,'class="blog-editorial__product-link"')!==3||count(body,'class="blog-related__item"')!==3||count(body,'class="blog-buyer-matrix"')!==1||count(body,"<details>")!==4)return response({error:"Incomplete persisted translation"},409);
     const matched=index.split('<article class="news-card">').slice(1).map(x=>x.split("</article>",1)[0]).filter(x=>x.includes('/blog/'+slug+'/'));
     if(matched.length!==1||count(matched[0],'/blog/'+slug+'/')!==3)return response({error:"Incomplete persisted index"},409);   }
  }
  const revision=await bumpPublishRevision(db);
  return response({success:true,postsInserted,translationsInserted,indexCardsAdded:indexCardsUpdated,localizedIndexesReordered,rfqCoverRecordsChanged:rfqChanged,d1PublishedCount:d1Order.length,indexOrderVerified:LANGS,publishRevision:revision.revision,publishedSlugs:SLUGS});
 }catch(e){return response({error:"D1 batch failed: "+String(e.message||"unknown").slice(0,160)},500);}
}

