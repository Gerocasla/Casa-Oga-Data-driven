import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from pathlib import Path
# Entregable 3 - Part D - section 9.2: end-to-end solution flow diagram (annex A).
OUT = Path(__file__).resolve().parent / "Casa_Oga_ParteD_Flujo_Solucion.png"
fig, ax = plt.subplots(figsize=(13, 7.4)); ax.set_xlim(0, 130); ax.set_ylim(0, 74); ax.axis("off")
C = {"dato": "#dbe7f3", "modelo": "#1f4e79", "neg": "#e8f1e4", "fb": "#fdf0dc"}
def box(x, y, w, h, title, body, color, tc="#1a1a1a", foot=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.6", fc=color, ec="#4a5a6a", lw=1))
    ax.text(x + w/2, y + h - 2.6, title, ha="center", va="top", fontsize=10.5, weight="bold", color=tc)
    ax.text(x + w/2, y + h - 7.2, body, ha="center", va="top", fontsize=8.3, color=tc, linespacing=1.35)
    if foot: ax.text(x + w/2, y + 1.6, foot, ha="center", va="bottom", fontsize=7.6, color=tc, style="italic")
def arrow(p, q, color="#4a5a6a", style="-|>", rad=0.0, ls="-"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=14, color=color, lw=1.5,
                                 connectionstyle=f"arc3,rad={rad}", linestyle=ls))
ax.text(65, 72, "Casa Óga · Flujo de la solución de punta a punta (primera versión)", ha="center", fontsize=13, weight="bold")
# fila superior
box(2, 42, 28, 25, "1 · Fuentes", "Ventas y Stock SKU-tienda\nÓrdenes de compra\nTransferencias y liquidaciones\nCatálogo y promociones", C["dato"], foot="POS · inventario · Compras")
box(35, 42, 28, 25, "2 · Ingesta", "Exportación mensual\nestandarizada (CSV)\nControl de recepción:\n5 archivos y claves válidas", C["dato"], foot="Mensual, días 1-3 · Mantenedor")
box(68, 42, 28, 25, "3 · Preparación", "Reglas de limpieza del E2\nCálculo de 60 features al\ncierre de t (sin leakage)\nExcluye posiciones inválidas", C["dato"], foot="Mensual · Python (pandas)")
box(101, 42, 27, 25, "4 · Scoring", "A: regla cobertura > 12\n(orden por capital inmovilizado)\nB: ensamble Top-600/mes\n(posiciones no incluidas en A)", C["modelo"], tc="white", foot="Mensual · scikit-learn / LightGBM")
# fila inferior
box(101, 5, 27, 27, "5 · Entrega", "Planilla y tablero en\nSharePoint por rol:\ncada tienda ve sus alertas\ncon motivo y variables", C["neg"], foot="Mensual, día 5 · Lucía O.")
box(68, 5, 28, 27, "6 · Decisión y acción", "Encargado propone acción\nComercial y Compras autorizan\nliquidar / transferir /\nfrenar compra / desestimar", C["neg"], foot="Cierre mensual · revisión humana")
box(35, 5, 28, 27, "7 · Registro", "Acción, motivo, responsable\ny resultado en t+3\n(target madurado)", C["fb"], foot="Cada cierre · Operaciones")
box(2, 5, 28, 27, "8 · Retroalimentación", "Recall@600 y precisión\npor mes y categoría\nModelo vs. regla a igual cupo\nReentrenamiento trimestral", C["fb"], foot="Trimestral · Mantenedor + soporte")
for a, b in [((30.8, 54.5), (34.2, 54.5)), ((63.8, 54.5), (67.2, 54.5)), ((96.8, 54.5), (100.2, 54.5))]: arrow(a, b)
arrow((114.5, 41.2), (114.5, 32.8))
for a, b in [((100.2, 18.5), (96.8, 18.5)), ((67.2, 18.5), (63.8, 18.5)), ((34.2, 18.5), (30.8, 18.5))]: arrow(a, b)
# loop de retroalimentación
arrow((12, 33.5), (104, 41.2), color="#c07a12", rad=-0.06, ls="--")
ax.text(68, 33.2, "Retroalimentación: nuevas etiquetas → reentrenar · si el modelo no supera a la regla a igual cupo, se publica sólo el bloque A", fontsize=7.8, color="#c07a12", ha="center")
fig.savefig(OUT, dpi=170, bbox_inches="tight", facecolor="white"); print("ok")
