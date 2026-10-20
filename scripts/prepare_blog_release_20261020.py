#!/usr/bin/env python3
"""Create reviewed CMS import statements from permanent Blog guide and localization sources.

Never mutate dist: author content in canonical JSON, then publish into D1.
Existing D1 blog posts/translations are preserved on conflict; localized index
cards are appended only if absent, retaining operator-managed surrounding copy.
"""
import html,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
SLUGS=["how-to-vet-plastic-water-bottle-factory-bulk-order", "mixed-color-size-water-bottle-wholesale-order", "custom-water-bottle-deposit-checklist"]
LOCALES=("es","pt","ru","tr")
GUIDES={v["slug"]:v for v in (json.loads((ROOT/"data/blog-guides.json").read_text(encoding="utf8"))+json.loads((ROOT/"data/blog-guides-20261020.json").read_text(encoding="utf8")))}
TRANS=json.loads((ROOT/"data/blog-localized-copy-20261020.json").read_text(encoding="utf8"))["articles"]
MATRICES=json.loads((ROOT/"data/blog-buyer-decision-tables-20261020.json").read_text(encoding="utf8"))["articles"]
EVIDENCE=json.loads((ROOT/"data/editorial-evidence.json").read_text(encoding="utf8"))
OUT=ROOT/"_local_ops"/"blog-batch-20261020"
OUT.mkdir(parents=True,exist_ok=True)
UI={
"es":{"home":"Inicio","guide":"Guía de compra","in":"EN ESTA GUÍA","quote":"Hablar del proyecto →","resources":"RECURSOS PARA COMPRADORES","before":"Antes de pedir una cotización","matrix":"Criterios de compra, no certificaciones de XUYI ni plazos garantizados; confirme el modelo y las normas del mercado.","check":"Lista de verificación del comprador","faq":"Preguntas frecuentes","cta":"¿Necesita cotizar un modelo específico?","ctap":"Envíe el modelo, material, cantidad, diseño y destino para revisar opciones verificadas.","button":"Solicitar cotización de botellas →","related":"Lecturas relacionadas","continue":"SEGUIR LEYENDO","published":"Publicado","sourceNext":"Siguiente paso","sourceRefs":"Referencias oficiales"},
"pt":{"home":"Início","guide":"Guia de compras","in":"NESTE GUIA","quote":"Fale do seu projeto →","resources":"RECURSOS PARA COMPRADORES","before":"Antes de pedir uma cotação","matrix":"Critérios de compra, não certificações da XUYI nem prazos garantidos; confirme o modelo e as regras do mercado.","check":"Checklist do comprador","faq":"Perguntas frequentes","cta":"Precisa de cotação para um modelo específico?","ctap":"Envie modelo, material, quantidade, arte e destino para avaliar opções verificadas.","button":"Solicitar cotação de garrafas →","related":"Leituras relacionadas","continue":"CONTINUE LENDO","published":"Publicado","sourceNext":"Próximo passo","sourceRefs":"Referências oficiais"},
"ru":{"home":"Главная","guide":"Руководство по закупке","in":"В ЭТОМ РУКОВОДСТВЕ","quote":"Обсудить проект →","resources":"РЕСУРСЫ ДЛЯ ПОКУПАТЕЛЕЙ","before":"Перед запросом цены","matrix":"Критерии покупателя, а не сертификаты XUYI или гарантия сроков: проверьте модель и требования рынка.","check":"Чек-лист покупателя","faq":"Часто задаваемые вопросы","cta":"Нужна цена конкретной модели?","ctap":"Пришлите модель, материал, количество, макет и страну назначения для проверки вариантов.","button":"Запросить предложение на бутылки →","related":"Связанные статьи","continue":"ПРОДОЛЖИТЬ ЧТЕНИЕ","published":"Опубликовано","sourceNext":"Следующий шаг","sourceRefs":"Официальные источники"},
"tr":{"home":"Ana Sayfa","guide":"Satın Alma Rehberi","in":"BU REHBERDE","quote":"Projenizi görüşün →","resources":"ALICI KAYNAKLARI","before":"Teklif istemeden önce","matrix":"Alıcı karar kriterleridir; XUYI sertifikası veya garanti edilen terminler değildir. Modeli ve pazar kurallarını doğrulayın.","check":"Alıcı kontrol listesi","faq":"Sık sorulan sorular","cta":"Belirli bir model için fiyat mı gerekiyor?","ctap":"Doğrulanmış seçenekler için model, malzeme, miktar, tasarım ve hedef pazarı bildirin.","button":"Şişe teklifi isteyin →","related":"İlgili okumalar","continue":"OKUMAYA DEVAM","published":"Yayınlanma","sourceNext":"Sonraki adım","sourceRefs":"Resmî kaynaklar"}}
E=lambda s:html.escape(str(s),quote=True)
def link_for(loc,path):
 if not path.startswith("/") or path.startswith("//"):raise ValueError(path)
 return "/"+loc+path
