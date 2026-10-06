# -*- coding: utf-8 -*-
"""
Diccionario de datos del dataset de entrenamiento v3 (envio a la catedra).

Entrada : Datasets_Modelo/dataset_entrenamiento_v3.parquet · Modelo/resultados/senal_univariada_v3.csv
Salida  : Envio-Profesores/3-Diccionario-de-Datos-v3.xlsx
Las reglas de nulos y transformaciones replican Modelo/construir_dataset_modelo.py (pasos 8 y 9).
"""
import os, sys
import numpy as np, pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
MOD = os.path.join(BASE, "..", "Modelo", "resultados")
ds = pd.read_parquet(os.path.join(ROOT, "Datasets_Modelo", "dataset_entrenamiento_v3.parquet"))
desc = pd.read_csv(os.path.join(ROOT, "Datasets_Modelo", "diccionario_features_v3.csv")).set_index("columna")["descripcion"]
sen = pd.read_csv(os.path.join(MOD, "senal_univariada_v3.csv")).set_index("feature")
imp = pd.read_csv(os.path.join(MOD, "importancia_permutacion_v3.csv"), index_col=0)["delta_pr_auc"]

IDS = ["fecha_mes", "id_tienda", "id_producto"]
CAT = ["categoria", "subcategoria", "region", "formato", "proveedor"]
NUM = [c for c in ds.columns if c not in IDS + CAT + ["costo_imputado", "target_cob12_t3", "split"]]
assert (ds["fecha_mes"].min(), ds["fecha_mes"].max()) == (pd.Timestamp("2022-03-01"), pd.Timestamp("2026-05-01"))
assert len(NUM) == 55 and len(NUM) + len(CAT) == 60

# ------------------------------------------------------------------ grupos (los 8 de la presentacion)
GRUPOS = {
 "Demanda e historia": ["unidades_vendidas", "u3_suma", "u6_suma", "u12_prom", "cv_u12", "tendencia_u3_vs_u12", "meses_con_venta_12",
                        "meses_sin_venta", "sin_venta_12m", "u_lag1", "u_lag2", "u12_max", "antig_posicion_meses", "historia_corta"],
 "Stock": ["stock_disponible", "var_stock_3m", "cobertura", "cobertura_3m_antes", "var_cobertura_3m"],
 "SKU en la cadena": ["stock_sku_cadena", "cobertura_sku_cadena", "tiendas_con_stock_sku", "tiendas_cob12_sku", "stock_deposito_sku",
                      "cobertura_deposito_sku", "tendencia_sku_cadena", "stock_vs_prom_sku"],
 "Contexto de tienda": ["tendencia_tienda", "tendencia_categoria_tienda", "peso_posicion_en_tienda", "pct_pos_cob12_tienda",
                        "cumplimiento_ppto_3m", "skus_en_tienda"],
 "Abastecimiento": ["uds_oc_recibidas_3m", "uds_oc_pendientes", "uds_oc_recibidas_12m", "n_oc_recibidas_12m", "meses_desde_ultima_oc",
                    "uds_transf_recibidas_3m", "uds_transf_enviadas_3m", "uds_transf_recibidas_12m", "lead_time_dias", "pedido_minimo_unidades"],
 "Acciones comerciales": ["liquidacion_activa", "descuento_liquidacion_activa", "liquidaciones_12m", "liquidaciones_sku_cadena_12m",
                          "promos_activas_categoria", "descuento_promo_max", "promos_categoria_12m"],
 "Producto": ["precio_rel_subcategoria", "antig_sku_meses", "categoria", "subcategoria", "proveedor"],
 "Tienda y calendario": ["m2_venta", "region", "formato", "mes_del_anio", "eventos_en_horizonte"]}
