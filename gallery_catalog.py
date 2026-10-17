"""XUYI G-series factory model image gallery.

Factory model identity has been confirmed by the business owner. Individual
dimensions, materials, packaging and other data remain unconfirmed until
model-specific source specifications are available.
"""
import json,html,re
from pathlib import Path
from urllib.parse import quote
ROOT=Path(__file__).resolve().parent
GALLERY=json.loads((ROOT/"data/gallery-reference-products.json").read_text(encoding="utf8"))["items"]
G05_DEPTH=json.loads((ROOT/"data/g05-depth.json").read_text(encoding="utf8"))["g-05"]
UI_LABELS=json.loads((ROOT/"data/ui-translations.json").read_text(encoding="utf8"))
assert {p["sourceFolder"] for p in GALLERY}=={1,2,3,4,5,9,10,12}
LABELS={
"en":("Factory Model","Confirm model specifications with XUYI","XUYI G-series factory bottle model. For an accurate quotation, confirm its capacity, materials, dimensions, available components, carton packing and destination-market documentation.","Factory model photographs","Request quote","Request sample","View Product","Capacity","Materials / components","MOQ / packing","FACTORY MODEL"),
"es":("Modelo de fábrica","Confirme los datos del modelo con XUYI","Modelo de botella de fábrica de la serie G de XUYI. Para cotizar, confirme capacidad, materiales, dimensiones, componentes, embalaje y documentación del mercado de destino.","Fotos del modelo de fábrica","Solicitar cotización","Solicitar muestra","Ver producto","Capacidad","Materiales y componentes","Pedido mínimo y embalaje","MODELO DE FÁBRICA"),
"pt":("Modelo de fábrica","Confirme as especificações com a XUYI","Modelo de garrafa de fábrica da série G da XUYI. Para cotação, confirme capacidade, materiais, dimensões, componentes, embalagem e documentação do mercado de destino.","Fotos do modelo de fábrica","Pedir orçamento","Pedir amostra","Ver produto","Capacidade","Materiais e componentes","Pedido mínimo e embalagem","MODELO DE FÁBRICA"),
"ru":("Заводская модель","Уточните характеристики модели в XUYI","Заводская модель бутылки серии G от XUYI. Для расчёта уточните объём, материалы, размеры, комплектующие, упаковку и документы для рынка назначения.","Фотографии заводской модели","Запросить цену","Запросить образец","Подробнее","Объём","Материалы и комплектующие","Минимальная партия и упаковка","ЗАВОДСКАЯ МОДЕЛЬ"),
"tr":("Fabrika modeli","Model özelliklerini XUYI ile doğrulayın","XUYI G serisi fabrika şişe modeli. Teklif için kapasite, malzemeler, ölçüler, bileşenler, koli ambalajı ve hedef pazar belgelerini doğrulayın.","Fabrika modeli fotoğrafları","Teklif isteyin","Numune isteyin","Ürünü incele","Kapasite","Malzemeler ve bileşenler","Asgari sipariş ve paketleme","FABRİKA MODELİ")}
def esc(v):return html.escape(str(v),quote=True)
def add_products(series):
 for p in GALLERY:
  m=p["model"];folder=p["sourceFolder"]
  if m in series or m!=f"G-{folder:02d}":raise ValueError("Invalid/duplicate gallery reference")
  if not all(src.startswith(f"/media/gallery/xuyi-g{folder:02d}-") for src in p["images"]):raise ValueError("Unapproved gallery photo")
  v={"model":m,"capacity":"","material":"","colors":"","packing":"","dimensions":"","carton_quantity":"","carton_size":""}
  series[m]={"model":m,"slug":p["slug"],"category":p["category"],"name":p["locales"]["en"],
   "images":p["images"],"capacity":"To confirm","material":"To confirm","colors":"","packing":"",
   "description":LABELS["en"][2],"variants":[v],"manualNew":True,"galleryReference":True,"factoryModel":True}
def g05_depth(product,locale):
    if product.get("model")!="G-05":return ""
    data=G05_DEPTH.get(locale) or G05_DEPTH["en"]
    cards="".join('<article class="benefit"><h3>'+esc(card["title"])+'</h3><p>'+esc(card["text"])+'</p></article>' for card in data["cards"])
    return ('<section class="section product-g05-depth" data-g05-depth="true"><div class="shell">'
      '<div class="section__head"><div><span class="eyebrow">'+esc(data["title"])+'</span><h2 class="section__title">'+esc(data["title"])+'</h2>'
      '<p>'+esc(data["intro"])+'</p></div></div><div class="grid grid--3">'+cards+'</div></div></section>')

