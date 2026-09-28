# -*- coding: utf-8 -*-
"""
Construye el dataset de entrenamiento del modelo de dead stock (Entregable 2 · Parte B · Seccion 2).

Definiciones (ver Recordatorios/05-decisiones-modelo.md):
  - Unidad de analisis : SKU-tienda-mes.
  - Universo           : posiciones con stock_disponible > 0 en t, no discontinuadas en t,
                         con al menos 3 meses de historia y con fila observada en t+3
                         (con 12 meses quedaban afuera el 40% de las filas y los productos nuevos).
  - Target             : cobertura > 12 meses en t+3 (stock / promedio de 12 meses de unidades
                         netas de devoluciones), sin discontinuados.
  - Features           : solo informacion disponible al cierre del mes t (sin leakage).
  - Particion          : temporal con embargo de 3 meses (= horizonte) entre bloques.

Criterios de limpieza aplicados antes (respuestas del negocio, ronda 2):
  H1 dedup por clave, 1ra ocurrencia · H4 stock negativo -> 0, ventas negativas neteadas ·
  H9 descuentos fuera de rango excluidos · H11 costo de OC x 1,2321 para los 22 SKUs sin costo.

Salidas (carpeta Datasets_Modelo/ en la raiz del repo):
  dataset_entrenamiento_vN.parquet            -> features sin transformar + target + split
  dataset_entrenamiento_vN_transformado.parquet -> matriz lista para el modelo (fit solo en train)
  dataset_entrenamiento_vN_muestra.csv        -> 1.000 filas para inspeccion rapida
  diccionario_features_vN.csv                 -> descripcion de cada columna
Log: Entregable/Entregable 2/Modelo/resultados/construir_dataset_log.txt
"""
import os, sys
import numpy as np, pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
DATA = os.path.join(ROOT, "Datasets_Normalizados")
OUTD = os.path.join(ROOT, "Datasets_Modelo")
RES = os.path.join(BASE, "resultados")
os.makedirs(OUTD, exist_ok=True); os.makedirs(RES, exist_ok=True)
LOG = open(os.path.join(RES, "construir_dataset_log.txt"), "w", encoding="utf-8")
def P(*a):
    t = " ".join(str(x) for x in a); print(t); LOG.write(t + "\n")

K = ["fecha_mes", "id_tienda", "id_producto"]
POS = ["id_tienda", "id_producto"]
VERSION = "v3"   # v3: universo con 3+ meses de historia, sin precio/costo absolutos ni transito (ver registro)
HIST_MIN = 3     # meses de historia minima de la posicion (v1-v2: 12)
FACTOR_COSTO_OC = 1.2321   # EDA/factor_costo_oc.py — supuesto declarado

def rd(nombre, **kw):
    return pd.read_csv(os.path.join(DATA, nombre), **kw)

# ---------------------------------------------------------------- 1. carga y correccion
v_raw = rd("Ventas_SKU_tienda_mensual.csv")
s = rd("Stock_SKU_tienda_mensual.csv").drop_duplicates(K)                        # H1
cat = rd("Productos_catalogo.csv").drop_duplicates("id_producto")                # H2
tie = rd("Tiendas.csv")
prov = rd("Proveedores.csv")
oc = rd("Ordenes_Compra.csv", parse_dates=["fecha_pedido", "fecha_recepcion"])
trf = rd("Transferencias_Stock.csv", parse_dates=["fecha_envio", "fecha_recepcion"])
liq = rd("Liquidaciones.csv", parse_dates=["fecha_inicio", "fecha_fin"])
pro = rd("Promociones_Comerciales.csv", parse_dates=["fecha_inicio", "fecha_fin"])
dep = rd("Stock_Deposito_Central.csv", parse_dates=["fecha_mes"])

pos_v = v_raw[v_raw["unidades_vendidas"] >= 0].drop_duplicates(K)               # H1
neg_v = v_raw[v_raw["unidades_vendidas"] < 0]                                    # H4 neteo (P23)
v = pd.concat([pos_v, neg_v]).groupby(K, as_index=False)[["unidades_vendidas", "venta_neta"]].sum()
s["stock_disponible"] = s["stock_disponible"].clip(lower=0)                      # H4 piso 0 (P16)

# H11: costo de los 22 SKUs sin costo = costo OC ponderado x factor
oc["monto"] = oc["unidades"] * oc["costo_unitario_ars"]
c_oc = oc.groupby("id_producto").agg(m=("monto", "sum"), u=("unidades", "sum"))
c_oc = (c_oc["m"] / c_oc["u"]) * FACTOR_COSTO_OC
cat["costo_imputado"] = cat["costo_unitario"].isna().astype(int)
cat["costo_unitario"] = cat["costo_unitario"].fillna(cat["id_producto"].map(c_oc))

liq = liq[liq["descuento_pct"].between(0, 100)]                                  # H9 (P28)
pro = pro[pro["descuento_pct"].between(0, 100)]                                  # H9
pro = pro[pro["fecha_fin"] >= pro["fecha_inicio"]].drop_duplicates()            # H10

P("=" * 90); P(f"DATASET DE ENTRENAMIENTO {VERSION} — dead stock SKU-tienda-mes"); P("=" * 90)

