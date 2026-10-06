# -*- coding: utf-8 -*-
"""
Datos del dashboard comparativo ANTES vs DESPUES del procesamiento y la limpieza (envio a la catedra).

ANTES   = Datasets/ tal como los entrega la catedra (sin tocar).
DESPUES = Datasets_Normalizados/ + criterios del plan de mejora, los mismos que usa
          Modelo/construir_dataset_modelo.py:
          R1-R4 normalizacion de texto, categorias y fechas · H1/H2 dedup 1ra ocurrencia ·
          H4 stock piso 0 y ventas negativas neteadas · H9 descuentos y presupuesto invalidos excluidos ·
          H10 promociones duplicadas o con fechas invertidas excluidas · H11 costo OC x 1,2321.

Salida: resultados/comparativo_antes_despues.json (lo consume Envio-Profesores/armar_envio.py)
"""
import os, sys, json
import numpy as np, pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
RAW, NRM = os.path.join(ROOT, "Datasets"), os.path.join(ROOT, "Datasets_Normalizados")
RES = os.path.join(BASE, "resultados")
MOD = os.path.join(BASE, "..", "Modelo", "resultados")
K = ["fecha_mes", "id_tienda", "id_producto"]
FACTOR = 1.2321
M = 1e6

def rd(carpeta, f, **kw): return pd.read_csv(os.path.join(carpeta, f), **kw)
def r(x, n=2): return None if x is None or (isinstance(x, float) and not np.isfinite(x)) else round(float(x), n)

# ------------------------------------------------------------------ carga
v0, s0 = rd(RAW, "Ventas_SKU_tienda_mensual.csv"), rd(RAW, "Stock_SKU_tienda_mensual.csv")
c0, l0 = rd(RAW, "Productos_catalogo.csv"), rd(RAW, "Liquidaciones.csv")
p0, b0 = rd(RAW, "Promociones_Comerciales.csv"), rd(RAW, "Presupuesto_Ventas_Tienda_Categoria.csv")

v1r = rd(NRM, "Ventas_SKU_tienda_mensual.csv")
pos = v1r[v1r["unidades_vendidas"] >= 0].drop_duplicates(K)
neg = v1r[v1r["unidades_vendidas"] < 0]
v1 = pd.concat([pos, neg]).groupby(K, as_index=False)[["unidades_vendidas", "venta_neta"]].sum()
s1 = rd(NRM, "Stock_SKU_tienda_mensual.csv").drop_duplicates(K)
s1["stock_disponible"] = s1["stock_disponible"].clip(lower=0)
c1 = rd(NRM, "Productos_catalogo.csv").drop_duplicates("id_producto")
oc = rd(NRM, "Ordenes_Compra.csv"); oc["m"] = oc["unidades"] * oc["costo_unitario_ars"]
c_oc = oc.groupby("id_producto")["m"].sum() / oc.groupby("id_producto")["unidades"].sum()
sin_costo = c1[c1["costo_unitario"].isna()]["id_producto"].tolist()
c1["costo_unitario"] = c1["costo_unitario"].fillna(c1["id_producto"].map(c_oc * FACTOR))
l1r = rd(NRM, "Liquidaciones.csv"); l1 = l1r[l1r["descuento_pct"].between(0, 100)]
p1r = rd(NRM, "Promociones_Comerciales.csv")
p1 = p1r[p1r["descuento_pct"].between(0, 100)]
p1 = p1[pd.to_datetime(p1["fecha_fin"]) >= pd.to_datetime(p1["fecha_inicio"])].drop_duplicates()
b1r = rd(NRM, "Presupuesto_Ventas_Tienda_Categoria.csv"); b1 = b1r[b1r["presupuesto_venta_ars"] > 0]

out = {}

