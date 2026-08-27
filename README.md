# Casa Óga — Proyecto Data Driven

Repositorio del trabajo de la materia "Factibilidad de Proyectos Data Driven" — caso Casa Óga (retail de hogar y decoración, empresa ficticia con fines académicos).

## Estructura

```
casa-oga-data-driven/
├── docs/                  → análisis y metodología generados durante el trabajo
│   ├── metodologia-limpieza-csvs.md
│   └── mini-analisis-kpis.md
├── data/
│   └── raw/               → los 6 CSV originales provistos por la cátedra
├── materials/
│   └── Respuestas_Grupo_1.xlsx
└── entregables/           → completar con los .docx de cada Entregable (ver nota abajo)
```


## Resumen del proyecto

Casa Óga es una cadena de retail de hogar y decoración (28 tiendas + e-commerce) que quiere pasar de decisiones basadas en experiencia a decisiones basadas en datos, en dos frentes:

1. **Mix de productos / dead stock**: predecir qué SKUs tienen riesgo de convertirse en stock de baja rotación.
2. **Clientes y fidelización / churn**: predecir qué clientes tienen riesgo de dejar de comprar (pendiente de datos a nivel cliente, todavía no provistos).

Con los datos disponibles hoy (ventas, stock, catálogo y liquidaciones a nivel SKU-tienda-mes, 2022-2025) se puede avanzar en el primer frente. El detalle de la limpieza aplicada a los CSV y el mini-análisis de KPIs de negocio están en `docs/`.

Reporte visual completo (KPIs, dead stock, costo de stock parado, margen en liquidaciones): [Casa Óga en Números](https://claude.ai/code/artifact/e5c495a6-c672-47fe-9d54-795db8806a7e).
