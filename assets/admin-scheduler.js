(()=>{'use strict';
const KEY='xuyiAdminToken',API='/api/admin/scheduler',BLOG='/api/admin/blog';
const $=id=>document.getElementById(id),status=s=>{const e=$('scheduler-status');if(e)e.textContent=s};
let currentId='',loaded=false;
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const token=()=>sessionStorage.getItem(KEY)||'';
async function api(url,method='GET',data=null){
 const r=await fetch(url,{method,headers:{authorization:'Bearer '+token(),...(data?{'content-type':'application/json'}:{})},body:data?JSON.stringify(data):undefined,cache:'no-store'});
 const j=await r.json().catch(()=>({}));if(!r.ok)throw Error(j.error||'HTTP '+r.status);return j;
}
function typeName(v){return v==='reviews'?'产品评价':'Blog 文章'}
function form(task=null){
 currentId=task?.id||'';
 $('scheduler-task-form').hidden=false;
 $('scheduler-form-heading').textContent=task?'编辑定时任务':'新建定时任务';
 $('scheduler-type').value=task?.content_type||'reviews';
 $('scheduler-name').value=task?.name||'';
 $('scheduler-time').value=task?.schedule_time||'09:17';
 $('scheduler-timezone').value=task?.timezone||'Asia/Shanghai';
 $('scheduler-limit').value=task?.daily_limit??3;
 $('scheduler-enabled').checked=false;
 $('scheduler-limit').max=$('scheduler-type').value==='reviews'?'20':'10';
}
function hideForm(){currentId='';$('scheduler-task-form').hidden=true}
function render(data){
 const tasks=$('scheduler-task-list');
 const enabled=data.tasks||[];
 const total=type=>enabled.filter(t=>t.enabled&&t.content_type===type).reduce((sum,t)=>sum+Number(t.daily_limit||0),0);
 const reviewTotal=total('reviews'),blogTotal=total('blog');
 const quota=$('scheduler-quota-summary');
 if(quota)quota.textContent='自动发布已关闭。当前仅保留队列记录：产品评价 '+reviewTotal+' 条；Blog '+blogTotal+' 篇。发布需在对应内容模块中手动完成。';
 tasks.innerHTML=data.tasks?.length?'<div class="table-wrap"><table class="pages-table"><thead><tr><th>任务</th><th>类型</th><th>状态</th><th>时间 / 时区</th><th>每日数量（本任务）</th><th>下次检查</th><th>操作</th></tr></thead><tbody>'+
 data.tasks.map(t=>'<tr><td>'+esc(t.name)+'<small>'+esc(t.id)+'</small></td><td>'+typeName(t.content_type)+'</td><td><span class="muted">仅队列</span></td><td>'+esc(t.schedule_time)+'<small>'+esc(t.timezone)+'</small></td><td>'+esc(t.daily_limit)+'</td><td>'+esc(t.nextRun)+'</td><td><button class="btn ghost" data-edit="'+esc(t.id)+'">编辑</button> '+(['reviews-daily','blog-daily'].includes(t.id)?'':'<button class="btn ghost" data-delete="'+esc(t.id)+'">删除</button>')+'</td></tr>').join('')+'</tbody></table></div>':'<p class="muted">暂无任务</p>';
 tasks.querySelectorAll('[data-edit]').forEach(b=>b.onclick=()=>form(data.tasks.find(t=>t.id===b.dataset.edit)));
 tasks.querySelectorAll('[data-delete]').forEach(b=>b.onclick=async()=>{if(!confirm('确定删除此定时任务？历史执行记录会保留。'))return;try{await api(API,'POST',{action:'delete',id:b.dataset.delete});await load()}catch(e){status(e.message)}});
 const queue=$('scheduler-blog-queue');
 queue.innerHTML=data.blogQueue?.length?data.blogQueue.map(q=>'<div class="blog-admin-row"><div><strong>'+esc(q.title)+'</strong><small>'+esc(q.slug)+' · '+esc(q.status)+' · '+esc(q.scheduledAt)+'</small></div>'+(q.status==='scheduled'?'<button class="btn ghost" data-cancel-queue="'+esc(q.slug)+'">取消定时</button>':'')+'</div>').join(''):'<p class="muted">暂无 Blog 定时文章。文章需在 Blog 编辑器中单独设置发布时间并通过审核确认。</p>';
 queue.querySelectorAll('[data-cancel-queue]').forEach(b=>b.onclick=async()=>{if(!confirm('取消这篇文章的定时发布？'))return;try{await api(BLOG,'POST',{action:'cancel-schedule',slug:b.dataset.cancelQueue});await load()}catch(e){status(e.message)}});
 const runs=$('scheduler-run-history');
 runs.innerHTML=data.runs?.length?'<div class="table-wrap"><table class="pages-table"><thead><tr><th>任务 ID</th><th>计划日期</th><th>开始时间</th><th>结束时间</th><th>结果</th><th>发布</th><th>跳过</th><th>错误</th></tr></thead><tbody>'+data.runs.map(r=>'<tr><td>'+esc(r.task_id)+'</td><td>'+esc(r.scheduled_for)+'</td><td>'+esc(r.started_at)+'</td><td>'+esc(r.finished_at||'—')+'</td><td>'+esc(r.status)+'</td><td>'+esc(r.published_count)+'</td><td>'+esc(r.skipped_count)+'</td><td>'+esc(r.error||'')+'</td></tr>').join('')+'</tbody></table></div>':'<p class="muted">暂无执行记录</p>';
}
async function load(){if(!token())return;status('正在读取 D1 定时任务…');try{const data=await api(API);render(data);loaded=true;status('已读取 '+(data.tasks?.length||0)+' 个任务、'+(data.runs?.length||0)+' 条执行记录。所有计划由 D1 控制。')}catch(e){status('读取失败：'+e.message)}}
$('scheduler-refresh')?.addEventListener('click',load);
$('scheduler-new')?.addEventListener('click',()=>form());
$('scheduler-cancel')?.addEventListener('click',hideForm);
$('scheduler-type')?.addEventListener('change',()=>{$('scheduler-limit').max=$('scheduler-type').value==='reviews'?'20':'10';if(Number($('scheduler-limit').value)>Number($('scheduler-limit').max))$('scheduler-limit').value=$('scheduler-limit').max;if(!currentId)$('scheduler-time').value=$('scheduler-type').value==='blog'?'00:00':'09:17'});
 $('scheduler-task-form')?.addEventListener('submit',async e=>{e.preventDefault();const task={id:currentId||undefined,content_type:$('scheduler-type').value,name:$('scheduler-name').value.trim(),schedule_time:$('scheduler-time').value,timezone:$('scheduler-timezone').value,daily_limit:Number($('scheduler-limit').value),enabled:false};try{await api(API,'POST',{action:'save',task});hideForm();await load()}catch(err){status('保存队列失败：'+err.message)}});
document.querySelectorAll('[data-admin-target="scheduler"]').forEach(b=>b.addEventListener('click',()=>load()));
if(token()&&!loaded)load();
})();