# ---------------------------------------------------------------- 2. panel y features de demanda/stock
d = s.merge(v, on=K)
d["fecha_mes"] = pd.to_datetime(d["fecha_mes"])
d = d.sort_values(POS + ["fecha_mes"]).reset_index(drop=True)
g = d.groupby(POS, sort=False)
u = "unidades_vendidas"
roll = lambda col, w, f, mp=1: g[col].transform(lambda x: getattr(x.rolling(w, min_periods=mp), f)())

d["u3_suma"] = roll(u, 3, "sum")
d["u6_suma"] = roll(u, 6, "sum")
d["u12_prom"] = roll(u, 12, "mean")
d["u12_std"] = roll(u, 12, "std", 2)
d["meses_con_venta_12"] = g[u].transform(lambda x: (x > 0).astype(int).rolling(12, min_periods=1).sum())
d["venta12_suma"] = roll("venta_neta", 12, "sum")

# meses consecutivos sin venta hasta t
def racha_cero(x):
    out, r = [], 0
    for val in x.to_numpy():
        r = r + 1 if val <= 0 else 0
        out.append(r)
    return pd.Series(out, index=x.index)
d["meses_sin_venta"] = g[u].transform(racha_cero)

d["cobertura"] = np.where(d["u12_prom"] > 0, d["stock_disponible"] / d["u12_prom"].where(d["u12_prom"] > 0), np.inf)
d["stock_3m_antes"] = g["stock_disponible"].shift(3)
d["var_stock_3m"] = d["stock_disponible"] - d["stock_3m_antes"]

baja = pd.to_datetime(d["id_producto"].map(cat.set_index("id_producto")["fecha_baja_catalogo"]))
d["discontinuado"] = baja.notna() & (baja <= d["fecha_mes"] + pd.offsets.MonthEnd(0))
d["con_stock"] = d["stock_disponible"] > 0

# ---------------------------------------------------------------- 3. target a 3 meses
d["pos_cob12"] = d["con_stock"] & (d["cobertura"] > 12) & ~d["discontinuado"]
d["target_cob12_t3"] = g["pos_cob12"].shift(-3)
d["mes_t3"] = g["fecha_mes"].shift(-3)
valido = (d["mes_t3"] - d["fecha_mes"]).dt.days.between(85, 95)
hist12 = g.cumcount() >= HIST_MIN - 1   # (nombre historico: ya no son 12 meses)

# ---------------------------------------------------------------- 4. features de SKU en la cadena (mes t)
sku_mes = d.groupby(["fecha_mes", "id_producto"]).agg(
    stock_sku_cadena=("stock_disponible", "sum"),
    u12_sku_cadena=("u12_prom", "sum"),
    tiendas_con_stock_sku=("con_stock", "sum"),
    tiendas_cob12_sku=("pos_cob12", "sum")).reset_index()
sku_mes["cobertura_sku_cadena"] = sku_mes["stock_sku_cadena"] / sku_mes["u12_sku_cadena"].where(sku_mes["u12_sku_cadena"] > 0)
d = d.merge(sku_mes, on=["fecha_mes", "id_producto"], how="left")

dep = dep.rename(columns={"stock_disponible": "stock_deposito_sku"})
d = d.merge(dep, on=["fecha_mes", "id_producto"], how="left")
d["stock_deposito_sku"] = d["stock_deposito_sku"].fillna(0)

# ---------------------------------------------------------------- 5. features de eventos (ventanas cerradas en t)
meses = pd.DatetimeIndex(sorted(d["fecha_mes"].unique()))
fin = lambda m: m + pd.offsets.MonthEnd(0)

def ventana(df, fcol, keys, valcol, n_meses):
    """Suma valcol de eventos con fcol dentro de los n_meses que terminan en t (inclusive)."""
    e = df.dropna(subset=[fcol]).copy()
    e["m"] = e[fcol].dt.to_period("M").dt.to_timestamp()
    e = e.groupby(keys + ["m"])[valcol].sum().reset_index()
    filas = []
    for m in meses:
        ini = m - pd.DateOffset(months=n_meses - 1)
        sub = e[(e["m"] >= ini) & (e["m"] <= m)].groupby(keys)[valcol].sum().reset_index()
        sub["fecha_mes"] = m; filas.append(sub)
    return pd.concat(filas)

# OC recibidas en los ultimos 3 meses (SKU) y pendientes de recepcion al cierre de t (SKU)
oc_rec = ventana(oc, "fecha_recepcion", ["id_producto"], "unidades", 3).rename(columns={"unidades": "uds_oc_recibidas_3m"})
pend = []
for m in meses:
    f = fin(m)
    sub = oc[(oc["fecha_pedido"] <= f) & (oc["fecha_recepcion"] > f)].groupby("id_producto")["unidades"].sum().reset_index()
    sub["fecha_mes"] = m; pend.append(sub)
oc_pend = pd.concat(pend).rename(columns={"unidades": "uds_oc_pendientes"})

trf_in = ventana(trf.rename(columns={"destino": "id_tienda"}), "fecha_recepcion", ["id_tienda", "id_producto"],
                 "unidades", 3).rename(columns={"unidades": "uds_transf_recibidas_3m"})
trf_out = ventana(trf.rename(columns={"origen": "id_tienda"}), "fecha_envio", ["id_tienda", "id_producto"],
                  "unidades", 3).rename(columns={"unidades": "uds_transf_enviadas_3m"})

