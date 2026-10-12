"""XUYI photo reference gallery: G-xx are enquiry IDs, not factory model numbers."""
import json,html,re
from pathlib import Path
from urllib.parse import quote
ROOT=Path(__file__).resolve().parent
GALLERY=json.loads((ROOT/"data/gallery-reference-products.json").read_text(encoding="utf8"))["items"]
assert {p["sourceFolder"] for p in GALLERY}=={1,2,3,4,5,9,10,12}
LABELS={
"en":("Photo reference — not a factory model","Unconfirmed; ask for actual product specification","Style reference only. XUYI's G code is not the factory model. Materials, capacity, size, accessory availability, packing and certification are NOT verified.","Reference product photographs","Request quote","Request sample","View Product","Capacity","Materials / components","MOQ / packing","PHOTO REF"),
"es":("Referencia de foto — no es modelo de fábrica","Sin confirmar; solicite datos del producto","Referencia visual. El código G de XUYI no es el modelo de fábrica. Materiales, capacidad, dimensiones, accesorios y documentación no están verificados.","Fotos de referencia","Solicitar cotización","Solicitar muestra","Ver producto","Capacidad","Materiales y componentes","Pedido mínimo y embalaje","REF. FOTO"),
"pt":("Referência de foto — não é modelo de fábrica","Não confirmado; consulte as especificações","Referência visual. O código G da XUYI não é um modelo de fábrica. Material, capacidade, tamanho, acessórios e certificados não estão confirmados.","Fotografias de referência","Pedir orçamento","Pedir amostra","Ver produto","Capacidade","Materiais e componentes","Pedido mínimo e embalagem","REF. FOTO"),
"ru":("Фотоартикул — не заводская модель","Не подтверждено; запросите характеристики","Фотокаталог. Код G — внутренний номер XUYI, а не модель завода. Материал, объём, размеры, аксессуары и документы требуют подтверждения.","Фотографии модели","Запросить цену","Запросить образец","Подробнее","Объём","Материалы и комплектующие","Минимальная партия и упаковка","ФОТО"),
"tr":("Fotoğraf referansı — fabrika modeli değil","Doğrulanmadı; ayrıntıları sorun","Fotoğraf referansı. G kodu XUYI sorgu numarasıdır, fabrika modeli değildir. Malzeme, kapasite, boyut, aksesuar ve belgeler doğrulanmalıdır.","Referans fotoğraflar","Teklif isteyin","Numune isteyin","Ürünü incele","Kapasite","Malzemeler ve bileşenler","Asgari sipariş ve paketleme","FOTO REF")}
def esc(v):return html.escape(str(v),quote=True)
def add_products(series):
 for p in GALLERY:
  m=p["model"];folder=p["sourceFolder"]
  if m in series or m!=f"G-{folder:02d}":raise ValueError("Invalid/duplicate gallery reference")
  if not all(src.startswith(f"/media/gallery/xuyi-g{folder:02d}-") for src in p["images"]):raise ValueError("Unapproved gallery photo")
  v={"model":m,"capacity":"","material":"","colors":"","packing":"","dimensions":"","carton_quantity":"","carton_size":""}
  series[m]={"model":m,"slug":p["slug"],"category":p["category"],"name":p["locales"]["en"],
   "images":p["images"],"capacity":"To confirm","material":"To confirm","colors":"","packing":"",
   "description":LABELS["en"][2],"variants":[v],"manualNew":True,"galleryReference":True}
def detail(product,locale):
 w=LABELS[locale];p=next(row for row in GALLERY if row["model"]==product["model"])
 prefix="" if locale=="en" else "/"+locale;name=p["locales"][locale]
 link=prefix+"/contact/?model="+quote(p["model"],safe="")
 main='<img id="main-photo" src="'+esc(p["images"][0])+'" alt="'+esc(name)+'" loading="eager">'
 thumbs=''.join('<button type="button" class="product-detail__thumb" data-main-photo="'+esc(src)+'"><img loading="lazy" src="'+esc(src)+'" alt="'+esc(name)+'"></button>' for src in p["images"])
 specs='<tr><th scope="row">'+esc(w[0])+'</th><td>'+esc(p["model"])+'</td></tr>'
 for k in w[7:10]:
  specs+='<tr><th scope="row">'+esc(k)+'</th><td>'+esc(w[1])+'</td></tr>'
 start=('<section class="section product-overview"><div class="shell"><nav class="breadcrumb"><a href="'+prefix+'/">Home</a> / <a href="'+prefix+'/products/">Products</a> / '+esc(p["model"])+'</nav>'
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
 return start+notes+photos+order+faq
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