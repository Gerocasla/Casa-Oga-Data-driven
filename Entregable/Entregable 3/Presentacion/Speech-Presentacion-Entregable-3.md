# Speech · Presentación Entregable 3 (Grupo 1)

> Guion para la versión de **Google Slides** (18 diapositivas: la del repo, commit `3d43da5`, sin la slide «Un responsable por resultado»). Amplía las notas del orador que trae cada slide. Está pensado para decirse, no para leerse: cada uno puede reformularlo con sus palabras mientras respete los números.
> Todos los números salen del compilado (`Compilado/Entregable_3_Grupo_1_Casa_Oga_COMPILADO.docx`). Entre paréntesis va la sección del documento, por si preguntan de dónde sale algo.

**Tiempo estimado:** ~15 minutos (unos 45-60 segundos por slide).

| Orden | Quién | Slides | Tiempo aprox. |
|---|---|---|---|
| 1 | Santiago · Comunicación | 1–3 | 2,5 min |
| 2 | Matías · Datos | 4–5 | 2 min |
| 3 | Simón · Modelado | 6–9 | 3,5 min |
| 4 | Gerónimo · Visualización | 10–13 | 3 min |
| 5 | Gianfranco · Coordinación | 14–17 | 3,5 min |
| 6 | Santiago | 18 | 1 min |

---

## 1 · Portada — Santiago

Buenas, somos el Grupo 1 y venimos a presentar el Entregable 3 del proyecto de Casa Óga.

El proyecto se resume en una frase: queremos que Casa Óga **detecte el stock que se va a inmovilizar tres meses antes de que pase**, y no en el conteo anual, cuando ya es tarde.

En este entregable respondimos cuatro preguntas: si el proyecto es técnicamente factible, si conviene económicamente, si se puede hacer dentro del marco legal y cómo llega el modelo a una decisión concreta del negocio. En paralelo hicimos las cuatro etapas del modelado.

Somos cinco y, como pide la Clase 13, cada resultado tiene un único dueño y cada uno cuenta su parte: Matías, el dataset y el pipeline; Simón, el modelo y su ficha; Gerónimo, el diseño de la solución y el tablero; Gianfranco coordina y es dueño del plan, y además cuenta la economía y lo legal; y yo llevo la narrativa, así que abro y cierro.

---

## 2 · Casa Óga detecta tarde el stock que no rota — Santiago

Primero, el problema. Casa Óga no tiene un problema de stock lento; todo retail lo tiene. **El problema es que lo detecta tarde.**

A agosto de 2026 había **882 posiciones**, o sea combinaciones de producto y tienda, con más de 12 meses de cobertura: con el ritmo de venta actual, ese stock tarda más de un año en venderse. Son **ARS 184,1 millones a costo**. Al costo de mantener stock que nos dio el negocio, 5% por mes, eso es del orden de 9 millones de pesos mensuales.

Hoy eso aparece en el conteo anual o cuando ya acumuló meses de capital, góndola y depósito parados, y la liquidación llega tarde y con más descuento. Además, armar ese análisis a mano en Excel les lleva unas **480 horas por año**.

Lo que proponemos es una **lista mensual de hasta 600 posiciones** a revisar, de 15 a 25 por tienda, tres meses antes de que crucen los 12 meses de cobertura. Y algo importante desde ya: **el modelo prioriza, las personas deciden**.

---

## 3 · Recomendamos un piloto supervisado — Santiago

Les adelantamos la conclusión, y después el equipo la justifica parte por parte.

- **Técnicamente**, el proyecto es factible con un score de **2,25 sobre 3**: factibilidad media. Lo que falta no son datos, es alguien en Casa Óga que sostenga el modelo.
- **Legalmente** es viable con condiciones, **2,2**: accesos por rol y un acuerdo de confidencialidad con la consultora.
- **El modelo funciona**: detecta entre el **71% y el 77%** de los casos con el cupo de 600 alertas, y le gana a la regla que podría aplicar el negocio hoy.
- **Lo que no cierra es la economía**: el recupero de la inversión está entre **35 y 59 meses**, y el ROI a tres años entre −13,7% y +0,9%.

