"""User-supplied LO source photographs: eight five-language product pages.

No CMS schema or new database table. Dimensions and PC+PP follow the source
photo's specification panel. Never present optional material engineering as
certification of the photographed SKU.
"""
import html
import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT=Path(__file__).resolve().parent
DATA=json.loads((ROOT/"data/lo-products.json").read_text(encoding="utf-8"))
LO_PRODUCTS=DATA["products"]
LO_MODELS=frozenset(p["model"] for p in LO_PRODUCTS)
UI_LABELS=json.loads((ROOT/"data/ui-translations.json").read_text(encoding="utf-8"))
IMAGE_LABELS={
 "en":("main product photo","image","product view"),
 "es":("foto principal del producto","imagen","vista del producto"),
 "pt":("foto principal do produto","imagem","vista do produto"),
 "ru":("основное фото товара","изображение","вид товара"),
 "tr":("ana ürün fotoğrafı","görsel","ürün görünümü")}

COPY={
 "en":dict(eyebrow="PLASTIC WATER BOTTLES · OEM WHOLESALE",model="Model",spec="Product Specifications",
  material="Catalog materials",capacity="Capacity",size="Approximate width × height",
  colors="Color options",colorsValue="Colors shown; confirm available variants",
  pack="Carton & packing",packValue="Please request packing specifications",
  imagesNote="Actual product photos. Color shades and dimensions may vary by batch.",
  introduction="Wholesale drinkware for distributors, brands and bulk buying projects. Share the model and intended use for an accurate quote.",
  cta="Request a Wholesale Quote",sample="Request a Sample",
  featuresTitle="Bottle Design & Buying Details",design="Real product photography",
  designText="Review handle, closure, drinking opening, capacity and the available designs from the photographed model.",
  terms="OEM Logo, Color & Packaging",termsText="Discuss the chosen bottle, decoration area, logo artwork, target quantity and retail or export packaging. Feasibility and MOQ are confirmed per order.",
  special="Custom Materials & Application Requirements",
  specialText="Need a BPA-free material option or a bottle designed for water at 100°C? Ask us to assess an alternative resin and the complete lid, straw and sealing assembly. These are custom project requirements, NOT verified claims for this standard PC+PP model; feasibility and any performance claim require an agreed material specification and finished-product tests.",
  materialNotice="PC+PP is the material combination shown in the source sheet, not a part-level bill of materials. Confirm resin grades, component materials and food-contact documentation for your market.",
  info="The image sheet states hand-measured dimensions; confirm production drawings before ordering."),
 "es":dict(eyebrow="BOTELLAS DE PLÁSTICO · MAYORISTA Y OEM",model="Modelo",spec="Especificaciones del producto",
  material="Materiales del catálogo",capacity="Capacidad",size="Anchura × altura aproximadas",
  colors="Opciones de color",colorsValue="Colores mostrados; confirmar variantes",
  pack="Caja y embalaje",packValue="Solicite los datos del embalaje",
  imagesNote="Fotos reales del producto. Los tonos y las dimensiones pueden variar.",
  introduction="Botellas para distribuidores, marcas y compras al por mayor. Indique modelo y uso previsto para una cotización exacta.",
  cta="Solicitar cotización mayorista",sample="Solicitar muestra",
  featuresTitle="Diseño y detalles de compra",design="Fotografías del producto",
  designText="Revise el asa, la tapa, la abertura, la capacidad y los diseños visibles de este modelo.",
  terms="Logotipo, color y embalaje OEM",termsText="Consulte la decoración, los colores, el logotipo, la cantidad y el embalaje. La viabilidad y el pedido mínimo dependen del proyecto.",
  special="Materiales especiales y requisitos de uso",
  specialText="¿Necesita una alternativa de material sin BPA o para agua a 100 °C? Solicite una evaluación de la resina y del conjunto de tapa, pajita y juntas. Son requisitos de desarrollo, NO prestaciones verificadas de este modelo PC+PP; deben confirmarse mediante especificaciones y ensayos del producto terminado.",
  materialNotice="PC+PP es la combinación de materiales del catálogo, no el desglose por pieza. Confirme resinas y documentos de contacto alimentario para su mercado.",
  info="Las dimensiones de la ficha son medidas manualmente y aproximadas."),
 "pt":dict(eyebrow="GARRAFAS DE PLÁSTICO · ATACADO E OEM",model="Modelo",spec="Especificações do produto",
  material="Materiais do catálogo",capacity="Capacidade",size="Largura × altura aproximadas",
  colors="Cores disponíveis",colorsValue="Cores nas fotos; confirmar variantes",
  pack="Caixas e embalagem",packValue="Solicite os dados de embalagem",
  imagesNote="Fotografias reais do produto. Tons e medidas podem variar.",
  introduction="Garrafas para distribuidores, marcas e compras por grosso. Envie o modelo e a aplicação para um orçamento correto.",
  cta="Pedir cotação por grosso",sample="Pedir amostra",
  featuresTitle="Design e detalhes de compra",design="Fotografias do produto",
  designText="Veja a pega, a tampa, a abertura, a capacidade e os modelos visíveis nas fotografias.",
  terms="Logótipo, cor e embalagem OEM",termsText="Consulte a decoração, as cores, o logótipo, a quantidade e a embalagem. A viabilidade e o MOQ dependem do pedido.",
  special="Materiais personalizados e condições de uso",
  specialText="Precisa de material sem BPA ou de uma garrafa para água a 100 °C? Peça uma avaliação da resina alternativa e do conjunto de tampa, palhinha e vedações. São requisitos de projeto, NÃO características verificadas do modelo PC+PP; exigem especificações acordadas e ensaios do produto final.",
  materialNotice="PC+PP é a combinação do catálogo, não a composição de cada peça. Confirme as resinas e os documentos de contacto alimentar para o mercado de destino.",
  info="As medidas da ficha foram obtidas manualmente e são aproximadas."),
 "ru":dict(eyebrow="ПЛАСТИКОВЫЕ БУТЫЛКИ · ОПТ И OEM",model="Модель",spec="Характеристики товара",
  material="Материалы по каталогу",capacity="Объём",size="Примерная ширина × высота",
  colors="Цвета",colorsValue="Цвета на фото; уточните варианты",
  pack="Упаковка и коробки",packValue="Уточните параметры упаковки",
  imagesNote="Реальные фотографии товара. Оттенки и размеры могут различаться.",
  introduction="Пластиковые бутылки для дистрибьюторов и оптовых покупателей. Укажите модель и назначение для расчёта заказа.",
  cta="Запросить оптовую цену",sample="Запросить образец",
  featuresTitle="Конструкция и условия заказа",design="Реальные фотографии",
  designText="Оцените ручку, крышку, горлышко, объём и показанные варианты изделия.",
  terms="Логотип, цвет и упаковка OEM",termsText="Обсудите нанесение логотипа, цвета, количество и упаковку. Возможности и минимальная партия подтверждаются по заказу.",
  special="Индивидуальные материалы и условия применения",
  specialText="Нужен материал без BPA или бутылка для воды температурой 100 °C? Запросите оценку другого полимера и всей конструкции: крышки, трубочки и уплотнений. Это требования к разработке, а НЕ подтверждённые свойства стандартной модели PC+PP. Нужны согласованные спецификации и испытания готового изделия.",
  materialNotice="PC+PP — общий состав из каталога, а не состав отдельных деталей. Уточните марки материалов и документы для контакта с пищей для нужного рынка.",
  info="Размеры в исходном описании получены вручную, возможна погрешность."),
 "tr":dict(eyebrow="PLASTİK SU ŞİŞELERİ · TOPTAN VE OEM",model="Model",spec="Ürün Özellikleri",
  material="Katalog malzemeleri",capacity="Kapasite",size="Yaklaşık genişlik × yükseklik",
  colors="Renk seçenekleri",colorsValue="Fotoğraftaki renkler; seçenekleri doğrulayın",
  pack="Koli ve ambalaj",packValue="Ambalaj detaylarını isteyin",
  imagesNote="Gerçek ürün fotoğrafları. Renk tonları ve ölçüler değişebilir.",
  introduction="Distribütörler, markalar ve toplu satın alma projeleri için su şişeleri. Doğru teklif için model ve kullanım amacını bildirin.",
  cta="Toptan Teklif İsteyin",sample="Numune İsteyin",
  featuresTitle="Tasarım ve Satın Alma Detayları",design="Gerçek ürün fotoğrafları",
  designText="Sapı, kapağı, ağızlığı, kapasiteyi ve fotoğraflardaki tasarımı inceleyin.",
  terms="OEM Logo, Renk ve Ambalaj",termsText="Logo konumu, renk, sipariş miktarı ve ambalajı görüşün. Uygunluk ve minimum sipariş miktarı projeye göre onaylanır.",
  special="Özel Malzemeler ve Kullanım Gereksinimleri",
  specialText="BPA içermeyen malzeme veya 100 °C su kullanımı için tasarlanmış bir şişe mi gerekiyor? Alternatif reçine ve kapak, pipet, conta grubunun değerlendirilmesini isteyin. Bunlar özel proje gereksinimleridir; standart PC+PP modelin doğrulanmış özellikleri DEĞİLDİR. Nihai ürün teknik şartları ve test sonuçları gereklidir.",
  materialNotice="PC+PP katalogdaki birleşik malzeme bilgisidir; her parçanın malzemesini göstermez. Hedef pazar için reçine sınıfını ve gıda temas belgelerini doğrulayın.",
  info="Kaynak görseldeki ölçüler elle alınmıştır, sapma olabilir.")
}

