# Speech · Presentación final (Grupo 1)

> Guion tomado de las notas del orador de `Casa-Oga-Presentacion-Final.pptx` (17 diapositivas, ~17 minutos). Todas las cifras salen de `Entregable 4/Modelo/resultados/modelo_final_v4_resultados.json` y del informe final.

| Orden | Quién | Diapositivas |
|---|---|---|
| 1 | Santiago · Comunicación | 1-3 |
| 2 | Gianfranco · Coordinación | 4 |
| 3 | Matías · Datos (calidad) | 5-6 |
| 4 | Simón · Modelado | 7-10 |
| 5 | Gerónimo · Visualización | 11-12 |
| 6 | Gianfranco · Coordinación | 13-16 |
| 7 | Santiago | 17 |

## 1 · Detección anticipada de inventario inmovilizado

SANTIAGO. Buenas, somos el Grupo 1. Esta es la presentación final del proyecto de Casa Óga: integra los tres entregables y todas las correcciones que nos hicieron la cátedra y Casa Óga. En una frase: queremos que Casa Óga intervenga el stock que se va a inmovilizar antes de que pase, no en el conteo anual. Cada uno presenta la parte de la que es responsable: Matías los datos, Simón el modelo, Gerónimo la solución, Gianfranco la economía, los riesgos y el plan, y yo abro y cierro.

## 2 · En 2026 el stock que no rota se cuadruplicó

SANTIAGO. Primero el problema, de afuera hacia adentro. En 2026 la venta cae 13,4% y el stock que no rota se dispara: las posiciones con más de 12 meses de cobertura pasan de 200 en diciembre a 866 en agosto, con 178,6 millones de pesos parados a costo. Una corrección importante respecto del Entregable 1: entre 2023 y 2025 el problema era estable en proporción; crecía el monto porque crecía el negocio. No es alarmismo: lo nuevo es 2026, y parte del salto puede venir del nuevo reporte de datos de ese año. Hoy esto se ve en el conteo anual: tarde.

## 3 · Recomendamos un piloto supervisado de tres cierres

SANTIAGO. Les adelantamos la conclusión y después el equipo la justifica. Técnicamente es factible con score 2,25: los datos alcanzan, lo que falta es alguien en Casa Óga que sostenga el modelo. Legalmente es viable con condiciones, 2,2. Económicamente, con los números corregidos, en un año como 2025 el proyecto recupera la inversión en unos 24 meses; pero es sensible al costo real de desarrollo. Y el modelo le gana a la regla simple en los dos años, con una ventaja chica en 2026. Por eso recomendamos un piloto supervisado de tres cierres. Le paso a Gianfranco, que cuenta qué corregimos.

## 4 · Qué cambió respecto de las entregas anteriores

GIANFRANCO. Antes de los resultados, qué corregimos. Del Entregable 1: había dos juegos de cifras que no cerraban; ahora hay un solo indicador reproducible y un solo dataset en todo el informe. Agregamos el backlog que el título prometía y separamos la influencia técnica de la de decisión en el mapa de stakeholders, sumando Sistemas y los proveedores. Del Entregable 3: el modelo se elige en una validación interna para que la de 2025 siga siendo independiente; el cupo de alertas lo fija el valor de cada alerta y no la capacidad; y la economía se presenta como dos ROI separados. Todo está detallado en la sección 12 del informe. Le paso a Matías.

## 5 · Los datos alcanzan, con reglas acordadas con Casa Óga

MATÍAS. Los datos alcanzan: 201 mil filas a nivel producto–tienda–mes, 60 variables calculadas al cierre de cada mes, y un 3,22% de casos positivos. Encontramos 13 problemas de calidad y cada uno tiene tratamiento en el proyecto y una acción para corregirlo en origen. Aplicamos las reglas que pidió Casa Óga: ante duplicados nos quedamos con el registro de mayor venta y las devoluciones al proveedor no se restan de la venta. Como 2026 viene de otro reporte, siempre mostramos 2025 y 2026 por separado. Queda un pendiente que no depende de nosotros: incorporar las correcciones de la Ronda 3; es condición previa al piloto, con fecha y responsable.

