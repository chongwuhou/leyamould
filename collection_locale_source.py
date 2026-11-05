"""Reviewed source copy for collection pages whose D1 translation record is not yet present.

This is a fail-closed, source-owned fallback: it only covers the three collection
routes already present in the English catalog and supplies reviewed locale copy.
D1 translations still win whenever they exist.
"""

from __future__ import annotations

import html
import re


COMMON = {
    "es": {
        "Home": "Inicio",
        "Products": "Productos",
        "All products": "Todos los productos",
        "Sports Water Bottles": "Botellas deportivas",
        "Large Capacity Water Jugs": "Garrafas de agua de gran capacidad",
        "Kids Water Bottles": "Botellas de agua infantiles",
        "Protein Shaker Bottles": "Shakers de proteínas",
        "Spray Water Bottles": "Botellas pulverizadoras",
        "Two-Way Drinking Cups": "Vasos de doble modo",
        "Titanium Vacuum Cups": "Vasos de vacío de titanio",
        "← Prev": "← Anterior",
        "Next →": "Siguiente →",
        "B2B SOURCING NOTES": "NOTAS DE ABASTECIMIENTO B2B",
        "How to Choose Before You Order": "Cómo elegir antes de pedir",
        "These are buying checkpoints, not claims that every model has the same features or approvals.": "Estos son puntos de compra; no significan que todos los modelos tengan las mismas funciones o aprobaciones.",
        "Send Your Model & Requirements →": "Envíe su modelo y requisitos →",
        "Read Wholesale Buying FAQs →": "Leer preguntas frecuentes de compras mayoristas →",
        "OEM & CUSTOMIZATION": "OEM Y PERSONALIZACIÓN",
        "Wholesale & Custom Bottle Solutions": "Soluciones de botellas personalizadas y al por mayor",
        "Ask about available colors, custom printing, branding and packing for the models that interest you.": "Consulte los colores disponibles, la impresión, el marcado y el embalaje de los modelos que le interesen.",
        "Factory-backed Supply": "Suministro respaldado por fábrica",
        "We operate our own manufacturing facility and coordinate additional products through selected production partners.": "Operamos nuestra propia fábrica y coordinamos productos adicionales mediante socios de producción seleccionados.",
        "Custom Branding": "Personalización de marca",
        "Discuss logo artwork, product color, decoration method and brand packaging for compatible models.": "Hable sobre el logotipo, el color del producto, el método de decoración y el embalaje de marca de los modelos compatibles.",
        "Detailed Product Data": "Datos detallados del producto",
        "Ask us about capacity, size, material components and packing configuration for each selected model.": "Consúltenos la capacidad, el tamaño, los componentes materiales y la configuración del embalaje de cada modelo seleccionado.",
        "Order Coordination": "Coordinación del pedido",
        "One B2B inquiry process for product selection, quotation, sampling, quality checks and shipment.": "Un proceso B2B para seleccionar productos, cotizar, preparar muestras, revisar la calidad y coordinar el envío.",
        "Product FAQ": "Preguntas frecuentes del producto",
        "Wholesale Buying Questions": "Preguntas de compra al por mayor",
        "Contact XUYI with model number, quantity and destination.": "Contacte con XUYI indicando el modelo, la cantidad y el destino.",
        "Can you customize bottle colors and logos?": "¿Pueden personalizar los colores y logotipos?",
        "We can review logo artwork, colors and packaging for each selected model. Available decoration methods and order requirements are confirmed during quotation.": "Podemos revisar el diseño del logotipo, los colores y el embalaje de cada modelo. Los métodos de decoración y los requisitos del pedido se confirman durante la cotización.",
        "What is your MOQ for wholesale orders?": "¿Cuál es su MOQ para pedidos al por mayor?",
        "Minimum order quantity depends on bottle model, stock availability and customization. Send us the products and estimated volume to get an accurate answer.": "La cantidad mínima depende del modelo, la disponibilidad y la personalización. Envíenos los productos y el volumen estimado para obtener una respuesta precisa.",
        "Do you offer samples before bulk production?": "¿Ofrecen muestras antes de la producción en volumen?",
        "Sample availability, lead time and cost are confirmed according to the product and destination. Please include your model number and required custom work.": "La disponibilidad, el plazo y el coste de la muestra se confirman según el producto y el destino. Incluya el modelo y el trabajo personalizado solicitado.",
        "Which bottle materials can you supply?": "¿Qué materiales de botella pueden suministrar?",
        "PC, Tritan, PP and PETG options are available according to customer requirements. Ask about BPA-free options for a selected model and request documentation for your destination market.": "Hay opciones de PC, Tritan, PP y PETG según los requisitos del cliente. Pregunte por opciones sin BPA para el modelo elegido y solicite la documentación para su mercado.",
        "Do you have your own factory?": "¿Disponen de fábrica propia?",
        "XUYI operates its own manufacturing facility and may coordinate production through selected partner facilities for some products. We confirm project requirements and applicable quality controls.": "XUYI opera su propia fábrica y puede coordinar algunos productos mediante instalaciones asociadas seleccionadas. Confirmamos los requisitos del proyecto y los controles de calidad aplicables.",
        "How long does production and shipping take?": "¿Cuánto tardan la producción y el envío?",
        "Production and shipping timelines depend on model, order quantity, materials, custom artwork and destination. We provide an order-specific timeline after reviewing requirements.": "Los plazos de producción y envío dependen del modelo, la cantidad, los materiales, el diseño personalizado y el destino. Ofrecemos un calendario específico después de revisar los requisitos.",
    },
    "pt": {
        "Home": "Início",
        "Products": "Produtos",
        "All products": "Todos os produtos",
        "Sports Water Bottles": "Garrafas esportivas",
        "Large Capacity Water Jugs": "Garrafões de água de grande capacidade",
        "Kids Water Bottles": "Garrafas de água infantis",
        "Protein Shaker Bottles": "Coqueteleiras de proteína",
        "Spray Water Bottles": "Garrafas spray",
        "Two-Way Drinking Cups": "Copos de duas formas de beber",
        "Titanium Vacuum Cups": "Copos a vácuo de titânio",
        "← Prev": "← Anterior",
        "Next →": "Próximo →",
        "B2B SOURCING NOTES": "NOTAS DE COMPRA B2B",
        "How to Choose Before You Order": "Como escolher antes de fazer o pedido",
        "These are buying checkpoints, not claims that every model has the same features or approvals.": "São pontos de verificação de compra; não afirmam que todos os modelos tenham os mesmos recursos ou aprovações.",
        "Send Your Model & Requirements →": "Envie seu modelo e requisitos →",
        "Read Wholesale Buying FAQs →": "Leia as perguntas frequentes de atacado →",
        "OEM & CUSTOMIZATION": "OEM E PERSONALIZAÇÃO",
        "Wholesale & Custom Bottle Solutions": "Soluções de garrafas personalizadas e atacado",
        "Ask about available colors, custom printing, branding and packing for the models that interest you.": "Consulte as cores disponíveis, impressão, marca e embalagem dos modelos de seu interesse.",
        "Factory-backed Supply": "Fornecimento apoiado pela fábrica",
        "We operate our own manufacturing facility and coordinate additional products through selected production partners.": "Operamos nossa própria fábrica e coordenamos produtos adicionais com parceiros de produção selecionados.",
        "Custom Branding": "Personalização de marca",
        "Discuss logo artwork, product color, decoration method and brand packaging for compatible models.": "Converse sobre a arte do logotipo, a cor do produto, o método de decoração e a embalagem de marca dos modelos compatíveis.",
        "Detailed Product Data": "Dados detalhados do produto",
        "Ask us about capacity, size, material components and packing configuration for each selected model.": "Pergunte sobre capacidade, tamanho, componentes de material e configuração de embalagem de cada modelo selecionado.",
        "Order Coordination": "Coordenação do pedido",
        "One B2B inquiry process for product selection, quotation, sampling, quality checks and shipment.": "Um processo B2B para seleção, cotação, amostras, controles de qualidade e envio.",
        "Product FAQ": "Perguntas frequentes do produto",
        "Wholesale Buying Questions": "Perguntas de compra por atacado",
        "Contact XUYI with model number, quantity and destination.": "Entre em contato com a XUYI informando o modelo, a quantidade e o destino.",
        "Can you customize bottle colors and logos?": "Vocês personalizam cores e logotipos das garrafas?",
        "We can review logo artwork, colors and packaging for each selected model. Available decoration methods and order requirements are confirmed during quotation.": "Podemos revisar a arte do logotipo, as cores e a embalagem de cada modelo. Os métodos de decoração e os requisitos do pedido são confirmados na cotação.",
        "What is your MOQ for wholesale orders?": "Qual é o MOQ para pedidos de atacado?",
        "Minimum order quantity depends on bottle model, stock availability and customization. Send us the products and estimated volume to get an accurate answer.": "A quantidade mínima depende do modelo, disponibilidade em estoque e personalização. Envie os produtos e o volume estimado para uma resposta precisa.",
        "Do you offer samples before bulk production?": "Vocês oferecem amostras antes da produção em volume?",
        "Sample availability, lead time and cost are confirmed according to the product and destination. Please include your model number and required custom work.": "A disponibilidade, o prazo e o custo da amostra são confirmados conforme o produto e o destino. Inclua o modelo e o trabalho personalizado necessário.",
        "Which bottle materials can you supply?": "Quais materiais de garrafa vocês fornecem?",
        "PC, Tritan, PP and PETG options are available according to customer requirements. Ask about BPA-free options for a selected model and request documentation for your destination market.": "Há opções de PC, Tritan, PP e PETG conforme os requisitos do cliente. Pergunte por opções sem BPA para o modelo selecionado e solicite a documentação para o seu mercado.",
        "Do you have your own factory?": "Vocês têm fábrica própria?",
        "XUYI operates its own manufacturing facility and may coordinate production through selected partner facilities for some products. We confirm project requirements and applicable quality controls.": "A XUYI opera sua própria fábrica e pode coordenar alguns produtos por meio de instalações parceiras selecionadas. Confirmamos os requisitos do projeto e os controles de qualidade aplicáveis.",
        "How long does production and shipping take?": "Quanto tempo levam a produção e o envio?",
        "Production and shipping timelines depend on model, order quantity, materials, custom artwork and destination. We provide an order-specific timeline after reviewing requirements.": "Os prazos de produção e envio dependem do modelo, quantidade, materiais, arte personalizada e destino. Fornecemos um cronograma específico após revisar os requisitos.",
    },
    "ru": {
        "Home": "Главная",
        "Products": "Продукция",
        "All products": "Все товары",
        "Sports Water Bottles": "Спортивные бутылки",
        "Large Capacity Water Jugs": "Бутылки большого объёма",
        "Kids Water Bottles": "Детские бутылки для воды",
        "Protein Shaker Bottles": "Шейкеры для протеина",
        "Spray Water Bottles": "Бутылки-распылители",
        "Two-Way Drinking Cups": "Двухрежимные питьевые стаканы",
        "Titanium Vacuum Cups": "Титановые вакуумные стаканы",
        "← Prev": "← Назад",
        "Next →": "Далее →",
        "B2B SOURCING NOTES": "ПРИМЕЧАНИЯ ДЛЯ B2B-ЗАКУПОК",
        "How to Choose Before You Order": "Как выбрать товар до заказа",
        "These are buying checkpoints, not claims that every model has the same features or approvals.": "Это контрольные точки закупки, а не утверждение, что все модели имеют одинаковые функции или разрешения.",
        "Send Your Model & Requirements →": "Отправьте модель и требования →",
        "Read Wholesale Buying FAQs →": "Читайте ответы для оптовых покупателей →",
        "OEM & CUSTOMIZATION": "OEM И ПЕРСОНАЛИЗАЦИЯ",
        "Wholesale & Custom Bottle Solutions": "Оптовые и индивидуальные решения для бутылок",
        "Ask about available colors, custom printing, branding and packing for the models that interest you.": "Уточните доступные цвета, печать, брендирование и упаковку интересующих моделей.",
        "Factory-backed Supply": "Поставка от производителя",
        "We operate our own manufacturing facility and coordinate additional products through selected production partners.": "Мы работаем на собственной производственной площадке и координируем дополнительные товары с отобранными производственными партнёрами.",
        "Custom Branding": "Брендирование под заказ",
        "Discuss logo artwork, product color, decoration method and brand packaging for compatible models.": "Обсудите макет логотипа, цвет изделия, способ декорирования и брендированную упаковку совместимых моделей.",
        "Detailed Product Data": "Подробные данные о товаре",
        "Ask us about capacity, size, material components and packing configuration for each selected model.": "Уточните объём, размеры, материалы компонентов и конфигурацию упаковки каждой выбранной модели.",
        "Order Coordination": "Координация заказа",
        "One B2B inquiry process for product selection, quotation, sampling, quality checks and shipment.": "Единый B2B-процесс выбора товара, расчёта, образцов, контроля качества и отгрузки.",
        "Product FAQ": "Вопросы о товаре",
        "Wholesale Buying Questions": "Вопросы оптовой закупки",
        "Contact XUYI with model number, quantity and destination.": "Свяжитесь с XUYI, указав модель, количество и направление поставки.",
        "Can you customize bottle colors and logos?": "Можно ли изменить цвета и логотипы бутылок?",
        "We can review logo artwork, colors and packaging for each selected model. Available decoration methods and order requirements are confirmed during quotation.": "Мы можем проверить макет логотипа, цвета и упаковку каждой выбранной модели. Способ декорирования и требования к заказу подтверждаются при расчёте.",
        "What is your MOQ for wholesale orders?": "Какой MOQ для оптового заказа?",
        "Minimum order quantity depends on bottle model, stock availability and customization. Send us the products and estimated volume to get an accurate answer.": "Минимальная партия зависит от модели, наличия и персонализации. Отправьте товары и предполагаемый объём, чтобы получить точный ответ.",
        "Do you offer samples before bulk production?": "Предоставляете ли вы образцы до массового производства?",
        "Sample availability, lead time and cost are confirmed according to the product and destination. Please include your model number and required custom work.": "Наличие, срок и стоимость образца подтверждаются с учётом товара и направления поставки. Укажите модель и требуемую персонализацию.",
        "Which bottle materials can you supply?": "Какие материалы бутылок вы поставляете?",
        "PC, Tritan, PP and PETG options are available according to customer requirements. Ask about BPA-free options for a selected model and request documentation for your destination market.": "Доступны варианты PC, Tritan, PP и PETG по требованиям клиента. Уточните варианты без BPA для выбранной модели и запросите документы для вашего рынка.",
        "Do you have your own factory?": "У вас есть собственное производство?",
        "XUYI operates its own manufacturing facility and may coordinate production through selected partner facilities for some products. We confirm project requirements and applicable quality controls.": "XUYI работает на собственной производственной площадке и для некоторых товаров может координировать выпуск на отобранных партнёрских предприятиях. Мы подтверждаем требования проекта и применимые проверки качества.",
        "How long does production and shipping take?": "Сколько занимают производство и доставка?",
        "Production and shipping timelines depend on model, order quantity, materials, custom artwork and destination. We provide an order-specific timeline after reviewing requirements.": "Сроки производства и доставки зависят от модели, количества, материалов, макета и направления поставки. После проверки требований мы предоставляем график для конкретного заказа.",
    },
    "tr": {
        "Home": "Ana Sayfa",
        "Products": "Ürünler",
        "All products": "Tüm ürünler",
        "Sports Water Bottles": "Spor su şişeleri",
        "Large Capacity Water Jugs": "Büyük hacimli su bidonları",
        "Kids Water Bottles": "Çocuk su şişeleri",
        "Protein Shaker Bottles": "Protein shaker şişeleri",
        "Spray Water Bottles": "Sprey su şişeleri",
        "Two-Way Drinking Cups": "Çift kullanımlı içme bardakları",
        "Titanium Vacuum Cups": "Titanyum vakumlu bardaklar",
        "← Prev": "← Önceki",
        "Next →": "Sonraki →",
        "B2B SOURCING NOTES": "B2B TEDARİK NOTLARI",
        "How to Choose Before You Order": "Sipariş vermeden önce nasıl seçilir",
        "These are buying checkpoints, not claims that every model has the same features or approvals.": "Bunlar satın alma kontrol noktalarıdır; her modelin aynı özelliklere veya onaylara sahip olduğu anlamına gelmez.",
        "Send Your Model & Requirements →": "Modelinizi ve gereksinimlerinizi gönderin →",
        "Read Wholesale Buying FAQs →": "Toptan satın alma SSS'lerini okuyun →",
        "OEM & CUSTOMIZATION": "OEM VE ÖZELLEŞTİRME",
        "Wholesale & Custom Bottle Solutions": "Toptan ve özel şişe çözümleri",
        "Ask about available colors, custom printing, branding and packing for the models that interest you.": "İlgilendiğiniz modeller için mevcut renkleri, özel baskıyı, markalamayı ve ambalajı sorun.",
        "Factory-backed Supply": "Fabrika destekli tedarik",
        "We operate our own manufacturing facility and coordinate additional products through selected production partners.": "Kendi üretim tesisimizi işletiyor ve ek ürünleri seçilmiş üretim ortaklarıyla koordine ediyoruz.",
        "Custom Branding": "Özel markalama",
        "Discuss logo artwork, product color, decoration method and brand packaging for compatible models.": "Uyumlu modeller için logo tasarımını, ürün rengini, dekorasyon yöntemini ve marka ambalajını görüşün.",
        "Detailed Product Data": "Ayrıntılı ürün verileri",
        "Ask us about capacity, size, material components and packing configuration for each selected model.": "Seçilen her modelin kapasitesini, ölçüsünü, malzeme bileşenlerini ve ambalaj yapılandırmasını sorun.",
        "Order Coordination": "Sipariş koordinasyonu",
        "One B2B inquiry process for product selection, quotation, sampling, quality checks and shipment.": "Ürün seçimi, teklif, numune, kalite kontrolleri ve sevkiyat için tek bir B2B talep süreci.",
        "Product FAQ": "Ürün SSS",
        "Wholesale Buying Questions": "Toptan satın alma soruları",
        "Contact XUYI with model number, quantity and destination.": "Model numarası, miktar ve teslimat bilgileriyle XUYI'ye ulaşın.",
        "Can you customize bottle colors and logos?": "Şişe renklerini ve logolarını özelleştirebilir misiniz?",
        "We can review logo artwork, colors and packaging for each selected model. Available decoration methods and order requirements are confirmed during quotation.": "Seçilen her model için logo tasarımını, renkleri ve ambalajı inceleyebiliriz. Dekorasyon yöntemi ve sipariş gereksinimleri teklif aşamasında doğrulanır.",
        "What is your MOQ for wholesale orders?": "Toptan siparişler için MOQ nedir?",
        "Minimum order quantity depends on bottle model, stock availability and customization. Send us the products and estimated volume to get an accurate answer.": "Minimum sipariş miktarı model, stok durumu ve özelleştirmeye bağlıdır. Kesin yanıt için ürünleri ve tahmini hacmi gönderin.",
        "Do you offer samples before bulk production?": "Toplu üretimden önce numune sunuyor musunuz?",
        "Sample availability, lead time and cost are confirmed according to the product and destination. Please include your model number and required custom work.": "Numune bulunabilirliği, süresi ve maliyeti ürüne ve teslimata göre doğrulanır. Model numarasını ve gereken özel çalışmayı belirtin.",
        "Which bottle materials can you supply?": "Hangi şişe malzemelerini tedarik edebilirsiniz?",
        "PC, Tritan, PP and PETG options are available according to customer requirements. Ask about BPA-free options for a selected model and request documentation for your destination market.": "Müşteri gereksinimlerine göre PC, Tritan, PP ve PETG seçenekleri bulunur. Seçilen model için BPA içermeyen seçenekleri sorun ve hedef pazar belgelerini isteyin.",
        "Do you have your own factory?": "Kendi fabrikanız var mı?",
        "XUYI operates its own manufacturing facility and may coordinate production through selected partner facilities for some products. We confirm project requirements and applicable quality controls.": "XUYI kendi üretim tesisini işletir; bazı ürünlerde seçilmiş ortak tesislerle üretimi koordine edebilir. Proje gereksinimlerini ve uygulanabilir kalite kontrollerini doğrularız.",
        "How long does production and shipping take?": "Üretim ve sevkiyat ne kadar sürer?",
        "Production and shipping timelines depend on model, order quantity, materials, custom artwork and destination. We provide an order-specific timeline after reviewing requirements.": "Üretim ve sevkiyat süreleri model, sipariş miktarı, malzemeler, özel tasarım ve teslimata bağlıdır. Gereksinimleri inceledikten sonra siparişe özel takvim sunarız.",
    },
}