# ------------------------------------------------------------------ 1. por fuente
def prob_fuente(nombre):
    """(problemas antes, problemas despues, detalle) por fuente, en filas o celdas afectadas."""
    if nombre == "Ventas_SKU_tienda_mensual.csv":
        a = int(v0.duplicated(K).sum()) + int((v0["unidades_vendidas"] < 0).sum())
        return a, 0, "2.378 claves duplicadas + 2.317 ventas negativas (devoluciones)"
    if nombre == "Stock_SKU_tienda_mensual.csv":
        return int(s0.duplicated(K).sum()) + int((s0["stock_disponible"] < 0).sum()), 0, "2.378 claves duplicadas + 1.209 stocks negativos"
    if nombre == "Productos_catalogo.csv":
        a = int(c0["id_producto"].duplicated().sum()) + int(c0.drop_duplicates("id_producto")["costo_unitario"].isna().sum()) + \
            int((c0["categoria"] != rd(NRM, nombre)["categoria"]).sum())
        return a, 0, "15 SKUs repetidos + 22 sin costo + 121 categorías mal escritas"
    if nombre == "Liquidaciones.csv":
        a = int((~l0["descuento_pct"].between(0, 100)).sum()) + int(l0["fecha_fin"].str.len().gt(10).sum())
        return a, 0, "3 descuentos fuera de rango + 8 fechas con hora"
    if nombre == "Promociones_Comerciales.csv":
        a = int((~p0["descuento_pct"].between(0, 100)).sum()) + int(p0.duplicated().sum()) + \
            int((pd.to_datetime(p0["fecha_fin"]) < pd.to_datetime(p0["fecha_inicio"])).sum()) + \
            int((p0["categoria"] != p1r["categoria"]).sum())
        return a, 0, "2 descuentos fuera de rango + 1 duplicada + 2 fechas invertidas + 19 categorías"
    if nombre == "Presupuesto_Ventas_Tienda_Categoria.csv":
        return int((b0["presupuesto_venta_ars"] <= 0).sum()) + int((b0["categoria"] != b1r["categoria"]).sum()), 0, \
            "309 celdas en cero + 3 negativas + 1.568 categorías con tilde"
    return None

FILAS_DESPUES = {"Ventas_SKU_tienda_mensual.csv": len(v1), "Stock_SKU_tienda_mensual.csv": len(s1),
                 "Productos_catalogo.csv": len(c1), "Liquidaciones.csv": len(l1),
                 "Promociones_Comerciales.csv": len(p1), "Presupuesto_Ventas_Tienda_Categoria.csv": len(b1)}
cambios = rd(RES, "cambios_normalizacion_aplicados.csv", encoding="utf-8-sig")
celdas_txt = cambios.groupby("fuente")["filas"].sum()
fuentes = []
for f in sorted(x for x in os.listdir(RAW) if x.endswith(".csv")):
    a, b = rd(RAW, f), rd(NRM, f)
    pf = prob_fuente(f)
    nombre = f[:-4]
    txt = int(celdas_txt.get(nombre, 0))
    pa, pd_, det = pf if pf else (txt, 0, "solo texto (tildes / formato)" if txt else "sin cambios")
    fuentes.append(dict(fuente=nombre, filas_antes=len(a), filas_despues=FILAS_DESPUES.get(f, len(b)),
                        columnas=a.shape[1], nulos_antes=int(a.isna().sum().sum()),
                        nulos_despues=int(a.isna().sum().sum()) - (22 if f == "Productos_catalogo.csv" else 0),
                        problemas_antes=pa, problemas_despues=pd_, celdas_texto=txt, detalle=det))
out["fuentes"] = fuentes
print(pd.DataFrame(fuentes).to_string())

# ------------------------------------------------------------------ 2. ventas
mes = sorted(v0["fecha_mes"].unique())
def serie(df, col, fn="sum"): return df.groupby("fecha_mes")[col].agg(fn).reindex(mes, fill_value=0)
out["ventas"] = dict(
    meses=[m[:7] for m in mes],
    filas_antes=serie(v0, "unidades_vendidas", "size").tolist(), filas_despues=serie(v1, "unidades_vendidas", "size").tolist(),
    uds_antes=serie(v0, "unidades_vendidas").astype(int).tolist(), uds_despues=serie(v1, "unidades_vendidas").astype(int).tolist(),
    venta_antes=[r(x / M, 1) for x in serie(v0, "venta_neta")], venta_despues=[r(x / M, 1) for x in serie(v1, "venta_neta")],
    dup_mes=v0[v0.duplicated(K)].groupby("fecha_mes").size().reindex(mes, fill_value=0).astype(int).tolist(),
    neg_mes=v0[v0["unidades_vendidas"] < 0].groupby("fecha_mes").size().reindex(mes, fill_value=0).astype(int).tolist(),
)
# distribucion de unidades por fila (bins enteros, recortado a -10..40)
def hist_int(x, lo, hi):
    x = x.clip(lo, hi)
    return x.value_counts().reindex(range(lo, hi + 1), fill_value=0).astype(int).tolist()
