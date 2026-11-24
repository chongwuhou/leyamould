/* Shared authenticated integration layer for the LEYA MOULD admin modules. */
(()=>{'use strict';const KEY='xuyiAdminToken';const $=(q)=>document.querySelector(q);const $$=(q)=>[...document.querySelectorAll(q)];let active='leads';
function showPanel(name){active=name;$$('[data-admin-target]').forEach(el=>el.classList.toggle('active',el.dataset.adminTarget===name));$$('[data-admin-module]').forEach(el=>{const section=el.dataset.adminModule;const visible=name==='all'||section===name||(name==='settings'&&section==='settings');el.hidden=!visible;});}
function setAuthenticated(ok){$('#admin-app')?.classList.toggle('hidden',!ok);$('#admin-lock')?.classList.toggle('hidden',ok);if(ok)showPanel(active);}
async function verify(){const token=sessionStorage.getItem(KEY);if(!token){setAuthenticated(false);return false}try{const r=await fetch('/api/admin/site-settings',{headers:{authorization:'Bearer '+token},cache:'no-store'});if(!r.ok)throw new Error('Session expired');setAuthenticated(true);return true}catch{sessionStorage.removeItem(KEY);setAuthenticated(false);return false}}
$('#token-form')?.addEventListener('submit',async event=>{event.preventDefault();const error=$('#lock-error');error.textContent='';const button=$('#token-form button[type="submit"]');button.disabled=true;try{const r=await fetch('/api/admin/auth',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({password:$('#token-input').value})});const data=await r.json().catch(()=>({}));if(!r.ok||!data.sessionToken)throw new Error(data.error||'登录失败');sessionStorage.setItem(KEY,data.sessionToken);$('#token-input').value='';setAuthenticated(true)}catch(e){error.textContent=e.message||'登录失败';setAuthenticated(false)}finally{button.disabled=false}});
$$('[data-admin-target]').forEach(el=>el.addEventListener('click',()=>showPanel(el.dataset.adminTarget)));
$('#logout-btn')?.addEventListener('click',()=>{sessionStorage.removeItem(KEY);setAuthenticated(false)});
$('#refresh-btn')?.addEventListener('click',()=>{if(sessionStorage.getItem(KEY))location.reload()});
async function checkSetup(){
 try{
  const response=await fetch('/api/admin/auth',{cache:'no-store'});
  const state=await response.json();
  if(!state.configured){
   const error=$('#lock-error');
   if(error)error.textContent='后台尚未初始化：请先在 LEYA MOULD Cloudflare Pages Production 中设置 ADMIN_TOKEN Secret。';
  }
 }catch{/* Login requests will still report their own errors. */}
}
checkSetup();
verify();
})();
