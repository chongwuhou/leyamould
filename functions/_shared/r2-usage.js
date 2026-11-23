// Protected LEYA R2 image usage checks. Fail closed when checks are unavailable.
export const KINDS={
  product:{prefix:"site-media/product/",editable:true},
  page:{prefix:"site-media/page/",editable:true},
  shared:{prefix:"site-media/shared/",editable:true},
  ppt:{prefix:"catalog-staging/ppt/",editable:false},
  excel:{prefix:"site-preview/excel/",editable:false},
  group:{prefix:"site-preview/group/",editable:false},
  capability:{prefix:"site-capabilities/",editable:false},
  gallery:{prefix:"site-gallery/",editable:false},
  blog:{prefix:"site-blog/",editable:false}
};
const SQL=[
  ["产品内容（草稿及正式）","SELECT model AS ref FROM xuyi_product_content WHERE instr(content_json,?)>0 LIMIT 12"],
  ["页面正文（草稿及正式）","SELECT route AS ref FROM xuyi_page_content WHERE instr(main_html,?)>0 LIMIT 12"],
  ["翻译覆盖","SELECT resource_id||' ['||locale||']' AS ref FROM xuyi_translation_overrides WHERE instr(translated_json,?)>0 LIMIT 12"],
  ["博客内容","SELECT slug AS ref FROM xuyi_blog_posts WHERE instr(content_json,?)>0 LIMIT 12"],
  ["博客未发布草稿","SELECT slug AS ref FROM xuyi_blog_drafts WHERE instr(draft_json,?)>0 LIMIT 12"],
  ["品牌与联系人","SELECT key AS ref FROM site_state WHERE instr(value,?)>0 LIMIT 12"]
];
export async function readUsageIndex(env,url){
  if(!env.ASSETS?.fetch)throw Error("Deployed Pages asset reader unavailable");
  const indexUrl=new URL("/r2-usage-index.json",url);
  const response=await env.ASSETS.fetch(new Request(indexUrl,{headers:{"cache-control":"no-store"}}));
  if(!response.ok)throw Error("R2 reference index not deployed");
  const data=await response.json();
  if(data?.site!=="leyamould"||data.schemaVersion!==1||
     !Number.isInteger(data.publishRevision)||
     !data.references||typeof data.references!=="object")throw Error("Invalid R2 reference index");
  return data;
}
export async function findMediaUsage(env,path,index){
  if(!env.LEYA_DB)throw Error("D1 usage verification unavailable");
  const state=await env.LEYA_DB.prepare("SELECT value FROM site_state WHERE key=?")
    .bind("publish_revision").first();
  const d1Revision=Number(state?.value);
  const liveRevision=Number(index.publishRevision);
  // The deployed index must describe exactly the same D1 revision. Allowing
  // either side to be newer would race a stale Pages deployment or unpublished
  // D1 references, so both cases fail closed.
  if(!state||!Number.isInteger(d1Revision)||!Number.isInteger(liveRevision)||
     d1Revision!==liveRevision)
    throw Error("D1 publish revision does not match the live Pages media index");

  const locations=new Set(index.references[path]||[]);
  for(const [description,sql] of SQL){
    try{
      const rows=(await env.LEYA_DB.prepare(sql).bind(path).all()).results||[];
      for(const row of rows)locations.add(description+": "+String(row.ref||"unknown"));
    }catch(error){
      // CMS tables may not exist before the first record is created.
      if(/no such table:\s*(xuyi_product_content|xuyi_page_content|xuyi_translation_overrides|xuyi_blog_posts|xuyi_blog_drafts|site_state)\b/i.test(String(error?.message||error)))continue;
      throw error;
    }
  }
  const all=[...locations];
  return {usageStatus:all.length?"used":"unused",used:all.length>0,referenceCount:all.length,
    references:all.slice(0,20),truncated:all.length>20,publishRevision:d1Revision};
}
export const imageKey=(kind,filename)=>{
  if(!Object.hasOwn(KINDS,kind))return null;
  if(KINDS[kind].editable&&!/^[a-f0-9]{32}\.(?:jpg|png|webp)$/.test(filename))return null;
  if(!/^[a-zA-Z0-9._-]{3,140}$/.test(filename)||filename.includes(".."))return null;
  return KINDS[kind].prefix+filename;
};