def related_info(slug,loc):
 # For older approved articles, use the localized D1 metadata captured in
 # the build snapshot; never modify that article's own content.
 if slug in TRANS and loc in TRANS[slug]:
  d=TRANS[slug][loc];return d["title"],d["description"]
 snap=ROOT/"_local_ops"/"build-snapshot.json"
 if snap.exists():
  rows=json.loads(snap.read_text(encoding="utf8")).get("translations",[])
  for row in rows:
   if row.get("resourceId")=="page:/blog/"+slug+"/" and row.get("locale")==loc:
    fields=row.get("content",{})
    if fields.get("title") and fields.get("description"):
     return fields["title"],fields["description"]
 article=GUIDES[slug];return article["title"],article["description"]
def local_main(post,locale):
 t=TRANS[post["slug"]][locale];mat=MATRICES[post["slug"]];u=UI[locale];prefix="/"+locale
 def T(key):return E(t[key])
 def A(href,name,classes=""):return '<a '+(('class="'+E(classes)+'" ') if classes else '')+'href="'+E(link_for(locale,href))+'">'+E(name)+'</a>'
 out='<section class="page-intro"><div class="shell"><div class="breadcrumb">'+A("/",u["home"])+' / '+A("/blog/","Blog")+' / '+E(u["guide"])+'</div><span class="eyebrow">XUYI · PLASTIC DRINKWARE</span><h1>'+T("title")+'</h1><p>'+T("description")+'</p></div></section>'
 out+='<section class="section blog-editorial"><div class="shell"><div class="blog-detail__cover"><img src="'+E(post["cover"])+'" alt="'+T("title")+' | XUYI" loading="lazy" decoding="async"></div><div class="blog-editorial__layout"><aside class="blog-editorial__aside"><div class="blog-toc"><span class="eyebrow">'+E(u["in"])+'</span><nav aria-label="'+E(u["in"])+'">'
 for i in range(len(post["sections"])):out+='<a href="#article-section-'+str(i)+'">'+T(f"sections.{i}.heading")+'</a>'
 out+='</nav>'+A("/contact/#inquiry",u["quote"],"blog-toc__quote")+'</div></aside><article class="article blog-editorial__body"><div class="blog-meta"><span>'+E(u["resources"])+'</span><span><time datetime="2026-10-20">'+E(u["published"])+' 2026-10-20</time></span></div>'
 out+='<p class="blog-lede">'+T("intro")+'</p><div class="blog-takeaway"><strong>'+E(u["before"])+'</strong><ul>'
 for i in range(3):out+='<li>'+T(f"checklist.{i}")+'</li>'
 out+='</ul></div>'
 for i,section in enumerate(post["sections"]):
  out+='<section class="blog-section" id="article-section-'+str(i)+'"><h2>'+T(f"sections.{i}.heading")+'</h2><p>'+T(f"sections.{i}.paragraph")
  for note in [x for x in post.get("product_notes",[]) if x["section"]==i]:
   sku=str(note["sku"]);txt=note["text"][locale];assert txt.count("{product}")==1
   before,after=txt.split("{product}")
   out+=' <span class="blog-editorial__product-note" data-editorial-model="'+E(sku)+'">'+E(before)+A('/products/'+sku+'/',note["label"][locale],"blog-editorial__product-link")+E(after)+'</span>'
  out+='</p></section>'
 out+='<nav class="blog-buyer-matrix__links blog-inline-links" aria-label="'+E(u["related"])+'">'
 for i,(label,href) in enumerate(post["inline_links"]):out+=A(href,t[f"inline.{i}"]+' →')
 out+='</nav>'
 out+='<section class="blog-buyer-matrix" id="buyer-decision-table"><h2>'+T("matrix.title")+'</h2><p>'+T("matrix.intro")+'</p><div class="blog-buyer-matrix__scroll"><table><thead><tr>'
 for i in range(3):out+='<th scope="col">'+T(f"matrix.head.{i}")+'</th>'
 out+='</tr></thead><tbody>'
 for i,row in enumerate(mat["rows"]):
  out+='<tr><th scope="row">'+T(f"matrix.rows.{i}.0")+'</th><td>'+T(f"matrix.rows.{i}.1")+'</td><td>'+T(f"matrix.rows.{i}.2")+'</td></tr>'
 out+='</tbody></table></div><p class="blog-buyer-matrix__note">'+E(u["matrix"])+'</p><nav class="blog-buyer-matrix__links" aria-label="'+E(u["guide"])+'">'
 for i,(label,path) in enumerate(mat["links"]):out+=A(path,t[f"matrix.links.{i}"]+' →')
 out+='</nav></section>' 
 if post["slug"] in EVIDENCE:
  evidence=EVIDENCE[post["slug"]]
  out+='<section class="blog-evidence" id="primary-sources" aria-labelledby="primary-sources-heading"><span class="eyebrow">SOURCE-CHECKED BUYER NOTES</span><h2 id="primary-sources-heading">'+T("sources.title")+'</h2><p>'+T("sources.insight")+'</p><p><strong>'+E(u["sourceNext"])+'</strong> '+T("sources.next_step")+'</p><h3>'+E(u["sourceRefs"])+'</h3><ul>' 
  for j,source in enumerate(evidence["sources"]):
   assert source["url"].startswith(("https://www.fda.gov/","https://eur-lex.europa.eu/","https://www.uspto.gov/","https://www.pantone.com/","https://www.eastman.com/","https://health.clevelandclinic.org/"))
   out+='<li><a href="'+E(source["url"])+'" target="_blank" rel="noopener noreferrer">'+T(f"sources.{j}")+' ↗</a></li>' 
  out+='</ul><p class="blog-evidence__caveat">'+T("sources.caveat")+'</p></section>' 
 out+='<section class="blog-checklist"><h2>'+E(u["check"])+'</h2><ul>' 
 for i,_ in enumerate(post["checklist"]):out+='<li>'+T(f"checklist.{i}")+'</li>'
 out+='</ul></section><section class="blog-faq"><h2>'+E(u["faq"])+'</h2>'
 for i,_ in enumerate(post["faqs"]):
  out+='<details><summary>'+T(f"faqs.{i}.question")+'</summary><p>'+T(f"faqs.{i}.answer")+'</p></details>'
 out+='</section><div class="blog-editorial__cta"><h2>'+E(u["cta"])+'</h2><p>'+E(u["ctap"])+'</p>'+A("/contact/#inquiry",u["button"],"button")+'</div>'
 out+='<section class="section section--soft blog-related"><div class="shell"><div class="section__head"><div><span class="eyebrow">'+E(u["continue"])+'</span><h2 class="section__title">'+E(u["related"])+'</h2></div></div><div class="blog-related__grid">'
 for related in post["related"]:
  title,description=related_info(related,locale)
  out+='<article class="blog-related__item">'+A("/blog/"+related+"/",title) +'<p>'+E(description)+'</p></article>'
 out+='</div></div></section></article></div></div></section>'
 assert out.count('class="blog-editorial__product-link"')==3
 assert out.count('class="blog-related__item"')==3
 return out

