(() => {
  const runtime=(()=>{try{return JSON.parse(document.getElementById('xuyi-runtime-ui')?.textContent||'{}')}catch{return {}}})();
  const t=message=>runtime.messages?.[message]||message;
  const search=document.getElementById('faq-search');
  if(!search)return;
  const groups=[...document.querySelectorAll('[data-faq-group]')];
  const items=[...document.querySelectorAll('[data-faq-item]')];
  const reset=document.getElementById('faq-reset');
  const results=document.getElementById('faq-results');
  const labels=[...document.querySelectorAll('.rs-faq__nav a')];
  function update(){
    const query=search.value.toLocaleLowerCase().trim();
    let count=0;
    for(const group of groups){
      let visible=0;
      for(const item of group.querySelectorAll('[data-faq-item]')){
        const show=!query||item.textContent.toLocaleLowerCase().includes(query);
        item.hidden=!show;
        if(show){visible++;count++;}
        else item.open=false;
      }
      group.hidden=visible===0;
    }
    for(const label of labels){
      const id=label.getAttribute('href')?.slice(1);
      const group=id?document.getElementById(id):null;
      label.hidden=!!group?.hidden;
    }
    if(reset)reset.hidden=!query;
    if(results)results.textContent=query?(count?String(count)+' '+t('answers match')+' “'+search.value.trim()+'”.':t('No answers match')+' “'+search.value.trim()+'”. '+t('Try another term.')):t('Browse all')+' '+items.length+' '+t('questions below.');
  }
  for(const suggestion of document.querySelectorAll('[data-faq-suggest]')){
    suggestion.addEventListener('click',()=>{search.value=suggestion.dataset.faqSuggest||'';update();search.focus();});
  }
  search.addEventListener('input',update);
  reset?.addEventListener('click',()=>{search.value='';update();search.focus()});
  update();
})();