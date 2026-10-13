// Regression: the real enquiry "查看" action must open a populated dialog.
// Pure local browser fixture: no production credentials, requests or D1 writes.
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {runInNewContext} from "node:vm";

const html=readFileSync(new URL("../admin/index.html",import.meta.url),"utf8");
const source=readFileSync(new URL("../assets/admin-forms.js",import.meta.url),"utf8");
for(const id of ["submission-editor","submission-editor-title","submission-editor-content"]){
  const found=[...html.matchAll(new RegExp('\\bid="'+id+'"','g'))];
  assert.equal(found.length,1,"Enquiry editor must declare exactly one #"+id);
}
assert.match(html,/<dialog\b[^>]*id="submission-editor"[^>]*aria-labelledby="submission-editor-title"/);
assert.match(html,/<form method="dialog">[\s\S]*?<\/form>/,"Native close action required");
assert.match(html,/<div class="editor-content" id="submission-editor-content"><\/div>/);

function element(extra={}){
  return {
    textContent:"",innerHTML:"",dataset:{},value:"",
    events:new Map(),
    addEventListener(name,callback){this.events.set(name,callback)},
    ...extra
  };
}

async function exercise(includeModal){
  const modal=element({
    opened:false,
    showModal(){this.opened=true},
    close(){this.opened=false}
  });
  const title=element();
  const content=element();
  const body=element();
  const status=element();
  const refresh=element();
  const openButton=element({dataset:{id:"sample-id"}});
  const elements=new Map([
    ["#forms-body",body],["#form-stats",element()],
    ["#forms-status",status],["#forms-refresh",refresh],
    ["#form-search",element()],["#form-status-filter",element()]
  ]);
  if(includeModal){
    elements.set("#submission-editor",modal);
    elements.set("#submission-editor-title",title);
    elements.set("#submission-editor-content",content);
  }
  const requests=[];
  const document={
    querySelector: selector=>elements.get(selector)||null,
    querySelectorAll(selector){
      if(selector===".open-submission" && body.innerHTML.includes('class="btn small ghost open-submission"')) return [openButton];
      return [];
    }
  };
  const submission={
    id:"sample-id",created_at:"2026-10-13",name:"Example",
    email:"buyer@example.test",brand:"XUYI",reference:"2501",
    requirements:"Please supply <plastic> cups",status:"new",
    fields_json:JSON.stringify({note:"<script>test</script>"}),
    smtp_status:"sent"
  };
  const fetch=async (url,options={})=>{
    const method=options.method||"GET";
    requests.push({url,method});
    assert.equal(method,"GET","Viewing details must not mutate D1 or send emails");
    const record=url.includes("?id=")
      ? {submission}
      : {submissions:[submission],stats:{total:1,new_count:1}};
    return {ok:true,status:200,json:async()=>record};
  };
  runInNewContext(source,{
    document,fetch,
    sessionStorage:{getItem:()=>"test-session"},
    URLSearchParams,
    MutationObserver:class{observe(){}},
    setTimeout:()=>0,clearTimeout:()=>{},
    console
  },{filename:"assets/admin-forms.js"});
  assert.ok(refresh.events.has("click"),"Refresh event must be bound");
  await refresh.events.get("click")();
  assert.match(body.innerHTML,/open-submission/,"List must render view button");
  assert.ok(openButton.events.has("click"),"View event must be bound");
  openButton.events.get("click")();
  // The real event handler invokes an async function without returning it.
  await new Promise(resolve=>setImmediate(resolve));
  await new Promise(resolve=>setImmediate(resolve));
  if(includeModal){
    assert.equal(modal.opened,true,"View must open the inquiry detail dialog");
    assert.equal(title.textContent,"XUYI 2501");
    assert.match(content.innerHTML,/buyer@example\.test/);
    assert.match(content.innerHTML,/Please supply &lt;plastic&gt; cups/);
    assert.match(content.innerHTML,/&lt;script&gt;test&lt;\/script&gt;/);
    assert.doesNotMatch(status.textContent,/读取失败/);
    assert.equal(requests.length,2,"Only list GET and detail GET expected");
    modal.close();
    assert.equal(modal.opened,false,"Close must dismiss modal");
  }else{
    assert.match(status.textContent,/询盘详情窗口未加载/);
    assert.doesNotMatch(status.textContent,/Cannot set properties of null/);
    assert.equal(requests.length,1,"Do not fetch private detail when modal DOM is missing");
  }
}

await exercise(true);
await exercise(false);
console.log("XUYI_ADMIN_INQUIRY_DETAIL_OPEN_CLOSE_AND_MISSING_DOM_TESTS_PASSED");