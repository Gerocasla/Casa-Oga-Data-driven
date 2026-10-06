# -*- coding: utf-8 -*-
"""
Arma la carpeta de envio a la catedra (Entregable 2).

  1-Entregable-2-Consolidado.docx             lo genera armar_consolidado.py (Partes A y B en un documento)
  2-Presentacion-Final-Entregable-2.html      copia de Presentacion/Casa-Oga-Entregable-2-v4-corta-modelo.html
  3-Dataset-Modelo-v3.zip                     dataset_entrenamiento_v3.csv: target + 60 variables (+ ids, control, split)
  4-Diccionario-de-Datos-v3.xlsx              lo genera armar_diccionario.py
  5-Dashboard-Antes-vs-Despues.html           plantilla + EDA/resultados/comparativo_antes_despues.json

Orden: python ../EDA/comparativo_antes_despues.py -> armar_diccionario.py -> armar_envio.py -> armar_consolidado.py
"""
import os, sys, json, shutil
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
E2 = os.path.dirname(BASE)
ROOT = os.path.abspath(os.path.join(E2, "..", ".."))

# 1. presentacion final
shutil.copyfile(os.path.join(E2, "Presentacion", "Casa-Oga-Entregable-2-v4-corta-modelo.html"),
                os.path.join(BASE, "2-Presentacion-Final-Entregable-2.html"))

# 2. dataset en CSV comprimido (el infinito de cobertura queda escrito como "inf")
ds = pd.read_parquet(os.path.join(ROOT, "Datasets_Modelo", "dataset_entrenamiento_v3.parquet"))
ds["fecha_mes"] = ds["fecha_mes"].dt.strftime("%Y-%m-%d")
# 6 cifras significativas: mismo dato, y el zip entra como adjunto de mail (< 25 MB)
ds.to_csv(os.path.join(BASE, "3-Dataset-Modelo-v3.zip"), index=False, float_format="%.6g",
          compression={"method": "zip", "archive_name": "dataset_entrenamiento_v3.csv", "compresslevel": 9})

# 4. dashboard comparativo: una pagina, solo lo que cuenta la presentacion (diapositivas 3 y 4)
c = json.load(open(os.path.join(E2, "EDA", "resultados", "comparativo_antes_despues.json"), encoding="utf-8"))
v, s, ca, ac, pr = c["ventas"]["kpi"], c["stock"]["kpi"], c["catalogo"], c["acciones"]["kpi"], c["presupuesto"]["kpi"]
d = {"ventas": {"venta": v["venta"], "unidades": v["unidades"], "claves_dup": v["claves_dup"][0], "filas_neg": v["filas_neg"][0]},
     "stock": {"capital": s["capital"], "filas_neg": s["filas_neg"][0], "minimo": s["minimo"][0]},
     "catalogo": {"categorias": ca["kpi"]["categorias"], "sin_costo": ca["kpi"]["sin_costo"][0], "decoracion_pct": ca["kpi"]["decoracion_pct"],
                  "cat_antes": ca["cat_antes"], "cat_despues": ca["cat_despues"]},
     "acciones": {"desc_fuera": ac["liq_fuera"][0] + ac["promo_fuera"][0]},
     "presupuesto": {"invalidas": pr["ceros"][0] + pr["negativas"][0]},
     "modelo": {"prevalencia": c["modelo"]["prevalencia"], "positivos": c["modelo"]["positivos"],
                "prev_mensual": c["modelo"]["prev_mensual"]}}
html = open(os.path.join(BASE, "dashboard_comparativo_plantilla.html"), encoding="utf-8").read()
datos = json.dumps(d, ensure_ascii=False, allow_nan=False).replace("</", r"<\/")
html = html.replace("/*__DATA__*/", datos)
open(os.path.join(BASE, "5-Dashboard-Antes-vs-Despues.html"), "w", encoding="utf-8").write(html)

for f in sorted(os.listdir(BASE)):
    if f[0].isdigit(): print(f"{f:45s} {os.path.getsize(os.path.join(BASE, f)) / 1e6:6.2f} MB")