Por eso nuestra recomendación no es "inviertan": es un **piloto supervisado de tres cierres mensuales**, sobre la infraestructura que ya tienen y sin inversión de expansión. El modelo pasa a ser el motor principal sólo si en el piloto le gana a la regla con el mismo cupo de alertas.

Ahora cada uno justifica su parte, en orden: datos, modelo, solución, y viabilidad y plan. Le paso la palabra a Matías, que arranca por la factibilidad técnica.

---

## 4 · Técnicamente factible, con una condición — Matías

Gracias. Evaluamos cuatro condiciones técnicas, cada una con un puntaje de 1 a 3 (sección 1.2).

**Datos suficientes: 3.** Tenemos 51 meses de historia y 6.853 casos positivos. Las dos fuentes con las que se calcula el target, ventas y stock, cruzan al 100% por tienda, producto y mes. Los datos no son el cuello de botella.

**Calidad utilizable: 2.** No hay nulos en las variables del target, pero hay un 1,59% de filas duplicadas por la migración del reporting de 2024, y tres problemas que no se arreglan sin cambiar sistemas: el catálogo pisa precio y costo sin guardar historia, el historial de precios es una reconstrucción y el stock en tránsito no tiene definición. Esas variables las sacamos del modelo en lugar de inventar datos.

**Infraestructura: 2.** Python, GitHub y un tablero HTML alcanzan para el piloto, con costo de licencias cero. Pero hoy la integración entre sistemas es manual, con exportaciones a Excel.

**Capacidad humana: 2**, y es la que más pesa. Nosotros podemos construir el modelo, pero Casa Óga no tiene área de datos y su responsable de IT renunció sin dejar documentación. **Nadie está nombrado para mantener el modelo.** Sin esa persona, un cambio como el de 2026, cuando la tasa de casos salta de 2,5% a 9%, pasaría sin que nadie lo detecte.

El promedio da **2,25: factibilidad media**. Se puede avanzar si antes del go-live se nombra un responsable y se estandariza la exportación mensual.

---

## 5 · Un experimento que respeta el tiempo — Matías

Ahora, cómo planteamos el experimento (sección 2).

La pregunta es: **¿qué posiciones van a superar 12 meses de cobertura dentro de tres meses?** Cada fila es una posición en un mes: 201.306 filas, 60 variables, y un 3,4% de casos positivos.

Como los datos tienen orden temporal, **entrenamos con el pasado y evaluamos con el futuro**, nunca con una partición aleatoria, porque eso infla los resultados. Entrenamos de marzo de 2022 a diciembre de 2024, validamos de abril a septiembre de 2025, y dejamos guardado como test enero a mayo de 2026. Entre cada bloque dejamos **tres meses de embargo**, igual al horizonte, para que ninguna etiqueta caiga en el bloque siguiente. **El test no se tocó hasta la evaluación final.**

Y revisamos variable por variable si estaría disponible al cierre del mes en que predecimos. Excluimos ventas y stock futuros, el precio y costo del catálogo, porque son los de hoy y no los de ese momento, y el presupuesto futuro, que se actualiza con la venta real. Liquidaciones, transferencias y órdenes de compra se recalcularon para usar sólo lo conocido hasta ese mes.

Un dato para retener: en 2026 la tasa de positivos sube a **9%**, cuatro veces más que en validación. Simón va a mostrar qué implica eso. Le paso.

---

## 6 · La regla actual detecta 3 de cada 10 casos — Simón

Gracias. Todo modelo tiene que ganarle a algo que el negocio ya pueda hacer sin modelo. Ese es el baseline.

La regla más simple es: **alertar toda posición cuya cobertura actual ya supera 12 meses.** Se calcula hoy en Excel con dos columnas. En validación 2025 genera unas **175 alertas por mes** y detecta **258 de 854 casos: un 30%**, con 24,6% de precisión. Lejos de la meta del negocio, que es detectar al menos el 75%.

Para comparar definimos una métrica principal: **Recall@600**. La cadena puede trabajar unas 600 intervenciones por mes, de 15 a 25 por tienda. Entonces medimos cuántos casos reales caen dentro de las 600 posiciones de mayor riesgo de cada mes.

