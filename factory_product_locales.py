"""Source-reviewed native-language product pages for new factory models.

D1 translations remain authoritative. This module supplies a deterministic,
model-specific source translation only when no reviewed D1 page translation
exists. It never changes factory facts or claims unverified certifications.
"""
from __future__ import annotations

from html import escape
import re

SOURCE_DOCUMENTS = {"puyunsm(1).pdf", "水杯最新产品.pptx"}

CATEGORY = {
    "Plastic Shaker Bottles": {"en":"Sports Shaker Bottle","es":"Vaso mezclador deportivo","pt":"Coqueteleira esportiva","ru":"Спортивный шейкер","tr":"Sporcu shaker şişesi"},
    "Plastic Sports Water Bottles": {"en":"Plastic Sports Water Bottle","es":"Botella deportiva de plástico","pt":"Garrafa esportiva de plástico","ru":"Пластиковая спортивная бутылка","tr":"Plastik spor matarası"},
    "Large Capacity Water Jugs": {"en":"Large-Capacity Sports Water Bottle","es":"Botella deportiva de gran capacidad","pt":"Garrafa esportiva de grande capacidade","ru":"Спортивная бутылка большого объёма","tr":"Büyük hacimli spor matarası"},
    "Spray Water Bottles": {"en":"Spray Water Bottle","es":"Botella con pulverizador","pt":"Garrafa com borrifador","ru":"Бутылка с распылителем","tr":"Spreyli su şişesi"},
    "Two-Way Drinking Cups": {"en":"Two-Way Drinking Cup","es":"Vaso con dos formas de beber","pt":"Copo com duas formas de beber","ru":"Термокружка с двумя способами питья","tr":"İki içim seçenekli bardak"},
    "Titanium Vacuum Cups": {"en":"Titanium Vacuum Cup","es":"Vaso térmico al vacío de titanio","pt":"Copo térmico a vácuo de titânio","ru":"Вакуумная термокружка из титана","tr":"Titanyum vakumlu termos bardak"},
}

