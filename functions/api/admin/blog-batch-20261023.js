import { authorizedReviewedBlogBatchRequest } from "../../_shared/build-auth.js";
import { ensureBlogSchema } from "../../_shared/blog-cms.js";
import { bumpPublishRevision } from "../../_shared/site-settings.js";

const SLUGS = [
  "hotel-resort-reusable-water-bottle-guest-amenity-sourcing",
  "ecommerce-private-label-water-bottle-marketplace-launch-checklist",
  "wholesale-water-bottle-distributor-assortment-planning"
];
const LOCALES = ["es", "pt", "ru", "tr"];
const REVIEWED_AT = "2026-10-23";
const TAIL = "</div></div></section>";
const reply = (body, status = 200) => Response.json(body, {
  status,
  headers: { "cache-control": "no-store", "x-robots-tag": "noindex,nofollow,noarchive" }
});
const count = (value, part) => String(value).split(part).length - 1;
const unsafeHtml = /<\s*(?:script|iframe|object|embed|form|style|link|base|meta|svg|math|template)\b|\bon[a-z-]+\s*=|\bsrcdoc\s*=|(?:javascript|vbscript|data)\s*:/i;

// This batch uses already-reviewed local editorial and factory catalog images.
// Unlike the 2026-10-19 guides, these three procurement guides do not include
// a separate primary-sources section. Do not fabricate source citations just
// to satisfy an obsolete batch gate.
export function validatePayload(payload) {
  if (!payload || !Array.isArray(payload.posts) || payload.posts.length !== SLUGS.length
      || !Array.isArray(payload.translations) || payload.translations.length !== SLUGS.length * LOCALES.length
      || !Array.isArray(payload.indexCards) || payload.indexCards.length !== SLUGS.length * LOCALES.length) {
    throw new Error("The reviewed batch must contain 3 posts, 12 translations and 12 index cards.");
  }
  const expected = new Set(SLUGS);
  const seenPosts = new Set();
  for (const item of payload.posts) {
    const slug = String(item?.slug || "");
    const post = item?.post;
    if (!expected.has(slug) || seenPosts.has(slug) || post?.slug !== slug) throw new Error("Unexpected or duplicate reviewed article.");
    if (typeof post.title !== "string" || post.title.length < 12
        || typeof post.description !== "string" || post.description.length < 25
        || typeof post.intro !== "string" || post.intro.length < 50
        || !/^\/assets\/(?:blog|editorial|curated-hd|products)\/[a-z0-9-]+\.webp$/.test(String(post.cover || ""))
        || !Array.isArray(post.sections) || post.sections.length !== 7
        || !Array.isArray(post.checklist) || post.checklist.length !== 10
        || !Array.isArray(post.faqs) || post.faqs.length !== 4
        || !Array.isArray(post.related) || post.related.length !== 3
        || !Array.isArray(post.product_notes) || post.product_notes.length !== 3
        || JSON.stringify(post).length > 100000) {
      throw new Error("Reviewed article content failed validation: " + slug);
    }
    seenPosts.add(slug);
  }
  if (seenPosts.size !== expected.size) throw new Error("Reviewed article set is incomplete.");

  const seenTranslations = new Set();
  for (const item of payload.translations) {
    const route = String(item?.route || "");
    const match = /^\/blog\/([a-z0-9-]+)\/$/.exec(route);
    const locale = String(item?.locale || "");
    const key = route + "|" + locale;
    const html = String(item?.mainHtml || "");
    if (!match || !expected.has(match[1]) || !LOCALES.includes(locale) || seenTranslations.has(key)
        || String(item?.title || "").length < 12 || String(item?.description || "").length < 25
        || html.length < 5000 || html.length > 250000 || unsafeHtml.test(html)
        || count(html, 'id="primary-sources"') > 1
        || count(html, 'class="blog-section"') !== 7
        || count(html, 'class="blog-editorial__product-link"') !== 3
        || count(html, 'class="blog-related__item"') !== 3
        || count(html, 'class="blog-buyer-matrix"') !== 1
        || count(html, "<details>") !== 4) {
      throw new Error("Reviewed translation failed validation: " + key);
    }
    seenTranslations.add(key);
  }
  for (const slug of SLUGS) for (const locale of LOCALES) {
    if (!seenTranslations.has("/blog/" + slug + "/|" + locale)) throw new Error("Missing reviewed translation.");
  }

  const seenCards = new Set();
  for (const item of payload.indexCards) {
    const slug = String(item?.slug || "");
    const locale = String(item?.locale || "");
    const key = slug + "|" + locale;
    const html = String(item?.html || "");
    const href = 'href="/blog/' + slug + '/"';
    if (!expected.has(slug) || !LOCALES.includes(locale) || seenCards.has(key)
        || html.length < 100 || html.length > 10000 || unsafeHtml.test(html)
        || !html.startsWith('<article class="news-card">') || !html.endsWith("</article>")
        || count(html, href) !== 3) {
      throw new Error("Reviewed index card failed validation: " + key);
    }
    seenCards.add(key);
  }
  for (const slug of SLUGS) for (const locale of LOCALES) {
    if (!seenCards.has(slug + "|" + locale)) throw new Error("Missing reviewed index card.");
  }
}