# liquidaciones: activa en t y cantidad iniciadas en los ultimos 12 meses (tienda o "Todas")
liq_t = liq[liq["tienda"] != "Todas"].rename(columns={"tienda": "id_tienda"})
liq_all = liq[liq["tienda"] == "Todas"]
act = []
for m in meses:
    f = fin(m)
    a = liq_t[(liq_t["fecha_inicio"] <= f) & (liq_t["fecha_fin"] >= m)][POS].drop_duplicates()
    a["fecha_mes"] = m; act.append(a)
liq_act = pd.concat(act); liq_act["liquidacion_activa"] = 1
liq_t = liq_t.assign(n=1)
liq_12 = ventana(liq_t, "fecha_inicio", POS, "n", 12).rename(columns={"n": "liquidaciones_12m"})
liq_all_act = []
for m in meses:
    f = fin(m)
    a = liq_all[(liq_all["fecha_inicio"] <= f) & (liq_all["fecha_fin"] >= m)][["id_producto"]].drop_duplicates()
    a["fecha_mes"] = m; liq_all_act.append(a)
liq_all_act = pd.concat(liq_all_act); liq_all_act["liq_todas"] = 1

# promociones activas en el mes para la categoria (canal fisico o todos)
pro_f = pro[pro["canal"].str.lower() != "online"]
pr = []
for m in meses:
    f = fin(m)
    a = pro_f[(pro_f["fecha_inicio"] <= f) & (pro_f["fecha_fin"] >= m)]
    a = a.groupby("categoria").agg(promos_activas_categoria=("id_promocion", "nunique"),
                                   descuento_promo_max=("descuento_pct", "max")).reset_index()
    a["fecha_mes"] = m; pr.append(a)
promo_mes = pd.concat(pr)

for extra, on in [(oc_rec, ["fecha_mes", "id_producto"]), (oc_pend, ["fecha_mes", "id_producto"]),
                  (trf_in, K), (trf_out, K), (liq_act, K), (liq_12, K),
                  (liq_all_act, ["fecha_mes", "id_producto"])]:
    d = d.merge(extra, on=on, how="left")
d["liquidacion_activa"] = d["liquidacion_activa"].fillna(0).astype(int) | d["liq_todas"].fillna(0).astype(int)
d = d.drop(columns="liq_todas")

# ---------------------------------------------------------------- 6. atributos de producto y tienda
cat["margen_lista"] = 1 - cat["costo_unitario"] / cat["precio_lista"]
d = d.merge(cat[["id_producto", "categoria", "subcategoria", "proveedor", "precio_lista", "costo_unitario",
                 "margen_lista", "costo_imputado", "fecha_alta_catalogo"]], on="id_producto", how="left")
d = d.merge(prov[["proveedor", "lead_time_dias", "pedido_minimo_unidades"]], on="proveedor", how="left")
d = d.merge(tie[["id_tienda", "region", "formato", "m2_venta"]], on="id_tienda", how="left")
d = d.merge(promo_mes, on=["fecha_mes", "categoria"], how="left")

alta = pd.to_datetime(d["fecha_alta_catalogo"])
d["antig_sku_meses"] = ((d["fecha_mes"].dt.year - alta.dt.year) * 12 + d["fecha_mes"].dt.month - alta.dt.month).clip(lower=0)
d["mes_del_anio"] = d["fecha_mes"].dt.month
d["capital_inmovilizado_pos"] = d["stock_disponible"] * d["costo_unitario"]
d["tendencia_u3_vs_u12"] = (d["u3_suma"] / 3) / d["u12_prom"].where(d["u12_prom"] > 0)
d["cv_u12"] = d["u12_std"] / d["u12_prom"].where(d["u12_prom"] > 0)
d["precio_medio_12m"] = d["venta12_suma"] / (d["u12_prom"] * 12).where(d["u12_prom"] > 0)
d["sin_venta_12m"] = (d["u12_prom"] <= 0).astype(int)

ceros = ["uds_oc_recibidas_3m", "uds_oc_pendientes", "uds_transf_recibidas_3m", "uds_transf_enviadas_3m",
         "liquidaciones_12m", "promos_activas_categoria", "descuento_promo_max"]
d[ceros] = d[ceros].fillna(0)

# ---------------------------------------------------------------- 6b. features agregadas en v2 (todas con informacion <= t)
d = d.sort_values(POS + ["fecha_mes"]).reset_index(drop=True)
g = d.groupby(POS, sort=False)
# trayectoria de la posicion
d["u_lag1"] = g[u].shift(1)
d["u_lag2"] = g[u].shift(2)
d["u12_max"] = g[u].transform(lambda x: x.rolling(12, min_periods=1).max())
d["venta3_suma"] = g["venta_neta"].transform(lambda x: x.rolling(3, min_periods=1).sum())
d["antig_posicion_meses"] = g.cumcount()
d["cobertura_3m_antes"] = g["cobertura"].shift(3)
d["var_cobertura_3m"] = d["cobertura"].replace(np.inf, np.nan) - d["cobertura_3m_antes"].replace(np.inf, np.nan)
d["transito_sobre_stock"] = d["stock_en_transito"] / d["stock_disponible"].where(d["stock_disponible"] > 0)
d["descuento_implicito_12m"] = 1 - d["precio_medio_12m"] / d["precio_lista"]
# peso de la posicion dentro de la tienda y comparacion con el mismo SKU en otras tiendas
tienda_mes = d.groupby(["fecha_mes", "id_tienda"]).agg(u12_tienda=("u12_prom", "sum"), u3_tienda=("u3_suma", "sum"),
                                                       skus_en_tienda=("con_stock", "sum"),
                                                       pct_pos_cob12_tienda=("pos_cob12", "mean")).reset_index()