out["ventas"]["hist_bins"] = list(range(-10, 41))
out["ventas"]["hist_antes"] = hist_int(v0["unidades_vendidas"], -10, 40)
out["ventas"]["hist_despues"] = hist_int(v1["unidades_vendidas"], -10, 40)
out["ventas"]["kpi"] = dict(
    filas=[len(v0), len(v1)], unidades=[int(v0["unidades_vendidas"].sum()), int(v1["unidades_vendidas"].sum())],
    venta=[r(v0["venta_neta"].sum() / M, 1), r(v1["venta_neta"].sum() / M, 1)],
    claves_dup=[int(v0.duplicated(K).sum()), int(v1.duplicated(K).sum())],
    filas_neg=[int((v0["unidades_vendidas"] < 0).sum()), int((v1["unidades_vendidas"] < 0).sum())],
    filas_identicas=[int(v0.duplicated().sum()), 0])

# ejemplos fila a fila: una clave duplicada y una venta negativa neteada
dupk = v0[v0.duplicated(K, keep=False)].sort_values(K)
k_ej = dupk.groupby(K).filter(lambda g: g["unidades_vendidas"].nunique() > 1).head(2)[K].iloc[0].tolist()
sel = lambda df: df[(df["fecha_mes"] == k_ej[0]) & (df["id_tienda"] == k_ej[1]) & (df["id_producto"] == k_ej[2])]
_n = v0[v0["unidades_vendidas"] < 0].merge(v0[v0["unidades_vendidas"] > 0][K], on=K)   # devolucion con venta el mismo mes
negk = _n.iloc[0][K].tolist()
sel2 = lambda df: df[(df["fecha_mes"] == negk[0]) & (df["id_tienda"] == negk[1]) & (df["id_producto"] == negk[2])]
rec = lambda df: df[K + ["unidades_vendidas", "venta_neta"]].to_dict("records")
out["ventas"]["ejemplos"] = [
    dict(titulo="Clave duplicada (H1)", nota="Dos filas para la misma clave mes-tienda-SKU con valores distintos: se conserva la 1ra ocurrencia.",
         antes=rec(sel(v0)), despues=rec(sel(v1))),
    dict(titulo="Venta negativa = devolución (H4)", nota="La devolución se netea contra la venta del mismo SKU-tienda-mes: no se pierde ni se lleva a 0.",
         antes=rec(sel2(v0)), despues=rec(sel2(v1)))]

# ------------------------------------------------------------------ 3. stock
out["stock"] = dict(
    meses=[m[:7] for m in mes],
    neg_antes=s0[s0["stock_disponible"] < 0].groupby("fecha_mes").size().reindex(mes, fill_value=0).astype(int).tolist(),
    neg_despues=s1[s1["stock_disponible"] < 0].groupby("fecha_mes").size().reindex(mes, fill_value=0).astype(int).tolist(),
    stock_antes=s0.groupby("fecha_mes")["stock_disponible"].sum().reindex(mes).astype(int).tolist(),
    stock_despues=s1.groupby("fecha_mes")["stock_disponible"].sum().reindex(mes).astype(int).tolist(),
    hist_bins=list(range(-20, 61, 1)),
    hist_antes=hist_int(s0["stock_disponible"], -20, 60), hist_despues=hist_int(s1["stock_disponible"], -20, 60))
cap = {}
for corte, et in [("2025-12-01", "dic-25"), ("2026-08-01", "ago-26")]:
    a = s0[s0["fecha_mes"] == corte].merge(c0[["id_producto", "costo_unitario"]], on="id_producto")
    b = s1[s1["fecha_mes"] == corte].merge(c1[["id_producto", "costo_unitario"]], on="id_producto")
    cap[et] = [r((a["stock_disponible"] * a["costo_unitario"]).sum() / M, 1), r((b["stock_disponible"] * b["costo_unitario"]).sum() / M, 1)]