// One-time, scope-locked correction of three source-reviewed cover collisions.
// No client-provided URLs, slugs, SQL or arbitrary blog edits are accepted.
const COVER_REPAIRS = [
 ["hotel-resort-reusable-water-bottle-guest-amenity-sourcing",
  "/assets/editorial/large-capacity-plastic-jug.webp",
  "/assets/products/jug.webp"],
 ["ecommerce-private-label-water-bottle-marketplace-launch-checklist",
  "/assets/blog/custom-product-planning-20261013.webp",
  "/assets/products/sports.webp"],
 ["wholesale-water-bottle-distributor-assortment-planning",
  "/assets/editorial/sports-bottles-category-20261013.webp",
  "/assets/products/kids.webp"]
];
function correctedIndex(source) {
  const prefix='<article class="news-card">';
  const chunks=source.split(prefix);
  for (const [slug,oldCover,newCover] of COVER_REPAIRS) {
    const needle='href="/blog/'+slug+'/"';
    let matching=0;
    for (let i=1;i<chunks.length;i++) {
      const index=chunks[i].indexOf("</article>");
      if(index<0)throw new Error("Unclosed Blog card");
      let card=chunks[i].slice(0,index),tail=chunks[i].slice(index);
      if(!card.includes(needle))continue;
      matching++;
      const old='src="'+oldCover+'"',next='src="'+newCover+'"';
      if(card.includes(old))card=card.replace(old,next);
      else if(!card.includes(next))throw new Error("Owner-edited Blog index cover; manual review required: "+slug);
      chunks[i]=card+tail;
    }
    if(matching!==1)throw new Error("Missing or duplicate approved Blog card: "+slug);
  }
  return chunks.join(prefix);
}
async function repairApprovedCovers(db) {
  try {
    await ensureBlogSchema(db);
    const rows=(await db.prepare("SELECT slug,status,content_json FROM xuyi_blog_posts WHERE slug IN (?,?,?)")
      .bind(...SLUGS).all()).results||[];
    if(rows.length!==3||rows.some(r=>r.status!=="published"))throw new Error("Reviewed Blog posts missing");
    const statements=[], updatedSlugs=[];
    for (const [slug,oldCover,newCover] of COVER_REPAIRS) {
      const row=rows.find(r=>r.slug===slug);
      if(!row)throw new Error("Unexpected missing model");
      const source=JSON.parse(row.content_json);
      if(source.cover!==oldCover && source.cover!==newCover)
        throw new Error("Owner-edited Blog cover is authoritative: "+slug);
      if(source.cover===oldCover) {
        statements.push(db.prepare("UPDATE xuyi_blog_posts SET content_json=?,updated_at=CURRENT_TIMESTAMP WHERE slug=? AND content_json=?")
          .bind(JSON.stringify({...source,cover:newCover}),slug,row.content_json));
        updatedSlugs.push(slug);
      }
    }
    const resources=COVER_REPAIRS.map(row=>"page:/blog/"+row[0]+"/");
    const translations=(await db.prepare(
      "SELECT resource_id,locale,translated_json FROM xuyi_translation_overrides WHERE resource_id IN (?,?,?,?) AND locale IN (?,?,?,?)"
    ).bind("page:/blog/",...resources,...LOCALES).all()).results||[];
    if(translations.length!==16)throw new Error("Expected 12 localized articles and four Blog index pages");
    let translatedRows=0,indexRows=0;
    for(const row of translations) {
      let content=JSON.parse(row.translated_json);
      if(typeof content.mainHtml!=="string")throw new Error("Invalid CMS translated body");
      let next=content.mainHtml;
      if(row.resource_id==="page:/blog/") {
        next=correctedIndex(next);
        if(next!==content.mainHtml)indexRows++;
      } else {
        const fixture=COVER_REPAIRS.find(x=>row.resource_id==="page:/blog/"+x[0]+"/");
        if(!fixture)throw new Error("Unexpected locale Blog row");
        const [,oldCover,newCover]=fixture;
        const begin='<div class="blog-detail__cover"><img src="';
        const oldHero=begin+oldCover+'"',newHero=begin+newCover+'"';
        if(next.includes(oldHero))next=next.replace(oldHero,newHero);
        else if(!next.includes(newHero))throw new Error("Owner-modified localized Blog hero; no automatic rewrite");
        if(next!==content.mainHtml)translatedRows++;
      }
      if(next!==content.mainHtml) {
        statements.push(db.prepare(
          "UPDATE xuyi_translation_overrides SET translated_json=?,reviewed_at=? WHERE resource_id=? AND locale=? AND translated_json=?"
        ).bind(JSON.stringify({...content,mainHtml:next}),REVIEWED_AT,row.resource_id,row.locale,row.translated_json));
      }
    }
    if(!statements.length)return reply({success:true,alreadyFixed:true,updatedSlugs:[],translatedRows:0,indexRows:0});
    const result=await db.batch(statements);
    if(result.some(r=>Number(r?.meta?.changes||0)!==1))
      throw new Error("D1 optimistic cover repair conflict; investigate before retry");
    const revision=await bumpPublishRevision(db);
    return reply({success:true,updatedSlugs,translatedRows,indexRows,publishRevision:revision.revision});
  }catch(error){
    return reply({error:"Reviewed cover repair not applied: "+String(error?.message||"unknown").slice(0,180)},409);
  }
}

