// Read-only D1 content/release audit viewer.
(()=>{
 const token=()=>sessionStorage.getItem("xuyiAdminToken")||"";
 const $=id=>document.getElementById(id);
 const status=msg=>{if($("audit-status"))$("audit-status").textContent=msg};
 const esc=value=>String(value??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
 async function load(){
  if(!token()){status("请先登录后台");return}
  const button=$("audit-refresh");if(button)button.disabled=true;status("正在读取审计记录…");
  try{
   const response=await fetch("/api/admin/audit?limit=100",{cache:"no-store",headers:{authorization:"Bearer "+token()}});
   const data=await response.json().catch(()=>({}));if(!response.ok)throw Error(data.error||"HTTP "+response.status);
   const body=$("audit-body");body.replaceChildren();
   for(const row of data.items||[]){
    const note=typeof row.metadata==="object"?JSON.stringify(row.metadata):"";
    const tr=document.createElement("tr");
    tr.innerHTML="<td>"+esc(row.created_at)+"</td><td>"+esc(row.actor)+"</td><td>"+esc(row.action)+"</td><td><code>"+esc(row.resource_type+" / "+row.resource_id)+"</code></td><td>"+esc(row.publish_revision??"")+"</td><td><code>"+esc((row.before_hash||"").slice(0,10)+" → "+(row.after_hash||"").slice(0,10))+"</code></td><td>"+esc(note)+"</td>";
    body.append(tr);
   }
   status("已读取 "+(data.items||[]).length+" 条记录；审计日志只读保存。");
  }catch(error){status("审计读取失败："+error.message)}
  finally{if(button)button.disabled=false}
 }
 $("audit-refresh")?.addEventListener("click",load);
 document.querySelector('[data-admin-target="audit"]')?.addEventListener("click",load);
})();

