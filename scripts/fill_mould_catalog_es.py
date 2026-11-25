"""Fill the reviewed Spanish baseline for every public mould family."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "data" / "mould-catalog.json"
translations = {
    "mineral-water-closure-cap-molds": ("Molde de tapón para agua y bebidas", "Moldes de precisión para cierres de agua mineral, bebidas carbonatadas y zumos.", "Revisión de cuello, resina, cavidades, refrigeración y máquina para cierres de bebidas."),
    "oil-bottle-cap-mould": ("Molde de tapón para aceite comestible", "Soluciones con anilla y precinto para botellas de aceite de oliva, girasol y cocina.", "La geometría del vertedor, el sellado, la resina y la máquina se revisan juntos."),
    "engine-oil-cap-mould": ("Molde de tapón para aceite de motor", "Cierres resistentes para lubricantes de automoción y envases industriales.", "El proyecto se define por el dibujo, la resistencia química, el par de aplicación y la máquina."),
    "food-packaging-cap-mould": ("Molde de tapón para envases alimentarios", "Moldes para cierres roscados y a presión de salsas, lácteos y alimentos secos.", "La seguridad alimentaria, el sellado, la resina y la producción objetivo se documentan antes de fabricar."),
    "medical-cap-mould": ("Molde de tapón médico", "Cierres de precisión para frascos farmacéuticos, jarabes y envases de diagnóstico.", "La geometría funcional, la limpieza, la resina y la evidencia de inspección forman parte de la revisión."),
    "flip-top-caps-mould": ("Molde de tapón cosmético flip-top", "Moldes con bisagra viva para champú, acondicionador y cuidado personal.", "La bisagra, el encaje, el orificio, el acabado y el objetivo de ciclos se revisan con la muestra."),
    "personal-care-cap-mould": ("Molde de tapón para cuidado personal", "Moldes para cierres disc-top, tubos y lociones con orificios personalizados.", "El dispensado, el acabado, la resina y el sellado se ajustan al envase y a la producción."),
    "functional-cap-mould": ("Molde de tapón funcional combinado", "Mecanismos de seguridad infantil, apertura fácil y precinto en una misma familia.", "La interacción, el montaje, la resina, la evidencia de apertura y las pruebas se revisan antes del acero."),
    "plastic-handle-cap-mould": ("Molde de asa de plástico", "Asas ergonómicas para botellas PET de 5–20 litros, aceite y bidones químicos.", "La interfaz con la botella, la carga, el agarre, la resina y la máquina se confirman en el informe."),
}
data = json.loads(path.read_text(encoding="utf-8"))
for row in data.get("categories", []):
    item = translations.get(row.get("slug"))
    if not item:
        continue
    title, description, detail = item
    row.update({
        "titleEs": title,
        "navTitleEs": title,
        "descriptionEs": description,
        "shortEs": description,
        "detailEs": detail,
        "metaEs": "Revisión técnica · Producción repetible",
    })
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
