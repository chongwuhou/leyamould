/* Exactly one canonical D1 record for each product route and configured locale. */
(()=>{"use strict";
 const el=id=>document.getElementById(id);
 const say=t=>{if(el("product-seo-status"))el("product-seo-status").textContent=t};
 const token=()=>sessionStorage.getItem("xuyiAdminToken")||"";
 let rows=[],models=[],languages=[],sourceLocale="";
 const current=()=>({slug:el("product-seo-slug").value.trim().toLowerCase(),locale:el("product-seo-locale").value});
 const languageName=code=>languages.find(item=>item.code===code)?.name||code;
 async function api(body){if(!token())throw Error("请先登录后台");
  const opts={method:body?"POST":"GET",headers:{"authorization":"Bearer "+token()},cache:"no-store"};
  if(body){opts.headers["content-type"]="application/json";opts.body=JSON.stringify(body)}
  const r=await fetch("/api/admin/product-seo",opts),d=await r.json().catch(()=>({}));
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
  el("product-seo-title").value=row?.seoTitle||"";el("product-seo-description").value=row?.metaDescription||"";
  say(row?"D1 已保存的 "+languageName(locale)+" 正式 SEO 文案。":"此语言没有 D1 记录，请核对型号或重新读取。");
 }
 async function load(){
  say("读取 D1 产品 SEO...");
  try{
   const data=await api();rows=data.items||[];models=data.models||[];languages=data.languages||[];
   sourceLocale=data.sourceLocale||languages[0]?.code||"";
   renderLanguages();renderSummary(data);
   el("product-seo-models").replaceChildren(...models.map(x=>{const node=document.createElement("option");node.value=x;return node;}));
   if(!el("product-seo-slug").value&&models[0])el("product-seo-slug").value=models[0];
   populate();say("D1 已读取 "+(data.productCount??models.length)+" 个已配置产品及 "+languages.length+" 种后台语言。");
  }catch(err){say("读取失败："+err.message)}
 }
 el("product-seo-reload")?.addEventListener("click",load);el("product-seo-reset")?.addEventListener("click",populate);
 el("product-seo-slug")?.addEventListener("change",populate);el("product-seo-locale")?.addEventListener("change",populate);
 document.querySelector('[data-admin-target="productseo"]')?.addEventListener("click",load);
 el("product-seo-editor")?.addEventListener("submit",async ev=>{
  ev.preventDefault();const {slug,locale}=current();
  if(!locale){say("D1 语言配置为空，不能保存。");return}
  if(!models.includes(slug)){say("请先选择真实产品型号，不能把其它型号的 SEO 文案套用过来。");return}
  const input={action:"save",slug,locale,seoTitle:el("product-seo-title").value.trim(),metaDescription:el("product-seo-description").value.trim()};
  try{await api(input);await load();say("已保存至 Cloudflare D1。点击顶部「一键全站重建」后已配置语言页面和 OG 同步更新。")}
  catch(err){say("保存失败："+err.message)}
 });
})();
