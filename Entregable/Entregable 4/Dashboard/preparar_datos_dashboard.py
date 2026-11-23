"""Entregable 4 - data for the HTML dashboard (alert list for the last month + model performance).

What it does:
  1. Production model: same HistGradientBoosting configuration chosen in modelo_final_v4.py, re-trained on every
     labelled row of dataset v4 (mar-22 to may-26), and used to score the last month of data (ago-26), whose label
     is not known yet. Scoring rows come from:
        VERSION_DATASET=v4 EXPORTAR_SCORING=1 python "Entregable/Entregable 2/Modelo/construir_dataset_modelo.py"
  2. Proposed flow on ago-26: block A = rule (coverage > 12 months), block B = the 150 positions with the highest
     model score outside block A (k_b from modelo_final_v4_resultados.json).
  3. For every alert: capital at cost, the three signals that stand out most, a suggested action (the store decides)
     and, for transfers, the store that sells the SKU fastest.
  4. Monthly hits of the flow vs the rule at the same quota in validation 2025 and test 2026, with the evaluation
     model (train <= dic-24), so the dashboard can show where the model adds value.
Output: Dashboard/datos_dashboard.json, read by armar_dashboard.py.

Run from the repo root:  python "Entregable/Entregable 4/Dashboard/preparar_datos_dashboard.py"
"""
import json
import os
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "4")
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier

ROOT = Path(__file__).resolve().parents[3]
DS = ROOT / "Datasets_Modelo"
DATA = ROOT / "Datasets_Normalizados"
OUT = Path(__file__).resolve().parent
RES = json.loads((ROOT / "Entregable/Entregable 4/Modelo/resultados/modelo_final_v4_resultados.json").read_text(encoding="utf-8"))
TARGET = "target_cob12_t3"
K_B = RES["punto_operacion"]["k_bloque_b"]
CAP_TIENDA = 25                # upper end of 15-25 interventions per store per month (E1)
FACTOR_COSTO_OC = 1.2321       # same assumption as the dataset (22 SKUs without catalogue cost)

raw = pd.read_parquet(DS / "dataset_entrenamiento_v4.parquet")
sco = pd.read_parquet(DS / "dataset_scoring_v4.parquet")
features = [c for c in raw.columns if c not in {"fecha_mes", "id_tienda", "id_producto", "costo_imputado", TARGET, "split"}]
cat = [c for c in features if raw[c].dtype == object]
num = [c for c in features if c not in cat]
for df in (raw, sco):
    for c in num:
        df[c] = df[c].replace([np.inf, -np.inf], [1000.0, -1000.0])


def to_cat(X, ref):
    X = X.copy()
    for c in cat:
        X[c] = pd.Categorical(X[c], categories=sorted(ref[c].dropna().unique()))
    return X


def hgb():
    return HistGradientBoostingClassifier(max_iter=300, learning_rate=.05, class_weight="balanced",
                                          categorical_features="from_dtype", random_state=0)


# ---------------- 1. production model on all labelled rows -> score ago-26 ----------------
m_prod = hgb().fit(to_cat(raw[features], raw), raw[TARGET].astype(int))
sco["score"] = m_prod.predict_proba(to_cat(sco[features], raw))[:, 1]
sco["percentil"] = sco["score"].rank(pct=True)
mes = pd.Timestamp(sco["fecha_mes"].max())

# capital at cost (same rule as Entregable 2 insights: catalogue cost, else purchase-order cost x factor)
catalogo = pd.read_csv(DATA / "Productos_catalogo.csv").drop_duplicates("id_producto")   # same as E2 insights
oc = pd.read_csv(DATA / "Ordenes_Compra.csv")
oc["m"] = oc["unidades"] * oc["costo_unitario_ars"]
c_oc = oc.groupby("id_producto")["m"].sum() / oc.groupby("id_producto")["unidades"].sum() * FACTOR_COSTO_OC
catalogo["costo"] = catalogo["costo_unitario"].fillna(catalogo["id_producto"].map(c_oc))
sco["costo_unit"] = sco["id_producto"].map(catalogo.set_index("id_producto")["costo"]).fillna(0)
sco["capital_ars"] = sco["stock_disponible"] * sco["costo_unit"]
tiendas = pd.read_csv(DATA / "Tiendas.csv").set_index("id_tienda")
sco["tienda"] = sco["id_tienda"].map(tiendas["nombre_tienda"])
sco["provincia"] = sco["id_tienda"].map(tiendas["provincia"])