¿Por qué con cupo fijo? Porque si no, gana el que más alerta: más alertas siempre detectan más, pero le cuestan más trabajo a la tienda. **Comparamos siempre a igual cupo.** Y elegimos el recall porque el error caro es el falso negativo: una posición que no alertamos sigue acumulando costo mes a mes.

---

## 7 · El ensamble supera a la regla a igual cupo — Simón

Primero le dimos a la regla la misma oportunidad que al modelo: ordenamos las posiciones por cobertura y tomamos las 600 primeras. Así detecta el **52,5%**.

Después probamos **siete familias de modelos de árboles**, siempre con validación temporal y sin mirar el test. Individualmente todos rondan el **68%**: ya le ganan a la regla por unos 16 puntos.

El modelo final es un **ensamble de tres**: HistGradientBoosting, ExtraTrees y LightGBM, promediando el ranking mensual de cada uno. Llega a **71%: 606 de 854 casos, 158 más que la regla con el mismo cupo**.

Pero lo decimos claro: en entrenamiento detecta el **99,7%** y en validación el 71%. **Hay sobreajuste**, y el ajuste lo aumentó en vez de reducirlo. Por eso el modelo no se usa solo ni sin revisión humana, y por eso el test final era tan importante.

---

## 8 · En el test 2026 el modelo generaliza — Simón

Evaluamos **una sola vez** sobre el test de 2026, sin reajustar nada después de ver el resultado.

El ensamble detecta el **76,9%** de los casos con una **precisión de 65%**. O sea, generaliza: no cae respecto de validación, sube.

Pero hay que leerlo con cuidado. Como pidió la cátedra, mostramos regla y modelo por separado en cada período. El modelo le gana a la regla en los dos años, pero **la ventaja se achica**: con el mismo cupo que la regla, el modelo acierta un 26% más en 2025 y sólo un 3% más en 2026.

¿Por qué? Porque **2026 fue un año más fácil**: hay cuatro veces más positivos, 9% contra 2,2%, los datos vienen de un nuevo reporte consolidado, y la cobertura sola ya separa muy bien los casos, con un AUC de 0,94. La precisión salta de 17% a 65% principalmente por eso.

Por eso no prometemos un número: informamos un **rango esperado, recall entre 71% y 77% y precisión entre 17% y 65%**.

---

## 9 · Cada alerta se puede explicar — Simón

El negocio pidió explicabilidad, así que verificamos qué variables pesan más y si tienen sentido.

Las principales son la **variabilidad de la venta** de los últimos 12 meses, las **unidades vendidas en los últimos 6 meses**, la **subcategoría**, la **cobertura actual** y la **venta promedio**. Todas son de demanda y stock y se conocen al cierre del mes. Ninguna es sospechosa de filtrar el futuro. Y aclaramos que importancia no implica causalidad.

Un caso real de validación: el **SKU00206 en la tienda 12**, de Cocina y mesa, en abril de 2025. Tenía 4 unidades en stock, 0 vendidas en seis meses y 5 meses sin ventas. Los tres modelos lo pusieron arriba del ranking, entró en las 600 alertas, y efectivamente a los tres meses superó los 12 meses de cobertura.

Y la ficha del modelo deja claro **para qué no sirve**: no ordena liquidar, no evalúa encargados ni tiendas y no es una probabilidad. Además rinde menos en Cocina y mesa, 61,8%, nueve puntos debajo del promedio, y eso queda monitoreado.

Con esto le paso a Gerónimo, que cuenta cómo el modelo se convierte en una solución.

---

## 10 · Regla + modelo, con decisión humana — Gerónimo

Gracias. El modelo no es la solución: es una pieza. Antes de elegir, lo comparamos con alternativas más simples (sección 9.1).

- **No hacer nada** no es opción: la detección sigue siendo anual y el costo sigue creciendo.
- **Un tablero descriptivo** sirve para mostrar, pero no anticipa: ve la posición cuando ya pasó los 12 meses. Lo usamos como canal.
- **La regla de negocio** es estable, explicable y la más precisa, pero no ve lo que todavía no llegó a 12 meses.
- **El modelo predictivo** justamente anticipa eso, pero tiene sobreajuste y una ventaja chica en 2026.
- **Automatizar la decisión** no: liquidar necesita contexto comercial. Automatizamos el armado de la lista, nunca la decisión.

