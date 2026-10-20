/* Exactly one canonical D1 record for each product route and locale. */
(()=>{"use strict";
 const el=id=>document.getElementById(id);
 const say=t=>{if(el("product-seo-status"))el("product-seo-status").textContent=t};
 const token=()=>sessionStorage.getItem("xuyiAdminToken")||"";
 let rows=[],models=[];
 const current=()=>({
  slug:el("product-seo-slug").value.trim().toLowerCase(),
  locale:el("product-seo-locale").value
 });
 async function api(body){
  if(!token())throw Error("请先登录后台");
  const opts={method:body?"POST":"GET",headers:{"authorization":"Bearer "+token()},cache:"no-store"};
  if(body){opts.headers["content-type"]="application/json";opts.body=JSON.stringify(body)}
  const r=await fetch("/api/admin/product-seo",opts);
  const d=await r.json().catch(()=>({}));
  if(!r.ok)throw Error(d.error||"HTTP "+r.status);
  return d;
 }
 function populate(){
  const {slug,locale}=current();
  const row=rows.find(x=>x.slug===slug&&x.locale===locale);
  el("product-seo-title").value=row?.seoTitle||"";
  el("product-seo-description").value=row?.metaDescription||"";
  say(row?"D1 已保存的 "+locale+" 正式 SEO 文案。":"此语言没有 D1 记录，请核对型号或重新读取。");
 }
 async function load(){
  say("读取 D1 产品 SEO...");
  try{
   const data=await api();rows=data.items||[];models=data.models||[];
   el("product-seo-models").replaceChildren(...models.map(x=>{
    const node=document.createElement("option");node.value=x;return node;
   }));
   if(!el("product-seo-slug").value&&models.includes("2292"))el("product-seo-slug").value="2292";
   populate();
   say("D1 已读取 "+rows.length+" 个产品语言 SEO 记录。");
  }catch(err){say("读取失败："+err.message)}
 }
 el("product-seo-reload")?.addEventListener("click",load);
 el("product-seo-reset")?.addEventListener("click",populate);
 el("product-seo-slug")?.addEventListener("change",populate);
 el("product-seo-locale")?.addEventListener("change",populate);
 document.querySelector('[data-admin-target="productseo"]')?.addEventListener("click",load);
 el("product-seo-editor")?.addEventListener("submit",async ev=>{
  ev.preventDefault();
  const {slug,locale}=current();
  if(!models.includes(slug)){say("请先选择真实产品型号，不能把其它型号的 SEO 文案套用过来。");return}
  const input={action:"save",slug,locale,seoTitle:el("product-seo-title").value.trim(),
   metaDescription:el("product-seo-description").value.trim()};
  try{
   await api(input);await load();say("已保存至 Cloudflare D1。点击顶部「一键全站重建」后五语页面和 OG 同步更新。");
  }catch(err){say("保存失败："+err.message)}
 });
})();
