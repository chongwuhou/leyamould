
(function(){
const runtimeUI=(()=>{try{return JSON.parse(document.getElementById('xuyi-runtime-ui')?.textContent||'{}')}catch{return {}}})();
const t=message=>runtimeUI.messages?.[message]||message;
// Menu photo warmup: hidden hover panels need their source images ready before first hover.
const menuPhotoWarmup=document.querySelectorAll('#menu-products .mega__image img,.mobile-nav__group-title img');
menuPhotoWarmup.forEach(img=>{img.loading='eager';img.decoding='async'});

const menu=document.getElementById('mobile-menu');
const nav=document.getElementById('mobile-navigation');
if(menu&&nav){menu.addEventListener('click',()=>{const state=!nav.classList.contains('open');nav.classList.toggle('open',state);menu.setAttribute('aria-expanded',String(state));menu.setAttribute('aria-label',state?t('Close menu'):t('Open menu'))});}
document.querySelectorAll('[data-mega-toggle]').forEach(b=>{b.addEventListener('click',e=>{e.stopPropagation();const parent=b.closest('.nav__drop');const opened=parent.classList.contains('open');document.querySelectorAll('.nav__drop.open').forEach(d=>{d.classList.remove('open');d.querySelector('[data-mega-toggle]')?.setAttribute('aria-expanded','false')});if(!opened){parent.classList.add('open');b.setAttribute('aria-expanded','true')}})});
document.addEventListener('click',e=>{if(!e.target.closest('.nav__drop'))document.querySelectorAll('.nav__drop.open').forEach(d=>{d.classList.remove('open');d.querySelector('[data-mega-toggle]')?.setAttribute('aria-expanded','false')})});
document.addEventListener('keydown',e=>{if(e.key==='Escape'){document.querySelectorAll('.nav__drop.open').forEach(d=>{d.classList.remove('open');d.querySelector('[data-mega-toggle]')?.setAttribute('aria-expanded','false')});if(nav){nav.classList.remove('open');menu?.setAttribute('aria-expanded','false')}}});
const search=document.getElementById('search-panel');const st=document.getElementById('search-toggle');if(search&&st){st.addEventListener('click',()=>{let open=!search.classList.contains('open');search.classList.toggle('open',open);st.setAttribute('aria-expanded',String(open));if(open)search.querySelector('input')?.focus()})}

// Buyer brief preview. This controls only locally displayed reference photos and inquiry link;
// it does not claim a specific customization is actually available.
const configButtons=[...document.querySelectorAll('[data-config-kind]')];
const requestButtons=[...document.querySelectorAll('[data-config-request]')];
if(configButtons.length){
 const refs={
  sports:{model:'2501',img:'/media/excel/row-003.webp',alt:'XUYI source sports bottle, model 2501'},
  kids:{model:'2508',img:'/media/excel/row-008.webp',alt:'XUYI source kids bottle, model 2508'},
  jug:{model:'2290',img:'/media/excel/row-021.webp',alt:'XUYI source larger water jug, model 2290'},
  shaker:{model:'501',img:'/media/ppt/slide-091.webp',alt:'XUYI source plastic shaker bottle, model 501'}
 };
 let selected='sports',focus='logo';
 const img=document.getElementById('configurator-photo');
 const info=document.getElementById('configurator-model');
 const cta=document.getElementById('configurator-cta');
 function render(){
  const r=refs[selected];if(!r||!img||!cta)return;
  img.src=r.img;img.alt=r.alt;
  if(info)info.textContent='Source catalog reference: Model '+r.model;
  cta.href='/contact/?model='+encodeURIComponent(r.model)+'&type='+encodeURIComponent(focus)+'#inquiry';
  configButtons.forEach(b=>{const active=b.dataset.configKind===selected;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active))});
  requestButtons.forEach(b=>{const active=b.dataset.configRequest===focus;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active))});
 }
 configButtons.forEach(b=>b.addEventListener('click',()=>{selected=b.dataset.configKind;render()}));
 requestButtons.forEach(b=>b.addEventListener('click',()=>{focus=b.dataset.configRequest;render()}));
 render();
}