# Genuine source-detail photography stays language-neutral. The surrounding
# captions and all claims are genuine HTML text in the selected page language.
DETAIL_COPY={
 "en":("Product Detail Photography","Real usage scenes and bottle design",
       "Lifestyle & carrying views","Drinking lid, straw and color variants",
       "These scenes come from the supplied product detail photography. Please confirm the exact cap, straw and included accessories for your selected variant."),
 "es":("Fotografías de producto en detalle","Escenas reales de uso y diseño",
       "Uso diario y transporte","Tapa, pajita y colores",
       "Imágenes extraídas de la ficha fotográfica del producto. Confirme la tapa, la pajita y los accesorios de la variante elegida."),
 "pt":("Fotografias detalhadas do produto","Cenas reais de uso e design",
       "Utilização e transporte","Tampa, palhinha e cores",
       "Imagens retiradas das fotografias de detalhe. Confirme a tampa, a palhinha e os acessórios da variante escolhida."),
 "ru":("Подробные фотографии товара","Реальные сцены использования и конструкция",
       "Использование и переноска","Крышка, трубочка и цвета",
       "Фото взяты из оригинальных материалов о товаре. Уточните крышку, трубочку и комплектацию выбранного варианта."),
 "tr":("Ayrıntılı ürün fotoğrafları","Gerçek kullanım sahneleri ve tasarım",
       "Günlük kullanım ve taşıma","Kapak, pipet ve renkler",
       "Görseller ürünün orijinal detay fotoğraflarından alınmıştır. Seçilen varyantın kapağını, pipetini ve aksesuarlarını doğrulayın.")
}

