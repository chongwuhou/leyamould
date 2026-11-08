/* XUYI D1 product SEO and locale-body console. */
(()=>{"use strict";
 const el=id=>document.getElementById(id);
 const say=t=>{if(el("product-seo-status"))el("product-seo-status").textContent=t};
 const bodySay=t=>{if(el("product-content-status"))el("product-content-status").textContent=t};
 const token=()=>sessionStorage.getItem("xuyiAdminToken")||"";
 let rows=[],models=[],languages=[],sourceLocale="",bodyRequest=0;
 const current=()=>({slug:el("product-seo-slug").value.trim().toLowerCase(),locale:el("product-seo-locale").value});
 const languageName=code=>languages.find(item=>item.code===code)?.name||code;
 const sourceName=()=>languageName(sourceLocale)||sourceLocale||"来源语言";
 const sourceRoute=slug=>"/products/"+encodeURIComponent(slug)+"/";
 async function api(body){
  if(!token())throw Error("请先登录后台");
  const opts={method:body?"POST":"GET",headers:{authorization:"Bearer "+token()},cache:"no-store"};
  if(body){opts.headers["content-type"]="application/json";opts.body=JSON.stringify(body)}
  const r=await fetch("/api/admin/product-seo",opts),d=await r.json().catch(()=>({}));
  if(!r.ok)throw Error(d.error||"HTTP "+r.status);return d;
 }
 async function readBody(slug,locale){
  const query="?slug="+encodeURIComponent(slug)+"&locale="+encodeURIComponent(locale);
  const r=await fetch("/api/admin/product-seo"+query,{headers:{authorization:"Bearer "+token()},cache:"no-store"});
  const d=await r.json().catch(()=>({}));
  if(!r.ok)throw Error(d.error||"HTTP "+r.status);return d;
 }
 function renderLanguages(){
  const select=el("product-seo-locale");if(!select)return;
  select.replaceChildren(...languages.map(item=>{const node=document.createElement("option");
   node.value=item.code;node.textContent=item.name||item.displayName||item.code;return node;}));
  if(sourceLocale&&languages.some(item=>item.code===sourceLocale))select.value=sourceLocale;
 }
 function renderSummary(data){
  if(el("product-seo-count"))el("product-seo-count").textContent=(data.productCount??models.length)+" 个已配置产品";
  if(el("product-seo-language-summary"))el("product-seo-language-summary").textContent=
   "当前语言："+languages.filter(item=>item.enabled!==false).map(item=>item.name||item.code).join("、");
 }
 function populate(){
  const {slug,locale}=current(),row=rows.find(x=>x.slug===slug&&x.locale===locale);
  el("product-seo-title").value=row?.seoTitle||"";
  el("product-seo-description").value=row?.metaDescription||"";
  const content=el("product-seo-content");
  if(content)content.value="";
  bodySay("");
  say(row?"D1 已保存的 "+languageName(locale)+" 正式 SEO 文案。":"此语言没有 D1 SEO 记录，请核对型号或重新读取。");
 }
 async function loadBody(){
  const {slug,locale}=current(),content=el("product-seo-content"),sourceButton=el("product-content-source");
  const request=++bodyRequest;
  if(!content||!sourceButton)return;
  content.value="";content.disabled=true;sourceButton.disabled=true;bodySay("");
  if(!slug||!locale){bodySay("请先选择产品和语言。");return}
  if(locale===sourceLocale){
   bodySay("来源语言正文请在 06「产品商详」入口维护。");
   return;
  }
  bodySay("正在读取 D1 多语言正文…");
  try{
   const data=await readBody(slug,locale);
   if(request!==bodyRequest)return;
   content.value=data.content?.mainHtml||"";
   content.disabled=false;sourceButton.disabled=false;
   bodySay(data.hasContent?"已读取 D1 正式正文，可直接翻译修订。":"尚无该语种正文；可读取来源语言正文后完整翻译。");
  }catch(error){if(request===bodyRequest)bodySay("正文读取失败："+error.message)}
 }
 async function load(){
  say("读取 D1 产品 SEO 与语言配置…");
  try{
   const data=await api();rows=data.items||[];models=data.models||[];languages=data.languages||[];
   sourceLocale=data.sourceLocale||languages[0]?.code||"";
   renderLanguages();renderSummary(data);
   el("product-seo-models").replaceChildren(...models.map(x=>{const node=document.createElement("option");node.value=x;return node;}));
   if(!el("product-seo-slug").value&&models[0])el("product-seo-slug").value=models[0];
   populate();await loadBody();
   say("D1 已读取 "+(data.productCount??models.length)+" 个已配置产品及 "+languages.length+" 种后台语言。");
  }catch(err){say("读取失败："+err.message)}
 }
 el("product-seo-reload")?.addEventListener("click",load);
 el("product-seo-reset")?.addEventListener("click",()=>{populate();loadBody()});
 el("product-seo-slug")?.addEventListener("change",()=>{populate();loadBody()});
 el("product-seo-locale")?.addEventListener("change",()=>{populate();loadBody()});
 el("product-content-source")?.addEventListener("click",async()=>{
  const {slug,locale}=current(),content=el("product-seo-content");
  if(!slug||!locale||locale===sourceLocale||!content)return;
  const request=++bodyRequest;content.disabled=true;bodySay("正在读取来源语言正文…");
  try{
   const response=await fetch(sourceRoute(slug),{cache:"no-store"});
   if(!response.ok)throw Error("来源语言页面读取失败");
   const main=new DOMParser().parseFromString(await response.text(),"text/html").getElementById("main-content");
   if(!main)throw Error("来源语言页面缺少 main 内容");
   if(request!==bodyRequest)return;
   content.value=main.innerHTML;content.disabled=false;bodySay("已读取 "+sourceName()+" 正文，请完成全文翻译后保存。");
  }catch(error){if(request===bodyRequest){content.disabled=false;bodySay("来源正文读取失败："+error.message)}}
 });
 document.querySelector('[data-admin-target="productseo"]')?.addEventListener("click",load);
 el("product-seo-editor")?.addEventListener("submit",async ev=>{
  ev.preventDefault();const {slug,locale}=current();
  if(!locale){say("D1 语言配置为空，不能保存。");return}
  if(!models.includes(slug)){say("请先选择真实产品型号，不能把其它型号的文案套用过来。");return}
  const input={action:"save",slug,locale,seoTitle:el("product-seo-title").value.trim(),metaDescription:el("product-seo-description").value.trim()};
  const mainHtml=el("product-seo-content")?.value.trim()||"";
  if(locale!==sourceLocale&&mainHtml)input.mainHtml=mainHtml;
  try{
   const result=await api(input);await load();
   say((result.contentSaved?"SEO 与对应语种正文":"SEO")+" 已保存至 Cloudflare D1。点击顶部「一键全站重建」后更新正式页面。");
  }catch(err){say("保存失败："+err.message)}
 });
})();