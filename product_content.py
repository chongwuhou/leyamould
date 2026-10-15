"""English structured XUYI product details built from catalog figures, not invented performance claims."""
import re,json
from site_renderer import CAT,SERIES,e,photo,product_grid,public_display_name,SITE_ORIGIN,render_template
from html import escape
PALETTE={
"星夜黑":"Midnight Black","奇幻粉":"Fantasy Pink","极光紫":"Aurora Purple","月芽白":"Moonlight White",
"嫩芽绿":"Sprout Green","罗兰紫":"Violet","海军蓝":"Navy Blue","藏青蓝":"Navy Blue",
"薄荷绿":"Mint Green","樱花粉":"Sakura Pink","石榴红":"Pomegranate Red","灵动紫":"Violet",
"军绿":"Army Green","浅蓝":"Light Blue","淡蓝":"Light Blue","淡紫":"Light Purple",
"淡绿":"Light Green","淡粉":"Light Pink","墨绿":"Dark Green","米白":"Ivory",
"灰":"Gray","黑":"Black","白":"White","紫":"Purple","红":"Red","绿":"Green","蓝":"Blue",
"粉":"Pink","青":"Cyan","棕":"Brown","橙":"Orange","黄":"Yellow","透明":"Clear"
}
UNUSUAL={"本紫色","寄红色"}
def localize_colors(text):
 if not text:return "Please confirm available colors"
 if not __import__("re").search(r"[\u3400-\u9fff]",str(text)):return str(text)
 text=str(text).replace("          "," ").replace("、","/").replace("，","/")
 pieces=[]
 for raw in text.split("/"):
  raw=raw.strip()
  if not raw:continue
  if any(word in raw for word in UNUSUAL):pieces.append("Color to be confirmed");continue
  gradient="渐变" in raw
  transparent="透明" in raw and raw not in ("透明款","透明")
  raw=re.sub(r"(渐变款|渐变|透明款|透明|款|色)","",raw)
  segments=[];unknown=False
  while raw:
   found=next((key for key in sorted(PALETTE,key=len,reverse=True) if raw.startswith(key)),None)
   if not found:unknown=True;break
   segments.append(PALETTE[found]);raw=raw[len(found):]
  if unknown:
   pieces.append("Color option to be confirmed")
  elif segments:
   name=(" to ".join(segments)+" gradient") if gradient else (" / ".join(segments))
   pieces.append(("Translucent " if transparent else "")+name)
  elif transparent:pieces.append("Transparent")
  else:pieces.append("Color option to be confirmed")
 return ", ".join(dict.fromkeys(pieces)) or "Please confirm available colors"
def material_en(v):
 return str(v or "").replace("硅胶","silicone").replace("包胶","overmolded grip")
def pack_en(v):
 return {"OPP袋":"OPP bag","磨砂束口袋混装":"Frosted drawstring pouch, mixed-color packing","Bag packaging (type to be confirmed)":"Bag packaging (type to be confirmed)"}.get(str(v),"Packing method to be confirmed")
def capacity_en(v,model=""):
 if model=="2506":return "To be confirmed (catalog discrepancy)"
 value=str(v).split("产品尺寸",1)[0].strip()
 cap=re.findall(r"\d+(?:\.\d+)?\s*ml",value,re.I)
 return " / ".join(dict.fromkeys(c.replace(" ","") for c in cap)) if cap else "Pending confirmation"
def model_en(value):
 return str(value).replace("透明款"," (Transparent Variant)")
def join_unique(items,field,fn=lambda x:x):
 result=[]
 for item in items:
  val=item.get(field)
  if val:
   v=fn(val)
   if v not in result:result.append(v)
 return " / ".join(result[:4]) if result else "Confirm with sales"
