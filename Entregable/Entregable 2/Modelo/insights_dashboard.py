# -*- coding: utf-8 -*-
"""
Datos de insight para el dashboard del Entregable 2 y la presentacion.
Lee Datasets_Normalizados (serie mensual) y Datasets_Modelo/dataset_entrenamiento_v2.parquet.
Salida: resultados/insights.json (lo consume EDA/antes_despues.py para armar el HTML).
Todo lo que usa el modelo de prueba se entrena SOLO en train; las curvas se miden en validacion.
"""
import os, sys, json
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
DATA = os.path.join(ROOT, "Datasets_Normalizados"); RES = os.path.join(BASE, "resultados")
K = ["fecha_mes", "id_tienda", "id_producto"]; M = 1e6
V = os.environ.get("VERSION_DATASET", "v3")
OUT = {}

# ------------------------------------------------------------------ panel limpio (todas las posiciones)
v = pd.read_csv(os.path.join(DATA, "Ventas_SKU_tienda_mensual.csv"))
pos = v[v["unidades_vendidas"] >= 0].drop_duplicates(K)
neg = v[v["unidades_vendidas"] < 0]
vn = pd.concat([pos, neg]).groupby(K, as_index=False)[["unidades_vendidas", "venta_neta"]].sum()
s = pd.read_csv(os.path.join(DATA, "Stock_SKU_tienda_mensual.csv")).drop_duplicates(K)
s["stock_disponible"] = s["stock_disponible"].clip(lower=0)
cat = pd.read_csv(os.path.join(DATA, "Productos_catalogo.csv")).drop_duplicates("id_producto")
oc = pd.read_csv(os.path.join(DATA, "Ordenes_Compra.csv")); oc["m"] = oc.unidades * oc.costo_unitario_ars
c_oc = oc.groupby("id_producto")["m"].sum() / oc.groupby("id_producto")["unidades"].sum() * 1.2321
cat["costo"] = cat["costo_unitario"].fillna(cat["id_producto"].map(c_oc))
d = s.merge(vn, on=K); d["fecha_mes"] = pd.to_datetime(d["fecha_mes"])
d = d.sort_values(["id_tienda", "id_producto", "fecha_mes"])
d["u12"] = d.groupby(["id_tienda", "id_producto"])["unidades_vendidas"].transform(lambda x: x.rolling(12, min_periods=1).mean())
d = d.merge(cat[["id_producto", "categoria", "costo"]], on="id_producto")
d["cob"] = np.where(d["u12"] > 0, d["stock_disponible"] / d["u12"].where(d["u12"] > 0), np.inf)
cs = d[d["stock_disponible"] > 0]

# 1. venta mensual 2025 vs 2026 (bruto: 2026 no trae devoluciones)
pos["fecha_mes"] = pd.to_datetime(pos["fecha_mes"])
b = pos.groupby("fecha_mes")["venta_neta"].sum() / M
OUT["venta_25_26"] = {"meses": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago"],
                      "v2025": [round(b[f"2025-{m:02d}-01"], 1) for m in range(1, 9)],
                      "v2026": [round(b[f"2026-{m:02d}-01"], 1) for m in range(1, 9)]}
st = cs.groupby("fecha_mes")["stock_disponible"].sum()
OUT["stock_vs_venta_idx"] = {"meses": [x.strftime("%Y-%m") for x in st.loc["2025-01":].index],
                             "stock": [round(x, 1) for x in (st.loc["2025-01":] / st.loc["2025-01-01"] * 100)],
                             "venta": [round(x, 1) for x in (b.loc["2025-01":] / b.loc["2025-01-01"] * 100)]}

# 2. percentiles de cobertura por mes (cola que se engorda)
cf = cs[np.isfinite(cs["cob"])]
qq = cf[cf["fecha_mes"] >= "2023-01-01"].groupby("fecha_mes")["cob"].quantile([.5, .9, .99]).unstack()
OUT["cobertura_pct"] = {"meses": [x.strftime("%Y-%m") for x in qq.index], "p50": qq[.5].round(1).tolist(),
                        "p90": qq[.9].round(1).tolist(), "p99": qq[.99].round(1).tolist()}
# posiciones en rojo y capital inmovilizado en rojo por mes
roj = cs[(cs["cob"] > 12)].copy(); roj["cap"] = roj["stock_disponible"] * roj["costo"]
rm = roj[roj["fecha_mes"] >= "2023-01-01"].groupby("fecha_mes").agg(pos=("cob", "size"), cap=("cap", "sum"))
OUT["rojo_mes"] = {"meses": [x.strftime("%Y-%m") for x in rm.index], "posiciones": rm["pos"].tolist(),
                   "capital": (rm["cap"] / M).round(1).tolist()}