const model=document.getElementById('inquiry-model');if(model){model.value=new URLSearchParams(location.search).get('model')||'';}const inquiryType=new URLSearchParams(location.search).get('type');if(inquiryType){const choices=document.querySelector('#inquiry select[name="type"]');if(choices){const target=/sample/i.test(inquiryType)?'Samples':/logo|graphic|brand/i.test(inquiryType)?'Custom Logo / Branding':/oem|molding|manufacturing/i.test(inquiryType)?'OEM / ODM':'Wholesale Quote';[...choices.options].forEach(o=>{if(o.value===target)choices.value=o.value})}}
// All five contact pages use the same D1 business contacts.
// Locale/region assignment is also rechecked by the form API on submit.
const contactLinks=[...document.querySelectorAll('[data-site-email],[data-site-whatsapp]')];
if(contactLinks.length){
 fetch('/api/site-settings',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('settings unavailable');return r.json()}).then(settings=>{
  const contacts=Array.isArray(settings.contacts)?settings.contacts:[];
  const locale=(document.documentElement.lang||'en').toLowerCase();
  const ordered=contacts.filter(c=>c&&c.enabled!==false).sort((a,b)=>Number(a.sortOrder||0)-Number(b.sortOrder||0));
  const contact=ordered.find(c=>Array.isArray(c.locales)&&c.locales.includes(locale))||ordered.find(c=>c.isDefault)||ordered[0];
  if(!contact)return;
  const email=String(contact.email||'').trim();
  const whatsapp=String(contact.whatsappUrl||'').trim();
  const waDigits=/(?:wa\.me\/|phone=)([1-9][0-9]{7,14})/.exec(whatsapp)?.[1]||'';
  const preferredDisplay=String(contact.phoneDisplay||'').trim();
  const waNumber=preferredDisplay.startsWith('+')&&preferredDisplay.replace(/\D/g,'')===waDigits
   ?preferredDisplay:(waDigits.startsWith('86')&&waDigits.length===13
    ?'+86 '+waDigits.slice(2,5)+' '+waDigits.slice(5,9)+' '+waDigits.slice(9)
    :(waDigits?'+'+waDigits:''));
  contactLinks.forEach(link=>{
   if(link.hasAttribute('data-site-email')&&/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)){
    link.href='mailto:'+email;link.textContent=email;
   }
   if(link.hasAttribute('data-site-whatsapp')&&/^https:\/\/(?:wa\.me|api\.whatsapp\.com|www\.whatsapp\.com)\//i.test(whatsapp)){
    link.href=whatsapp;
    // Preserve the chat link while also exposing the actual D1 WhatsApp number.
    // Do not replace text on icon-only rail links (their SVG must remain intact).
    if(link.hasAttribute('data-site-whatsapp-number')&&waNumber){
     const isContactBody=!!link.closest('.contact-layout');
     link.textContent='WhatsApp: '+waNumber+(isContactBody?' · Chat →':'');
    }
   }
  });
 }).catch(()=>{}); // Existing approved contact remains visible if D1 is unavailable.
}