# ---------------- 2. proposed flow ----------------
A = sco["cobertura"] > 12
B = sco.index.isin(sco[~A].nlargest(K_B, "score").index)
sco["bloque"] = np.where(A, "A", np.where(B, "B", ""))
al = sco[sco["bloque"] != ""].copy()

# ---------------- 3. signals, action and destination ----------------
# signals: the variables with the largest permutation importance, read in the direction that raises the risk;
# for each alert we keep the three where the position sits furthest into the risky tail of the month.
SENALES = [  # column, direction (+1: a high value raises the risk), label builder
    ("cobertura", 1, lambda r: f"cobertura de {fmt_cob(r.cobertura)}"),
    ("u6_suma", -1, lambda r: f"{r.u6_suma:.0f} u. vendidas en los últimos 6 meses"),
    ("meses_sin_venta", 1, lambda r: f"{r.meses_sin_venta:.0f} meses seguidos sin venta"),
    ("stock_vs_prom_sku", 1, lambda r: f"stock {f1(r.stock_vs_prom_sku)} veces el promedio del SKU por tienda"),
    ("tendencia_u3_vs_u12", -1, lambda r: f"venta del trimestre {pct(r.tendencia_u3_vs_u12)} contra su ritmo anual"),
    ("cobertura_sku_cadena", 1, lambda r: f"el SKU tiene {fmt_cob(r.cobertura_sku_cadena)} de cobertura en toda la cadena"),
]


def f1(v):
    return f"{v:.1f}".replace(".", ",")


def fmt_cob(v):
    return "más de 12 meses sin venta" if v >= 999 else f"{f1(v)} meses"


def pct(v):
    return f"{(v - 1) * 100:+.0f}%" if np.isfinite(v) and v > -999 else "sin dato"


ranks = pd.DataFrame({c: (sco[c] * d).rank(pct=True) for c, d, _ in SENALES}, index=sco.index)


def motivos(r):
    rk = ranks.loc[r.name].sort_values(ascending=False)
    lab = {c: f for c, _, f in SENALES}
    return [lab[c](r) for c in rk.index[:3]]


# fastest-selling store for the same SKU with low coverage (transfer destination)
dest = (sco[(sco["cobertura"] < 6) & (sco["u12_prom"] > 0)]
        .sort_values("u12_prom", ascending=False).groupby("id_producto").head(3))
dest_map = {k: g[["id_tienda", "tienda", "u12_prom", "cobertura"]].to_dict("records") for k, g in dest.groupby("id_producto")}


def accion(r):
    """Suggested action, in this order. The store and Comercial decide; this only proposes.
    Transfer only when the SKU is not overstocked in the chain (coverage < 12) and another store sells it at
    >= 1 u./month with < 3 months of coverage: the problem is where the stock sits, not how much there is."""
    cands = [d for d in dest_map.get(r.id_producto, []) if d["id_tienda"] != r.id_tienda
             and d["u12_prom"] >= 1 and d["cobertura"] < 3]
    if cands and r.cobertura_sku_cadena < 12:
        d = cands[0]
        return "Transferir", f"a {d['tienda']} ({f1(d['u12_prom'])} u./mes, cobertura {f1(d['cobertura'])} meses)"
    if r.uds_oc_pendientes > 0:
        return "Frenar compra", f"{r.uds_oc_pendientes:.0f} u. en órdenes de compra pendientes del SKU"
    if r.bloque == "B" and r.meses_sin_venta < 3:
        return "Frenar reposición", "todavía vende: no reponer y revisar exhibición antes de liquidar"
    return "Liquidar", "el SKU está sobrestockeado en la cadena o ninguna tienda lo vende rápido"


al["motivos"] = al.apply(motivos, axis=1)
acc = al.apply(accion, axis=1)
al["accion"] = [a for a, _ in acc]
al["detalle_accion"] = [d for _, d in acc]
al = al.sort_values(["id_tienda", "capital_ars"], ascending=[True, False])
al["prioridad_tienda"] = al.groupby("id_tienda").cumcount() + 1
al["dentro_capacidad"] = al["prioridad_tienda"] <= CAP_TIENDA