GRUPO_DE = {c: g for g, cs in GRUPOS.items() for c in cs}
assert sorted(GRUPO_DE) == sorted(NUM + CAT)
PARA_QUE = {
 "Demanda e historia": ("Ventas", "Mide cuánto rota la posición: si se vende poco, el stock se acumula."),
 "Stock": ("Stock y ventas", "Muestra si la cobertura viene subiendo hacia los 12 meses."),
 "SKU en la cadena": ("Stock de tiendas y depósito", "Muestra si el exceso es del producto en toda la cadena, no de una sola tienda."),
 "Contexto de tienda": ("Ventas, stock, presupuesto", "Distingue si el problema es del producto o de la tienda."),
 "Abastecimiento": ("Órdenes de compra, transferencias, proveedores", "Muestra cuánto entró y cuánto está por llegar: más compra, más sobrestock."),
 "Acciones comerciales": ("Liquidaciones, promociones", "Muestra si ya se intentó vender la posición con liquidaciones o promociones."),
 "Producto": ("Catálogo", "Describe el producto y su proveedor, sobre el que Compras puede actuar."),
 "Tienda y calendario": ("Tiendas y fecha", "Tipo de tienda y época del año: la venta cambia con la estacionalidad.")}

V, S, D, C, O, T, L, P, PR, TI, PRE = ("Ventas_SKU_tienda_mensual", "Stock_SKU_tienda_mensual", "Stock_Deposito_Central",
    "Productos_catalogo", "Ordenes_Compra", "Transferencias_Stock", "Liquidaciones", "Promociones_Comerciales", "Proveedores",
    "Tiendas", "Presupuesto_Ventas_Tienda_Categoria")
FUENTE = {
 "fecha_mes": S, "id_tienda": S, "id_producto": S,
 "unidades_vendidas": V, "u3_suma": V, "u6_suma": V, "u12_prom": V, "cv_u12": V, "tendencia_u3_vs_u12": V, "meses_con_venta_12": V,
 "meses_sin_venta": V, "sin_venta_12m": V, "u_lag1": V, "u_lag2": V, "u12_max": V, "antig_posicion_meses": f"{V} + {S}", "historia_corta": f"{V} + {S}",
 "stock_disponible": S, "var_stock_3m": S, "cobertura": f"{S} + {V}", "cobertura_3m_antes": f"{S} + {V}", "var_cobertura_3m": f"{S} + {V}",
 "stock_sku_cadena": S, "cobertura_sku_cadena": f"{S} + {V}", "tiendas_con_stock_sku": S, "tiendas_cob12_sku": f"{S} + {V}",
 "stock_deposito_sku": D, "cobertura_deposito_sku": f"{D} + {V}", "tendencia_sku_cadena": V, "stock_vs_prom_sku": S,
 "tendencia_tienda": V, "tendencia_categoria_tienda": f"{V} + {C}", "peso_posicion_en_tienda": V, "pct_pos_cob12_tienda": f"{S} + {V}",
 "cumplimiento_ppto_3m": f"{PRE} + {V}", "skus_en_tienda": S,
 "uds_oc_recibidas_3m": O, "uds_oc_pendientes": O, "uds_oc_recibidas_12m": O, "n_oc_recibidas_12m": O, "meses_desde_ultima_oc": O,
 "uds_transf_recibidas_3m": T, "uds_transf_enviadas_3m": T, "uds_transf_recibidas_12m": T, "lead_time_dias": PR, "pedido_minimo_unidades": PR,
 "liquidacion_activa": L, "descuento_liquidacion_activa": L, "liquidaciones_12m": L, "liquidaciones_sku_cadena_12m": L,
 "promos_activas_categoria": P, "descuento_promo_max": P, "promos_categoria_12m": P,
 "precio_rel_subcategoria": C, "antig_sku_meses": C, "categoria": C, "subcategoria": C, "proveedor": C,
 "m2_venta": TI, "region": TI, "formato": TI, "mes_del_anio": "Fecha de corte", "eventos_en_horizonte": "Fecha de corte (eventos fijos jun · nov · dic)",
 "costo_imputado": f"{C} + {O}", "target_cob12_t3": f"{S} + {V} + {C} (en t+3)", "split": "Fecha de corte"}
