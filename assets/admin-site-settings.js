(() => {
  const SETTINGS="/api/admin/site-settings", TRANSLATIONS="/api/admin/translations", TOKEN="xuyiAdminToken";
  const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
  const esc=v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const slug=v=>String(v||"").toLowerCase().normalize("NFKD").replace(/[\u0300-\u036f]/g,"").replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"");
  const token=()=>sessionStorage.getItem(TOKEN)||"";
  let settings=null, translations={jobs:[],settings:{},languages:{},secretStatus:{}}, lastToken="";

  async function api(url,method="GET",body=null){
    const t=token(); if(!t) throw new Error("请先登录后台");
    const r=await fetch(url,{method,headers:{...(body?{"content-type":"application/json"}:{}),authorization:"Bearer "+t},body:body?JSON.stringify(body):undefined,cache:"no-store"});
    const d=await r.json().catch(()=>({})); if(!r.ok) throw new Error(d.error||("HTTP "+r.status)); return d;
  }
  function langRow(x={}){
    const def=settings?.languages?.defaultLocale===x.code, src=settings?.languages?.sourceLocale===x.code;
    return `<tr class="language-row"><td><input class="lang-code" value="${esc(x.code||"")}" placeholder="fr"></td><td><input class="lang-display" value="${esc(x.displayName||"")}"></td><td><input class="lang-native" value="${esc(x.nativeName||"")}"></td><td><input class="lang-prefix" value="${esc(x.pathPrefix||"")}"></td><td><input class="lang-sort" type="number" value="${Number(x.sortOrder||10)}"></td><td><input class="lang-default" name="default-locale" type="radio" ${def?"checked":""}></td><td><input class="lang-source" name="source-locale" type="radio" ${src?"checked":""}></td><td><input class="lang-enabled" type="checkbox" ${x.enabled!==false?"checked":""}></td><td><input class="lang-ready" type="checkbox" ${x.publishReady!==false?"checked":""}></td><td><button class="btn small ghost remove-language" type="button">删除</button></td></tr>`;
  }
  function renderLangEditors(){
    const host=$("#language-ui-editors"), body=$("#language-config-body"); if(!host||!body||!settings)return;
    const old=new Map((settings.languages?.languages||[]).map(x=>[x.code,x.uiText||{}]));
    host.innerHTML=$$(".language-row",body).map(row=>{
      const code=$(".lang-code",row).value.trim().toLowerCase().replaceAll("_","-"); if(!code)return "";
      const prior=$(`.language-ui-json[data-code="${CSS.escape(code)}"]`);
      const value=prior?prior.value:JSON.stringify(old.get(code)||{},null,2);
      return `<label class="block-label">${esc(code.toUpperCase())} UI JSON<textarea class="language-ui-json" data-code="${esc(code)}" rows="6" spellcheck="false">${esc(value)}</textarea></label>`;
    }).join("");
  }
  function renderLanguages(){
    const body=$("#language-config-body"); if(!body||!settings)return;
    body.innerHTML=(settings.languages?.languages||[]).map(langRow).join("");
    $$(".remove-language",body).forEach(b=>b.onclick=()=>{if($$(".language-row",body).length>1){b.closest("tr").remove();renderLangEditors();}});
    $$(".lang-code",body).forEach(i=>i.onchange=renderLangEditors); renderLangEditors();
  }
  function collectLanguages(){
    const rows=$$(".language-row",$("#language-config-body")), old=new Map((settings.languages?.languages||[]).map(x=>[x.code,x.uiText||{}]));
    const languages=rows.map(row=>{
      const code=$(".lang-code",row).value.trim().toLowerCase().replaceAll("_","-");
      let uiText=old.get(code)||{}; const editor=$(`.language-ui-json[data-code="${CSS.escape(code)}"]`);
      if(editor?.value.trim()){try{uiText=JSON.parse(editor.value)}catch{throw new Error(code+" UI JSON 格式错误")}}
      return {code,displayName:$(".lang-display",row).value.trim(),nativeName:$(".lang-native",row).value.trim(),pathPrefix:$(".lang-prefix",row).value.trim(),sortOrder:Number($(".lang-sort",row).value||0),enabled:$(".lang-enabled",row).checked,publishReady:$(".lang-ready",row).checked,uiText};
    });
    const di=rows.findIndex(r=>$(".lang-default",r).checked), si=rows.findIndex(r=>$(".lang-source",r).checked);
    if(di<0||si<0)throw new Error("必须选择默认语言和源语言");
    return {schemaVersion:1,defaultLocale:languages[di].code,sourceLocale:languages[si].code,languages};
  }
  function contactRow(x={}){
    return `<tr class="contact-row" data-id="${esc(x.id||"")}"><td><input class="contact-name" value="${esc(x.name||"")}" placeholder="Alice"><input class="contact-title" value="${esc(x.title||"")}" placeholder="Sales Manager"></td><td><input class="contact-email" type="email" value="${esc(x.email||"")}"></td><td><input class="contact-phone-display" value="${esc(x.phoneDisplay||"")}" placeholder="+86 ..."><input class="contact-phone-e164" value="${esc(x.phoneE164||"")}" placeholder="+86138..."><input class="contact-whatsapp" value="${esc(x.whatsappUrl||"")}" placeholder="https://wa.me/..."></td><td><input class="contact-locales" value="${esc((x.locales||[]).join(","))}" placeholder="en,de"></td><td><input class="contact-regions" value="${esc((x.regions||[]).join(","))}" placeholder="middle-east,uae"></td><td><input class="contact-avatar" value="${esc(x.avatarUrl||"")}" placeholder="/assets/..."></td><td><input class="contact-sort" type="number" value="${Number(x.sortOrder||10)}"></td><td><input class="contact-default" name="default-contact" type="radio" ${x.isDefault?"checked":""}></td><td><input class="contact-enabled" type="checkbox" ${x.enabled!==false?"checked":""}></td><td><button class="btn small ghost remove-contact" type="button">删除</button></td></tr>`;
  }
  function renderContacts(){
    const body=$("#contact-config-body"); if(!body||!settings)return;
    body.innerHTML=(settings.contacts?.contacts||[]).map(contactRow).join("");
    $$(".remove-contact",body).forEach(b=>b.onclick=()=>{if($$(".contact-row",body).length>1)b.closest("tr").remove();});
  }
  function collectContacts(){
    return {schemaVersion:1,contacts:$$(".contact-row",$("#contact-config-body")).map((r,i)=>({
      id:r.dataset.id||slug($(".contact-name",r).value)||("contact-"+(i+1)),name:$(".contact-name",r).value.trim(),title:$(".contact-title",r).value.trim(),email:$(".contact-email",r).value.trim(),
      phoneDisplay:$(".contact-phone-display",r).value.trim(),phoneE164:$(".contact-phone-e164",r).value.trim(),whatsappUrl:$(".contact-whatsapp",r).value.trim(),avatarUrl:$(".contact-avatar",r).value.trim(),
      locales:$(".contact-locales",r).value.split(",").map(x=>x.trim()).filter(Boolean),regions:$(".contact-regions",r).value.split(",").map(x=>x.trim()).filter(Boolean),sortOrder:Number($(".contact-sort",r).value||0),
      isDefault:$(".contact-default",r).checked,enabled:$(".contact-enabled",r).checked
    }))};
  }
  function renderTranslationSettings(){
    if(!$("#translation-provider"))return; const s=translations.settings||{}, langs=translations.languages?.languages||settings?.languages?.languages||[];
    $("#translation-provider").value=s.provider||"manual";
    $("#translation-source-locale").innerHTML=langs.map(x=>`<option value="${esc(x.code)}" ${x.code===s.sourceLocale?"selected":""}>${esc(x.nativeName||x.displayName||x.code)} (${esc(x.code)})</option>`).join("");
    $("#translation-model").value=s.model||""; $("#translation-endpoint").value=s.endpoint||""; $("#translation-auto-queue").checked=s.autoQueue!==false; $("#translation-auto-run").checked=!!s.autoTranslate; $("#translation-review").checked=s.requireHumanReview!==false;
    const x=translations.secretStatus||{}; $("#translation-secret-status").textContent=`Secret 状态：Google ${x.googleCloudTranslation?"✓":"未配置"} · DeepL ${x.deepl?"✓":"未配置"} · OpenAI-Compatible ${x.openaiCompatible?"✓":"未配置"}。API Key 不显示、不写入 D1。`;
  }
  function payload(id){const t=$(`.translation-json[data-id="${CSS.escape(id)}"]`);try{return JSON.parse(t.value)}catch{throw new Error("译文 JSON 格式错误")}}
  function renderJobs(){
    const host=$("#translation-jobs"); if(!host)return; const jobs=translations.jobs||[];
    host.innerHTML=jobs.length?jobs.map(j=>`<article class="batch-card translation-job"><div><strong>${esc(j.resource_id)}</strong> · ${esc(j.source_locale)} → ${esc(j.target_locale)} · <span class="status ${esc(j.status)}">${esc(j.status)}</span></div><div class="muted">Provider: ${esc(j.provider||"manual")} · ${esc(j.updated_at||"")}${j.error_message?" · "+esc(j.error_message):""}</div><textarea class="translation-json" data-id="${esc(j.id)}" rows="7" spellcheck="false">${esc(JSON.stringify(Object.keys(j.translated||{}).length?j.translated:j.source,null,2))}</textarea><div class="row-actions"><button class="btn small ghost tr-save" data-id="${esc(j.id)}">保存译文待审核</button><button class="btn small ghost tr-run" data-id="${esc(j.id)}">调用机翻</button><button class="btn small primary tr-approve" data-id="${esc(j.id)}">审核通过并排队发布</button><button class="btn small ghost tr-requeue" data-id="${esc(j.id)}">重新排队</button></div></article>`).join(""):'<div class="muted">暂无翻译任务。保存源语言型号内容后会自动排队，也可以手工输入型号 ID。</div>';
    $$(".tr-save",host).forEach(b=>b.onclick=()=>job("save_job",b.dataset.id,true)); $$(".tr-run",host).forEach(b=>b.onclick=()=>job("run_job",b.dataset.id));
    $$(".tr-approve",host).forEach(b=>b.onclick=()=>job("approve_job",b.dataset.id,true)); $$(".tr-requeue",host).forEach(b=>b.onclick=()=>job("requeue_job",b.dataset.id));
  }
  async function loadSettings(){settings=await api(SETTINGS);renderLanguages();renderContacts();$("#language-settings-status").textContent="线上 D1 配置已载入。";}
  async function loadTranslations(){translations=await api(TRANSLATIONS);renderTranslationSettings();renderJobs();}
  async function saveLanguages(){const e=$("#language-settings-status");try{const d=await api(SETTINGS,"POST",{action:"save_languages",config:collectLanguages()});settings.languages=d.config;renderLanguages();e.textContent="已保存；发布版本 "+d.revision+" 已排队。";await loadTranslations();}catch(x){e.textContent="保存失败："+x.message}}
  async function saveContacts(){const e=$("#contact-settings-status");try{const d=await api(SETTINGS,"POST",{action:"save_contacts",config:collectContacts()});settings.contacts=d.config;renderContacts();e.textContent="已保存；发布版本 "+d.revision+" 已排队。";}catch(x){e.textContent="保存失败："+x.message}}
  async function saveTranslation(){const e=$("#translation-settings-status");try{const cfg={schemaVersion:1,provider:$("#translation-provider").value,sourceLocale:$("#translation-source-locale").value,autoQueue:$("#translation-auto-queue").checked,autoTranslate:$("#translation-auto-run").checked,model:$("#translation-model").value.trim(),endpoint:$("#translation-endpoint").value.trim(),requireHumanReview:$("#translation-review").checked};await api(SETTINGS,"POST",{action:"save_translation",config:cfg});e.textContent="翻译设置已保存。API Key 仍只存在 Pages Secret。";await loadTranslations();}catch(x){e.textContent="保存失败："+x.message}}
  async function enqueue(){const id=$("#translation-model-id").value.trim(),e=$("#translation-settings-status");if(!id)return;try{const d=await api(TRANSLATIONS,"POST",{action:"enqueue_model",modelId:id,force:true});e.textContent="已生成/刷新 "+Number(d.queued||0)+" 个翻译任务。";await loadTranslations();}catch(x){e.textContent="排队失败："+x.message}}
  async function job(action,id,withPayload=false){const e=$("#translation-settings-status");try{const body={action,id};if(withPayload)body.translated=payload(id);const d=await api(TRANSLATIONS,"POST",body);e.textContent=action==="approve_job"?"译文已审核入库；发布版本 "+d.revision+" 已排队。":"翻译任务已更新。";await loadTranslations();}catch(x){e.textContent="任务失败："+x.message}}
  function bind(){
    $("#add-language")?.addEventListener("click",()=>{
      const body=$("#language-config-body");
      body.insertAdjacentHTML("beforeend",langRow({sortOrder:100,enabled:true,publishReady:false,uiText:{}}));
      const row=body.lastElementChild;
      $(".remove-language",row).onclick=()=>{if($$(".language-row",body).length>1){row.remove();renderLangEditors();}};
      $(".lang-code",row).onchange=renderLangEditors;
      renderLangEditors();
    });
    $("#save-languages")?.addEventListener("click",saveLanguages); $("#reload-site-settings")?.addEventListener("click",async()=>{await loadSettings();await loadTranslations();});
    $("#add-contact")?.addEventListener("click",()=>{$("#contact-config-body").insertAdjacentHTML("beforeend",contactRow({sortOrder:100,enabled:true,isDefault:false}));const row=$("#contact-config-body").lastElementChild;$(".remove-contact",row).onclick=()=>row.remove();});
    $("#save-contacts")?.addEventListener("click",saveContacts); $("#save-translation-settings")?.addEventListener("click",saveTranslation); $("#enqueue-translation-model")?.addEventListener("click",enqueue); $("#reload-translations")?.addEventListener("click",loadTranslations);
  }
  async function tick(){
    const t=token(); if(t&&t!==lastToken&&!$("#admin-app")?.classList.contains("hidden")){lastToken=t;try{await loadSettings();await loadTranslations();}catch(e){if($("#language-settings-status"))$("#language-settings-status").textContent="设置读取失败："+e.message}}
    if(!t)lastToken="";
  }
  bind(); setInterval(tick,500); tick();
})();