tienda_mes["tendencia_tienda"] = (tienda_mes["u3_tienda"] / 3) / tienda_mes["u12_tienda"].where(tienda_mes["u12_tienda"] > 0)
d = d.merge(tienda_mes[["fecha_mes", "id_tienda", "u12_tienda", "skus_en_tienda", "pct_pos_cob12_tienda", "tendencia_tienda"]],
            on=["fecha_mes", "id_tienda"], how="left")
d["peso_posicion_en_tienda"] = d["u12_prom"] / d["u12_tienda"].where(d["u12_tienda"] > 0)
d["stock_vs_prom_sku"] = d["stock_disponible"] / (d["stock_sku_cadena"] / d["tiendas_con_stock_sku"]).where(d["tiendas_con_stock_sku"] > 0)
sku_tr = d.groupby(["fecha_mes", "id_producto"]).agg(u3c=("u3_suma", "sum"), u12c=("u12_prom", "sum")).reset_index()
sku_tr["tendencia_sku_cadena"] = (sku_tr["u3c"] / 3) / sku_tr["u12c"].where(sku_tr["u12c"] > 0)
d = d.merge(sku_tr[["fecha_mes", "id_producto", "tendencia_sku_cadena"]], on=["fecha_mes", "id_producto"], how="left")
d["cobertura_deposito_sku"] = d["stock_deposito_sku"] / d["u12_sku_cadena"].where(d["u12_sku_cadena"] > 0)
# tendencia de la categoria dentro de la tienda
ct = d.groupby(["fecha_mes", "id_tienda", "categoria"]).agg(u3=("u3_suma", "sum"), u12=("u12_prom", "sum")).reset_index()
ct["tendencia_categoria_tienda"] = (ct["u3"] / 3) / ct["u12"].where(ct["u12"] > 0)
d = d.merge(ct[["fecha_mes", "id_tienda", "categoria", "tendencia_categoria_tienda"]], on=["fecha_mes", "id_tienda", "categoria"], how="left")
# precio relativo dentro de la subcategoria
d["precio_rel_subcategoria"] = d["precio_lista"] / d.groupby("subcategoria")["precio_lista"].transform("median")
# abastecimiento en 12 meses y recencia de la ultima OC recibida (SKU)
oc12 = ventana(oc.assign(n=1), "fecha_recepcion", ["id_producto"], "unidades", 12).rename(columns={"unidades": "uds_oc_recibidas_12m"})
noc12 = ventana(oc.assign(n=1), "fecha_recepcion", ["id_producto"], "n", 12).rename(columns={"n": "n_oc_recibidas_12m"})
rec = []
for m in meses:
    f = fin(m)
    ult = oc[oc["fecha_recepcion"] <= f].groupby("id_producto")["fecha_recepcion"].max().reset_index()
    ult["meses_desde_ultima_oc"] = ((f - ult["fecha_recepcion"]).dt.days / 30.44).round(1)
    ult["fecha_mes"] = m; rec.append(ult[["id_producto", "fecha_mes", "meses_desde_ultima_oc"]])
oc_rec_ult = pd.concat(rec)
trf12 = ventana(trf.rename(columns={"destino": "id_tienda"}), "fecha_recepcion", POS, "unidades", 12).rename(columns={"unidades": "uds_transf_recibidas_12m"})
# liquidaciones del SKU en toda la cadena (12 meses) y descuento de la liquidacion activa
liq_sku12 = ventana(liq.assign(n=1), "fecha_inicio", ["id_producto"], "n", 12).rename(columns={"n": "liquidaciones_sku_cadena_12m"})
dact = []
for m in meses:
    f = fin(m)
    a = liq_t[(liq_t["fecha_inicio"] <= f) & (liq_t["fecha_fin"] >= m)].groupby(POS)["descuento_pct"].max().reset_index()
    a["fecha_mes"] = m; dact.append(a)
liq_desc = pd.concat(dact).rename(columns={"descuento_pct": "descuento_liquidacion_activa"})
# promociones de la categoria en los ultimos 12 meses (canal fisico o todos)
pro_f2 = pro_f.assign(n=1)
promo12 = ventana(pro_f2, "fecha_inicio", ["categoria"], "n", 12).rename(columns={"n": "promos_categoria_12m"})
# presupuesto: cumplimiento de la tienda-categoria en los ultimos 3 meses (celdas invalidas excluidas, H9)
pre = rd("Presupuesto_Ventas_Tienda_Categoria.csv", parse_dates=["fecha_mes"])
pre = pre[pre["presupuesto_venta_ars"] > 0]
real = d.groupby(["fecha_mes", "id_tienda", "categoria"])["venta_neta"].sum().reset_index()
pc = pre.merge(real, on=["fecha_mes", "id_tienda", "categoria"], how="left").fillna({"venta_neta": 0})
pc = pc.sort_values(["id_tienda", "categoria", "fecha_mes"])
gp = pc.groupby(["id_tienda", "categoria"])
pc["cumplimiento_ppto_3m"] = gp["venta_neta"].transform(lambda x: x.rolling(3, min_periods=1).sum()) / \
                             gp["presupuesto_venta_ars"].transform(lambda x: x.rolling(3, min_periods=1).sum())