LABEL = {
    "en": {
        "home":"Home","products":"Products","model":"Model","capacity":"Capacity","material":"Material / components","dimensions":"Product dimensions","colors":"Available colors","weight":"Unit weight","temperature":"Catalog temperature range","packing":"Unit packing","carton_qty":"Master carton quantity","carton_size":"Master carton dimensions","gross":"Master carton gross weight","source":"Factory catalog reference","details":"Model-specific sourcing details","faq":"Frequently asked questions","quote":"Request a wholesale quote","sample":"Discuss a sample","confirm":"Not specified in the factory catalog; confirm the exact SKU","no_colors":"Color names or codes are not specified; confirm options for the exact model.","no_material":"Exact body, lid and seal materials are not specified; confirm by SKU.","no_dimensions":"Dimensions are not specified; confirm the exact variant.","image_note":"Factory catalog image. Confirm the exact variant and sample appearance before ordering.","family_image_note":"Shared factory-family image; it does not prove the exact variant appearance. Confirm the selected model and sample.","plastic_custom":"For plastic models, ask about custom PP, PC, PETG, Tritan, PE or ABS options. Confirm the resin grade and the body, lid and seal components for the exact SKU. BPA-free status and food-contact suitability require model-specific evidence.","titanium_custom":"For titanium models, request the exact grade and composition, lid and seal materials, vacuum construction details, finish options and test documents for the selected SKU.","other_custom":"Body, lid, drinking valve and seal materials must be confirmed for the exact model. Custom component or material options can be reviewed against the project, sample and destination-market requirements.","capacity_answer":"The factory record lists {capacity}. The oz figure is an approximate overseas retail size class, not an exact conversion. Confirm the selected variant before ordering.","material_answer":"The source record lists {material}. Confirm which material is used for the body, lid and seal, and request destination-market food-contact evidence for the exact SKU.","plastic_answer":"Custom plastic resin options, colors, logo decoration and packaging can be discussed. The exact resin and component combination must be confirmed for this model; no BPA-free or food-contact certification is implied.","titanium_answer":"Confirm the titanium grade, composition, vacuum construction, lid materials and any thermal test method for the exact SKU before making performance claims.","other_answer":"Confirm the body, lid, valve and seal materials for the exact model. Custom options depend on the component design and order requirements.","packing_answer":"The source record lists {packing}. Confirm carton quantity, outer dimensions and final packing against the approved sample.","quote_answer":"Send the model number, required capacity, quantity, destination market, logo artwork, color brief and packing requirements. XUYI can then confirm sample availability, MOQ, quotation and lead time.","capacity_q":"What capacity is listed for model {model}?","material_q":"Which materials are specified for this model?","custom_q":"Can the plastic material, color or logo be customized?","packing_q":"What carton packing is listed?","quote_q":"What information is needed for a wholesale quotation?","verify":"Catalog figures are references. Confirm the selected variant, sample, component materials and final packing before mass production.",
    },
    "es": {
        "home":"Inicio","products":"Productos","model":"Modelo","capacity":"Capacidad","material":"Materiales y componentes","dimensions":"Dimensiones del producto","colors":"Colores disponibles","weight":"Peso por unidad","temperature":"Rango de temperatura del catálogo","packing":"Embalaje unitario","carton_qty":"Unidades por caja maestra","carton_size":"Medidas de la caja maestra","gross":"Peso bruto de la caja maestra","source":"Referencia del catálogo de fábrica","details":"Datos de compra específicos del modelo","faq":"Preguntas frecuentes","quote":"Solicitar cotización mayorista","sample":"Consultar una muestra","confirm":"No especificado en el catálogo de fábrica; confirmar el SKU exacto","no_colors":"No se indican nombres ni códigos de color; confirme las opciones del modelo exacto.","no_material":"No se especifican los materiales del cuerpo, la tapa y la junta; confirmar por SKU.","no_dimensions":"No se indican dimensiones; confirme la variante exacta.","image_note":"Imagen del catálogo de fábrica. Confirme la variante exacta y el aspecto de la muestra antes de pedir.","family_image_note":"Imagen compartida de una familia de fábrica; no confirma el aspecto de cada variante. Verifique el modelo y la muestra.","plastic_custom":"Para los modelos de plástico, consulte opciones a medida en PP, PC, PETG, Tritan, PE o ABS. Confirme la resina y los materiales del cuerpo, la tapa y la junta para el SKU exacto. El estado sin BPA y la aptitud alimentaria requieren pruebas del modelo.","titanium_custom":"Para los modelos de titanio, solicite el grado y la composición exactos, los materiales de la tapa y la junta, la estructura de vacío, los acabados y los documentos de ensayo del SKU elegido.","other_custom":"Los materiales del cuerpo, la tapa, la válvula y la junta deben confirmarse para el modelo exacto. Las opciones de componentes o materiales se revisan según el proyecto, la muestra y el mercado de destino.","capacity_answer":"El registro de fábrica indica {capacity}. La cifra en oz es una clase comercial aproximada para otros mercados, no una conversión exacta. Confirme la variante elegida antes de pedir.","material_answer":"El registro de origen indica {material}. Confirme qué material corresponde al cuerpo, la tapa y la junta, y solicite documentos de contacto alimentario para el SKU exacto.","plastic_answer":"Se pueden consultar resinas plásticas, colores, logotipo y embalaje personalizados. La combinación exacta de resina y componentes debe confirmarse para este modelo; no se presupone certificación sin BPA ni de contacto alimentario.","titanium_answer":"Confirme el grado y la composición del titanio, la estructura de vacío, los materiales de la tapa y el método de ensayo térmico del SKU exacto antes de hacer afirmaciones de rendimiento.","other_answer":"Confirme los materiales del cuerpo, la tapa, la válvula y la junta del modelo exacto. Las opciones personalizadas dependen del diseño de los componentes y del pedido.","packing_answer":"El registro de origen indica {packing}. Confirme la cantidad por caja, las dimensiones exteriores y el embalaje final con la muestra aprobada.","quote_answer":"Envíe el modelo, la capacidad requerida, la cantidad, el mercado de destino, el diseño del logotipo, los colores y el embalaje. XUYI podrá confirmar muestras, MOQ, cotización y plazo.","capacity_q":"¿Qué capacidad indica el catálogo para el modelo {model}?","material_q":"¿Qué materiales se especifican para este modelo?","custom_q":"¿Se pueden personalizar el plástico, el color o el logotipo?","packing_q":"¿Qué embalaje por caja indica el catálogo?","quote_q":"¿Qué datos se necesitan para una cotización mayorista?","verify":"Las cifras son referencias del catálogo. Confirme la variante, la muestra, los materiales de los componentes y el embalaje final antes de la producción.",
    },
    "pt": {
        "home":"Início","products":"Produtos","model":"Modelo","capacity":"Capacidade","material":"Materiais e componentes","dimensions":"Dimensões do produto","colors":"Cores disponíveis","weight":"Peso por unidade","temperature":"Faixa de temperatura do catálogo","packing":"Embalagem unitária","carton_qty":"Unidades por caixa master","carton_size":"Dimensões da caixa master","gross":"Peso bruto da caixa master","source":"Referência do catálogo da fábrica","details":"Dados de compra específicos do modelo","faq":"Perguntas frequentes","quote":"Solicitar cotação para atacado","sample":"Consultar uma amostra","confirm":"Não especificado no catálogo da fábrica; confirme o SKU exato","no_colors":"Os nomes ou códigos de cores não estão especificados; confirme as opções do modelo exato.","no_material":"Os materiais do corpo, da tampa e da vedação não estão especificados; confirme por SKU.","no_dimensions":"As dimensões não estão especificadas; confirme a variante exata.","image_note":"Imagem do catálogo da fábrica. Confirme a variante exata e a aparência da amostra antes do pedido.","family_image_note":"Imagem compartilhada de uma família de fábrica; não confirma a aparência de cada variante. Verifique o modelo e a amostra.","plastic_custom":"Para modelos de plástico, consulte opções personalizadas em PP, PC, PETG, Tritan, PE ou ABS. Confirme a resina e os materiais do corpo, da tampa e da vedação para o SKU exato. A condição sem BPA e a adequação ao contato com alimentos exigem evidências do modelo.","titanium_custom":"Para modelos de titânio, solicite o grau e a composição exatos, os materiais da tampa e da vedação, a estrutura a vácuo, os acabamentos e os documentos de teste do SKU escolhido.","other_custom":"Os materiais do corpo, da tampa, da válvula e da vedação devem ser confirmados para o modelo exato. Opções de componentes ou materiais podem ser avaliadas conforme o projeto, a amostra e o mercado de destino.","capacity_answer":"O registro da fábrica indica {capacity}. O valor em oz é uma classe comercial aproximada para outros mercados, não uma conversão exata. Confirme a variante escolhida antes do pedido.","material_answer":"O registro de origem indica {material}. Confirme qual material é usado no corpo, na tampa e na vedação e solicite documentos de contato com alimentos para o SKU exato.","plastic_answer":"É possível consultar resinas plásticas, cores, logotipo e embalagem personalizados. A combinação exata de resina e componentes deve ser confirmada para este modelo; não se presume certificação sem BPA ou para contato com alimentos.","titanium_answer":"Confirme o grau e a composição do titânio, a estrutura a vácuo, os materiais da tampa e o método de teste térmico do SKU exato antes de fazer alegações de desempenho.","other_answer":"Confirme os materiais do corpo, da tampa, da válvula e da vedação do modelo exato. As opções personalizadas dependem do projeto dos componentes e do pedido.","packing_answer":"O registro de origem indica {packing}. Confirme a quantidade por caixa, as dimensões externas e a embalagem final com a amostra aprovada.","quote_answer":"Envie o modelo, a capacidade desejada, a quantidade, o mercado de destino, a arte do logotipo, as cores e os requisitos de embalagem. A XUYI poderá confirmar amostras, MOQ, cotação e prazo.","capacity_q":"Qual capacidade está listada para o modelo {model}?","material_q":"Quais materiais estão especificados para este modelo?","custom_q":"É possível personalizar o plástico, a cor ou o logotipo?","packing_q":"Qual embalagem por caixa está listada?","quote_q":"Quais informações são necessárias para uma cotação de atacado?","verify":"Os números são referências do catálogo. Confirme a variante, a amostra, os materiais dos componentes e a embalagem final antes da produção.",
    },
    "ru": {
        "home":"Главная","products":"Продукция","model":"Модель","capacity":"Объём","material":"Материалы и компоненты","dimensions":"Размеры изделия","colors":"Доступные цвета","weight":"Вес единицы","temperature":"Температурный диапазон по каталогу","packing":"Индивидуальная упаковка","carton_qty":"Количество в транспортной коробке","carton_size":"Размеры транспортной коробки","gross":"Вес брутто транспортной коробки","source":"Ссылка на каталог производителя","details":"Данные для закупки конкретной модели","faq":"Часто задаваемые вопросы","quote":"Запросить оптовое предложение","sample":"Обсудить образец","confirm":"В каталоге производителя не указано; уточните точный SKU","no_colors":"Названия или коды цветов не указаны; уточните варианты для конкретной модели.","no_material":"Материалы корпуса, крышки и уплотнителя не указаны; уточните по SKU.","no_dimensions":"Размеры не указаны; уточните конкретный вариант.","image_note":"Изображение из каталога производителя. Перед заказом подтвердите вариант и внешний вид образца.","family_image_note":"Общее изображение семейства моделей; оно не подтверждает вид конкретного варианта. Проверьте модель и образец.","plastic_custom":"Для пластиковых моделей можно запросить варианты PP, PC, PETG, Tritan, PE или ABS. Уточните марку полимера и материалы корпуса, крышки и уплотнителя для конкретного SKU. Статус BPA-free и пригодность для пищевого контакта требуют документов именно этой модели.","titanium_custom":"Для титановых моделей запросите точную марку и состав титана, материалы крышки и уплотнителя, конструкцию вакуумной изоляции, варианты отделки и протоколы испытаний выбранного SKU.","other_custom":"Материалы корпуса, крышки, питьевого клапана и уплотнителя необходимо уточнить для конкретной модели. Индивидуальные материалы и компоненты рассматриваются с учётом проекта, образца и требований рынка.","capacity_answer":"В записи производителя указан объём {capacity}. Значение oz — приблизительный торговый размер для зарубежного рынка, а не точный пересчёт. Перед заказом подтвердите выбранный вариант.","material_answer":"В исходной записи указано: {material}. Уточните материал корпуса, крышки и уплотнителя и запросите документы для пищевого контакта по конкретному SKU.","plastic_answer":"Можно обсудить индивидуальные полимеры, цвета, логотип и упаковку. Точный состав смолы и компонентов необходимо подтвердить для этой модели; наличие BPA-free или пищевого сертификата не предполагается.","titanium_answer":"Перед заявлениями о свойствах подтвердите марку и состав титана, вакуумную конструкцию, материалы крышки и метод тепловых испытаний конкретного SKU.","other_answer":"Уточните материалы корпуса, крышки, клапана и уплотнителя конкретной модели. Возможности индивидуализации зависят от конструкции компонентов и заказа.","packing_answer":"В исходной записи указано: {packing}. Подтвердите количество в коробке, внешние размеры и итоговую упаковку по утверждённому образцу.","quote_answer":"Укажите модель, нужный объём, рынок поставки, количество, макет логотипа, цвета и требования к упаковке. После этого XUYI подтвердит образец, MOQ, цену и срок поставки.","capacity_q":"Какой объём указан для модели {model}?","material_q":"Какие материалы указаны для этой модели?","custom_q":"Можно ли изменить пластик, цвет или логотип?","packing_q":"Какая упаковка указана для транспортной коробки?","quote_q":"Какие данные нужны для оптового расчёта?","verify":"Значения приведены по каталогу. Перед серийным заказом подтвердите вариант, образец, материалы компонентов и итоговую упаковку.",
    },
    "tr": {
        "home":"Ana Sayfa","products":"Ürünler","model":"Model","capacity":"Kapasite","material":"Malzeme ve bileşenler","dimensions":"Ürün ölçüleri","colors":"Mevcut renkler","weight":"Birim ağırlık","temperature":"Katalog sıcaklık aralığı","packing":"Birim ambalajı","carton_qty":"Ana koli adedi","carton_size":"Ana koli ölçüleri","gross":"Ana koli brüt ağırlığı","source":"Fabrika kataloğu referansı","details":"Modele özel satın alma bilgileri","faq":"Sık sorulan sorular","quote":"Toptan teklif isteyin","sample":"Numuneyi görüşün","confirm":"Fabrika kataloğunda belirtilmemiştir; kesin SKU'yu doğrulayın","no_colors":"Renk adları veya kodları belirtilmemiştir; kesin modelin seçeneklerini doğrulayın.","no_material":"Gövde, kapak ve conta malzemeleri belirtilmemiştir; SKU bazında doğrulayın.","no_dimensions":"Ölçüler belirtilmemiştir; kesin varyantı doğrulayın.","image_note":"Fabrika katalog görseli. Siparişten önce kesin varyantı ve numune görünümünü doğrulayın.","family_image_note":"Bir ürün ailesinin ortak görselidir; kesin varyantın görünümünü kanıtlamaz. Modeli ve numuneyi doğrulayın.","plastic_custom":"Plastik modeller için özel PP, PC, PETG, Tritan, PE veya ABS seçeneklerini sorun. Kesin SKU için reçine sınıfını ve gövde, kapak, conta bileşenlerini doğrulayın. BPA içermeme ve gıda temas uygunluğu model bazında belge gerektirir.","titanium_custom":"Titanyum modellerde seçilen SKU için kesin kaliteyi ve bileşimi, kapak ve conta malzemelerini, vakum yapısını, yüzey seçeneklerini ve test belgelerini isteyin.","other_custom":"Gövde, kapak, içme valfi ve conta malzemeleri kesin model için doğrulanmalıdır. Özel bileşen veya malzeme seçenekleri proje, numune ve hedef pazar gereksinimlerine göre değerlendirilir.","capacity_answer":"Fabrika kaydında {capacity} belirtilmiştir. oz değeri yaklaşık bir yurt dışı perakende boyut sınıfıdır; kesin dönüşüm değildir. Siparişten önce seçilen varyantı doğrulayın.","material_answer":"Kaynak kaydında {material} belirtilmiştir. Kesin SKU için gövde, kapak ve conta malzemelerini doğrulayın ve hedef pazara uygun gıda temas belgelerini isteyin.","plastic_answer":"Özel plastik reçine, renk, logo ve ambalaj seçenekleri görüşülebilir. Kesin reçine ve bileşen birleşimi bu model için doğrulanmalıdır; BPA içermeme veya gıda temas sertifikası varsayılmaz.","titanium_answer":"Performans iddiasından önce kesin SKU'nun titanyum kalitesini ve bileşimini, vakum yapısını, kapak malzemelerini ve ısıl test yöntemini doğrulayın.","other_answer":"Kesin modelin gövde, kapak, valf ve conta malzemelerini doğrulayın. Özelleştirme seçenekleri bileşen tasarımına ve siparişe bağlıdır.","packing_answer":"Kaynak kaydında {packing} belirtilmiştir. Koli adedini, dış ölçüleri ve son ambalajı onaylı numuneyle doğrulayın.","quote_answer":"Model numarasını, istenen kapasiteyi, miktarı, hedef pazarı, logo tasarımını, renkleri ve ambalaj gereksinimlerini gönderin. XUYI numune, MOQ, teklif ve teslim süresini doğrulayabilir.","capacity_q":"{model} modeli için hangi kapasite listeleniyor?","material_q":"Bu model için hangi malzemeler belirtiliyor?","custom_q":"Plastik malzeme, renk veya logo özelleştirilebilir mi?","packing_q":"Hangi koli ambalajı listeleniyor?","quote_q":"Toptan fiyat teklifi için hangi bilgiler gerekir?","verify":"Rakamlar katalog referansıdır. Seri üretimden önce varyantı, numuneyi, bileşen malzemelerini ve son ambalajı doğrulayın.",
    },
}

