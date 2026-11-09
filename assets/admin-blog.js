(()=>{'use strict';
const KEY='xuyiAdminToken',API='/api/admin/blog';
const $=sel=>document.querySelector(sel),status=(message)=>{const e=$('#blog-admin-status');if(e)e.textContent=message};
let loaded=false,current='';
function token(){return sessionStorage.getItem(KEY)||''}
async function api(method='GET',data=null,url=API){
 const r=await fetch(url,{method,headers:{authorization:'Bearer '+token(),...(data?{'content-type':'application/json'}:{})},body:data?JSON.stringify(data):undefined,cache:'no-store'});
 const j=await r.json().catch(()=>({}));
 if(!r.ok)throw Error(j.error||'HTTP '+r.status);
 return j;
}
function esc(v){return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function toSections(text){
 return text.trim().split(/(?=^##\s+)/m).map(piece=>piece.trim()).filter(Boolean).map(piece=>{
 const lines=piece.split('\n');
 const heading=lines.shift().replace(/^##\s*/,'').trim();
 return {heading,paragraph:lines.join('\n').trim()};
 });
}
function setForm(post={},existing=false){
 current=existing?post.slug:'';
 const form=$('#blog-editor-form');
 form.hidden=false;
 $('#blog-admin-list').hidden=true;
 const assign=(k,v)=>{$('#blog-'+k).value=v??''};
 assign('slug',post.slug||'');$('#blog-slug').readOnly=existing;
 assign('group',post.group||'Wholesale & Planning');
 assign('title',post.title||'');
 assign('description',post.description||'');
 assign('keyword',post.primary_keyword||'');
 assign('secondary',(post.secondary_keywords||[]).join('\n'));
 assign('cover',post.cover||'/media/ppt/slide-059.webp');
 assign('intro',post.intro||'');
 assign('sections',(post.sections||[]).map(s=>'## '+s.heading+'\n'+s.paragraph).join('\n\n'));
 assign('checklist',(post.checklist||[]).join('\n'));
 assign('faqs',(post.faqs||[]).map(q=>q.question+' | '+q.answer).join('\n'));
  assign('related',(post.related||[]).join('\n'));  assign('scheduled-at',post.scheduled_at?new Intl.DateTimeFormat('sv-SE',{timeZone:'Asia/Shanghai',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).format(new Date(post.scheduled_at)).replace(' ','T'):'');
  $('#blog-editorial-approved').checked=false;
  $('#blog-editor-heading').textContent=existing?'编辑：'+post.title:'新建 Blog 文章';
  $('#blog-cover-preview').src=$('#blog-cover').value; $('#blog-preview-link').href=existing&&post.status==='published'?'/blog/'+encodeURIComponent(post.slug)+'/':'/blog/';
 status(existing?'已打开文章，可修改草稿或发布。':'开始编辑新文章；仅单击正式发布才公开。');
}
function fromForm(){
 const v=k=>$('#blog-'+k).value.trim();
 const faqs=v('faqs').split('\n').map(line=>line.trim()).filter(Boolean).map(line=>{
   const index=line.indexOf('|');if(index<0)throw Error('FAQ 格式应为：问题 | 回答');
   return {question:line.slice(0,index).trim(),answer:line.slice(index+1).trim()};
 });
 return {
  slug:v('slug').toLowerCase(),group:v('group'),title:v('title'),description:v('description'),
  primary_keyword:v('keyword'),secondary_keywords:v('secondary').split('\n').map(x=>x.trim()).filter(Boolean),
  cover:v('cover'),intro:v('intro'),sections:toSections(v('sections')),
  faqs,checklist:v('checklist').split('\n').map(x=>x.trim()).filter(Boolean),
  related:v('related').split('\n').map(x=>x.trim()).filter(Boolean)
 };
}
async function list(){
 if(!token())return;
 status('正在读取 D1 文章…');
 try{
 const data=await api();
 const root=$('#blog-admin-list');root.hidden=false;
 $('#blog-editor-form').hidden=true;
  root.innerHTML=data.posts.length?data.posts.map(post=>'<div class="blog-admin-row"><div><strong>'+esc(post.title)+'</strong><small>'+esc(post.slug)+' · '+esc(post.group||'')+' · '+esc(post.status)+(post.schedule_status?' · 定时：'+esc(post.schedule_status)+' '+esc(post.scheduled_at||''):'')+(post.has_draft?' · 有未发布草稿':'')+' · '+esc(post.updated_at||'')+'</small></div><button type="button" class="btn ghost" data-edit-blog="'+esc(post.slug)+'">编辑</button>'+(post.status==='published'?'<button type="button" class="btn ghost" data-retire-blog="'+esc(post.slug)+'">撤回</button>':'')+'</div>').join(''):'<p class="muted">暂无文章，点击“新建文章”即可创建。</p>'; root.querySelectorAll('[data-edit-blog]').forEach(button=>button.addEventListener('click',async()=>{
  try{const {post}=await api('GET',null,API+'?slug='+encodeURIComponent(button.dataset.editBlog));setForm(post,true)}catch(err){status(err.message)}
 }));
 root.querySelectorAll('[data-retire-blog]').forEach(button=>button.addEventListener('click',async()=>{
  if(!confirm('确定要从正式站撤回这篇文章吗？撤回后客户将无法再访问文章 URL。'))return;
  button.disabled=true;
  try{await api('POST',{action:'retire',slug:button.dataset.retireBlog});await list()}
  catch(error){status('撤回失败：'+error.message);button.disabled=false}
 }));
 loaded=true;status('D1 文章总数：'+data.posts.length+'。其中发布后可以立即在线访问。');
 }catch(err){status('Blog 数据读取失败：'+err.message)}
}
async function submit(action){
 const save=$('#blog-save-btn'),publish=$('#blog-publish-btn'),schedule=$('#blog-schedule-btn');
 save.disabled=publish.disabled=schedule.disabled=true;
 try{
  const post=fromForm();
  if(!post.slug||post.sections.length<2)throw Error('至少需要两段正文内容。');
  const payload={action,post};
  if(action==='publish'||action==='schedule'){
   payload.editorialApproved=$('#blog-editorial-approved').checked;
  }
  if(action==='schedule'){
   const local=$('#blog-scheduled-at').value;
   if(!local)throw Error('请先选择计划发布时间（北京时间）。');
   payload.scheduledAt=new Date(local+':00:00+08:00').toISOString();
  }
  const res=await api('POST',payload);
  status(action==='publish'?'已发布到正式站：'+res.url:action==='schedule'?'已安排定时发布：'+res.scheduledAt:'草稿已保存，仅后台可见。');
  if(action==='publish')window.open(res.url,'_blank','noopener');
  await list();
 }catch(err){status('保存失败：'+err.message)}
 finally{save.disabled=publish.disabled=schedule.disabled=false}
}$('#blog-new-btn')?.addEventListener('click',()=>setForm({},false));
$('#blog-refresh-btn')?.addEventListener('click',list);
$('#blog-close-btn')?.addEventListener('click',list);
$('#blog-editor-form')?.addEventListener('submit',ev=>{ev.preventDefault();submit('save')});
$('#blog-publish-btn')?.addEventListener('click',()=>submit('publish'));
$('#blog-schedule-btn')?.addEventListener('click',()=>submit('schedule'));
$('#blog-cover')?.addEventListener('change',()=>{$('#blog-cover-preview').src=$('#blog-cover').value});
$('#blog-upload')?.addEventListener('change',async(ev)=>{
 const file=ev.target.files?.[0];if(!file)return;
 const result=$('#blog-upload-status');
 if(!['image/jpeg','image/png','image/webp'].includes(file.type)||file.size>6*1024*1024){result.textContent='仅支持 JPEG/PNG/WebP，最大 6MB';return}
 result.textContent='正在上传图片…';
 const body=new FormData();body.append('image',file);
 try{
  const response=await fetch('/api/admin/blog-media',{method:'POST',headers:{authorization:'Bearer '+token()},body});
  const data=await response.json();
  if(!response.ok)throw Error(data.error||'Upload failed');
  $('#blog-cover').value=data.path;$('#blog-cover-preview').src=data.path;
  result.textContent='图片已上传到旭一 R2，可用于当前文章。';
 }catch(error){result.textContent='上传失败：'+error.message}
});
document.querySelectorAll('[data-admin-target="blog"]').forEach(btn=>btn.addEventListener('click',()=>{if(token())list()}));
if(token()&&!loaded)list();
})();