for extra, on in [(oc12, ["fecha_mes", "id_producto"]), (noc12, ["fecha_mes", "id_producto"]), (oc_rec_ult, ["fecha_mes", "id_producto"]),
                  (trf12, K), (liq_sku12, ["fecha_mes", "id_producto"]), (liq_desc, K), (promo12, ["fecha_mes", "categoria"]),
                  (pc[["fecha_mes", "id_tienda", "categoria", "cumplimiento_ppto_3m"]], ["fecha_mes", "id_tienda", "categoria"])]:
    d = d.merge(extra, on=on, how="left")
d[["uds_oc_recibidas_12m", "n_oc_recibidas_12m", "uds_transf_recibidas_12m", "liquidaciones_sku_cadena_12m",
   "descuento_liquidacion_activa", "promos_categoria_12m"]] = d[["uds_oc_recibidas_12m", "n_oc_recibidas_12m",
   "uds_transf_recibidas_12m", "liquidaciones_sku_cadena_12m", "descuento_liquidacion_activa", "promos_categoria_12m"]].fillna(0)
# calendario comercial fijo (Hot Sale jun, Black Friday nov, Navidad dic segun Calendario.csv): se conoce de antemano,
# por eso se puede mirar el horizonte t+1..t+3 sin leakage. No se usa Calendario.csv porque no cubre 2026 (H12).
EVENTOS = {6, 11, 12}
d["historia_corta"] = (d["antig_posicion_meses"] < 11).astype(int)   # < 12 meses: ritmo con los meses disponibles
d["eventos_en_horizonte"] = sum(((d["fecha_mes"].dt.month + k - 1) % 12 + 1).isin(EVENTOS).astype(int) for k in (1, 2, 3))

# ---------------------------------------------------------------- 7. universo y particion
univ = valido & hist12 & d["con_stock"] & ~d["discontinuado"]
P(f"Panel SKU-tienda-mes (post dedup y join ventas-stock): {len(d):,} filas")
P(f"  - con stock en t                         : {int(d['con_stock'].sum()):,}")
P(f"  - no discontinuadas en t                 : {int((d['con_stock'] & ~d['discontinuado']).sum()):,}")
P(f"  - con {HIST_MIN}+ meses de historia              : {int((d['con_stock'] & ~d['discontinuado'] & hist12).sum()):,}")
P(f"  - con etiqueta observable en t+3 (UNIVERSO): {int(univ.sum()):,}")

ds = d[univ].copy()
ds["target_cob12_t3"] = ds["target_cob12_t3"].astype(int)

def particion(m):
    if m <= pd.Timestamp("2024-12-01"): return "train"
    if pd.Timestamp("2025-04-01") <= m <= pd.Timestamp("2025-09-01"): return "validacion"
    if m >= pd.Timestamp("2026-01-01"): return "test"
    return "embargo"
ds["split"] = ds["fecha_mes"].map(particion)

# v3: fuera precio_lista, margen_lista, capital_inmovilizado_pos, precio_medio_12m, venta3_suma y
# descuento_implicito_12m (precio y costo son la foto ACTUAL del catalogo: aplicados a meses pasados son
# anacronicos, mismo argumento que excluye el estado del catalogo) y stock_en_transito / transito_sobre_stock
# (H6: campo sin definicion, pierde la senal en 2026). Entra historia_corta.
FEATURES_NUM = ["unidades_vendidas", "u3_suma", "u6_suma", "u12_prom", "cv_u12", "tendencia_u3_vs_u12",
                "meses_con_venta_12", "meses_sin_venta", "sin_venta_12m",
                "stock_disponible", "var_stock_3m", "cobertura",
                "stock_sku_cadena", "cobertura_sku_cadena", "tiendas_con_stock_sku", "tiendas_cob12_sku",
                "stock_deposito_sku", "uds_oc_recibidas_3m", "uds_oc_pendientes",
                "uds_transf_recibidas_3m", "uds_transf_enviadas_3m",
                "liquidacion_activa", "liquidaciones_12m", "promos_activas_categoria", "descuento_promo_max",
                "antig_sku_meses", "lead_time_dias", "pedido_minimo_unidades", "m2_venta", "mes_del_anio",
                "u_lag1", "u_lag2", "u12_max", "antig_posicion_meses", "historia_corta",
                "cobertura_3m_antes", "var_cobertura_3m",
                "peso_posicion_en_tienda", "stock_vs_prom_sku", "tendencia_sku_cadena", "cobertura_deposito_sku",
                "tendencia_tienda", "skus_en_tienda", "pct_pos_cob12_tienda", "tendencia_categoria_tienda",
                "precio_rel_subcategoria", "uds_oc_recibidas_12m", "n_oc_recibidas_12m", "meses_desde_ultima_oc",
                "uds_transf_recibidas_12m", "liquidaciones_sku_cadena_12m", "descuento_liquidacion_activa",
                "promos_categoria_12m", "cumplimiento_ppto_3m", "eventos_en_horizonte"]
FEATURES_CAT = ["categoria", "subcategoria", "region", "formato", "proveedor"]
IDS = ["fecha_mes", "id_tienda", "id_producto"]
# costo_imputado queda como marca de control (sugerencia del negocio P2), no como feature:
# los 22 SKUs no aparecen en train, asi que seria una columna constante
AUDIT = ["costo_imputado"]
cols = IDS + FEATURES_NUM + FEATURES_CAT + AUDIT + ["target_cob12_t3", "split"]
ds = ds[cols].reset_index(drop=True)