UNIDAD = {
 "unidades_vendidas": "unidades", "u3_suma": "unidades", "u6_suma": "unidades", "u12_prom": "unidades/mes", "cv_u12": "ratio",
 "tendencia_u3_vs_u12": "ratio", "meses_con_venta_12": "meses (0-12)", "meses_sin_venta": "meses", "sin_venta_12m": "0/1",
 "u_lag1": "unidades", "u_lag2": "unidades", "u12_max": "unidades", "antig_posicion_meses": "meses", "historia_corta": "0/1",
 "stock_disponible": "unidades", "var_stock_3m": "unidades", "cobertura": "meses", "cobertura_3m_antes": "meses", "var_cobertura_3m": "meses",
 "stock_sku_cadena": "unidades", "cobertura_sku_cadena": "meses", "tiendas_con_stock_sku": "tiendas", "tiendas_cob12_sku": "tiendas",
 "stock_deposito_sku": "unidades", "cobertura_deposito_sku": "meses", "tendencia_sku_cadena": "ratio", "stock_vs_prom_sku": "ratio",
 "tendencia_tienda": "ratio", "tendencia_categoria_tienda": "ratio", "peso_posicion_en_tienda": "proporción", "pct_pos_cob12_tienda": "proporción",
 "cumplimiento_ppto_3m": "ratio", "skus_en_tienda": "posiciones", "uds_oc_recibidas_3m": "unidades", "uds_oc_pendientes": "unidades",
 "uds_oc_recibidas_12m": "unidades", "n_oc_recibidas_12m": "órdenes", "meses_desde_ultima_oc": "meses", "uds_transf_recibidas_3m": "unidades",
 "uds_transf_enviadas_3m": "unidades", "uds_transf_recibidas_12m": "unidades", "lead_time_dias": "días", "pedido_minimo_unidades": "unidades",
 "liquidacion_activa": "0/1", "descuento_liquidacion_activa": "%", "liquidaciones_12m": "cantidad", "liquidaciones_sku_cadena_12m": "cantidad",
 "promos_activas_categoria": "cantidad", "descuento_promo_max": "%", "promos_categoria_12m": "cantidad", "precio_rel_subcategoria": "ratio",
 "antig_sku_meses": "meses", "m2_venta": "m²", "mes_del_anio": "1-12", "eventos_en_horizonte": "meses (0-3)", "costo_imputado": "0/1",
 "target_cob12_t3": "0/1"}
VENTANA = {
 "unidades_vendidas": "t", "u3_suma": "t-2 a t", "u6_suma": "t-5 a t", "u12_prom": "t-11 a t", "cv_u12": "t-11 a t", "tendencia_u3_vs_u12": "t-11 a t",
 "meses_con_venta_12": "t-11 a t", "meses_sin_venta": "hasta t", "sin_venta_12m": "t-11 a t", "u_lag1": "t-1", "u_lag2": "t-2", "u12_max": "t-11 a t",
 "antig_posicion_meses": "hasta t", "historia_corta": "hasta t", "var_stock_3m": "t-3 a t", "cobertura_3m_antes": "t-3", "var_cobertura_3m": "t-3 a t",
 "tendencia_sku_cadena": "t-11 a t", "tendencia_tienda": "t-11 a t", "tendencia_categoria_tienda": "t-11 a t", "peso_posicion_en_tienda": "t-11 a t",
 "cumplimiento_ppto_3m": "t-2 a t", "uds_oc_recibidas_3m": "t-2 a t", "uds_oc_pendientes": "al cierre de t", "uds_oc_recibidas_12m": "t-11 a t",
 "n_oc_recibidas_12m": "t-11 a t", "meses_desde_ultima_oc": "hasta t", "uds_transf_recibidas_3m": "t-2 a t", "uds_transf_enviadas_3m": "t-2 a t",
 "uds_transf_recibidas_12m": "t-11 a t", "liquidaciones_12m": "t-11 a t", "liquidaciones_sku_cadena_12m": "t-11 a t", "promos_categoria_12m": "t-11 a t",
 "eventos_en_horizonte": "t+1 a t+3 (calendario fijo, conocido de antemano)", "target_cob12_t3": "t+3", "fecha_mes": "t", "split": "—"}