Entonces combinamos: el **bloque A es la regla**, cobertura mayor a 12 meses, ordenada por capital inmovilizado. El **bloque B es el ensamble**, que completa el cupo hasta 600 con lo que la regla todavía no ve. La regla da la base estable y el modelo agrega la anticipación.

---

## 11 · Un ciclo mensual de cinco días — Gerónimo

Así funciona cada mes, de punta a punta (sección 9.2):

1. **Días 1 a 3, ingesta:** llegan cinco archivos, ventas, stock, órdenes de compra, transferencias y liquidaciones, con formato y clave fijos. Se controla que estén los cinco y que no haya claves desconocidas.
2. **Días 3 y 4, preparación:** se aplican las reglas de limpieza del Entregable 2, se calculan las 60 variables y se guarda una bitácora con el hash del archivo original, para trazabilidad.
3. **Día 4, scoring:** primero el bloque A con la regla, después el ensamble completa hasta 600.
4. **Día 5, entrega:** cada rol ve su tablero y su planilla en SharePoint.
5. **Decisión:** la tienda propone la acción y Comercial y Compras autorizan; la acción se ejecuta en 2 a 4 semanas.
6. **Aprendizaje:** a los tres meses sabemos qué pasó de verdad. Esas etiquetas vuelven para medir modelo contra regla y para reentrenar cada trimestre.

En el proyecto, Matías es responsable de ingesta y preparación, Simón del scoring y yo del tablero. En Casa Óga hace falta un mantenedor del pipeline y Lucía O. como dueña funcional.

---

## 12 · Cada rol ve solo lo que necesita — Gerónimo

La salida llega a cada persona con lo que necesita para decidir, y nada más (sección 9.3).

A la izquierda está una **maqueta ilustrativa** de la vista de una tienda: su lista de 15 a 25 posiciones con cobertura, ventas de los últimos seis meses, en qué bloque entró y un **motivo legible**. No ve costos ni datos de otras tiendas. Cada fila se resuelve de cuatro formas: liquidar, transferir, frenar compras o desestimar con motivo.

Los demás roles:

- **María G., Comercial:** resumen por categoría; autoriza liquidaciones.
- **Diego P., Compras:** los SKUs en riesgo en varias tiendas, con órdenes de compra pendientes y costo; puede frenar compras.
- **Carlos F., Finanzas:** valor recuperado y horas ahorradas; decide la continuidad del proyecto.
- **Lucía O., Operaciones:** la lista consolidada; coordina y decide transferencias.

Esta separación no es sólo de diseño: es la condición legal que después cuenta Gianfranco.

---

## 13 · Cómo sabemos si sigue funcionando — Gerónimo

Un modelo en producción se degrada si nadie lo mira. Definimos cinco cosas a monitorear, cada una con un umbral y una acción concreta (sección 10.2):

- **Calidad de los datos**, en cada cierre: si falta un archivo, aparece una clave desconocida o una alerta con stock negativo, esas filas no se publican hasta corregirse.
- **Desempeño del modelo**, a los tres meses: si el Recall@600 cae debajo de 60% o el modelo no le gana a la regla dos cierres seguidos, **se publica sólo el bloque A y se reentrena**.
- **Cambio en los datos:** si la mediana de cobertura se mueve más de 20% o la tasa de positivos sale del rango 2,2% a 9%, las alertas se marcan como provisionales y se adelanta el reentrenamiento.
- **Adopción:** si menos del 60% de las alertas tiene una acción registrada, se revisan los motivos con las tiendas.
- **Impacto de negocio**, trimestral: si el beneficio anualizado no llega a USD 9.150, que es el equilibrio a tres años, se congela la expansión.

Ese último umbral es justo el tema de Gianfranco. Le paso.

---

## 14 · La economía todavía no cierra — Gianfranco

Gracias. La inversión no es el problema (sección 3).

La inversión inicial es de **USD 9.570**: 3.000 de desarrollo del modelo, 3.000 de conexiones con el POS y el inventario según cotización de los proveedores, 1.800 de integración y limpieza de datos, 900 de capacitación y un 10% de contingencia. El mantenimiento es de **USD 5.960 por año**. Todo entra holgado en el presupuesto de USD 30.000.

