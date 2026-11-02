import assert from "node:assert/strict";
import {scheduleBlogLocalePost} from "../functions/_shared/publish-scheduler.js";

class MockD1 {
  constructor(){this.localeRows=new Map();}
  prepare(sql){
    const db=this;
    let args=[];
    return {
      bind(...values){args=values;return this;},
      async run(){
        if(sql.startsWith("INSERT INTO xuyi_blog_locale_schedule")){
          const [slug,locale,scheduled_at,payload_json,content_sha256]=args;
          const key=slug+"|"+locale;
          if(db.localeRows.has(key))return {meta:{changes:0}};
          db.localeRows.set(key,{slug,locale,scheduled_at,status:"scheduled",approved:1,payload_json,content_sha256});
          return {meta:{changes:1}};
        }
        return {meta:{changes:1}};
      },
      async first(){
        if(sql.includes("FROM xuyi_blog_locale_schedule WHERE slug=? AND locale=?")){
          return db.localeRows.get(args[0]+"|"+args[1])||null;
        }
        return null;
      },
      async all(){return {results:[]};}
    };
  }
  async batch(statements){
    const results=[];
    for(const statement of statements)results.push(await statement.run());
    return results;
  }
}

const db=new MockD1();
const scheduledAt=new Date(Date.now()+24*60*60*1000).toISOString();
const payload=JSON.stringify({
  locale:"es",
  translated:{title:"Guía de compra de botellas escolares",description:"Guía de adquisición para escuelas.",mainHtml:"<article>"+("contenido editorial revisado ".repeat(80))+"</article>"},
  indexCardHtml:'<article class="news-card"><a href="/blog/demo-school-guide/"><img src="/media/blog/demo.webp" alt="Descripción visual detallada de la imagen de portada para lectores"></a></article>'
});
const first=await scheduleBlogLocalePost(db,{slug:"demo-school-guide",locale:"es",scheduledAt,approved:true,payloadJson:payload});
assert.equal(first.reused,false);
assert.equal(db.localeRows.size,1);
const second=await scheduleBlogLocalePost(db,{slug:"demo-school-guide",locale:"es",scheduledAt,approved:true,payloadJson:payload});
assert.equal(second.reused,true);
await assert.rejects(
  scheduleBlogLocalePost(db,{slug:"demo-school-guide",locale:"es",scheduledAt,approved:true,payloadJson:payload+" "}),
  /conflicts/
);
await assert.rejects(
  scheduleBlogLocalePost(db,{slug:"demo-school-guide",locale:"fr",scheduledAt,approved:true,payloadJson:payload}),
  /not enabled/
);
await assert.rejects(
  scheduleBlogLocalePost(db,{slug:"demo-school-guide",locale:"pt",scheduledAt,approved:false,payloadJson:payload}),
  /explicit owner authorization/
);
console.log("XUYI_LOCALE_SCHEDULE_HASH_LOCK_IDEMPOTENCY_AND_APPROVAL_PASS");