def detail(product,locale):
 w=LABELS[locale];p=next(row for row in GALLERY if row["model"]==product["model"])
 prefix="" if locale=="en" else "/"+locale;name=p["locales"][locale]
 link=prefix+"/contact/?model="+quote(p["model"],safe="")
 main='<img id="main-photo" src="'+esc(p["images"][0])+'" alt="'+esc(name)+'" loading="eager">'
 thumbs=''.join('<button type="button" class="product-detail__thumb" data-main-photo="'+esc(src)+'"><img loading="lazy" src="'+esc(src)+'" alt="'+esc(name)+'"></button>' for src in p["images"])
 specs='<tr><th scope="row">'+esc(w[0])+'</th><td>'+esc(p["model"])+'</td></tr>'
 for k in w[7:10]:
  specs+='<tr><th scope="row">'+esc(k)+'</th><td>'+esc(w[1])+'</td></tr>'
 home=UI_LABELS.get(locale,{}).get("Home","Home")
 products=UI_LABELS.get(locale,{}).get("Products","Products")
 start=('<section class="section product-overview"><div class="shell"><nav class="breadcrumb"><a href="'+prefix+'/">'+esc(home)+'</a> / <a href="'+prefix+'/products/">'+esc(products)+'</a> / '+esc(p["model"])+'</nav>'
 '<div class="product-detail"><div class="product-detail__photos"><div class="product-detail__main">'+main+'</div><div class="product-detail__thumbs">'+thumbs+'</div></div>'
 '<div><span class="eyebrow">'+esc(w[0])+'</span><h1>'+esc(name)+'</h1><p class="copy-muted">'+esc(w[2])+'</p>'
 '<table class="spec"><tbody>'+specs+'</tbody></table><div class="actions">'
 '<a class="button" href="'+esc(link)+'#inquiry">'+esc(w[4])+' →</a><a class="button button--outline" href="'+esc(link)+'&amp;type=Samples#inquiry">'+esc(w[5])+' ↗</a></div>'
 '</div></div></div></section>')
 # Exact adjacent section structure also preserves existing material module insertion.
 notes='<section class="section section--soft product-content"><div class="shell"><h2 class="section__title">'+esc(w[0])+'</h2><p>'+esc(w[2])+'</p></div></section>'
 photos='<section class="section gallery-reference-photos"><div class="shell"><h2 class="section__title">'+esc(w[3])+'</h2><div class="gallery-reference-photos__grid">'
 for n,src in enumerate(p["images"],1):
  photos+='<figure><img src="'+esc(src)+'" alt="'+esc(name)+' - '+str(n)+'" loading="lazy"></figure>'
 photos+='</div><p class="copy-muted">'+esc(w[2])+'</p></div></section>'
 order=('<section class="section product-ordering"><div class="shell"><h2 class="section__title">'+esc(w[4])+
   '</h2><p>'+esc(w[2])+'</p><p class="product-content__cta"><a class="button" href="'+esc(link)+'#inquiry">'+esc(w[4])+
   ' →</a></p></div></section>')
 faq=('<section class="section section--soft"><div class="shell"><div class="faq-list"><details><summary>'+
   esc(w[0])+'</summary><p>'+esc(w[2])+'</p></details></div></div></section>')
 return start+notes+g05_depth(product,locale)+photos+order+faq
def catalog_cards(body,locale,route):
 from site_renderer import CAT
 if route!="/products/" and not route.startswith("/collections/"):return body
 chosen=[p for p in GALLERY if route=="/products/" or route=="/collections/"+CAT[p["category"]][1]+"/"]
 if not chosen:return body
 anchor='<div class="grid grid--4 product-grid">'
 s=body.find(anchor)
 if s<0:raise ValueError("Missing catalog grid "+route)
 begin=s+len(anchor);depth=1;close=None
 for match in re.finditer(r'<div\b[^>]*>|</div\s*>',body[begin:],re.I):
  depth+=-1 if match.group().startswith("</") else 1
  if depth==0:close=begin+match.start();break
 if close is None:raise ValueError("Unclosed product grid")
 source=body[begin:close];selected_urls={("/" if locale=="en" else "/"+locale+"/")+"products/"+p["slug"]+"/" for p in chosen}
 found={}
 def lift(m):
  card=m.group();href=re.search(r'\bhref="([^"]+)"',card.split(">",1)[0])
  if href and href.group(1) in selected_urls:
   if href.group(1) in found:raise ValueError("Duplicate "+href.group(1))
   found[href.group(1)]=card
   return ""
  return card
 remaining=re.sub(r'<a\b[^>]*\bdata-product-card\b[^>]*>.*?</a>',lift,source,flags=re.I|re.S)
 out=""
 for p in chosen:
  u=("/" if locale=="en" else "/"+locale+"/")+"products/"+p["slug"]+"/"
  card=found.get(u)
  if not card:
   name=p["locales"][locale];cat=CAT[p["category"]][1]
   card=('<a class="product-card" data-product-card data-category="'+esc(cat)+'" data-search="'+esc((p["model"]+" "+name).lower())+
     '" href="'+u+'"><div class="product-card__image"><img src="'+esc(p["images"][0])+'" alt="'+esc(name)+'" loading="lazy"></div>'
     '<div class="product-card__body"><span class="product-card__small">'+esc(p["model"])+
     '</span><h3>'+esc(name)+'</h3><span class="product-card__link">'+esc(LABELS[locale][6])+' ↗</span></div></a>')
  card=card.replace(' data-product-card ',' data-product-card data-gallery-reference="true" ',1)
  card=card.replace('<div class="product-card__body">','<div class="product-card__body"><span class="product-card__reference">'+esc(LABELS[locale][10])+' · G</span>',1)
  out+=card
 return body[:begin]+out+remaining+body[close:]
