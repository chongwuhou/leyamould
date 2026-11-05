import {authorizedProductSeoPromotionRequest} from "../../_shared/build-auth.js";
import {bumpPublishRevision} from "../../_shared/site-settings.js";

const reply=(value,status=200)=>Response.json(value,{status,headers:{
  "cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"
}});

const LOCALES=["es","pt","ru","tr"];
const COLLECTIONS={
  "/collections/kids-water-bottles/":{
    oldTitle:"Kids Water Bottles Wholesale | XUYI Bottles",
    oldMeta:"Explore XUYI plastic kids water bottles with different straw lids, handles and colors. Compare models and confirm samples, artwork and ordering details before buying.",
    seoTitle:"Kids Plastic Water Bottles Wholesale OEM | XUYI",
    seoDescription:"B2B kids plastic water bottles with straw and carry-strap options. Ask the XUYI OEM factory about custom plastic materials, colors, logos and bulk packing.",
    h1:{
      en:"B2B Kids Plastic Water Bottles Manufacturer — OEM Factory",
      es:"Fabricante B2B de botellas infantiles de plástico — Fábrica OEM",
      pt:"Fabricante B2B de garrafas infantis de plástico — Fábrica OEM",
      ru:"B2B-производитель детских пластиковых бутылок — OEM-завод",
      tr:"B2B çocuk plastik mataraları üreticisi — OEM fabrika"
    },
    intro:{
      en:"Wholesale kids plastic water bottles with straw, carry-strap and color options for private label, school and promotional programs. Custom plastic materials, logo and packing can be reviewed by model.",
      es:"Botellas infantiles de plástico al por mayor con pajita, correa y opciones de color para marca privada, colegios y promociones. Los materiales plásticos, el logo y el embalaje se revisan por modelo.",
      pt:"Garrafas infantis de plástico para atacado com palhinha, alça e opções de cor para marca própria, escolas e promoções. Materiais plásticos, logo e embalagem podem ser avaliados por modelo.",
      ru:"Детские пластиковые бутылки оптом с трубочкой, ремешком и вариантами цвета для private label, школ и промо-программ. Полимеры, логотип и упаковка согласуются по модели.",
      tr:"Özel marka, okul ve promosyon programları için pipetli, askılı ve renk seçenekli toptan çocuk plastik mataraları. Özel plastik malzeme, logo ve koli seçenekleri modele göre görüşülür."
    }
  },
  "/collections/large-capacity-water-jugs/":{
    oldTitle:"Large Capacity Water Jugs Wholesale | XUYI Bottles",
    oldMeta:"Browse larger-capacity XUYI plastic water jugs for sports, travel and daily use. Compare capacities, handles and lids, then confirm the model and packing options.",
    seoTitle:"Large-Capacity Plastic Water Jugs Wholesale OEM | XUYI",
    seoDescription:"B2B large-capacity plastic water jugs for fitness and outdoor buyers. Confirm factory ml, approximate oz size class, materials, colors, lids, logos and packing by model.",
    h1:{
      en:"B2B Large-Capacity Plastic Water Jugs Manufacturer — OEM Factory",
      es:"Fabricante B2B de jarras de agua grandes de plástico — Fábrica OEM",
      pt:"Fabricante B2B de jarras de água grandes de plástico — Fábrica OEM",
      ru:"B2B-производитель пластиковых бутылок большого объёма — OEM-завод",
      tr:"B2B büyük hacimli plastik su mataraları üreticisi — OEM fabrika"
    },
    intro:{
      en:"Large-capacity plastic water jugs for fitness, outdoor, team and promotional buyers. Confirm each model’s factory ml capacity, approximate oz size class, colors, handle, lid, custom plastic material and bulk packing.",
      es:"Jarras de agua grandes de plástico para fitness, exterior, equipos y promociones. Confirme por modelo la capacidad de fábrica en ml, la clase oz aproximada, los colores, el asa, la tapa, el plástico a medida y el embalaje.",
      pt:"Jarras de água grandes de plástico para fitness, exterior, equipas e promoções. Confirme por modelo a capacidade de fábrica em ml, a classe oz aproximada, cores, asa, tampa, plástico sob medida e embalagem.",
      ru:"Пластиковые бутылки большого объёма для фитнеса, улицы, команд и промо-заказов. По каждой модели уточняйте заводской объём в мл, примерный класс oz, цвет, ручку, крышку, полимер и упаковку.",
      tr:"Fitness, outdoor, takım ve promosyon alıcıları için büyük hacimli plastik su mataraları. Her modelin fabrika ml kapasitesini, yaklaşık oz sınıfını, renk, tutamak, kapak, özel plastik ve koli seçeneklerini doğrulayın."
    }
  },
  "/collections/plastic-shaker-bottles/":{
    oldTitle:"Protein Shaker Bottles Wholesale | XUYI Bottles",
    oldMeta:"Compare XUYI plastic protein shaker bottles for fitness and sports nutrition. Review each model's lid, cup shape and components; ask about samples and branding options.",
    seoTitle:"Plastic Shaker Bottles Wholesale OEM Factory | XUYI",
    seoDescription:"B2B plastic shaker bottles for gym, protein and fitness programs. Confirm ml capacity, approximate oz class, mixing components, custom plastic, logo and bulk packing by model.",
    h1:{
      en:"B2B Plastic Shaker Bottles Manufacturer — OEM Factory",
      es:"Fabricante B2B de botellas shaker de plástico — Fábrica OEM",
      pt:"Fabricante B2B de coqueteleiras de plástico — Fábrica OEM",
      ru:"B2B-производитель пластиковых шейкеров — OEM-завод",
      tr:"B2B plastik shaker şişesi üreticisi — OEM fabrika"
    },
    intro:{
      en:"Wholesale plastic shaker bottles for gym, protein, fitness and sports-nutrition programs. Review factory ml capacity, approximate oz size class, mixing components, custom plastic material, logo, colors and packing by model.",
      es:"Botellas shaker de plástico al por mayor para gimnasio, proteína, fitness y nutrición deportiva. Revise por modelo la capacidad ml, la clase oz aproximada, los componentes de mezcla, el plástico a medida, el logo, los colores y el embalaje.",
      pt:"Coqueteleiras de plástico para atacado destinadas a ginásio, proteína, fitness e nutrição desportiva. Avalie por modelo a capacidade ml, a classe oz aproximada, os componentes, o plástico sob medida, logo, cores e embalagem.",
      ru:"Пластиковые шейкеры оптом для залов, протеиновых, фитнес- и спортивных программ. По модели проверьте объём в мл, примерный класс oz, компоненты, полимер, логотип, цвет и упаковку.",
      tr:"Spor salonu, protein, fitness ve spor beslenme programları için toptan plastik shaker şişeleri. Model bazında ml kapasitesini, yaklaşık oz sınıfını, karıştırma bileşenlerini, özel plastiği, logoyu, renkleri ve koliyi inceleyin."
    }
  },
  "/collections/sports-water-bottles/":{
    oldTitle:"Wholesale Sports Water Bottles & Custom OEM | XUYI",
    oldMeta:"Source wholesale plastic sports water bottles from XUYI. Compare bottle capacity, lids and designs, then request custom logo options, samples and an OEM quotation.",
    seoTitle:"Plastic Sports Water Bottles Wholesale OEM | XUYI",
    seoDescription:"B2B plastic sports water bottles for active and promotional collections. Confirm factory ml, approximate oz class, materials, colors, lid components, logo and packing by model.",
    h1:{
      en:"B2B Plastic Sports Water Bottles Manufacturer — OEM Factory",
      es:"Fabricante B2B de botellas deportivas de plástico — Fábrica OEM",
      pt:"Fabricante B2B de garrafas esportivas de plástico — Fábrica OEM",
      ru:"B2B-производитель пластиковых спортивных бутылок — OEM-завод",
      tr:"B2B plastik spor mataraları üreticisi — OEM fabrika"
    },
    intro:{
      en:"Wholesale plastic sports water bottles for active, outdoor and promotional collections. Confirm factory ml capacity, approximate oz size class, source-confirmed material, colors, logo, lid components and bulk packing by model.",
      es:"Botellas deportivas de plástico al por mayor para colecciones activas, exteriores y promocionales. Confirme por modelo la capacidad ml, la clase oz aproximada, el material de origen, los colores, el logo, la tapa y el embalaje.",
      pt:"Garrafas esportivas de plástico para atacado em coleções ativas, outdoor e promocionais. Confirme por modelo a capacidade ml, a classe oz aproximada, o material de origem, cores, logo, tampa e embalagem.",
      ru:"Пластиковые спортивные бутылки оптом для активных, outdoor- и промо-коллекций. По модели уточняйте заводской объём в мл, примерный класс oz, материал, цвет, логотип, крышку и упаковку.",
      tr:"Aktif yaşam, outdoor ve promosyon koleksiyonları için toptan plastik spor mataraları. Model bazında fabrika ml kapasitesini, yaklaşık oz sınıfını, kaynağı doğrulanmış malzemeyi, renkleri, logoyu, kapağı ve koliyi onaylayın."
    }
  },
  "/collections/spray-water-bottles/":{
    oldTitle:"Spray Water Bottles Wholesale | XUYI Bottles",
    oldMeta:"Spray water bottles for promotional, outdoor and everyday drinkware projects. Confirm nozzle, trigger and materials by model.",
    seoTitle:"Spray Water Bottles Wholesale OEM Factory | XUYI",
    seoDescription:"B2B spray water bottles for outdoor, cooling and promotional programs. Confirm factory ml, approximate oz class, nozzle, custom plastic, colors, logo and packing by model.",
    h1:{
      en:"B2B Spray Water Bottles Manufacturer — OEM Factory",
      es:"Fabricante B2B de botellas de agua con pulverizador — Fábrica OEM",
      pt:"Fabricante B2B de garrafas com borrifador — Fábrica OEM",
      ru:"B2B-производитель бутылок с распылителем — OEM-завод",
      tr:"B2B spreyli su matarası üreticisi — OEM fabrika"
    },
    intro:{
      en:"Wholesale spray water bottles for outdoor, cooling, promotional and retail programs. Confirm factory ml capacity, approximate oz size class, nozzle, trigger, custom plastic material, colors, logo and packing by model.",
      es:"Botellas con pulverizador al por mayor para exterior, refrigeración, promociones y retail. Confirme por modelo la capacidad ml, la clase oz aproximada, la boquilla, el gatillo, el plástico a medida, los colores, el logo y el embalaje.",
      pt:"Garrafas com borrifador para atacado em programas outdoor, de arrefecimento, promocionais e retail. Confirme por modelo a capacidade ml, a classe oz aproximada, bico, gatilho, plástico sob medida, cores, logo e embalagem.",
      ru:"Бутылки с распылителем оптом для улицы, охлаждения, промо и розницы. По модели уточняйте объём в мл, примерный класс oz, распылитель, курок, полимер, цвет, логотип и упаковку.",
      tr:"Outdoor, serinletme, promosyon ve perakende programları için toptan spreyli su mataraları. Model bazında ml kapasitesini, yaklaşık oz sınıfını, nozulu, tetiği, özel plastiği, renkleri, logoyu ve koliyi doğrulayın."
    }
  },
  "/collections/two-way-drinking-cups/":{
    oldTitle:"Two-Way Drinking Cups Wholesale | XUYI Bottles",
    oldMeta:"Dual-mode drinking cups for travel, retail and promotional collections. Confirm lid components and materials by exact model.",
    seoTitle:"Dual-Mode Two-Way Drinking Cups Wholesale OEM | XUYI",
    seoDescription:"B2B dual-mode two-way drinking cups for travel, retail and promotional collections. Review model-specific ml capacity and approximate oz class, lid seal design, custom plastic materials, colors, logo and bulk packing.",
    h1:{
      en:"B2B Dual-Mode Two-Way Drinking Cups Manufacturer — OEM Factory",
      es:"Fabricante B2B de vasos de doble modo — Fábrica OEM",
      pt:"Fabricante B2B de copos de dupla função — Fábrica OEM",
      ru:"B2B-производитель кружек с двумя способами питья — OEM-завод",
      tr:"B2B iki içim seçenekli bardak üreticisi — OEM fabrika"
    },
    intro:{
      en:"Wholesale dual-mode two-way drinking cups for travel, retail and promotional collections. Review model-specific ml capacity and approximate oz class, lid seal design, custom plastic materials, colors, logo and bulk packing.",
      es:"Vasos de doble modo al por mayor para viaje, retail y promociones. Revise por modelo la capacidad ml y la clase oz aproximada, el sellado de la tapa, los plásticos a medida, los colores, el logo y el embalaje.",
      pt:"Copos de dupla função para atacado em viagens, retail e promoções. Avalie por modelo a capacidade ml e a classe oz aproximada, a vedação da tampa, os plásticos sob medida, cores, logo e embalagem.",
      ru:"Кружки с двумя способами питья оптом для путешествий, розницы и промо. По модели проверьте объём в мл и примерный класс oz, уплотнение крышки, полимеры, цвет, логотип и упаковку.",
      tr:"Seyahat, perakende ve promosyon koleksiyonları için toptan iki içim seçenekli bardaklar. Model bazında ml kapasitesini ve yaklaşık oz sınıfını, kapak conta tasarımını, özel plastikleri, renkleri, logoyu ve koliyi inceleyin."
    }
  },
  "/collections/titanium-vacuum-cups/":{
    oldTitle:"Titanium Vacuum Cups Wholesale | XUYI Bottles",
    oldMeta:"Titanium vacuum cups for insulated drinkware sourcing. Verify grade, purity, vacuum construction and test documents for each SKU.",
    seoTitle:"Titanium Vacuum Cups Wholesale OEM Factory | XUYI",
    seoDescription:"B2B titanium vacuum cups for insulated drinkware sourcing. Confirm factory ml capacity, approximate oz class, titanium grade, lid and seal materials, finish, logo and test documents by SKU.",
    h1:{
      en:"B2B Titanium Vacuum Cups Manufacturer — OEM Factory",
      es:"Fabricante B2B de vasos térmicos al vacío de titanio — Fábrica OEM",
      pt:"Fabricante B2B de copos térmicos a vácuo de titânio — Fábrica OEM",
      ru:"B2B-производитель вакуумных термокружек из титана — OEM-завод",
      tr:"B2B titanyum vakumlu termos bardak üreticisi — OEM fabrika"
    },
    intro:{
      en:"Wholesale titanium vacuum cups for insulated drinkware sourcing. Confirm factory ml capacity, approximate oz class, titanium grade, lid and seal materials, finish, logo and test documents by SKU.",
      es:"Vasos térmicos al vacío de titanio al por mayor. Confirme por SKU la capacidad ml, la clase oz aproximada, el grado de titanio, los materiales de tapa y junta, el acabado, el logo y los documentos de prueba.",
      pt:"Copos térmicos a vácuo de titânio para atacado. Confirme por SKU a capacidade ml, a classe oz aproximada, o grau de titânio, materiais da tampa e vedação, acabamento, logo e documentos de teste.",
      ru:"Титановые вакуумные термокружки оптом для закупки теплоизолированной посуды. По SKU уточняйте объём в мл, примерный класс oz, марку титана, материалы крышки и уплотнителя, отделку, логотип и документы.",
      tr:"Yalıtımlı içecek ürünleri tedariki için toptan titanyum vakumlu termos bardaklar. SKU bazında ml kapasitesini, yaklaşık oz sınıfını, titanyum kalitesini, kapak ve conta malzemelerini, yüzeyi, logoyu ve test belgelerini doğrulayın."
    }
  }
};


