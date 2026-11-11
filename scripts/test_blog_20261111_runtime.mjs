import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {blogHtml,normalizeBlogPost,reviewedBlogRelatedAtEnd} from '../functions/_shared/blog-cms.js';
for(let i=1;i<=3;i++){
  const src=JSON.parse(readFileSync('data/blog-guides-20261111-'+i+'.json','utf8'));
  assert.equal(src.product_notes.length,3);
  assert.equal(src.related.length,3);
  const post={...src,status:'published',published_at:'2026-11-11T00:00:00Z'};
  const html=blogHtml(post);
  assert.equal((html.match(/class="blog-editorial__product-link"/g)||[]).length,3,src.slug);
  assert.equal((html.match(/class="blog-related__item"/g)||[]).length,3,src.slug);
  assert.equal((html.match(/class="blog-section"/g)||[]).length,7);
  assert.equal((html.match(/<details>/g)||[]).length,4);
  assert.ok(html.includes('src="'+src.cover+'"'),src.slug);
  assert.ok(html.includes('alt="'+src.coverAlt+'"'),src.slug);
  assert.ok(html.includes('Published 2026-11-11'),src.slug);
  for(const n of src.product_notes)assert.ok(html.includes('href="/products/'+n.sku+'/"'),n.sku);
  for(const slug of src.related)assert.ok(html.includes('href="/blog/'+slug+'/"'),slug);
  assert.equal(reviewedBlogRelatedAtEnd({...post,relatedReading:false}),'');
  assert.equal((blogHtml({...post,product_notes:[]}).match(/class="blog-editorial__product-link"/g)||[]).length,0);
  const revised={...post,sections:post.sections.map((s,i)=>i===0?{...s,paragraph:s.paragraph+' Owner edit preserved.'}:s)};
  assert.ok(blogHtml(revised).includes('Owner edit preserved.'));
  const normalized=normalizeBlogPost(src);
  assert.equal(normalized.coverAlt,src.coverAlt);
}
console.log('XUYI_20261111_THREE_LIVE_D1_DYNAMIC_ARTICLE_OWNER_EDITS_AND_LINKS_PASS');