// Store public inquiries in XUYI D1 before reporting success.
const inquiryForm=document.getElementById('inquiry');
if(inquiryForm){
 const formButton=inquiryForm.querySelector('button[type="submit"]');
 const formStatus=document.getElementById('inquiry-status');
 if(formButton){
  formButton.disabled=true;
  if(formStatus)formStatus.textContent=t('Checking online enquiry availability…');
  fetch('/api/site-settings',{cache:'no-store'})
   .then(async res=>{if(!res.ok)throw Error('Status unavailable');return res.json()})
   .then(data=>{
    if(data?.inquiry?.acceptsForm===true){formButton.disabled=false;if(formStatus)formStatus.textContent='';}
    else if(formStatus)formStatus.textContent=t('Online enquiry submissions are temporarily unavailable. Please contact us by email or WhatsApp using the links on this page.');
   })
   .catch(()=>{if(formStatus)formStatus.textContent=t('Online enquiry submissions are temporarily unavailable. Please contact us by email or WhatsApp using the links on this page.')});
 }
}
if(inquiryForm){inquiryForm.addEventListener('submit',async event=>{
 event.preventDefault();
 const button=inquiryForm.querySelector('button[type="submit"]');
 const status=document.getElementById('inquiry-status');
 if(button.disabled)return;
 const fields=new FormData(inquiryForm);
 if(!fields.get('consent')){status.textContent=t('Please accept the privacy policy.');return;}
 button.disabled=true;status.textContent=t('Submitting your enquiry…');
 try{
  const payload={source:'xuyi-contact-form',consent:true,pageUrl:location.href,locale:document.documentElement.lang||'en',
   region:fields.get('country')||'',company:fields.get('company')||'',email:fields.get('email')||'',
   reference:fields.get('model')||'',requirements:fields.get('requirements')||'',
   website:fields.get('website')||'',fields:{material:fields.get('material')||'',quantity:fields.get('quantity')||'',inquiry_type:fields.get('type')||''}};
  const response=await fetch('/api/form-submit',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(payload)});
  const result=await response.json().catch(()=>({}));
  if(!response.ok||!result.saved)throw Error(result.error||t('The enquiry could not be received. Please use our email or WhatsApp contact instead.'));
  status.textContent=t('Thank you. Your enquiry has been recorded. For urgent requests, please also contact us by email or WhatsApp.');
  inquiryForm.reset();
 }catch(error){status.textContent=error.message||t('The request could not be sent.')}
 finally{button.disabled=false}
})}
// Every model already has a real <a href> in HTML. Page links additionally
// make the selected visible group directly shareable/crawlable as ?page=N.
// Without JavaScript all source-authored model anchors remain readable.
const params=new URLSearchParams(location.search);
const q=document.querySelector('[data-catalog-query]');
if(q&&params.has('q'))q.value=(params.get('q')||'').slice(0,120);
const category=document.querySelector('[data-catalog-category]');
if(category&&params.has('category'))category.value=params.get('category')||'';
const count=document.getElementById('filter-count');
const cards=[...document.querySelectorAll('[data-product-card]')];
const perPage=18;
let page=Math.max(1,Math.floor(Number(params.get('page'))||1));
const pageStatus=document.getElementById('page-status'),prev=document.getElementById('page-prev'),next=document.getElementById('page-next');
const isLinkPager=prev?.tagName==='A'&&next?.tagName==='A';
function pageHref(n){const u=new URLSearchParams();if(q?.value.trim())u.set('q',q.value.trim().slice(0,120));if(category?.value)u.set('category',category.value);if(n>1)u.set('page',String(n));return '?'+(u.toString()||'page=1')}
function render(){
 const query=(q?.value||'').toLowerCase().trim(),cat=category?.value||'';
 const matching=cards.filter(c=>(!cat||c.dataset.category===cat)&&(!query||(c.dataset.search||'').includes(query)));
 const totalPages=Math.max(1,Math.ceil(matching.length/perPage));
 page=Math.max(1,Math.min(page,totalPages));
 cards.forEach(c=>{c.hidden=true});
 matching.slice((page-1)*perPage,page*perPage).forEach(c=>{c.hidden=false});
 if(count)count.textContent=matching.length+' '+t('models');
 if(pageStatus)pageStatus.textContent=page+' / '+totalPages;
 if(isLinkPager){
  for(const [element,n,disabled] of [[prev,page-1,page<=1],[next,page+1,page>=totalPages]]){
   element.href=pageHref(Math.max(1,Math.min(n,totalPages)));
   if(disabled){element.setAttribute('aria-disabled','true');element.tabIndex=-1}
   else{element.removeAttribute('aria-disabled');element.removeAttribute('tabindex')}
  }
  document.querySelectorAll('[data-page-link]').forEach(a=>{
   const n=Number(a.dataset.pageLink);
   a.href=pageHref(n);a.hidden=n>totalPages;
   if(n===page)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');
  });
 }else{
  if(prev)prev.disabled=page<=1;
  if(next)next.disabled=page>=totalPages;
 }
}
if(cards.length){
 function filterChanged(){page=1;render()}
 q?.addEventListener('input',filterChanged);
 category?.addEventListener('change',filterChanged);
 if(isLinkPager){
  prev?.addEventListener('click',event=>{if(prev.getAttribute('aria-disabled')==='true')event.preventDefault()});
  next?.addEventListener('click',event=>{if(next.getAttribute('aria-disabled')==='true')event.preventDefault()});
 }else{
  prev?.addEventListener('click',()=>{page--;render();q?.scrollIntoView({block:'center'})});
  next?.addEventListener('click',()=>{page++;render();q?.scrollIntoView({block:'center'})});
 }
 render();
}

