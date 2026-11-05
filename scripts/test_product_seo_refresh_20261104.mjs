import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {REVIEWED_SEO_SOURCE as previous} from "../functions/_shared/reviewed-product-seo-20261020.js";
import {REVIEWED_SEO_REFRESH_SOURCE as reviewed} from "../functions/_shared/reviewed-product-seo-refresh-20261104.js";
import {
  REVIEWED_COUNT, expectedReviewedRows, targetTitle, targetDescription, classifyReviewedRow, onRequestGet, onRequestPost
} from "../functions/api/admin/product-seo-refresh-20261104.js";
import {normalizeProductSeo} from "../functions/_shared/product-seo.js";

assert.equal(REVIEWED_COUNT,505);
assert.equal(expectedReviewedRows().size,505);
assert.equal(reviewed.length,505);
assert.deepEqual(
  Object.fromEntries(["en","es","pt","ru","tr"].map(locale=>[
    locale,reviewed.filter(row=>row.locale===locale).length
  ])),
  {en:101,es:101,pt:101,ru:101,tr:101}
);

const priorMap=new Map(previous.map(row=>[row.slug+"/"+row.locale,row]));
const seen=new Set();
const titleSets=new Map();const descriptionSets=new Map();
for(const row of reviewed){
  const key=row.slug+"/"+row.locale;
  assert(!seen.has(key),"duplicate refresh key "+key);
  seen.add(key);
  const old=priorMap.get(key);
  assert(old,"missing previous reviewed source "+key);
  assert.notEqual(row.newTitle,old.newTitle,"refresh title must differ from prior approved source");
  assert.notEqual(row.newDescription,old.newDescription,"refresh description must differ from prior approved source");
  const normalized=normalizeProductSeo({
    slug:row.slug,locale:row.locale,
    seoTitle:targetTitle(row),metaDescription:targetDescription(row)
  });
  assert.equal(normalized.title,targetTitle(row));
  assert.equal(normalized.description,targetDescription(row));
  assert(targetTitle(row).length<=60,key+" title length");
  assert(targetDescription(row).length<=180,key+" description length");
  assert(row.newTitle.includes("OEM")&&row.newTitle.includes("XUYI"),key+" B2B/OEM title");
  assert(targetDescription(row).toLowerCase().includes("b2b"),key+" B2B description");
  if(row.hasCapacity){
    assert(row.newTitle.toLowerCase().includes("ml"),key+" mL title");
    assert(row.newTitle.toLowerCase().includes("oz"),key+" oz title");
  }
  assert(
    row.newTitle!==old.newTitle||row.newDescription!==old.newDescription,
    key+" must have a reviewed source refresh"
  );
  const titleSet=titleSets.get(row.locale)||new Set();
  assert(!titleSet.has(targetTitle(row)),key+" duplicate title");
  titleSet.add(targetTitle(row));
  titleSets.set(row.locale,titleSet);
  const descriptionSet=descriptionSets.get(row.locale)||new Set();
  assert(!descriptionSet.has(targetDescription(row)),key+" duplicate meta description");
  descriptionSet.add(targetDescription(row));
  descriptionSets.set(row.locale,descriptionSet);
  if(row.twoWay){
    const variants={
      en:["Dual-Mode Cup","Travel Cup","Seal-Design Cup","Daily-Use Cup","Dual-Drink Cup"],
      es:["Vaso doble","Vaso de viaje","Vaso con sello","Vaso diario","Vaso de doble uso"],
      pt:["Copo duplo","Copo de viagem","Copo com vedação","Copo diário","Copo de dupla função"],
      ru:["Кружка 2-в-1","Дорожная кружка","Кружка с уплотнением","Повседневная кружка","Кружка с двумя режимами"],
      tr:["Çift içimli bardak","Seyahat bardağı","Contalı bardak","Günlük bardak","İki içimli bardak"]
    };
    assert(variants[row.locale].some(term=>row.newTitle.includes(term)),key+" two-way SEO modifier");
  }

  assert.deepEqual(
    classifyReviewedRow(row,{seo_title:old.newTitle,meta_description:old.newDescription}),
    {title:"eligible",description:"eligible"}
  );
  assert.deepEqual(
    classifyReviewedRow(row,{seo_title:targetTitle(row),meta_description:targetDescription(row)}),
    {title:"updated",description:"updated"}
  );
  assert.deepEqual(
    classifyReviewedRow(row,{seo_title:"Owner edited title for "+row.slug,meta_description:old.newDescription}),
    {title:"preserved",description:"eligible"},
    "an owner title edit must not block the independent description refresh"
  );
  assert.deepEqual(
    classifyReviewedRow(row,{seo_title:old.newTitle,meta_description:"Owner edited description for "+row.slug}),
    {title:"eligible",description:"preserved"},
    "an owner description edit must not block the independent title refresh"
  );
  assert.deepEqual(classifyReviewedRow(row,null),{title:"missing",description:"missing"});
}