def details(obj):
 category=obj['category'];display=CAT[category][0];model=model_en(obj['model'])
 name=public_display_name(obj)
 variants=obj['variants']
 if str(obj['model'])=='2506':name="Plastic Sports Water Bottle — Model 2506"
 capacity=join_unique(variants,'capacity',lambda x:capacity_en(x,obj['model']))
 materials=join_unique(variants,'material',material_en)
 if obj.get('manualNew') and re.fullmatch(r'G-\d+',str(obj['model']),re.I):
  materials='Customizable plastic materials including PP, PC, PETG, Tritan, PE and ABS; request and approve component-specific specification (not stock material confirmation)'
 dims=join_unique(variants,'dimensions',lambda x: str(x)+" cm (source figure; confirm)") 
 colors=join_unique(variants,'colors',localize_colors)
 packing=join_unique(variants,'packing',pack_en)
 qty=join_unique(variants,'carton_quantity',lambda x:str(x)+" pcs/carton")
 carton=join_unique(variants,'carton_size',lambda x:str(x)+" cm (source figure)")
 source_word="Submitted" if obj.get("manualNew") else "Catalog"
 data=[
 ("Model",model),("Product Category",display),(source_word+" Capacity",capacity),
 ("Materials (buyer to confirm)" if obj.get("manualNew") else "Materials Listed in Catalog",materials),(source_word+" Dimensions",dims),
 (source_word+" Color Options",colors),("Listed Unit Packing",packing),
 ("Master Carton Quantity",qty),("Master Carton Dimensions",carton)
 ]
 photos=obj['images']
 if not photos:return ''
 img=photos[0]
 lead=("Model "+model+" is a "+display.lower()+" design offered for wholesale supply and custom branding discussions. "
       +"Buyers can request product-specific information on the lid style, materials, capacity, colors, logo decoration and shipping cartons. "
       +"The figures below come from the original product catalog and should be confirmed for the exact variant and order volume.")
 if obj.get("manualNew"):
  lead=obj["description"]+" Please confirm all product parameters and options before ordering."
 if category=="Kids Plastic Water Bottles":
  points=[
   ("School and children's product planning","Compare the cap, straw, carrying accessory and easy-clean areas to your intended age group. Compliance and age suitability depend on the selected finished product."),
   ("Parts and material review","Request body, lid, straw and gasket specifications. Children's product requirements depend on the sales market and need evidence for the exact SKU."),
   ("Branded collection options","Discuss colors and graphic placement only after checking the available model and sample.") ]
 elif category=="Large Capacity Water Jugs":
  points=[
   ("Large-volume hydration design","Review carrying balance, side handle, base stability and comfortable use when filled. Ask for the exact cap and seal configuration."),
   ("Packaging and freight","Bulkier bottles change master carton volume. Confirm carton pack, outer size and shipment terms before comparing total landed cost."),
   ("Color and private label","Colorways and logo feasibility are confirmed at model and order quantity level.") ]
 elif category=="Plastic Shaker Bottles":
  points=[
   ("Mixing assembly","Check whether the chosen SKU includes a mixing insert, measurement scale or drinking spout; photos alone do not guarantee included accessories."),
   ("Seal and cleaning review","Confirm cap threads, gaskets and accessible cleaning areas for the intended use. Do not assume dishwasher suitability."),
   ("Gym merchandise and OEM","Review artwork size, printing method, carton configuration and samples for the actual model.") ]
 else:
  points=[
   ("Everyday and sport applications","Check handling, bottle opening, spout type and practical cleaning for the intended use environment."),
   ("Closure and seal design","Different lid types have different threads and gasket locations. Request real samples before making leakproof performance claims."),
   ("Brand-ready customization","Choose compatible colors, logos and packing based on this model's tooling and decoration area.") ]
 spec=render_template("product-spec",ROWS=''.join('<tr><th scope="row">'+e(k)+'</th><td>'+e(v)+'</td></tr>' for k,v in data))
 thumbs=render_template("product-thumbnails",ITEMS=''.join('<button type="button" class="product-detail__thumb" data-main-photo="'+e(x)+'" aria-label="Show model '+e(model)+' product image '+str(i+1)+'">'+photo(x,"")+'</button>' for i,x in enumerate(photos)))
 breadcrumb='<nav class="breadcrumb" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/products/">Products</a> / <a href="/collections/'+e(CAT[category][1])+'/">'+e(display)+'</a> / '+e(model)+'</nav>'
 h=render_template("product-overview",BREADCRUMB=breadcrumb,
   MAIN_PHOTO=photo(img,name+" model "+model,"eager").replace('<img ','<img id="main-photo" ',1),
   THUMBNAILS=thumbs,MODEL=e(model),NAME=e(name),LEAD=e(lead),SPECS=spec,SLUG=e(obj["slug"]),
   PHOTO_NOTE=e("Submitted product imagery; please confirm sample appearance and final specifications." if obj.get("manualNew") else "Catalog imagery; final color and specification are confirmed with your order."))
 h+='<section class="section section--soft product-content"><div class="shell"><div class="section__head"><div><span class="eyebrow">PRODUCT DETAILS</span><h2 class="section__title">Design, Materials &amp; Applications</h2><p>Model-specific buying considerations for commercial sourcing.</p></div></div><div class="grid grid--3">'
 for title,desc in points:h+=render_template("product-benefit",HEADING=e(title),DESCRIPTION=e(desc))
 h+='</div></div></section>'
 h+='<section class="section product-ordering"><div class="shell"><div class="section__head"><div><span class="eyebrow">OEM / ODM</span><h2 class="section__title">Customization &amp; Ordering Process</h2><p>Define practical options before approving production.</p></div></div><div class="grid grid--4">'
 steps=[("01 · Choose exact SKU","Send the model number, required capacity, cap type and material or BPA-free requirements."),
 ("02 · Share brand requirements","Include logo artwork, preferred color references, printed positions, private-label packaging and target quantity."),
 ("03 · Approve a sample","Review print positioning, cap and seal operation, material evidence and packing against an agreed sample."),
 ("04 · Confirm delivery plan","Agree MOQ, actual quotation, inspection requirements, carton counts, export documents and shipment terms.")]
 for title,desc in steps:h+=render_template("product-benefit",HEADING=e(title),DESCRIPTION=e(desc))
 h+='</div><p class="product-content__cta"><a href="/capabilities/oem-odm/">Explore OEM/ODM Services →</a> · <a href="/capabilities/custom-logo/">Custom Logo Options →</a></p></div></section>'
 qs=[
 ("Can I order custom printed model "+model+"?","Logo placement, decoration process and minimum order quantity are confirmed against the actual product, artwork and order quantity."),
 ("What capacity and plastic material does this SKU use?",("The submitted product details list " if obj.get("manualNew") else "The catalog reference lists ")+capacity+" capacity and "+materials+" materials. Request component-level verification and market-specific food-contact documents before confirming your order."),
 ("Is this bottle BPA-free and leakproof?","BPA-free material options or leak testing can be requested. Neither claim is guaranteed for every variant; confirm test evidence, cap design and intended usage conditions."),
 ("How do I request a sample and shipping quote?","Send the model, target quantity, destination, logo details and pack type. The team will confirm availability, sample costs and appropriate trade terms.")
 ]
 h+='<section class="section section--soft"><div class="shell"><div class="section__head"><div><span class="eyebrow">MODEL FAQ</span><h2 class="section__title">Frequently Asked Questions</h2></div></div><div class="faq-list">'
 for question,answer in qs:h+='<details><summary>'+e(question)+'</summary><p>'+e(answer)+'</p></details>'
 h+='</div></div></section>'
 similar=[x for x in SERIES.values() if x["category"]==category and x["model"]!=obj['model']][:4]
 if similar:h+='<section class="section"><div class="shell"><div class="section__head"><div><span class="eyebrow">PRODUCT RANGE</span><h2 class="section__title">Related Bottle Models</h2></div></div>'+product_grid(similar)+'</div></section>'
 return h
