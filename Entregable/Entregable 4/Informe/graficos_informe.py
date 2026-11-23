"""Entregable 4 - charts for the final report and the deck (PNG, static).

Inputs: Entregable 2/Modelo/resultados/insights.json and Entregable 4/Modelo/resultados/modelo_final_v4_resultados.json
Run from the repo root:  python "Entregable/Entregable 4/Informe/graficos_informe.py"
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "graficos"
OUT.mkdir(exist_ok=True)
INS = json.loads((ROOT / "Entregable/Entregable 2/Modelo/resultados/insights.json").read_text(encoding="utf-8"))
RES = json.loads((ROOT / "Entregable/Entregable 4/Modelo/resultados/modelo_final_v4_resultados.json").read_text(encoding="utf-8"))

BLUE, ORANGE, GRAY = "#2a78d6", "#eb6834", "#8a8984"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.family": "Arial", "font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True})


def fmt(n):
    return f"{n:,.0f}".replace(",", ".")


# 1. Positions with coverage > 12 months, monthly (one measure, one axis)
m = INS["rojo_mes"]
fig, ax = plt.subplots(figsize=(8.6, 3.4))
x = list(range(len(m["meses"])))
ax.plot(x, m["posiciones"], color=BLUE, lw=2)
ax.fill_between(x, m["posiciones"], color=BLUE, alpha=0.08, lw=0)
ticks = [i for i, s in enumerate(m["meses"]) if s.endswith("-01") or s == m["meses"][-1]]
ax.set_xticks(ticks, [m["meses"][i].replace("-01", "\nene").replace("2026-08", "2026\nago") for i in ticks])
for i, lbl in ((m["meses"].index("2025-12"), "dic-25: 200"), (len(x) - 1, "ago-26: 866")):
    ax.scatter([i], [m["posiciones"][i]], s=36, color=BLUE, zorder=3, edgecolor="white", linewidth=2)
    off = (0, -18) if lbl.startswith("dic") else (-8, 8)
    ax.annotate(lbl, (i, m["posiciones"][i]), xytext=off, textcoords="offset points",
                ha="center" if lbl.startswith("dic") else "right", color=INK, fontsize=9)
ax.set_ylabel("Posiciones SKU–tienda")
ax.set_ylim(0, 950)
ax.set_title("Posiciones con más de 12 meses de cobertura, por mes", loc="left", color=INK, fontsize=11, fontweight="bold")
fig.tight_layout()
fig.savefig(OUT / "01_posiciones_cobertura12.png", dpi=200)
plt.close(fig)

# 2. Net value per month vs alerts per month, validation 2025 (model vs rule)
cur = RES["periodos"]["validacion"]["curva"]
ks = sorted(int(k) for k in cur if int(k) % 50 == 0)
fig, ax = plt.subplots(figsize=(8.6, 3.6))
for name, col, lbl in (("HistGradientBoosting", BLUE, "Modelo (gradient boosting)"), ("Regla", ORANGE, "Regla ordenada por cobertura")):
    v = [cur[str(k)][name]["valor_neto_mes_usd"] for k in ks]
    ax.plot(ks, v, color=col, lw=2, marker="o", ms=4, label=lbl)
ax.axhline(0, color=INK2, lw=0.8)
kop = RES["flujo"]["validacion"]["flujo"]["alertas_mes"]
ax.axvline(kop, color=GRAY, lw=1, ls="--")
ax.text(kop + 8, ax.get_ylim()[0] + 20, f"cupo propuesto ≈ {kop:.0f}/mes", color=INK2, fontsize=9)
ax.axvspan(420, 700, color=GRAY, alpha=0.08, lw=0)
ax.text(560, ax.get_ylim()[1] * 0.92, "capacidad declarada\n420–700", ha="center", color=INK2, fontsize=8.5)
ax.set_xlabel("Alertas por mes")
ax.set_ylabel("Valor neto (USD por mes)")
ax.legend(frameon=False, loc="lower left")
ax.set_title("Validación abr–sep 2025: el valor deja de crecer mucho antes de llenar la capacidad", loc="left",
             color=INK, fontsize=11, fontweight="bold")
fig.tight_layout()
fig.savefig(OUT / "02_valor_vs_alertas_2025.png", dpi=200)
plt.close(fig)

# 3. Proposed flow vs rule alone and vs same quota by coverage, both periods (grouped bars, VP)
fl = RES["flujo"]
fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.3))
for ax, key, title in ((axes[0], "validacion", "Validación 2025"), (axes[1], "test", "Test 2026")):
    f = fl[key]
    vals = [f["bloque_a"]["vp"], f["regla_mismo_cupo"]["vp"], f["flujo"]["vp"]]
    labels = ["Solo regla\n(bloque A)", "Cobertura\nmismo cupo", "Flujo A + B\n(propuesto)"]
    cols = [ORANGE, GRAY, BLUE]
    bars = ax.bar(labels, vals, color=cols, width=0.6)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v, fmt(v), ha="center", va="bottom", fontsize=9, color=INK)
    ax.set_title(f"{title} · {f['flujo']['alertas_mes']:.0f} alertas/mes", loc="left", color=INK, fontsize=10)
    ax.set_ylabel("Casos detectados (VP)" if key == "validacion" else "")
    ax.grid(axis="x", visible=False)
fig.suptitle("Casos en riesgo detectados por el flujo propuesto", x=0.01, ha="left", color=INK, fontsize=11, fontweight="bold")
fig.tight_layout()
fig.savefig(OUT / "03_flujo_vs_regla.png", dpi=200)
plt.close(fig)

# 4. Permutation importance (top 10)
imp = RES["importancia_permutacion"]["variables"][:10][::-1]
nombres = {"u6_suma": "Unidades vendidas en 6 meses", "cobertura": "Cobertura actual", "cv_u12": "Variabilidad de la venta (12 m)",
           "stock_sku_cadena": "Stock del SKU en la cadena", "peso_posicion_en_tienda": "Peso de la posición en la tienda",
           "u12_prom": "Venta promedio 12 meses", "unidades_vendidas": "Unidades vendidas en el mes",
           "u_lag1": "Venta del mes anterior", "subcategoria": "Subcategoría", "u3_suma": "Unidades vendidas en 3 meses",
           "stock_disponible": "Stock disponible", "antig_sku_meses": "Antigüedad del SKU"}
fig, ax = plt.subplots(figsize=(8.6, 3.6))
ax.barh([nombres.get(r["variable"], r["variable"]) for r in imp], [r["caida_recall_pp"] for r in imp], color=BLUE, height=0.6)
for i, r in enumerate(imp):
    ax.text(r["caida_recall_pp"] + 0.08, i, f"{r['caida_recall_pp']:.1f}", va="center", fontsize=9, color=INK)
ax.set_xlabel(f"Puntos de recall que se pierden al mezclar la variable (Top-{RES['importancia_permutacion']['k']}, validación 2025)")
ax.grid(axis="y", visible=False)
ax.set_title("Qué variables usa el modelo (importancia por permutación)", loc="left", color=INK, fontsize=11, fontweight="bold")
fig.tight_layout()
fig.savefig(OUT / "04_importancia_permutacion.png", dpi=200)
plt.close(fig)
print("OK", sorted(p.name for p in OUT.glob("*.png")))