FEATURES = [
    (r"\bpill\b|pill compartment", {"en":"a pill compartment","es":"un compartimento para pastillas","pt":"um compartimento para comprimidos","ru":"отделение для таблеток","tr":"hap bölmesi"}),
    (r"mixing ball|mixing insert|mixing accessory", {"en":"a mixing insert or accessory","es":"un inserto o accesorio mezclador","pt":"um acessório misturador","ru":"вставка или аксессуар для смешивания","tr":"karıştırıcı aparat"}),
    (r"\bstraw\b", {"en":"a straw drinking option","es":"una opción de bebida con pajita","pt":"uma opção de consumo com canudo","ru":"вариант питья через трубочку","tr":"pipetli içim seçeneği"}),
    (r"flip[\s-]?top|flip lid", {"en":"a flip-top lid","es":"una tapa abatible","pt":"uma tampa flip-top","ru":"откидную крышку","tr":"flip-top kapak"}),
    (r"\bhandle\b|carry loop|carry ring|carrying handle", {"en":"a carry handle or loop","es":"un asa o anilla de transporte","pt":"uma alça ou argola para transporte","ru":"ручку или петлю для переноски","tr":"taşıma sapı veya halkası"}),
    (r"\bspray\b|sprayer|mist nozzle", {"en":"a spray head or trigger","es":"un cabezal o gatillo pulverizador","pt":"um borrifador ou gatilho","ru":"распылитель или курок","tr":"sprey başlığı veya tetiği"}),
    (r"time marker|time scale|time markings", {"en":"time markers","es":"marcas horarias","pt":"marcações de horário","ru":"временные отметки","tr":"zaman işaretleri"}),
    (r"gradient|degrad[eê]", {"en":"a gradient color finish","es":"un acabado de color degradado","pt":"um acabamento em degradê","ru":"градиентную расцветку","tr":"degrade renk görünümü"}),
    (r"two[\s-]?way|dual drinking|two drinking", {"en":"two drinking modes","es":"dos modos de consumo","pt":"duas formas de beber","ru":"два способа питья","tr":"iki içim modu"}),
    (r"transparent|clear body", {"en":"a transparent body","es":"un cuerpo transparente","pt":"um corpo transparente","ru":"прозрачный корпус","tr":"şeffaf gövde"}),
]