out["stock"]["kpi"] = dict(
    filas=[len(s0), len(s1)], claves_dup=[int(s0.duplicated(K).sum()), 0],
    filas_neg=[int((s0["stock_disponible"] < 0).sum()), int((s1["stock_disponible"] < 0).sum())],
    minimo=[int(s0["stock_disponible"].min()), int(s1["stock_disponible"].min())],
    unidades_neg=[int(s0.loc[s0["stock_disponible"] < 0, "stock_disponible"].sum()), 0],
    capital=cap)
nk = s0[s0["stock_disponible"] < 0].sort_values("stock_disponible").iloc[0][K].tolist()
sel3 = lambda df: df[(df["fecha_mes"] == nk[0]) & (df["id_tienda"] == nk[1]) & (df["id_producto"] == nk[2])]
out["stock"]["ejemplos"] = [dict(titulo="Stock negativo (H4)", nota="Error de sincronización POS-inventario (P14): piso en 0.",
                                 antes=sel3(s0)[K + ["stock_disponible", "stock_en_transito"]].to_dict("records"),
                                 despues=sel3(s1)[K + ["stock_disponible", "stock_en_transito"]].to_dict("records"))]

# ------------------------------------------------------------------ 4. catalogo y categorias
cat_n0 = c0["categoria"].value_counts()
cat_n1 = c1["categoria"].value_counts()
vc0 = v0.merge(c0.drop_duplicates("id_producto")[["id_producto", "categoria"]], on="id_producto").groupby("categoria")["venta_neta"].sum() / M
vc1 = v1.merge(c1[["id_producto", "categoria"]], on="id_producto").groupby("categoria")["venta_neta"].sum() / M
canon = rd(NRM, "Productos_catalogo.csv")["categoria"]
mapa = pd.DataFrame({"crudo": c0["categoria"], "canon": canon}).drop_duplicates().sort_values(["canon", "crudo"])
out["catalogo"] = dict(
    cat_antes=[dict(label=k, skus=int(cat_n0[k]), venta=r(vc0.get(k, 0), 1),
                    canon=mapa.loc[mapa["crudo"] == k, "canon"].iloc[0]) for k in cat_n0.index],
    cat_despues=[dict(label=k, skus=int(cat_n1[k]), venta=r(vc1.get(k, 0), 1)) for k in cat_n1.index],
    kpi=dict(filas=[len(c0), len(c1)], ids_repetidos=[int(c0["id_producto"].duplicated().sum()), 0],
             categorias=[int(c0["categoria"].nunique()), int(c1["categoria"].nunique())],
             sin_costo=[int(c0.drop_duplicates("id_producto")["costo_unitario"].isna().sum()), int(c1["costo_unitario"].isna().sum())]))
cos = rd(RES, "costo_ajustado_22_skus.csv")
out["catalogo"]["costos_22"] = [dict(sku=x.id_producto, categoria=x.categoria, precio=r(x.precio_lista, 0), costo_oc=r(x.costo_oc, 0),
                                     costo_ajustado=r(x.costo_ajustado, 0), margen=r((1 - x.costo_ajustado / x.precio_lista) * 100, 1))
                                for x in cos.itertuples()]
cc = c1[~c1["id_producto"].isin(sin_costo)]
out["catalogo"]["margen_resto"] = r((1 - cc["costo_unitario"] / cc["precio_lista"]).mean() * 100, 1)
dup_sku = c0[c0["id_producto"].duplicated(keep=False)].sort_values("id_producto")
ej = dup_sku["id_producto"].iloc[0]
cols_c = ["id_producto", "categoria", "subcategoria", "proveedor", "costo_unitario", "precio_lista"]
out["catalogo"]["ejemplos"] = [dict(titulo="SKU repetido en el maestro (H2)",
    nota="Mismo SKU en dos filas, idénticas salvo el proveedor (error del sistema, P11): queda la 1ra. Es la causa de las claves duplicadas en Ventas y Stock.",
    antes=c0[c0["id_producto"] == ej][cols_c].to_dict("records"), despues=c1[c1["id_producto"] == ej][cols_c].to_dict("records"))]
