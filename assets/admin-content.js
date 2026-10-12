/* XUYI D1 content console. Reuses Demalong's authenticated admin endpoints. */
(()=>{"use strict";
 const token=()=>sessionStorage.getItem("xuyiAdminToken")||"";
 const $=id=>document.getElementById(id);
 const esc=v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
 let state={},tab="brand",dirty=false,bannerLocale="en";
 const requiredData={brand:"brand",banners:"bannerDraft",navigation:"site",pages:"pages",
  "page-body":"pageBodies",products:"products","new-product":"products",locales:"locales"};
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
   const endpoints=[["brand-config","brand"],["site-config","site"],["site-settings","settings"],["pages","pages"],
    ["product-content","products"],["page-translations","locales"],["page-content","pageBodies"],
    ["home-banners","banners"]];
   // A failed unrelated CMS endpoint must not disable Banner/new-product editing.
   const results=await Promise.allSettled(endpoints.map(([route])=>api(route)));
   const errors=[];
   results.forEach((result,i)=>{
    const [route,key]=endpoints[i];
    if(result.status==="fulfilled")state[key]=result.value;
    else{state[key]=null;errors.push(route+": "+result.reason.message)}
   });
   state.bannerDraft=null;
   if(state.banners){
    if(state.banners.config)state.bannerDraft=structuredClone(state.banners.config);
    else{
     try{
      const defaults=await fetch("/assets/home-banner-defaults.json",{cache:"no-store"});
      if(!defaults.ok)throw Error("Banner defaults unavailable");
      state.bannerDraft=structuredClone(await defaults.json());
     }catch(error){errors.push("Banner 默认设置: "+error.message)}
    }
   }
   dirty=false;
   say(errors.length?"部分模块读取失败（其他模块仍可使用）："+errors.join("；"):"已读取 D1，修改后需要保存。未审核内容不会自动公开。");
   render();
  }catch(e){say("读取失败："+e.message)}
 }
 function render(){
  const container=$("content-form");
  if(!container)return;
  if(!state[requiredData[tab]]){container.innerHTML="<p>当前栏目数据尚未读取成功，请点击「读取线上 D1 内容」重试；其他栏目可继续编辑。</p>";return}
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
  if(tab==="banners"){
   const items=state.bannerDraft?.slides||[];
   const options=(state.settings?.languages?.languages||[])
      .map(x=>[x.code,x.nativeName||x.displayName||x.code]);
   html='<h3>首页 3 张 Banner · 统一图片和链接</h3>'+
     '<p>语言列表由 D1 设置统一管理。可先准备尚未 publishReady 的新语言文案；完整审核且准备好 UI、表单和页面后再启用。图片统一使用 R2 或已发布 /assets/。</p>'+
     '<label class="block-label">当前编辑语言 <select id="cms-banner-language">'+
       options.map(([code,label])=>'<option value="'+code+'"'+(code===bannerLocale?' selected':'')+'>'+label+'</option>').join("")+'</select></label>';
   for(let i=0;i<items.length;i++){
    const item=items[i],copy=bannerLocale==="en"?item:item.translations?.[bannerLocale]||{};
    html+='<section style="padding:14px 0;border-bottom:1px solid #ddd"><h4>Banner '+(i+1)+'</h4>';
    if(bannerLocale==="en"){
     html+=field("b"+i+"-img",item.img,"高清图片路径（R2 /media/... 或现有 /assets/...）")+
       '<div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:10px 0">'+
       '<img data-banner-preview="'+i+'" src="'+esc(item.img)+'" alt="Banner '+(i+1)+' 当前图片" style="width:180px;height:110px;object-fit:contain;border:1px solid #ddd;border-radius:8px">'+
       '<input data-banner-upload="'+i+'" type="file" accept="image/jpeg,image/png,image/webp" aria-label="上传第 '+(i+1)+' 张 Banner 图">'+
       '<button type="button" class="btn ghost" data-banner-upload-btn="'+i+'">上传图片并使用</button></div>'+
       field("b"+i+"-link",item.link,"图片与按钮共同跳转的链接（站内 /路径/ 或 HTTPS）");
    }
    html+=field("b"+i+"-title",copy.title,"标题（常规部分）")+
       field("b"+i+"-highlight",copy.highlight,"标题（强调部分）")+
       field("b"+i+"-description",copy.description,"Banner 说明",3)+
       field("b"+i+"-cta",copy.cta,"按钮显示文字")+
       field("b"+i+"-alt",copy.alt,"图片描述（ALT）")+
       '<p><small>图片：'+esc(item.img)+'　链接：'+esc(item.link)+'</small></p></section>';
   }
   html+='<p>保存前，请逐一核对所有已发布语言的标题和按钮；修改图片和跳转会影响所有语言。</p>'+
    button("保存 3 张 Banner 并等待发布","banners");
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
   html='<h3>产品结构化商详与 SEO</h3><p>可输入完整型号或部分型号（例如 008、LO-008、2095），选择后读取官网现有商详及已保存的 D1 修改。保存草稿不会覆盖原始网站内容。</p>'+
   '<label class="block-label">搜索已有商品型号 <input type="search" id="cms-product-search" placeholder="输入 008 查找 LO-008" autocomplete="off" aria-label="搜索已有商品型号"></label>'+
   '<select id="cms-product-matches" size="6" aria-label="已有商品型号匹配结果" style="width:100%;margin:8px 0 12px"></select>'+
   '<p id="cms-product-current" role="status" aria-live="polite"></p>'+
   field("model","","当前选中型号（从上方选择）")+
   field("name","","英文产品名称")+
   field("material","","材质/部件材料（必须真实核实）")+
   field("capacity","","容量")+
   field("image","","产品主图路径（媒体库上传后复制 /media/product/...）")+
   field("description","","英文产品描述",4)+
   field("seoTitle","","SEO Title")+
   field("seoDescription","","Meta Description",3)+
   '<label class="block-label">状态 <select data-cms-field="status"><option value="draft">草稿（不影响官网）</option><option value="published">审核完成并发布</option></select></label>'+
   button("保存产品到 D1","product");
  }
  if(tab==="new-product"){
   const cats=state.products?.categories||[];
   const existing=(state.products?.items||[]).filter(row=>row.content?.newProduct);
   html='<h3>创建或修改单个商品</h3><p>不做批量导入。先保存 D1 草稿，确认真实型号、材质、容量、图片和说明后再发布。正式发布生成英文商品页；其他语言只有经过对应译文审核才会生成。不会自动复制英文充当翻译。</p>'+
    '<label class="block-label">已保存的新增商品（可选） <select id="cms-new-existing"><option value="">+ 新建单个商品</option>'+
      existing.map(item=>'<option value="'+esc(item.model)+'">'+esc(item.model)+' · '+esc(item.status)+'</option>').join("")+'</select></label>'+
    field("model","","新商品型号 / URL 标识（小写英文字母、数字和短横线；例如 bottle-9001）")+
    '<label class="block-label">产品类别 <select data-cms-field="category">'+
      cats.map(label=>'<option value="'+esc(label)+'">'+esc(label)+'</option>').join("")+'</select></label>'+
    field("name","","英文产品名称（真实名称，不能编造）")+
    field("capacity","","容量（如 750ml；必须实测或确认）")+
    field("material","","材质（如 PP；必须核实）")+
    field("colors","","颜色选项（可选）")+
    field("packing","","包装信息（可选）")+
    field("image","","R2 产品主图路径（先在 R2 图片管理上传，必须存在）")+
    field("description","","英文产品说明（按实际产品填写）",5)+
    field("seoTitle","","SEO Title（最多 90 字符）")+
    field("seoDescription","","Meta Description（最多 240 字符）",3)+
    '<label class="block-label">保存状态 <select data-cms-field="status"><option value="draft">只存草稿，不生成页面</option><option value="published">资料核实完成，进入自动发布队列</option></select></label>'+
    '<p>页面路径：/products/型号/。新产品复用现有列表、详情、图片、SEO 与 R2 溢出模板，无须单独编辑 HTML。</p>'+
    button("保存单个新商品","new-product");
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
    '<label class="block-label">目标语言 <select id="cms-locale">'+
       (state.settings?.languages?.languages||[])
          .filter(x=>x.code!==state.settings?.languages?.sourceLocale)
          .map(x=>'<option value="'+esc(x.code)+'">'+esc(x.nativeName||x.displayName||x.code)+'</option>').join("")+
     '</select></label>'+
    '<label class="block-label">英文原始路径 <select id="cms-locale-route"></select></label>'+
    field("localeTitle","","翻译后的 Title")+
    field("localeDescription","","翻译后的 Meta Description")+
    field("localeHtml","","已完整翻译的 Main HTML",16)+
    button("读取英文页面供翻译","locale-source")+' '+
    button("审核完成并保存","locale-save");
  }
  container.innerHTML=html;
  if(tab==="banners"){
   for(let i=0;i<3;i++){
    container.querySelector('[data-banner-upload-btn="'+i+'"]')?.addEventListener("click",async event=>{
     const file=container.querySelector('[data-banner-upload="'+i+'"]')?.files?.[0];
     if(!file){say("请先选择第 "+(i+1)+" 张新图片");return}
     if(file.size>6*1024*1024){say("单张图片不能超过 6MB");return}
     const uploadButton=event.currentTarget;uploadButton.disabled=true;say("正在上传 Banner "+(i+1)+" 到旭一 R2…");
     try{
      const body=new FormData();body.set("kind","shared");body.set("image",file);
      const sourceAlt=String(state.bannerDraft.slides[i].alt||"").trim();
      if(!sourceAlt)throw Error("请先填写这张 Banner 的英文 ALT，再上传图片");
      body.set("altByLocale",JSON.stringify({en:sourceAlt}));
      const response=await fetch("/api/admin/media",{method:"POST",
       headers:{"authorization":"Bearer "+token()},body,cache:"no-store"});
      const saved=await response.json().catch(()=>({}));
      if(!response.ok||!saved.path)throw Error(saved.error||"上传失败");
      state.bannerDraft.slides[i].img=saved.path;
      const input=container.querySelector('[data-cms-field="b'+i+'-img"]');
      if(input)input.value=saved.path;
      const preview=container.querySelector('[data-banner-preview="'+i+'"]');
      if(preview)preview.src=saved.path;
      say("Banner "+(i+1)+" 图片已上传，尚需点击「保存 3 张 Banner」才会更新官网。");
     }catch(error){say("上传失败："+error.message)}
     finally{uploadButton.disabled=false}
    });
   }
   $("cms-banner-language")?.addEventListener("change",event=>{
    collectBannerFields();
    bannerLocale=event.target.value;
    render();
   });
   for(let i=0;i<3;i++)container.querySelector('[data-cms-field="b'+i+'-img"]')?.addEventListener("change",event=>{
    const row=state.bannerDraft?.slides?.[i];if(row)row.img=event.target.value.trim();
   });
  }

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
   const search=$("cms-product-search"),matches=$("cms-product-matches"),notice=$("cms-product-current");
   model.readOnly=true;
   const known=[...new Set([...(state.products.catalogModels||[]),
     ...(state.products.items||[]).filter(x=>!x.content?.newProduct).map(x=>x.model)])].sort();
   let requestNumber=0;
   const sourceFields=["name","material","capacity","image","description","seoTitle","seoDescription"];
   const resetFields=()=>{for(const key of sourceFields){
     const el=container.querySelector('[data-cms-field="'+key+'"]');if(el)el.value="";
   }container.querySelector('[data-cms-field="status"]').value="draft";};
   async function selectProduct(id){
    if(!known.includes(id))return;
    const request=++requestNumber;
    model.value=id;resetFields();notice.textContent="正在读取 "+id+" 的当前商品页面和 D1 商详…";
    const entry=(state.products.items||[]).find(x=>x.model===id&&!x.content?.newProduct);
    const route="/products/"+(/^(?:LO|G)-/.test(id)?id.toLowerCase():encodeURIComponent(id))+"/";
    let original={},sourceAvailable=false;
    try{
     const response=await fetch(route,{cache:"no-store"});
     if(!response.ok)throw Error("HTTP "+response.status);
     const doc=new DOMParser().parseFromString(await response.text(),"text/html");
     const spec=[...doc.querySelectorAll(".product-detail .spec tr")].map(tr=>({
       label:(tr.querySelector("th")?.textContent||"").trim().toLowerCase(),
       value:(tr.querySelector("td")?.textContent||"").trim()
     }));
     const valueFor=(pattern)=>spec.find(r=>pattern.test(r.label))?.value||"";
     original={
      name:(doc.querySelector(".product-detail h1")?.textContent||"").trim(),
      capacity:valueFor(/capacity|容量/),
      material:valueFor(/material|材质/),
      image:doc.querySelector(".product-detail__main img")?.getAttribute("src")||"",
      description:(doc.querySelector(".product-detail > div:last-child > p.copy-muted")?.textContent||"").trim(),
      seoTitle:doc.title,
      seoDescription:doc.querySelector('meta[name="description"]')?.getAttribute("content")||""
     };
     sourceAvailable=Boolean(original.name);
    }catch(error){if(request===requestNumber)notice.textContent="已选中 "+id+"，但暂无法读取官网当前商品信息："+error.message;}
    if(request!==requestNumber)return;
    for(const [key,val] of Object.entries({...original,...(entry?.content||{})})){
     const el=container.querySelector('[data-cms-field="'+key+'"]');
     if(el&&typeof val==="string")el.value=val;
    }
    container.querySelector('[data-cms-field="status"]').value=entry?.status||"draft";
    const label=entry?"已有 D1 "+(entry.status==="published"?"正式发布":"草稿")+"记录":"当前为官网原始商品，尚无单独 D1 修改记录";
    notice.innerHTML=esc(id)+" · "+esc(label)+"。 <a href=\""+esc(route)+"\" target=\"_blank\" rel=\"noopener\">查看当前商品页 ↗</a>"+
      (sourceAvailable?"":"（未能自动读取全部字段，请先核对再保存）");
   }
   function filterProducts(){
    const query=search.value.trim().toLowerCase();
    const list=known.filter(id=>id.toLowerCase().includes(query));
    matches.innerHTML=list.slice(0,100).map(id=>'<option value="'+esc(id)+'">'+esc(id)+'</option>').join("");
    if(query&&list.length===1)selectProduct(list[0]);
    else if(!list.length)notice.textContent="没有找到匹配的型号";
    else notice.textContent="找到 "+list.length+" 款，选择一个型号查看详情";
   }
   search.addEventListener("input",filterProducts);
   matches.addEventListener("change",()=>selectProduct(matches.value));
   matches.addEventListener("click",()=>selectProduct(matches.value));
   filterProducts();
  } 
  if(tab==="new-product"){
   const select=$("cms-new-existing");
   select.addEventListener("change",()=>{
    const entry=(state.products?.items||[]).find(row=>row.model===select.value&&row.content?.newProduct);
    const keys=["model","name","capacity","material","colors","packing","image","description","seoTitle","seoDescription"];
    for(const key of keys){
     const element=container.querySelector('[data-cms-field="'+key+'"]');
     if(element)element.value=entry?(key==="model"?entry.model:entry.content[key]||""):"";
    }
    container.querySelector('[data-cms-field="status"]').value=entry?.status||"draft";
    if(entry)container.querySelector('[data-cms-field="category"]').value=entry.content.category;
   });
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
   const pages=[...(state.pages.pages||[])];
   for(const entry of state.products?.items||[]){
    if(entry.content?.newProduct&&entry.status==="published"){
     const route="/products/"+entry.model+"/";
     if(!pages.some(p=>p.route===route))pages.push({route,label:entry.content.name||entry.model});
    }
   }
   selector.innerHTML=pages.map(x=>'<option value="'+esc(x.route)+'">'+esc(x.route+" · "+x.label)+'</option>').join("");
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
 function collectBannerFields(){
  if(tab!=="banners")return;
  for(let i=0;i<3;i++){
   const row=state.bannerDraft?.slides?.[i];if(!row)continue;
   if(bannerLocale==="en"){
    row.img=value("b"+i+"-img");
    row.link=value("b"+i+"-link");
   }
   const target=bannerLocale==="en"?row:(row.translations?.[bannerLocale]||{});
   for(const k of ["title","highlight","description","alt","cta"])
    target[k]=value("b"+i+"-"+k);
   if(bannerLocale!=="en")row.translations[bannerLocale]=target;
  }
 }
 const value=(name)=>document.querySelector('#content-form [data-cms-field="'+name+'"]')?.value?.trim()||"";
 async function save(action){
  say("正在验证并保存到 XUYI D1 …");
  try{
   let result;
   if(action==="banners"){
    collectBannerFields();
    if(!window.confirm("确认 3 张 Banner 的图片、按钮链接和五语文案均已检查？保存后进入 D1 定时发布队列。"))return;
    result=await api("home-banners",{config:state.bannerDraft});
   }else if(action==="brand"){
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
   }else if(action==="new-product"){
    const status=value("status");
    if(status==="published"&&!window.confirm("请确认容量、材质、产品图片属于真实型号；确认后保存 D1 并排队生成英文产品页。四语译文需要另外审核。"))return;
    const content={category:value("category"),name:value("name"),material:value("material"),
      capacity:value("capacity"),colors:value("colors"),packing:value("packing"),
      image:value("image"),description:value("description"),
      seoTitle:value("seoTitle"),seoDescription:value("seoDescription")};
    result=await api("product-content",{action:"create_product",model:value("model"),status,content});
   }else if(action==="product"){
    if(!value("model")||(state.products.catalogModels||[]).length&&!state.products.catalogModels.includes(value("model")))
      throw Error("请先从已有商品型号列表中选择产品");
    result=await api("product-content",{action:"save_product",model:value("model"),
     status:value("status"),content:{name:value("name"),material:value("material"),capacity:value("capacity"),
       description:value("description"),image:value("image"),seoTitle:value("seoTitle"),seoDescription:value("seoDescription")}});
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
 for(const tabName of ["brand","banners","navigation","pages","page-body","products","new-product","locales"]){
  $("content-tab-"+tabName)?.addEventListener("click",()=>{tab=tabName;if(!state[requiredData[tab]])load();else render();});
 }
 $("content-load")?.addEventListener("click",load);
 document.querySelector('[data-admin-target="content"]')?.addEventListener("click",()=>{
  if(!state.brand)load();
 });
})();