PLASTIC_CATEGORIES = {"Plastic Shaker Bottles","Plastic Sports Water Bottles","Large Capacity Water Jugs","Spray Water Bottles"}
COLOR_WORDS = {
    "light blue":{"en":"Light Blue","es":"azul claro","pt":"azul-claro","ru":"светло-синий","tr":"açık mavi"},
    "blue":{"en":"Blue","es":"azul","pt":"azul","ru":"синий","tr":"mavi"},
    "gray":{"en":"Gray","es":"gris","pt":"cinza","ru":"серый","tr":"gri"},
    "grey":{"en":"Gray","es":"gris","pt":"cinza","ru":"серый","tr":"gri"},
    "red":{"en":"Red","es":"rojo","pt":"vermelho","ru":"красный","tr":"kırmızı"},
    "black":{"en":"Black","es":"negro","pt":"preto","ru":"чёрный","tr":"siyah"},
    "white":{"en":"White","es":"blanco","pt":"branco","ru":"белый","tr":"beyaz"},
    "green":{"en":"Green","es":"verde","pt":"verde","ru":"зелёный","tr":"yeşil"},
    "pink":{"en":"Pink","es":"rosa","pt":"rosa","ru":"розовый","tr":"pembe"},
    "purple":{"en":"Purple","es":"morado","pt":"roxo","ru":"фиолетовый","tr":"mor"},
    "yellow":{"en":"Yellow","es":"amarillo","pt":"amarelo","ru":"жёлтый","tr":"sarı"},
    "transparent":{"en":"Transparent","es":"transparente","pt":"transparente","ru":"прозрачный","tr":"şeffaf"},
}

def _model(row: dict) -> str:
    return str(row.get("factoryModel") or row.get("model") or "").strip()

def _values(row: dict, field: str, limit: int = 3) -> list[str]:
    variants = row.get("variants") or [row]
    found = []
    for variant in variants:
        if isinstance(variant, dict):
            value = str(variant.get(field) or "").strip()
            if value and value not in found:
                found.append(value)
    return found[:limit]

def _one(row: dict, field: str) -> str:
    return " / ".join(_values(row, field, 3))

def _capacity(row: dict, locale: str) -> str:
    from scripts.source_catalog_capacity_oz import catalog_volume_numbers, volume_terms
    numbers = catalog_volume_numbers(row)
    return volume_terms(numbers, locale) if numbers else {"en":"Capacity to be confirmed","es":"Capacidad por confirmar","pt":"Capacidade a confirmar","ru":"Объём уточняется","tr":"Kapasite doğrulanacak"}[locale]

def _feature_phrases(row: dict, locale: str) -> list[str]:
    source = " ".join(str(row.get(key) or "") for key in ("name", "description", "sourceNotes"))
    found = []
    for pattern, translations in FEATURES:
        if re.search(pattern, source, re.I):
            phrase = translations[locale]
            if phrase not in found:
                found.append(phrase)
        if len(found) == 2:
            break
    return found

def localized_name(row: dict, locale: str) -> str:
    category = str(row.get("category") or "")
    base = CATEGORY.get(category, {}).get(locale, CATEGORY.get(category, {}).get("en", "Drinkware"))
    features = _feature_phrases(row, locale)
    if not features:
        return base
    joiner = {"en":" with ","es":" con ","pt":" com ","ru":" — ","tr":" · "}[locale]
    return base + joiner + " / ".join(features)

def _material(row: dict, locale: str) -> str:
    raw = _one(row, "material")
    if not raw or re.search(r"not specified|confirm exact|to be confirmed|unknown", raw, re.I):
        return LABEL[locale]["no_material"]
    terms = {
        "body":{"en":"body","es":"cuerpo","pt":"corpo","ru":"корпус","tr":"gövde"},
        "lid":{"en":"lid","es":"tapa","pt":"tampa","ru":"крышка","tr":"kapak"},
        "silicone":{"en":"silicone","es":"silicona","pt":"silicone","ru":"силикон","tr":"silikon"},
    }
    raw = raw.replace("bottle body", "body")
    for key, values in terms.items():
        raw = re.sub(r"\b" + key + r"\b", values[locale], raw, flags=re.I)
    return raw

def _colors(row: dict, locale: str) -> str:
    raw = _one(row, "colors")
    if not raw or re.search(r"not specified|confirm available|to be confirmed", raw, re.I):
        return LABEL[locale]["no_colors"]
    for word in sorted(COLOR_WORDS, key=len, reverse=True):
        raw = re.sub(r"\b" + re.escape(word) + r"\b", COLOR_WORDS[word][locale], raw, flags=re.I)
    return raw.replace(", ", " / ")