El problema es el retorno. El beneficio tiene dos partes: lo que el modelo detecta de más frente a la regla **con el mismo cupo de alertas**, y las horas de armado manual que se ahorran al automatizar la lista. Con los aciertos de la Etapa 4, el beneficio esperado queda entre **USD 7.899 y 9.230 por año**, y el **ROI a tres años entre −13,7% y +0,9%**. El recupero queda entre **35 y 59 meses**, contra un máximo de 12 que proponemos como criterio para aprobar una expansión.

Y hay un matiz más: **entre el 44% y el 51% de ese beneficio es tiempo liberado**, que sólo es ahorro si evita un costo real, por ejemplo una contratación. Para llegar al equilibrio hacen falta USD 9.150 por año.

Por eso no recomendamos expandir: recomendamos un piloto que mida el valor recuperado de verdad.

---

## 15 · Legal viable; tres riesgos a vigilar — Gianfranco

**Legalmente el proyecto es viable con condiciones: 2,2** (sección 5).

- **Datos personales: 3.** El modelo trabaja con producto, tienda y mes; no usa datos de clientes ni de empleados, así que hoy la Ley 25.326 no se activa. Dejamos como política no incorporar nunca datos personales.
- **Seguridad y accesos: 2.** El riesgo real es que circulen costos y condiciones de proveedores, que son información confidencial. Se resuelve con la matriz de accesos por rol que mostró Gerónimo, con doble autenticación.
- **Trazabilidad fiscal: 2.** Conservamos los CSV originales sin tocar, con hash y bitácora de cada transformación, para que cualquier cifra se pueda rastrear.
- **Contratos externos: 2.** Falta firmar una adenda de confidencialidad con la consultora, que incluya la entrega del código.
- **Explicabilidad: 2.** El ranking es trazable, pero no explica causas. Por eso el modelo nunca liquida solo.

Los **tres riesgos críticos** (sección 6.3), cada uno con una señal medible y una respuesta: que **los ahorros no se materialicen**, y entonces Carlos F. congela la expansión; que **lleguen datos de stock o maestros inconsistentes**, y entonces esas filas no se publican; y que **el ensamble se degrade** por sobreajuste o cambio en los datos, y entonces se vuelve a la regla en ese segmento y se reentrena.

---

## 16 · Cinco criterios para salir a producción — Gianfranco

Para autorizar el go-live definimos **cinco criterios verificables**, cada uno con quién lo aprueba (sección 10.3):

1. Una exportación completa y válida: cinco archivos, cero claves desconocidas y cero alertas con stock negativo.
2. Un modelo con Recall@600 de al menos 60% en test temporal y que no pierda contra la regla con el mismo cupo.
3. Un responsable del modelo nombrado por escrito, con 5 a 6 horas por semana.
4. La adenda de confidencialidad firmada, accesos por rol con doble autenticación y la PC de procesamiento cifrada.
5. El protocolo de decisión humana aprobado y los usuarios del piloto capacitados.

**Hoy se cumple uno: el del modelo.** Tiene 76,9% en test contra un piso de 60%, y con el mismo cupo que la regla acierta 1.067 contra 1.034.

Los otros cuatro no dependen del equipo sino de Casa Óga. Por eso son las **precondiciones del plan**.

---

## 17 · Plan: de precondiciones a la decisión — Gianfranco

El plan tiene seis fases, cada una con un responsable y un criterio de cierre. Las semanas son relativas al inicio.

- **Precondiciones, primeras dos semanas:** con la Dirección, nombrar al responsable y firmar la adenda. **Sin eso no se arranca.** Es el hito 1.
- En paralelo parcial, **pipeline y datos** con Matías, que cierra con una corrida válida de cinco archivos; **modelo y scoring** con Simón, con los bloques A y B reproducibles y versionados; y **tablero, accesos y taller** con Gerónimo y Santiago, que cierra con una prueba de acceso de una tienda y el acta del taller.
- **Go-live alrededor de la semana 6**, hito 2.
- **Piloto de tres cierres mensuales**, coordinado conmigo y con Lucía O., con la meta de que al menos el 60% de las alertas tenga una acción registrada. Termina en el hito 3, el tercer cierre.
- **Evaluación y decisión** con Simón y Carlos F.: como la verdad de cada alerta se conoce tres meses después, la decisión llega **cerca de la semana 28**. Ahí se decide, con datos propios, si el ensamble pasa a ser el motor principal y si se expande.

