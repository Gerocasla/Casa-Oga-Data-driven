# Registro de cambios — 2026-08-30, 14:59

Actualización del Entregable 1 · Parte D (Diseño de Dashboard) para alinearlo con
`minianalisiskpis.md` y `metodologialimpiezacsvs.md`, que pasan a ser la fuente de verdad.

Archivo generado: `entregables/Entregable-1-ParteD-Diseno-Dashboard-v2.docx` (v2.0)

---

## Cambios aplicados

### Reemplazos sobre la versión anterior

| Sección | Antes | Ahora |
|---|---|---|
| 1.1 Objetivo | Monitoreo diario de ventas, margen, rotación y quiebres de stock | Monitoreo mensual de dead stock a nivel SKU–tienda: incidencia, capital inmovilizado, costo mensual y evolución |
| 1.2 Preguntas de negocio | 9 preguntas, varias sobre margen por tienda, una vacía («¿?») | 5 preguntas, todas sobre dead stock |
| 2 Indicadores | Margen bruto %, Facturación, % vendido con liquidaciones, Días en inventario, Costo de almacenamiento | 5 KPIs con los valores del MD: 5,39% · $34,2 M · $3,15 M/mes · dead stock por categoría · 23,1 pp de caída de margen |
| 3.1 Usuarios | 4 roles, preguntas con «hoy» y «vs objetivo» | 5 roles con nombre, preguntas mensuales y sin referencia a presupuesto (dato no disponible) |
| 4 Wireframe | Mayormente texto de plantilla sin completar | Filtros, 5 tarjetas de KPI, 5 visualizaciones y nivel de detalle definidos |
| 5.1 Granularidad | «Transacción diaria», actualización «diaria o en tiempo real» | SKU–tienda–mes, actualización mensual (la extracción diaria no está automatizada) |
| 5.1 Fuentes | 7 fuentes listadas sin estado | Tabla con el estado real de cada fuente (disponible / pendiente / no disponible) |
| 5.2 Calidad de datos | Texto de ejemplo sin reemplazar | Las 7 correcciones documentadas en el MD de limpieza |
| 6.1 Alcance | V2 = «incorporar alertas y las 28 tiendas» | V1 = diagnóstico sobre las 28 tiendas; V2 = sistema predictivo con alertas mensuales |

### Secciones nuevas

- **2.1 Definición de dead stock** — las tres condiciones en OR (≥3 meses sin venta, stock muerto proyectado > 0, discontinuado con stock) y la justificación de usar OR en lugar de AND.
- **2.2 Validación del semáforo del negocio** — el umbral 30/70 deja 73,6% del catálogo en Rojo, por encima de la capacidad operativa declarada (420–700 SKU–tienda por mes). No es accionable tal cual.
- **6.2 Datos pendientes de reclamar** — `Proveedores.csv` y `Costo_almacenamiento.csv`.

### Otros archivos incorporados

- `entregables/Entregable-1-ParteB-Objetivos-Stakeholders-Restricciones.docx`
- `entregables/Preguntas-abiertas-para-validacion.docx`
- `entregables/Semaforo-Dead-Stock-Casa-Oga.html` y `.pdf` — análisis de calibración del semáforo
- `Respuestas Grupo 1 al 18-8.xlsx` — segunda ronda del relevamiento (54 preguntas)

---

## Pendientes

### Bloqueantes para la entrega

- [ ] **Resolver el número de dead stock.** El MD reporta 431 combinaciones (5,39%). Reimplementando la definición escrita sobre el mismo universo (7.993 pares con stock en dic-2025) el resultado da **620 (7,76%)**: C1 = 365, C2 = 168, C3 = 139, sin intersección entre las tres. El propio texto del MD dice que las condiciones 2 y 3 «casi duplican» la cobertura, lo cual encaja con 620 y no con 431. De ese número dependen también los $34,2 M y los $3,15 M/mes. Revisar el script que generó las cifras.
- [ ] Completar **fecha de entrega** y la columna de **roles** de cada integrante en la portada.
- [ ] Faltan los **legajos** de Simón Volpato Escandarani y Santiago Javier Hernández.

### Decisiones a tomar

- [ ] **Umbrales de semáforo por KPI.** El MD da valores actuales pero no umbrales; en el entregable quedaron como «pendiente de validar con el negocio».
- [ ] **Margen y facturación**: se quitaron de los KPIs por pertenecer al otro proyecto (riesgo de margen bajo por tienda). Definir si vuelven como franja de contexto sin semáforo.
- [ ] Adjuntar el **boceto/mockup** del dashboard al entregable.

### Datos a reclamar al cliente

- [ ] `Proveedores.csv` — figura como entregado en la Parte 3 del relevamiento, no está entre los archivos recibidos.
- [ ] `Costo_almacenamiento.csv` — ídem. **No estaba detectado en el MD**; se suma al mismo reclamo.
- [ ] Dataset de **devoluciones** — el cliente confirmó que lo entregará por separado. La limpieza actual lleva a 0 las 2.317 filas negativas, que es la decisión opuesta a lo acordado.
- [ ] **Movimientos de 2026** (ventas, stock, liquidaciones) — confirmados por el cliente.
- [ ] **Histórico de transferencias** entre tiendas y depósito — Lucía O. coordina; falta que nosotros confirmemos rango de fechas y nivel de detalle.

### A validar con el negocio

- [ ] **«Regalos» no existe en el catálogo.** El cliente la nombra como categoría estacional y propuso pilotear sobre «Decoración y Regalos». Las 7 categorías reales son Decoración, Textil hogar, Cocina y mesa, Muebles, Baño, Organización e Iluminación. Además Decoración es la categoría más vendedora (21,7%), así que no encaja con el criterio de «baja contribución» con el que la eligieron.
- [ ] **Estacionalidad por categoría.** El negocio pide cortes distintos por categoría; en los datos las 7 categorías comparten el mismo patrón (pico noviembre-diciembre, piso enero-febrero). Confirmar si es una limitación del dataset del curso.

### Higiene del repositorio

- [ ] Eliminar las versiones viejas `mini-analisis-kpis.md` y `metodologia-limpieza-csvs.md`, que conviven con `minianalisiskpis.md` y `metodologialimpiezacsvs.md` y contienen cifras desactualizadas (365 combinaciones / 4,6%).