def _packing(row: dict, locale: str) -> str:
    raw = _one(row, "packing")
    if not raw:
        return LABEL[locale]["confirm"]
    if re.search(r"not specified|confirm|unknown", raw, re.I):
        return LABEL[locale]["confirm"]
    replacements = {
        "en":[("OPP bag packaging","OPP bag packaging")],
        "es":[("OPP bag packaging","bolsa OPP"),("custom individual boxes","cajas individuales personalizadas"),("and printing"," e impresión"),("(MOQ to confirm)","(MOQ por confirmar)")],
        "pt":[("OPP bag packaging","saco OPP"),("custom individual boxes","caixas individuais personalizadas"),("and printing"," e impressão"),("(MOQ to confirm)","(MOQ a confirmar)")],
        "ru":[("OPP bag packaging","пакет OPP"),("custom individual boxes","индивидуальные коробки на заказ"),("and printing"," и печать"),("(MOQ to confirm)","(MOQ уточняется)")],
        "tr":[("OPP bag packaging","OPP poşet ambalaj"),("custom individual boxes","özel tekli kutular"),("and printing"," ve baskı"),("(MOQ to confirm)","(MOQ doğrulanmalı)")],
    }
    for old, new in replacements[locale]:
        raw = raw.replace(old, new)
    return raw

def _dimension(row: dict) -> str:
    raw = _one(row, "dimensions")
    return raw.replace("*", " × ").replace("x", " × ").replace("X", " × ") if raw else ""

def _feature_lead(row: dict, locale: str) -> str:
    features = _feature_phrases(row, locale)
    if not features:
        return ""
    prefix = {"en":"The listed design includes ","es":"El diseño indicado incluye ","pt":"O design listado inclui ","ru":"В описании конструкции указаны ","tr":"Listelenen tasarım özellikleri: "}[locale]
    return prefix + " / ".join(features) + "."

def _lead(row: dict, locale: str) -> str:
    model = _model(row)
    name = localized_name(row, locale)
    capacity = _capacity(row, locale)
    dimensions = _dimension(row)
    weight = _one(row, "unit_weight")
    carton_qty = _one(row, "carton_quantity")
    facts = []
    if dimensions: facts.append({"en":"dimensions ","es":"dimensiones ","pt":"dimensões ","ru":"размеры ","tr":"ürün ölçüleri "}[locale] + dimensions)
    if weight: facts.append({"en":"unit weight ","es":"peso por unidad ","pt":"peso por unidade ","ru":"вес единицы ","tr":"birim ağırlığı "}[locale] + weight)
    if carton_qty: facts.append({"en":"carton pack ","es":"unidades por caja ","pt":"unidades por caixa ","ru":"количество в коробке ","tr":"koli adedi "}[locale] + carton_qty)
    if locale == "en":
        parts = [f"XUYI model {model} is listed as a {name} with a catalog capacity of {capacity}."]
        if _feature_lead(row, locale): parts.append(_feature_lead(row, locale))
        if facts: parts.append("The factory record also lists " + "; ".join(facts) + ".")
        parts.append("Confirm the exact body and lid combination, color, included components and carton pack against an approved sample before bulk production.")
    elif locale == "es":
        parts = [f"El modelo XUYI {model} figura como {name}, con una capacidad de catálogo de {capacity}."]
        if _feature_lead(row, locale): parts.append(_feature_lead(row, locale))
        if facts: parts.append("El registro de fábrica también indica " + "; ".join(facts) + ".")
        parts.append("Confirme el cuerpo, la tapa, el color, los componentes incluidos y la caja con una muestra aprobada antes de la producción.")
    elif locale == "pt":
        parts = [f"O modelo XUYI {model} está listado como {name}, com capacidade de catálogo de {capacity}."]
        if _feature_lead(row, locale): parts.append(_feature_lead(row, locale))
        if facts: parts.append("O registro da fábrica também informa " + "; ".join(facts) + ".")
        parts.append("Confirme corpo, tampa, cor, componentes incluídos e caixa com uma amostra aprovada antes da produção.")
    elif locale == "ru":
        parts = [f"Модель XUYI {model} указана как {name}, объём по каталогу — {capacity}."]
        if _feature_lead(row, locale): parts.append(_feature_lead(row, locale))
        if facts: parts.append("В записи производителя также указаны " + "; ".join(facts) + ".")
        parts.append("Перед серийным заказом подтвердите корпус, крышку, цвет, комплектующие и коробку по утверждённому образцу.")
    else:
        parts = [f"XUYI {model} modeli, katalog kapasitesi {capacity} olan {name} olarak listelenmiştir."]
        if _feature_lead(row, locale): parts.append(_feature_lead(row, locale))
        if facts: parts.append("Fabrika kaydında ayrıca " + "; ".join(facts) + " belirtilir.")
        parts.append("Toplu üretimden önce gövdeyi, kapağı, rengi, dahil olan parçaları ve koli düzenini onaylı numuneyle doğrulayın.")
    return " ".join(parts)

