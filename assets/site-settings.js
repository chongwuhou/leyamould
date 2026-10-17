(()=>{'use strict';const FALLBACK={email:'Janey@xuyibottles.com',whatsappUrl:'https://wa.me/8615395897937'};const select=document.querySelector('[data-language-switch]');const staticOptions=select?[...select.options].map(el=>({code:el.value,nativeName:el.textContent})):[];const chooseDefault=()=>{if(!select)return;select.innerHTML='<option value="en">English</option>';select.value='en';select.disabled=true};const contactLinks=(contact)=>{const email=contact?.email||FALLBACK.email;const wa=contact?.whatsappUrl||FALLBACK.whatsappUrl;document.querySelectorAll('[data-site-email]').forEach(el=>{el.textContent=email;el.href='mailto:'+encodeURIComponent(email).replace('%40','@')});document.querySelectorAll('[data-site-email-link]').forEach(el=>{el.href='mailto:'+encodeURIComponent(email).replace('%40','@');el.title='Email '+email});document.querySelectorAll('[data-site-whatsapp]').forEach(el=>{el.href=wa;el.target='_blank';el.rel='noopener noreferrer';el.title='WhatsApp'})};contactLinks(FALLBACK);chooseDefault();const currentLocale=()=>document.documentElement.lang||'en';const configure=configured=>{if(!select||!configured.length)return;
const alternates=new Map([...document.querySelectorAll('link[rel="alternate"][hreflang]')]
  .filter(el=>el.href&&configured.some(x=>x.code===el.hreflang))
  .map(el=>[el.hreflang,el.href]));
const current=currentLocale();
if(current==='en'&&!alternates.has('en'))alternates.set('en',location.href);
const langs=configured.filter(x=>alternates.has(x.code));
if(!langs.length){chooseDefault();return}
select.innerHTML='';
langs.forEach(x=>{const opt=document.createElement('option');opt.value=x.code;
 opt.textContent=x.nativeName||x.displayName||x.code;select.append(opt)});
select.value=langs.some(x=>x.code===current)?current:(langs[0]?.code||'en');
select.disabled=langs.length<2;
select.onchange=()=>{
 const target=alternates.get(select.value);
 if(!target){select.value=current;return}
 const url=new URL(target,location.origin);
 if(url.origin!==location.origin){select.value=current;return}
 location.assign(url.pathname+location.search+location.hash);
};
};configure(staticOptions);fetch('/api/site-settings',{cache:'no-store'}).then(async response=>{if(!response.ok)throw Error('site settings unavailable');return response.json()}).then(data=>{const list=Array.isArray(data.contacts)?data.contacts:[];const c=list.find(x=>x.enabled!==false&&x.isDefault)||list[0];contactLinks(c||FALLBACK);const configured=Array.isArray(data.languages?.items)?data.languages.items:[];
configure(configured);
}).catch(()=>{configure(staticOptions)})})();