"""Entregable 3 - Part D - Modeling stage 4: single final evaluation on the reserved test set.

Loads the model FIXED in stage 3 (Part C): an ensemble of HistGradientBoosting + ExtraTrees + LightGBM,
score = mean of the three monthly percentile ranks, decision = Top-600 alerts per month. Nothing is
re-trained or re-tuned here: the joblib and the threshold are used exactly as delivered.

Reproduces / reports (sections 8.1, 8.2, 8.3 and 11.2 of Part D):
- the fixed model on validation (abr-sep 2025, to check it reproduces Part C) and on test (ene-may 2026),
- baseline "cobertura actual > 12 meses" (Part A, 2.5) on both periods, plus the same rule ranked
  by coverage with the same quota of 600 alerts per month (Part B, 4.4),
- the original HistGradientBoosting of Part B (component of the joblib) as a reference,
- the model restricted to the same number of alerts as the fixed rule (equal-effort comparison),
- precision, recall, F1, AUC-ROC, PR-AUC, confusion matrices and estimated net value (USD) with the
  unit values of Part B (USD 10,04 per TP and USD 2,20 per FP, both with 70% adoption; FN = 0),
- the expected-scenario ROI of Part B (3.4) recomputed with the incremental hits observed in test.

Inputs: by default the dataset CSV and the joblib are read from "Data driven 3C.zip" (Part C evidence).
The joblib was serialized with scikit-learn 1.8.0 and numpy 2.x: run with those versions
(pip install "scikit-learn==1.8.0" "numpy>=2" "pandas<3" lightgbm joblib matplotlib), otherwise it does not load.
AUC/PR-AUC of the rule use raw coverage as score (Etapa 1 capped it at 60: PR-AUC 0.204 vs 0.206 here).
Run from the repo root:  python "Entregable/Entregable 3/Modelo/etapa4_evaluacion_final.py"
Optional:  --dataset <dataset_entrenamiento_v3.csv>  --modelo <ensamble_modelos_arboles.joblib>
"""
import argparse
import hashlib
import json
import tempfile
import zipfile
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

ROOT = Path(__file__).resolve().parents[3]
E3 = ROOT / "Entregable" / "Entregable 3"
OUT = Path(__file__).resolve().parent / "resultados"
ZIP_3C = E3 / "Data driven 3C.zip"
MEMBER = "Data driven 3C/Casa_Oga_Parte_3C_Modelos_Evidencias/"
SHA_3C = "796ba1a483aaeed934cf0e6cd93442af2e5c0e2eb53b9d7d97330bd0d5212a80"  # ensamble_etapa3_resultados.json

TARGET = "target_cob12_t3"
K = 600                      # fixed in Part C, 7.2: Top-600 alerts per month
VALOR_VP = 10.04             # Part B, 4.4: USD 14,34 x 70% adoption
COSTO_FP = 2.20              # Part B, 4.4: USD 3,14 x 70% adoption
# Part B, 3.3 / workbook "Supuestos": value of one extra hit at equal quota = 70% x (14,34 + 3,14)
VALOR_ACIERTO_INCREMENTAL = 0.7 * (14.340524263935757 + 3.141025641025641)
HORAS_AHORRO = 4032.0        # Part B, 3.3: 480 h x USD 12 x 70%
INVERSION, MANTENIMIENTO = 9570.0, 5960.0  # Part B, 3.2

lines = []


def log(text=""):
    print(text)
    lines.append(str(text))


def resolve_inputs(args):
    if args.dataset and args.modelo:
        return Path(args.dataset), Path(args.modelo)
    tmp = Path(tempfile.mkdtemp(prefix="etapa4_"))
    with zipfile.ZipFile(ZIP_3C) as z:
        for name in ("dataset_entrenamiento_v3.csv", "ensamble_modelos_arboles.joblib"):
            target = tmp / name
            target.write_bytes(z.read(MEMBER + name))
    return tmp / "dataset_entrenamiento_v3.csv", tmp / "ensamble_modelos_arboles.joblib"


parser = argparse.ArgumentParser()
parser.add_argument("--dataset")
parser.add_argument("--modelo")
data_path, model_path = resolve_inputs(parser.parse_args())