const LEGACY_TRANSLATIONS={
  "/collections/kids-water-bottles/":{
    es:{title:"Botellas de agua para niños al por mayor | Botellas XUYI",h1:"Botellas de agua para niños"},
    pt:{title:"Garrafas de água infantis no atacado | Garrafas XUYI",h1:"Garrafas de água infantis"},
    ru:{title:"Детские бутылки для воды оптом | Бутылки XUYI",h1:"Детские бутылки для воды"},
    tr:{title:"Çocuk Su Şişeleri Toptan Satış | XUYI Şişeler",h1:"Çocuk Su Şişeleri"}
  },
  "/collections/large-capacity-water-jugs/":{
    es:{title:"Jarras de agua de gran capacidad al por mayor | Botellas XUYI",h1:"Jarras de agua de gran capacidad"},
    pt:{title:"Jarros de água de grande capacidade atacado | Garrafas XUYI",h1:"Jarros de água de grande capacidade"},
    ru:{title:"Кувшины для воды большой емкости оптом | Бутылки XUYI",h1:"Большая емкость для воды Кувшины"},
    tr:{title:"Büyük Kapasiteli Su Sürahileri Toptan Satış | XUYI Şişeler",h1:"Büyük Kapasiteli Su Sürahileri"}
  },
  "/collections/plastic-shaker-bottles/":{
    es:{title:"Botellas mezcladoras de proteínas al por mayor | Botellas XUYI",h1:"Botellas mezcladoras de proteínas"},
    pt:{title:"Garrafas para shaker de proteína no atacado | Garrafas XUYI",h1:"Garrafas Shaker de Proteína"},
    ru:{title:"Бутылки для протеиновых шейкеров оптом | Бутылки XUYI",h1:"Бутылочки для протеинового шейкера"},
    tr:{title:"Protein Çalkalayıcı Şişeleri Toptan Satış | XUYI Şişeler",h1:"Protein Çalkalayıcı Şişeleri"}
  }
};

