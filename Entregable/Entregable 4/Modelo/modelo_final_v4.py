"""Entregable 4 (final) - re-evaluation of the model on dataset v4, applying the Entregable 3 feedback.

What it does (all on Datasets_Modelo/dataset_entrenamiento_v4*.parquet, the dataset delivered in Entregable 2):
  1. Re-trains the same Stage-3 configuration (HistGradientBoosting, ExtraTrees, LightGBM and their
     monthly percentile-rank ensemble) plus a logistic regression, with the same temporal policy.
  2. Model selection on the INTERNAL validation (train <= mar-2024, embargo apr-jun 2024, eval jul-dec 2024):
     the ensemble is kept only if it beats gradient boosting there (feedback 7.1).
  3. One metric for every stage: Recall@K and net value at the operating quota, PR-AUC as secondary.
  4. Operating quota chosen by value, not by capacity: alerts are added in tranches of 50 per month while the
     tranche precision in validation 2025 stays above the break-even precision (feedback 7.2 and 9).
  5. Value per correct action from the reproducible Entregable 2 figure (ARS 184,1 M / 882 positions);
     the Entregable 1 figure (ARS 83,9 M / 661) is kept as sensitivity (feedback 3.3-3.6).
  6. Two ROIs: automating the list with the rule (no model) and the incremental ROI of the model.
  7. Permutation importance on the final ranking, Wilson confidence intervals by segment, and the
     persistence of "no sale" months in 2025 vs 2026 (feedback 7.3, 7.4, 8.2).
The test 2026 block is only used for the final report, never to choose anything.

Run from the repo root:  python "Entregable/Entregable 4/Modelo/modelo_final_v4.py"
"""
import json
import os
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "4")
import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.preprocessing import OrdinalEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[3]
DS = ROOT / "Datasets_Modelo"
OUT = Path(__file__).resolve().parent / "resultados"
OUT.mkdir(exist_ok=True)
TARGET = "target_cob12_t3"
CAPACIDAD = 600          # ceiling: 15-25 interventions x 28 stores (420-700); a ceiling, not a goal
TRAMO = 50

# ---------------- economic inputs (Entregable 3, Part B workbook "Supuestos") ----------------
ARS_USD = 1560.0
COSTO_MENSUAL, MESES_AHORRO = 0.05, 3
PCT_TEMPRANA, PRECIO_TEMPRANA, PCT_TARDIO, PRECIO_TARDIO, MARGEN = 0.85, 0.825, 0.70, 0.55, 0.45
CIERRE_TARDIO, EXITO, ADOPCION = 0.25, 0.60, 0.70
COSTO_FP_ARS = 4900.0
HORAS_AHORRO_USD = 480 * 12 * 0.70           # 4.032
INVERSION, RECURRENTE = 9570.0, 5960.0       # Part B 3.2
DESARROLLO_MODELO = 3000.0 * 1.10            # model development + its 10% contingency
APOYO_EXTERNO = 800.0                        # quarterly external support (re-training)
MANTENEDOR = 3120.0                          # existing staff time (opportunity cost, not cash)
DS_HORA, HORAS_MES = 18.0, 160               # sensitivity: data scientist 3-4 months (1,5x analyst rate)


def valor_unitario(capital_ars):
    cap = capital_ars / ARS_USD
    mejora = cap * (PCT_TEMPRANA * PRECIO_TEMPRANA - PCT_TARDIO * PRECIO_TARDIO) / (1 - MARGEN)
    ahorro = cap * COSTO_MENSUAL * MESES_AHORRO
    accion = EXITO * (ahorro + mejora * CIERRE_TARDIO)
    vp, fp = ADOPCION * accion, ADOPCION * COSTO_FP_ARS / ARS_USD
    return {"capital_por_posicion_ars": capital_ars, "capital_por_posicion_usd": cap,
            "beneficio_accion_usd": accion, "valor_vp_usd": vp, "costo_fp_usd": fp,
            "precision_equilibrio": fp / (vp + fp)}


VALOR = {"base_e2": valor_unitario(184.1e6 / 882), "sensibilidad_e1": valor_unitario(83.9e6 / 661)}
VP, FP = VALOR["base_e2"]["valor_vp_usd"], VALOR["base_e2"]["costo_fp_usd"]
P_EQ = VALOR["base_e2"]["precision_equilibrio"]

LOG = []


def log(s=""):
    print(s, flush=True)
    LOG.append(s)


