import assert from "node:assert/strict";
import GUIDES from "../data/blog-guides.json" with {type:"json"};
import P1 from "../data/blog-inline-edits-reviewed-part1.json" with {type:"json"};
import P2 from "../data/blog-inline-edits-reviewed-part2.json" with {type:"json"};
import {blogHtml,renderEditableParagraph} from "../functions/_shared/blog-cms.js";
const reviewed={...P1,...P2};
assert.equal(Object.keys(reviewed).length,16);
for(const post of GUIDES){
 const source=reviewed[post.slug];
 assert.equal(source.length,2);
 const updated=structuredClone(post);
 for(const note of source){
  updated.sections[note.section].paragraph+=" "+note.text.en.replace("{model}","[model "+note.sku+"](/products/"+note.sku+"/)");
 }
 const html=blogHtml(updated);
 assert.equal((html.match(/class="blog-editorial__product-link"/g)||[]).length,2,post.slug);
 assert.equal((html.match(/data-editorial-model="/g)||[]).length,0,post.slug);
 assert.equal((html.match(/class="blog-related__item"/g)||[]).length,3,post.slug);
 assert(html.indexOf('class="blog-related__item"')<html.indexOf('</article>'),post.slug);
 for(const note of source){
  const s='<section class="blog-section" id="article-section-'+note.section+'">';
  const begin=html.indexOf(s),end=html.indexOf("</section>",begin);
  assert(begin>=0&&end>begin);
  const part=html.slice(begin,end);
  assert(part.includes('href="/products/'+note.sku+'/"'),post.slug);
 }
}
assert.equal(renderEditableParagraph("A <script>alert(1)</script>"),"A &lt;script&gt;alert(1)&lt;/script&gt;");
assert(!renderEditableParagraph("[external](https://evil.example/)").includes("<a "));
assert(!renderEditableParagraph("[img](/media/image.webp)").includes("<a "));
assert(!renderEditableParagraph("[bad](/products/../../)").includes("<a "));
assert(renderEditableParagraph("[Model 2095](/products/2095/)").includes('href="/products/2095/"'));
console.log("XUYI_D1_EDITORIAL_MARKDOWN_16_POSTS_RENDER_AS_SAFE_NATURAL_INLINE_LINKS_PASSED");