function normalizeLocalizedLinks(value,locale){
  if(locale==="en")return String(value);
  return String(value)
    .replace(/href="\/products\//g,'href="/'+locale+'/products/')
    .replace(/href="\/collections\//g,'href="/'+locale+'/collections/');
}
function dedupeProductCards(value){
  const seen=new Set();
  return String(value).replace(/<a\b[^>]*\bdata-product-card\b[^>]*>[\s\S]*?<\/a>/gi,card=>{
    const match=card.match(/\bhref="([^"]+)"/i);
    if(!match)return card;
    const href=match[1];
    if(seen.has(href))return "";
    seen.add(href);
    return card;
  });
}
function escapeHtml(value){
  return String(value).replace(/[&<>"']/g,character=>({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
  }[character]));
}
function localizedBody(sourceHtml,entry,locale){
  let html=String(sourceHtml);
  const h1=escapeHtml(entry.h1[locale]||entry.h1.en);
  const intro=escapeHtml(entry.intro[locale]||entry.intro.en);
  const h1Pattern=/<h1\b[^>]*>[\s\S]*?<\/h1>/i;
  if(h1Pattern.test(html)){
    html=html.replace(h1Pattern,match=>match.replace(/>[\s\S]*?<\/h1>/i,">"+h1+"</h1>"));
  }else{
    html="<h1>"+h1+"</h1>"+html;
  }
  const end=html.search(/<\/h1>/i);
  if(end>=0){
    const before=html.slice(0,end+5);
    const after=html.slice(end+5);
    const paragraph=after.match(/<p\b[^>]*>[\s\S]*?<\/p>/i);
    if(paragraph){
      const start=after.indexOf(paragraph[0]);
      const replacement=paragraph[0].replace(/>[\s\S]*?<\/p>/i,">"+intro+"</p>");
      html=before+after.slice(0,start)+replacement+after.slice(start+paragraph[0].length);
    }else{
      html=before+"<p class=\"collection-intro\">"+intro+"</p>"+after;
    }
  }
  return html;
}
async function prepare(c){
  if(!await authorizedProductSeoPromotionRequest(c.request,c.env))
    return {error:reply({error:"Unauthorized"},401)};
  if(!c.env.XUYI_DB)return {error:reply({error:"Missing XUYI D1 binding"},503)};
  return {db:c.env.XUYI_DB};
}