# ---------------- data ----------------
raw = pd.read_parquet(DS / "dataset_entrenamiento_v4.parquet")
raw["fecha_mes"] = raw["fecha_mes"].dt.strftime("%Y-%m-%d")
trf = pd.read_parquet(DS / "dataset_entrenamiento_v4_transformado.parquet")
assert len(raw) == len(trf) == 201310
features = [c for c in raw.columns if c not in {"fecha_mes", "id_tienda", "id_producto", "costo_imputado", TARGET, "split"}]
cat = [c for c in features if raw[c].dtype == object]
num = [c for c in features if c not in cat]
for c in num:
    raw[c] = raw[c].replace([np.inf, -np.inf], [1000.0, -1000.0])
lin_cols = [c for c in trf.columns if c not in {"fecha_mes", "id_tienda", "id_producto", "costo_imputado", TARGET, "split"}]
Y = raw[TARGET].astype(int).to_numpy()
split = raw["split"].to_numpy()
fecha = raw["fecha_mes"].to_numpy()


def prep(train_mask):
    """Same preparation as Stage 3: categories/encoder/medians fitted on the training rows only."""
    X = raw[features].copy()
    Xc = X.copy()
    for c in cat:
        Xc[c] = pd.Categorical(Xc[c], categories=sorted(Xc.loc[train_mask, c].dropna().unique()))
    enc = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1, encoded_missing_value=-2)
    enc.fit(X.loc[train_mask, cat].fillna("Desconocido"))
    Xe = X.copy()
    Xe[cat] = enc.transform(X[cat].fillna("Desconocido"))
    med = X.loc[train_mask, num].median()
    for c in num:
        Xe[c] = Xe[c].fillna(med[c])
    Xe = Xe.astype("float32")
    XL = trf[lin_cols].astype("float64").fillna(0.0)
    sc = StandardScaler().fit(XL[train_mask])
    XL = pd.DataFrame(sc.transform(XL), columns=lin_cols, index=XL.index)
    return Xc, Xe, XL


def new_models():
    return {
        "HistGradientBoosting": HistGradientBoostingClassifier(max_iter=300, learning_rate=.05, class_weight="balanced",
                                                               categorical_features="from_dtype", random_state=0),
        "ExtraTrees": ExtraTreesClassifier(n_estimators=350, min_samples_leaf=15, max_features=.8, n_jobs=4,
                                           random_state=0, class_weight="balanced_subsample"),
        "LightGBM": LGBMClassifier(objective="binary", class_weight="balanced", random_state=0, n_jobs=4, verbosity=-1,
                                   n_estimators=700, learning_rate=.025, num_leaves=45, min_child_samples=40,
                                   subsample=.8, subsample_freq=1, colsample_bytree=.8, reg_lambda=4, reg_alpha=.5),
        "Logistica": LogisticRegression(C=0.1, class_weight="balanced", max_iter=3000),
    }


def fit_score(train_mask, score_masks):
    Xc, Xe, XL = prep(train_mask)
    data = {"HistGradientBoosting": Xc, "LightGBM": Xc, "ExtraTrees": Xe, "Logistica": XL}
    models, scores = new_models(), {k: {} for k in score_masks}
    for name, m in models.items():
        t0 = time.time()
        m.fit(data[name][train_mask], Y[train_mask])
        for key, mask in score_masks.items():
            scores[key][name] = m.predict_proba(data[name][mask])[:, 1]
        log(f"  fit {name:22s} {time.time() - t0:6.1f}s")
    return models, scores, data


def add_rank_scores(d, sc):
    """Monthly percentile ranks; ensemble = mean of the three tree ranks (Stage 3 definition)."""
    for name, p in sc.items():
        d["s_" + name] = p
        d["pct_" + name] = pd.Series(p, index=d.index).groupby(d["fecha_mes"]).rank(method="average", pct=True)
    d["s_Ensamble"] = d[["pct_HistGradientBoosting", "pct_ExtraTrees", "pct_LightGBM"]].mean(axis=1)
    d["s_Regla"] = d["cobertura"].clip(upper=1000)
    return d


def top_k(d, score, k, eligible=None):
    tmp = pd.DataFrame({"m": d["fecha_mes"].to_numpy(), "s": np.asarray(score, float)}, index=d.index)
    if eligible is not None:
        tmp = tmp[np.asarray(eligible)]
    tmp = tmp.sort_values(["m", "s"], ascending=[True, False], kind="mergesort")
    pos = tmp.groupby("m", sort=False).cumcount()
    lim = k if np.isscalar(k) else tmp["m"].map(k)
    return d.index.isin(tmp.index[pos < lim])