## 6 · Técnicamente factible, con una condición

MATÍAS. Evaluamos cuatro condiciones técnicas de 1 a 3. Datos suficientes tiene 3. Calidad, infraestructura y capacidad humana tienen 2: hay problemas, pero son superables. Una corrección: la PC de oficina existe y es el entorno del piloto, no compramos equipo. La condición que más pesa es la humana: si antes del piloto no se nombra un responsable del modelo, el score baja a 2,0. Le paso a Simón con el modelo.

## 7 · Elegimos el modelo más simple que rinde igual

SIMÓN. Una de las correcciones de la cátedra fue que habíamos elegido el ensamble mirando la validación 2025, con lo que esa validación dejaba de ser independiente. Ahora elegimos en una validación interna de 2024, con una regla fijada antes de mirar: el ensamble entra sólo si le gana al gradient boosting en todos los cupos. No le gana, así que nos quedamos con un solo modelo de gradient boosting: sobreajusta menos y es más fácil de explicar y de mantener. La logística queda cerca y sigue siendo la alternativa si hiciera falta algo más simple.

## 8 · El cupo lo fija el valor de cada alerta, no la capacidad

SIMÓN. Antes llenábamos la capacidad: 600 alertas por mes. La cátedra nos marcó que la capacidad es un techo, no una meta, y que las últimas alertas costaban más de lo que recuperaban. Con el valor por posición reproducible, una alerta paga si acierta más del 11,8%. Entonces armamos la lista así: entra completa la regla de cobertura y el modelo agrega tramos de 50 mientras el tramo pague. En 2025 los tres primeros tramos pagan y el cuarto no: el modelo suma 150 alertas por mes. El gráfico muestra que el valor deja de crecer mucho antes de las 600.

## 9 · Le gana a la regla en los dos años; en 2026, por poco

SIMÓN. Con el mismo número de alertas, el flujo regla más modelo detecta 404 casos en 2025 contra 354 de ordenar por cobertura: 14% más. En 2026, 1.475 contra 1.452: apenas 2% más. Le gana en los dos años, así que es robusto, pero la ventaja es chica justo en el año fácil. ¿Por qué 2026 es más fácil? De las posiciones sin venta en un mes, las que siguen sin vender tres meses pasan de 9,8% en 2025 a 82,4% en 2026: con esa persistencia la cobertura sola casi alcanza. Por eso informamos el desempeño como un rango.

## 10 · El modelo mira lo que miraría un comprador, antes

SIMÓN. Para explicar el modelo mezclamos al azar cada variable y medimos cuántos casos se pierden: así vemos qué usa el sistema completo y en la métrica del negocio. Lo que más pesa es la venta de los últimos 6 meses, la cobertura actual y la variabilidad de la venta: lo mismo que miraría un comprador, pero combinado antes de que la cobertura cruce los 12 meses. También corregimos la lectura por segmento: con 18 casos, Patagonia tiene un intervalo de 20% a 61%, así que no podemos decir que el modelo funcione peor ahí. Cocina y mesa sí, y tiene su propio umbral de monitoreo. Le paso a Gerónimo con la solución.

## 11 · Una lista mensual por tienda, y una persona decide

GERÓNIMO. Así llega el modelo a una decisión. Cada cierre se reciben cinco archivos con formato fijo; se limpian con las reglas del Entregable 2; se arma la lista: primero todo lo que ya tiene más de 12 meses de cobertura, que se explica solo, y después las 150 posiciones que el modelo anticipa. Cada tienda ve sólo sus alertas, sin costos y con el motivo. La tienda propone liquidar, transferir, frenar compras o desestimar, y Comercial y Compras autorizan en una sesión de 30 minutos. Tres meses después medimos si acertamos y ajustamos el cupo.