def add_schema(html,obj):
 from product_share_source import real_product_images
 model=model_en(obj["model"])
 title=public_display_name(obj)
 site=SITE_ORIGIN+"/products/"+obj['slug']+"/"
 product={
  "@type":"Product","name":title,"sku":model,"description":"Wholesale "+title+". Confirm model materials, capacity, colors, logo options and packaging with XUYI before ordering.",
  "brand":{"@type":"Brand","name":"XUYI Bottles"},
  "category":CAT[obj['category']][0],
  "url":site,
  "additionalProperty":[{"@type":"PropertyValue","name":"Material (catalog reference)","value":join_unique(obj['variants'],'material',material_en)},
                        {"@type":"PropertyValue","name":"Capacity (catalog reference)","value":join_unique(obj['variants'],'capacity',lambda x:capacity_en(x,obj['model']))}]
 }
 authentic=real_product_images(obj)
 if authentic:product["image"]=[SITE_ORIGIN+src for src in authentic]
 breadcrumb={"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":SITE_ORIGIN+"/"},{"@type":"ListItem","position":2,"name":"Products","item":SITE_ORIGIN+"/products/"},{"@type":"ListItem","position":3,"name":model,"item":site}]}
 graph={"@context":"https://schema.org","@graph":[product,breadcrumb]}
 fragment='<script type="application/ld+json">'+json.dumps(graph,ensure_ascii=False).replace("</","<\\/")+'</script>'
 return html.replace("</head>",fragment+"</head>",1)