def met(y, sel, meses, vp=VP, fp=FP):
    n, tp = int(sel.sum()), int(y[sel].sum())
    pos = int(y.sum())
    return {"alertas": n, "alertas_mes": round(n / meses, 1), "vp": tp, "fp": n - tp, "fn": pos - tp,
            "precision": tp / n if n else 0.0, "recall": tp / pos if pos else 0.0,
            "valor_neto_usd": round(tp * vp - (n - tp) * fp, 1),
            "valor_neto_mes_usd": round((tp * vp - (n - tp) * fp) / meses, 1)}


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (c - h, c + h)


results = {"insumos": {"dataset": "dataset_entrenamiento_v4", "filas": len(raw), "valor_unitario": VALOR,
                       "capacidad_techo_alertas_mes": CAPACIDAD, "tramo": TRAMO}}
log(f"Dataset v4: {len(raw):,} filas · features {len(features)} ({len(cat)} cat) · lineal {len(lin_cols)}")
for k, v in VALOR.items():
    log(f"Valor {k}: capital/posicion USD {v['capital_por_posicion_usd']:.2f} · VP USD {v['valor_vp_usd']:.2f} · "
        f"FP USD {v['costo_fp_usd']:.2f} · precision de equilibrio {v['precision_equilibrio']:.1%}")

# =============== 1. internal validation 2024 (model selection) ===============
log("\n=== 1. VALIDACION INTERNA (train <= mar-24 · embargo abr-jun 24 · eval jul-dic 24) ===")
m_int_tr = (split == "train") & (fecha <= "2024-03-01")
m_int_ev = (split == "train") & (fecha >= "2024-07-01")
_, sc_int, _ = fit_score(m_int_tr, {"int": m_int_ev})
d_int = raw.loc[m_int_ev, ["fecha_mes", "cobertura", TARGET]].reset_index(drop=True)
d_int = add_rank_scores(d_int, sc_int["int"])
y_int = d_int[TARGET].to_numpy()
mi = d_int["fecha_mes"].nunique()
results["validacion_interna"] = {}
for k in (175, 300, 420, 600):
    row = {n: met(y_int, top_k(d_int, d_int["s_" + n], k), mi) for n in
           ("Regla", "Logistica", "HistGradientBoosting", "Ensamble")}
    results["validacion_interna"][f"top_{k}"] = row
    log(f" Top-{k}: " + " · ".join(f"{n} VP {r['vp']} rec {r['recall']:.1%}" for n, r in row.items()))
results["validacion_interna"]["positivos"] = int(y_int.sum())
results["validacion_interna"]["pr_auc"] = {n: float(average_precision_score(y_int, d_int["s_" + n])) for n in
                                           ("Regla", "Logistica", "HistGradientBoosting", "Ensamble")}

# =============== 2. final fit (train <= dic-24) -> validation 2025 and test 2026 ===============
log("\n=== 2. MODELO FINAL (train <= dic-24) ===")
m_tr = split == "train"
masks = {"train": m_tr, "validacion": split == "validacion", "test": split == "test"}
models, sc, data = fit_score(m_tr, masks)
D = {}
for key, mask in masks.items():
    d = raw.loc[mask, ["fecha_mes", "id_tienda", "id_producto", "categoria", "region", "cobertura",
                       "unidades_vendidas", "stock_disponible", TARGET]].reset_index(drop=True)
    D[key] = add_rank_scores(d, sc[key])