def add_products(series):
    if DATA.get("schemaVersion")!=1 or len(LO_PRODUCTS)!=8:raise ValueError("Unexpected LO catalog")
    for p in LO_PRODUCTS:
        model=p["model"]
        if model in series:raise ValueError("LO source model collision: "+model)
        if not model.startswith("LO-00") or p["material"]!="PC+PP" or len(p["images"])!=3:
            raise ValueError("LO source model/material/images must be reviewed")
        for img in p["images"]:
            file=ROOT/img.lstrip("/")
            if not img.startswith("/assets/lo/") or not file.is_file():
                raise ValueError("Missing LO photo: "+img)
        if [x.get("purpose") for x in p.get("detailImages",[])]!=["lifestyle","design"]:
            raise ValueError("Missing LO source-detail visual sections: "+model)
        for img in p["detailImages"]:
            src=str(img.get("src",""))
            if not src.startswith("/assets/lo/detail/") or not (ROOT/src.lstrip("/")).is_file():
                raise ValueError("Missing source-detail photo: "+src)
        row={k:p.get(k,"") for k in ("name","description","capacity","material","colors","packing","dimensions","carton_quantity","carton_size")}
        row.update({"model":model,"slug":p["slug"],"category":p["category"],"images":p["images"],
                   "variants":[{**row,"model":model}],"manualNew":True,"loNew":True})
        series[model]=row