P(f"\nPeriodo de los cortes t: {ds['fecha_mes'].min().date()} a {ds['fecha_mes'].max().date()} "
  f"(etiquetas hasta {(ds['fecha_mes'].max() + pd.DateOffset(months=3)).date()})")
P(f"Posiciones distintas: {ds.groupby(['id_tienda','id_producto']).ngroups:,} · SKUs: {ds['id_producto'].nunique()} · tiendas: {ds['id_tienda'].nunique()}")
P(f"Features: {len(FEATURES_NUM)} numericas + {len(FEATURES_CAT)} categoricas = {len(FEATURES_NUM) + len(FEATURES_CAT)}")
P(f"Prevalencia total: {ds['target_cob12_t3'].mean():.2%} ({int(ds['target_cob12_t3'].sum()):,} positivos)")

P("\nPARTICION TEMPORAL (embargo de 3 meses = horizonte, para que ninguna etiqueta de un bloque caiga en el siguiente)")
tab = ds.groupby("split").agg(desde=("fecha_mes", "min"), hasta=("fecha_mes", "max"), filas=("target_cob12_t3", "size"),
                              positivos=("target_cob12_t3", "sum"), prevalencia=("target_cob12_t3", "mean"))
tab = tab.loc[["train", "validacion", "test", "embargo"]]
tab["desde"] = tab["desde"].dt.strftime("%Y-%m"); tab["hasta"] = tab["hasta"].dt.strftime("%Y-%m")
tab["prevalencia"] = (tab["prevalencia"] * 100).round(2)
P(tab.to_string())

# ---------------------------------------------------------------- 8. diagnostico para las transformaciones
P("\nNULOS REMANENTES (antes de transformar)")
nul = ds[FEATURES_NUM].isna().sum(); nul = nul[nul > 0]
P(nul.to_string() if len(nul) else "  ninguno")
P(f"  cobertura infinita (stock > 0 sin venta en 12 m): {int(np.isinf(ds['cobertura']).sum()):,}")

tr = ds[ds["split"] == "train"]
fin_num = tr[FEATURES_NUM].replace([np.inf, -np.inf], np.nan)
sk = fin_num.skew().sort_values(ascending=False)
P("\nASIMETRIA (skew, train) — > 1 se considera sesgada")
P(sk.round(2).to_string())
q = fin_num.quantile([0.5, 0.99, 1.0]).T
q.columns = ["p50", "p99", "max"]
P("\nMEDIANA / P99 / MAX (train)")
P(q.round(2).to_string())

# ---------------------------------------------------------------- 9. transformaciones (fit SOLO en train)
SESGADAS = [c for c in FEATURES_NUM if sk.get(c, 0) > 1 and fin_num[c].min() >= 0
            and c not in ("sin_venta_12m", "costo_imputado", "liquidacion_activa", "historia_corta")]
X = ds.copy()
X["cobertura"] = X["cobertura"].replace(np.inf, np.nan)
# faltantes remanentes: ratios sin denominador (sin venta en 12 m) -> tope + flag ya existente
TOPE_COB = 60
X["cobertura"] = X["cobertura"].fillna(TOPE_COB).clip(upper=TOPE_COB)
X["cobertura_sku_cadena"] = X["cobertura_sku_cadena"].fillna(TOPE_COB).clip(upper=TOPE_COB)
X["tendencia_u3_vs_u12"] = X["tendencia_u3_vs_u12"].fillna(0)
X["cv_u12"] = X["cv_u12"].fillna(0)
X["var_stock_3m"] = X["var_stock_3m"].fillna(0)
# v2: mismas reglas para las nuevas (denominador cero o ausencia de evento, no dato perdido)
# sin dato en t-3 (posicion con menos de 4 meses): se asume la cobertura actual (sin cambio);
# infinito (sin venta en ese momento): tope
X["cobertura_3m_antes"] = X["cobertura_3m_antes"].fillna(X["cobertura"]).replace(np.inf, np.nan).fillna(TOPE_COB).clip(upper=TOPE_COB)
X["var_cobertura_3m"] = X["var_cobertura_3m"].fillna(0)
X["meses_desde_ultima_oc"] = X["meses_desde_ultima_oc"].fillna(TOPE_COB)
for c, v in [("peso_posicion_en_tienda", 0),
             ("stock_vs_prom_sku", 1), ("tendencia_sku_cadena", 1), ("tendencia_tienda", 1), ("tendencia_categoria_tienda", 1)]:
    X[c] = X[c].fillna(v)
for c in ["cobertura_deposito_sku", "cumplimiento_ppto_3m"]:   # sin denominador / sin presupuesto valido -> mediana de train
    X[c] = X[c].replace(np.inf, np.nan).fillna(X.loc[X["split"] == "train", c].replace(np.inf, np.nan).median())
# outliers: winsorizacion p1-p99 con limites de train, solo en continuas (> 15 valores distintos);
# en conteos de pocos valores (liquidaciones, promos, tiendas) el p99 coincide con el minimo y los anularia
lim = {}
for c in FEATURES_NUM:
    if c in ("mes_del_anio", "sin_venta_12m", "costo_imputado", "liquidacion_activa", "historia_corta"): continue
    trc = X.loc[X["split"] == "train", c]
    if trc.nunique() <= 15: continue
    lo, hi = trc.quantile([0.01, 0.99])
    lim[c] = (lo, hi); X[c] = X[c].clip(lo, hi)
