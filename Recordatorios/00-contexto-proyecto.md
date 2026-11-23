# Contexto del proyecto

> Actualizado 23-11-2026. Estado general y cómo reproducir: `README.md` de la raíz. **Entrega final:** `Entregable/Entregable 4/README.md`.

- **Materia:** Factibilidad de Proyectos Data Driven (ITBA, 2C 2026) — **Grupo 1**.
- **Integrantes:** Gerónimo Fasce (64401) · Gianfranco Di Claudio (64505) · Matías Fleischer (65616) · Simón Volpato Escandarani (legajo pendiente) · Santiago Javier Hernández (legajo pendiente; responsable del dashboard).
- **Caso:** Casa Óga, retail de hogar y decoración (28 tiendas + e-commerce), empresa ficticia.
- **Frente trabajado:** mix de productos / dead stock — modelo predictivo SKU–tienda de riesgo a 3 meses. (Frente churn: sin datos de clientes, fuera de alcance.)
- **Stakeholders del caso:** María G. (Comercial, aprobadora del target y del semáforo) · Carlos F. (Financiera, presupuesto y costo de capital) · Lucía O. (Operaciones, capacidad de intervención) · Diego P. (Compras) · responsables de tienda. IT: el responsable renunció sin dejar documentación (P3-P4).

## Dónde está cada cosa
- **Repo (privado):** https://github.com/Gerocasla/Casa-Oga-Data-driven — es la fuente de verdad; las carpetas locales de cada integrante son clones.
- `Datasets/` crudos (no se editan) · `Datasets_Normalizados/` **usar estos** · `Datasets_Modelo/` dataset de entrenamiento.
- `Entregable/Entregable 1/` TP1 entregado · `Entregable/Entregable 2/` TP2 (Word, dashboard, scripts, presentación) · `Entregable/Entregable 3/` TP3 (compilado, modelo v3, presentación).
- **`Entregable/Entregable 4/` ENTREGA FINAL:** informe consolidado (docx/pdf), presentación (pptx + speech) y dashboard HTML por área, con todos sus generadores.
- `Material/` respuestas del negocio y diapositivas · `Mejoras/` feedback de la cátedra · `Cambios/` análisis del TP1 (históricos) · `Recordatorios/` estas notas.

## Estructura de los entregables
- **Entregable 1 (Clases 1-4):** A Contexto · B Objetivos, stakeholders y restricciones · C Visión, metodología y backlog · D Dashboard.
- **Entregable 2 (Clases 6-8):** A Alcance, EDA y evaluación de calidad · B Hallazgos y plan de mejora, dashboard antes/después, dataset de entrenamiento y transformaciones.
- **Entregable 3 (Clases 10-13):** factibilidad técnica y modelado, factibilidad económica, evaluación, riesgos y legal, diseño de la solución y veredicto.
- **Entrega final (Entregable 4):** un documento consolidado con todos los TPs y una sección «Cambios» (ver `01-reglas-de-entrega.md`), más la presentación y el dashboard. Armado el 22/23-11-2026.

## Cifras de referencia

**Entrega final (dataset v4, `Entregable 4/Modelo/resultados/modelo_final_v4_resultados.json`) — las que mandan:**
- Dataset v4: 201.310 filas × 60 features · 3,22% positivos. Train ≤ dic-24 · val abr-sep 25 · test ene-may 26.
- Modelo: HistGradientBoosting. Flujo = regla (cobertura > 12) + 150 alertas del modelo; break-even 11,8%.
- Casos acertados, flujo vs regla con el mismo cupo: 404 vs 354 (2025) · 1.475 vs 1.452 (2026).
- ROI 3 años del total (año tipo 2025): +18,6%, recupero en ~24 meses.
- Ago-26: 866 posiciones con cobertura > 12 (ARS 178,6 M a costo) + 150 del modelo = 1.016 alertas (ARS 189,1 M).
  - La capacidad es de 700 alertas (28 × 25); las que entran en el cupo concentran el 93% del capital.

**Del Entregable 2 (v3; reemplazadas por las de arriba donde se superponen):**

- Venta ene-2022 a ago-2026: **$40.083,4 M** · 925.015 unidades (devoluciones neteadas). 2026 vs 2025 (ene-ago, bruto): **−13,2%**; 8,9 pp son los 96 SKUs discontinuados a fin de 2025 (sin altas desde jul-2025). Los 634 SKUs que siguen: −4,8%.
- Cobertura: mediana ~5 meses estable; percentil 99 de **16 a 48 meses** entre dic-25 y ago-26.
- Posiciones con cobertura > 12 meses a ago-26: **882 · $184,1 M a costo** · 363 SKUs · ~$9,2 M/mes al 5%.
- Target: **3,40%** de positivos (6.853 / 201.306, dataset v3); 2,5% hasta 2025 y 9% en 2026.
- Costo de mantener stock: 5% mensual (2% almacenaje + 3% oportunidad, negocio); el dataset dice 1,5% de almacenaje.

**Del TP1 (corte dic-2025) — NO reproducibles, no usar sin aclarar:**
- Capital inmovilizado $83,9 M (661 posiciones), 10,63% → 8,27%, cobertura 10,6 → 5,2, semáforo 345 rojo / 652 amarillo. El script `calculo_dead_stock.py` no existe; circulan tres cifras para la misma métrica (431, 620 y 661). La «cobertura 10,6 → 5,2» es un efecto de cálculo (D2) y la «estacionalidad 143/61» es crecimiento (D1).
- Ver `02-correcciones-tp1.md` antes de usar cualquiera en el consolidado.
