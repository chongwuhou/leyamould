// Thin UI around the existing LEYA MOULD admin security API.
(()=>{"use strict";
const $=id=>document.getElementById(id);
const token=()=>sessionStorage.getItem("xuyiAdminToken")||"";
let currentPath="admin";
const message=(id,value)=>{const el=$(id);if(el)el.textContent=value;};
async function api(data){
 const t=token();if(!t)throw new Error("请先登录后台");
 const response=await fetch("/api/admin/security",{
  method:data?"POST":"GET",
  headers:{"authorization":"Bearer "+t,...(data?{"content-type":"application/json"}:{})},
  body:data?JSON.stringify(data):undefined,cache:"no-store"});
 const result=await response.json().catch(()=>({}));
 if(!response.ok)throw new Error(result.error||"HTTP "+response.status);
 return result;
}
async function load(){
 try{
  const state=await api();
  $("admin-path-input").value=state.adminPath||"admin";
  currentPath=state.adminPath||"admin";
  message("admin-security-badge",state.passwordConfigured?"密码已设置":"待设置独立后台密码");
  message("admin-path-status","目前后台入口："+state.adminUrl);
  message("admin-password-status",state.passwordConfigured
   ?"已配置独立密码；原管理员恢复密钥仍可使用。":"当前仅支持恢复密钥登录，建议配置独立密码。");
 }catch(error){message("admin-password-status","读取失败："+error.message)}
}
async function changePassword(){
 const password=$("admin-password-new").value;
 const confirmPassword=$("admin-password-confirm").value;
 if(password.length<10||password!==confirmPassword){
  message("admin-password-status","密码至少 10 位且两次必须一致。");return;
 }
 if(!window.confirm("更换密码会让现有后台登录会话失效，确认继续？"))return;
 const btn=$("save-admin-password");btn.disabled=true;
 try{
  await api({action:"set_password",password,confirmPassword});
  $("admin-password-new").value="";$("admin-password-confirm").value="";
  sessionStorage.removeItem("xuyiAdminToken");
  message("admin-password-status","密码已更新。请使用新密码重新登录。");
  location.reload();
 }catch(error){message("admin-password-status","更新失败："+error.message)}
 finally{btn.disabled=false}
}
async function changePath(){
 const slug=$("admin-path-input").value.trim();
 if(slug===currentPath){message("admin-path-status","后台地址未变化。");return;}
 if(!/^[a-z0-9][a-z0-9-]{2,47}$/.test(slug)){
  message("admin-path-status","路径只允许 3–48 位小写字母、数字或连字符。");return;
 }
 if(!window.confirm("确认更换后台地址为 /"+slug+"/ ？必须等待 GitHub Actions 部署成功后再使用新入口。"))return;
 const btn=$("save-admin-path");btn.disabled=true;
 try{
  const result=await api({action:"save_path",adminPath:slug});
  message("admin-path-status","已排队修订 "+result.revision+"。部署成功后使用："+result.adminUrl+
    "；旧域名缓存仍需独立清理。不要现在关闭现有后台页面。");
 }catch(error){message("admin-path-status","更新失败："+error.message)}
 finally{btn.disabled=false}
}
$("save-admin-password")?.addEventListener("click",changePassword);
$("save-admin-path")?.addEventListener("click",changePath);
document.querySelector('[data-admin-target="settings"]')?.addEventListener("click",load);
})();
