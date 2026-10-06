"""Entregable 3 - Part A - Modeling stage 1: experiment sheet, temporal split and baselines.

Reproduces every number reported in sections 1.1 (data sufficiency and quality) and 2.1-2.5:
- critical-variable nulls and key match between the main sources (raw data),
- rows / positives / prevalence per temporal split of dataset_entrenamiento_v3,
- baseline 1 (always predict the majority class) and baseline 2 (business rule:
  current coverage > 12 months), both evaluated on the validation split.

Run from the repo root:  python "Entregable/Entregable 3/Modelo/etapa1_experimento_baseline.py"
"""
from pathlib import Path

import pandas as pd
from sklearn.metrics import (average_precision_score, confusion_matrix, f1_score,
                             precision_score, recall_score)

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "resultados" / "etapa1_log.txt"
lines = []


def log(text=""):
    print(text)
    lines.append(str(text))


# --- 1. Data quality evidence on the raw sources ---------------------------------
raw = ROOT / "Datasets"
ventas = pd.read_csv(raw / "Ventas_SKU_tienda_mensual.csv")
stock = pd.read_csv(raw / "Stock_SKU_tienda_mensual.csv")
catalogo = pd.read_csv(raw / "Productos_catalogo.csv")
key = ["fecha_mes", "id_tienda", "id_producto"]

log("=== CALIDAD (datos crudos) ===")
for name, df, cols in [("Ventas", ventas, ["unidades_vendidas", "venta_neta"]),
                       ("Stock", stock, ["stock_disponible"]),
                       ("Catalogo", catalogo, ["costo_unitario", "categoria", "proveedor"])]:
    for c in cols:
        if c in df.columns:
            log(f"{name}.{c}: nulos {df[c].isna().sum():,} de {len(df):,} ({df[c].isna().mean():.2%})")

kv = ventas[key].drop_duplicates()
ks = stock[key].drop_duplicates()
m = kv.merge(ks, on=key, how="outer", indicator=True)
log(f"Claves (mes, tienda, SKU) unicas: ventas {len(kv):,} · stock {len(ks):,}")
log(f"Join ventas-stock: {m['_merge'].value_counts().to_dict()} -> no matchea {(m['_merge'] != 'both').mean():.2%}")
skus_cat = set(catalogo["id_producto"])
log(f"SKUs de ventas fuera del catalogo: {(~ventas['id_producto'].isin(skus_cat)).sum():,}")
log(f"Filas con clave duplicada en ventas: {ventas.duplicated(key, keep=False).sum():,} "
    f"({ventas.duplicated(key, keep=False).mean():.2%})")

# --- 2. Experiment sheet and temporal split ----------------------------------------
ds = pd.read_parquet(ROOT / "Datasets_Modelo" / "dataset_entrenamiento_v3.parquet")
target = "target_cob12_t3"
ds["fecha_mes"] = pd.to_datetime(ds["fecha_mes"])
log("\n=== FICHA DEL EXPERIMENTO ===")
log(f"Filas: {len(ds):,} · periodos (meses de corte): {ds['fecha_mes'].nunique()} "
    f"({ds['fecha_mes'].min():%Y-%m} a {ds['fecha_mes'].max():%Y-%m})")
log(f"Positivos: {int(ds[target].sum()):,} · prevalencia {ds[target].mean():.2%}")

log("\n=== PARTICION TEMPORAL ===")
part = (ds.groupby("split")
          .agg(desde=("fecha_mes", "min"), hasta=("fecha_mes", "max"), meses=("fecha_mes", "nunique"),
               filas=(target, "size"), positivos=(target, "sum"), prevalencia=(target, "mean")))
part["desde"] = part["desde"].dt.strftime("%Y-%m")
part["hasta"] = part["hasta"].dt.strftime("%Y-%m")
part["prevalencia"] = (part["prevalencia"] * 100).round(2)
log(part.loc[["train", "validacion", "test", "embargo"]].to_string())

# --- 3. Baselines on validation (test stays untouched until stage 4) ---------------
val = ds[ds["split"] == "validacion"]
y = val[target].astype(int)
baselines = {
    "Baseline 1: clase mayoritaria": (pd.Series(0, index=val.index), pd.Series(0.0, index=val.index)),
    "Baseline 2: cobertura actual > 12 meses": ((val["cobertura"] > 12).astype(int), val["cobertura"].clip(upper=60)),
}
log("\n=== BASELINES (validacion) ===")
for name, (pred, score) in baselines.items():
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    log(f"\n{name}")
    log(f"  VP={tp:,} FN={fn:,} FP={fp:,} VN={tn:,}")
    log(f"  PR-AUC (regla binaria) = {average_precision_score(y, pred):.3f}")
    if score.nunique() > 1:
        log(f"  PR-AUC (cobertura como puntaje continuo) = {average_precision_score(y, score):.3f}")
    log(f"  precision={precision_score(y, pred, zero_division=0):.3f} "
        f"recall={recall_score(y, pred, zero_division=0):.3f} f1={f1_score(y, pred, zero_division=0):.3f}")
    log(f"  alertas por mes (promedio): {pred.groupby(val['fecha_mes']).sum().mean():.0f}")

OUT.write_text("\n".join(lines), encoding="utf-8")
