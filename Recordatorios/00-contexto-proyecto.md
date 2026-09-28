# Contexto del proyecto

> Actualizado 28-09-2026. Estado general y cómo reproducir: `README.md` de la raíz.

- **Materia:** Factibilidad de Proyectos Data Driven (ITBA, 2C 2026) — **Grupo 1**.
- **Integrantes:** Gerónimo Fasce (64401) · Gianfranco Di Claudio (64505) · Matías Fleischer (65616) · Simón Volpato Escandarani (legajo pendiente) · Santiago Javier Hernández (legajo pendiente; responsable del dashboard).
- **Caso:** Casa Óga, retail de hogar y decoración (28 tiendas + e-commerce), empresa ficticia.
- **Frente trabajado:** mix de productos / dead stock — modelo predictivo SKU–tienda de riesgo a 3 meses. (Frente churn: sin datos de clientes, fuera de alcance.)
- **Stakeholders del caso:** María G. (Comercial, aprobadora del target y del semáforo) · Carlos F. (Financiera, presupuesto y costo de capital) · Lucía O. (Operaciones, capacidad de intervención) · Diego P. (Compras) · responsables de tienda. IT: el responsable renunció sin dejar documentación (P3-P4).

## Dónde está cada cosa
- **Repo (privado):** https://github.com/Gerocasla/Casa-Oga-Data-driven — es la fuente de verdad; las carpetas locales de cada integrante son clones.
- `Datasets/` crudos (no se editan) · `Datasets_Normalizados/` **usar estos** · `Datasets_Modelo/` dataset de entrenamiento.
- `Entregable/Entregable 1/` TP1 entregado · `Entregable/Entregable 2/` TP2 (Word, dashboard, scripts, presentación).
- `Material/` respuestas del negocio y diapositivas · `Mejoras/` feedback de la cátedra · `Cambios/` análisis del TP1 (históricos) · `Recordatorios/` estas notas.

## Estructura de los entregables
- **Entregable 1 (Clases 1-4):** A Contexto · B Objetivos, stakeholders y restricciones · C Visión, metodología y backlog · D Dashboard.
- **Entregable 2 (Clases 6-8):** A Alcance, EDA y evaluación de calidad · B Hallazgos y plan de mejora, dashboard antes/después, dataset de entrenamiento y transformaciones.
- **Entrega final:** un documento consolidado con todos los TPs y una sección «Cambios» (ver `01-reglas-de-entrega.md`).

## Cifras de referencia

**Vigentes (Entregable 2, corte ago-2026, datos limpios):**
- Venta ene-2022 a ago-2026: **$40.083,4 M** · 925.015 unidades (devoluciones neteadas). 2026 vs 2025 (ene-ago, bruto): **−13,2%**.
- Cobertura: mediana ~5 meses estable; percentil 99 de **16 a 48 meses** entre dic-25 y ago-26.
- Posiciones con cobertura > 12 meses a ago-26: **882 · $184,1 M a costo** · 363 SKUs · ~$9,2 M/mes al 5%.
- Target: **3,40%** de positivos (6.853 / 201.306, dataset v3); 2,5% hasta 2025 y 9% en 2026.
- Costo de mantener stock: 5% mensual (2% almacenaje + 3% oportunidad, negocio); el dataset dice 1,5% de almacenaje.

**Del TP1 (corte dic-2025) — NO reproducibles, no usar sin aclarar:**
- Capital inmovilizado $83,9 M (661 posiciones), 10,63% → 8,27%, cobertura 10,6 → 5,2, semáforo 345 rojo / 652 amarillo. El script `calculo_dead_stock.py` no existe; circulan tres cifras para la misma métrica (431, 620 y 661). La «cobertura 10,6 → 5,2» es un efecto de cálculo (D2) y la «estacionalidad 143/61» es crecimiento (D1).
- Ver `02-correcciones-tp1.md` antes de usar cualquiera en el consolidado.
