import {authorizedReviewedBlogBatchRequest} from "../../_shared/build-auth.js";
import {ensureBlogSchema,normalizeBlogPost} from "../../_shared/blog-cms.js";
import {ensurePublishScheduler,scheduleBlogPost,scheduleBlogLocalePost} from "../../_shared/publish-scheduler.js";
import IMAGE_MANIFEST from "../../../data/blog-images-reviewed-20261103.json" with {type:"json"};
import SCHOOL from "../../../data/blog-scheduled-20261103-1.json" with {type:"json"};
import PARKS from "../../../data/blog-scheduled-20261103-2.json" with {type:"json"};
import CORPORATE from "../../../data/blog-scheduled-20261103-3.json" with {type:"json"};

const DAY="2026-11-03";
const LOCALES=["es","pt","ru","tr"];
const SCHEDULES={
  "bulk-water-bottles-for-school-student-programs":"2026-11-03T09:15:00+08:00",
  "parks-recreation-water-bottle-bulk-procurement":"2026-11-03T13:00:00+08:00",
  "corporate-wellness-water-bottle-bulk-sourcing":"2026-11-03T16:30:00+08:00"
};
const PRODUCTS={
  "bulk-water-bottles-for-school-student-programs":["2501","2508","2509"],
  "parks-recreation-water-bottle-bulk-procurement":["2501","2502","2505"],
  "corporate-wellness-water-bottle-bulk-sourcing":["2511","2512","2513"]
};
const SOURCES=[SCHOOL,PARKS,CORPORATE];
const reply=(body,status=200)=>Response.json(body,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
const unique=values=>[...new Set(values)];
const imageFor=slug=>IMAGE_MANIFEST.images.find(x=>x.slug===slug);
const bodyOf=post=>post.sections.map(x=>x.paragraph).join("\n");
const productLinks=post=>unique([...bodyOf(post).matchAll(/\]\(\/products\/([A-Za-z0-9_-]+)\//g)].map(x=>x[1]));
const objectKey=image=>"site-blog/"+image.cover.split("/").at(-1);
const sha256=async value=>Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",new TextEncoder().encode(value)))).map(v=>v.toString(16).padStart(2,"0")).join("");
const count=(v,n)=>String(v).split(n).length-1;
const blocked=/<\s*(?:script|iframe|object|embed|form|style|link|base|meta|svg|math|template)\b|\bon[a-z-]+\s*=|\bsrcdoc\s*=|(?:javascript|vbscript|data)\s*:/i;

export function prepareScheduledPosts(){
  const prepared=[];
  for(const source of SOURCES){
    const slug=String(source?.slug||"");
    const scheduledAt=SCHEDULES[slug];
    if(!scheduledAt||source.updated!==DAY)throw Error("Unapproved article or schedule date: "+slug);
    const post=normalizeBlogPost(source);
    post.updated=DAY;
    if(post.sections.length!==7||post.sections.some(x=>x.paragraph.length<650)
      ||post.checklist.length!==10||post.faqs.length!==4||post.related.length!==3)
      throw Error("Article structure failed: "+slug);
    const links=productLinks(post),expected=PRODUCTS[slug];
    if(!expected||links.length!==3||expected.some(x=>!links.includes(x))||links.some(x=>!expected.includes(x)))
      throw Error("Three distinct approved product links required: "+slug);
    if(unique(post.related).length!==3||post.related.includes(slug))
      throw Error("Three distinct related articles required: "+slug);
    const image=imageFor(slug);
    if(!image||post.cover!==image.cover||!post.cover.endsWith("-20261103.webp")||post.coverAlt.length<40)
      throw Error("Cover or visible-scene alt mismatch: "+slug);
    const sourceMetadata=SOURCES.find(x=>x.slug===slug);
    if(sourceMetadata?.product_notes?.length!==3||sourceMetadata?.inline_links?.length!==2||
       sourceMetadata?.buyerDecisionTable?.rows?.length!==6)
      throw Error("Model notes, contextual links or buyer decision matrix missing: "+slug);
    const contentJson=JSON.stringify(post);
    if(contentJson.length>100000)throw Error("Article exceeds CMS content limit: "+slug);
    prepared.push({slug,post,contentJson,scheduledAt,image,sourceMetadata});
  }
  if(prepared.length!==3)throw Error("Exactly three articles required");
  return prepared;
}

export function validateLocalizedPayload(input,prepared=prepareScheduledPosts()){
  const translations=Array.isArray(input?.translations)?input.translations:[];
  const cards=Array.isArray(input?.indexCards)?input.indexCards:[];
  if(translations.length!==12||cards.length!==12)throw Error("Exactly 12 translated article pages and 12 localized index cards are required");
  const translationMap=new Map(),cardMap=new Map();
  for(const item of translations){
    const key=String(item?.slug||"")+"|"+String(item?.locale||"");
    if(translationMap.has(key))throw Error("Duplicate localized article: "+key);
    translationMap.set(key,item);
  }
  for(const item of cards){
    const key=String(item?.slug||"")+"|"+String(item?.locale||"");
    if(cardMap.has(key))throw Error("Duplicate localized index card: "+key);
    cardMap.set(key,item);
  }
  for(const source of prepared){
    for(const locale of LOCALES){
      const key=source.slug+"|"+locale,t=translationMap.get(key),card=cardMap.get(key);
      if(!t||!card)throw Error("Missing locale page or index card: "+key);
      if(t.route!=="/blog/"+source.slug+"/"||card.slug!==source.slug||card.locale!==locale)
        throw Error("Localized route identity mismatch: "+key);
      if(String(t.title||"").length<12||String(t.description||"").length<25)
        throw Error("Localized SEO title or description is incomplete: "+key);
      const html=String(t.mainHtml||""),cardHtml=String(card.html||"");
      const sectionBlocks=html.split('<section class="blog-section"').slice(1).map(x=>x.split("</section>",1)[0]);
      const linkedSections=sectionBlocks.filter(x=>x.includes('class="blog-editorial__product-link"')).length;
      if(html.length<5000||html.length>250000||blocked.test(html)||count(html,'class="blog-section"')!==7||
         count(html,'class="blog-editorial__product-link"')!==3||linkedSections!==3||count(html,'class="blog-related__item"')!==3||
         count(html,'class="blog-buyer-matrix"')!==1||count(html,"<details>")!==4||
         !html.includes('src="'+source.post.cover+'"'))
        throw Error("Localized article structure or cover validation failed: "+key);
      const alt=/<img\b[^>]*\balt="([^"]+)"/i.exec(html)?.[1]||"";
      if(alt.length<40)throw Error("Localized visible-scene cover alt is missing: "+key);
      for(const model of PRODUCTS[source.slug]){
        if(!html.includes('href="/'+locale+'/products/'+model+'/"'))throw Error("Localized model link missing: "+key+" "+model);
      }
      for(const related of source.post.related){
        if(!html.includes('href="/'+locale+'/blog/'+related+'/"'))throw Error("Localized related link missing: "+key+" "+related);
      }
      if(!cardHtml.startsWith('<article class="news-card">')||!cardHtml.endsWith("</article>")||blocked.test(cardHtml)||
         count(cardHtml,'href="/blog/'+source.slug+'/"')!==3||!cardHtml.includes('src="'+source.post.cover+'"'))
        throw Error("Localized index card validation failed: "+key);
      if(!cardHtml.includes('alt="')||!cardHtml.match(/\balt="[^"]{40,}"/))
        throw Error("Localized index card cover alt is missing: "+key);
    }
  }
  return {translations:translationMap,cards:cardMap};
}

export async function onRequestPost(context){
  if(!(await authorizedReviewedBlogBatchRequest(context.request,context.env)))return reply({error:"Unauthorized"},401);
  const db=context.env.XUYI_DB,bucket=context.env.XUYI_ASSETS;
  if(!db||!bucket)return reply({error:"XUYI D1 or R2 binding unavailable"},503);
  let input;try{input=await context.request.json();}catch{return reply({error:"Invalid JSON"},400);}
  if(input?.editorialApproved!==true)return reply({error:"Owner authorization for the five-language scheduled release is required"},400);
  let prepared,localized;
  try{prepared=prepareScheduledPosts();localized=validateLocalizedPayload(input,prepared);}
  catch(e){return reply({error:String(e.message||e).slice(0,260)},400);}
  try{
    await ensureBlogSchema(db);
    await ensurePublishScheduler(db);
    const tasks=(await db.prepare("SELECT daily_limit FROM xuyi_publish_tasks WHERE content_type='blog' AND enabled=1").all()).results||[];
    const limit=tasks.reduce((n,x)=>n+Math.max(0,Number(x.daily_limit||0)),0);
    if(limit<3)return reply({error:"Enabled Blog daily limit is below three"},409);
    const start="2026-11-02T16:00:00.000Z",end="2026-11-03T16:00:00.000Z";
    const slugs=prepared.map(x=>x.slug),marks=slugs.map(()=>"?").join(",");
    const otherScheduled=(await db.prepare("SELECT COUNT(*) AS n FROM xuyi_blog_schedule WHERE status='scheduled' AND approved=1 AND scheduled_at>=? AND scheduled_at<? AND slug NOT IN ("+marks+")").bind(start,end,...slugs).first())?.n||0;
    const otherPublished=(await db.prepare("SELECT COUNT(*) AS n FROM xuyi_blog_schedule WHERE status='published' AND published_at>=? AND published_at<? AND slug NOT IN ("+marks+")").bind(start,end,...slugs).first())?.n||0;
    if(Number(otherScheduled)+Number(otherPublished)+3>limit)return reply({error:"Other Blog posts already use part of the 2026-11-03 daily quota"},409);
    const localePlan=[];
    for(const item of prepared){
      const storedImage=await bucket.head(objectKey(item.image));
      if(!storedImage||storedImage.customMetadata?.sha256!==item.image.sha256||storedImage.httpMetadata?.contentType!=="image/webp")
        return reply({error:"Reviewed cover missing or unverified in R2: "+item.slug},409);
      const existing=await db.prepare("SELECT status,content_json FROM xuyi_blog_posts WHERE slug=?").bind(item.slug).first();
      if(existing&&existing.status!=="draft")return reply({error:"Existing article is not a draft: "+item.slug},409);
      if(existing&&existing.content_json!==item.contentJson)return reply({error:"Existing D1 draft differs from reviewed source: "+item.slug},409);
      const queue=await db.prepare("SELECT status,content_sha256 FROM xuyi_blog_schedule WHERE slug=?").bind(item.slug).first();
      if(queue&&(queue.status!=="scheduled"||queue.content_sha256!==await sha256(item.contentJson)))
        return reply({error:"Existing English schedule conflicts with this release: "+item.slug},409);
      for(const locale of LOCALES){
        const key=item.slug+"|"+locale,t=localized.translations.get(key),card=localized.cards.get(key);
        const translated={title:t.title,description:t.description,mainHtml:t.mainHtml};
        const payloadJson=JSON.stringify({locale,translated,indexCardHtml:card.html});
        const hash=await sha256(payloadJson),scheduledAt=new Date(item.scheduledAt).toISOString();
        const prior=await db.prepare("SELECT status,scheduled_at,approved,content_sha256,payload_json FROM xuyi_blog_locale_schedule WHERE slug=? AND locale=?").bind(item.slug,locale).first();
        if(prior&&(prior.status!=="scheduled"||Number(prior.approved)!==1||prior.scheduled_at!==scheduledAt||prior.content_sha256!==hash||prior.payload_json!==payloadJson))
          return reply({error:"Existing locale schedule conflicts with this release: "+key},409);
        const detail=await db.prepare("SELECT translated_json FROM xuyi_translation_overrides WHERE resource_id=? AND locale=?").bind("page:/blog/"+item.slug+"/",locale).first();
        if(detail){
          let saved;try{saved=JSON.parse(detail.translated_json)}catch{return reply({error:"Existing locale article override is invalid: "+key},409);}
          if(saved.title!==translated.title||saved.description!==translated.description||saved.mainHtml!==translated.mainHtml)
            return reply({error:"Existing locale article override differs from this release: "+key},409);
        }
        const index=await db.prepare("SELECT translated_json FROM xuyi_translation_overrides WHERE resource_id='page:/blog/' AND locale=?").bind(locale).first();
        if(!index)return reply({error:"Localized Blog index override missing: "+locale},409);
        let indexContent;try{indexContent=JSON.parse(index.translated_json)}catch{return reply({error:"Localized Blog index JSON invalid: "+locale},409);}
        const href='href="/blog/'+item.slug+'/"',hrefCount=count(indexContent.mainHtml||"",href);
        if(hrefCount!==0&&!(hrefCount===3&&String(indexContent.mainHtml).includes(card.html)))
          return reply({error:"Localized Blog index already contains a conflicting card: "+key},409);
        if(hrefCount===0&&!String(indexContent.mainHtml||"").endsWith("</div></div></section>"))
          return reply({error:"Localized Blog index does not have the reviewed insertion point: "+locale},409);
        localePlan.push({slug:item.slug,locale,scheduledAt,payloadJson,hash});
      }
    }
    // Confirm all manually selected related articles are already published
    // before creating any new draft or schedule row.
    for(const item of prepared){
      const relatedMarks=item.post.related.map(()=>"?").join(",");
      const related=(await db.prepare("SELECT slug FROM xuyi_blog_posts WHERE status='published' AND slug IN ("+relatedMarks+")").bind(...item.post.related).all()).results||[];
      if(unique(related.map(x=>x.slug)).length!==3)return reply({error:"Related articles are not all published: "+item.slug},409);
    }
    const inserts=prepared.map(x=>db.prepare("INSERT INTO xuyi_blog_posts(slug,status,content_json,published_at) VALUES(?,'draft',?,NULL) ON CONFLICT(slug) DO NOTHING").bind(x.slug,x.contentJson));
    if(inserts.length)await db.batch(inserts);
    const scheduled=[],localeSchedules=[];
    for(const item of prepared){
      const stored=await db.prepare("SELECT status,content_json FROM xuyi_blog_posts WHERE slug=?").bind(item.slug).first();
      if(stored?.status!=="draft"||stored.content_json!==item.contentJson)return reply({error:"D1 draft verification failed: "+item.slug},409);
      const marksRelated=item.post.related.map(()=>"?").join(",");
      const related=(await db.prepare("SELECT slug FROM xuyi_blog_posts WHERE status='published' AND slug IN ("+marksRelated+")").bind(...item.post.related).all()).results||[];
      if(unique(related.map(x=>x.slug)).length!==3)return reply({error:"Related articles are not all published: "+item.slug},409);
      const result=await scheduleBlogPost(db,{slug:item.slug,scheduledAt:item.scheduledAt,approved:true,contentJson:item.contentJson});
      scheduled.push({...result,scheduledAtLocal:item.scheduledAt,timezone:"Asia/Shanghai"});
    }
    for(const item of localePlan){
      const result=await scheduleBlogLocalePost(db,{slug:item.slug,locale:item.locale,scheduledAt:item.scheduledAt,approved:true,payloadJson:item.payloadJson});
      localeSchedules.push(result);
    }
    const saved=(await db.prepare("SELECT slug,scheduled_at,status,approved FROM xuyi_blog_schedule WHERE slug IN ("+marks+") ORDER BY scheduled_at").bind(...slugs).all()).results||[];
    const savedLocales=(await db.prepare("SELECT slug,locale,scheduled_at,status,approved FROM xuyi_blog_locale_schedule WHERE slug IN ("+marks+") ORDER BY scheduled_at,locale").bind(...slugs).all()).results||[];
    if(saved.length!==3||saved.some(x=>x.status!=="scheduled"||Number(x.approved)!==1)||savedLocales.length!==12||savedLocales.some(x=>x.status!=="scheduled"||Number(x.approved)!==1))
      return reply({error:"D1 five-language schedule verification failed"},409);
    return reply({success:true,day:DAY,timezone:"Asia/Shanghai",languages:["en",...LOCALES],scheduled,localeSchedules,verifiedRows:saved,verifiedLocaleRows:savedLocales});
  }catch(e){return reply({error:"D1 five-language schedule failed: "+String(e.message||e).slice(0,220)},500);}
}