Le devuelvo la palabra a Santiago para el cierre.

---

## 18 · Veredicto integrado — Santiago

Cerramos. Nuestra recomendación es **avanzar con un piloto supervisado de tres cierres, sin inversión de expansión**.

El proyecto es técnicamente factible, legalmente viable con condiciones y el modelo generaliza. La pregunta que queda abierta no es si el modelo funciona, sino **si paga su costo**, y eso sólo lo puede responder un piloto con datos propios de Casa Óga.

Antes de implementar hacen falta tres cosas, y las tres están en manos de Casa Óga:

1. Nombrar al responsable del modelo, con 5 a 6 horas por semana.
2. Estandarizar la exportación mensual con control de recepción.
3. Firmar la adenda de confidencialidad y activar los accesos por rol.

El riesgo que la dirección tiene que conocer es que **el beneficio no se materialice**: casi la mitad del valor esperado es tiempo liberado, y el valor de cada alerta depende de supuestos de recupero que todavía no observamos. Por eso lo vamos a medir desde el primer cierre.

El próximo paso, en el Entregable 4, es la prueba de concepto del piloto: la lista mensual y el tablero por rol. Muchas gracias. ¿Preguntas?

---

## Preguntas probables y respuesta corta

| Pregunta | Quién responde | Respuesta |
|---|---|---|
| Si la regla en 2026 casi iguala al modelo, ¿para qué el modelo? | Simón | Con el mismo cupo le gana en los dos años (+66 aciertos en 2025, +33 en 2026). 2026 fue más fácil (9% de positivos, cobertura sola con AUC 0,94). Por eso la regla es la base (bloque A) y el modelo complementa; el piloto decide si pasa a motor principal. |
| ¿Por qué 600 alertas por mes? | Simón / Gerónimo | Son 28 tiendas × 15 a 25 intervenciones = 420 a 700. Tomamos 600, unas 21 por tienda. Ese número de capacidad nunca se midió: hay que validarlo con Lucía O. en el piloto. |
| ¿Por qué 12 meses de cobertura? | Matías | Salió primero de la capacidad operativa: con cortes más bajos la lista excede lo que la cadena puede trabajar. Coincide con rotación anual < 1 (análisis FSN, "non-moving"), pero eso fue un respaldo posterior. No existe un estándar académico para hogar y decoración. |
| ¿El sobreajuste no invalida el modelo? | Simón | Es un riesgo declarado (99,7% contra 71%), pero el test temporal, que no se usó para elegir nada, dio 76,9%: generaliza. Por eso va con revisión humana, monitoreo a t+3 y vuelta a la regla si el Recall@600 baja de 60%. |
| ¿Por qué el falso negativo vale USD 0 si es el error más caro? | Gianfranco | Su costo es el beneficio que no se captura, y eso ya está reflejado en que hay menos verdaderos positivos. Asignarle un costo propio lo contaría dos veces. Por eso los métodos se comparan con el mismo cupo. |
| Si el ROI es negativo, ¿por qué avanzar? | Gianfranco | No pedimos inversión de expansión: el piloto usa la infraestructura existente y sirve para medir el valor real. Si el beneficio no llega a USD 9.150 por año, se congela. |
| ¿Por qué el valor por caso usa 661 posiciones y ARS 83,9 M (E1) y no los 882 / 184,1 M? | Gianfranco | La cifra del E1 no es reproducible; usamos el valor por posición más bajo para no sobrestimar el beneficio. Antes del piloto se recalcula con la cifra reproducible del E2. |
| ¿Por qué 2026 tiene 9% de positivos? | Matías | No está explicado por el negocio. Coincide con más posiciones sin venta (de 365 a 929 entre dic-25 y ago-26) y la mitad de liquidaciones. Por eso la partición es temporal y se monitorea el cambio de distribución. |
| ¿Quién es el mantenedor? | Gianfranco | Propuesta: un analista del equipo de Sofía R., 5 a 6 horas por semana. No está confirmado por Casa Óga: es una precondición del go-live. |