def _benefits(row: dict, locale: str) -> list[tuple[str, str]]:
    category = str(row.get("category") or "")
    model = _model(row)
    capacity = _capacity(row, locale)
    dims = _dimension(row) or LABEL[locale]["no_dimensions"]
    material = _material(row, locale)
    carton = _one(row, "carton_quantity") or LABEL[locale]["confirm"]
    feature = " / ".join(_feature_phrases(row, locale)) or localized_name(row, locale)
    if category == "Titanium Vacuum Cups":
        return {
            "en":[("Construction review",f"Model {model} is listed as a titanium vacuum cup. Confirm titanium grade, lid assembly, vacuum structure and thermal test evidence for {capacity}."),("Material and finish", "Request composition and finish for the exact SKU. Do not infer purity, food-contact approval or heat-retention performance from a family image."),("Wholesale packing",f"Check protective packing and carton configuration ({carton}) before comparing freight.")],
            "es":[("Revisión de construcción",f"El modelo {model} figura como vaso térmico al vacío de titanio. Confirme el grado, la tapa, la estructura de vacío y las pruebas térmicas para {capacity}."),("Material y acabado","Solicite la composición y el acabado del SKU exacto. No deduzca pureza, aprobación alimentaria ni retención térmica a partir de una imagen de familia."),("Embalaje mayorista",f"Revise la protección y la configuración de caja ({carton}) antes de comparar el flete.")],
            "pt":[("Revisão da construção",f"O modelo {model} está listado como copo térmico a vácuo de titânio. Confirme grau, tampa, estrutura a vácuo e testes térmicos para {capacity}."),("Material e acabamento","Solicite composição e acabamento do SKU exato. Não presuma pureza, aprovação para contato com alimentos ou retenção térmica por uma imagem de família."),("Embalagem para atacado",f"Verifique a proteção e a configuração da caixa ({carton}) antes de comparar o frete.")],
            "ru":[("Проверка конструкции",f"Модель {model} указана как титановая вакуумная термокружка. Уточните марку титана, крышку, вакуумную конструкцию и тепловые испытания для объёма {capacity}."),("Материал и отделка","Запросите состав и отделку конкретного SKU. Не делайте выводы о чистоте титана, пищевом допуске или сохранении температуры по общему фото серии."),("Оптовая упаковка",f"Проверьте защитную упаковку и количество в коробке ({carton}) до расчёта доставки.")],
            "tr":[("Yapı kontrolü",f"{model} modeli titanyum vakumlu bardak olarak listelenmiştir. {capacity} seçeneği için titanyum kalitesini, kapağı, vakum yapısını ve ısıl testleri doğrulayın."),("Malzeme ve yüzey","Kesin SKU için bileşimi ve yüzey işlemini isteyin. Seri görselinden saflık, gıda teması onayı veya sıcak tutma performansı çıkarmayın."),("Toptan ambalaj",f"Nakliyeyi karşılaştırmadan önce koruyucu ambalajı ve koli düzenini ({carton}) kontrol edin.")],
        }[locale]
    if category == "Two-Way Drinking Cups":
        return {
            "en":[("Dual-use design",f"Review the two-way drinking arrangement on model {model}. Confirm the lid parts and drinking openings included for {capacity}."),("Body and lid materials","Ask for body, lid, valve and gasket materials separately. A combined material list does not establish which component uses each resin."),("Retail and bulk packing",f"Confirm colors, carton quantity ({carton}) and protective packing against the final sample.")],
            "es":[("Diseño de doble uso",f"Revise las dos formas de beber del modelo {model}. Confirme las piezas de la tapa y las aberturas incluidas para {capacity}."),("Materiales del cuerpo y la tapa","Solicite por separado los materiales del cuerpo, la tapa, la válvula y la junta. Una lista combinada no identifica cada componente."),("Embalaje minorista y mayorista",f"Confirme colores, unidades por caja ({carton}) y protección con la muestra final.")],
            "pt":[("Design de uso duplo",f"Revise as duas formas de beber do modelo {model}. Confirme as peças da tampa e as aberturas incluídas para {capacity}."),("Materiais do corpo e da tampa","Solicite separadamente os materiais do corpo, da tampa, da válvula e da vedação. Uma lista combinada não identifica cada componente."),("Embalagem de varejo e atacado",f"Confirme cores, unidades por caixa ({carton}) e proteção com a amostra final.")],
            "ru":[("Два способа питья",f"Проверьте конструкцию с двумя способами питья модели {model}. Уточните детали крышки и отверстия для объёма {capacity}."),("Материалы корпуса и крышки","Запросите отдельно материалы корпуса, крышки, клапана и уплотнителя. Общий перечень не определяет материал каждой детали."),("Розничная и оптовая упаковка",f"Согласуйте цвета, количество в коробке ({carton}) и защитную упаковку по образцу.")],
            "tr":[("Çift kullanımlı tasarım",f"{model} modelinin iki içim düzenini inceleyin. {capacity} seçeneğinde hangi kapak parçalarının ve içme açıklıklarının bulunduğunu doğrulayın."),("Gövde ve kapak malzemeleri","Gövde, kapak, valf ve conta malzemelerini ayrı ayrı isteyin. Birleşik malzeme listesi her parçanın reçinesini göstermez."),("Perakende ve toptan ambalaj",f"Renkleri, koli adedini ({carton}) ve koruyucu ambalajı son numuneyle doğrulayın.")],
        }[locale]
    return {
        "en":[("Product design",f"Model {model} is listed as {localized_name(row,locale)}. Review {feature}, the opening and closure against the intended sports, gym or everyday use."),("Plastic and component choices",f"The source material field reads: {material}. Confirm the exact resin and whether the body, lid and seal use different materials. Custom plastic options can be discussed by SKU."),("Wholesale packing",f"Compare dimensions {dims} and carton quantity {carton} before calculating storage and freight.")],
        "es":[("Diseño del producto",f"El modelo {model} figura como {localized_name(row,locale)}. Revise {feature}, la abertura y el cierre según el uso deportivo o diario."),("Plástico y componentes",f"El campo de materiales indica: {material}. Confirme la resina y si el cuerpo, la tapa y la junta utilizan materiales distintos. Las opciones de plástico a medida se consultan por SKU."),("Embalaje mayorista",f"Compare las dimensiones {dims} y las unidades por caja {carton} para calcular almacenamiento y transporte.")],
        "pt":[("Design do produto",f"O modelo {model} está listado como {localized_name(row,locale)}. Avalie {feature}, a abertura e o fecho para o uso esportivo ou diário."),("Plástico e componentes",f"O campo de materiais informa: {material}. Confirme a resina e se corpo, tampa e vedação usam materiais diferentes. Opções de plástico sob medida podem ser avaliadas por SKU."),("Embalagem para atacado",f"Compare as dimensões {dims} e as unidades por caixa {carton} para calcular armazenagem e frete.")],
        "ru":[("Конструкция изделия",f"Модель {model} указана как {localized_name(row,locale)}. Оцените {feature}, горловину и крышку для спортивного или повседневного использования."),("Пластик и компоненты",f"В поле материала указано: {material}. Уточните марку полимера и материалы корпуса, крышки и уплотнителя. Варианты индивидуального пластика обсуждаются для конкретного SKU."),("Оптовая упаковка",f"Сравните размеры {dims} и количество в коробке {carton} для расчёта хранения и перевозки.")],
        "tr":[("Ürün tasarımı",f"{model} modeli {localized_name(row,locale)} olarak listelenmiştir. Spor veya günlük kullanım için {feature}, ağız ve kapak yapısını inceleyin."),("Plastik ve bileşen seçenekleri",f"Malzeme alanında şu bilgi yer alır: {material}. Kesin reçineyi ve gövde, kapak, conta malzemelerini doğrulayın. Özel plastik seçenekleri SKU bazında görüşülebilir."),("Toptan ambalaj",f"Depolama ve nakliye hesabı için {dims} ölçülerini ve {carton} koli adedini karşılaştırın.")],
    }[locale]

