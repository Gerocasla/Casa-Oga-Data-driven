"""Entregable 3 - Part D - Simulation of the combined first-version flow (section 9.2), requested by Group 3.

Block A: rule "cobertura actual > 12 meses" (all positions that meet it, capped at 600 per month).
Block B: fixed stage-3 ensemble, Top-ranked positions NOT in block A, until the month reaches 600 alerts.
Compared with the same 600 alerts per month ranked only by coverage and with the ensemble alone (Top-600).

Nothing is re-trained or re-tuned: same joblib, same dataset and same unit values as etapa4_evaluacion_final.py.
Run from the repo root with scikit-learn 1.8.0, numpy 2, lightgbm (see etapa4_evaluacion_final.py):
    python "Entregable/Entregable 3/Modelo/etapa4_flujo_combinado.py"
Optional:  --dataset <dataset_entrenamiento_v3.csv>  --modelo <ensamble_modelos_arboles.joblib>
"""
import argparse
import json
import tempfile
import zipfile
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
ZIP_3C = ROOT / "Entregable" / "Entregable 3" / "Data driven 3C.zip"
MEMBER = "Data driven 3C/Casa_Oga_Parte_3C_Modelos_Evidencias/"
OUT = Path(__file__).resolve().parent / "resultados"
TARGET, K = "target_cob12_t3", 600
VALOR_VP, COSTO_FP = 10.04, 2.20
VALOR_ACIERTO_INCREMENTAL = 0.7 * (14.340524263935757 + 3.141025641025641)
HORAS_AHORRO, INVERSION, MANTENIMIENTO = 4032.0, 9570.0, 5960.0

parser = argparse.ArgumentParser()
parser.add_argument("--dataset")
parser.add_argument("--modelo")
args = parser.parse_args()
if args.dataset and args.modelo:
    data_path, model_path = Path(args.dataset), Path(args.modelo)
else:
    tmp = Path(tempfile.mkdtemp(prefix="flujo_"))
    with zipfile.ZipFile(ZIP_3C) as z:
        for name in ("dataset_entrenamiento_v3.csv", "ensamble_modelos_arboles.joblib"):
            (tmp / name).write_bytes(z.read(MEMBER + name))
    data_path, model_path = tmp / "dataset_entrenamiento_v3.csv", tmp / "ensamble_modelos_arboles.joblib"

# Same feature preparation as etapa4_evaluacion_final.py
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
for c in cat:
    X_cat[c] = pd.Categorical(X_cat[c], categories=sorted(X_cat.loc[train, c].dropna().unique()))
X_enc = X.copy()
X_enc[cat] = enc.transform(X[cat].fillna("Desconocido"))
for c in num:
    X_enc[c] = X_enc[c].fillna(med[c]).astype("float32")
X_enc = X_enc.astype("float32")


def top_per_month(d, score, k, eligible=None):
    tmp = d[["fecha_mes"]].copy()
    tmp["score"] = np.asarray(score, dtype=float)
    if eligible is not None:
        tmp = tmp[np.asarray(eligible)]
    tmp = tmp.sort_values(["fecha_mes", "score"], ascending=[True, False], kind="mergesort")
    pos = tmp.groupby("fecha_mes", sort=False).cumcount()
    cupo = k if np.isscalar(k) else tmp["fecha_mes"].map(k)
    return d.index.isin(tmp.index[pos < cupo])


def metrics(y, sel, meses):
    n, tp = int(sel.sum()), int(y[sel].sum())
    return {"alertas": n, "alertas_mes": round(n / meses, 1), "vp": tp, "fp": n - tp,
            "precision": tp / n if n else 0.0, "recall": tp / int(y.sum()),
            "valor_neto_usd": round(tp * VALOR_VP - (n - tp) * COSTO_FP, 2)}


