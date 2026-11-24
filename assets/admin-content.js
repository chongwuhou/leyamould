 /* LEYA MOULD D1 content console. Reuses the shared authenticated admin endpoints. */
(()=>{"use strict";
 const token=()=>sessionStorage.getItem("xuyiAdminToken")||"";
 const $=id=>document.getElementById(id);
 const esc=v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  let state={},tab="brand",dirty=false,bannerLocale="";
  const languageConfig=()=>state.settings?.languages||{};
  const sourceLocale=()=>languageConfig().sourceLocale||"en";
  const requiredData={brand:"brand",banners:"bannerDraft",navigation:"site",pages:"pages",
   "page-body":"pageBodies","structured-copy":"structuredCopy",products:"products","new-product":"products",locales:"locales"};
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
 const arrayEditor=(key,kind,label)=>'<section class="cms-array-editor" data-array-editor="'+esc(key)+'" data-array-kind="'+esc(kind)+'">'+
  '<h4>'+esc(label)+'</h4><div class="cms-array-rows"></div><button type="button" class="btn ghost cms-array-add">+ 添加一项</button>'+
  '<textarea data-cms-field="'+esc(key)+'" hidden></textarea></section>';
 const arrayEditors=new Map();
 function normalizeArrayRows(kind, value){
  if(!Array.isArray(value))return [];
  if(kind==="answers")return value.map(row=>({question:String(row?.question||""),answer:String(row?.answer||"")}));
  if(kind==="groups")return value.map(group=>({title:String(group?.title||""),items:Array.isArray(group?.items)?group.items.map(row=>({question:String(row?.question||""),answer:String(row?.answer||"")})):[]}));
  return value.map(row=>({id:String(row?.id||"section"),eyebrow:String(row?.eyebrow||""),title:String(row?.title||""),body:String(row?.body||""),bullets:Array.isArray(row?.bullets)?row.bullets.join("\\n"):String(row?.bullets||"")}));
 }
 function mountArrayEditor(root,key,kind,initial=[]){
  const editor=root.querySelector('[data-array-editor="'+CSS.escape(key)+'"]');if(!editor)return;
  const rowsRoot=editor.querySelector(".cms-array-rows"),hidden=editor.querySelector('[data-cms-field="'+CSS.escape(key)+'"]');
  let rows=normalizeArrayRows(kind,initial);
  const sync=()=>{hidden.value=JSON.stringify(rows);};
  const render=()=>{
   rowsRoot.innerHTML=rows.map((row,index)=>{
    if(kind==="answers")return '<div class="cms-array-row" data-row="'+index+'"><input data-part="question" placeholder="问题" value="'+esc(row.question)+'"><textarea data-part="answer" rows="3" placeholder="回答">'+esc(row.answer)+'</textarea><button type="button" class="btn danger cms-array-remove">删除</button></div>';
    if(kind==="groups")return '<div class="cms-array-row" data-row="'+index+'"><input data-part="title" placeholder="分组标题" value="'+esc(row.title)+'"><textarea data-part="items" rows="5" placeholder="每行：问题 | 回答">'+esc((row.items||[]).map(item=>item.question+" | "+item.answer).join("\\n"))+'</textarea><button type="button" class="btn danger cms-array-remove">删除分组</button></div>';
    return '<div class="cms-array-row" data-row="'+index+'"><div class="cms-array-grid"><input data-part="id" placeholder="模块标识" value="'+esc(row.id)+'"><input data-part="eyebrow" placeholder="眉标题" value="'+esc(row.eyebrow)+'"><input data-part="title" placeholder="标题" value="'+esc(row.title)+'"></div><textarea data-part="body" rows="3" placeholder="正文">'+esc(row.body)+'</textarea><textarea data-part="bullets" rows="2" placeholder="要点，每行一条">'+esc(row.bullets)+'</textarea><button type="button" class="btn danger cms-array-remove">删除模块</button></div>';
   }).join("");
   rowsRoot.querySelectorAll(".cms-array-row").forEach((rowEl,index)=>rowEl.querySelectorAll("[data-part]").forEach(input=>input.addEventListener("input",()=>{
    const part=input.dataset.part;
    if(kind==="groups"&&part==="items")rows[index].items=String(input.value||"").split(/\\n+/).map(line=>line.split("|")).map(parts=>({question:String(parts.shift()||"").trim(),answer:parts.join("|").trim()})).filter(item=>item.question&&item.answer);
    else rows[index][part]=input.value;
    sync();
   })));
   rowsRoot.querySelectorAll(".cms-array-remove").forEach((btn,index)=>btn.addEventListener("click",()=>{rows.splice(index,1);render();sync();}));
   sync();
  };
  editor.querySelector(".cms-array-add")?.addEventListener("click",()=>{rows.push(kind==="answers"?{question:"",answer:""}:kind==="groups"?{title:"",items:[]}:{id:"section",eyebrow:"",title:"",body:"",bullets:""});render();});
  render();
  const api={set(value){rows=normalizeArrayRows(kind,value);render();},get(){return rows;}};arrayEditors.set(key,api);return api;
 }
 function hydrateArrayEditor(key,value){arrayEditors.get(key)?.set(value);}
 async function load(){
   say("正在读取 LEYA MOULD D1 …");
  try{
   const endpoints=[["brand-config","brand"],["site-config","site"],["site-settings","settings"],["pages","pages"],
    ["product-content","products"],["page-translations","locales"],["page-content","pageBodies"],
    ["structured-copy","structuredCopy"],
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
    bannerLocale=sourceLocale();
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
   const b=state.brand.config||{},c=b.contact||{},id=b.identity||{},footer=b.footer||{},social=b.social||{};
   html='<h3>品牌与全站联系信息</h3><p>邮箱、WhatsApp 同时要核对联系设置模块，避免表单与模板不一致。</p>'+
    field("displayName",id.displayName,"品牌显示名称")+
    field("legalName",id.legalName,"公司名称（请核实实际注册主体）")+
    field("email",c.email,"业务邮箱")+
    field("phoneE164",c.phoneE164,"WhatsApp 号码（国际格式 +86…）")+
    field("address",c.address,"公司地址")+
    '<h4 style="margin:18px 0 6px">顶部信息栏社交链接</h4><p class="muted">顶部栏按源站显示 TikTok、YouTube、Facebook 图标；留空时使用平台首页，可在这里替换为公司账号。</p>'+
    field("socialTiktok",social.tiktok,"TikTok 链接")+
    field("socialYoutube",social.youtube,"YouTube 链接")+
    field("socialFacebook",social.facebook,"Facebook 链接")+
    field("footerAbout",footer.about,"页脚介绍",3)+
    button("保存品牌并排队发布","brand");
  }
  if(tab==="banners"){
    const items=state.bannerDraft?.slides||[],source=sourceLocale();
   const options=(state.settings?.languages?.languages||[])
      .map(x=>[x.code,x.nativeName||x.displayName||x.code]);
   html='<h3>首页 3 张 Banner · 统一图片和链接</h3>'+
     '<p>语言列表由 D1 设置统一管理。可先准备尚未 publishReady 的新语言文案；完整审核且准备好 UI、表单和页面后再启用。图片统一使用 R2 或已发布 /assets/。</p>'+
     '<label class="block-label">当前编辑语言 <select id="cms-banner-language">'+
       options.map(([code,label])=>'<option value="'+code+'"'+(code===bannerLocale?' selected':'')+'>'+label+'</option>').join("")+'</select></label>';
   for(let i=0;i<items.length;i++){
     const item=items[i],copy=bannerLocale===source?item:item.translations?.[bannerLocale]||{};
    html+='<section style="padding:14px 0;border-bottom:1px solid #ddd"><h4>Banner '+(i+1)+'</h4>';
     if(bannerLocale===source){
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
   html='<h3>导航与跳转管理</h3><p>数组字段与 LEYA MOULD site-config CMS 一致。仅允许网站实际路径或经核准的外链，编辑前请核对目标 URL。</p>'+
    field("navigation",JSON.stringify(state.site.navigation||[],null,2),"导航 JSON：id / parentId / label / url / sortOrder",16)+
    field("redirects",JSON.stringify(state.site.redirects||[],null,2),"301/302 跳转规则 JSON",7)+
    button("保存导航","navigation")+' '+button("保存跳转规则","redirects");
  }
  if(tab==="pages"){
   html='<h3>逐页 SEO 设置</h3><p>网站尚未正式上线时请保持 noindex。正式上线后可按页面独立控制 robots 和 sitemap；标题、描述及这些开关都会进入 D1 并参与下一次完整构建。</p>'+ 
   '<label>选择页面 <input type="search" id="cms-route-filter" placeholder="搜索 URL / 标题" aria-label="搜索页面"></label>'+
   '<select id="cms-route" size="9" style="width:100%;margin:10px 0"></select>'+
   field("seoTitle","","SEO Title（最多 90 字符）")+
   field("seoDescription","","Meta Description（最多 240 字符）")+
   '<label class="block-label">页面 Robots <select data-cms-field="robots"><option value="noindex,nofollow">noindex,nofollow</option><option value="noindex,follow">noindex,follow</option><option value="index,follow">index,follow</option></select></label>'+ 
   '<label class="block-label"><input type="checkbox" data-cms-field="sitemapEnabled"> 加入 sitemap.xml</label>'+ 
   button("保存所选页面 SEO","pages");
  }
  if(tab==="products"){
    html='<h3>模具类别内容与 SEO</h3><p>选择九个已配置的模具类别，编辑标题、说明、技术要点和 SEO。保存草稿不会改变前端样式，只会在下一次完整构建时更新数据内容。</p>'+
    '<label class="block-label">搜索模具类别 <input type="search" id="cms-product-search" placeholder="输入 cap、oil 或 handle" autocomplete="off" aria-label="搜索模具类别"></label>'+
    '<select id="cms-product-matches" size="6" aria-label="模具类别匹配结果" style="width:100%;margin:8px 0 12px"></select>'+
   '<p id="cms-product-current" role="status" aria-live="polite"></p>'+
    field("model","","当前类别 slug（从上方选择）")+
    field("title","","英文类别标题")+
    field("navTitle","","导航显示名称")+
    field("short","","类别简述",3)+
    field("detail","","类别详细说明",4)+
    field("meta","","规格标签（例如 48 Cavity · Hot Runner）")+
    field("image","","类别主图路径（媒体库上传后复制 /media/...）")+
     field("checks","","技术核对要点（每行一条）",4)+
     field("body","","结构化正文导语（纯文本）",5)+
     arrayEditor("sections","sections","英文正文区块")+
     arrayEditor("faqs","answers","英文产品 FAQ")+
     field("bodyEs","","西班牙语结构化正文导语（纯文本）",5)+
     arrayEditor("sectionsEs","sections","西班牙语正文区块")+
     arrayEditor("faqsEs","answers","西班牙语产品 FAQ")+
   field("seoTitle","","SEO Title")+
   field("seoDescription","","Meta Description",3)+
   '<label class="block-label">状态 <select data-cms-field="status"><option value="draft">草稿（不影响官网）</option><option value="published">审核完成并发布</option></select></label>'+
   button("保存产品到 D1","product");
  }
  if(tab==="structured-copy"){
   const routes=state.structuredCopy?.routes||["/","/contact/","/faq/"];
   html='<h3>结构化页面正文 · D1</h3><p>只维护可编辑文案和问答数组，不接触 HTML/CSS。保存后由完整构建生成页面；已有后台编辑会按当前语种和路径覆盖。</p>'+
    '<label class="block-label">语种 <select id="cms-structured-locale">'+(state.structuredCopy?.locales||["en","es"]).map(locale=>'<option value="'+esc(locale)+'">'+esc(locale)+"</option>").join("")+'</select></label>'+ 
    '<label class="block-label">页面 <select id="cms-structured-route">'+routes.map(route=>'<option value="'+esc(route)+'">'+esc(route)+"</option>").join("")+'</select></label>'+ 
    field("structuredEyebrow","","眉标题")+
    field("structuredTitle","","模块标题")+
    field("structuredSubtitle","","模块说明",3)+
    arrayEditor("quickAnswers","answers","Quick Answers（问题与回答）")+
    arrayEditor("groups","groups","FAQ 分组")+
    arrayEditor("sections","sections","结构化正文区块")+
    '<textarea data-cms-field="structuredJson" hidden></textarea>'+ 
    button("保存结构化正文","structured-copy");
  }
  if(tab==="new-product"){
   const cats=state.products?.categories||[];
   html='<h3>工厂目录安全批量导入</h3><p>选择由工厂画册整理的 JSON 清单。系统通过现有后台媒体 API 上传图片到 R2，再通过现有产品 CMS API 创建 D1 商品；已有型号自动跳过，不覆盖原有商品或人工编辑。发布后生成英文商品页，其他语言需完成对应译文后再生成。</p>'+
    '<label class="block-label">产品目录 JSON <input id="cms-new-bulk-file" type="file" accept=".json,application/json"></label>'+
    button("安全导入产品目录（创建式，不覆盖已有商品）","new-product-bulk")+
    '<label class="block-label">编辑已导入的新商品 <select id="cms-new-existing"><option value="">新建商品</option>'+
      (state.products?.items||[]).filter(row=>row.content?.newProduct===true).map(row=>'<option value="'+esc(row.model)+'">'+esc((row.content?.factoryModel||row.model)+" · "+(row.content?.name||"")+" · "+(row.status||"draft"))+'</option>').join("")+'</select></label>'+
     '<p>选择已导入的新商品可更新其 D1 资料；旧目录型号不会在此修改。</p>'+
     '<hr><h3>单个商品创建</h3>'+
    field("model","","新商品型号 / URL 标识（小写英文字母、数字和短横线）")+
    field("factoryModel","","工厂画册印刷型号（保留原大小写）")+
    '<label class="block-label">产品类别 <select data-cms-field="category">'+
      cats.map(label=>'<option value="'+esc(label)+'">'+esc(label)+'</option>').join("")+'</select></label>'+
    field("name","","英文产品名称")+
    field("capacity","","容量（保留画册原始规格与多容量关系）")+
    field("material","","材质（未确认时明确标注待核实）")+
    field("dimensions","","产品尺寸（按画册原文）")+
    field("unit_weight","","单个产品重量")+
    field("temperature_range","","温度范围")+
    field("colors","","颜色选项（可选）")+
    field("packing","","单品包装信息（可选）")+
    field("retail_box_size","","彩盒尺寸")+
    field("carton_quantity","","外箱装量")+
    field("carton_size","","外箱尺寸")+
    field("carton_gross_weight","","外箱毛重")+
    field("catalogOunceLabel","","画册印刷的 oz 标识")+
    field("sourceDocument","","来源文件名")+
    field("sourcePage","","来源页码")+
    field("sourceNotes","","画册备注及需要确认的规格",4)+
    field("qcStatus","","资料核验状态")+
    field("imageReviewStatus","","图片审核状态")+
    field("image","","R2 产品主图路径")+
    field("description","","英文产品说明（保留全部已知信息及待确认事项）",5)+
    field("seoTitle","","SEO Title（最多 90 字符）")+
    field("seoDescription","","Meta Description（最多 240 字符）",3)+
    '<label class="block-label">保存状态 <select data-cms-field="status"><option value="draft">只存草稿，不生成页面</option><option value="published">发布（仅已注册的模具类别）</option></select></label>'+
    '<p>页面路径：/product/类别-slug.html。新增类别先保存草稿；完成模具目录、公开路由和详情模板注册后，才允许发布。</p>'+
    button("保存单个新商品","new-product");
  }
  if(tab==="page-body"){
   html='<h3>普通页面正文管理</h3><p>管理 About、Capabilities、Manufacturing、Quality Control、Contact 等页面；Blog 与产品详情各用其自身编辑器。草稿不影响前台，审核后发布才会覆盖现有页面主内容。</p>'+
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
  arrayEditors.clear();
  container.innerHTML=html;
  container.querySelectorAll("[data-array-editor]").forEach(editor=>mountArrayEditor(container,editor.dataset.arrayEditor,editor.dataset.arrayKind,[]));
  if(tab==="banners"){
   for(let i=0;i<3;i++){
    container.querySelector('[data-banner-upload-btn="'+i+'"]')?.addEventListener("click",async event=>{
     const file=container.querySelector('[data-banner-upload="'+i+'"]')?.files?.[0];
     if(!file){say("请先选择第 "+(i+1)+" 张新图片");return}
     if(file.size>6*1024*1024){say("单张图片不能超过 6MB");return}
     const uploadButton=event.currentTarget;uploadButton.disabled=true;say("正在上传 Banner "+(i+1)+" 到 LEYA MOULD R2…");
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

  if(tab==="structured-copy"){
   const locale=$("cms-structured-locale"),route=$("cms-structured-route"),target=container.querySelector('[data-cms-field="structuredJson"]');
   const fill=()=>{
    const data=state.structuredCopy?.pageCopy?.[locale?.value]?.[route?.value]||{};
    for(const [key,value] of [["structuredEyebrow",data.eyebrow||""],["structuredTitle",data.title||""],["structuredSubtitle",data.subtitle||""]]){const el=container.querySelector('[data-cms-field="'+key+'"]');if(el)el.value=value;}
    hydrateArrayEditor("quickAnswers",data.quickAnswers||[]);hydrateArrayEditor("groups",data.groups||[]);hydrateArrayEditor("sections",data.sections||[]);
    if(target)target.value=JSON.stringify({eyebrow:data.eyebrow||"",title:data.title||"",subtitle:data.subtitle||"",quickAnswers:data.quickAnswers||[],groups:data.groups||[],sections:data.sections||[]},null,2);
   };
   locale?.addEventListener("change",fill);route?.addEventListener("change",fill);fill();
  }

  container.querySelectorAll("[data-cms-action]").forEach(el=>el.addEventListener("click",()=>save(el.dataset.cmsAction)));
  if(tab==="pages"){
   const input=$("cms-route-filter"),sel=$("cms-route");
   const fill=()=>{const q=input.value.trim().toLowerCase();
    sel.innerHTML=(state.pages.pages||[]).filter(x=>(x.route+" "+x.label).toLowerCase().includes(q))
      .map(x=>'<option value="'+esc(x.route)+'">'+esc(x.route+" · "+x.label)+'</option>').join("");sel.selectedIndex=0;selectPage()};
   const selectPage=()=>{const row=(state.pages.pages||[]).find(x=>x.route===sel.value);
    const t=container.querySelector('[data-cms-field="seoTitle"]'),d=container.querySelector('[data-cms-field="seoDescription"]'),r=container.querySelector('[data-cms-field="robots"]'),s=container.querySelector('[data-cms-field="sitemapEnabled"]');
    if(t)t.value=row?.seoTitle||"";if(d)d.value=row?.metaDescription||"";if(r)r.value=row?.robots||"noindex,nofollow";if(s)s.checked=row?.sitemapEnabled===true;};
   input.oninput=fill;sel.onchange=selectPage;fill();
  }
  if(tab==="products"){
   const model=container.querySelector('[data-cms-field="model"]');
   const search=$("cms-product-search"),matches=$("cms-product-matches"),notice=$("cms-product-current");
   model.readOnly=true;
   const known=[...new Set([...(state.products.catalogModels||[]),
     ...(state.products.items||[]).filter(x=>!x.content?.newProduct).map(x=>x.model)])].sort();
   let requestNumber=0;
     const sourceFields=["title","navTitle","short","detail","meta","image","checks","body","sections","faqs","bodyEs","sectionsEs","faqsEs","seoTitle","seoDescription"];
     const resetFields=()=>{for(const key of sourceFields){
      const el=container.querySelector('[data-cms-field="'+key+'"]');if(el)el.value=((key.includes("sections")||key.includes("faqs"))?"[]":"");
   }container.querySelector('[data-cms-field="status"]').value="draft";};
   async function selectProduct(id){
    if(!known.includes(id))return;
    const request=++requestNumber;
     model.value=id;resetFields();notice.textContent="正在读取 "+id+" 的当前类别页面和 D1 内容…";
     const entry=(state.products.items||[]).find(x=>x.model===id&&!x.content?.newProduct);
     const route=(state.products.modelRoutes||{})[id]||"/product/"+encodeURIComponent(id)+".html";
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
       title:(doc.querySelector("main h1,h1")?.textContent||"").trim(),
       navTitle:(doc.querySelector("main h1,h1")?.textContent||"").trim(),
       short:(doc.querySelector(".mould-hero-subtitle")?.textContent||"").trim(),
       detail:(doc.querySelector(".mould-detail-page .mould-section-heading p")?.textContent||"").trim(),
       image:doc.querySelector("main img,.mould-detail-page img")?.getAttribute("src")||"",
      seoTitle:doc.title,
      seoDescription:doc.querySelector('meta[name="description"]')?.getAttribute("content")||""
     };
      sourceAvailable=Boolean(original.title);
    }catch(error){if(request===requestNumber)notice.textContent="已选中 "+id+"，但暂无法读取官网当前商品信息："+error.message;}
    if(request!==requestNumber)return;
     for(const [key,val] of Object.entries({...original,...(entry?.content||{})})){
      const el=container.querySelector('[data-cms-field="'+key+'"]');
      if(!el)continue;
       if(["sections","faqs","sectionsEs","faqsEs"].includes(key)&&Array.isArray(val))el.value=JSON.stringify(val,null,2);
       else if(key==="checks"&&Array.isArray(val))el.value=val.join("\\n");
      else if(typeof val==="string")el.value=val;
    }
    hydrateArrayEditor("sections",entry?.content?.sections||[]);hydrateArrayEditor("faqs",entry?.content?.faqs||[]);
    hydrateArrayEditor("sectionsEs",entry?.content?.sectionsEs||[]);hydrateArrayEditor("faqsEs",entry?.content?.faqsEs||[]);
    container.querySelector('[data-cms-field="status"]').value=entry?.status||"draft";
    const label=entry?"已有 D1 "+(entry.status==="published"?"正式发布":"草稿")+"记录":"当前为官网原始商品，尚无单独 D1 修改记录";
     notice.innerHTML=esc(id)+" · "+esc(label)+"。 <a href=\""+esc(route)+"\" target=\"_blank\" rel=\"noopener\">查看当前类别页 ↗</a>"+
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
    if(select)select.addEventListener("change",()=>{
     const entry=(state.products?.items||[]).find(row=>row.model===select.value&&row.content?.newProduct===true);
     const keys=["model","factoryModel","name","capacity","material","dimensions","unit_weight","temperature_range","colors","packing","retail_box_size","carton_quantity","carton_size","carton_gross_weight","catalogOunceLabel","sourceDocument","sourcePage","sourceNotes","qcStatus","imageReviewStatus","image","description","seoTitle","seoDescription"];
     for(const key of keys){
      const element=container.querySelector('[data-cms-field="'+key+'"]');
      if(element)element.value=entry?(key==="model"?entry.model:entry.content[key]||""):"";
     }
     const modelField=container.querySelector('[data-cms-field="model"]');if(modelField)modelField.readOnly=!!entry;
     const statusField=container.querySelector('[data-cms-field="status"]');if(statusField)statusField.value=entry?.status||"draft";
     const categoryField=container.querySelector('[data-cms-field="category"]');if(categoryField)categoryField.value=entry?.content?.category||categoryField.options[0]?.value||"";
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
      const route=(state.products.modelRoutes||{})[entry.model]||"/product/"+entry.model+".html";
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
   const source=sourceLocale();
  for(let i=0;i<3;i++){
   const row=state.bannerDraft?.slides?.[i];if(!row)continue;
    if(bannerLocale===source){
    row.img=value("b"+i+"-img");
    row.link=value("b"+i+"-link");
   }
    const target=bannerLocale===source?row:(row.translations?.[bannerLocale]||{});
   for(const k of ["title","highlight","description","alt","cta"])
    target[k]=value("b"+i+"-"+k);
    if(bannerLocale!==source)row.translations[bannerLocale]=target;
  }
 }
 const value=(name)=>document.querySelector('#content-form [data-cms-field="'+name+'"]')?.value?.trim()||"";
 async function save(action){
     say("正在验证并保存到 LEYA MOULD D1 …");
  try{
   let result;
   if(action==="banners"){
    collectBannerFields();
     if(!window.confirm("确认 3 张 Banner 的图片、按钮链接和已配置语种文案均已检查？保存后进入 D1 定时发布队列。"))return;
    result=await api("home-banners",{config:state.bannerDraft});
   }else if(action==="brand"){
    const b=structuredClone(state.brand.config);
    b.identity={...(b.identity||{}),displayName:value("displayName"),legalName:value("legalName")};
    b.contact={...(b.contact||{}),email:value("email"),phoneE164:value("phoneE164"),address:value("address"),whatsappUrl:"https://wa.me/"+value("phoneE164").replace(/\D/g,"")};
    b.social={...(b.social||{}),tiktok:value("socialTiktok"),youtube:value("socialYoutube"),facebook:value("socialFacebook")};
    b.footer={...(b.footer||{}),about:value("footerAbout")};
    result=await api("brand-config",{config:b});
   }else if(action==="navigation"||action==="redirects"){
    let rows;try{rows=JSON.parse(value(action==="navigation"?"navigation":"redirects"))}catch{throw Error("请输入正确的 JSON 数组")}
    result=await api("site-config",{action:action==="navigation"?"save_navigation":"save_redirects",[action]:rows});
   }else if(action==="pages"){
    const selected=$("cms-route").value;
    const robots=container.querySelector('[data-cms-field="robots"]')?.value||"noindex,nofollow";
    const sitemapEnabled=Boolean(container.querySelector('[data-cms-field="sitemapEnabled"]')?.checked);
    const rows=state.pages.pages.map(row=>({...row}));
    const target=rows.find(x=>x.route===selected);if(!target)throw Error("请先选择页面");
    target.seoTitle=value("seoTitle");target.metaDescription=value("seoDescription");
    target.robots=robots;target.sitemapEnabled=sitemapEnabled;
    result=await api("pages",{action:"save_pages",pages:rows});
    }else if(action==="new-product"){
     const selectedExisting=$("cms-new-existing")?.value||"";
     const enteredModel=value("model").trim().toLowerCase();
     const model=selectedExisting||enteredModel;
     if(!model)throw Error("请输入新商品型号");
     if(selectedExisting&&enteredModel!==selectedExisting)throw Error("已选商品的型号标识不可修改");
     const exists=(state.products?.items||[]).some(row=>String(row.model).toLowerCase()===model)||(state.products?.catalogModels||[]).some(row=>String(row).toLowerCase()===model);
     if(!selectedExisting&&exists)throw Error("该型号已存在；请在编辑列表中选择后更新，创建操作不会覆盖已有商品。");
     const existingEntry=selectedExisting?(state.products?.items||[]).find(row=>row.model===selectedExisting&&row.content?.newProduct===true):null;
     const status=value("status");
     if(status==="published"&&!window.confirm(selectedExisting?"确认更新这款已导入的新商品？将使用当前 D1 资料和 R2 主图生成源语言商品页；其他语种仍需审核译文。":"请确认容量、材质、产品图片属于真实型号；确认后保存 D1 并排队生成源语言商品页。其他语种译文需要另外审核。"))return;
     const content={category:value("category"),factoryModel:value("factoryModel"),name:value("name"),material:value("material"),
      capacity:value("capacity"),dimensions:value("dimensions"),unit_weight:value("unit_weight"),temperature_range:value("temperature_range"),
      colors:value("colors"),packing:value("packing"),retail_box_size:value("retail_box_size"),carton_quantity:value("carton_quantity"),
      carton_size:value("carton_size"),carton_gross_weight:value("carton_gross_weight"),catalogOunceLabel:value("catalogOunceLabel"),
      sourceDocument:value("sourceDocument"),sourcePage:value("sourcePage"),sourceNotes:value("sourceNotes"),qcStatus:value("qcStatus"),
      imageReviewStatus:existingEntry&&existingEntry.content.image!==value("image")?"pending_manual_review":value("imageReviewStatus"),image:value("image"),description:value("description"),
      seoTitle:value("seoTitle"),seoDescription:value("seoDescription"),
      sourceSha256:existingEntry?.content?.sourceSha256||"",
      sourceImageSha256:existingEntry?.content?.image===value("image")?(existingEntry.content.sourceImageSha256||""):""};
     result=await api("product-content",{action:"create_product",createOnly:!selectedExisting,model,status,content});
   }else if(action==="new-product-bulk"){
    const file=document.getElementById("cms-new-bulk-file")?.files?.[0];
    if(!file)throw Error("请先选择工厂目录 JSON 文件");
    if(file.size>25*1024*1024)throw Error("目录文件超过 25MB，请压缩图片后重新生成");
    let manifest;try{manifest=JSON.parse(await file.text())}catch{throw Error("JSON 文件无法解析")}
    if(manifest.schemaVersion!==1||!Array.isArray(manifest.records)||manifest.records.length<1||manifest.records.length>100)
      throw Error("目录清单格式不正确：只支持 1–100 个产品");
    if(manifest.recordCount!==undefined&&manifest.recordCount!==manifest.records.length)
      throw Error("目录记录数与清单声明不一致");
    if(manifest.sourceDocument&&!/^[0-9a-f]{64}$/i.test(manifest.sourceSha256||""))
      throw Error("来源文件缺少有效 SHA-256 校验值");
    const seen=new Set();
    for(const row of manifest.records){
      if(!row||typeof row.model!=="string"||!/^[a-z0-9][a-z0-9-]{1,63}$/.test(row.model)||seen.has(row.model))
        throw Error("目录中存在无效或重复型号");
      if(!row.content||typeof row.content!=="object"||typeof row.imageBase64!=="string"||row.imageBase64.length<100||row.imageMime!=="image/webp"||!(/^[0-9a-f]{64}$/i.test(row.imageSha256||"")))
        throw Error("型号 "+row.model+" 缺少商品资料、完整图片或 SHA-256 校验值");
      const locales=(state.settings?.languages?.languages||[]).filter(language=>language.enabled!==false&&language.publishReady!==false).map(language=>language.code);
      if(!row.imageAlt||locales.some(locale=>typeof row.imageAlt[locale]!=="string"||!row.imageAlt[locale].trim()))
       throw Error("型号 "+row.model+" 缺少已配置语种的图片 ALT");
      seen.add(row.model);
    }
    const existing=new Set((state.products?.items||[]).map(row=>String(row.model).toLowerCase()));
    (state.products?.catalogModels||[]).forEach(model=>existing.add(String(model).toLowerCase()));
    const already=manifest.records.filter(row=>existing.has(row.model)).map(row=>row.model);
    const fresh=manifest.records.filter(row=>!existing.has(row.model));
    if(!fresh.length){say("导入结束：清单中的型号已全部存在，未修改任何商品。");return}
    if(!window.confirm("来源："+String(manifest.sourceDocument||"工厂目录")+"\n清单："+manifest.records.length+" 款\n本次新建："+fresh.length+" 款\n已存在跳过："+already.length+" 款\n\n将逐款上传原始产品图片到 R2，并通过后台 CMS API 创建已发布英文商品页。已有型号不会覆盖。是否继续？"))return;
    const created=[],skipped=[...already],failed=[];
    for(let i=0;i<fresh.length;i++){
      const row=fresh[i];let imagePath="";
      say("正在导入 "+(i+1)+"/"+fresh.length+"："+row.model+"（上传原始图片）");
      try{
        const bytes=Uint8Array.from(atob(row.imageBase64),ch=>ch.charCodeAt(0));
        const digest=await crypto.subtle.digest("SHA-256",bytes);
        const hash=Array.from(new Uint8Array(digest),byte=>byte.toString(16).padStart(2,"0")).join("");
        if(hash!==row.imageSha256.toLowerCase())throw Error("产品图片 SHA-256 校验失败");
        const imageFile=new File([bytes],row.model+".webp",{type:"image/webp"});
        const form=new FormData();form.set("kind","product");form.set("image",imageFile);
        form.set("altByLocale",JSON.stringify(row.imageAlt||{[sourceLocale()]:(row.content.factoryModel||row.model)+" "+(row.content.name||"mould")+" factory catalog product image"}));
        const upload=await fetch("/api/admin/media",{method:"POST",headers:{authorization:"Bearer "+token()},body:form,cache:"no-store"});
        const media=await upload.json().catch(()=>({}));
        if(!upload.ok||!media.path)throw Error(media.error||"R2 图片上传失败");
        imagePath=media.path;
        const content={...row.content,sourceDocument:manifest.sourceDocument||row.content.sourceDocument||"",sourceSha256:manifest.sourceSha256||row.content.sourceSha256||"",sourceImageSha256:row.imageSha256,image:imagePath};
        const saved=await api("product-content",{action:"create_product",createOnly:true,model:row.model,status:row.status||"published",content});
        if(!saved?.saved)throw Error(saved?.error||"CMS 未确认保存");
        created.push(row.model);
      }catch(error){
        if(imagePath){
          const filename=imagePath.split("/").pop();
          await fetch("/api/admin/media?kind=product&filename="+encodeURIComponent(filename),{method:"DELETE",headers:{authorization:"Bearer "+token()},cache:"no-store"}).catch(()=>{});
        }
        const message=String(error?.message||error);
        if(/already exists|already published|409/i.test(message))skipped.push(row.model);
        else failed.push({model:row.model,error:message});
      }
    }
    await load();
    const details=failed.slice(0,12).map(item=>item.model+": "+item.error).join("；");
    say("目录导入完成：新建 "+created.length+" 款；跳过 "+skipped.length+" 款；失败 "+failed.length+" 款。"+(details?"失败明细："+details:"")+" 已有商品未覆盖。");
    return;
    }else if(action==="product"){
     if(!value("model")||(state.products.catalogModels||[]).length&&!state.products.catalogModels.includes(value("model")))
       throw Error("请先从已配置的模具类别列表中选择类别");
     const checks=String(value("checks")||"").split(/\\n+/).map(item=>item.trim()).filter(Boolean);
      const sections=arrayEditors.get("sections")?.get()||[],faqs=arrayEditors.get("faqs")?.get()||[],sectionsEs=arrayEditors.get("sectionsEs")?.get()||[],faqsEs=arrayEditors.get("faqsEs")?.get()||[];
      result=await api("product-content",{action:"save_product",model:value("model"),
       status:value("status"),content:{title:value("title"),navTitle:value("navTitle"),short:value("short"),detail:value("detail"),meta:value("meta"),
         image:value("image"),checks,body:value("body"),sections,faqs,bodyEs:value("bodyEs"),sectionsEs,faqsEs,seoTitle:value("seoTitle"),seoDescription:value("seoDescription")}});
    }else if(action==="structured-copy"){
     const content={eyebrow:value("structuredEyebrow"),title:value("structuredTitle"),subtitle:value("structuredSubtitle"),quickAnswers:arrayEditors.get("quickAnswers")?.get()||[],groups:arrayEditors.get("groups")?.get()||[],sections:arrayEditors.get("sections")?.get()||[]};
     const target=document.querySelector('[data-cms-field="structuredJson"]');if(target)target.value=JSON.stringify(content);
     result=await api("structured-copy",{action:"save_page_copy",locale:$('cms-structured-locale').value,route:$('cms-structured-route').value,content});
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
  for(const tabName of ["brand","banners","navigation","pages","page-body","structured-copy","products","new-product","locales"]){
  $("content-tab-"+tabName)?.addEventListener("click",()=>{tab=tabName;if(!state[requiredData[tab]])load();else render();});
 }
 $("content-load")?.addEventListener("click",load);
 document.querySelector('[data-admin-target="content"]')?.addEventListener("click",()=>{
  if(!state.brand)load();
 });
})();