sha = hashlib.sha256(data_path.read_bytes()).hexdigest()
log("=== INSUMOS ===")
log(f"Dataset: {data_path.name} · sha256 {sha[:16]}... · coincide con Parte C: {sha == SHA_3C}")
log(f"Modelo: {model_path.name} (ensamble fijado en la Etapa 3, sin reentrenar)")

# --- 1. Rebuild the exact feature matrices used in stage 3 -------------------------
bundle = joblib.load(model_path)
models, enc, med = bundle["modelos"], bundle["encoder"], bundle["medianas"]
features, cat = bundle["features"], bundle["categoricas"]
num = [c for c in features if c not in cat]

ds = pd.read_csv(data_path)
for col in num:
    ds[col] = ds[col].replace([np.inf, -np.inf], [1000.0, -1000.0])
train = ds["split"] == "train"
X = ds[features].copy()
X_cat = X.copy()
for c in cat:  # same category levels as stage 3: learned on the train split only
    X_cat[c] = pd.Categorical(X_cat[c], categories=sorted(X_cat.loc[train, c].dropna().unique()))
X_enc = X.copy()
X_enc[cat] = enc.transform(X[cat].fillna("Desconocido"))
for c in num:
    X_enc[c] = X_enc[c].fillna(med[c]).astype("float32")
X_enc = X_enc.astype("float32")

log("\n=== CATEGORIAS NO VISTAS EN TRAIN (test) ===")
test_mask = ds["split"] == "test"
for c in cat:
    unseen = set(ds.loc[test_mask, c].dropna()) - set(ds.loc[train, c].dropna())
    log(f"{c}: {len(unseen)} niveles nuevos en test")

# --- 2. Score validation and test ONCE ----------------------------------------------
periods = {"validacion": "Validacion abr-sep 2025", "test": "Test ene-may 2026"}
frames = {}
for split in periods:
    mask = (ds["split"] == split).to_numpy()
    d = ds.loc[mask, ["fecha_mes", "id_tienda", "id_producto", "categoria", "region",
                      "cobertura", TARGET]].reset_index(drop=True)
    for name, model in models.items():
        xx = X_enc if name == "ExtraTrees" else X_cat
        d["pred_" + name] = model.predict_proba(xx.loc[mask])[:, 1]
        d["pct_" + name] = d["pred_" + name].groupby(d["fecha_mes"]).rank(method="average", pct=True)
    d["score_ensamble"] = d[[f"pct_{k}" for k in models]].mean(axis=1)
    frames[split] = d


def select_top(d, score, k):
    """Top-k per month, stable order (same rule as modelo_ensamble_final.py)."""
    tmp = d[["fecha_mes"]].copy()
    tmp["score"] = np.asarray(score)
    tmp = tmp.sort_values(["fecha_mes", "score"], ascending=[True, False], kind="mergesort")
    pos_in_month = tmp.groupby("fecha_mes", sort=False).cumcount()
    cupo = k if np.isscalar(k) else tmp["fecha_mes"].map(k)  # fixed k, or k per month (dict)
    idx = tmp.index[pos_in_month < cupo]
    return d.index.isin(idx)


def evaluate(d, sel, score):
    y = d[TARGET].astype(int).to_numpy()
    n, tp, pos = int(sel.sum()), int(y[sel].sum()), int(y.sum())
    pr = tp / n if n else 0.0
    re = tp / pos
    meses = d["fecha_mes"].nunique()
    valor = tp * VALOR_VP - (n - tp) * COSTO_FP
    return {
        "alertas": n, "alertas_mes": round(n / meses, 1), "vp": tp, "fp": n - tp, "fn": pos - tp,
        "vn": len(y) - pos - (n - tp), "precision": pr, "recall": re,
        "f1": 2 * pr * re / (pr + re) if pr + re else 0.0,
        "auc_roc": float(roc_auc_score(y, score)), "pr_auc": float(average_precision_score(y, score)),
        "valor_neto_usd": round(valor, 2), "valor_neto_mensual_usd": round(valor / meses, 2),
        "valor_neto_anualizado_usd": round(valor / meses * 12, 2), "meses": meses,
    }


results = {"insumos": {"dataset_sha256": sha, "coincide_parte_c": sha == SHA_3C,
                       "umbral": f"Top-{K} por mes sobre score_ensamble (promedio de percentiles mensuales)",
                       "valor_vp_usd": VALOR_VP, "costo_fp_usd": COSTO_FP},
           "periodos": {}}

