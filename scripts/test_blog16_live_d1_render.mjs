import assert from "node:assert/strict";
import GUIDES from "../data/blog-guides.json" with {type:"json"};
import PART1 from "../data/blog-inline-edits-reviewed-part1.json" with {type:"json"};
import PART2 from "../data/blog-inline-edits-reviewed-part2.json" with {type:"json"};
import {blogHtml,reviewedBlogParagraphNote,reviewedBlogRelatedAtEnd} from "../functions/_shared/blog-cms.js";
const changes={...PART1,...PART2};
assert.equal(Object.keys(changes).length,GUIDES.length);
for(const post of GUIDES){
 const authored=changes[post.slug];
 assert.equal(authored.length,2,post.slug);
 const actual=blogHtml(post);
 assert.equal((actual.match(/data-editorial-model="/g)||[]).length,2,post.slug);
 assert.equal((actual.match(/class="blog-related__item"/g)||[]).length,3,post.slug);
 assert.equal((actual.match(/class="section section--soft blog-related"/g)||[]).length,1,post.slug);
 const paragraphPositions=[];
 for(const item of authored){
  const expected='/products/'+item.sku+'/';
  const marker='data-editorial-model="'+item.sku+'"';
  assert(actual.includes(marker),post.slug+':'+item.sku);
  assert(actual.includes('href="'+expected+'"'),post.slug+':'+item.sku);
  paragraphPositions.push(actual.indexOf(marker));
  const opening='<section class="blog-section" id="article-section-'+item.section+'">';
  const start=actual.indexOf(opening),end=actual.indexOf('</section>',start);
  assert(start>=0&&actual.slice(start,end).includes(marker),'not in reviewed paragraph '+post.slug);
 }
 assert(paragraphPositions[0]!==paragraphPositions[1],post.slug);
 assert(actual.indexOf('class="blog-related__item"')>actual.indexOf('class="blog-editorial__cta"'),post.slug);
 assert(actual.indexOf('class="blog-related__item"')<actual.indexOf('</article>'),post.slug);
 for(const related of post.related)assert(actual.includes('href="/blog/'+related+'/"'),post.slug+':'+related);
 const ownerIntro={...post,intro:post.intro+' (reviewed by CMS)'};
 assert.equal((blogHtml(ownerIntro).match(/data-editorial-model="/g)||[]).length,0,post.slug+':owner intro');
 for(const item of authored){
  const modified={...post,sections:post.sections.map((v,i)=>i===item.section?{...v,paragraph:v.paragraph+' CMS editor changed this.'}:v)};
  assert.equal(reviewedBlogParagraphNote(modified,modified.sections[item.section],item.section),"",post.slug+':owner paragraph');
  assert(blogHtml(modified).includes('CMS editor changed this.'),post.slug);
 }
 const newRelated={...post,related:[post.related[1],post.related[0]]};
 const swapped=blogHtml(newRelated);
 assert.equal((swapped.match(/class="blog-related__item"/g)||[]).length,2);
 assert(swapped.indexOf('/blog/'+post.related[1]+'/')<swapped.indexOf('/blog/'+post.related[0]+'/'));
 const legacyNoRelated={...post,related:[]};
 assert.equal((blogHtml(legacyNoRelated).match(/class="blog-related__item"/g)||[]).length,3,post.slug+':legacy D1 fallback');
 assert.equal(reviewedBlogRelatedAtEnd({...post,related:[],relatedReading:false}),"",post.slug+':owner explicit optout');
 assert.equal(reviewedBlogRelatedAtEnd({...ownerIntro,related:[]}),"",post.slug+':owner intro edit');
}
const newArticle={...GUIDES[0],slug:"a-new-2027-guide",related:[],sections:[...GUIDES[0].sections]};
assert.equal((blogHtml(newArticle).match(/data-editorial-model="/g)||[]).length,0);
assert.equal((blogHtml(newArticle).match(/class="blog-related__item"/g)||[]).length,0);
console.log("XUYI_ENGLISH_D1_RUNTIME_16_POSTS_WITH_NATURAL_SKU_LINKS_END_RELATED_OWNER_FIRST_PASSED",GUIDES.length);