MODELOS = ("Regla", "Logistica", "HistGradientBoosting", "Ensamble")
results["periodos"] = {}
for key, d in D.items():
    y = d[TARGET].to_numpy()
    meses = d["fecha_mes"].nunique()
    r = {"meses": meses, "filas": len(d), "positivos": int(y.sum()), "prevalencia": float(y.mean()),
         "regla_fija": met(y, (d["cobertura"] > 12).to_numpy(), meses),
         "auc": {n: float(roc_auc_score(y, d["s_" + n])) for n in MODELOS},
         "pr_auc": {n: float(average_precision_score(y, d["s_" + n])) for n in MODELOS},
         "curva": {}}
    for k in range(TRAMO, 701, TRAMO):
        r["curva"][k] = {n: met(y, top_k(d, d["s_" + n], k), meses) for n in MODELOS}
    for k in (175,):
        r["curva"][k] = {n: met(y, top_k(d, d["s_" + n], k), meses) for n in MODELOS}
    results["periodos"][key] = r
    rf = r["regla_fija"]
    log(f"\n[{key}] filas {len(d):,} · positivos {r['positivos']:,} ({r['prevalencia']:.2%}) · meses {meses}")
    log(f"  regla fija cob>12: {rf['alertas_mes']}/mes VP {rf['vp']} prec {rf['precision']:.1%} rec {rf['recall']:.1%} "
        f"valor USD {rf['valor_neto_mes_usd']}/mes")
    log("  PR-AUC " + " · ".join(f"{n} {v:.3f}" for n, v in r["pr_auc"].items()))
    for k in (175, 300, 600):
        log(f"  Top-{k}: " + " · ".join(f"{n} VP {m['vp']} rec {m['recall']:.1%} prec {m['precision']:.1%} "
                                       f"val {m['valor_neto_mes_usd']:.0f}" for n, m in r["curva"][k].items()))

# ---- selection rule (feedback 7.1): ensemble only if it beats HGB in the internal validation ----
vi = results["validacion_interna"]
gana_int = all(vi[f"top_{k}"]["Ensamble"]["vp"] > vi[f"top_{k}"]["HistGradientBoosting"]["vp"] for k in (175, 300, 420))
MOD = "Ensamble" if gana_int else "HistGradientBoosting"
results["modelo_elegido"] = {"modelo": MOD, "ensamble_supera_hgb_en_validacion_interna": bool(gana_int)}
log(f"\nModelo elegido: {MOD} (ensamble supera a HGB en validacion interna Top-175/300/420: {gana_int})")

# =============== 3. operating point: tranches of 50 while tranche precision > break-even ===============
log(f"\n=== 3. PUNTO DE OPERACION (precision de equilibrio {P_EQ:.1%}) ===")


def tramos(d, score, eligible=None, kmax=CAPACIDAD):
    y = d[TARGET].to_numpy()
    rows, prev = [], np.zeros(len(d), bool)
    for k in range(TRAMO, kmax + 1, TRAMO):
        sel = top_k(d, score, k, eligible)
        new = sel & ~prev
        rows.append({"hasta": k, "alertas_tramo": int(new.sum()), "vp_tramo": int(y[new].sum()),
                     "precision_tramo": float(y[new].mean()) if new.sum() else 0.0})
        prev = sel
    return rows


dv, dt = D["validacion"], D["test"]
# model alone
tr_mod = tramos(dv, dv["s_" + MOD])
k_mod = 0
for t in tr_mod:
    if t["precision_tramo"] > P_EQ:
        k_mod = t["hasta"]
    else:
        break
# combined flow: block A = fixed rule (cob > 12) ; block B = model ranking outside A, tranches of 50
A_v = (dv["cobertura"] > 12).to_numpy()
tr_b = tramos(dv, dv["s_" + MOD], eligible=~A_v, kmax=CAPACIDAD)
a_mes_max = int(pd.Series(A_v).groupby(dv["fecha_mes"]).sum().max())
k_b = 0
for t in tr_b:
    if t["precision_tramo"] > P_EQ and t["hasta"] + a_mes_max <= CAPACIDAD:
        k_b = t["hasta"]
    else:
        break
results["punto_operacion"] = {"tramos_modelo_validacion": tr_mod, "tramos_bloque_b_validacion": tr_b,
                              "k_modelo_solo": k_mod, "k_bloque_b": k_b, "precision_equilibrio": P_EQ}
log(f"  {MOD} solo: tramos con precision > equilibrio hasta Top-{k_mod}")
log("  tramos bloque B (val 2025): " + ", ".join(f"{t['hasta']}:{t['precision_tramo']:.0%}" for t in tr_b))
log(f"  bloque B: {k_b} alertas/mes ademas de la regla (bloque A max {a_mes_max}/mes en val)")