def sql_quote(v):return "'"+str(v).replace("'","''")+"'"
def save(name,sql):
 (OUT/name).write_text(sql+"\n",encoding="utf8")
def localized_card(post,locale):
 t=TRANS[post["slug"]][locale];u=UI[locale]
 href=link_for(locale,"/blog/"+post["slug"]+"/")
 # D1 stores canonical /blog/... and link localizer adds prefix exactly once.
 href="/blog/"+post["slug"]+"/"
 img='<a class="news-card__image" href="'+E(href)+'"><img src="'+E(post["cover"])+'" alt="'+E(t["title"])+' | XUYI" loading="lazy" decoding="async"></a>'
 return '<article class="news-card">'+img+'<div class="news-card__info"><span class="news-card__category">'+E(u["resources"])+'</span><h3><a href="'+E(href)+'">'+E(t["title"])+'</a></h3><p>'+E(t["description"])+'</p><a class="news-card__read" href="'+E(href)+'">'+E(u["continue"])+' →</a></div></article>'

def prepare():
 total=0
 posts=[]
 translations=[]
 index_cards=[]
 for slug in SLUGS:
  post=GUIDES[slug]
  posts.append({"slug":slug,"post":post,"publishedAt":"2026-10-20T00:00:00Z"})
  payload=json.dumps(post,ensure_ascii=False,separators=(",",":"))
  stmt="INSERT INTO xuyi_blog_posts(slug,status,content_json,published_at,updated_at) VALUES ("+sql_quote(slug)+",'published',"+sql_quote(payload)+",'2026-10-20T00:00:00Z',CURRENT_TIMESTAMP) ON CONFLICT(slug) DO NOTHING;"
  save(slug+"-post.sql",stmt);total+=1
  for loc in LOCALES:
   t=TRANS[slug][loc]
   main_html=local_main(post,loc)
   content={"title":t["title"],"description":t["description"],"mainHtml":main_html}
   translations.append({"route":"/blog/"+slug+"/","locale":loc,**content})
   payload=json.dumps(content,ensure_ascii=(loc=="ru"),separators=(",",":"))
   rid="page:/blog/"+slug+"/"
   stmt="INSERT INTO xuyi_translation_overrides(resource_id,locale,translated_json,reviewed_at) VALUES ("+sql_quote(rid)+","+sql_quote(loc)+","+sql_quote(payload)+",'2026-10-20') ON CONFLICT(resource_id,locale) DO NOTHING;"
   save(slug+"-"+loc+".sql",stmt)
   total+=1
 for loc in LOCALES:
  statements=[]
  for slug in SLUGS:
   post=GUIDES[slug];card=localized_card(post,loc)
   index_cards.append({"locale":loc,"slug":slug,"html":card})
   # A guarded, append-only D1 CMS update: never replace existing owner copy.
   jsonpath="$.mainHtml"
   expression="json_extract(translated_json,'"+jsonpath+"')"
   tail="'</div></div></section>'"
   newhtml="substr("+expression+",1,length("+expression+")-length("+tail+"))||"+sql_quote(card)+"||"+tail
   stmt="UPDATE xuyi_translation_overrides SET translated_json=json_set(translated_json,'"+jsonpath+"',"+newhtml+"),reviewed_at='2026-10-20' WHERE resource_id='page:/blog/' AND locale="+sql_quote(loc)+" AND substr("+expression+",-length("+tail+"))="+tail+" AND instr("+expression+","+sql_quote("/blog/"+slug+"/")+")=0;"
   statements.append(stmt)
  save("index-"+loc+".sql","\n".join(statements))
 manifest={"posts":posts,"translations":translations,"indexCards":index_cards}
 (OUT/"payload.json").write_text(json.dumps(manifest,ensure_ascii=False,separators=(",",":")),encoding="utf8")
 print("BLOG_CMS_SQL_PREPARED",total,"ARTICLES/TRANSLATIONS + 4 INDEX FILES; API_PAYLOAD",len(posts),len(translations),len(index_cards))
if __name__=="__main__":prepare()