CATEGORIES = {
    "spray-water-bottles": {
        "en_title": "Spray Water Bottles",
        "en_description": "Spray water bottles for promotional, outdoor and everyday drinkware projects. Confirm nozzle, trigger and materials by model.",
        "locales": {
            "es": {
                "title": "Botellas pulverizadoras al por mayor | Fabricante OEM XUYI",
                "description": "Botellas de agua pulverizadoras para compras B2B, promociones, exterior y uso diario. Consulte la boquilla, el gatillo y los materiales por modelo.",
                "heading": "Botellas de agua pulverizadoras OEM para mayoristas",
                "intro": "Botellas de agua pulverizadoras para promociones, exterior y uso diario. Confirme la boquilla, el gatillo y los materiales de cada modelo; consulte especificaciones, colores y opciones de cotización al por mayor.",
                "steps": [
                    ("Revisar el conjunto pulverizador", "Confirme la boquilla, la acción del gatillo, el patrón de pulverización y los componentes incluidos del modelo exacto."),
                    ("Revisar sellos y limpieza", "Compruebe los sellos, los tubos internos y el acceso para la limpieza; solicite una muestra antes de afirmar que no hay fugas."),
                    ("Confirmar marca y embalaje", "Verifique el área de decoración, las piezas de repuesto, la cantidad por cartón y el embalaje minorista del SKU."),
                ],
            },
            "pt": {
                "title": "Garrafas spray no atacado | Fabricante OEM XUYI",
                "description": "Garrafas de água spray para compras B2B, promoções, atividades ao ar livre e uso diário. Confirme bico, gatilho e materiais por modelo.",
                "heading": "Garrafas de água spray OEM para atacado",
                "intro": "Garrafas de água spray para promoções, atividades ao ar livre e uso diário. Confirme bico, gatilho e materiais de cada modelo; consulte especificações, cores e opções de cotação para atacado.",
                "steps": [
                    ("Verifique o conjunto spray", "Confirme o bico, o acionamento do gatilho, o padrão de spray e os componentes incluídos no modelo exato."),
                    ("Revise vedação e limpeza", "Verifique vedações, tubos internos e acesso para limpeza; peça uma amostra antes de fazer afirmações sobre vazamentos."),
                    ("Confirme marca e embalagem", "Verifique a área de decoração, peças de reposição, quantidade por caixa e embalagem de varejo do SKU."),
                ],
            },
            "ru": {
                "title": "Бутылки-распылители оптом | Производитель XUYI",
                "description": "Бутылки-распылители для B2B-проектов, промоакций, отдыха и повседневного использования. Уточняйте насадку, курок и материалы по модели.",
                "heading": "Бутылки-распылители OEM для оптовых покупателей",
                "intro": "Бутылки-распылители для промоакций, отдыха и повседневного использования. Уточняйте насадку, курок и материалы каждой модели; запрашивайте характеристики, цвета и оптовый расчёт.",
                "steps": [
                    ("Проверьте распылительный узел", "Уточните насадку, работу курка, форму распыления и комплектацию конкретной модели."),
                    ("Проверьте уплотнения и очистку", "Проверьте уплотнения, внутренние трубки и доступ для очистки; запросите образец до заявлений о герметичности."),
                    ("Подтвердите брендирование и упаковку", "Уточните зону декорирования, запасные детали, количество в коробке и розничную упаковку SKU."),
                ],
            },
            "tr": {
                "title": "Sprey su şişeleri toptan | XUYI OEM üreticisi",
                "description": "Promosyon, dış mekân ve günlük kullanım projeleri için sprey su şişeleri. Model bazında püskürtme başlığını, tetiği ve malzemeleri doğrulayın.",
                "heading": "Toptan OEM sprey su şişeleri",
                "intro": "Promosyon, dış mekân ve günlük kullanım için sprey su şişeleri. Her modelin başlığını, tetiğini ve malzemelerini doğrulayın; teknik özellikleri, renkleri ve toptan teklif seçeneklerini sorun.",
                "steps": [
                    ("Sprey düzeneğini kontrol edin", "Kesin model için püskürtme başlığını, tetik hareketini, püskürtme şeklini ve dahil bileşenleri doğrulayın."),
                    ("Contaları ve temizliği inceleyin", "Kapak contalarını, iç tüpleri ve temizlik erişimini kontrol edin; sızdırmazlık iddiasından önce numune isteyin."),
                    ("Markalama ve ambalajı doğrulayın", "Seçilen SKU için baskı alanını, yedek parçaları, koli adedini ve perakende ambalajını doğrulayın."),
                ],
            },
        },
    },
    "two-way-drinking-cups": {
        "en_title": "Two-Way Drinking Cups",
        "en_description": "Dual-mode drinking cups for travel, retail and promotional collections. Confirm lid components and materials by exact model.",
        "locales": {
            "es": {
                "title": "Vasos de doble modo al por mayor | Fabricante OEM XUYI",
                "description": "Vasos de doble modo para beber en viajes, retail y promociones. Confirme los componentes de la tapa y los materiales por modelo exacto.",
                "heading": "Vasos de doble modo para beber | Fabricante OEM",
                "intro": "Vasos de doble modo para viajes, retail y promociones. Confirme los componentes de la tapa y los materiales de cada modelo; consulte especificaciones, colores y cotizaciones para compras B2B.",
                "steps": [
                    ("Verificar los dos modos de bebida", "Confirme las dos opciones de consumo y el conjunto de tapa suministrado con el modelo exacto."),
                    ("Revisar el sellado y la limpieza", "Compruebe las piezas desmontables, los sellos y el acceso para la limpieza; pruebe una muestra antes de afirmar que es estanco."),
                    ("Confirmar materiales y rendimiento", "Solicite los materiales exactos del cuerpo y la tapa, además de cualquier evidencia de rendimiento térmico relevante."),
                ],
            },
            "pt": {
                "title": "Copos de duas formas de beber no atacado | XUYI OEM",
                "description": "Copos de duas formas de beber para viagem, varejo e promoções. Confirme os componentes da tampa e os materiais pelo modelo exato.",
                "heading": "Copos de duas formas de beber OEM para atacado",
                "intro": "Copos de duas formas de beber para viagem, varejo e promoções. Confirme os componentes da tampa e os materiais de cada modelo; consulte especificações, cores e cotações para compras B2B.",
                "steps": [
                    ("Verifique as duas formas de beber", "Confirme as duas opções de consumo e o conjunto de tampa fornecido com o modelo exato."),
                    ("Revise vedação e limpeza", "Verifique peças removíveis, vedações e acesso para limpeza; teste uma amostra antes de fazer afirmações de estanqueidade."),
                    ("Confirme materiais e desempenho", "Solicite os materiais exatos do corpo e da tampa e qualquer evidência relevante de desempenho térmico."),
                ],
            },
            "ru": {
                "title": "Двухрежимные питьевые стаканы оптом | XUYI",
                "description": "Двухрежимные стаканы для поездок, розничных и промо-наборов. Уточняйте компоненты крышки и материалы по точной модели.",
                "heading": "Двухрежимные питьевые стаканы OEM для опта",
                "intro": "Двухрежимные стаканы для поездок, розничных и промо-наборов. Уточняйте компоненты крышки и материалы каждой модели; запрашивайте характеристики, цвета и расчёт для B2B-закупки.",
                "steps": [
                    ("Проверьте оба режима питья", "Уточните оба варианта питья и комплектацию крышки конкретной модели."),
                    ("Проверьте герметичность и очистку", "Проверьте съёмные детали, уплотнения и доступ для очистки; протестируйте образец до заявлений о герметичности."),
                    ("Подтвердите материалы и свойства", "Запросите точные материалы корпуса и крышки, а также имеющиеся подтверждения термических свойств."),
                ],
            },
            "tr": {
                "title": "Çift kullanımlı içme bardakları toptan | XUYI OEM",
                "description": "Seyahat, perakende ve promosyon koleksiyonları için çift kullanımlı içme bardakları. Kapak bileşenlerini ve malzemeleri kesin model bazında doğrulayın.",
                "heading": "Toptan OEM çift kullanımlı içme bardakları",
                "intro": "Seyahat, perakende ve promosyon koleksiyonları için çift kullanımlı içme bardakları. Her modelin kapak bileşenlerini ve malzemelerini doğrulayın; özellikleri, renkleri ve B2B teklif seçeneklerini sorun.",
                "steps": [
                    ("İki içme modunu doğrulayın", "Kesin modelle birlikte verilen iki içme seçeneğini ve kapak düzeneğini doğrulayın."),
                    ("Sızdırmazlık ve temizliği inceleyin", "Çıkarılabilir parçaları, contaları ve temizlik erişimini kontrol edin; sızdırmazlık iddiasından önce numune test edin."),
                    ("Malzeme ve performansı doğrulayın", "Gövde ve kapak malzemelerini, ayrıca ilgili ısıl performans kanıtlarını isteyin."),
                ],
            },
        },
    },
    "titanium-vacuum-cups": {
        "en_title": "Titanium Vacuum Cups",
        "en_description": "Titanium vacuum cups for insulated drinkware sourcing. Verify grade, purity, vacuum construction and test documents for each SKU.",
        "locales": {
            "es": {
                "title": "Vasos de vacío de titanio al por mayor | XUYI",
                "description": "Vasos de vacío de titanio para compras de drinkware térmico. Verifique el grado, la pureza, la construcción de vacío y los documentos de prueba de cada SKU.",
                "heading": "Vasos térmicos de titanio para compradores B2B",
                "intro": "Vasos de vacío de titanio para compras de drinkware térmico. Verifique el grado, la pureza, la construcción de vacío y los documentos de prueba de cada SKU; solicite colores y cotización OEM.",
                "steps": [
                    ("Verificar el grado del titanio", "Solicite documentos del grado y la composición del SKU exacto; no se base solo en una afirmación de pureza de la serie."),
                    ("Comprobar la construcción de vacío", "Confirme la capacidad, la estructura de vacío y el método de prueba térmica del modelo seleccionado."),
                    ("Revisar el acabado y el embalaje", "Apruebe el acabado, los componentes de la tapa, el embalaje protector y los detalles de la caja mediante una muestra."),
                ],
            },
            "pt": {
                "title": "Copos a vácuo de titânio no atacado | XUYI",
                "description": "Copos a vácuo de titânio para compras de recipientes térmicos. Verifique grau, pureza, construção a vácuo e documentos de teste de cada SKU.",
                "heading": "Copos a vácuo de titânio para compradores B2B",
                "intro": "Copos a vácuo de titânio para compras de recipientes térmicos. Verifique grau, pureza, construção a vácuo e documentos de teste de cada SKU; solicite cores e cotação OEM.",
                "steps": [
                    ("Verifique o grau do titânio", "Solicite documentos do grau e da composição do SKU exato; não dependa apenas de uma afirmação de pureza da série."),
                    ("Confira a construção a vácuo", "Confirme a capacidade, a estrutura a vácuo e o método de teste térmico do modelo selecionado."),
                    ("Revise acabamento e embalagem", "Aprove o acabamento, os componentes da tampa, a embalagem protetora e os detalhes da caixa com base em uma amostra."),
                ],
            },
            "ru": {
                "title": "Титановые вакуумные стаканы оптом | XUYI",
                "description": "Титановые вакуумные стаканы для закупки термопосуды. Проверяйте марку, чистоту, вакуумную конструкцию и документы испытаний каждого SKU.",
                "heading": "Титановые вакуумные стаканы для B2B-покупателей",
                "intro": "Титановые вакуумные стаканы для закупки термопосуды. Проверяйте марку, чистоту, вакуумную конструкцию и документы испытаний каждого SKU; запрашивайте цвета и OEM-расчёт.",
                "steps": [
                    ("Проверьте марку титана", "Запросите документы о марке и составе точного SKU; не полагайтесь только на заявление о чистоте серии."),
                    ("Проверьте вакуумную конструкцию", "Уточните объём, вакуумную конструкцию и метод термических испытаний выбранной модели."),
                    ("Проверьте отделку и упаковку", "Согласуйте отделку, компоненты крышки, защитную упаковку и детали коробки по образцу."),
                ],
            },
            "tr": {
                "title": "Titanyum vakumlu bardaklar toptan | XUYI",
                "description": "Yalıtımlı içecek gereçleri tedariki için titanyum vakumlu bardaklar. Her SKU için kalite sınıfını, saflığı, vakum yapısını ve test belgelerini doğrulayın.",
                "heading": "B2B alıcılar için titanyum vakumlu bardaklar",
                "intro": "Yalıtımlı içecek gereçleri tedariki için titanyum vakumlu bardaklar. Her SKU'nun kalite sınıfını, saflığını, vakum yapısını ve test belgelerini doğrulayın; renkleri ve OEM teklifini sorun.",
                "steps": [
                    ("Titanyum sınıfını doğrulayın", "Kesin SKU için kalite sınıfı ve bileşim belgelerini isteyin; yalnızca seri saflık beyanına güvenmeyin."),
                    ("Vakum yapısını kontrol edin", "Seçilen modelin kapasitesini, vakum yapısını ve ısıl test yöntemini doğrulayın."),
                    ("Yüzey ve ambalajı inceleyin", "Yüzeyi, kapak bileşenlerini, koruyucu ambalajı ve koli ayrıntılarını numune üzerinden onaylayın."),
                ],
            },
        },
    },
}