export async function onRequestPost(context) {
  if (!(await authorizedReviewedBlogBatchRequest(context.request, context.env))) {
    return reply({ error: "Unauthorized reviewed batch request" }, 401);
  }
  const db = context.env.XUYI_DB;
  if (!db) return reply({ error: "XUYI_DB binding missing" }, 503);

  let payload;
  try { payload = await context.request.json(); }
  catch { return reply({ error: "Invalid JSON" }, 400); }
  // Only this exact, one-time reviewed cover correction can run before normal batch validation.
  if(payload?.fixApprovedCovers===true && Object.keys(payload).length===1)
    return repairApprovedCovers(db);
  try { validatePayload(payload); }
  catch (error) { return reply({ error: String(error?.message || "Invalid reviewed batch").slice(0, 240) }, 400); }

  try {
    await ensureBlogSchema(db);
    const statements = [];
    const postSql = "INSERT INTO xuyi_blog_posts (slug,status,content_json,published_at,updated_at) VALUES(?,'published',?,?,CURRENT_TIMESTAMP) ON CONFLICT(slug) DO NOTHING";
    for (const item of payload.posts) {
      statements.push(db.prepare(postSql).bind(item.slug, JSON.stringify(item.post), "2026-10-23T00:00:00Z"));
    }
    const translationSql = "INSERT INTO xuyi_translation_overrides (resource_id,locale,translated_json,reviewed_at) VALUES(?,?,?,?) ON CONFLICT(resource_id,locale) DO NOTHING";
    for (const item of payload.translations) {
      const content = JSON.stringify({ title: item.title, description: item.description, mainHtml: item.mainHtml });
      statements.push(db.prepare(translationSql).bind("page:" + item.route, item.locale, content, REVIEWED_AT));
    }
    const indexSql = "UPDATE xuyi_translation_overrides SET translated_json=json_set(translated_json,'$.mainHtml',substr(json_extract(translated_json,'$.mainHtml'),1,length(json_extract(translated_json,'$.mainHtml'))-length(?))||?||?), reviewed_at=? WHERE resource_id='page:/blog/' AND locale=? AND substr(json_extract(translated_json,'$.mainHtml'),-length(?))=? AND instr(json_extract(translated_json,'$.mainHtml'),?)=0";
    for (const item of payload.indexCards) {
      const href = "/blog/" + item.slug + "/";
      statements.push(db.prepare(indexSql).bind(TAIL, item.html, TAIL, REVIEWED_AT, item.locale, TAIL, TAIL, href));
    }

    const results = await db.batch(statements);
    const postsInserted = results.slice(0, SLUGS.length)
      .reduce((sum, row) => sum + Number(row?.meta?.changes || 0), 0);
    const translationsInserted = results.slice(SLUGS.length, SLUGS.length + payload.translations.length)
      .reduce((sum, row) => sum + Number(row?.meta?.changes || 0), 0);
    const indexCardsAdded = results.slice(SLUGS.length + payload.translations.length)
      .reduce((sum, row) => sum + Number(row?.meta?.changes || 0), 0);

    const posts = (await db.prepare(
      "SELECT slug,status FROM xuyi_blog_posts WHERE slug IN (?,?,?)"
    ).bind(...SLUGS).all()).results || [];
    if (new Set(posts.filter(row => row.status === "published").map(row => row.slug)).size !== SLUGS.length) {
      return reply({ error: "Final D1 check failed: all three reviewed articles are not published." }, 409);
    }

    const resources = ["page:/blog/", ...SLUGS.map(slug => "page:/blog/" + slug + "/")];
    const rows = (await db.prepare(
      "SELECT resource_id,locale,translated_json FROM xuyi_translation_overrides WHERE resource_id IN (?,?,?,?) AND locale IN (?,?,?,?)"
    ).bind(...resources, ...LOCALES).all()).results || [];
    const lookup = new Map(rows.map(row => [row.resource_id + "|" + row.locale, row]));
    for (const slug of SLUGS) for (const locale of LOCALES) {
      const row = lookup.get("page:/blog/" + slug + "/|" + locale);
      if (!row) return reply({ error: "Final D1 check failed: missing article translation." }, 409);
      let body = "";
      try { body = JSON.parse(row.translated_json).mainHtml || ""; } catch {}
      if (body.length < 5000 || count(body, 'id="primary-sources"') > 1
          || count(body, 'class="blog-section"') !== 7
          || count(body, 'class="blog-editorial__product-link"') !== 3
          || count(body, 'class="blog-related__item"') !== 3
          || count(body, 'class="blog-buyer-matrix"') !== 1 || count(body, "<details>") !== 4) {
        return reply({ error: "Final D1 check failed: reviewed article translation is incomplete." }, 409);
      }
    }
    for (const locale of LOCALES) {
      const row = lookup.get("page:/blog/|" + locale);
      if (!row) return reply({ error: "Final D1 check failed: missing localized Blog index." }, 409);
      let body = "";
      try { body = JSON.parse(row.translated_json).mainHtml || ""; } catch {}
      for (const slug of SLUGS) {
        const cards = body.split('<article class="news-card">').slice(1)
          .map(part => '<article class="news-card">' + part.split("</article>", 1)[0] + "</article>")
          .filter(card => card.includes("/blog/" + slug + "/"));
        if (cards.length !== 1 || count(cards[0], 'href="/blog/' + slug + '/"') !== 3) {
          return reply({ error: "Final D1 check failed: localized Blog index card is missing or duplicated." }, 409);
        }
      }
    }

    const revision = await bumpPublishRevision(db);
    return reply({
      success: true,
      postsInserted,
      translationsInserted,
      indexCardsAdded,
      publishRevision: revision.revision,
      publishedSlugs: SLUGS
    });
  } catch (error) {
    return reply({ error: "D1 batch operation failed: " + String(error?.message || "unknown error").slice(0, 180) }, 500);
  }
}