flujo = {}
for key, d in (("validacion", dv), ("test", dt)):
    y = d[TARGET].to_numpy()
    meses = d["fecha_mes"].nunique()
    A = (d["cobertura"] > 12).to_numpy()
    B = top_k(d, d["s_" + MOD], k_b, eligible=~A) if k_b else np.zeros(len(d), bool)
    F = A | B
    nA = pd.Series(A).groupby(d["fecha_mes"]).sum()
    regla_igual = top_k(d, d["s_Regla"], (nA + k_b).astype(int).to_dict())   # coverage ranking, same quota
    mod_igual = top_k(d, d["s_" + MOD], (nA + k_b).astype(int).to_dict())
    flujo[key] = {"bloque_a": met(y, A, meses), "bloque_b": met(y, B, meses), "flujo": met(y, F, meses),
                  "regla_mismo_cupo": met(y, regla_igual, meses), "modelo_mismo_cupo": met(y, mod_igual, meses),
                  "modelo_top600": met(y, top_k(d, d["s_" + MOD], 600), meses),
                  "regla_top600": met(y, top_k(d, d["s_Regla"], 600), meses),
                  "flujo_600": met(y, A | top_k(d, d["s_" + MOD], (600 - nA).clip(lower=0).astype(int).to_dict(),
                                                eligible=~A), meses),
                  "modelo_top175": met(y, top_k(d, d["s_" + MOD], 175), meses),
                  "regla_top175": met(y, top_k(d, d["s_Regla"], 175), meses),
                  "sensibilidad_valor_e1": {
                      "flujo": met(y, F, meses, VALOR["sensibilidad_e1"]["valor_vp_usd"], VALOR["sensibilidad_e1"]["costo_fp_usd"]),
                      "bloque_a": met(y, A, meses, VALOR["sensibilidad_e1"]["valor_vp_usd"], VALOR["sensibilidad_e1"]["costo_fp_usd"])}}
    f = flujo[key]
    log(f"\n[{key}] bloque A {f['bloque_a']['alertas_mes']}/mes VP {f['bloque_a']['vp']} prec {f['bloque_a']['precision']:.1%}"
        f" · bloque B {f['bloque_b']['alertas_mes']}/mes VP {f['bloque_b']['vp']} prec {f['bloque_b']['precision']:.1%}")
    log(f"  flujo {f['flujo']['alertas_mes']}/mes VP {f['flujo']['vp']} rec {f['flujo']['recall']:.1%} prec "
        f"{f['flujo']['precision']:.1%} valor USD {f['flujo']['valor_neto_mes_usd']}/mes · regla mismo cupo VP "
        f"{f['regla_mismo_cupo']['vp']} · modelo mismo cupo VP {f['modelo_mismo_cupo']['vp']}")
    log(f"  a 600: flujo VP {f['flujo_600']['vp']} val {f['flujo_600']['valor_neto_mes_usd']}/mes · modelo VP "
        f"{f['modelo_top600']['vp']} val {f['modelo_top600']['valor_neto_mes_usd']} · regla VP {f['regla_top600']['vp']}"
        f" val {f['regla_top600']['valor_neto_mes_usd']}")
    log(f"  a 175: modelo VP {f['modelo_top175']['vp']} val {f['modelo_top175']['valor_neto_mes_usd']} · regla VP "
        f"{f['regla_top175']['vp']} val {f['regla_top175']['valor_neto_mes_usd']}")
results["flujo"] = flujo

# =============== 4. ROI: automation with the rule (no model) vs incremental model ===============
log("\n=== 4. ROI (escenario esperado) ===")


def roi(benef, inv, rec):
    c3 = inv + 3 * rec
    return {"beneficio_anual": round(benef, 0), "inversion": inv, "recurrente": rec,
            "roi_anio1": (benef - inv - rec) / (inv + rec), "roi_3anios": (3 * benef - c3) / c3,
            "recupero_meses": round(inv / (benef - rec) * 12, 1) if benef > rec else None}


