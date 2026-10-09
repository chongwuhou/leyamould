/* XUYI D1 content console. Reuses Demalong's authenticated admin endpoints. */
(()=>{"use strict";
 const token=()=>sessionStorage.getItem("xuyiAdminToken")||"";
 const $=id=>document.getElementById(id);
 const esc=v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
 let state={},tab="brand",dirty=false;
 const say=v=>{$("content-status").textContent=v};
 async function api(route,body){
  if(!token())throw Error("请先登录后台");
  const r=await fetch("/api/admin/"+route,{method:body?"POST":"GET",headers:{"authorization":"Bearer "+token(),...(body?{"content-type":"application/json"}:{})},body:body?JSON.stringify(body):undefined,cache:"no-store"});
  const data=await r.json().catch(()=>({}));if(!r.ok)throw Error(data.error||"HTTP "+r.status);
  return data;
 }
 const field=(key,value,label,rows=0)=>'<label class="block-label">'+esc(label)+(rows
  ?'<textarea data-cms-field="'+esc(key)+'" rows="'+rows+'">'+esc(value)+'</textarea>'
  :'<input data-cms-field="'+esc(key)+'" value="'+esc(value)+'">')+'</label>';
 const button=(label,action)=>'<button class="btn primary" data-cms-action="'+action+'" type="button">'+label+'</button>';
 async function load(){
  say("正在读取旭一 D1 …");
  try{
   const results=await Promise.all(["brand-config","site-config","pages","product-content","page-translations","page-content"].map(x=>api(x)));
   [state.brand,state.site,state.pages,state.products,state.locales,state.pageBodies]=results;
   dirty=false;say("已读取 D1，修改后需要保存。未审核内容不会自动公开。");
   render();
  }catch(e){say("读取失败："+e.message)}
 }
 function render(){
  const container=$("content-form");
  if(!container)return;
  if(!state.brand){container.innerHTML="<p>请先点击「读取线上 D1 内容」。</p>";return}
  let html="";
  if(tab==="brand"){
   const b=state.brand.config||{},c=b.contact||{},id=b.identity||{},footer=b.footer||{};
   html='<h3>品牌与全站联系信息</h3><p>邮箱、WhatsApp 同时要核对联系设置模块，避免表单与模板不一致。</p>'+
    field("displayName",id.displayName,"品牌显示名称")+
    field("legalName",id.legalName,"公司名称（请核实实际注册主体）")+
    field("email",c.email,"业务邮箱")+
    field("phoneE164",c.phoneE164,"WhatsApp 号码（国际格式 +86…）")+
    field("footerAbout",footer.about,"页脚介绍",3)+
    button("保存品牌并排队发布","brand");
  }
  if(tab==="navigation"){
   html='<h3>导航与跳转管理</h3><p>数组字段与德玛隆 site-config CMS 一致。仅允许网站实际路径或经核准的外链，编辑前请核对目标 URL。</p>'+
    field("navigation",JSON.stringify(state.site.navigation||[],null,2),"导航 JSON：id / parentId / label / url / sortOrder",16)+
    field("redirects",JSON.stringify(state.site.redirects||[],null,2),"301/302 跳转规则 JSON",7)+
    button("保存导航","navigation")+' '+button("保存跳转规则","redirects");
  }
  if(tab==="pages"){
   html='<h3>逐页 SEO 设置</h3><p>生产站暂保持 noindex。标题和描述修改将进入 D1 并参与下一次完整构建；所有原有 URL 保留。</p>'+
   '<label>选择页面 <input type="search" id="cms-route-filter" placeholder="搜索 URL / 标题" aria-label="搜索页面"></label>'+
   '<select id="cms-route" size="9" style="width:100%;margin:10px 0"></select>'+
   field("seoTitle","","SEO Title（最多 90 字符）")+
   field("seoDescription","","Meta Description（最多 240 字符）")+
   '<p>页面 Robots：<strong>noindex,nofollow</strong>（索引权限由独立上线审批控制）</p>'+
   button("保存所选页面 SEO","pages");
  }
  if(tab==="products"){
   html='<h3>产品结构化商详与 SEO</h3><p>输入现有产品型号，保存草稿不会公开。正式发布仅允许经过核实的型号资料覆盖原有页面，不会改写历史源文件。</p>'+
   field("model","","产品型号，例如 2095")+
   field("name","","英文产品名称")+
   field("material","","材质/部件材料（必须真实核实）")+
   field("capacity","","容量")+
   field("description","","英文产品描述",4)+
   field("seoTitle","","SEO Title")+
   field("seoDescription","","Meta Description",3)+
   '<label class="block-label">状态 <select data-cms-field="status"><option value="draft">草稿（不影响官网）</option><option value="published">审核完成并发布</option></select></label>'+
   button("保存产品到 D1","product");
  }
  if(tab==="page-body"){
   html='<h3>普通页面正文管理</h3><p>管理 About、Why Us、Capabilities 等页面；Blog 与产品详情各用其自身编辑器。草稿不影响前台，审核后发布才会覆盖现有页面主内容。</p>'+
    '<label class="block-label">英文原始页面 <select id="cms-page-body-route"></select></label>'+
    field("pageBodyHtml","","主内容完整 HTML（保留类名、图片、链接及页面结构）",20)+
    '<label class="block-label">状态 <select data-cms-field="pageBodyStatus"><option value="draft">草稿</option><option value="published">审核发布</option></select></label>'+
    button("读取当前英文页正文","page-body-source")+' '+button("保存页面正文","page-body-save");
  }
  if(tab==="locales"){
   html='<h3>多语言正式页面 · 翻译审核</h3><p>先复制英文原文，再逐段翻译。只有完整审核并设置发布就绪才会生成对应语言 URL；不会把英文假装成其他语言。</p>'+
    '<label class="block-label">目标语言 <select id="cms-locale"><option value="es">Español</option><option value="pt">Português</option><option value="ru">Русский</option><option value="tr">Türkçe</option></select></label>'+
    '<label class="block-label">英文原始路径 <select id="cms-locale-route"></select></label>'+
    field("localeTitle","","翻译后的 Title")+
    field("localeDescription","","翻译后的 Meta Description")+
    field("localeHtml","","已完整翻译的 Main HTML",16)+
    button("读取英文页面供翻译","locale-source")+' '+
    button("审核完成并保存","locale-save");
  }
  container.innerHTML=html;
  container.querySelectorAll("[data-cms-action]").forEach(el=>el.addEventListener("click",()=>save(el.dataset.cmsAction)));
  if(tab==="pages"){
   const input=$("cms-route-filter"),sel=$("cms-route");
   const fill=()=>{const q=input.value.trim().toLowerCase();
    sel.innerHTML=(state.pages.pages||[]).filter(x=>(x.route+" "+x.label).toLowerCase().includes(q))
      .map(x=>'<option value="'+esc(x.route)+'">'+esc(x.route+" · "+x.label)+'</option>').join("");sel.selectedIndex=0;selectPage()};
   const selectPage=()=>{const row=(state.pages.pages||[]).find(x=>x.route===sel.value);
    const t=container.querySelector('[data-cms-field="seoTitle"]'),d=container.querySelector('[data-cms-field="seoDescription"]');
    if(t)t.value=row?.seoTitle||"";if(d)d.value=row?.metaDescription||"";};
   input.oninput=fill;sel.onchange=selectPage;fill();
  }
  if(tab==="products"){
   const model=container.querySelector('[data-cms-field="model"]');
   model.addEventListener("change",()=>{const entry=(state.products.items||[]).find(x=>x.model===model.value.trim());if(!entry)return;
    for(const [key,val] of Object.entries(entry.content||{})){const el=container.querySelector('[data-cms-field="'+key+'"]');if(el)el.value=val;}
    container.querySelector('[data-cms-field="status"]').value=entry.status;});
  } 
  if(tab==="page-body"){
   const routes=$("cms-page-body-route");
   routes.innerHTML=(state.pageBodies?.editableRoutes||[]).map(route=>'<option value="'+esc(route)+'">'+esc(route)+'</option>').join("");
   routes.onchange=()=>{const item=(state.pageBodies?.items||[]).find(x=>x.route===routes.value);
    container.querySelector('[data-cms-field="pageBodyHtml"]').value=item?.mainHtml||"";
    container.querySelector('[data-cms-field="pageBodyStatus"]').value=item?.status||"draft";
   };
   routes.onchange();
  }
  if(tab==="locales"){
   const selector=$("cms-locale-route");
   selector.innerHTML=(state.pages.pages||[]).map(x=>'<option value="'+esc(x.route)+'">'+esc(x.route+" · "+x.label)+'</option>').join("");
   selector.onchange=fillLocale;$("cms-locale").onchange=fillLocale;fillLocale();
  }

 }
 function fillLocale(){
  const r=$("cms-locale-route")?.value,l=$("cms-locale")?.value;
  const x=(state.locales?.items||[]).find(p=>p.route===r&&p.locale===l);
  for(const [key,field] of [["localeTitle","title"],["localeDescription","description"],["localeHtml","mainHtml"]]){
   const el=document.querySelector('[data-cms-field="'+key+'"]');if(el)el.value=x?.content?.[field]||"";
  }
 }
 const value=(name)=>document.querySelector('#content-form [data-cms-field="'+name+'"]')?.value?.trim()||"";
 async function save(action){
  say("正在验证并保存到 XUYI D1 …");
  try{
   let result;
   if(action==="brand"){
    const b=structuredClone(state.brand.config);
    b.identity={...(b.identity||{}),displayName:value("displayName"),legalName:value("legalName")};
    b.contact={...(b.contact||{}),email:value("email"),phoneE164:value("phoneE164"),whatsappUrl:"https://wa.me/"+value("phoneE164").replace(/\D/g,"")};
    b.footer={...(b.footer||{}),about:value("footerAbout")};
    result=await api("brand-config",{config:b});
   }else if(action==="navigation"||action==="redirects"){
    let rows;try{rows=JSON.parse(value(action==="navigation"?"navigation":"redirects"))}catch{throw Error("请输入正确的 JSON 数组")}
    result=await api("site-config",{action:action==="navigation"?"save_navigation":"save_redirects",[action]:rows});
   }else if(action==="pages"){
    const selected=$("cms-route").value;
    const rows=state.pages.pages.map(row=>({...row,robots:"noindex,nofollow",sitemapEnabled:false}));
    const target=rows.find(x=>x.route===selected);if(!target)throw Error("请先选择页面");
    target.seoTitle=value("seoTitle");target.metaDescription=value("seoDescription");
    result=await api("pages",{action:"save_pages",pages:rows});
   }else if(action==="product"){
    result=await api("product-content",{action:"save_product",model:value("model"),
     status:value("status"),content:{name:value("name"),material:value("material"),capacity:value("capacity"),
       description:value("description"),seoTitle:value("seoTitle"),seoDescription:value("seoDescription")}});
   }else if(action==="page-body-source"){
    const route=$("cms-page-body-route").value;
    const response=await fetch(route,{cache:"no-store"});
    if(!response.ok)throw Error("无法读取英文页面正文");
    const main=new DOMParser().parseFromString(await response.text(),"text/html").getElementById("main-content");
    if(!main)throw Error("找不到页面的 main 内容");
    document.querySelector('[data-cms-field="pageBodyHtml"]').value=main.innerHTML;
    say("已读取。请检查所有图片、链接及交互结构；不允许嵌入 JS/脚本。");return;
   }else if(action==="page-body-save"){
    const status=value("pageBodyStatus");
    if(status==="published"&&!window.confirm("确认页面正文已经核实并加入正式发布队列？"))return;
    result=await api("page-content",{action:"save_page",route:$("cms-page-body-route").value,status,
      mainHtml:value("pageBodyHtml")});
   }else if(action==="locale-source"){
    const response=await fetch($("cms-locale-route").value,{cache:"no-store"});
    if(!response.ok)throw Error("无法读取英文页面");
    const doc=new DOMParser().parseFromString(await response.text(),"text/html");
    const main=doc.getElementById("main-content");
    if(!main)throw Error("英文原页面缺少 main");
    document.querySelector('[data-cms-field="localeHtml"]').value=main.innerHTML;
    say("已读取英文页面。请先完成全文翻译与检查，再点击审核保存。");return;
   }else if(action==="locale-save"){
    if(!window.confirm("确认全部可见正文已按目标语言翻译、图片链接及参数已经核对？"))return;
    result=await api("page-translations",{route:$("cms-locale-route").value,locale:$("cms-locale").value,
       title:value("localeTitle"),description:value("localeDescription"),mainHtml:value("localeHtml")});
   }else throw Error("Unknown operation");
   say("保存成功；D1 修订 "+(result.revision??"已记录")+"。发布任务会按设定自动重新构建。");
   await load();
  }catch(e){say("保存失败："+e.message)}
 }
 for(const tabName of ["brand","navigation","pages","page-body","products","locales"]){
  $("content-tab-"+tabName)?.addEventListener("click",()=>{tab=tabName;render();});
 }
 $("content-load")?.addEventListener("click",load);
 document.querySelector('[data-admin-target="content"]')?.addEventListener("click",()=>{
  if(!state.brand)load();
 });
})();