def detail(product,locale):
    if locale not in COPY:raise ValueError("No LO translation for "+locale)
    w=COPY[locale];model=product["model"]
    data=next(x for x in LO_PRODUCTS if x["model"]==model)
    item=data["locales"][locale]
    esc=lambda s:html.escape(str(s),quote=True)
    prefix="" if locale=="en" else "/"+locale
    photos=product["images"];name=item["title"]
    image_labels=IMAGE_LABELS[locale]
    photograph='<img id="main-photo" src="'+esc(photos[0])+'" alt="'+esc(name)+' - '+esc(image_labels[0])+'" loading="eager" decoding="async">'
    thumbs='<div class="product-detail__thumbs">'+''.join(
      '<button type="button" class="product-detail__thumb" data-main-photo="'+esc(path)+'" aria-label="'+esc(name)+' - '+esc(image_labels[1])+' '+str(i)+'">'
      '<img src="'+esc(path)+'" alt="'+esc(name)+' - '+esc(image_labels[2])+' '+str(i)+'" loading="lazy"></button>'
      for i,path in enumerate(photos,1))+'</div>'
    def spec(label,value):return '<tr><th scope="row">'+esc(label)+'</th><td>'+esc(value)+'</td></tr>'
    rows=(spec(w["model"],model)+spec(w["capacity"],product["capacity"])+spec(w["material"],product["material"])+
          spec(w["size"],product["dimensions"])+spec(w["colors"],w["colorsValue"])+spec(w["pack"],w["packValue"]))
    link=prefix+"/contact/?model="+quote(model,safe="")
    overview=(
      '<section class="section product-overview"><div class="shell"><nav class="breadcrumb"><a href="'+(prefix+"/")+'">'+
      esc(UI_LABELS.get(locale,{}).get("Home","Home"))+'</a> / <a href="'+prefix+'/products/">'+
      esc(UI_LABELS.get(locale,{}).get("Products","Products"))+'</a> / '+esc(model)+'</nav>'
      '<div class="product-detail"><div class="product-detail__photos"><div class="product-detail__main">'+
      photograph+'</div>'+thumbs+'<p class="copy-muted">'+esc(w["imagesNote"])+'</p></div>'
      '<div><span class="eyebrow">'+esc(w["eyebrow"])+' · '+esc(model)+'</span>'
      '<h1>'+esc(name)+'</h1><div class="product-detail__lead"><p class="copy-muted">'+esc(w["introduction"])+'</p></div>'
      '<table class="spec"><tbody>'+rows+'</tbody></table><div class="actions"><a class="button" href="'+esc(link)+'#inquiry">'+
      esc(w["cta"])+' →</a><a class="button button--outline" href="'+esc(link)+'&amp;type=Samples#inquiry">'+
      esc(w["sample"])+' ↗</a></div><p class="product-detail__quote-note">'+esc(w["info"])+'</p>'
      '<p class="notice">'+esc(w["materialNotice"])+'</p></div></div></div></section>')
    benefits=''.join('<article class="benefit"><h3>'+esc(w[h])+'</h3><p>'+esc(w[t])+'</p></article>'
                     for h,t in (("design","designText"),("terms","termsText"),("special","specialText")))
    details='<section class="section section--soft product-content"><div class="shell"><div class="section__head"><div><span class="eyebrow">'+esc(w["eyebrow"])+'</span><h2 class="section__title">'+esc(w["featuresTitle"])+'</h2></div></div><div class="grid grid--3">'+benefits+'</div></div></section>'
    order='<section class="section product-ordering"><div class="shell"><div class="section__head"><div><span class="eyebrow">OEM / ODM</span><h2 class="section__title">'+esc(w["terms"])+'</h2><p>'+esc(w["info"])+'</p></div></div><p class="product-content__cta"><a class="button" href="'+esc(link)+'#inquiry">'+esc(w["cta"])+' →</a></p></div></section>'
    faqs={
      "en":("Can I request BPA-free materials or a 100°C water-use design?","These are custom project targets, not standard-model claims. The resin, cap, straw and seals must be evaluated and the final assembly tested before confirming."),
      "es":("¿Se pueden solicitar materiales sin BPA o uso a 100 °C?","Son objetivos de desarrollo, no características confirmadas del modelo estándar. Hay que evaluar los materiales y ensayar el producto terminado."),
      "pt":("Posso solicitar materiais sem BPA ou uso com água a 100 °C?","São requisitos de desenvolvimento, não características confirmadas do modelo normal. Precisamos avaliar os materiais e testar o produto final."),
      "ru":("Можно запросить материалы без BPA или конструкцию для воды 100 °C?","Это требования к индивидуальному проекту, а не свойства стандартной модели. Нужны оценка материалов и испытания готовой бутылки."),
      "tr":("BPA içermeyen malzeme veya 100 °C su gereksinimi talep edilebilir mi?","Bunlar standart ürün özelliği değil, özel proje hedefleridir. Malzemeler değerlendirilmeli ve bitmiş ürün test edilmelidir.")
    }
    q,a=faqs[locale]
    faq='<section class="section section--soft"><div class="shell"><div class="faq-list"><details><summary>'+esc(q)+'</summary><p>'+esc(a)+'</p></details></div></div></section>'
    photo_words=DETAIL_COPY[locale]
    photo_figure=[]
    for i,img in enumerate(data["detailImages"]):
        caption=photo_words[2+i]
        photo_figure.append(
          '<figure class="lo-photo-details__figure"><img src="'+esc(img["src"])+
          '" width="'+str(int(img["width"]))+'" height="'+str(int(img["height"]))+
          '" loading="lazy" decoding="async" alt="'+esc(name+" — "+caption)+
          '"><figcaption>'+esc(caption)+'</figcaption></figure>')
    photo_details=(
      '<section class="section lo-photo-details" id="product-detail-photos">'
      '<div class="shell"><div class="section__head"><div><span class="eyebrow">'+esc(photo_words[0])+
      '</span><h2 class="section__title">'+esc(photo_words[1])+'</h2></div></div>'
      '<div class="lo-photo-details__stack">'+''.join(photo_figure)+'</div>'
      '<p class="lo-photo-details__note">'+esc(photo_words[4])+'</p></div></section>')
    from product_material_performance import inject
    return inject(overview+details+photo_details+order+faq,product,locale,"/products/"+data["slug"]+"/")