NULO = {
 "cv_u12": "Vacío si no hubo venta en 12 meses (división por 0). Transformado: 0.",
 "tendencia_u3_vs_u12": "Vacío si no hubo venta en 12 meses (división por 0). Transformado: 0.",
 "var_stock_3m": "Vacío si la posición no tiene dato en t-3 (menos de 4 meses). Transformado: 0 (sin cambio).",
 "cobertura": "inf = stock > 0 sin venta en 12 meses (marcado también en sin_venta_12m). Transformado: tope 60.",
 "cobertura_3m_antes": "Vacío sin dato en t-3: toma la cobertura actual. inf = sin venta en t-3. Transformado: tope 60.",
 "var_cobertura_3m": "Vacío sin dato en t-3 o con cobertura infinita en t o t-3. Transformado: 0.",
 "cobertura_sku_cadena": "inf = el SKU no vendió en la cadena en 12 meses. Transformado: tope 60.",
 "cobertura_deposito_sku": "inf = stock en depósito sin venta del SKU en la cadena. Transformado: mediana de train.",
 "tendencia_categoria_tienda": "Vacío si la categoría no vendió en la tienda en 12 meses. Transformado: 1 (neutro).",
 "meses_desde_ultima_oc": "Vacío si el SKU nunca recibió una OC hasta t. Transformado: 60.",
 "cumplimiento_ppto_3m": "Vacío sin presupuesto válido (> 0) en la ventana. Transformado: mediana de train.",
 "peso_posicion_en_tienda": "Transformado: vacío → 0.", "stock_vs_prom_sku": "Transformado: vacío → 1.",
 "tendencia_sku_cadena": "Transformado: vacío → 1.", "tendencia_tienda": "Transformado: vacío → 1."}

# ------------------------------------------------------------------ transformaciones (misma logica que el paso 9 del constructor)
tr = ds[ds["split"] == "train"]
fin_num = tr[NUM].replace([np.inf, -np.inf], np.nan)
sk = fin_num.skew()
BIN = ["sin_venta_12m", "liquidacion_activa", "historia_corta"]
SESG = [c for c in NUM if sk.get(c, 0) > 1 and fin_num[c].min() >= 0 and c not in BIN]
WINS = [c for c in NUM if c not in BIN + ["mes_del_anio"] and tr[c].nunique() > 15]
# control: las listas tienen que coincidir con las que registro el constructor en su log
_log = open(os.path.join(MOD, "construir_dataset_log.txt"), encoding="utf-8").read()
_lista = lambda et: [x.strip() for x in _log.split(et, 1)[1].split(chr(10), 1)[0].split(",")]
assert WINS == _lista("winsorizadas p1-p99:") and SESG == _lista("log1p aplicado a:"), "transformaciones distintas al log"
def tratamiento(c):
    if c in CAT: return f"One-hot ({ds[c].nunique()} columnas 0/1; categorías vistas en train)"
    if c == "mes_del_anio": return "Seno y coseno del mes (cíclica: diciembre queda junto a enero)"
    if c in BIN: return "Binaria: sin transformar"
    p = []
    if c in WINS: p.append("winsorización p1-p99")
    if c in SESG: p.append("log(1+x)")
    if c in ("var_stock_3m", "var_cobertura_3m"): p.append("log con signo")
    p.append("estandarización")
    return " → ".join(p) + " (parámetros ajustados solo en train)"

# ------------------------------------------------------------------ filas del diccionario
def rol(c):
    if c in IDS: return "Identificador" if c != "fecha_mes" else "Fecha de corte"
    if c in NUM: return "Variable numérica"
    if c in CAT: return "Variable categórica"
    if c == "target_cob12_t3": return "TARGET"
    if c == "split": return "Partición"
    return "Control (no es variable)"