const hero=document.querySelector('[data-hero]');
if(hero){
 let slides=[
 {title:'Custom Water Bottles <span>Built for Your Brand.</span>',description:'Explore sports, kids, large capacity and shaker bottles with factory-backed supply and project-specific branding options.',img:'/assets/curated-hd/gradient-sports.webp',alt:'Colorful gradient plastic sports bottle collection',link:'/products/',cta:'Explore Our Products →'},
 {title:'Plastic Sports Bottles <span>For Every Collection.</span>',description:'Compare carry-handle styles, colorful bottle shapes and source catalog models for wholesale buyers.',img:'/assets/curated-hd/outdoor-lifestyle.webp',alt:'Colorful sports bottles arranged for outdoor activities',link:'/collections/sports-water-bottles/',cta:'See Sports Bottles →'},
 {title:'Custom Drinkware <span>Designed Around You.</span>',description:'Discuss logo artwork, packaging, models and sample requirements for your next B2B plastic bottle project.',img:'/assets/curated-hd/customizable-assortment.webp',alt:'Plastic water bottle color and lid variants for customization',link:'/capabilities/',cta:'View Customization →'}
 ];
 if(Array.isArray(runtimeUI.slides)&&runtimeUI.slides.length===slides.length){slides=slides.map((slide,i)=>({...slide,...runtimeUI.slides[i]}))}
 // D1 reviewed banner settings are baked into this page at release time.
 // Never load an admin API in the public site or allow unreviewed HTML.
 try{
  const managed=JSON.parse(document.getElementById("xuyi-home-banners")?.textContent||"null");
  if(Array.isArray(managed)&&managed.length===3&&managed.every(v=>
      typeof v?.title==="string"&&typeof v?.highlight==="string"&&
      typeof v?.link==="string"&&typeof v?.img==="string"))
   slides=slides.map((fallback,i)=>({...fallback,...managed[i],managed:true}));
 }catch{}

 const title=hero.querySelector('#hero-title'),desc=hero.querySelector('#hero-description'),
       img=hero.querySelector('#hero-image'),cta=hero.querySelector('#hero-cta'),
       status=hero.querySelector('#hero-status'),
       dots=[...hero.querySelectorAll('[data-hero-go]')],
       controls=hero.querySelector('.hero__controls'),
       prefersReducedMotion=window.matchMedia('(prefers-reduced-motion: reduce)');
 // Both the image and call-to-action lead to the configured banner URL.
 let artLink=img?.closest("a");
 if(img&&!artLink){
  artLink=document.createElement("a");
  artLink.className="hero__art-link";
  artLink.setAttribute("aria-label","Open featured collection");
  img.parentNode.insertBefore(artLink,img);
  artLink.append(img);
 }
 const DELAY=5500;
 let idx=0,timer=null,inView=true,hoveringControls=false,focusWithin=false,touchStart=null;
 function stop(){
  if(timer!==null){clearTimeout(timer);timer=null}
  hero.classList.remove('is-playing');
 }
 function schedule(){
  stop();
  if(document.hidden||!inView||hoveringControls||focusWithin||prefersReducedMotion.matches)return;
  // Restart the progress indicator whenever the next automatic slide is scheduled.
  void hero.offsetWidth;
  hero.classList.add('is-playing');
  timer=setTimeout(()=>show(idx+1,false),DELAY);
 }
 function show(index,announce){
  idx=(index+slides.length)%slides.length;
  const slide=slides[idx];
  if(slide.managed){
   title.replaceChildren(document.createTextNode(slide.title+" "));
   const emphasis=document.createElement("span");emphasis.textContent=slide.highlight;
   title.append(emphasis);
  }else{title.innerHTML=slide.title;}
  desc.textContent=slide.description;
  if(img.getAttribute('src')!==slide.img)img.src=slide.img;
  img.alt=slide.alt;
  if(artLink){
   artLink.href=slide.link;
   artLink.setAttribute("aria-label",slide.alt||"Featured collection");
   if(/^https:\/\//i.test(slide.link)){artLink.target="_blank";artLink.rel="noopener noreferrer";}
   else{artLink.removeAttribute("target");artLink.removeAttribute("rel");}
  }
  cta.href=slide.link;
  if(/^https:\/\//i.test(slide.link)){cta.target="_blank";cta.rel="noopener noreferrer";}
  else{cta.removeAttribute("target");cta.removeAttribute("rel");}
  cta.textContent=slide.cta;
  dots.forEach((dot,i)=>{
   const active=i===idx;
   dot.classList.toggle('active',active);
   dot.setAttribute('aria-pressed',String(active));
  });
  hero.classList.remove('hero--animating');
  void hero.offsetWidth;
  hero.classList.add('hero--animating');
  if(announce&&status)status.textContent=t('Slide')+' '+(idx+1)+' '+t('of')+' '+slides.length;
  schedule();
 }
 hero.querySelectorAll('[data-hero-nav]').forEach(button=>button.addEventListener('click',()=>{
  show(idx+Number(button.dataset.heroNav),true);
 }));
 dots.forEach((dot,i)=>dot.addEventListener('click',()=>show(i,true)));
 controls?.addEventListener('mouseenter',()=>{hoveringControls=true;stop()});
 controls?.addEventListener('mouseleave',()=>{hoveringControls=false;schedule()});
 hero.addEventListener('focusin',()=>{focusWithin=true;stop()});
 hero.addEventListener('focusout',event=>{
  if(!hero.contains(event.relatedTarget)){focusWithin=false;schedule()}
 });
 hero.addEventListener('keydown',event=>{
  if(event.key==='ArrowLeft'||event.key==='ArrowRight'){
   event.preventDefault();
   show(idx+(event.key==='ArrowRight'?1:-1),true);
  }
 });
 hero.addEventListener('touchstart',event=>{
  if(event.touches.length===1)touchStart={x:event.touches[0].clientX,y:event.touches[0].clientY};
 },{passive:true});
 hero.addEventListener('touchend',event=>{
  if(!touchStart||!event.changedTouches.length)return;
  const dx=event.changedTouches[0].clientX-touchStart.x;
  const dy=event.changedTouches[0].clientY-touchStart.y;
  touchStart=null;
  if(Math.abs(dx)>55&&Math.abs(dx)>Math.abs(dy)*1.3)show(idx+(dx<0?1:-1),true);
 },{passive:true});
 document.addEventListener('visibilitychange',schedule);
 if(prefersReducedMotion.addEventListener)prefersReducedMotion.addEventListener('change',schedule);
 if('IntersectionObserver' in window){
  const observer=new IntersectionObserver(entries=>{
   inView=entries[0]?.isIntersecting!==false;
   schedule();
  },{threshold:.2});
  observer.observe(hero);
 }
 show(0,false);
 // Keep the other two locally hosted images ready for their first appearance.
 slides.slice(1).forEach(slide=>{const preload=new Image();preload.src=slide.img});
 schedule();
}
const bottleTabs=[...document.querySelectorAll('.bottle-tab[role="tab"]')];
function selectTab(i){bottleTabs.forEach((t,j)=>{const active=i===j;t.classList.toggle('active',active);t.setAttribute('aria-selected',String(active));const panel=document.getElementById(t.getAttribute('aria-controls'));if(panel)panel.hidden=!active})}
bottleTabs.forEach((t,i)=>{t.addEventListener('click',()=>selectTab(i));t.addEventListener('keydown',ev=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(ev.key)){ev.preventDefault();const n=ev.key==='Home'?0:ev.key==='End'?bottleTabs.length-1:(i+(ev.key==='ArrowLeft'?-1:1)+bottleTabs.length)%bottleTabs.length;selectTab(n);bottleTabs[n].focus()}})});