for split, label in periods.items():
    d = frames[split]
    y = d[TARGET].astype(int)
    cov = d["cobertura"].clip(upper=1000)
    regla = (d["cobertura"] > 12).to_numpy()
    k_regla = pd.Series(regla).groupby(d["fecha_mes"]).sum().astype(int).to_dict()
    res = {
        "filas": len(d), "positivos": int(y.sum()), "prevalencia": float(y.mean()),
        "meses": int(d["fecha_mes"].nunique()), "positivos_mes": round(y.sum() / d["fecha_mes"].nunique(), 1),
        "regla_cobertura_12": evaluate(d, regla, cov),
        "regla_cobertura_top600": evaluate(d, select_top(d, cov, K), cov),
        "hgb_original_top600": evaluate(d, select_top(d, d["pred_HistGradientBoosting"], K),
                                        d["pred_HistGradientBoosting"]),
        "ensamble_top600": evaluate(d, select_top(d, d["score_ensamble"], K), d["score_ensamble"]),
        "ensamble_mismo_cupo_regla": evaluate(d, select_top(d, d["score_ensamble"], k_regla), d["score_ensamble"]),
    }
    sel = select_top(d, d["score_ensamble"], K)
    d["alerta"] = sel.astype(int)
    res["mensual"] = [{"mes": m, "positivos": int(g[TARGET].sum()), "vp_ensamble": int((g.alerta * g[TARGET]).sum()),
                       "alertas_regla12": int((g.cobertura > 12).sum()),
                       "vp_regla12": int(((g.cobertura > 12) * g[TARGET]).sum())}
                      for m, g in d.groupby("fecha_mes")]
    res["segmentos_categoria"] = sorted(
        [{"categoria": c, "positivos": int(g[TARGET].sum()), "vp": int((g.alerta * g[TARGET]).sum()),
          "recall": (g.alerta * g[TARGET]).sum() / g[TARGET].sum() if g[TARGET].sum() else None}
         for c, g in d.groupby("categoria")], key=lambda r: r["recall"] if r["recall"] is not None else 0)
    results["periodos"][split] = res

# --- 3. Log ----------------------------------------------------------------------------
NAMES = {"regla_cobertura_12": "Regla fija: cobertura actual > 12 meses",
         "regla_cobertura_top600": "Regla ordenada por cobertura, Top-600/mes",
         "hgb_original_top600": "HistGradientBoosting original (3B), Top-600/mes",
         "ensamble_top600": "Ensamble final (3C), Top-600/mes  <- MODELO FIJADO",
         "ensamble_mismo_cupo_regla": "Ensamble con el mismo cupo mensual que la regla fija"}
for split, label in periods.items():
    r = results["periodos"][split]
    log(f"\n=== {label.upper()} ===")
    log(f"Filas {r['filas']:,} · positivos {r['positivos']:,} ({r['positivos_mes']}/mes) · "
        f"prevalencia {r['prevalencia']:.2%} · meses {r['meses']}")
    for key, name in NAMES.items():
        m = r[key]
        log(f"\n{name}")
        log(f"  alertas {m['alertas']:,} ({m['alertas_mes']}/mes) · VP={m['vp']:,} FN={m['fn']:,} "
            f"FP={m['fp']:,} VN={m['vn']:,}")
        log(f"  precision={m['precision']:.3f} recall={m['recall']:.3f} f1={m['f1']:.3f} "
            f"AUC-ROC={m['auc_roc']:.3f} PR-AUC={m['pr_auc']:.3f}")
        log(f"  valor neto USD {m['valor_neto_usd']:,.0f} en {m['meses']} meses "
            f"({m['valor_neto_mensual_usd']:,.0f}/mes · {m['valor_neto_anualizado_usd']:,.0f}/anio)")
    log("\n  Mensual (positivos · VP ensamble Top-600 · alertas y VP de la regla fija):")
    for x in r["mensual"]:
        log(f"   {x['mes']}: {x['positivos']} · {x['vp_ensamble']} · {x['alertas_regla12']} / {x['vp_regla12']}")
    log("  Recall del ensamble por categoria:")
    for x in r["segmentos_categoria"]:
        log(f"   {x['categoria']}: {x['vp']}/{x['positivos']} = {x['recall']:.1%}")