EXTRA = {"fecha_mes": "Mes de corte t: la predicción se hace al cierre de este mes. No es variable del modelo.",
         "id_tienda": "Identificador de la tienda (T01-T28). No es variable: acompaña la predicción.",
         "id_producto": "Identificador del SKU. No es variable: acompaña la predicción.",
         "costo_imputado": "1 si el costo del SKU es el supuesto de OC × 1,2321 (H11). Marca de control pedida por el negocio (P2); no es variable porque es constante en train.",
         "target_cob12_t3": "1 si en t+3 la posición tiene stock > 0, no está discontinuada y su cobertura (stock / promedio de 12 meses de unidades netas) supera 12 meses.",
         "split": "train (mar-22 a dic-24) · validacion (abr-25 a sep-25) · test (ene-26 a may-26) · embargo (resto de 2025: no se usa para entrenar ni evaluar)."}
filas = []
for i, c in enumerate(ds.columns, 1):
    x = ds[c]
    es_num = pd.api.types.is_numeric_dtype(x)
    xf = x.replace([np.inf, -np.inf], np.nan) if es_num else x
    tipo = {"datetime64[ns]": "fecha (AAAA-MM-DD)", "object": "texto"}.get(str(x.dtype), "entero" if str(x.dtype).startswith("int") else "decimal")
    if c in ("sin_venta_12m", "liquidacion_activa", "historia_corta", "costo_imputado", "target_cob12_t3"): tipo = "binaria 0/1"
    vals = ""
    if not es_num and c != "fecha_mes":
        vc = x.value_counts()
        vals = ", ".join(vc.index[:8]) + (f" … (+{len(vc) - 8})" if len(vc) > 8 else "")
    s = sen.loc[c] if c in sen.index else None
    filas.append({
        "#": i, "Columna": c, "Rol": rol(c), "Grupo": GRUPO_DE.get(c, "—"),
        "Descripción": EXTRA.get(c, desc.get(c, "")).replace("Categoria", "Categoría").replace("Region", "Región"),
        "Fuente(s)": FUENTE.get(c, ""), "Ventana": VENTANA.get(c, "t"), "Unidad": UNIDAD.get(c, "—"), "Tipo": tipo,
        "Nulos": int(x.isna().sum()), "Nulos %": round(x.isna().mean(), 4),
        "Infinitos": int(np.isinf(x).sum()) if es_num else 0,
        "Mín": float(xf.min()) if es_num else None, "Mediana": float(xf.median()) if es_num else None,
        "Media": float(xf.mean()) if es_num else None, "Máx": float(xf.max()) if es_num else None,
        "Valores distintos": int(x.nunique()), "Valores (más frecuentes)": vals,
        "Nulos / infinitos: qué significan": NULO.get(c, "") if x.isna().any() or (es_num and np.isinf(x).any()) else "Sin nulos",
        "Tratamiento en la matriz transformada": tratamiento(c) if c in NUM + CAT else "—",
        "Señal sola (AUC train)": float(s["auc_train"]) if s is not None else None,
        "AUC validación": float(s["auc_validacion"]) if s is not None else None,
        "AUC test": float(s["auc_test"]) if s is not None else None,
        "Importancia (Δ PR-AUC)": float(imp[c]) if c in imp.index else None})
dic = pd.DataFrame(filas)

# ------------------------------------------------------------------ libro
NAVY, GOLD, LINE, MUTED = "0F172A", "FFC72C", "E2E8F0", "6E6E73"
F = lambda **k: Font(name="Arial", **k)
thin = Side(style="thin", color=LINE)
wb = Workbook()