def catalog_cards(body,locale,route):
    """Append LO products into a D1-translated existing HTML catalog grid.

    D1 retains ownership of all legacy translated text; only new items are
    inserted. Validate the exact HTML grid before changing anything.
    """
    if locale not in COPY:raise ValueError("Unknown LO locale "+str(locale))
    if route!="/products/" and not route.startswith("/collections/"):
        return body
    from site_renderer import CAT
    selected=(LO_PRODUCTS if route=="/products/" else [
        p for p in LO_PRODUCTS if route=="/collections/"+CAT[p["category"]][1]+"/"])
    if not selected:return body
    start=body.find('<div class="grid grid--4 product-grid">')
    if start<0:raise ValueError("Missing catalog card grid: "+locale+" "+route)
    begin=start+len('<div class="grid grid--4 product-grid">')
    depth=1;close=None
    for m in re.finditer(r'<div\b[^>]*>|</div\s*>',body[begin:],re.I):
        depth+=(-1 if m.group().startswith("</") else 1)
        if depth==0:
            close=begin+m.start()
            break
    if close is None:raise ValueError("Unclosed catalog grid")
    esc=lambda v:html.escape(str(v),quote=True)
    model_labels={"en":"MODEL","es":"MODELO","pt":"MODELO","ru":"МОДЕЛЬ","tr":"MODEL"}
    markup=""
    for product in selected:
        slug=product["slug"]
        url=("/" if locale=="en" else "/"+locale+"/")+"products/"+slug+"/"
        # Idempotent if the original translated HTML was already updated.
        if 'href="'+url+'"' in body[begin:close]:
            continue
        loc=product["locales"][locale]
        cat=CAT[product["category"]][1]
        title=loc["title"]
        search=title+" "+product["model"]+" "+product["capacity"]+" "+product["material"]+" wholesale OEM"
        img=product["images"][0]
        link_text={"en":"View Product","es":"Ver producto","pt":"Ver produto",
                   "ru":"Подробнее","tr":"Ürünü İncele"}[locale]
        markup+=(
          '<a class="product-card" data-product-card data-category="'+esc(cat)+'" data-search="'+esc(search.lower())+'" href="'+url+'">'
          '<div class="product-card__image"><img src="'+esc(img)+'" alt="'+esc(title)+' — '+esc(product["model"])+'" loading="lazy" decoding="async"></div>'
          '<div class="product-card__body"><span class="product-card__small">'+esc(model_labels[locale])+' '+esc(product["model"])+'</span><h3>'+esc(title)+'</h3><span class="product-card__link">'+esc(link_text)+' ↗</span></div></a>')
    # LO products were appended after the 85 legacy models and therefore hidden
    # by the 18-items-per-page initial view. Hoist reviewed LO cards first in
    # both D1-overridden and source-built listings, without discarding edits.
    grid=body[begin:close]+markup
    selected_urls={
        ("/" if locale=="en" else "/"+locale+"/")+"products/"+p["slug"]+"/"
        for p in selected
    }
    seen={}
    card_pattern=re.compile(r'<a\b[^>]*\bdata-product-card\b[^>]*>.*?</a>',re.I|re.S)
    def extract_new(match):
        card=match.group(0)
        opening=card.split(">",1)[0]
        href=re.search(r'\bhref="([^"]+)"',opening)
        if not href or href.group(1) not in selected_urls:
            return card
        url=href.group(1)
        if url in seen:
            raise ValueError("Duplicate new product card: "+url)
        seen[url]=card
        return ""
    remaining=card_pattern.sub(extract_new,grid)
    if set(seen)!=selected_urls:
        raise ValueError("Missing new product cards in "+locale+" "+route+": "+str(selected_urls-set(seen)))
    labels={"en":"NEW","es":"NOVEDAD","pt":"NOVO","ru":"НОВИНКА","tr":"YENİ"}
    front=[]
    for product in selected:
        url=("/" if locale=="en" else "/"+locale+"/")+"products/"+product["slug"]+"/"
        card=seen[url]
        # Source-built or previously staged LO cards can already exist in D1
        # catalog HTML. Localize just their "MODEL" badge, never their SKU.
        card=re.sub(r'(<span class="product-card__small">)MODEL(\s+'+re.escape(product["model"])+r'</span>)',
                    lambda m:m.group(1)+esc(model_labels[locale])+m.group(2),card,count=1)
        if 'data-new-product=' not in card:
            card=card.replace(" data-product-card ",' data-product-card data-new-product="true" ',1)
        if 'class="product-card__new"' not in card:
            card=card.replace('<div class="product-card__body">',
                '<div class="product-card__body"><span class="product-card__new">'+esc(labels[locale])+'</span>',1)
        front.append(card)
    return body[:begin]+''.join(front)+remaining+body[close:]
