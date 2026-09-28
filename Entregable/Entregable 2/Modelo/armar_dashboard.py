# -*- coding: utf-8 -*-
"""Arma Entregable 2/Dashboard-Calidad-Antes-Despues.html con los resultados de:
EDA/antes_despues.py (antes_despues.json), EDA/eda_ago26.py (eda_ago26.json) y Modelo/insights_dashboard.py (insights.json)."""
import os, json
BASE = os.path.dirname(os.path.abspath(__file__)); E2 = os.path.dirname(BASE)
L = lambda p: json.load(open(p, encoding="utf-8"))
data = {"ad": L(os.path.join(E2, "EDA", "resultados", "antes_despues.json")),
        "eda": L(os.path.join(E2, "EDA", "resultados", "eda_ago26.json")),
        "ins": L(os.path.join(BASE, "resultados", "insights.json"))}
tpl = open(os.path.join(BASE, "dashboard_plantilla.html"), encoding="utf-8").read()
out = os.path.join(E2, "Dashboard-Calidad-Antes-Despues.html")
open(out, "w", encoding="utf-8").write(tpl.replace("/*__DATA__*/", json.dumps(data, ensure_ascii=False)))
print("OK ->", out)