periods = {"validacion": "Validacion abr-sep 2025", "test": "Test ene-may 2026"}
results, lines = {}, []
for split, label in periods.items():
    mask = (ds["split"] == split).to_numpy()
    d = ds.loc[mask, ["fecha_mes", "cobertura", TARGET]].reset_index(drop=True)
    for name, model in models.items():
        xx = X_enc if name == "ExtraTrees" else X_cat
        p = model.predict_proba(xx.loc[mask])[:, 1]
        d["pct_" + name] = pd.Series(p).groupby(d["fecha_mes"]).rank(method="average", pct=True)
    d["score"] = d[[f"pct_{k}" for k in models]].mean(axis=1)
    y = d[TARGET].astype(int).to_numpy()
    meses = d["fecha_mes"].nunique()
    cov = d["cobertura"].clip(upper=1000)

    regla = (d["cobertura"] > 12).to_numpy()
    bloque_a = top_per_month(d, cov, K, eligible=regla)  # cap 600; never binds (max 243/month)
    cupo_b = (K - pd.Series(bloque_a).groupby(d["fecha_mes"]).sum()).astype(int).to_dict()
    bloque_b = top_per_month(d, d["score"], cupo_b, eligible=~bloque_a)
    flujo = bloque_a | bloque_b
    cob600 = top_per_month(d, cov, K)
    ens600 = top_per_month(d, d["score"], K)

    r = {"meses": meses, "positivos": int(y.sum()),
         "max_alertas_bloque_a_mes": int(pd.Series(bloque_a).groupby(d["fecha_mes"]).sum().max()),
         "bloque_a": metrics(y, bloque_a, meses), "bloque_b": metrics(y, bloque_b, meses),
         "flujo_combinado": metrics(y, flujo, meses), "cobertura_top600": metrics(y, cob600, meses),
         "ensamble_top600": metrics(y, ens600, meses),
         "coincidencia_flujo_vs_cobertura600": int((flujo & cob600).sum())}
    extra = r["flujo_combinado"]["vp"] - r["cobertura_top600"]["vp"]
    benef_pred = extra / meses * 12 * VALOR_ACIERTO_INCREMENTAL
    benef = benef_pred + HORAS_AHORRO
    r["roi_escenario_esperado"] = {
        "vp_extra_vs_cobertura600": extra, "beneficio_predictivo_anual": round(benef_pred, 0),
        "beneficio_anual_total": round(benef, 0),
        "roi_anio1": (benef - INVERSION - MANTENIMIENTO) / (INVERSION + MANTENIMIENTO),
        "roi_3anios": (3 * benef - INVERSION - 3 * MANTENIMIENTO) / (INVERSION + 3 * MANTENIMIENTO),
        "recupero_meses": round(INVERSION / (benef - MANTENIMIENTO) * 12, 1) if benef > MANTENIMIENTO else None}
    results[split] = r

    lines.append(f"=== {label.upper()} === positivos {r['positivos']} · meses {meses} · "
                 f"max bloque A/mes {r['max_alertas_bloque_a_mes']}")
    for key in ("bloque_a", "bloque_b", "flujo_combinado", "cobertura_top600", "ensamble_top600"):
        m = r[key]
        lines.append(f"  {key:18s} alertas {m['alertas']:>5} ({m['alertas_mes']}/mes) VP {m['vp']:>5} "
                     f"prec {m['precision']:.3f} recall {m['recall']:.3f} valor USD {m['valor_neto_usd']:,.0f}")
    q = r["roi_escenario_esperado"]
    lines.append(f"  +{extra} VP vs cobertura Top-600 · beneficio USD {q['beneficio_anual_total']:,.0f}/anio · "
                 f"ROI 1 {q['roi_anio1']:.1%} · ROI 3 {q['roi_3anios']:.1%} · recupero {q['recupero_meses']} meses")

OUT.mkdir(exist_ok=True)
(OUT / "etapa4_flujo_combinado.json").write_text(json.dumps(results, indent=2, default=float), encoding="utf-8")
(OUT / "etapa4_flujo_combinado_log.txt").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