# distribuciones sesgadas: log1p (var_stock_3m puede ser negativa -> signed log)
for c in SESGADAS:
    X[c] = np.log1p(X[c])
X["var_stock_3m"] = np.sign(X["var_stock_3m"]) * np.log1p(X["var_stock_3m"].abs())
X["var_cobertura_3m"] = np.sign(X["var_cobertura_3m"]) * np.log1p(X["var_cobertura_3m"].abs())
# temporal ciclica
X["mes_sin"] = np.sin(2 * np.pi * X["mes_del_anio"] / 12)
X["mes_cos"] = np.cos(2 * np.pi * X["mes_del_anio"] / 12)
X = X.drop(columns="mes_del_anio")
# escalado estandar (media/desvio de train) sobre las continuas
BIN = ["sin_venta_12m", "liquidacion_activa", "historia_corta"]
CONT = [c for c in FEATURES_NUM if c not in BIN + ["mes_del_anio"]]
mu = X.loc[X["split"] == "train", CONT].mean(); sd = X.loc[X["split"] == "train", CONT].std().replace(0, 1)
X[CONT] = (X[CONT] - mu) / sd
# one-hot de categoricas nominales (categorias vistas en train)
X = pd.get_dummies(X, columns=FEATURES_CAT, prefix=FEATURES_CAT, dtype=int)
feat_final = [c for c in X.columns if c not in IDS + AUDIT + ["target_cob12_t3", "split"]]

P(f"\nTRANSFORMADO: {len(X):,} filas x {len(feat_final)} features (+ ids, marca de costo imputado, target y split)")
P(f"  winsorizadas p1-p99: {', '.join(lim)}")
P(f"  log1p aplicado a: {', '.join(SESGADAS)}")
const = [c for c in feat_final if X.loc[X["split"] == "train", c].nunique() <= 1]
P(f"  columnas constantes en train: {const if const else 'ninguna'}")
P(f"  filas con costo imputado (22 SKUs): {int(ds['costo_imputado'].sum()):,}")
P(f"  one-hot: " + ", ".join(f"{c} ({ds[c].nunique()})" for c in FEATURES_CAT))
peso = (1 - tr["target_cob12_t3"].mean()) / tr["target_cob12_t3"].mean()
P(f"  balanceo sugerido: class_weight positivo = {peso:.1f} (calculado en train, sin sobremuestreo)")

# ---------------------------------------------------------------- 10. guardado
ds.to_parquet(os.path.join(OUTD, f"dataset_entrenamiento_{VERSION}.parquet"), index=False)
X.to_parquet(os.path.join(OUTD, f"dataset_entrenamiento_{VERSION}_transformado.parquet"), index=False)
ds.sample(1000, random_state=42).sort_values(IDS).to_csv(
    os.path.join(OUTD, f"dataset_entrenamiento_{VERSION}_muestra.csv"), index=False)

