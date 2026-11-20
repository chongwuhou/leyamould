import assert from "node:assert/strict";
import {withInformationalIntent} from "../functions/blog/[[path]].js";
import {blogHtml,composePage} from "../functions/_shared/blog-cms.js";
import ROLE from "../data/search-intent-three-landing-roles.json" with {type:"json"};

const role=ROLE.languages.en.blog;
const source={
 slug:"sports-water-bottle-customization",title:role.baseline.title,description:role.baseline.description,
 intro:"A sourcing guide explaining how bottle lids, carrying features, capacity and logo artwork affect samples.",
 updated:"2026-10-09",cover:"/media/ppt/slide-030.webp",sections:[],checklist:[],faqs:[]
};
const revised=withInformationalIntent(source);
assert.equal(revised.title,role.preferred.title);
assert.equal(revised.description,role.preferred.description);
assert.equal(source.title,role.baseline.title);
assert(blogHtml(revised).includes("<h1>"+role.preferred.title+"</h1>"));
const customTitle=withInformationalIntent({...source,title:"OWNER ALTERNATE TITLE"});
assert.equal(customTitle.title,"OWNER ALTERNATE TITLE");
assert.equal(customTitle.description,source.description);
const customDesc=withInformationalIntent({...source,description:"OWNER ALTERNATE DESCRIPTION"});
assert.equal(customDesc.description,"OWNER ALTERNATE DESCRIPTION");
assert.equal(customDesc.title,source.title);
assert.deepEqual(withInformationalIntent({...source,slug:"another-post"}),{...source,slug:"another-post"});
assert.deepEqual(withInformationalIntent(revised),revised);
const shell='<html><head><title>Old</title><meta name="description" content="Old"><link rel="canonical" href="https://leyamould.com/blog/sports-water-bottle-customization/"></head><body><main id="main-content">Old</main></body></html>';
const html=composePage(shell,blogHtml(revised),revised,"/blog/sports-water-bottle-customization/");
assert(html.includes("<title>"+role.preferred.title+"</title>"));
assert(html.includes("<h1>"+role.preferred.title+"</h1>"));
console.log("XUYI_DYNAMIC_D1_BLOG_INFORMATION_INTENT_OWNER_PASSED");
