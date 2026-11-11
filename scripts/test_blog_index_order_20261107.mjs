import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {sortLocalizedBlogIndexByD1Order} from '../functions/_shared/blog-cms.js';
const fixture=JSON.parse(readFileSync('scripts/fixtures/blog-index-order-baseline-20261107.json','utf8'));
const endpoint=readFileSync('functions/api/admin/blog-batch.js','utf8');
assert.ok(/listBlogPosts\(db,\s*["']published["']\)/.test(endpoint),'batch must use the shared D1 live-list query');
assert.ok(endpoint.includes('sortLocalizedBlogIndexByD1Order') && endpoint.includes('d1Order'),'all localized indexes must follow the full D1 order');
assert.ok(endpoint.includes('configuredLocales(languageConfig)'),'the endpoint must read publish-ready locales from D1');
assert.ok(endpoint.includes('indexOrderVerified: locales') || endpoint.includes('indexOrderVerified:locales'),'the endpoint must verify every configured locale');
assert.ok(!endpoint.includes('const LANGS='),'the generic endpoint must not hardcode a locale list');
assert.ok(!endpoint.includes('moveLocalizedBlogCardsToFront'),'no hardcoded batch-first repair is allowed');
assert.ok(endpoint.includes('const d1Order') && endpoint.includes('listBlogPosts(db, "published")'),'the endpoint must derive order from the D1 result');
assert.ok(endpoint.indexOf('sortLocalizedBlogIndexByD1Order') < endpoint.indexOf('bumpPublishRevision'),'ordering must be verified before the publish revision bump');
const expected=fixture.live_order_before_repair.en;
const batch=new Set(fixture.batch_slugs);
assert.equal(expected.length,76);
assert.equal(new Set(expected).size,76);
assert.deepEqual(new Set(expected.slice(0,3)),batch);
assert.deepEqual(expected.slice(3),fixture.existing_73_order);
function card(locale,slug,index){
 const prefix=locale==='en'?'':locale+'/';
 const href='/'+prefix+'blog/'+slug+'/';
 const marker='OWNER_LOCALIZED_CARD_'+locale+'_'+index+'_'+slug;
 return '<article class="news-card"><a href="'+href+'" class="news-card__image"><img src="/owner/'+locale+'/'+index+'.webp" alt="'+marker+'"></a><div class="news-card__info"><h3><a href="'+href+'">'+marker+'</a></h3><p>'+marker+'_DESCRIPTION</p><a href="'+href+'">Read Article</a></div></article>';
}
function html(locale,order){
 return '<section class="section blog-listing"><div class="shell"><div class="blog-listing__grid">\n'+order.map((slug,i)=>card(locale,slug,i)).join('\n')+'\n</div></div></section>';
}
function parse(source){
 return [...source.matchAll(/<article class="news-card">[\s\S]*?<\/article>/g)].map(m=>{
  const links=[...m[0].matchAll(/href="\/(?:(?:en|es|pt|ru|tr)\/)?blog\/([a-z0-9]+(?:-[a-z0-9]+)*)\/"/g)].map(x=>x[1]);
  assert.equal(links.length,3);
  assert.equal(new Set(links).size,1);
  return {slug:links[0],html:m[0]};
 });
}
for(const locale of ['es','pt','ru','tr']){
 const beforeOrder=fixture.live_order_before_repair[locale];
 const before=html(locale,beforeOrder);
 const originalCards=new Map(parse(before).map(x=>[x.slug,x.html]));
 assert.deepEqual(beforeOrder.filter(slug=>!batch.has(slug)),fixture.existing_73_order,locale);
 const sorted=sortLocalizedBlogIndexByD1Order(before,expected);
 const result=parse(sorted);
 assert.deepEqual(result.map(x=>x.slug),expected,locale);
 for(const row of result)assert.equal(row.html,originalCards.get(row.slug),'Localized card content changed: '+locale+' '+row.slug);
 assert.equal(sortLocalizedBlogIndexByD1Order(sorted,expected),sorted,'sorting must be idempotent');
 const reversed=sortLocalizedBlogIndexByD1Order(sorted,[...expected].reverse());
 assert.deepEqual(parse(reversed).map(x=>x.slug),[...expected].reverse(),'order must follow the supplied D1 result, not hardcoded slugs');
 assert.ok(sorted.startsWith('<section class="section blog-listing">'));
 assert.ok(sorted.endsWith('</div></div></section>'));
}
assert.throws(()=>sortLocalizedBlogIndexByD1Order(html('es',expected.slice(0,-1)),expected),/card count differs/);
assert.throws(()=>sortLocalizedBlogIndexByD1Order(html('es',[...expected.slice(0,-1),expected[0]]),expected),/Duplicate localized Blog card/);
assert.throws(()=>sortLocalizedBlogIndexByD1Order(html('es',expected),[...expected,expected[0]]),/invalid or duplicate slug/);
const clean=html('es',expected);
const malformed=clean.replace('<article class="news-card">','<article class="news-card"><div class="legacy-card-wrapper">').replace('</article>','</article></div></article>');
const repaired=sortLocalizedBlogIndexByD1Order(malformed,expected);
assert.equal((repaired.match(/<article class="news-card">/g)||[]).length,expected.length,'historical nested wrappers must be removed');
assert.deepEqual(parse(repaired).map(x=>x.slug),expected,'historical malformed card records must recover in D1 order');
console.log('XUYI_20261107_LOCALIZED_BLOG_CARDS_FOLLOW_FULL_D1_ORDER_AND_PRESERVE_ALL_CARD_HTML');