DESC = {
 "fecha_mes": "Mes de corte t (la prediccion se hace al cierre de este mes)",
 "id_tienda": "Tienda (identificador, no se usa como feature)",
 "id_producto": "SKU (identificador, no se usa como feature)",
 "unidades_vendidas": "Unidades netas de devoluciones vendidas en t",
 "u3_suma": "Unidades netas de los ultimos 3 meses",
 "u6_suma": "Unidades netas de los ultimos 6 meses",
 "u12_prom": "Promedio mensual de unidades netas de los ultimos 12 meses (ritmo de venta)",
 "cv_u12": "Coeficiente de variacion de las unidades de 12 meses (demanda intermitente)",
 "tendencia_u3_vs_u12": "Ritmo de 3 meses sobre ritmo de 12 meses (>1 acelera, <1 frena)",
 "meses_con_venta_12": "Meses con venta > 0 en los ultimos 12",
 "meses_sin_venta": "Meses consecutivos sin venta hasta t",
 "sin_venta_12m": "1 si no hubo venta neta en 12 meses (cobertura infinita)",
 "precio_medio_12m": "Venta neta / unidades de 12 meses",
 "stock_disponible": "Stock disponible en t (piso en 0)",
 "stock_en_transito": "Stock en transito en t (definicion no documentada, H6)",
 "var_stock_3m": "Variacion del stock disponible respecto de t-3",
 "cobertura": "Meses de stock en t: stock / u12_prom",
 "capital_inmovilizado_pos": "Stock x costo unitario (con costo ajustado en los 22 SKUs)",
 "stock_sku_cadena": "Stock del SKU sumado en las 28 tiendas en t",
 "cobertura_sku_cadena": "Cobertura del SKU a nivel cadena en t",
 "tiendas_con_stock_sku": "Tiendas con stock del SKU en t",
 "tiendas_cob12_sku": "Tiendas donde el SKU ya supera 12 meses de cobertura en t",
 "stock_deposito_sku": "Stock del SKU en el deposito central en t",
 "uds_oc_recibidas_3m": "Unidades del SKU recibidas por OC en los ultimos 3 meses",
 "uds_oc_pendientes": "Unidades del SKU pedidas y no recibidas al cierre de t",
 "uds_transf_recibidas_3m": "Unidades transferidas hacia la posicion en los ultimos 3 meses",
 "uds_transf_enviadas_3m": "Unidades transferidas desde la posicion en los ultimos 3 meses",
 "liquidacion_activa": "1 si la posicion (o el SKU en todas las tiendas) esta en liquidacion en t",
 "liquidaciones_12m": "Liquidaciones iniciadas sobre la posicion en los ultimos 12 meses",
 "promos_activas_categoria": "Promociones de la categoria vigentes en t (canal fisico o todos)",
 "descuento_promo_max": "Descuento maximo de esas promociones",
 "precio_lista": "Precio de lista del catalogo",
 "margen_lista": "1 - costo / precio de lista",
 "costo_imputado": "1 si el costo es el supuesto de OC x 1,2321 (H11)",
 "antig_sku_meses": "Meses desde el alta del SKU en el catalogo",
 "lead_time_dias": "Lead time declarado del proveedor",
 "pedido_minimo_unidades": "Pedido minimo del proveedor",
 "m2_venta": "Superficie de venta de la tienda",
 "mes_del_anio": "Mes calendario de t (1-12)",
 "categoria": "Categoria del SKU (7)", "subcategoria": "Subcategoria del SKU",
 "region": "Region de la tienda (5)", "formato": "Formato de la tienda (3)",
 "u_lag1": "Unidades netas en t-1", "u_lag2": "Unidades netas en t-2",
 "u12_max": "Maximo mensual de unidades en 12 meses", "venta3_suma": "Venta neta de los ultimos 3 meses",
 "antig_posicion_meses": "Meses con registro de la posicion hasta t",
 "cobertura_3m_antes": "Cobertura de la posicion en t-3", "var_cobertura_3m": "Cambio de cobertura entre t-3 y t",
 "transito_sobre_stock": "Stock en transito / stock disponible (H6: usar con cautela)",
 "descuento_implicito_12m": "1 - precio medio realizado / precio de lista (12 meses)",
 "peso_posicion_en_tienda": "Participacion de la posicion en las unidades de la tienda (12 meses)",
 "stock_vs_prom_sku": "Stock de la posicion / stock promedio del SKU en las tiendas que lo tienen",
 "tendencia_sku_cadena": "Ritmo de 3 vs 12 meses del SKU en toda la cadena",
 "cobertura_deposito_sku": "Stock del SKU en deposito / ritmo mensual del SKU en la cadena",
 "tendencia_tienda": "Ritmo de 3 vs 12 meses de toda la tienda",
 "skus_en_tienda": "Posiciones con stock en la tienda en t",
 "pct_pos_cob12_tienda": "Proporcion de posiciones de la tienda con cobertura > 12 en t",
 "tendencia_categoria_tienda": "Ritmo de 3 vs 12 meses de la categoria en la tienda",
 "precio_rel_subcategoria": "Precio de lista / mediana de la subcategoria",
 "uds_oc_recibidas_12m": "Unidades del SKU recibidas por OC en 12 meses",
 "n_oc_recibidas_12m": "OC del SKU recibidas en 12 meses",
 "meses_desde_ultima_oc": "Meses desde la ultima OC recibida del SKU",
 "uds_transf_recibidas_12m": "Unidades transferidas hacia la posicion en 12 meses",
 "liquidaciones_sku_cadena_12m": "Liquidaciones del SKU en toda la cadena en 12 meses",
 "descuento_liquidacion_activa": "Descuento de la liquidacion vigente en la posicion (0 si no hay)",
 "promos_categoria_12m": "Promociones de la categoria iniciadas en 12 meses",
 "cumplimiento_ppto_3m": "Venta / presupuesto de la tienda-categoria en 3 meses (celdas invalidas excluidas)",
 "eventos_en_horizonte": "Meses con evento comercial fijo (Hot Sale, Black Friday, Navidad) entre t+1 y t+3",
 "proveedor": "Proveedor del SKU (10)",
 "historia_corta": "1 si la posicion tiene menos de 12 meses de historia (ritmo calculado con los meses disponibles)",
 "target_cob12_t3": "TARGET: 1 si en t+3 la posicion tiene cobertura > 12 meses (sin discontinuados)",
 "split": "train / validacion / test / embargo"}
pd.DataFrame({"columna": cols, "descripcion": [DESC[c] for c in cols]}).to_csv(
    os.path.join(OUTD, f"diccionario_features_{VERSION}.csv"), index=False)

P(f"\nGuardado en {OUTD}")
# ---------------------------------------------------------------- 11. senal univariada (solo descriptiva, no selecciona)
from sklearn.metrics import roc_auc_score
filas = []
for c in FEATURES_NUM:
    fila = {"feature": c}
    for sp in ["train", "validacion", "test"]:
        s_ = ds[ds["split"] == sp]; x = s_[c].replace([np.inf, -np.inf], np.nan)
        x = x.fillna(x.max() if c.startswith("cobertura") else x.median())
        a = roc_auc_score(s_["target_cob12_t3"], x)
        fila[f"auc_{sp}"] = round(max(a, 1 - a), 3); fila[f"dir_{sp}"] = "+" if a >= .5 else "-"
    filas.append(fila)
sen = pd.DataFrame(filas).sort_values("auc_train", ascending=False)
sen.to_csv(os.path.join(RES, f"senal_univariada_{VERSION}.csv"), index=False)
P("\nSENAL UNIVARIADA (AUC de cada feature sola; + = mas valor, mas riesgo)")
P(sen.to_string(index=False))
LOG.close()