ult = roj[roj["fecha_mes"] == roj["fecha_mes"].max()]
bc = ult.groupby("categoria").agg(pos=("cob", "size"), cap=("cap", "sum")).sort_values("cap", ascending=False)
tot_cat = cs[cs["fecha_mes"] == cs["fecha_mes"].max()].assign(cap=lambda x: x.stock_disponible * x.costo).groupby("categoria")["cap"].sum()
OUT["rojo_ago26_cat"] = {"cat": bc.index.tolist(), "posiciones": bc["pos"].tolist(), "capital": (bc["cap"] / M).round(1).tolist(),
                         "pct_capital_cat": (bc["cap"] / tot_cat.reindex(bc.index) * 100).round(1).tolist(),
                         "total_pos": int(len(ult)), "total_cap": round(ult["cap"].sum() / M, 1)}
sk = ult.groupby("id_producto")["cap"].sum().sort_values(ascending=False)
OUT["rojo_ago26_sku"] = {"skus": int(len(sk)), "top20_pct": round(sk.head(20).sum() / sk.sum() * 100, 1),
                         "tiendas_por_sku_top10": ult[ult.id_producto.isin(sk.head(10).index)].groupby("id_producto").size().reindex(sk.head(10).index).tolist(),
                         "top10": sk.head(10).index.tolist(), "top10_cap": (sk.head(10) / M).round(1).tolist()}

# ------------------------------------------------------------------ dataset del modelo
ds = pd.read_parquet(os.path.join(ROOT, "Datasets_Modelo", f"dataset_entrenamiento_{V}.parquet"))
y = "target_cob12_t3"
pm = ds.groupby("fecha_mes").agg(tasa=(y, "mean"), filas=(y, "size"), split=("split", "first"))
OUT["prevalencia_mes"] = {"meses": [x.strftime("%Y-%m") for x in pm.index], "tasa": (pm["tasa"] * 100).round(2).tolist(),
                          "split": pm["split"].tolist()}
# transiciones t -> t+3
hoy = (ds["cobertura"] > 12)
NOF_ = ["fecha_mes", "id_tienda", "id_producto", "costo_imputado", y, "split"]
spl = ds.groupby("split").agg(desde=("fecha_mes", "min"), hasta=("fecha_mes", "max"), filas=(y, "size"), positivos=(y, "sum"), tasa=(y, "mean"))
OUT["resumen"] = {"version": V, "filas": int(len(ds)), "positivos": int(ds[y].sum()), "prevalencia": round(ds[y].mean() * 100, 2),
                  "n_num": int(sum(ds[c].dtype != object for c in ds.columns if c not in NOF_)),
                  "n_cat": int(sum(ds[c].dtype == object for c in ds.columns if c not in NOF_)),
                  "posiciones": int(ds.groupby(["id_tienda", "id_producto"]).ngroups), "skus": int(ds["id_producto"].nunique()),
                  "tasa_hasta_2025": round(ds[ds.fecha_mes < "2026-01-01"][y].mean() * 100, 1), "tasa_2026": round(ds[ds.fecha_mes >= "2026-01-01"][y].mean() * 100, 1),
                  "split": {k: {"desde": r.desde.strftime("%b-%y"), "hasta": r.hasta.strftime("%b-%y"), "filas": int(r.filas), "positivos": int(r.positivos),
                                "tasa": round(r.tasa * 100, 2)} for k, r in spl.iterrows()}}
OUT["transicion"] = {"sano_sano": int((~hoy & (ds[y] == 0)).sum()), "sano_rojo": int((~hoy & (ds[y] == 1)).sum()),
                     "rojo_sano": int((hoy & (ds[y] == 0)).sum()), "rojo_rojo": int((hoy & (ds[y] == 1)).sum())}
# tasa por categoria y por tienda (con intervalo binomial 95%)
tv = ds[ds["split"].isin(["train", "validacion"])]
bt = tv.groupby("id_tienda")[y].agg(["mean", "size"])
bt["ic"] = 1.96 * np.sqrt(bt["mean"] * (1 - bt["mean"]) / bt["size"])
media = tv[y].mean()
bt = bt.sort_values("mean")
OUT["tasa_tienda"] = {"tiendas": bt.index.tolist(), "tasa": (bt["mean"] * 100).round(2).tolist(),
                      "ic": (bt["ic"] * 100).round(2).tolist(), "media": round(media * 100, 2),
                      "fuera_ic": int(((bt["mean"] - bt["ic"] > media) | (bt["mean"] + bt["ic"] < media)).sum())}
bcat = tv.groupby("categoria")[y].mean().sort_values(ascending=False)
OUT["tasa_categoria"] = {"cat": bcat.index.tolist(), "tasa": (bcat * 100).round(2).tolist()}
# concentracion de positivos por SKU
psku = tv[tv[y] == 1].groupby("id_producto").size().sort_values(ascending=False)
cum = psku.cumsum() / psku.sum()
OUT["conc_sku"] = {"skus_con_positivos": int(len(psku)), "skus_universo": int(tv["id_producto"].nunique()),
                   "n50": int((cum < .5).sum() + 1), "n80": int((cum < .8).sum() + 1)}