export async function onRequestGet(c){
  const {db,error}=await prepare(c);if(error)return error;
  const translations=(await db.prepare(
    "SELECT resource_id,locale FROM xuyi_translation_overrides WHERE resource_id LIKE 'page:/collections/%'"
  ).all()).results||[];
  const bodies=(await db.prepare(
    "SELECT route FROM xuyi_page_content WHERE route LIKE '/collections/%'"
  ).all()).results||[];
  return reply({
    routes:Object.keys(COLLECTIONS).length,
    englishBodies:bodies.length,
    localizedRows:translations.length,
    expectedMissingLocalized:Object.keys(COLLECTIONS).length*LOCALES.length-translations.length
  });
}
export async function onRequestPost(c){
  const {db,error}=await prepare(c);if(error)return error;
  let input;try{input=await c.request.json()}catch{return reply({error:"Invalid JSON"},400)};
  if(input?.action!=="seed"||typeof input.route!=="string"||
     !COLLECTIONS[input.route]||typeof input.sourceHtml!=="string"||
     input.sourceHtml.length<500||input.sourceHtml.length>250000)
    return reply({error:"Invalid fixed collection seed"},400);

  const route=input.route;
  const entry=COLLECTIONS[route];
  const sourceHtml=input.sourceHtml;
  const routeWithoutSlash=route.endsWith("/")?route.slice(0,-1):route;
  const currentPage=await db.prepare(
    "SELECT route,seo_title,meta_description FROM site_pages WHERE route IN (?,?) ORDER BY CASE WHEN route=? THEN 0 ELSE 1 END LIMIT 1"
  ).bind(route,routeWithoutSlash,route).first();
  const currentBody=await db.prepare(
    "SELECT route FROM xuyi_page_content WHERE route=?"
  ).bind(route).first();
  const currentLocales=(await db.prepare(
    "SELECT locale,translated_json FROM xuyi_translation_overrides WHERE resource_id=?"
  ).bind("page:"+route).all()).results||[];
  const localeSet=new Set(currentLocales.map(row=>row.locale));
  const queries=[];
  let updatedPageFields=0;
  if(!currentPage){
    queries.push(db.prepare(
      "INSERT INTO site_pages(route,label,seo_title,meta_description,updated_at) "+
      "SELECT ?,?,?,?,CURRENT_TIMESTAMP WHERE NOT EXISTS (SELECT 1 FROM site_pages WHERE route IN (?,?))"
    ).bind(route,entry.h1.en,entry.seoTitle,entry.seoDescription,route,routeWithoutSlash));
    updatedPageFields+=2;
  }else{
    if(currentPage.seo_title===entry.oldTitle){
      queries.push(db.prepare(
        "UPDATE site_pages SET seo_title=?,updated_at=CURRENT_TIMESTAMP WHERE route=? AND seo_title=?"
      ).bind(entry.seoTitle,currentPage.route,entry.oldTitle));
      updatedPageFields++;
    }
    if(currentPage.meta_description===entry.oldMeta){
      queries.push(db.prepare(
        "UPDATE site_pages SET meta_description=?,updated_at=CURRENT_TIMESTAMP WHERE route=? AND meta_description=?"
      ).bind(entry.seoDescription,currentPage.route,entry.oldMeta));
      updatedPageFields++;
    }
  }
  if(!currentBody){
    queries.push(db.prepare(
      "INSERT INTO xuyi_page_content(route,main_html,publication_status,updated_at) VALUES(?,?,?,CURRENT_TIMESTAMP) ON CONFLICT(route) DO NOTHING"
    ).bind(route,localizedBody(sourceHtml,entry,"en"),"published"));
  }
  let insertedLocales=0;
  let updatedLocales=0;
  for(const locale of LOCALES){
    const title={
      es:entry.h1.es+" | XUYI",
      pt:entry.h1.pt+" | XUYI",
      ru:entry.h1.ru+" | XUYI",
      tr:entry.h1.tr+" | XUYI"
    }[locale];
    const description=entry.intro[locale];
    const existing=currentLocales.find(row=>row.locale===locale);
    if(existing){
      const legacy=LEGACY_TRANSLATIONS[route]?.[locale];
      let payload=null;
      try{payload=JSON.parse(existing.translated_json||"{}");}catch{}
      const existingBody=typeof payload?.mainHtml==="string"?payload.mainHtml:"";
      const repairedBody=dedupeProductCards(normalizeLocalizedLinks(existingBody,locale));
      const bodyNeedsRepair=repairedBody!==existingBody;
      const isLegacy=Boolean(legacy&&(
        payload?.title===legacy.title||
        (typeof payload?.mainHtml==="string"&&payload.mainHtml.includes(legacy.h1))||
        bodyNeedsRepair
      ));
      if(isLegacy){
        const nextPayload={...(payload||{}),title,description,mainHtml:localizedBody(repairedBody||sourceHtml,entry,locale)};
        queries.push(db.prepare(
          "UPDATE xuyi_translation_overrides SET translated_json=?,reviewed_at=CURRENT_TIMESTAMP WHERE resource_id=? AND locale=? AND translated_json=?"
        ).bind(JSON.stringify(nextPayload),"page:"+route,locale,existing.translated_json));
        updatedLocales++;
      }
      continue;
    }
    queries.push(db.prepare(
      "INSERT INTO xuyi_translation_overrides(resource_id,locale,translated_json,reviewed_at) VALUES(?,?,?,CURRENT_TIMESTAMP) ON CONFLICT(resource_id,locale) DO NOTHING"
    ).bind("page:"+route,locale,JSON.stringify({
      title,description,mainHtml:localizedBody(sourceHtml,entry,locale)
    })));
    insertedLocales++;
  }
  if(queries.length){
    await db.batch(queries);
    const revision=await bumpPublishRevision(db);
    return reply({route,updatedPageFields,insertedEnglishBody:currentBody?0:1,insertedLocales,updatedLocales,...revision});
  }
  return reply({route,updatedPageFields,insertedEnglishBody:0,insertedLocales:0,updatedLocales:0,unchanged:true});
}
