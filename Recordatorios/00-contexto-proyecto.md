# Contexto del proyecto

- **Materia:** Factibilidad de Proyectos Data Driven (ITBA) — **Grupo 1**.
- **Caso:** Casa Óga, retail de hogar y decoración (28 tiendas + e-commerce), empresa ficticia.
- **Frente trabajado:** Mix de productos / dead stock — modelo predictivo SKU-tienda de probabilidad de dead stock a 3 meses. (Frente churn: pendiente de datos de clientes.)
- **Responsable del dashboard (Parte D):** Santiago Hernández.

## Dónde está cada cosa
- **Carpeta local de trabajo:** `Desktop\Data-Driven\`
  - `Datasets\` → 15 CSV (los 6 originales + 9 adicionales que no están en el repo)
  - `Entregable\Entregable 1\` → documentos entregados del TP1 (`Entregable_1_Consolidado_G1.docx`, `Dashboard Entrega 1.html`, partes B/D, semáforo, etc.)
  - `Entregable\Entregable 2\` → plantilla/consigna del TP2 (`Entregable 2 - Parte A - Alcance y Evaluacion de Calidad de Datos.docx`)
  - `Cambios\` → documentos de análisis y sus versiones (metodología de limpieza, mini-análisis KPIs, actualización Parte D, panel dead stock)
  - `Material\` → respuestas del cliente (xlsx) y README del repo
  - `Mejoras\` → feedback de la cátedra (`Feedback Grupo 1.xlsx`)
  - `Recordatorios\` → esta carpeta
- **Repo GitHub (privado):** https://github.com/Gerocasla/Casa-Oga-Data-driven
- `Desktop\ITBA\DATADRIVEN\` → carpeta vieja. **No tocar.**

## Estructura del Entregable 1 (Clases 1-4)
- **Parte A** — Contexto organizacional
- **Parte B** — Objetivos, stakeholders y restricciones
- **Parte C** — Visión, metodología y backlog inicial
- **Parte D** — Diseño de dashboard

## Cifras insignia (deben ser consistentes en TODO el documento)
- Capital inmovilizado dic-2025: **$83,9 M** (661 posiciones, definición binaria)
- % posiciones en dead stock: **10,63% (ene-2023) → 8,27%**; cobertura **10,6 → 5,2 meses**
- Semáforo por cobertura: **345 rojo / 652 amarillo**; 420-700 alertas mensuales
- Piloto: Cocina y mesa + Decoración — 2.911 posiciones, $49,4 M de $83,9 M (59%)
- Presupuesto USD 30.000; costo de mantener stock 5% mensual ($7,7 M/mes)

> ⚠️ Ver corrección #1 en `02-correcciones-tp1.md`: la tabla de la Sección 5.3 tiene cifras que contradicen estas.