# mapa de riesgo: cobertura actual x tendencia
cb = pd.cut(tv["cobertura"].replace(np.inf, 999), [0, 3, 6, 9, 12, np.inf], labels=["<3", "3-6", "6-9", "9-12", ">12"], right=False)
tb = pd.cut(tv["tendencia_u3_vs_u12"].fillna(0), [-np.inf, .5, .8, 1.2, np.inf], labels=["cae >50%", "cae 20-50%", "estable", "sube >20%"])
hm = tv.groupby([cb, tb], observed=False)[y].agg(["mean", "size"])
OUT["mapa_riesgo"] = {"cob": ["<3", "3-6", "6-9", "9-12", ">12"], "tend": ["cae >50%", "cae 20-50%", "estable", "sube >20%"],
                      "tasa": [[round(hm.loc[(c, t), "mean"] * 100, 1) if hm.loc[(c, t), "size"] >= 30 else None for t in ["cae >50%", "cae 20-50%", "estable", "sube >20%"]] for c in ["<3", "3-6", "6-9", "9-12", ">12"]],
                      "n": [[int(hm.loc[(c, t), "size"]) for t in ["cae >50%", "cae 20-50%", "estable", "sube >20%"]] for c in ["<3", "3-6", "6-9", "9-12", ">12"]]}
# de donde vienen los positivos: cobertura actual de los que caen en rojo
pos_ = tv[tv[y] == 1]
OUT["origen_positivos"] = {"bandas": ["<6", "6-9", "9-12", ">12 (ya rojo)"],
                           "pct": [round(x, 1) for x in (pd.cut(pos_["cobertura"].replace(np.inf, 999), [0, 6, 9, 12, np.inf], right=False)
                                                         .value_counts(normalize=True, sort=False) * 100).tolist()]}
# senal univariada
sen = pd.read_csv(os.path.join(RES, f"senal_univariada_{V}.csv"))
OUT["senal"] = sen[["feature", "auc_train", "auc_validacion", "auc_test"]].head(20).to_dict("records")
OUT["senal_sin"] = int((sen["auc_train"] < 0.55).sum()); OUT["n_features_num"] = int(len(sen))
imp = pd.read_csv(os.path.join(RES, f"importancia_permutacion_{V}.csv"), index_col=0)["delta_pr_auc"]
OUT["importancia"] = {"feature": imp.head(12).index.tolist(), "valor": imp.head(12).round(4).tolist()}

# curva de capacidad (modelo de prueba entrenado en train, medido en validacion)
NOF = ["fecha_mes", "id_tienda", "id_producto", "costo_imputado", y, "split"]
Rc = ds.copy()
for c in Rc.columns:
    if Rc[c].dtype == object and c not in ("id_tienda", "id_producto", "split"): Rc[c] = Rc[c].astype("category")
Rc = Rc.replace([np.inf], 1e3); F = [c for c in ds.columns if c not in NOF]
tr = Rc[Rc["split"] == "train"]
gb = HistGradientBoostingClassifier(max_iter=300, learning_rate=.05, class_weight="balanced",
                                    categorical_features="from_dtype", random_state=0).fit(tr[F], tr[y])
curva = {}
for sp in ["validacion", "test"]:
    va = Rc[Rc["split"] == sp].copy(); va["p"] = gb.predict_proba(va[F])[:, 1]
    ks = [50, 100, 200, 300, 420, 500, 600, 700, 850, 1000]
    rm_, rr_, pm_ = [], [], []
    for k in ks:
        tm = va.sort_values("p", ascending=False).groupby("fecha_mes").head(k)
        tr_ = va.sort_values("cobertura", ascending=False).groupby("fecha_mes").head(k)
        rm_.append(round(tm[y].sum() / va[y].sum() * 100, 1)); rr_.append(round(tr_[y].sum() / va[y].sum() * 100, 1))
        pm_.append(round(tm[y].mean() * 100, 1))
    curva[sp] = {"k": ks, "recall_modelo": rm_, "recall_regla": rr_, "precision_modelo": pm_,
                 "positivos_mes": round(va.groupby("fecha_mes")[y].sum().mean())}
OUT["capacidad"] = curva
json.dump(OUT, open(os.path.join(RES, "insights.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)
for k in ["rojo_ago26_cat", "rojo_ago26_sku", "tasa_tienda", "conc_sku", "origen_positivos", "transicion", "senal_sin"]:
    print(k, OUT[k] if k != "tasa_tienda" else {kk: OUT[k][kk] for kk in ("media", "fuera_ic")})
print("mapa", OUT["mapa_riesgo"]["tasa"])
print("capacidad val", curva["validacion"])