alertas = [{
    "tienda_id": r.id_tienda, "tienda": r.tienda, "provincia": r.provincia, "region": r.region, "formato": r.formato,
    "sku": r.id_producto, "categoria": r.categoria, "subcategoria": r.subcategoria, "proveedor": r.proveedor,
    "bloque": r.bloque, "score": round(float(r.score), 4), "percentil": round(float(r.percentil) * 100, 1),
    "stock": int(r.stock_disponible), "venta_12m_prom": round(float(r.u12_prom), 2), "venta_6m": int(r.u6_suma),
    "cobertura": None if r.cobertura >= 999 else round(float(r.cobertura), 1),
    "meses_sin_venta": int(r.meses_sin_venta), "oc_pendientes": int(r.uds_oc_pendientes),
    "capital_ars": round(float(r.capital_ars)), "costo_imputado": int(r.costo_imputado),
    "motivos": r.motivos, "accion": r.accion, "detalle_accion": r.detalle_accion,
    "prioridad_tienda": int(r.prioridad_tienda), "dentro_capacidad": bool(r.dentro_capacidad),
} for r in al.itertuples()]

tiendas_res = []
for tid, g in sco.groupby("id_tienda"):
    a = al[al["id_tienda"] == tid]
    tiendas_res.append({"tienda_id": tid, "tienda": g["tienda"].iloc[0], "region": g["region"].iloc[0],
                        "formato": g["formato"].iloc[0], "posiciones": len(g),
                        "capital_total_ars": round(float(g["capital_ars"].sum())),
                        "alertas_a": int((a["bloque"] == "A").sum()), "alertas_b": int((a["bloque"] == "B").sum()),
                        "capital_alertas_ars": round(float(a["capital_ars"].sum()))})

# ---------------- 4. monthly hits, validation 2025 and test 2026 (evaluation model, train <= dic-24) ----------------
tr = raw["split"] == "train"
m_eval = hgb().fit(to_cat(raw.loc[tr, features], raw.loc[tr]), raw.loc[tr, TARGET].astype(int))
mensual = []
for sp in ("validacion", "test"):
    d = raw[raw["split"] == sp].copy()
    d["score"] = m_eval.predict_proba(to_cat(d[features], raw.loc[tr]))[:, 1]
    for f, g in d.groupby("fecha_mes"):
        a = g["cobertura"] > 12
        b = g.index.isin(g[~a].nlargest(K_B, "score").index)
        n = int(a.sum()) + int(b.sum())
        regla = g.nlargest(n, "cobertura").index
        y = g[TARGET].astype(int)
        mensual.append({"mes": pd.Timestamp(f).strftime("%Y-%m"), "periodo": sp, "alertas": n, "positivos": int(y.sum()),
                        "vp_flujo": int(y[a | b].sum()), "vp_regla_mismo_cupo": int(y.loc[regla].sum()),
                        "vp_bloque_b": int(y[b].sum())})

out = {
    "mes_lista": mes.strftime("%Y-%m"), "k_bloque_b": K_B, "capacidad_tienda": CAP_TIENDA,
    "modelo": "HistGradientBoosting reentrenado con todas las filas etiquetadas (mar-22 a may-26)",
    "universo_mes": {"posiciones": len(sco), "capital_total_ars": round(float(sco["capital_ars"].sum())),
                     "posiciones_cob12": int(A.sum()), "capital_cob12_ars": round(float(sco.loc[A, "capital_ars"].sum()))},
    "alertas": alertas, "tiendas": tiendas_res, "mensual": mensual,
    "resultados_modelo": {k: RES[k] for k in ("insumos", "modelo_elegido", "punto_operacion", "flujo", "roi",
                                              "importancia_permutacion", "segmentos")},
    "curvas": {sp: RES["periodos"][sp]["curva"] for sp in ("validacion", "test")},
    "pr_auc": {sp: RES["periodos"][sp]["pr_auc"] for sp in ("validacion", "test")},
    "positivos": {sp: RES["periodos"][sp]["positivos"] for sp in ("validacion", "test")},
}
(OUT / "datos_dashboard.json").write_text(json.dumps(out, ensure_ascii=False, default=float), encoding="utf-8")
print(f"Mes {out['mes_lista']}: {len(sco):,} posiciones · bloque A {int(A.sum())} · bloque B {int(B.sum())} · "
      f"alertas {len(alertas)} · dentro de capacidad {int(al['dentro_capacidad'].sum())}")
print(al["accion"].value_counts().to_string())
print(pd.DataFrame(mensual).groupby("periodo")[["vp_flujo", "vp_regla_mismo_cupo"]].sum().to_string())