def _steps(row: dict, locale: str) -> list[tuple[str, str]]:
    model = _model(row)
    return {
        "en":[("Confirm the exact model",f"Send model {model}, required capacity, lid style and material or component requirements."),("Define the brand brief","Share logo artwork, color references, decoration positions, retail packaging and target order quantity."),("Approve a sample","Check the body, lid, seal, included accessories, dimensions and print position on an approved sample."),("Confirm bulk delivery","Agree MOQ, quotation, inspection requirements, carton count, export documents and shipment terms.")],
        "es":[("Confirme el modelo exacto",f"Indique el modelo {model}, la capacidad, el tipo de tapa y los requisitos de materiales o componentes."),("Defina los requisitos de marca","Comparta el logotipo, las referencias de color, las posiciones de impresión, el embalaje y la cantidad prevista."),("Apruebe una muestra","Revise cuerpo, tapa, junta, accesorios, dimensiones e impresión en una muestra aprobada."),("Confirme la entrega","Confirme MOQ, cotización, inspección, cajas, documentos de exportación y condiciones de envío.")],
        "pt":[("Confirme o modelo exato",f"Informe o modelo {model}, a capacidade, o tipo de tampa e os requisitos de materiais ou componentes."),("Defina os requisitos da marca","Envie a arte do logotipo, referências de cor, posições de impressão, embalagem e quantidade pretendida."),("Aprove uma amostra","Verifique corpo, tampa, vedação, acessórios, dimensões e impressão em uma amostra aprovada."),("Confirme a entrega","Confirme MOQ, cotação, inspeção, caixas, documentos de exportação e condições de envio.")],
        "ru":[("Уточните модель",f"Укажите модель {model}, нужный объём, тип крышки и требования к материалам или компонентам."),("Передайте требования к бренду","Передайте макет логотипа, цвета, расположение печати, розничную упаковку и планируемый тираж."),("Утвердите образец","Проверьте корпус, крышку, уплотнитель, комплектующие, размеры и печать на утверждённом образце."),("Согласуйте поставку","Согласуйте MOQ, цену, контроль, количество коробок, экспортные документы и условия отгрузки.")],
        "tr":[("Kesin modeli doğrulayın",f"{model} modelini, gereken kapasiteyi, kapak tipini ve malzeme/bileşen gereksinimlerini iletin."),("Marka gereksinimlerini belirleyin","Logo dosyasını, renk referanslarını, baskı konumlarını, perakende ambalajını ve sipariş miktarını paylaşın."),("Numuneyi onaylayın","Gövdeyi, kapağı, contayı, aksesuarları, ölçüleri ve baskı yerini onaylı numunede kontrol edin."),("Toplu sevkiyatı netleştirin","MOQ, teklif, denetim, koli adedi, ihracat belgeleri ve sevkiyat koşullarını netleştirin.")],
    }[locale]

def _faq(row: dict, locale: str) -> list[tuple[str, str]]:
    labels = LABEL[locale]
    model = _model(row)
    from scripts.source_catalog_capacity_oz import catalog_volume_numbers, volume_terms
    numbers = catalog_volume_numbers(row)
    capacity = _capacity(row, locale)
    material = _material(row, locale)
    packing = _packing(row, locale)
    category = str(row.get("category") or "")
    custom_answer = labels["plastic_answer"] if category in PLASTIC_CATEGORIES else (labels["titanium_answer"] if category == "Titanium Vacuum Cups" else labels["other_answer"])
    custom_question = labels["custom_q"] if category in PLASTIC_CATEGORIES else ({
        "en":"Can the titanium grade, lid or finish be customized?","es":"¿Se pueden personalizar el grado de titanio, la tapa o el acabado?","pt":"É possível personalizar o grau do titânio, a tampa ou o acabamento?","ru":"Можно ли выбрать марку титана, крышку или отделку?","tr":"Titanyum kalitesi, kapak veya yüzey özelleştirilebilir mi?"
    }[locale] if category == "Titanium Vacuum Cups" else {
        "en":"Can body, lid or seal materials, color or logo be customized?","es":"¿Se pueden personalizar los materiales, el color o el logotipo?","pt":"É possível personalizar materiais, cor ou logotipo?","ru":"Можно ли изменить материалы, цвет или логотип?","tr":"Malzeme, renk veya logo özelleştirilebilir mi?"
    }[locale])
    return [
        (labels["capacity_q"].format(model=model), labels["capacity_answer"].format(capacity=capacity)),
        (labels["material_q"], labels["material_answer"].format(material=material)),
        (custom_question, custom_answer),
        (labels["packing_q"], labels["packing_answer"].format(packing=packing)),
        (labels["quote_q"], labels["quote_answer"]),
    ]

def _spec_rows(row: dict, locale: str) -> list[tuple[str, str]]:
    labels = LABEL[locale]
    product_type = {"en":"Product type","es":"Tipo de producto","pt":"Tipo de produto","ru":"Тип изделия","tr":"Ürün türü"}[locale]
    rows = [
        (labels["model"], _model(row)),
        (product_type, localized_name(row, locale)),
        (labels["capacity"], _capacity(row, locale)),
        (labels["material"], _material(row, locale)),
        (labels["dimensions"], _dimension(row) or labels["no_dimensions"]),
        (labels["colors"], _colors(row, locale)),
    ]
    optional = [
        (labels["weight"], _one(row,"unit_weight")),
        (labels["temperature"], _one(row,"temperature_range")),
        (labels["packing"], _packing(row,locale)),
        (labels["carton_qty"], _one(row,"carton_quantity")),
        (labels["carton_size"], _one(row,"carton_size")),
        (labels["gross"], _one(row,"carton_gross_weight")),
    ]
    rows.extend((label,value) for label,value in optional if value)
    page = str(row.get("sourcePage") or "").strip()
    if page:
        rows.append((labels["source"], {"en":f"Factory catalog, page {page}","es":f"Catálogo de fábrica, página {page}","pt":f"Catálogo da fábrica, página {page}","ru":f"Каталог производителя, стр. {page}","tr":f"Fabrika kataloğu, sayfa {page}"}[locale]))
    return rows

