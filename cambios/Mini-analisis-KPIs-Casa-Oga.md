# Mini-análisis de datos — Casa Óga (2022-2025)

Análisis exploratorio de los 6 CSV subidos al proyecto (Calendario, Tiendas, Productos_catalogo, Stock_SKU_tienda_mensual, Ventas_SKU_tienda_mensual, Liquidaciones), más las respuestas oficiales del relevamiento a la empresa (Grupo 1) y el documento de contexto "Casa ÓGA_Proyecto Data Driven 2Q 2026 Mix Productos.pdf".

**Dashboard principal:** [Panel de Dead Stock](https://claude.ai/code/artifact/d360de71-73a6-43a5-80c5-d099da6233b6) — 5 pestañas: Contexto del negocio · Dead stock resumen · Semáforo propuesto · Evolución · Explorador por tienda.
**Otros reportes:** [Casa Óga en Números](https://claude.ai/code/artifact/e5c495a6-c672-47fe-9d54-795db8806a7e) · [Histórico % vendido](https://claude.ai/code/artifact/851f10a1-61a4-4156-befb-158561905139) · [Costo de Almacenaje — Stock Parado](https://claude.ai/code/artifact/62c3cb1e-a77e-40a3-b8b1-5539ac39f49a)

> **⚠️ Lo más importante de este documento (31-ago-2026).** Antes de armar la presentación se testeó la afirmación central del proyecto — "el dead stock viene empeorando" — por cuatro caminos independientes. **Ninguno la confirma.** El detalle está en "Verificación del diagnóstico". Esto no invalida el proyecto, pero **sí obliga a cambiar el mensaje**: no se puede presentar como "les frenamos un deterioro". Ver "Qué conviene presentar" al final.
>
> **Nota:** los números de dead stock fueron recalculados de punta a punta tras detectar que el resultado anterior (431 combinaciones, 5,39%) no era reproducible a partir de la propia definición escrita. Ver "Dead stock: metodología final"; script en `calculo_dead_stock.py`.
>
> **Nota:** la sección "Indicadores clave" también se recalculó — sus números salían de datos crudos, sin la limpieza usada en el resto del documento. Diferencias menores al 1%.

## Alcance de los datos
- 28 tiendas, 800 SKUs en catálogo (634 activos), 239.336 filas SKU–tienda–mes de ventas y de stock (236.958 tras deduplicar por clave).
- Rango: enero 2022 – diciembre 2025 (48 meses). 7 categorías, 25 subcategorías.
- El catálogo trae `fecha_alta_catalogo`, `fecha_baja_catalogo` y `estado` (Activo/Discontinuado) por SKU — se usan para el modelo de dead stock.
- No hay archivo de clientes/CRM — soporta bien el proyecto de **Mix de Productos / dead stock**, pero **no** el de **churn de clientes**.
- El relevamiento confirmó que **no existe una definición formal de dead stock** en la empresa hoy. También mencionan un `Proveedores.csv` como "ya entregado" que **no está entre los archivos** — pendiente de reclamar.
- **Es un dataset armado para el curso** (el documento de contexto aclara que Casa Óga es ficticia). Es posible que se haya generado sin incorporar el deterioro que describe el enunciado — ver "Verificación del diagnóstico".

## Indicadores clave
- Venta del último trimestre (oct–dic 2025): **$3.401,1 M** · 77.954 unidades · **+8,9%** vs. el mismo trimestre de 2024.
- Venta acumulada 4 años: $32.538,4 M · 750.538 unidades. Crecimiento anual: 2022 $1.812 M → 2023 $6.323 M → 2024 $10.669 M → 2025 $13.734 M. Últimos 12 meses vs. 12 previos: **+28,7%**.
- Margen bruto teórico de lista: ~44,9% promedio, parejo entre categorías (43,7%–46,1%).
- Mix por categoría (venta / % de SKUs): Decoración 22,8% / 19,6% · Cocina y mesa 19,1% / 15,3% · Iluminación 14,2% / 10,8% · Textil hogar 12,7% / 15,9% · Muebles 11,8% / 14,6% · Organización 11,1% / 11,8% · Baño 8,4% / 12,1%. **No aparece ninguna categoría con "alta variedad y baja contribución" en grado extremo** — Baño es la más despareja (3,7 pp de brecha), pero moderada.
- Por región: AMBA 39,3% · Centro 21,9% · NOA 17,9% · Cuyo 17,2% · Patagonia 3,7%.
- Estacionalidad: **todas las categorías** con el mismo patrón — pico en noviembre-diciembre, piso en enero-febrero, sin estacionalidades diferenciadas. Vale confirmarlo con el negocio.
- Concentración (Pareto): 248 de 798 SKUs con venta explican el 80% de la facturación; los otros 550 son cola larga — ahí vive el riesgo de baja rotación.

## Verificación del diagnóstico: ¿el problema viene empeorando?

El documento de contexto (sección 3) dice que "durante el último año calendario" la dirección detectó que **"una proporción creciente de SKUs muestra muy baja rotación"** y que el capital inmovilizado aumentó. Se buscó ese deterioro por cuatro caminos independientes:

| Indicador | 2023 | 2025 | Dirección |
|---|---|---|---|
| % de posiciones en dead stock | 8,86% | 7,93% | Mejora |
| % del gasto de almacenaje en stock parado 3+ meses | 1,28% | 0,99% | Mejora |
| Cobertura total del inventario | 8,1 meses | 5,8 meses | Mejora |
| Capital inmovilizado, en pesos | $41,4 M | $93,1 M | **Empeora** |

Además se descartaron dos explicaciones alternativas:

- **No hay sobrecompra.** Entre 2023 y 2025 las ventas se multiplicaron por 2,13 y el stock por 2,14. Las unidades por posición están planas (x1,03).
- **No se está engordando la cola.** Se midió la distribución de cobertura posición por posición en 36 cortes mensuales: la mediana está clavada en ~5,4 meses y **todos** los percentiles mejoraron (p90 de 9,78 a 9,31 meses; p99 de 20,3 a 16,0; posiciones con más de 12 meses de cobertura, de 7,48% a 2,63%). No es el caso de "el promedio mejora pero los casos malos empeoran".

**Conclusión:** en pesos absolutos el capital inmovilizado sí creció (más del doble), pero acompañando un negocio que también se duplicó. Normalizado de cualquier forma, el problema está estable o mejorando.

**Esto no contradice a la dirección, la explica.** Su propio documento (pág. 3) dice que el seguimiento "continúa siendo reactivo" y que la baja rotación "se detecta recién en el conteo de inventario de fin de año". Mirando pesos acumulados una vez al año, sin métrica normalizada contra un catálogo que se duplicó, es esperable percibir un deterioro que el indicador relativo no muestra.

*(Scripts: `verificacion_hallazgos.py`.)*

## Dead stock: metodología final

La unidad de medida es la **combinación SKU–tienda**: un producto puede estar sano en una tienda y frenado en otra, así que cuenta una vez por cada tienda donde tiene stock. Hoy hay **7.993 combinaciones con stock**. Una es dead stock si tiene `stock_disponible > 0` y cumple **cualquiera** de:

1. **`meses_sin_venta ≥ 3`** — 0 unidades vendidas en los últimos 3 meses.
2. **`stock_muerto_proyectado > 0`** — el stock excede lo que se vendería en 12 meses al ritmo reciente. `run_rate = ventas últimos 12 meses ÷ antigüedad de la combinación (tope 12)`; `stock_muerto_proyectado = máx(0, stock_disponible − run_rate × 12)`.
3. **Discontinuado con stock** — dado de baja del catálogo pero con mercadería remanente.

Se eligió el **OR**: con AND el universo cae a menos del 1% del catálogo, dejando afuera el caso de "vende poco pero tiene demasiado stock".

**Corrección (31-ago-2026):** las 431 combinaciones anteriores no eran reproducibles — la sola unión de las condiciones 1 y 3 ya supera ese número, imposible en un OR. Venía de una sesión previa cuyo script nunca se guardó. Se recalculó de cero. De paso se corrigió la deduplicación de Stock y Ventas, que solo eliminaba filas idénticas y dejaba pasar ~2.378 filas por archivo con la misma clave (mes + tienda + SKU) y valores distintos.

**Limitación de la condición 1 (importante para presentar).** Las posiciones que marca C1 venden **0,50 unidades/mes** en la mediana, contra 1,92 del total. A ese ritmo la probabilidad de tres meses seguidos en cero *por puro azar* es del **22,3%**, y el **64,5%** de todas las posiciones tuvo alguna racha de 3+ meses en cero en los últimos 24 meses. C1 detecta productos de bajo volumen comportándose normal tanto como productos frenados. **Es una lista a revisar, no a liquidar.**

La condición 2 mantiene una ambigüedad: "meses reales que la combinación lleva con datos" se leyó como antigüedad desde su primera aparición en stock (tope 12). Decisión documentada, a validar.

## Dead stock: resultado (corte dic-2025)
- **661 combinaciones SKU–tienda, 8,27% de las 7.993 con stock.** Involucran 263 SKUs distintos y las 28 tiendas, y representan el **4,0% de las unidades físicas**.
- **Capital inmovilizado: $83,9 M** — 2,38% del valor total del stock a costo.

**Composición del capital (las tres condiciones no valen lo mismo):**

| Condición | Posiciones | Capital | % del total | Naturaleza |
|---|---|---|---|---|
| Discontinuado con stock | 139 | $39,6 M | 47% | **Accionable hoy, sin modelo** |
| Sin venta 3 meses (C1) | 365 | $34,6 M | 41% | Alerta a validar (ver limitación) |
| Excedente estructural (C2) | 157 | $9,8 M | 12% | Palanca de compras / transferencias |

**El hallazgo más accionable: los 139 casos de discontinuados corresponden a solo 13 SKUs distintos.** Cada uno tiene stock remanente en varias tiendas, así que la decisión se toma una vez por producto y se ejecuta en todas. El mayor (SKU00657, Cocina y mesa) tiene 263 unidades en 15 tiendas por **$13,6 M**.

**Costo de mantenerlo:** el 5% mensual (2% almacenaje + 3% oportunidad) lo confirmó el negocio, pero **la base sobre la que se aplica fue decisión nuestra**. Sobre valor a costo da **$4,2 M/mes** ($50,4 M/año); sobre precio de lista da **$7,7 M/mes** ($92,2 M/año — más que el valor del propio stock, difícil de defender). Se muestra la base a costo por ser la convención habitual. **Conviene validar cuál prefiere el negocio.**

- **Por categoría** (% de posiciones en dead stock): Cocina y mesa 9,87% · Baño 9,32% · Decoración 8,46% · Iluminación 8,39% · Textil hogar 8,17% · Organización 6,93% · Muebles 6,50%.

## Semáforo propuesto

La definición de dead stock es **binaria** y solo captura los casos extremos: una combinación con 9 o 10 meses de stock encima hoy figura como sana, aunque claramente rote lento. El semáforo agrega esa gradación sin reemplazar la definición.

| Banda | Criterio | Posiciones | % | Stock a costo | Uso |
|---|---|---|---|---|---|
| 🔴 Rojo | >12 meses de cobertura **o** discontinuado | 345 | 4,32% | $109,7 M | Lista de acción del mes |
| 🟡 Amarillo | entre 9 y 12 meses de cobertura | 652 | 8,16% | $356,3 M | Lista de vigilancia |
| 🟢 Verde | menos de 9 meses | 6.996 | 87,53% | $3.062,2 M | Sin acción |

**Los cortes se calibraron contra la capacidad operativa declarada por el negocio (420 a 700 combinaciones por mes),** no por criterio estético. La mediana del catálogo rota en 5,5 meses y el percentil 90 está en 9,3 — por eso el amarillo arranca en 9 meses: marca al 10% que más tarda en rotar. Con el rojo en 12 meses más los discontinuados, la lista de acción queda en 345 posiciones, dentro de la capacidad.

| Si el corte de acción fuera… | Posiciones | Stock alcanzado | Costo mensual (5%) |
|---|---|---|---|
| >6 meses | 3.189 (39,9%) | $1.879,3 M | $94,0 M/mes |
| >7 meses | 2.275 (28,5%) | $1.286,5 M | $64,3 M/mes |
| >8 meses | 1.382 (17,3%) | $763,2 M | $38,2 M/mes |
| **>9 meses** | **874 (10,9%)** | **$434,2 M** | **$21,7 M/mes** |
| >10 meses | 544 (6,8%) | $231,4 M | $11,6 M/mes |
| >11 meses | 401 (5,0%) | $135,8 M | $6,8 M/mes |
| **>12 meses** | **210 (2,6%)** | **$70,9 M** | **$3,5 M/mes** |
| >14 meses | 147 (1,8%) | $33,8 M | $1,7 M/mes |

Se ve que mover el corte tres meses cambia la escala del problema por veinte. Y que ser demasiado exigente no tiene sentido: con corte en 6 meses estaríamos apuntando a más de la mitad del inventario de la empresa, que no es dead stock sino el stock normal de operación.

**⚠️ Base de cálculo — no comparar con la sección anterior sin leer esto.** Los pesos de esta sección toman el **stock completo** de cada posición marcada, y el costo mensual es el 5% sobre ese valor a costo. Es una base más amplia que el "capital inmovilizado" de la sección de dead stock, que en las posiciones que sí venden descuenta la parte que va a rotar igual. Por eso la banda roja son $109,7 M de stock acá pero **$56,4 M medida con el criterio de capital inmovilizado** ($2,8 M/mes contra los $4,2 M/mes del dead stock completo). Las dos bases son válidas pero responden preguntas distintas: para decidir un umbral operativo interesa el stock completo (es lo que hay que mover físicamente); para cuantificar la pérdida, el capital inmovilizado, que es más conservador. Lo que no se puede es mezclarlas sin avisar — sin esta aclaración, la banda roja parecía costar más ($5,5 M/mes) que el dead stock completo del que es subconjunto.

**Lo que aporta:** el rojo es un subconjunto de las 661 que ya detectábamos, pero de las 652 en amarillo **603 no aparecen hoy en ningún indicador**. Esa es la zona ciega que el semáforo cubre. Por categoría, rojo + amarillo se concentra en Decoración (13,5%), Iluminación (13,4%) y Cocina y mesa (13,4%).

*(Pendiente de validar con el negocio antes de fijarlo como definición oficial.)*

## Evolución en el tiempo (ene-2023 a dic-2025)
- En % del catálogo: de 10,63% en ene-23 a 8,27% en dic-25 (promedio últimos 12 meses: 7,93%), con bastante ruido mes a mes.
- En pesos: de $34,3 M (ene-23) a $83,9 M (dic-25); promedió $41,4 M en 2023 contra $93,1 M en los últimos 12 meses. Mes más alto de la serie: **$149,1 M en agosto de 2025**, 1,6x el promedio de ese año.
- Cobertura total del inventario: de 10,55 meses (ene-23) a 5,16 meses (dic-25), bajando de forma sostenida.
- Serie mensual completa en `dead_stock_evolucion_mensual.csv`.

## Diferencias entre tiendas: son ruido, no gestión

- Con ~285 posiciones por tienda y una tasa promedio de 8,27%, el desvío esperable **por puro azar** es de ±1,63 pp. El desvío observado entre las 28 tiendas es de **1,24 pp — menor que el que produciría el azar solo**.
- Solo 1 de 28 tiendas (Tucumán 9) se aparta más allá de su margen de error, que es lo que se esperaría por azar al comparar 28 tiendas con 95% de confianza.
- No hay relación con el tamaño del local (correlación −0,054 con los m²) ni con el formato.

**Implicancia:** no corresponde abrir investigaciones por tienda a partir de este ranking ni presentarlo como desempeño. El panel lo muestra con barras de error, línea de promedio y un aviso explícito.

## Umbral de "semáforo" que proponía el negocio (validación)
El negocio pensaba en Rojo <30%, Amarillo 30-70%, Verde >70% de rotación mensual (unidades vendidas ÷ stock). Con ese umbral literal, **73,6% del catálogo queda en Rojo** — muy por encima de su capacidad operativa. No es accionable. La propuesta de la sección "Semáforo propuesto" reemplaza este planteo con cortes calibrados contra esa misma capacidad.

## Costo de almacenaje aislado
Aislando solo el 2% de almacenaje (sin el 3% de oportunidad) del stock sin venta en 3+ meses: en pesos nominales crece (de $756 mil/mes en ene-2023 a $1,28 M/mes en dic-2025) porque el inventario total también creció, pero como **% del gasto total de almacenaje** bajó, de 1,28% promedio en 2023 a 0,99% en los últimos 12 meses. El porcentaje no cambia si se calcula sobre costo en vez de lista.

*(Esta vista tenía pestaña propia en el panel y se quitó el 31-ago-2026: su conclusión ya está en la tabla de verificación y en el gráfico de cobertura, y era repetición. El detalle sigue disponible en el artifact standalone "Costo de Almacenaje — Stock Parado".)*

## Impacto de las liquidaciones en el margen
- Margen normal promedio: 44,9%. Con liquidación: 21,7%. Caída: **23,1 pp**. Descuento promedio: 26,9%. El 14,3% vende por debajo del costo.
- Mayor caída por motivo: Sobrestock (−24,6 pp) > Baja rotación (−23,5 pp) > Discontinuación (−22,6 pp) > Fin de temporada (−22,0 pp).

> **Corrección (31-ago-2026) — se retira el argumento de "detectar antes = liquidar con menos descuento".** Este documento lo daba como base del argumento de negocio. **Los datos no lo respaldan:**
> - Correlación entre meses parado antes de liquidar y profundidad del descuento: **0,027** (p=0,65, no significativa).
> - De 505 liquidaciones válidas, **467 se hicieron con el producto vendiendo normal el mes anterior** — ya liquidan a tiempo. Solo 7 tras 3+ meses parado.
> - Volumen marginal: **1.560 unidades en 4 años** (0,2% de las unidades vendidas), **$21,5 M de margen resignado ($5,4 M/año)**.
>
> El "−23,1 pp" es cierto pero sobre una base mínima. No conviene usarlo como justificación económica del proyecto.

## Compras y reposición (relevamiento oficial)
No hay frecuencia de compra/reposición formal documentada. Circuito informal: Compras y Categorías propone según tendencias; aprobación entre Compras y Comercial, sin comité; cantidad inicial por mínimo del proveedor + estimación manual (no un modelo); asignación a tiendas manual. El `Proveedores.csv` que permitiría estimar cadencia real está marcado como entregado pero no disponible.

## Transferencias entre tiendas
No se describe un proceso sistemático. Se pidió a Gerencia de Operaciones el historial de transferencias para incorporarlo como palanca de acción (mover excedente a una tienda con mejor rotación en vez de liquidar). Especialmente relevante para la banda amarilla y para la condición 2.

## Calidad de datos
- 1.209 filas de stock con `stock_disponible` negativo; 2.317 filas de ventas con valores negativos (¿devoluciones sin marcar?).
- **15 SKUs duplicados en el catálogo** — se usa la 1ra ocurrencia.
- **~2.378 filas por archivo en stock y en ventas** que comparten clave mes+tienda+SKU con valores distintos, concentradas en esos 15 SKUs. Se deduplica por clave (solo 21 y 56 eran duplicados exactos).
- Nombres de categoría inconsistentes ("Decoración"/"DECO", "Textil Hogar"/"TEXTIL_HOGAR") — 21 SKUs.
- 22 SKUs sin `costo_unitario`; 8 liquidaciones con fechas no parseables y 3 con `descuento_pct` fuera de rango.
- **Bug de fechas corregido:** `fecha_baja_catalogo` se comparaba contra el día 1 del mes de corte en vez del fin de mes, lo que hacía que ninguna baja del propio mes contara como discontinuada.
- **Particularidad del dataset:** toda posición con stock vendió al menos 1 unidad en los últimos 12 meses. No existe el caso "nunca vende", lo que limita el poder de la condición 1 al extrapolar a datos reales.

## Qué conviene presentar a Casa Óga

Ordenado por lo que se sostiene mejor con los datos:

1. **La foto de hoy:** $83,9 M inmovilizados (2,38% del stock), $4,2 M/mes de costo, y de qué están hechos (tabla de composición).
2. **El hallazgo central — la brecha entre percepción y datos.** La dirección percibe deterioro; los cuatro indicadores dicen estabilidad o mejora. Ambas no pueden ser ciertas, y hoy la empresa **no tiene forma de saber cuál es**. Está confirmado por su propio documento (seguimiento reactivo, conteo anual). Es más fuerte y más respetuoso que "ustedes están mal".
3. **La acción inmediata:** 13 SKUs discontinuados concentran $39,6 M en 139 posiciones — 47% del capital inmovilizado, sin necesidad de modelo. Es el quick win que da credibilidad al resto.
4. **El semáforo propuesto:** rojo/amarillo/verde calibrado contra su capacidad operativa real, que hace visibles 603 posiciones hoy invisibles.
5. **El sistema:** no como freno de un deterioro, sino como el instrumento de medición que falta — alertas mensuales por combinación SKU–tienda.

**Qué NO presentar:** que el problema viene empeorando (no se sostiene); el ranking de tiendas como desempeño (es ruido); el argumento de liquidar antes con menos descuento (no está en los datos); el costo sobre precio de lista sin aclarar la base; y números del semáforo mezclados con los de dead stock sin aclarar que usan bases distintas.

## Relevancia para el proyecto
- **Mix Productos / dead stock**: los datos alcanzan para el modelo a nivel SKU–tienda. Siguientes pasos: validar el semáforo con el negocio, formalizar las alertas mensuales, y conseguir el historial de transferencias y el `Proveedores.csv` para poder recomendar acciones y no solo detectar.
- **Clientes y Fidelización / churn**: falta el dataset de clientes a nivel individual.

## Archivos y scripts del proyecto

| Archivo | Qué es |
|---|---|
| `calculo_dead_stock.py` | Cálculo de dead stock: limpieza (`load_clean_data`), las 3 condiciones, valuación. Es la base de todo lo demás. |
| `verificacion_hallazgos.py` | Los chequeos de "Verificación del diagnóstico" y la calibración del semáforo: cobertura, dispersión, costo de reacción, composición, significancia por tienda, umbrales. |
| `prep_dashboard_data.py` | Arma el JSON que consume el panel. |
| `build_standalone.py` | Convierte el HTML publicado (fragmento sin `<html>`/`<body>`, formato que exige la plataforma de artifacts) en un archivo descargable que abre solo. |
| `dead_stock_evolucion_mensual.csv` | Serie mensual, 36 cortes. |
| `costo_almacenaje_evolucion.py` / `.csv` | Costo de almacenaje del stock parado 3+ meses. |
| `dead-stock-dashboard.html` | El panel completo, versión descargable (con esqueleto HTML, se abre con doble clic). |

**Para reproducir todo:** dejar los CSV originales en el mismo directorio y correr `calculo_dead_stock.py` → `costo_almacenaje_evolucion.py` → `prep_dashboard_data.py` → `build_standalone.py`.