def _replace_text_nodes(markup: str, replacements: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        raw = match.group(1)
        value = html.unescape(raw).strip()
        target = replacements.get(value)
        if not target:
            return match.group(0)
        leading = raw[: len(raw) - len(raw.lstrip())]
        trailing = raw[len(raw.rstrip()) :]
        return ">" + leading + html.escape(target) + trailing + "<"

    return re.sub(r">([^<>]+)<", replace, markup)


def translation_for(route: str, locale: str, source_body: str) -> dict[str, str] | None:
    if locale not in COMMON:
        return None
    slug = route.strip("/").split("/")[-1]
    category = CATEGORIES.get(slug)
    if not category:
        return None
    copy = category["locales"].get(locale)
    if not copy:
        return None

    replacements = dict(COMMON[locale])
    replacements.update({
        "XUYI · PLASTIC DRINKWARE": {
            "es": "XUYI · DRINKWARE DE PLÁSTICO",
            "pt": "XUYI · RECIPIENTES PLÁSTICOS",
            "ru": "XUYI · ПЛАСТИКОВАЯ ПОСУДА",
            "tr": "XUYI · PLASTİK İÇECEK GEREÇLERİ",
        }[locale],
        "/" + " Products / " + category["en_title"]: "/ " + COMMON[locale]["Products"] + " / " + COMMON[locale].get(category["en_title"], category["en_title"]),
    })
    for english, translated in zip(
        (
            "Check the Spray Assembly",
            "Confirm the nozzle, trigger action, spray pattern and included components for the exact model.",
            "Review Seals and Cleaning",
            "Check cap seals, internal tubes and cleaning access; request a sample before making leakage claims.",
            "Confirm Branding and Packing",
            "Verify decoration area, spare parts, carton quantity and retail packaging for the selected SKU.",
        ),
        copy["steps"] if slug == "spray-water-bottles" else (),
    ):
        replacements[english] = translated
    if slug == "two-way-drinking-cups":
        replacements.update({
            "Verify Both Drinking Modes": copy["steps"][0][0],
            "Confirm the two drinking options and the lid assembly supplied with the exact model.": copy["steps"][0][1],
            "Review Seal and Cleaning": copy["steps"][1][0],
            "Check removable parts, seals and cleaning access; test a sample before making leak-resistance claims.": copy["steps"][1][1],
            "Confirm Materials and Performance": copy["steps"][2][0],
            "Request the exact body/lid material details and any relevant thermal-performance evidence.": copy["steps"][2][1],
        })
    elif slug == "titanium-vacuum-cups":
        replacements.update({
            "Verify Titanium Grade": copy["steps"][0][0],
            "Request grade and composition documents for the exact SKU; do not rely on a series-level purity statement alone.": copy["steps"][0][1],
            "Check Vacuum Construction": copy["steps"][1][0],
            "Confirm capacity, vacuum structure and the thermal test method for the selected model.": copy["steps"][1][1],
            "Review Finish and Packing": copy["steps"][2][0],
            "Approve surface finish, lid components, protective packaging and carton details against a sample.": copy["steps"][2][1],
        })

    replacements[category["en_title"]] = COMMON[locale].get(category["en_title"], category["en_title"])
    replacements[category["en_description"] + " Explore model-specific specifications, colors and wholesale quotation options."] = copy["intro"]
    body = _replace_text_nodes(source_body, replacements)

    body = re.sub(
        r"(<section class=\"page-intro\"[\s\S]*?<h1\b[^>]*>).*?(</h1>)",
        lambda match: match.group(1) + html.escape(copy["heading"]) + match.group(2),
        body,
        count=1,
        flags=re.I,
    )
    body = body.replace(
        'aria-label="Search bottles"',
        'aria-label="' + html.escape({
            "es": "Buscar botellas",
            "pt": "Pesquisar garrafas",
            "ru": "Поиск бутылок",
            "tr": "Şişe ara",
        }[locale], quote=True) + '"',
    )
    body = body.replace(
        'placeholder="Search model, capacity or bottle type…"',
        'placeholder="' + html.escape({
            "es": "Buscar modelo, capacidad o tipo de botella…",
            "pt": "Pesquisar modelo, capacidade ou tipo de garrafa…",
            "ru": "Поиск модели, объёма или типа бутылки…",
            "tr": "Model, kapasite veya şişe türü ara…",
        }[locale], quote=True) + '"',
    )
    return {
        "title": copy["title"],
        "description": copy["description"],
        "mainHtml": body,
    }