sk = sin_costo[0]
c0d = c0.drop_duplicates("id_producto")
out["catalogo"]["ejemplos"].append(dict(titulo="SKU sin costo (H11)",
    nota=f"Costo = costo de OC ponderado x {str(FACTOR).replace('.', ',')} (supuesto declarado; nivela el margen con el 44,9% del resto).",
    antes=c0d[c0d["id_producto"] == sk][cols_c].to_dict("records"), despues=c1[c1["id_producto"] == sk][cols_c].to_dict("records")))

# ------------------------------------------------------------------ 5. liquidaciones y promociones
def hist_desc(x, lo=-20, hi=160, paso=10):
    bins = list(range(lo, hi + paso, paso))
    h = pd.cut(x, bins=bins, right=False).value_counts().sort_index().astype(int).tolist()
    return bins[:-1], h
bl, hl0 = hist_desc(l0["descuento_pct"]); _, hl1 = hist_desc(l1["descuento_pct"])
_, hp0 = hist_desc(p0["descuento_pct"]); _, hp1 = hist_desc(p1["descuento_pct"])
out["acciones"] = dict(
    bins=bl, liq_antes=hl0, liq_despues=hl1, promo_antes=hp0, promo_despues=hp1,
    kpi=dict(liq_filas=[len(l0), len(l1)], liq_fuera=[int((~l0["descuento_pct"].between(0, 100)).sum()), 0],
             liq_desc=[r(l0["descuento_pct"].mean(), 1), r(l1["descuento_pct"].mean(), 1)],
             liq_fechas_hora=[int(l0["fecha_fin"].str.len().gt(10).sum()), int(l1r["fecha_fin"].str.len().gt(10).sum())],
             promo_filas=[len(p0), len(p1)], promo_fuera=[int((~p0["descuento_pct"].between(0, 100)).sum()), 0],
             promo_desc=[r(p0["descuento_pct"].mean(), 1), r(p1["descuento_pct"].mean(), 1)],
             promo_dup=[int(p0.duplicated().sum()), 0],
             promo_fechas_inv=[int((pd.to_datetime(p0["fecha_fin"]) < pd.to_datetime(p0["fecha_inicio"])).sum()), 0],
             liq_todas=int((l0["tienda"] == "Todas").sum())))
fuera_l = l0[~l0["descuento_pct"].between(0, 100)]
hora = l0[l0["fecha_fin"].str.len() > 10]
cl = ["id_liquidacion", "id_producto", "tienda", "fecha_inicio", "fecha_fin", "descuento_pct"]
out["acciones"]["ejemplos"] = [
    dict(titulo="Descuento fuera de rango (H9)", nota="Error de carga (dígito de más o signo invertido, P24-P28): se excluye del cálculo.",
         antes=fuera_l[cl].to_dict("records"), despues=[]),
    dict(titulo="Fecha con hora (R2)", nota="Era una fecha válida con otro formato: se unifica y el registro se recupera (el TP1 la había descartado).",
         antes=hora[cl].head(3).to_dict("records"), despues=l1r[l1r["id_liquidacion"].isin(hora["id_liquidacion"].head(3))][cl].to_dict("records"))]

# ------------------------------------------------------------------ 6. presupuesto
cat_map = c1.set_index("id_producto")["categoria"]
def real_de(v): return v.assign(categoria=v["id_producto"].map(cat_map)).groupby(["fecha_mes", "id_tienda", "categoria"])["venta_neta"].sum()
def cumpl(b, v):
    x = b.merge(real_de(v).reset_index(), on=["fecha_mes", "id_tienda", "categoria"], how="left").fillna({"venta_neta": 0})
    g = x.groupby("fecha_mes")[["venta_neta", "presupuesto_venta_ars"]].sum()
    return (g["venta_neta"] / g["presupuesto_venta_ars"].where(g["presupuesto_venta_ars"] > 0) * 100)
def cumpl_anual(b, v, anio="2022"):
    x = b[b["fecha_mes"].str.startswith(anio)].merge(real_de(v).reset_index(), on=["fecha_mes", "id_tienda", "categoria"], how="left").fillna({"venta_neta": 0})
    return x["venta_neta"].sum() / x["presupuesto_venta_ars"].sum() * 100