const authResponse=await onRequestGet({
  request:new Request("https://xuyibottles.com/api/admin/product-seo-refresh-20261104"),
  env:{ADMIN_TOKEN:"test-admin-secret"}
});
assert.equal(authResponse.status,401);
const authSource=readFileSync("functions/_shared/build-auth.js","utf8");
assert(authSource.includes("/api/admin/product-seo-refresh-20261104"));
const workflow=readFileSync(".github/workflows/publish-xuyi.yml","utf8");
assert(workflow.includes("scripts/promote_product_seo_refresh_20261104.py"));
assert(workflow.includes("scripts/test_product_seo_refresh_20261104.mjs"));

const dbRows=new Map(reviewed.map(row=>{
  const old=priorMap.get(row.slug+"/"+row.locale);
  return [row.slug+"/"+row.locale,{
    slug:row.slug,locale:row.locale,seo_title:old.newTitle,meta_description:old.newDescription
  }];
}));const stateRows=new Map();
const fakeDb={
  prepare(sql){
    let params=[];
    const statement={
      bind(...values){params=values;return statement;},
      async all(){
        if(sql.includes("FROM xuyi_product_seo"))return {results:[...dbRows.values()]};
        return {results:[]};
      },
      async first(){
        if(sql.includes("FROM site_state")){
          const key=params[0]||((sql.match(/key='([^']+)'/)||[])[1]);
          return key&&stateRows.has(key)?{value:stateRows.get(key)}:null;
        }
        return null;
      },
      async run(){
        if(sql.startsWith("CREATE TABLE"))return {success:true};
        if(sql.startsWith("UPDATE xuyi_product_seo SET seo_title")){
          const [value,slug,locale,expected1,expected2]=params;
          const row=dbRows.get(slug+"/"+locale);
          if(row&&[expected1,expected2].includes(row.seo_title))row.seo_title=value;
          return {success:true};
        }
        if(sql.startsWith("UPDATE xuyi_product_seo SET meta_description")){
          const [value,slug,locale,expected1,expected2]=params;
          const row=dbRows.get(slug+"/"+locale);
          if(row&&[expected1,expected2].includes(row.meta_description))row.meta_description=value;
          return {success:true};
        }
        if(sql.startsWith("INSERT INTO site_state")){
          const literal=(sql.match(/VALUES\('([^']+)'/)||[])[1];
          const key=literal||params[0];
          const value=literal?params[0]:"505";
          stateRows.set(key,value);
          return {success:true};
        }
        return {success:true};
      }
    };
    return statement;
  },
  async batch(queries){for(const query of queries)await query.run();return {success:true};}
};
const ownerTitleRow=dbRows.get("2095/en");
ownerTitleRow.seo_title="Owner-approved English title for model 2095";
const ownerDescriptionRow=dbRows.get("2095/es");
ownerDescriptionRow.meta_description="Owner-approved Spanish description for model 2095, retained by the refresh.";
const originalFetch=globalThis.fetch;
globalThis.fetch=async()=>({
  ok:true,
  async json(){return {success:true,result:{name:"xuyi-drinkware-site"}};}
});
try{
  const requestFor=(method,body)=>new Request(
    "https://xuyibottles.com/api/admin/product-seo-refresh-20261104",
    {method,headers:{"Authorization":"Bearer test-ci-project-token","Content-Type":"application/json"},
     ...(body?{body:JSON.stringify(body)}:{})}
  );
  const preflight=await onRequestGet({request:requestFor("GET"),env:{XUYI_DB:fakeDb}});
  assert.equal(preflight.status,200);
  const preflightBody=await preflight.json();
  assert.equal(preflightBody.titleEligible,504);
  assert.equal(preflightBody.titlePreserved,1);
  assert.equal(preflightBody.descriptionEligible,504);
  assert.equal(preflightBody.descriptionPreserved,1);
  for(let batchIndex=0;batchIndex<Math.ceil(REVIEWED_COUNT/15);batchIndex++){
    const response=await onRequestPost({
      request:requestFor("POST",{action:"batch",batchIndex}),env:{XUYI_DB:fakeDb}
    });
    assert.equal(response.status,200);
  }
  const after=await onRequestGet({request:requestFor("GET"),env:{XUYI_DB:fakeDb}});
  const afterBody=await after.json();
  assert.equal(afterBody.titleEligible,0);
  assert.equal(afterBody.descriptionEligible,0);
  assert.equal(afterBody.titleUpdated,504);
  assert.equal(afterBody.titlePreserved,1);
  assert.equal(afterBody.descriptionUpdated,504);
  assert.equal(afterBody.descriptionPreserved,1);
  assert.equal(afterBody.missingRows.length,0);
  assert.equal(ownerTitleRow.seo_title,"Owner-approved English title for model 2095");
  assert.equal(ownerDescriptionRow.meta_description,"Owner-approved Spanish description for model 2095, retained by the refresh.");
  const finalized=await onRequestPost({
    request:requestFor("POST",{action:"finalize"}),env:{XUYI_DB:fakeDb}
  });
  const finalBody=await finalized.json();
  assert.equal(finalized.status,200);
  assert.equal(finalBody.complete,true);
  assert.equal(finalBody.revision,1);
}finally{
  globalThis.fetch=originalFetch;
}
console.log("XUYI_PRODUCT_SEO_REFRESH_505_ROWS_5_LOCALES_FIELDWISE_OWNER_GUARD_PASS");
