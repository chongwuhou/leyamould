/* Minimal no-library editor for real SKU-specific buyer reviews. */
(()=>{"use strict";
 const $=id=>document.getElementById(id);
 const esc=v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
 const status=message=>{const e=$("review-admin-status");if(e)e.textContent=message};
 const token=()=>sessionStorage.getItem("xuyiAdminToken")||"";
 let items=[],models=[],editingId="";
 async function call(body){
  if(!token())throw Error("请先登录网站后台");
  const options={method:body?"POST":"GET",headers:{authorization:"Bearer "+token()},cache:"no-store"};
  if(body){options.headers["content-type"]="application/json";options.body=JSON.stringify(body)}
  const response=await fetch("/api/admin/product-reviews",options);
  const data=await response.json().catch(()=>({}));
  if(!response.ok)throw Error(data.error||"HTTP "+response.status);
  return data;
 }
 function clear(){
  editingId="";
  $("review-editor").reset();
  $("review-authentic").checked=false;
  $("review-save").textContent="保存到 D1";
 }
 function render(){
  $("review-model-options").innerHTML=models.map(x=>'<option value="'+esc(x)+'"></option>').join("");
  const query=$("review-filter").value.trim().toLowerCase();
  const rows=items.filter(x=>(x.model+" "+x.author+" "+x.content).toLowerCase().includes(query));
  $("review-admin-list").innerHTML=rows.length?rows.map(r=>
   '<article class="panel" style="margin:10px 0;padding:14px"><div class="row-actions" style="justify-content:space-between;align-items:center">'+
   '<strong>'+esc(r.model)+' · '+esc(r.author)+'</strong><span>'+("★".repeat(r.rating))+
   ("☆".repeat(5-r.rating))+' · '+esc(r.reviewDate)+' · '+(r.status==="published"?"已审核发布":"草稿")+'</span></div>'+
   '<p style="white-space:pre-wrap">'+esc(r.content)+'</p><div class="row-actions">'+
   '<button class="btn ghost" type="button" data-review-edit="'+esc(r.id)+'">编辑</button>'+
   (r.status==="published"?'<button class="btn ghost" type="button" data-review-hide="'+esc(r.id)+'">撤销发布</button>':"")+
   '<button class="btn ghost" type="button" data-review-delete="'+esc(r.id)+'">删除</button></div></article>'
  ).join(""):'<p class="muted">尚无记录，或当前筛选无匹配。</p>';
 }
 async function load(){
  status("正在读取 D1 评价...");
  try{
   const data=await call();items=data.items||[];models=data.models||[];
   render();status("已读取 "+items.length+" 条记录；草稿不会出现在产品页。");
  }catch(err){status("读取失败："+err.message)}
 }
 function edit(r){
  editingId=r.id;
  for(const [name,val] of [["model",r.model],["rating",String(r.rating)],["author",r.author],
   ["reviewDate",r.reviewDate],["content",r.content],["status",r.status]]){
   const el=$("review-editor").elements.namedItem(name);if(el)el.value=val;
  }
  $("review-authentic").checked=false;
  $("review-save").textContent="保存修改到 D1";
  $("review-editor").scrollIntoView({behavior:"smooth",block:"start"});
  status("正在编辑 "+r.model+" 的评价。修改或重新发布时需要再次确认真实性和授权。");
 }
 $("review-editor")?.addEventListener("submit",async event=>{
  event.preventDefault();
  const form=event.currentTarget;
  const body={action:"save",id:editingId||undefined,model:form.elements.namedItem("model").value.trim(),
   rating:Number(form.elements.namedItem("rating").value),author:form.elements.namedItem("author").value.trim(),
   reviewDate:form.elements.namedItem("reviewDate").value,
   content:form.elements.namedItem("content").value.trim(),
   status:form.elements.namedItem("status").value,
   confirmedAuthentic:$("review-authentic").checked};
  if(!models.includes(body.model)){status("请从已有产品型号中选择，不要把公司评价挂到不存在的型号。");return}
  if(body.status==="published"&&!body.confirmedAuthentic){
   status("发布前必须核实真实评价、产品对应关系和客户公开授权。");return;
  }
  const button=$("review-save");button.disabled=true;
  try{
   const r=await call(body);clear();await load();
   status((r.status==="published"?"评价已审核保存":"草稿已保存")+
    "。变更进入 D1 发布队列，请点击后台顶部「一键全站重建」让产品页及 Google 数据同步更新。");
  }catch(err){status("保存失败："+err.message)}
  finally{button.disabled=false}
 });
 $("review-admin-list")?.addEventListener("click",async event=>{
  const button=event.target.closest("button");if(!button)return;
  const id=button.dataset.reviewEdit||button.dataset.reviewHide||button.dataset.reviewDelete;
  const found=items.find(x=>x.id===id);if(!found)return;
  if(button.dataset.reviewEdit){edit(found);return}
  if(button.dataset.reviewHide){
   if(!confirm("确认撤销公开？需要重新构建后前台和 Google 数据才会移除。"))return;
   try{await call({...found,action:"save",status:"draft"});await load();status("已撤销发布，等待全站重建。")}
   catch(err){status(err.message)}
  }
  if(button.dataset.reviewDelete){
   if(!confirm("确定永久删除这条评价？如果已公开，重新构建后将从产品页和结构化数据移除。"))return;
   try{await call({action:"delete",id});if(editingId===id)clear();await load();status("评价已删除，等待全站重建。")}
   catch(err){status(err.message)}
  }
 });
 $("review-new")?.addEventListener("click",()=>{clear();status("新建评价草稿，发布前须核实真实客户资料。")});
 $("review-cancel")?.addEventListener("click",clear);
 $("review-reload")?.addEventListener("click",load);
 $("review-filter")?.addEventListener("input",render);
 document.querySelector('[data-admin-target="reviews"]')?.addEventListener("click",load);
})();