def detail(row: dict, locale: str, series: dict | None = None) -> str:
    if locale not in LABEL:
        raise ValueError("Unsupported factory product locale: " + str(locale))
    from site_renderer import CAT, photo, render_template
    from scripts.source_catalog_capacity_oz import product_h1_text

    labels = LABEL[locale]
    model = _model(row)
    slug = str(row.get("slug") or model).strip("/")
    category = str(row.get("category") or "")
    if category not in CAT:
        raise ValueError("Unknown factory product category: " + category)
    category_slug = CAT[category][1]
    name = localized_name(row, locale)
    h1 = product_h1_text(locale, row)
    images = row.get("images") or []
    if not images:
        raise ValueError("Factory product has no reviewed image: " + model)
    main_image = str(images[0])
    alt = f"{name} · {labels['model']} {model}"
    main_photo = photo(main_image, alt, "eager").replace("<img ", '<img id="main-photo" ', 1)
    family_image = row.get("imageReviewStatus") == "visually_reviewed_source_family_image"
    photo_note = labels["family_image_note"] if family_image else labels["image_note"]
    breadcrumb = (
        '<nav class="breadcrumb" aria-label="Breadcrumb"><a href="/">' + escape(labels["home"]) +
        '</a> / <a href="/products/">' + escape(labels["products"]) +
        '</a> / <a href="/collections/' + escape(category_slug) + '/">' +
        escape(CATEGORY.get(category, {}).get(locale, category)) + '</a> / ' + escape(model) + '</nav>'
    )
    specs = '<table class="spec">' + "".join(
        '<tr><th scope="row">' + escape(label) + '</th><td>' + escape(value) + '</td></tr>'
        for label, value in _spec_rows(row, locale)
    ) + '</table>'
    thumbs = ""
    if len(images) > 1:
        aria = {"en":"Show product image ","es":"Mostrar imagen del producto ","pt":"Mostrar imagem do produto ","ru":"Показать фото товара ","tr":"Ürün görselini göster "}[locale]
        thumbs = '<div class="product-detail__thumbs">' + "".join(
            '<button type="button" class="product-detail__thumb" data-main-photo="' + escape(str(image),quote=True) +
            '" aria-label="' + escape(aria + model + " " + str(index+1),quote=True) + '">' +
            photo(str(image),"") + '</button>' for index,image in enumerate(images[1:4])
        ) + '</div>'
    eyebrow = {
        "en":"B2B WHOLESALE DRINKWARE MANUFACTURER","es":"FABRICANTE DE BOTELLAS PARA MAYORISTAS B2B",
        "pt":"FABRICANTE DE GARRAFAS PARA ATACADO B2B","ru":"ПРОИЗВОДИТЕЛЬ ДЛЯ ОПТОВЫХ B2B-ПОСТАВОК",
        "tr":"B2B TOPTAN MATARA ÜRETİCİSİ",
    }[locale]
    quote = {
        "en":"To compare wholesale quotations, include this model, capacity, destination, logo or color brief and carton requirements.",
        "es":"Para comparar cotizaciones mayoristas, incluya el modelo, la capacidad, el destino, el logotipo o los colores y los requisitos de caja.",
        "pt":"Para comparar cotações de atacado, informe o modelo, a capacidade, o destino, o logotipo ou as cores e os requisitos da caixa.",
        "ru":"Для сравнения оптовых предложений укажите модель, объём, рынок поставки, логотип или цвета и требования к коробке.",
        "tr":"Toptan teklifleri karşılaştırmak için model, kapasite, hedef pazar, logo veya renk brief'i ve koli gereksinimlerini belirtin.",
    }[locale]
    before_order = {
        "en":"Before ordering: confirm body and lid material grades, food-contact evidence for the destination market, selected capacity, color, artwork, MOQ and lead time.",
        "es":"Antes del pedido: confirme los materiales del cuerpo y la tapa, los documentos de contacto alimentario del mercado de destino, la capacidad, el color, el diseño, el MOQ y el plazo.",
        "pt":"Antes do pedido: confirme os materiais do corpo e da tampa, os documentos de contato com alimentos do mercado de destino, a capacidade, a cor, a arte, o MOQ e o prazo.",
        "ru":"Перед заказом подтвердите материалы корпуса и крышки, документы для пищевого контакта на целевом рынке, объём, цвет, макет, MOQ и срок.",
        "tr":"Siparişten önce gövde ve kapak malzeme sınıflarını, hedef pazar için gıda temas belgelerini, kapasiteyi, rengi, tasarımı, MOQ ve termin süresini doğrulayın.",
    }[locale]
    body = (
        '<section class="section product-overview"><div class="shell">' + breadcrumb +
        '<div class="product-detail"><div class="product-detail__photos"><div class="product-detail__main">' +
        main_photo + '</div>' + thumbs + '<p class="copy-muted">' + escape(photo_note) +
        '</p></div><div><span class="eyebrow">' + escape(eyebrow + " · " + labels["model"] + " " + model) +
        '</span><h1>' + escape(h1) + '</h1><div class="product-detail__lead"><p class="copy-muted">' +
        escape(_lead(row,locale)) + '</p></div>' + specs +
        '<div class="actions"><a class="button" href="/contact/?model=' + escape(slug,quote=True) +
        '#inquiry">' + escape(labels["quote"]) + ' →</a><a class="button button--outline" href="/contact/?model=' +
        escape(slug,quote=True) + '&amp;type=Samples#inquiry">' + escape(labels["sample"]) + ' ↗</a></div>' +
        '<p class="product-detail__quote-note">' + escape(quote) + '</p><p class="notice">' +
        escape(before_order) + '</p></div></div></div></section>'
    )
    body += '<section class="section section--soft product-content"><div class="shell"><div class="section__head"><div><span class="eyebrow">' + escape(labels["details"]) + '</span><h2 class="section__title">' + escape(name) + '</h2><p>' + escape(_lead(row,locale)) + '</p></div></div><div class="grid grid--3">'
    for heading,description in _benefits(row,locale):
        body += render_template("product-benefit",HEADING=escape(heading),DESCRIPTION=escape(description))
    body += '</div></div></section>'
    body += '<section class="section product-ordering"><div class="shell"><div class="section__head"><div><span class="eyebrow">OEM / ODM</span><h2 class="section__title">' + escape({"en":"Wholesale OEM / ODM process","es":"Proceso OEM / ODM mayorista","pt":"Processo OEM / ODM para atacado","ru":"Процесс оптового OEM / ODM","tr":"Toptan OEM / ODM süreci"}[locale]) + '</h2><p>' + escape(quote) + '</p></div></div><div class="grid grid--4">'
    for heading,description in _steps(row,locale):
        body += render_template("product-benefit",HEADING=escape(heading),DESCRIPTION=escape(description))
    body += '</div><p class="product-content__cta"><a href="/capabilities/oem-odm/">' + escape({"en":"OEM / ODM capabilities","es":"Capacidades OEM / ODM","pt":"Recursos OEM / ODM","ru":"Возможности OEM / ODM","tr":"OEM / ODM yetenekleri"}[locale]) + ' →</a> · <a href="/capabilities/custom-logo/">' + escape({"en":"Custom logo","es":"Logotipo personalizado","pt":"Logotipo personalizado","ru":"Индивидуальный логотип","tr":"Özel logo"}[locale]) + ' →</a></p></div></section>'
    body += '<section class="section section--soft"><div class="shell"><div class="section__head"><div><span class="eyebrow">' + escape(labels["faq"]) + '</span><h2 class="section__title">' + escape(labels["faq"] + " · " + model) + '</h2></div></div><div class="faq-list">'
    for question,answer in _faq(row,locale):
        body += '<details><summary>' + escape(question) + '</summary><p>' + escape(answer) + '</p></details>'
    body += '</div></div></section>'
    if series:
        related = [item for item in series.values() if item.get("category")==category and item.get("slug")!=slug and item.get("sourceDocument") in SOURCE_DOCUMENTS][:4]
        if related:
            related_title = {"en":"Related wholesale models","es":"Modelos mayoristas relacionados","pt":"Modelos relacionados para atacado","ru":"Похожие модели для оптовых закупок","tr":"İlgili toptan modeller"}[locale]
            body += '<section class="section"><div class="shell"><div class="section__head"><div><span class="eyebrow">' + escape(labels["products"]) + '</span><h2 class="section__title">' + escape(related_title) + '</h2></div></div><ul class="related-product-links">'
            for item in related:
                body += '<li><a href="/products/' + escape(str(item.get("slug") or item.get("model")),quote=True) + '/">' + escape(localized_name(item,locale) + " · " + _model(item)) + '</a></li>'
            body += '</ul></div></section>'
    return body

def translation_for(row: dict, locale: str, series: dict | None = None) -> dict:
    from scripts.source_catalog_capacity_oz import catalog_volume_numbers, new_seo, new_seo_without_capacity
    numbers = catalog_volume_numbers(row)
    title,description = new_seo(locale,row,numbers) if numbers else new_seo_without_capacity(locale,row)
    return {"title":title,"description":description,"mainHtml":detail(row,locale,series)}