## 12 · Cada usuario ve lo que necesita para decidir

GERÓNIMO. Cada usuario recibe sólo lo que necesita. La tienda ve su lista corta, alrededor de 11 posiciones por mes, sin costos. Comercial autoriza, Compras ve el riesgo por SKU y proveedor en una vista restringida, Operaciones coordina las transferencias y Finanzas sigue el valor recuperado. Una aclaración que nos pidió la cátedra: el tablero es un corte mensual, con carga manual, no un tablero en vivo. Le paso a Gianfranco con la economía.

## 13 · La lista ya paga sola; el modelo suma por encima

GIANFRANCO. La economía cambió con las correcciones. La cátedra nos pidió usar el valor por posición reproducible del Entregable 2, 208 mil pesos, en lugar del del Entregable 1, y separar dos cosas: cuánto vale automatizar la lista con la regla, sin modelo, y cuánto agrega el modelo. En un año como 2025, automatizar la lista da un ROI a tres años de 21,7%; el modelo agrega unos USD 2.029 por año, con un ROI propio de 6,8%; y el total recupera la inversión en 24 meses. En un año como 2026 los números son mucho mejores, pero lo tomamos como techo, no como expectativa.

## 14 · Dos supuestos mueven el resultado

GIANFRANCO. Fuimos honestos con la sensibilidad. Si el desarrollo cuesta lo que costaría de verdad, tres o cuatro meses de un científico de datos, el ROI a tres años pasa a -3,3% y -11,6%. Y si usáramos el valor por posición del Entregable 1, no se recupera. La cátedra lo dijo bien: con 80 a 134 dólares de capital por posición, cada acierto vale poco; el proyecto rinde por volumen y por las horas que ahorra. Sacamos además el criterio de recupero de 12 meses, que no venía de Casa Óga: usamos ROI a tres años mayor o igual a cero.

## 15 · Legal viable con condiciones; los riesgos, medidos

GIANFRANCO. Legalmente es viable con condiciones, 2,2: no hay datos personales, y el riesgo real es que costos y condiciones de proveedores lleguen a quien no corresponde; se resuelve con accesos por rol y una adenda de confidencialidad. Aclaramos que el 2 en explicabilidad aplica al modelo, no a la regla. Los riesgos ahora están construidos sobre el escenario de referencia, no el optimista: el primero es que el beneficio no llegue a los 9.150 dólares por año que hacen viable el proyecto. Cada riesgo tiene una señal medible y una respuesta.

## 16 · Plan: un mes de preparación y un piloto de seis

GIANFRANCO. El plan tiene dos partes. Cuatro semanas de preparación: aprobar el target, incorporar la Ronda 3 y reevaluar, nombrar al mantenedor, firmar la adenda, configurar los accesos y estandarizar la exportación. Después, un piloto de tres cierres; como el resultado se conoce tres meses después, las cohortes maduran entre los meses 4 y 6, y en el mes 6 Finanzas decide si continúa. El go-live tiene cinco criterios de sí o no. Una corrección de la cátedra: el desempeño ya no se da por cumplido con el test de 2026; se mide con las cohortes del piloto. Le devuelvo la palabra a Santiago.

## 17 · Viable con condiciones como piloto supervisado

SANTIAGO. Cerramos. Nuestra recomendación es avanzar con un piloto supervisado de tres cierres, sin compras nuevas. Antes de empezar hay tres acciones: nombrar al mantenedor y firmar la adenda con accesos por rol, estandarizar la exportación mensual y reconstruir el dataset con la Ronda 3. El riesgo residual es que la ventaja del modelo sea chica en la práctica, como en 2026; si pasa, el proyecto igual vale por la lista automatizada y las horas que ahorra, y el modelo se retira sin costo adicional. Gracias; quedamos para preguntas.