def hoja(ws, df, anchos, fmt=None, titulo=None, nota=None):
    r0 = 1
    if titulo:
        ws.cell(1, 1, titulo).font = F(bold=True, size=14, color=NAVY)
        if nota: ws.cell(2, 1, nota).font = F(size=10, color=MUTED)
        r0 = 4
    for j, col in enumerate(df.columns, 1):
        cl = ws.cell(r0, j, col)
        cl.font = F(bold=True, color="FFFFFF", size=10); cl.fill = PatternFill("solid", fgColor=NAVY)
        cl.alignment = Alignment(wrap_text=True, vertical="center", horizontal="right" if pd.api.types.is_numeric_dtype(df[col]) else "left")
        ws.column_dimensions[get_column_letter(j)].width = anchos.get(col, 14)
    for i, row in enumerate(df.itertuples(index=False), r0 + 1):
        for j, v in enumerate(row, 1):
            if isinstance(v, float) and not np.isfinite(v): v = None
            cl = ws.cell(i, j, v)
            cl.font = F(size=10, bold=(df.columns[j - 1] == "Columna"))
            cl.alignment = Alignment(wrap_text=True, vertical="top")
            cl.border = Border(bottom=thin)
            if fmt and df.columns[j - 1] in fmt: cl.number_format = fmt[df.columns[j - 1]]
        if "Rol" in df.columns and row[df.columns.get_loc("Rol")] == "TARGET":
            for j in range(1, len(df.columns) + 1):
                ws.cell(i, j).fill = PatternFill("solid", fgColor="FFF3CC")
    ws.freeze_panes = ws.cell(r0 + 1, 3 if "Columna" in df.columns else 1)
    ws.auto_filter.ref = f"A{r0}:{get_column_letter(len(df.columns))}{r0 + len(df)}"
    ws.row_dimensions[r0].height = 32

# Léeme
ws = wb.active; ws.title = "Léeme"
ws.column_dimensions["A"].width = 30; ws.column_dimensions["B"].width = 110
pos_ = int(ds["target_cob12_t3"].sum())
_ptr = ds.loc[ds["split"] == "train", "target_cob12_t3"].mean(); peso_pos = (1 - _ptr) / _ptr
lineas = [
 ("Casa Óga · Dataset de entrenamiento v3 · Diccionario de datos", None),
 ("Grupo 1 · Factibilidad de Proyectos Data Driven (ITBA, 2C 2026)", None), ("", None),
 ("Qué se predice", "Al cierre de cada mes t, si una posición SKU-tienda va a quedar con stock inmovilizado: más de 12 meses de cobertura en t+3."),
 ("Target", "target_cob12_t3 = 1 si en t+3 la posición tiene stock > 0, no está discontinuada y stock / promedio mensual de 12 meses de unidades netas > 12."),
 ("Unidad de análisis", "Posición SKU-tienda-mes (una fila = una posición en un mes de corte)."),
 ("Universo", "Posiciones con stock > 0 en t, no discontinuadas en t, con 3 o más meses de historia y con fila observada en t+3."),
 ("Tamaño", f"{len(ds):,} filas · {ds.groupby(['id_tienda', 'id_producto']).ngroups:,} posiciones · {ds['id_producto'].nunique()} SKUs · {ds['id_tienda'].nunique()} tiendas · cortes mar-2022 a may-2026 (etiquetas hasta ago-2026)".replace(",", ".")),
 ("Positivos", f"{pos_:,} ({pos_ / len(ds):.2%})".replace(",", "X").replace(".", ",").replace("X", ".")
              + f" · balanceo sugerido: peso de la clase positiva ≈ {peso_pos:.0f} (calculado en train, sin sobremuestreo)"),
 ("Variables", "60 variables para alimentar el modelo: 55 numéricas + 5 categóricas (106 columnas tras one-hot), en 8 grupos. Todas usan solo información disponible al cierre de t (sin leakage)."),
 ("Otras columnas", "3 de identificación (fecha_mes, id_tienda, id_producto), 1 marca de control (costo_imputado), el target y la partición (split). Total 66 columnas."),
 ("Partición", "Temporal con embargo de 3 meses (= horizonte): train mar-22→dic-24 · validación abr→sep-25 · test ene→may-26. Las filas 'embargo' no se usan."),
 ("Nulos e infinitos", "Son intencionales (ratios sin denominador, posición sin historia en t-3, SKU sin OC). En el CSV el infinito aparece como 'inf'. Ver la columna 'Nulos / infinitos: qué significan'."),
 ("Datos de origen", "Datasets_Normalizados/ + criterios de limpieza del plan de mejora: dedup de claves (H1-H2), stock con piso 0 y devoluciones neteadas (H4), descuentos y presupuesto inválidos excluidos (H9), promociones inválidas excluidas (H10), costo OC × 1,2321 para 22 SKUs (H11)."),
 ("Señal y dirección", "Las columnas AUC miden cuánto separa cada variable sola al target (0,5 = nada). Son descriptivas: ninguna variable se eligió mirando el test."),
 ("", None), ("Hojas", None),
 ("Diccionario", "Las 66 columnas: rol, grupo, descripción, fuente, ventana, unidad, tipo, nulos, rango, valores, transformación y señal."),
 ("Grupos", "Los 8 grupos de variables, de qué archivos salen y para qué sirven."),
 ("Partición", "Filas, positivos y prevalencia por bloque."),
 ("Categóricas", "Valores de cada variable categórica con filas y tasa de positivos."),
 ("Excluidas", "Columnas candidatas que se evaluaron y no entran al modelo, con el motivo.")]
