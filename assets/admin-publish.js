(() => {
  const button=document.getElementById("publish-site-btn");
  const status=document.getElementById("publish-site-status");
  if(!button||!status)return;
  button.addEventListener("click",async()=>{
    if(!window.confirm("确认排队一次旭一全站重建吗？发布需要 GitHub Actions 已配置 XUYI 凭据。"))return;
    const token=sessionStorage.getItem("xuyiAdminToken");
    if(!token){status.textContent="请先登录后台。";return}
    button.disabled=true;
    status.textContent="正在向 D1 写入发布修订…";
    try {
      const result=await fetch("/api/admin/publish",{
        method:"POST",headers:{"authorization":"Bearer "+token},cache:"no-store"
      });
      const data=await result.json().catch(()=>({}));
      if(!result.ok)throw Error(data.error||"HTTP "+result.status);
      status.textContent="已排队修订 "+data.revision+"。GitHub Actions 启用后会自动检查并发布；这不是部署成功通知。";
    }catch(error){status.textContent="无法排队发布："+error.message}
    finally{button.disabled=false}
  });
})();