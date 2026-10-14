// XUYI Blog CMS extends Demalong's D1-backed page-editor and revision approach.
// Match the separately reviewed static Blog sources on D1-backed live routes.
import EDITORIAL_EVIDENCE from "../../data/editorial-evidence.json" with {type:"json"};
import BUYER_PATHWAYS from "../../data/blog-buyer-pathways.json" with {type:"json"};
import BLOG_FEATURE_PATHWAYS from "../../data/blog-feature-pathways.json" with {type:"json"};
export const esc = value => String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
function verifiedEvidence(post){
 const evidence=EDITORIAL_EVIDENCE[post?.slug];
 if(!evidence)return "";
 const sourceLinks=evidence.sources.filter(s=>
  /^https:\/\/(?:www\.fda\.gov|eur-lex\.europa\.eu|www\.iso\.org)\//.test(s.url))
  .map(s=>'<li><a href="'+esc(s.url)+'" target="_blank" rel="noopener noreferrer">'+esc(s.label)+' ↗</a></li>').join("");
 if(sourceLinks.length===0)return "";
 return '<section class="blog-evidence" id="primary-sources" aria-labelledby="primary-sources-heading"><span class="eyebrow">SOURCE-CHECKED BUYER NOTES</span><h2 id="primary-sources-heading">'+esc(evidence.title)+'</h2><p>'+esc(evidence.insight)+'</p><p><strong>Practical next step:</strong> '+esc(evidence.next_step)+'</p><h3>Primary references</h3><ul>'+sourceLinks+'</ul><p class="blog-evidence__caveat">External regulations and standards are independent references, not product certification or proof of testing by XUYI. Confirm applicability and the latest rules for the exact product, destination and transaction date.</p></section>';
}
function contentModifiedDate(post){
 const value=String(post?.updated||"").slice(0,10);
 return EDITORIAL_EVIDENCE[post?.slug] && value<"2026-10-10"?"2026-10-10":value;
}
function actualPublishedDate(post){
 const raw=String(post?.published_at||post?.updated||"").slice(0,10);
 return /^\d{4}-\d{2}-\d{2}$/.test(raw)?raw:"";
}
export async function ensureBlogSchema(db){
 await db.prepare("CREATE TABLE IF NOT EXISTS xuyi_blog_posts (slug TEXT PRIMARY KEY,status TEXT NOT NULL DEFAULT 'draft',content_json TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,published_at TEXT)").run();
 await db.prepare("CREATE INDEX IF NOT EXISTS idx_xuyi_blog_status ON xuyi_blog_posts(status,updated_at)").run();
 await db.prepare("CREATE TABLE IF NOT EXISTS xuyi_blog_drafts (slug TEXT PRIMARY KEY,draft_json TEXT NOT NULL,updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)").run();
}
const str=(x,max=300)=>String(x??'').trim().slice(0,max);
const slugOk=x=>/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(x)&&x.length<=120;
const IMAGE=/^(\/media\/(?:ppt\/slide-\d{3}\.webp|excel\/row-\d{3}\.webp|group\/[a-z0-9-]+\.webp|blog\/[a-z0-9_-]+\.(?:webp|png|jpg|jpeg))|\/assets\/[a-zA-Z0-9/_-]+\.(?:webp|png|jpg|jpeg))$/;
export function normalizeBlogPost(raw){
 const slug=str(raw?.slug,140).toLowerCase();if(!slugOk(slug))throw Error('Invalid slug.');
 const title=str(raw?.title,125),description=str(raw?.description,250),intro=str(raw?.intro,2000);
 if(title.length<12||description.length<25||intro.length<50)throw Error('Title, description and introduction must be substantive.');
 const cover=str(raw?.cover,220);if(!IMAGE.test(cover))throw Error('Use a local XUYI image path.');
 const items=raw?.sections;
 if(!Array.isArray(items)||items.length<2||items.length>24)throw Error('Please write 2–24 article sections.');
 const sections=items.map(s=>({heading:str(s?.heading,140),paragraph:str(s?.paragraph,4200)}));
 if(sections.some(s=>s.heading.length<5||s.paragraph.length<60))throw Error('Each section needs a heading and paragraph.');
 const faqs=(Array.isArray(raw?.faqs)?raw.faqs:[]).slice(0,12).map(q=>({question:str(q?.question,220),answer:str(q?.answer,1500)}));
 if(faqs.some(x=>!x.question||!x.answer))throw Error('FAQ questions and answers must be complete.');
 const checklist=(Array.isArray(raw?.checklist)?raw.checklist:[]).slice(0,16).map(v=>str(v,300)).filter(Boolean);
 const related=(Array.isArray(raw?.related)?raw.related:[]).slice(0,5).map(x=>str(x,120)).filter(slugOk).filter(x=>x!==slug);
 const group=str(raw?.group,70)||'Buyer Resources',updated=new Date().toISOString().slice(0,10);
 const primary_keyword=str(raw?.primary_keyword,110),secondary_keywords=(Array.isArray(raw?.secondary_keywords)?raw.secondary_keywords:[]).slice(0,12).map(v=>str(v,110)).filter(Boolean);
 return {slug,title,description,intro,cover,sections,faqs,checklist,related,group,category:'Buyer Resources',primary_keyword,secondary_keywords,updated};
}
export async function listBlogPosts(db,status=''){
 await ensureBlogSchema(db);
 const st=status?db.prepare('SELECT * FROM xuyi_blog_posts WHERE status=? ORDER BY updated_at DESC').bind(status):db.prepare('SELECT * FROM xuyi_blog_posts ORDER BY updated_at DESC');
 const rows=(await st.all()).results||[];
 const saved=(await db.prepare('SELECT slug FROM xuyi_blog_drafts').all()).results||[];
 const hasDraft=new Set(saved.map(x=>x.slug));
 return rows.map(row=>{
  let post={};try{post=JSON.parse(row.content_json)}catch{}
  return {...post,slug:row.slug,status:row.status,updated_at:row.updated_at,published_at:row.published_at,has_draft:hasDraft.has(row.slug)};
 });
}
export async function findBlogPost(db,slug){
 await ensureBlogSchema(db);
 const row=await db.prepare('SELECT * FROM xuyi_blog_posts WHERE slug=?').bind(slug).first();
 if(!row)return null;
 let post;try{post=JSON.parse(row.content_json)}catch{return null}
 return {...post,status:row.status,updated_at:row.updated_at,published_at:row.published_at};
}
export async function findEditableBlogPost(db,slug){
 const post=await findBlogPost(db,slug);
 if(!post)return null;
 const draft=await db.prepare('SELECT draft_json FROM xuyi_blog_drafts WHERE slug=?').bind(slug).first();
 if(!draft)return post;
 try{return {...JSON.parse(draft.draft_json),status:post.status,isDraftVersion:true,slug,published_at:post.published_at}}
 catch{return post}
}
export function blogHtml(post){
 let body='<section class="page-intro"><div class="shell"><div class="breadcrumb"><a href="/">Home</a> / <a href="/blog/">Blog</a> / Buying Guide</div><span class="eyebrow">XUYI · PLASTIC DRINKWARE</span><h1>'+esc(post.title)+'</h1><p>'+esc(post.description)+'</p></div></section>';
 body+='<section class="section blog-editorial"><div class="shell"><div class="blog-detail__cover"><img src="'+esc(post.cover)+'" alt="'+esc(post.coverAlt||post.title)+'" loading="eager"></div><div class="blog-editorial__layout"><aside class="blog-editorial__aside"><div class="blog-toc"><span class="eyebrow">IN THIS GUIDE</span><nav aria-label="Article sections">';
 for(let i=0;i<post.sections.length;i++)body+='<a href="#article-section-'+i+'">'+esc(post.sections[i].heading)+'</a>';
 const published=actualPublishedDate(post),modified=contentModifiedDate(post);
 const timeline=(published?'<time datetime="'+esc(published)+'">Published '+esc(published)+'</time>':'')+
   (modified&&modified>published?' · <time datetime="'+esc(modified)+'">Reviewed '+esc(modified)+'</time>':'');
 body+='</nav><a class="blog-toc__quote" href="/contact/#inquiry">Discuss your project →</a></div></aside><article class="article blog-editorial__body"><div class="blog-meta"><span>BUYER RESOURCES</span><span>'+timeline+'</span></div><p class="blog-lede">'+esc(post.intro)+'</p>';
 if(post.checklist?.length){body+='<div class="blog-takeaway"><strong>Before requesting a quote</strong><ul>';for(const tip of post.checklist.slice(0,3))body+='<li>'+esc(tip)+'</li>';body+='</ul></div>'}
 post.sections.forEach((section,i)=>{body+='<section class="blog-section" id="article-section-'+i+'"><h2>'+esc(section.heading)+'</h2><p>'+esc(section.paragraph)+'</p></section>'});
 body+=verifiedEvidence(post);
 if(post.checklist?.length){body+='<section class="blog-checklist"><h2>Buyer checklist</h2><ul>';for(const tip of post.checklist)body+='<li>'+esc(tip)+'</li>';body+='</ul></section>'}
 if(post.faqs?.length){body+='<section class="blog-faq"><h2>Frequently asked questions</h2>';for(const q of post.faqs)body+='<details><summary>'+esc(q.question)+'</summary><p>'+esc(q.answer)+'</p></details>';body+='</section>'}
 body+='<div class="blog-editorial__cta"><h2>Need a quote for a specific model?</h2><p>Send the model, expected order quantity, logo requirements and destination market. XUYI can review confirmed material and customization options.</p><a class="button" href="/contact/#inquiry">Request a Plastic Bottle Quote →</a></div>';
 // The live EN article comes from D1, unlike reviewed translated static
 // articles. Derive the extra reader link from the same shared 9-post map
 // used by the static build; never overwrite any stored D1 article content.
 const destination=BUYER_PATHWAYS[post.slug];
 if(destination){
  const allowed={
   "collections/sports-water-bottles":"Compare plastic sports water bottles",
   "collections/kids-water-bottles":"Browse children's bottle models",
   "capabilities/custom-water-bottle":"Review custom plastic bottle options",
   "request-sample":"Plan a product sample request",
   "features/straw-lid":"Explore straw-lid bottle designs",
   "capabilities/oem-odm":"Compare OEM and ODM services"
  };
  if(!Object.hasOwn(allowed,destination))throw Error("Unknown editorial link target");
  body+='<section class="seo-next-buyer"><h2>Continue your sourcing research</h2><p>View this related product or buying guide: <a href="/'+esc(destination)+'/">'+esc(allowed[destination])+' →</a></p></section>';
 }
 body+='</article></div></div></section>';
 // D1 replaces the built English article's <main>, so this must share the
 // same source mapping as the static five-language builder. Append *outside*
 // the article, retaining the original approved page layout and D1 content.
 const features=BLOG_FEATURE_PATHWAYS["blog/"+post.slug]||[];
 if(features.length){
  const labels={
   "applications/everyday-hydration":"Everyday hydration applications",
   "applications/kids-school":"Kids and school bottle applications",
   "applications/outdoor-travel":"Outdoor and travel applications",
   "applications/promotional-gifts":"Promotional gift bottle applications",
   "features/large-capacity":"Large-capacity bottle designs",
   "features/carry-handle":"Carry-handle bottle options",
   "features/gradient-colors":"Gradient-color bottle options",
   "features/straw-lid":"Straw-lid bottle options"
  };
  let links="";
  for(const target of features){
   if(!Object.hasOwn(labels,target))throw Error("Unexpected curated feature pathway");
   links+='<a href="/'+esc(target)+'/">'+esc(labels[target])+' →</a>';
  }
  body+='<section class="section buyer-pathways" aria-label="Explore related bottle choices"><div class="shell"><h2>Explore related bottle choices</h2><p>Compare bottle use cases and design features before selecting a specific model.</p><div class="buyer-pathways__links">'+links+'</div></div></section>';
 }
 return body;
}
export function blogCard(post){
 const url='/blog/'+post.slug+'/';
 return '<article class="news-card"><a href="'+url+'" class="news-card__image"><img src="'+esc(post.cover)+'" alt="'+esc(post.coverAlt||post.title)+'" loading="lazy"></a><div class="news-card__info"><span class="news-card__category">'+esc((post.group||'Buyer Resources').toUpperCase())+'</span><h3><a href="'+url+'">'+esc(post.title)+'</a></h3><p>'+esc(post.description)+'</p><a class="news-card__read" href="'+url+'">Read Article →</a></div></article>';
}
export function composePage(template,body,post,route){
 if(!template.includes('<main id="main-content">'))throw Error('Blog page template missing');
 let html=template.replace(/<main id="main-content">[\s\S]*?<\/main>/,'<main id="main-content">'+body+'</main>');
 if(post){
  const url='https://xuyibottles.com'+route;
  html=html.replace(/<title>[\s\S]*?<\/title>/,'<title>'+esc(post.title)+'</title>');
  html=html.replace(/<meta name="description" content="[^"]*">/,'<meta name="description" content="'+esc(post.description)+'">');
  html=html.replace(/<link rel="canonical" href="[^"]*">/,'<link rel="canonical" href="'+esc(url)+'">');
  html=html.replace(/<meta property="og:url" content="[^"]*">/,'<meta property="og:url" content="'+esc(url)+'">');
  const social=[['og:title',post.title],['og:description',post.description]];
  for(const [key,value] of social){
   const tag='<meta property="'+key+'" content="'+esc(value)+'">';
   const match=new RegExp('<meta property="'+key+'" content="[^"]*">');
   html=match.test(html)?html.replace(match,tag):html.replace('</head>',tag+'</head>');
  }
  html=html.replace(/<meta property="og:image" content="[^"]*">/,'');
  html=html.replace(/<script type="application\/ld\+json">[\s\S]*?<\/script>/g,'');
  const graph={'@context':'https://schema.org','@type':'BlogPosting',headline:post.title,description:post.description,inLanguage:'en',dateModified:contentModifiedDate(post),mainEntityOfPage:url,publisher:{'@type':'Organization',name:'XUYI Bottles'},image:['https://xuyibottles.com'+post.cover]};
  if(actualPublishedDate(post))graph.datePublished=actualPublishedDate(post);
  if(EDITORIAL_EVIDENCE[post.slug])graph.citation=EDITORIAL_EVIDENCE[post.slug].sources
    .filter(s=>/^https:\/\/(?:www\.fda\.gov|eur-lex\.europa\.eu|www\.iso\.org)\//.test(s.url))
    .map(s=>({'@type':'CreativeWork',name:s.label,url:s.url}));
  const safe=JSON.stringify(graph).replace(/</g,'\\u003c');
  html=html.replace('</head>','<meta property="og:image" content="'+esc('https://xuyibottles.com'+post.cover)+'"><script type="application/ld+json">'+safe+'</script></head>');
 }
 return html;
}