for i, (a, b) in enumerate(lineas, 1):
    ws.cell(i, 1, a).font = F(bold=True, size=14 if i == 1 else 10, color=NAVY if i <= 2 or b is None else "1C1C1E")
    if b:
        ws.cell(i, 2, b).font = F(size=10); ws.cell(i, 2).alignment = Alignment(wrap_text=True, vertical="top")
        ws.cell(i, 1).alignment = Alignment(vertical="top")
ws.cell(5, 1).fill = ws.cell(5, 2).fill = PatternFill("solid", fgColor="FFF3CC")

hoja(wb.create_sheet("Diccionario"), dic,
     {"#": 5, "Columna": 28, "Rol": 18, "Grupo": 20, "Descripción": 60, "Fuente(s)": 34, "Ventana": 16, "Unidad": 12, "Tipo": 14,
      "Valores (más frecuentes)": 40, "Nulos / infinitos: qué significan": 46, "Tratamiento en la matriz transformada": 46},
     {"Nulos %": "0.0%", "Mín": "#,##0.##", "Mediana": "#,##0.##", "Media": "#,##0.##", "Máx": "#,##0.##", "Nulos": "#,##0",
      "Infinitos": "#,##0", "Valores distintos": "#,##0", "Señal sola (AUC train)": "0.000", "AUC validación": "0.000", "AUC test": "0.000",
      "Importancia (Δ PR-AUC)": "0.0000"},
     "Diccionario de datos · dataset_entrenamiento_v3.csv",
     "Estadísticas sobre las 201.306 filas (sin infinitos). AUC = señal univariada (Modelo/chequeo de señal); importancia = permutación en un modelo de prueba, no es el modelo final.")

gr = pd.DataFrame([{"Grupo": g, "Variables": len(cs), "Sale de": PARA_QUE[g][0], "Para qué sirve": PARA_QUE[g][1], "Columnas": ", ".join(cs)}
                   for g, cs in GRUPOS.items()])
hoja(wb.create_sheet("Grupos"), gr, {"Grupo": 22, "Variables": 10, "Sale de": 34, "Para qué sirve": 60, "Columnas": 90})

sp = ds.groupby("split").agg(Desde=("fecha_mes", "min"), Hasta=("fecha_mes", "max"), Filas=("target_cob12_t3", "size"),
                             Positivos=("target_cob12_t3", "sum")).loc[["train", "validacion", "test", "embargo"]].reset_index()
