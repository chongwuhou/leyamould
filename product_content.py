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

def factory_model_code(obj):
 value=obj.get("factoryModel")
 if isinstance(value,str) and value.strip():return value.strip()
 return str(obj.get("model") or "").strip()
def join_unique(items,field,fn=lambda x:x):
 result=[]
 for item in items:
  val=item.get(field)
  if val:
   v=fn(val)
   if v not in result:result.append(v)
 return " / ".join(result[:4]) if result else "Confirm with sales"
_FACTORY_SEO_TYPES = {
 "Plastic Shaker Bottles":"Sports Shaker Bottle",
 "Plastic Sports Water Bottles":"Sports Water Bottle",
 "Large Capacity Water Jugs":"Large Sports Bottle",
 "Spray Water Bottles":"Spray Water Bottle",
 "Two-Way Drinking Cups":"Two-Way Drinking Cup",
 "Titanium Vacuum Cups":"Titanium Vacuum Cup",
}
def factory_catalog_seo_title(obj):
 if not (obj.get("sourceDocument") and obj.get("sourcePage")):
  return str(obj.get("seoTitle") or "")
 capacity=str(obj.get("capacity") or "")
 tokens=re.findall(r"(\d+(?:\.\d+)?)\s*(ml|l|oz)\b",capacity,re.I)
 if tokens:
  units={unit.lower() for _,unit in tokens}
  if len(units)==1:
   unit=next(iter(units))
   capacity_label="/".join(value for value,_ in tokens)+unit
  else:
   capacity_label="/".join(value+unit.lower() for value,unit in tokens)
 else:
  capacity_label="/".join(re.findall(r"\d+(?:\.\d+)?",capacity))
 kind=_FACTORY_SEO_TYPES.get(str(obj.get("category") or ""),"Drinkware")
 model=factory_model_code(obj).upper()
 prefix=" ".join(part for part in (capacity_label,kind) if part)
 title=" | ".join(part for part in (prefix,model,"XUYI") if part)
 if len(title)>60:
  title=" | ".join(part for part in (capacity_label,model,"XUYI") if part)
 if len(title)>60:
  title=" | ".join(part for part in (model,"XUYI") if part)
 if len(title)>60:
  raise ValueError("Factory catalog SEO title exceeds 60 characters: "+model)
 return title
