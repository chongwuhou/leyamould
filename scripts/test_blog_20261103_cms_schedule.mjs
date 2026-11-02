import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {blogHtml,normalizeBlogPost,reviewedBlogRelatedAtEnd} from "../functions/_shared/blog-cms.js";

const posts=[1,2,3].map(i=>JSON.parse(readFileSync("data/blog-scheduled-20261103-"+i+".json","utf8")));
assert.equal(posts.length,3);
const slugs=new Set();
for(const source of posts){
  assert.ok(!slugs.has(source.slug),"Article slugs must be unique");
  slugs.add(source.slug);
  assert.equal(source.sections.length,7,source.slug);
  assert.equal(source.checklist.length,10,source.slug);
  assert.equal(source.faqs.length,4,source.slug);
  assert.equal(source.related.length,3,source.slug);
  const body=source.sections.map(s=>s.paragraph).join("\n");
  const productSlugs=[...new Set([...body.matchAll(/\]\(\/products\/([A-Za-z0-9_-]+)\//g)].map(m=>m[1]))];
  assert.equal(productSlugs.length,3,"Three distinct in-body model links: "+source.slug);
  const linkedSourceSections=source.sections.filter(s=>s.paragraph.includes("/products/")).length;
  assert.equal(linkedSourceSections,3,"Product references must be distributed across three editorial sections: "+source.slug);
  const post=normalizeBlogPost(source);
  assert.equal(post.coverAlt,source.coverAlt,"CMS must preserve the reviewed cover alt: "+source.slug);
  assert.equal(post.cover,source.cover);
  assert.equal(post.related.length,3);
  const related=reviewedBlogRelatedAtEnd(post);
  assert.equal((related.match(/class="blog-related__item"/g)||[]).length,3,"Exactly three manually selected related cards: "+source.slug);
  for(const slug of source.related)assert.ok(related.includes('href="/blog/'+slug+'/"'),"Missing related slug "+slug);
  assert.equal(reviewedBlogRelatedAtEnd({...post,relatedReading:false}),"","Respect explicit owner suppression: "+source.slug);
  const html=blogHtml(post);
  assert.ok(html.includes('alt="'+source.coverAlt+'"'),"Accurate cover alt must survive CMS normalization: "+source.slug);
  assert.equal((html.match(/class="blog-editorial__product-link"/g)||[]).length,3,"Exactly three distinct in-body model links: "+source.slug);
  assert.equal((html.match(/class="blog-related__item"/g)||[]).length,3,"Related cards render for new D1 CMS article: "+source.slug);
  assert.ok(html.indexOf('class="blog-related__item"')<html.indexOf("</article>"),"Related cards remain inside the article end: "+source.slug);
}
console.log("XUYI_20261103_THREE_B2B_CMS_ARTICLES_LINKS_RELATED_AND_COVER_ALT_PASS",posts.length);