// LEYA model-reference editor.  It only calls the authenticated CMS route;
// no third-party catalogue API or translation service is contacted.
(()=>{
  const $=id=>document.getElementById(id);
  const status=$('model-reference-status');
  const list=$('model-reference-list');
  if(!status||!list)return;
  let items=[];
  const token=()=>sessionStorage.getItem('xuyiAdminToken')||'';
  const esc=value=>String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const api=async(method='GET',body)=>{
    const options={method,headers:{Authorization:'Bearer '+token()}};
    if(body!==undefined){options.headers['content-type']='application/json';options.body=JSON.stringify(body)}
    const response=await fetch('/api/admin/model-references',options);
    const data=await response.json().catch(()=>({error:'Invalid server response'}));
    if(!response.ok)throw Error(data.error||('Request failed: '+response.status));
    return data;
  };
  const value=id=>$(id)?.value.trim()||'';
  const setValue=(id,v)=>{if($(id))$(id).value=v??''};
  function reset(){
    ['model-reference-slug','model-reference-title','model-reference-alt','model-reference-source-url','model-reference-source-image','model-reference-image','model-reference-pdf','model-reference-pdf-sha256','model-reference-description','model-reference-title-es','model-reference-alt-es','model-reference-description-es'].forEach(id=>setValue(id,''));
    setValue('model-reference-sort','0');setValue('model-reference-publication','draft');
    $('model-reference-editor')?.removeAttribute('data-edit-slug');
  }
  function edit(item){
    setValue('model-reference-slug',item.slug);setValue('model-reference-family',item.family);
    setValue('model-reference-title',item.title);setValue('model-reference-alt',item.alt);
    setValue('model-reference-source-url',item.sourceUrl);setValue('model-reference-source-image',item.sourceImage);
    setValue('model-reference-image',item.imagePath);setValue('model-reference-description',item.description);
    setValue('model-reference-pdf',item.pdfUrl);setValue('model-reference-pdf-sha256',item.pdfSha256);setValue('model-reference-pdf-pages',item.pdfPages||0);
    setValue('model-reference-sort',item.sortOrder);setValue('model-reference-publication',item.publicationStatus);
    const es=item.translations?.es||{};setValue('model-reference-title-es',es.title);setValue('model-reference-alt-es',es.alt);setValue('model-reference-description-es',es.description);
    $('model-reference-editor')?.setAttribute('data-edit-slug',item.slug);
    $('model-reference-editor')?.scrollIntoView({behavior:'smooth',block:'start'});
  }
  function render(){
    if(!items.length){list.innerHTML='<p class="muted">D1 中还没有型号记录。可以先保存草稿，完成 R2 图片和审核后再发布。</p>';return}
    list.innerHTML='<div class="table-wrap"><table class="pages-table"><thead><tr><th>型号</th><th>产品族</th><th>状态</th><th>图片</th><th>更新时间</th><th></th></tr></thead><tbody>'+items.map(item=>
      '<tr><td><strong>'+esc(item.title)+'</strong><br><small>'+esc(item.slug)+'</small></td><td>'+esc(item.family)+'</td><td><span class="pill">'+esc(item.publicationStatus)+'</span></td><td>'+esc(item.imagePath||'未绑定 R2')+'</td><td>'+esc(item.updatedAt||'')+'</td><td><button type="button" class="btn ghost" data-model-edit="'+esc(item.slug)+'">编辑</button>'+(item.publicationStatus==='draft'?'<button type="button" class="btn ghost" data-model-delete="'+esc(item.slug)+'">删除</button>':'')+'</td></tr>'
    ).join('')+'</tbody></table></div>';
    list.querySelectorAll('[data-model-edit]').forEach(button=>button.addEventListener('click',()=>{const item=items.find(row=>row.slug===button.dataset.modelEdit);if(item)edit(item)}));
    list.querySelectorAll('[data-model-delete]').forEach(button=>button.addEventListener('click',async()=>{
      if(!confirm('确认删除这个草稿型号？'))return;
      try{status.textContent='正在删除…';await api('POST',{action:'delete',slug:button.dataset.modelDelete});status.textContent='草稿已删除';await load()}
      catch(error){status.textContent=error.message}
    }));
  }
  async function load(){
    try{status.textContent='正在读取 D1…';const data=await api();items=Array.isArray(data.items)?data.items:[];render();status.textContent='共 '+items.length+' 条（草稿 '+(data.counts?.draft||0)+'，已发布 '+(data.counts?.published||0)+'）'}
    catch(error){status.textContent=error.message;list.innerHTML='<p class="error">无法读取型号参考库：'+esc(error.message)+'</p>'}
  }
  $('model-reference-editor')?.addEventListener('submit',async event=>{
    event.preventDefault();
    const translations={};
    const es={title:value('model-reference-title-es'),alt:value('model-reference-alt-es'),description:value('model-reference-description-es')};
    if(Object.values(es).some(Boolean))translations.es=es;
    const item={slug:value('model-reference-slug'),family:value('model-reference-family'),title:value('model-reference-title'),alt:value('model-reference-alt'),sourceUrl:value('model-reference-source-url'),sourceImage:value('model-reference-source-image'),imagePath:value('model-reference-image'),pdfUrl:value('model-reference-pdf'),pdfSha256:value('model-reference-pdf-sha256'),pdfPages:Number(value('model-reference-pdf-pages')||0),description:value('model-reference-description'),sortOrder:Number(value('model-reference-sort')||0),publicationStatus:value('model-reference-publication'),translations};
    try{status.textContent='正在保存…';await api('POST',{action:'save',item});status.textContent='已保存到 D1；如需前台更新，请执行一次全站重建';await load()}
    catch(error){status.textContent=error.message}
  });
  $('model-reference-reload')?.addEventListener('click',load);
  $('model-reference-new')?.addEventListener('click',reset);
  $('model-reference-reset')?.addEventListener('click',reset);
  $('model-reference-import')?.addEventListener('click',async()=>{
    const file=$('model-reference-import-file')?.files?.[0];
    if(!file){status.textContent='先选择 prepare_model_reference_import.py 生成的 JSON';return}
    try{
      const payload=JSON.parse(await file.text());
      if(payload?.action!=='bulk_import'||!Array.isArray(payload.items)||!payload.items.length)throw Error('导入文件不是有效的型号批量 JSON');
      if(!confirm('将导入 '+payload.items.length+' 条型号草稿；已有 slug 默认跳过，确认继续？'))return;
      status.textContent='正在以 D1 原子批次导入…';
      const result=await api('POST',{...payload,action:'bulk_import',createOnly:true});
      status.textContent='批量导入完成：新增 '+(result.saved?.length||0)+'，已存在 '+(result.existing?.length||0)+'；全部仍为草稿';
      await load();
    }catch(error){status.textContent=error.message}
  });
  document.querySelectorAll('[data-admin-target="modelreferences"]').forEach(button=>button.addEventListener('click',load));
})();