document.querySelectorAll('[data-main-photo]').forEach(button=>{button.addEventListener('click',()=>{const large=document.querySelector('#main-photo');if(large){large.src=button.dataset.mainPhoto;large.alt=button.querySelector('img')?.alt||'Bottle image'}})});

// News & Blogs carousel controls. Scrolling and arrow activation both update the active counter.
const newsSlider=document.getElementById('news-slider');
if(newsSlider){
 const newsCards=[...newsSlider.querySelectorAll('.news-card')];
 const newsPrev=document.getElementById('news-prev');
 const newsNext=document.getElementById('news-next');
 const newsCounter=document.getElementById('news-active-count');
 const currentStep=()=>{
  if(!newsCards.length)return 0;
  const gap=parseFloat(getComputedStyle(newsSlider).gap)||0;
  const cardSize=newsCards[0].getBoundingClientRect().width+gap;
  const maxScroll=Math.max(0,newsSlider.scrollWidth-newsSlider.clientWidth);
  if(newsSlider.scrollLeft>=maxScroll-4)return newsCards.length-1;
  return Math.max(0,Math.min(newsCards.length-1,Math.round(newsSlider.scrollLeft/cardSize)));
 };
 const refresh=()=>{
  const active=currentStep();
  if(newsCounter)newsCounter.textContent=String(active+1).padStart(2,'0');
  if(newsPrev)newsPrev.disabled=newsSlider.scrollLeft<=4;
  if(newsNext)newsNext.disabled=newsSlider.scrollLeft>=newsSlider.scrollWidth-newsSlider.clientWidth-4;
 };
 const move=(dir)=>{
  const distance=newsCards[0].getBoundingClientRect().width+(parseFloat(getComputedStyle(newsSlider).gap)||0);
  newsSlider.scrollBy({left:dir*distance,behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth'});
 };
 newsPrev?.addEventListener('click',()=>move(-1));
 newsNext?.addEventListener('click',()=>move(1));
 newsSlider.addEventListener('scroll',refresh,{passive:true});
 if(typeof ResizeObserver!=='undefined'){const observer=new ResizeObserver(refresh);observer.observe(newsSlider)}
 refresh();
}

})();