# --- 4. Generalization and ROI update (Part B expected scenario) ------------------------
log("\n=== GENERALIZACION (validacion -> test) ===")
v, t = results["periodos"]["validacion"], results["periodos"]["test"]
for key in ("regla_cobertura_12", "ensamble_top600"):
    for met in ("precision", "recall", "f1", "auc_roc"):
        log(f"{NAMES[key][:40]:40s} {met:9s} {v[key][met]:.3f} -> {t[key][met]:.3f} "
            f"({(t[key][met] - v[key][met]) * 100:+.1f} pp)")

log("\n=== ROI ESCENARIO ESPERADO (Parte B 3.4) CON ACIERTOS INCREMENTALES OBSERVADOS ===")
roi = {}
for split in periods:
    r = results["periodos"][split]
    extra = r["ensamble_top600"]["vp"] - r["regla_cobertura_top600"]["vp"]
    extra_anual = extra / r["meses"] * 12
    benef_pred = extra_anual * VALOR_ACIERTO_INCREMENTAL
    benef = benef_pred + HORAS_AHORRO
    roi1 = (benef - INVERSION - MANTENIMIENTO) / (INVERSION + MANTENIMIENTO)
    roi3 = (3 * benef - INVERSION - 3 * MANTENIMIENTO) / (INVERSION + 3 * MANTENIMIENTO)
    payback = INVERSION / (benef - MANTENIMIENTO) * 12 if benef > MANTENIMIENTO else None
    roi[split] = {"vp_extra_vs_regla_top600": extra, "vp_extra_anual": round(extra_anual, 1),
                  "beneficio_predictivo_anual": round(benef_pred, 0), "beneficio_anual_total": round(benef, 0),
                  "roi_anio1": roi1, "roi_3anios": roi3,
                  "recupero_con_mantenimiento_meses": round(payback, 1) if payback else None}
    log(f"{periods[split]}: +{extra} aciertos vs regla Top-600 ({extra_anual:.0f}/anio) -> beneficio predictivo "
        f"USD {benef_pred:,.0f} + horas USD {HORAS_AHORRO:,.0f} = USD {benef:,.0f}/anio · ROI anio 1 {roi1:.1%} · "
        f"ROI 3 anios {roi3:.1%} · recupero {('%.0f meses' % payback) if payback else 'no recupera'}")
results["roi_escenario_esperado"] = roi

OUT.mkdir(exist_ok=True)
(OUT / "etapa4_resultados.json").write_text(json.dumps(results, ensure_ascii=False, indent=2, default=float),
                                            encoding="utf-8")
(OUT / "etapa4_log.txt").write_text("\n".join(lines), encoding="utf-8")

# --- 5. Chart: rule vs model, validation vs test ------------------------------------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

series = [("regla_cobertura_12", "Regla fija\ncobertura > 12"), ("regla_cobertura_top600", "Regla por cobertura\nTop-600/mes"),
          ("ensamble_top600", "Ensamble\nTop-600/mes")]
fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharey=True)
for ax, met, title in zip(axes, ("precision", "recall"), ("Precisión", "Recall")):
    x = np.arange(len(series))
    for i, (split, color) in enumerate((("validacion", "#8fa9c7"), ("test", "#1f4e79"))):
        vals = [results["periodos"][split][k][met] for k, _ in series]
        bars = ax.bar(x + (i - 0.5) * 0.36, vals, 0.36, color=color, label=periods[split])
        for b, val in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, val + 0.015, f"{val:.0%}", ha="center", fontsize=8)
    ax.set_xticks(x, [s for _, s in series], fontsize=8)
    ax.set_title(title)
    ax.set_ylim(0, 1.05)
    ax.spines[["top", "right"]].set_visible(False)
axes[0].legend(fontsize=8, frameon=False, loc="upper left")
fig.suptitle("Etapa 4 · Regla vs. modelo en validación 2025 y test 2026", fontsize=11)
fig.tight_layout()
fig.savefig(OUT / "etapa4_regla_vs_modelo.png", dpi=160)
plt.close(fig)
print("FINAL", OUT / "etapa4_resultados.json")