roi_res = {}
for key in ("validacion", "test"):
    f = flujo[key]
    v_reg = f["bloque_a"]["valor_neto_mes_usd"] * 12
    v_inc = (f["flujo"]["valor_neto_mes_usd"] - f["bloque_a"]["valor_neto_mes_usd"]) * 12
    inv_auto = INVERSION - DESARROLLO_MODELO
    rec_auto = RECURRENTE - APOYO_EXTERNO
    r_auto = roi(HORAS_AHORRO_USD + v_reg, inv_auto, rec_auto)
    r_auto_caja = roi(HORAS_AHORRO_USD + v_reg, inv_auto, rec_auto - MANTENEDOR)
    r_inc = roi(v_inc, DESARROLLO_MODELO, APOYO_EXTERNO)
    r_tot = roi(HORAS_AHORRO_USD + v_reg + v_inc, INVERSION, RECURRENTE)
    r_tot_caja = roi(HORAS_AHORRO_USD + v_reg + v_inc, INVERSION, RECURRENTE - MANTENEDOR)
    ds_lo, ds_hi = DS_HORA * HORAS_MES * 3 * 1.1, DS_HORA * HORAS_MES * 4 * 1.1
    r_inc_ds = [roi(v_inc, c, APOYO_EXTERNO) for c in (ds_lo, ds_hi)]
    r_tot_ds = [roi(HORAS_AHORRO_USD + v_reg + v_inc, INVERSION - DESARROLLO_MODELO + c, RECURRENTE) for c in (ds_lo, ds_hi)]
    # sensitivity: value per position from Entregable 1
    s = f["sensibilidad_valor_e1"]
    v_reg_e1 = s["bloque_a"]["valor_neto_mes_usd"] * 12
    v_inc_e1 = (s["flujo"]["valor_neto_mes_usd"] - s["bloque_a"]["valor_neto_mes_usd"]) * 12
    r_tot_e1 = roi(HORAS_AHORRO_USD + v_reg_e1 + v_inc_e1, INVERSION, RECURRENTE)
    roi_res[key] = {"valor_regla_anual": round(v_reg, 0), "valor_incremental_modelo_anual": round(v_inc, 0),
                    "horas_anual": HORAS_AHORRO_USD, "automatizacion_sin_modelo": r_auto,
                    "automatizacion_sin_modelo_solo_caja": r_auto_caja, "incremental_modelo": r_inc,
                    "total": r_tot, "total_solo_caja": r_tot_caja,
                    "incremental_modelo_desarrollo_3a4_meses": r_inc_ds, "total_desarrollo_3a4_meses": r_tot_ds,
                    "costo_desarrollo_3a4_meses": [ds_lo, ds_hi], "total_valor_posicion_e1": r_tot_e1}
    log(f"[{key}] valor regla USD {v_reg:,.0f}/anio · incremental modelo USD {v_inc:,.0f}/anio · horas USD {HORAS_AHORRO_USD:,.0f}")
    for lbl, q in (("automatizacion (sin modelo)", r_auto), ("  idem solo caja", r_auto_caja),
                   ("incremental del modelo", r_inc), ("total", r_tot), ("  total solo caja", r_tot_caja),
                   ("total con desarrollo 3 meses DS", r_tot_ds[0]), ("total con desarrollo 4 meses DS", r_tot_ds[1]),
                   ("total valor posicion E1", r_tot_e1)):
        log(f"  {lbl:34s} benef {q['beneficio_anual']:>8,.0f} inv {q['inversion']:>7,.0f} rec {q['recurrente']:>6,.0f}"
            f" · ROI1 {q['roi_anio1']:7.1%} · ROI3 {q['roi_3anios']:7.1%} · recupero {q['recupero_meses']}")
results["roi"] = roi_res

# =============== 5. explainability: permutation importance of the final ranking ===============
log("\n=== 5. IMPORTANCIA POR PERMUTACION (validacion 2025, metrica: VP del flujo / Top-K del modelo) ===")
mask_v = masks["validacion"]
rng = np.random.default_rng(0)
K_IMP = max(k_mod, 300)


def model_rank(dfc, dfe):
    d = dv[["fecha_mes"]].copy()
    if MOD == "Ensamble":
        ps = []
        for n, xx in (("HistGradientBoosting", dfc), ("ExtraTrees", dfe), ("LightGBM", dfc)):
            p = models[n].predict_proba(xx)[:, 1]
            ps.append(pd.Series(p).groupby(d["fecha_mes"]).rank(pct=True))
        return np.mean(ps, axis=0)
    return models[MOD].predict_proba(dfc)[:, 1]


Xc_v = data["HistGradientBoosting"][mask_v].reset_index(drop=True)
Xe_v = data["ExtraTrees"][mask_v].reset_index(drop=True)
yv = dv[TARGET].to_numpy()
base_vp = int(yv[top_k(dv, model_rank(Xc_v, Xe_v), K_IMP)].sum())
imp = []
for f_ in features:
    perm = rng.permutation(len(Xc_v))
    c2, e2 = Xc_v.copy(), Xe_v.copy()
    c2[f_] = c2[f_].to_numpy()[perm]
    e2[f_] = e2[f_].to_numpy()[perm]
    vp_ = int(yv[top_k(dv, model_rank(c2, e2), K_IMP)].sum())
    imp.append({"variable": f_, "vp_permutado": vp_, "caida_vp": base_vp - vp_,
                "caida_recall_pp": 100 * (base_vp - vp_) / yv.sum()})