b0n = b0.copy(); b0n["categoria"] = b1r["categoria"]       # misma fila: solo para poder cruzar con la venta
mb = sorted(b0["fecha_mes"].unique())
ca, cd = cumpl(b0n, v0).reindex(mb), cumpl(b1, v1).reindex(mb)   # antes: venta cruda (con duplicados), como en antes_despues.py
out["presupuesto"] = dict(meses=[m[:7] for m in mb], cumpl_antes=[r(x, 1) for x in ca], cumpl_despues=[r(x, 1) for x in cd],
    invalidas_mes=b0[b0["presupuesto_venta_ars"] <= 0].groupby("fecha_mes").size().reindex(mb, fill_value=0).astype(int).tolist(),
    kpi=dict(celdas=[len(b0), len(b1)], ceros=[int((b0["presupuesto_venta_ars"] == 0).sum()), 0],
             negativas=[int((b0["presupuesto_venta_ars"] < 0).sum()), 0],
             cumpl_2022=[r(cumpl_anual(b0n, v0), 2), r(cumpl_anual(b1, v1), 2)]))

# metricas de la tabla de la Parte B 1.3 que no salen de lo anterior (mismo calculo, EDA/antes_despues.py)
ad = rd(RES, "antes_despues.csv").set_index("metrica")
out["catalogo"]["kpi"]["decoracion_pct"] = [r(ad.loc["Participacion de Decoracion en la venta (%)", "antes"]),
                                            r(ad.loc["Participacion de Decoracion en la venta (%)", "despues"])]
out["modelo_cob12_dic25"] = [int(ad.loc["Posiciones con cobertura > 12 meses a dic-25", "antes"]),
                             int(ad.loc["Posiciones con cobertura > 12 meses a dic-25", "despues"])]

# ------------------------------------------------------------------ 7. normalizacion de texto
out["texto"] = cambios.to_dict("records")

# ------------------------------------------------------------------ 8. del panel al dataset del modelo
log = open(os.path.join(MOD, "construir_dataset_log.txt"), encoding="utf-8").read()
ds = pd.read_parquet(os.path.join(ROOT, "Datasets_Modelo", "dataset_entrenamiento_v3.parquet"))
sp = ds.groupby("split").agg(desde=("fecha_mes", "min"), hasta=("fecha_mes", "max"), filas=("target_cob12_t3", "size"),
                             positivos=("target_cob12_t3", "sum"))
sp["prev"] = sp["positivos"] / sp["filas"] * 100
prev_mes = ds.groupby("fecha_mes")["target_cob12_t3"].mean() * 100
split_mes = ds.groupby("fecha_mes")["split"].first()
out["modelo"] = dict(
    embudo=[["Ventas crudas (mes-tienda-SKU)", len(v0)], ["Sin claves duplicadas, devoluciones neteadas", len(v1)],
            ["Panel ventas × stock", 297022], ["Con stock en t", 294301], ["No discontinuadas en t", 292241],
            ["Con 3+ meses de historia", 271722], ["Con etiqueta observable en t+3 (universo)", len(ds)]],
    split=[dict(split=s, desde=sp.loc[s, "desde"].strftime("%Y-%m"), hasta=sp.loc[s, "hasta"].strftime("%Y-%m"),
                filas=int(sp.loc[s, "filas"]), positivos=int(sp.loc[s, "positivos"]), prev=r(sp.loc[s, "prev"], 2))
           for s in ["train", "validacion", "embargo", "test"]],
    prev_meses=[d.strftime("%Y-%m") for d in prev_mes.index], prev=[r(x, 2) for x in prev_mes], prev_split=split_mes.tolist(),
    prevalencia=[2.61, 3.40], positivos=[5260, int(ds["target_cob12_t3"].sum())],
    filas=len(ds), posiciones=int(ds.groupby(["id_tienda", "id_producto"]).ngroups), skus=int(ds["id_producto"].nunique()),
    features=60, features_num=55, features_cat=5, onehot=106)
assert "201,306" in log

json.dump(out, open(os.path.join(RES, "comparativo_antes_despues.json"), "w", encoding="utf-8"),
          ensure_ascii=False, default=lambda o: o.item() if hasattr(o, "item") else str(o))
print("OK: resultados/comparativo_antes_despues.json")