def details(obj):
 category=obj['category'];display=CAT[category][0]
 manual_new=bool(obj.get("manualNew"))
 factory_catalog=manual_new and bool(obj.get("sourceDocument")) and bool(obj.get("sourcePage"))
 model=model_en(factory_model_code(obj))
 name=public_display_name(obj)
 if manual_new:name=name+" — Model "+model
 variants=obj['variants']
 if str(obj['model'])=='2506':name="Plastic Sports Water Bottle — Model 2506"
 capacity=join_unique(variants,'capacity',lambda x:str(x) if manual_new else capacity_en(x,obj['model']))
 materials=join_unique(variants,'material',material_en)
 if obj.get('manualNew') and re.fullmatch(r'G-\d+',str(obj['model']),re.I):
  materials='Customizable plastic materials including PP, PC, PETG, Tritan, PE and ABS; request and approve component-specific specification (not stock material confirmation)'
 def dimension_value(value):
  text=str(value).strip()
  if manual_new and not re.fullmatch(r'[\d.\s*×xX/+-]+',text):return text
  return text+" cm (source figure; confirm)"
 dims=join_unique(variants,'dimensions',dimension_value)
 colors=join_unique(variants,'colors',localize_colors)
 packing=join_unique(variants,'packing',lambda x:str(x) if manual_new else pack_en(x))
 qty=join_unique(variants,'carton_quantity',lambda x:str(x)+" pcs/carton")
 carton=join_unique(variants,'carton_size',dimension_value)
 source_word="Factory Catalog" if factory_catalog else ("Submitted" if manual_new else "Catalog")
 data=[
 ("Model",model),("Product Category",display),(source_word+" Capacity",capacity),
 ("Materials (confirm by exact SKU)" if manual_new else "Materials Listed in Catalog",materials),(source_word+" Dimensions",dims),
 (source_word+" Color Options",colors),("Listed Unit Packing",packing),
 ("Master Carton Quantity",qty),("Master Carton Dimensions",carton)
 ]
 if factory_catalog:
  optional=[("Listed Unit Weight",join_unique(variants,'unit_weight',lambda x:str(x))),
   ("Listed Temperature Range",join_unique(variants,'temperature_range',lambda x:str(x))),
   ("Retail Box Dimensions",join_unique(variants,'retail_box_size',dimension_value)),
   ("Master Carton Gross Weight",join_unique(variants,'carton_gross_weight',lambda x:str(x))),
   ("Printed Ounce Label (catalog notation)",join_unique(variants,'catalogOunceLabel',lambda x:str(x))),
   ("Factory Catalog Source",join_unique(variants,'sourceDocument',lambda x:str(x))),
   ("Factory Catalog Page",join_unique(variants,'sourcePage',lambda x:"Page "+str(x))),
   ("Catalog Notes",join_unique(variants,'sourceNotes',lambda x:str(x)))]
  data.extend((label,value) for label,value in optional if value and value!="Confirm with sales")
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
 elif category=="Spray Water Bottles":
  points=[("Spray head and trigger","Confirm the nozzle, trigger action, spray pattern and included components for the exact model."),("Leakage and cleaning review","Check the cap seal, internal tube and cleaning access. Do not assume leakproof performance without sample testing."),("Branding and packing","Confirm decoration area, spare parts, carton quantity and retail packaging before quotation.")]
 elif category=="Two-Way Drinking Cups":
  points=[("Dual drinking modes","Verify both drinking options and the exact lid assembly shown for the selected model."),("Seal and cleaning review","Check seals, removable components and cleaning access; request a sample before making leak-resistance claims."),("Material and performance evidence","Confirm the exact body, lid and insulation materials and any temperature-performance documents for the SKU.")]
 elif category=="Titanium Vacuum Cups":
  points=[("Titanium grade and purity","Request material-grade and composition documents for the exact SKU; do not rely on a series-level purity statement alone."),("Vacuum insulation verification","Confirm the vacuum structure, capacity and thermal test method for the selected model."),("Surface finish and packaging","Review finish, lid components, protective packing and carton details against an approved sample.")]
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
    PHOTO_NOTE=e(
      "Factory catalog family image shared by related variants; it does not confirm the exact SKU appearance. Confirm the selected model, capacity and sample before ordering."
      if factory_catalog and obj.get("imageReviewStatus") == "visually_reviewed_source_family_image"
      else ("Factory catalog image; confirm the exact variant and sample appearance before ordering."
            if factory_catalog else
            ("Submitted product imagery; please confirm sample appearance and final specifications."
             if manual_new else
             "Catalog imagery; final color and specification are confirmed with your order."))))
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
  ("What capacity and material does this SKU use?",("The factory catalog lists " if factory_catalog else ("The submitted product details list " if manual_new else "The catalog reference lists "))+capacity+" capacity and "+materials+" materials. Request component-level verification and market-specific food-contact documents before confirming your order."),
 ("Is this product BPA-free and leakproof?","BPA-free material options or leak testing can be requested. Neither claim is guaranteed for every variant; confirm test evidence, cap design and intended usage conditions."),
 ("How do I request a sample and shipping quote?","Send the model, target quantity, destination, logo details and pack type. The team will confirm availability, sample costs and appropriate trade terms.")
 ]
 h+='<section class="section section--soft"><div class="shell"><div class="section__head"><div><span class="eyebrow">MODEL FAQ</span><h2 class="section__title">Frequently Asked Questions</h2></div></div><div class="faq-list">'
 for question,answer in qs:h+='<details><summary>'+e(question)+'</summary><p>'+e(answer)+'</p></details>'
 h+='</div></div></section>'
 similar=[x for x in SERIES.values() if x["category"]==category and x["model"]!=obj['model']][:4]
 if similar:h+='<section class="section"><div class="shell"><div class="section__head"><div><span class="eyebrow">PRODUCT RANGE</span><h2 class="section__title">Related Drinkware Models</h2></div></div>'+product_grid(similar)+'</div></section>'
 from scripts.source_catalog_capacity_oz import source_body_enrichment
 return source_body_enrichment(h,"en",obj)

def add_schema(html,obj):
 from product_share_source import real_product_images
 model=model_en(factory_model_code(obj))
 title=public_display_name(obj)
 if obj.get("manualNew"):title=title+" — Model "+model
 site=SITE_ORIGIN+"/products/"+obj['slug']+"/"
 product={
  "@type":"Product","name":title,"sku":model,"description":obj.get("seoDescription") or ("Wholesale "+title+". Confirm model materials, capacity, colors, logo options and packaging with XUYI before ordering."),
  "brand":{"@type":"Brand","name":"XUYI Bottles"},
  "category":CAT[obj['category']][0],
  "url":site,
  "additionalProperty":[{"@type":"PropertyValue","name":"Material (catalog reference)","value":join_unique(obj['variants'],'material',material_en)},
                        {"@type":"PropertyValue","name":"Capacity (catalog reference)","value":join_unique(obj['variants'],'capacity',lambda x:str(x) if obj.get("manualNew") else capacity_en(x,obj['model']))}]
 }
 authentic=real_product_images(obj)
 if authentic:product["image"]=[SITE_ORIGIN+src for src in authentic]
 breadcrumb={"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":SITE_ORIGIN+"/"},{"@type":"ListItem","position":2,"name":"Products","item":SITE_ORIGIN+"/products/"},{"@type":"ListItem","position":3,"name":model,"item":site}]}
 graph={"@context":"https://schema.org","@graph":[product,breadcrumb]}
 fragment='<script type="application/ld+json">'+json.dumps(graph,ensure_ascii=False).replace("</","<\\/")+'</script>'
 return html.replace("</head>",fragment+"</head>",1)