imp.sort(key=lambda r: r["caida_vp"], reverse=True)
results["importancia_permutacion"] = {"k": K_IMP, "vp_base": base_vp, "variables": imp}
for r_ in imp[:12]:
    log(f"  {r_['variable']:30s} -{r_['caida_vp']:4d} VP ({r_['caida_recall_pp']:.1f} pp de recall@{K_IMP})")

# =============== 6. segments with Wilson 95% CI (operating flow) ===============
log("\n=== 6. SEGMENTOS (flujo propuesto, IC 95% Wilson) ===")
seg = {}
for key, d in (("validacion", dv), ("test", dt)):
    A = (d["cobertura"] > 12).to_numpy()
    B = top_k(d, d["s_" + MOD], k_b, eligible=~A) if k_b else np.zeros(len(d), bool)
    d = d.assign(alerta=(A | B).astype(int))
    tot = d[TARGET].sum()
    g_rec = (d["alerta"] * d[TARGET]).sum() / tot
    seg[key] = {"recall_global": float(g_rec)}
    for grp in ("region", "categoria"):
        rows = []
        for val, g in d.groupby(grp):
            p = int(g[TARGET].sum())
            tp = int((g["alerta"] * g[TARGET]).sum())
            lo, hi = wilson(tp, p)
            rows.append({"segmento": str(val), "positivos": p, "vp": tp, "recall": tp / p if p else None,
                         "ic95": [lo, hi], "global_dentro_ic": bool(lo is not None and lo <= g_rec <= hi)})
        seg[key][grp] = sorted(rows, key=lambda z: z["recall"] if z["recall"] is not None else 0)
    log(f"[{key}] recall global {g_rec:.1%}")
    for grp in ("region", "categoria"):
        for z in seg[key][grp]:
            if z["positivos"]:
                log(f"  {grp:9s} {z['segmento']:22s} {z['vp']:4d}/{z['positivos']:<4d} {z['recall']:.1%} "
                    f"IC [{z['ic95'][0]:.0%}-{z['ic95'][1]:.0%}] {'' if z['global_dentro_ic'] else '<- fuera'}")
results["segmentos"] = seg

# =============== 7. why 2026 is easier: persistence of no-sale months ===============
log("\n=== 7. PERSISTENCIA SIN VENTA (posiciones con stock y sin venta en t: sigue sin vender t+1..t+3) ===")
p = raw[["id_tienda", "id_producto", "fecha_mes", "unidades_vendidas", "stock_disponible"]].copy()
p["fm"] = pd.to_datetime(p["fecha_mes"])
p = p.sort_values(["id_tienda", "id_producto", "fm"])
key_ = p["id_tienda"] + "|" + p["id_producto"]
idx = {(k, f): u for k, f, u in zip(key_, p["fm"], p["unidades_vendidas"])}
pers = {}
for anio in (2025, 2026):
    sub = p[(p["fm"].dt.year == anio) & (p["fm"].dt.month <= 5) & (p["unidades_vendidas"] <= 0) & (p["stock_disponible"] > 0)]
    ok = tot_ = 0
    for k, f in zip(key_.loc[sub.index], sub["fm"]):
        fut = [idx.get((k, f + pd.DateOffset(months=h))) for h in (1, 2, 3)]
        if any(v is None for v in fut):
            continue
        tot_ += 1
        ok += all(v <= 0 for v in fut)
    pers[anio] = {"posiciones_mes": tot_, "siguen_sin_vender": ok, "proporcion": ok / tot_ if tot_ else None}
    log(f"  ene-may {anio}: {ok:,} de {tot_:,} = {ok / tot_:.1%}")
results["persistencia_sin_venta"] = pers

(OUT / "modelo_final_v4_resultados.json").write_text(json.dumps(results, indent=2, ensure_ascii=False, default=float),
                                                    encoding="utf-8")
(OUT / "modelo_final_v4_log.txt").write_text("\n".join(LOG), encoding="utf-8")
log("\nOK -> resultados/modelo_final_v4_resultados.json")
