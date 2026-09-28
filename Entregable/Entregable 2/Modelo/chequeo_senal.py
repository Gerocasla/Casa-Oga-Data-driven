# -*- coding: utf-8 -*-
"""
Chequeo de sanidad del dataset de entrenamiento (NO es el modelo final).
Entrena modelos de prueba solo con el bloque de train y mide en validacion y test:
  - regresion logistica (version transformada) y gradient boosting (version sin transformar)
  - regla trivial: "la posicion ya supera 12 meses de cobertura hoy"
  - curva de capacidad: % de casos capturados con N alertas por mes (modelo vs ordenar por cobertura)
  - importancia por permutacion del gradient boosting en validacion
Salidas: resultados/chequeo_sanidad_vN.csv · capacidad_alertas_vN.csv · importancia_permutacion_vN.csv
"""
import os, sys
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import roc_auc_score, average_precision_score, recall_score, precision_score

sys.stdout.reconfigure(encoding="utf-8")
V = os.environ.get("VERSION_DATASET", "v3")
BASE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(BASE, "resultados")
DM = os.path.abspath(os.path.join(BASE, "..", "..", "..", "Datasets_Modelo"))
Y = "target_cob12_t3"; NOF = ["fecha_mes", "id_tienda", "id_producto", "costo_imputado", Y, "split"]
X = pd.read_parquet(os.path.join(DM, f"dataset_entrenamiento_{V}_transformado.parquet"))
R = pd.read_parquet(os.path.join(DM, f"dataset_entrenamiento_{V}.parquet"))
F = [c for c in X.columns if c not in NOF]; FR = [c for c in R.columns if c not in NOF]
Rc = R.copy()
for c in FR:
    if Rc[c].dtype == object: Rc[c] = Rc[c].astype("category")
Rc = Rc.replace([np.inf], 1e3)

tr, rtr = X[X.split == "train"], Rc[Rc.split == "train"]
lr = LogisticRegression(max_iter=5000, class_weight="balanced", C=0.5).fit(tr[F], tr[Y])
gb = HistGradientBoostingClassifier(max_iter=300, learning_rate=.05, class_weight="balanced",
                                    categorical_features="from_dtype", random_state=0).fit(rtr[FR], rtr[Y])
filas = []
for sp in ["validacion", "test"]:
    y = X[X.split == sp][Y]
    for nom, p in [("logistica", lr.predict_proba(X[X.split == sp][F])[:, 1]), ("gradient boosting", gb.predict_proba(Rc[Rc.split == sp][FR])[:, 1])]:
        filas.append(dict(modelo=nom, split=sp, auc=round(roc_auc_score(y, p), 3), pr_auc=round(average_precision_score(y, p), 3),
                          recall_05=round(recall_score(y, p > .5), 3), precision_05=round(precision_score(y, p > .5), 3)))
    s = R[R.split == sp]; t = (s.cobertura > 12).astype(int)
    filas.append(dict(modelo="regla: cobertura > 12 hoy", split=sp, auc=None, pr_auc=round(s[Y].mean(), 3),
                      recall_05=round(recall_score(s[Y], t), 3), precision_05=round(precision_score(s[Y], t), 3)))
chk = pd.DataFrame(filas); chk.to_csv(os.path.join(RES, f"chequeo_sanidad_{V}.csv"), index=False)
print(chk.to_string(index=False))

cap = []
for sp in ["validacion", "test"]:
    va = Rc[Rc.split == sp].copy(); va["p"] = gb.predict_proba(va[FR])[:, 1]
    for k in [50, 100, 200, 300, 420, 500, 600, 700, 850, 1000]:
        tm = va.sort_values("p", ascending=False).groupby("fecha_mes").head(k)
        rg = va.sort_values("cobertura", ascending=False).groupby("fecha_mes").head(k)
        cap.append(dict(split=sp, alertas_mes=k, recall_modelo=round(tm[Y].sum() / va[Y].sum() * 100, 1),
                        precision_modelo=round(tm[Y].mean() * 100, 1), recall_regla=round(rg[Y].sum() / va[Y].sum() * 100, 1),
                        precision_regla=round(rg[Y].mean() * 100, 1), positivos_mes=round(va.groupby("fecha_mes")[Y].sum().mean())))
cap = pd.DataFrame(cap); cap.to_csv(os.path.join(RES, f"capacidad_alertas_{V}.csv"), index=False)
print(cap[cap.alertas_mes.isin([420, 700])].to_string(index=False))

va = Rc[Rc.split == "validacion"]
pi = permutation_importance(gb, va[FR], va[Y], scoring="average_precision", n_repeats=3, random_state=0, n_jobs=-1)
imp = pd.Series(pi.importances_mean, FR).sort_values(ascending=False)
imp.round(5).to_csv(os.path.join(RES, f"importancia_permutacion_{V}.csv"), header=["delta_pr_auc"])
print(imp.head(12).round(4).to_string())