sp["Desde"] = sp["Desde"].dt.strftime("%Y-%m"); sp["Hasta"] = sp["Hasta"].dt.strftime("%Y-%m")
sp["Prevalencia"] = sp["Positivos"] / sp["Filas"]
sp["Uso"] = ["Entrenar", "Ajustar umbral y modelo", "Evaluación final (no se mira hasta el final)", "Separa bloques: no se usa"]
sp = sp.rename(columns={"split": "Bloque"})
hoja(wb.create_sheet("Partición"), sp, {"Bloque": 14, "Uso": 44}, {"Filas": "#,##0", "Positivos": "#,##0", "Prevalencia": "0.00%"})

cats = []
for c in CAT:
    g = ds.groupby(c)["target_cob12_t3"].agg(["size", "mean"]).sort_values("size", ascending=False)
    for v, row in g.iterrows():
        cats.append({"Variable": c, "Valor": v, "Filas": int(row["size"]), "% de filas": row["size"] / len(ds), "Tasa de positivos": row["mean"]})
hoja(wb.create_sheet("Categóricas"), pd.DataFrame(cats), {"Variable": 16, "Valor": 30},
     {"Filas": "#,##0", "% de filas": "0.0%", "Tasa de positivos": "0.00%"})

exc = pd.DataFrame([
 ("Presupuesto de los meses siguientes", "Presupuesto_Ventas_Tienda_Categoria", "Habla del futuro", "Es un plan que se actualiza con la venta real: adelantaría la respuesta (leakage). Solo entra el cumplimiento de los últimos 3 meses."),
 ("Estado actual del catálogo (activo / discontinuado)", "Productos_catalogo", "Habla del futuro", "Es la foto de hoy: marcaría como discontinuados productos que ese mes seguían activos. Se usa solo para excluir del universo a las discontinuadas en t."),
 ("precio_lista, margen_lista, capital_inmovilizado_pos, precio_medio_12m, venta3_suma, descuento_implicito_12m", "Productos_catalogo / Ventas", "Dato no confiable", "Precio y costo del catálogo son los de hoy (P10): aplicados a meses pasados son anacrónicos. Queda solo el precio relativo a la subcategoría."),
 ("stock_en_transito, transito_sobre_stock", "Stock_SKU_tienda_mensual", "Dato no confiable", "H6: campo sin definición, 9× las transferencias en curso; su señal cae de AUC 0,67 a 0,50 en 2026."),
 ("Antigüedad de la tienda", "Tiendas", "Dato no confiable", "H3: 6 tiendas registran ventas antes de su fecha de apertura. Se usa la antigüedad de la posición."),
 ("Historial de precios", "Historial_Precios_SKU", "Dato no confiable", "H8: es una reconstrucción hecha una vez para el proyecto, no un registro (P8-P10)."),
 ("Devoluciones por motivo, calendario (temporada, feriados)", "Devoluciones_SKU, Calendario", "Sin datos de 2026", "H12: ambas fuentes terminan en dic-2025. Las devoluciones ya están neteadas en la venta; los eventos fijos se derivan de la fecha."),
 ("id_tienda, id_producto", "—", "No describen la posición", "Identifican: el modelo memorizaría en lugar de aprender patrones. Quedan en la tabla para saber de quién es cada predicción."),
 ("Costo de almacenamiento, costo_imputado", "Costo_almacenamiento / Catálogo", "Constantes", "Un valor por categoría (redundante con categoría) y una marca que vale 0 en todo train.")],
 columns=["Columna(s) candidata(s)", "Fuente", "Motivo", "Detalle"])
hoja(wb.create_sheet("Excluidas"), exc, {"Columna(s) candidata(s)": 46, "Fuente": 32, "Motivo": 22, "Detalle": 90})

wb["Diccionario"].sheet_properties.tabColor = GOLD
out = os.path.join(BASE, "4-Diccionario-de-Datos-v3.xlsx")
wb.save(out)
print("OK:", out, dic.shape, "| log1p:", len(SESG), "| winsor:", len(WINS))
