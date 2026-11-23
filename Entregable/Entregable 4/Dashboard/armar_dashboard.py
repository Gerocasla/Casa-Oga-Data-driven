"""Entregable 4 - builds the self-contained dashboard (one HTML file, works offline, no external libraries).

Inputs : Dashboard/datos_dashboard.json (from preparar_datos_dashboard.py) and Dashboard/dashboard_plantilla.html
Output : Entregable 4/Casa-Oga-Dashboard.html

Run from the repo root:
  python "Entregable/Entregable 4/Dashboard/preparar_datos_dashboard.py"   # trains the model and scores the last month
  python "Entregable/Entregable 4/Dashboard/armar_dashboard.py"
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
datos = (HERE / "datos_dashboard.json").read_text(encoding="utf-8").replace("</", "<\\/")
html = (HERE / "dashboard_plantilla.html").read_text(encoding="utf-8").replace("__DATOS__", datos)
out = HERE.parent / "Casa-Oga-Dashboard.html"
out.write_text(html, encoding="utf-8")
print(f"OK -> {out} ({out.stat().st_size / 1024:.0f} KB)")
