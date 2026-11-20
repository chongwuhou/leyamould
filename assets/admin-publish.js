(()=>{
 const queue=document.getElementById("publish-site-btn");
 const check=document.getElementById("publish-check-btn");
 const status=document.getElementById("publish-site-status");
 if(!queue||!status)return;
 const token=()=>sessionStorage.getItem("xuyiAdminToken")||"";
 async function getJson(url,headers={}){
  const res=await fetch(url,{cache:"no-store",headers});
  const data=await res.json().catch(()=>({}));
  if(!res.ok)throw Error(data.error||"HTTP "+res.status);
  return data;
 }
 async function checkStatus(){
  if(!token()){status.textContent="请先登录后台查看发布状态。";return}
  if(check)check.disabled=true;
  status.textContent="正在核对 D1 修订与已部署版本…";
  try{
   const [desired,live]=await Promise.all([
    getJson("/api/publish-state",{authorization:"Bearer "+token()}),
    getJson("/build-meta.json?admin_status="+Date.now())
   ]);
   if(live.pagesProject!=="leyamould")throw Error("生产版本身份不匹配");
   const expected=Number(desired.publishRevision||0);
   const deployed=Number(live.publishRevision||0);
   const sha=String(live.sourceRevision||"").slice(0,12);
   if(expected>deployed){
    status.textContent="待发布：D1 修订 "+expected+"，当前线上修订 "+deployed+"（版本 "+sha+"）。GitHub 定时任务尚未将最新内容部署；请核对 Actions 运行记录。";
   }else if(expected===deployed){
    status.textContent="修订已同步：D1 "+expected+"，线上 "+deployed+"（版本 "+sha+"）。这只证明修订一致，不代表 SMTP、翻译审核或 CDN 清理完成。";
   }else{
    status.textContent="警告：线上修订 "+deployed+" 高于 D1 "+expected+"，请检查发布历史与数据库绑定。";
   }
  }catch(error){status.textContent="发布状态检查失败："+error.message}
  finally{if(check)check.disabled=false}
 }
 queue.addEventListener("click",async()=>{
  if(!window.confirm("确认将旭一全站重建请求排入 D1？GitHub Actions 未运行前不会立即上线。"))return;
  const session=token();
  if(!session){status.textContent="请先登录后台。";return}
  queue.disabled=true;status.textContent="正在向 D1 写入发布修订…";
  try{
   const result=await fetch("/api/admin/publish",{
    method:"POST",headers:{authorization:"Bearer "+session},cache:"no-store"
   });
   const data=await result.json().catch(()=>({}));
   if(!result.ok)throw Error(data.error||"HTTP "+result.status);
   status.textContent="已排队修订 "+data.revision+"；尚未部署。请在 GitHub Actions 完成后点击“检查发布状态”。";
  }catch(error){status.textContent="无法排队发布："+error.message}
  finally{queue.disabled=false}
 });
 if(check)check.addEventListener("click",checkStatus);
})();
