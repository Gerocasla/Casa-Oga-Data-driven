# Respuestas del negocio — Ronda 2 (calidad de datos)

> Respuestas de Casa Óga (vía la cátedra) al cuestionario `Entregable/Entregable 2/Preguntas-Calidad-de-Datos-Ronda-2.docx` (32 preguntas).
> Recibidas el 25-09-2026. Texto tal como llegó. Dónde se aplicó cada una: `Entregable/Entregable 2/PROBLEMAS-CALIDAD-DATOS.md` (H2, H4, H5, H8, H9, H11) y Parte B §1.2.

## Bloque 1 · Productos sin costo unitario (22 SKUs)

**P1.** El circuito hoy es en dos pasos separados y sin control cruzado: Compras y Categorías da de alta el producto con sus atributos comerciales, y por separado Finanzas carga el costo. No hay un paso que obligue a que ambas cargas estén completas antes de que el producto quede activo esto puede ser un issue para el modelo predictivo? qué sugerencias pueden realizar al respecto.

**P2.** La causa es la del circuito de Pregunta 1: el alta comercial no depende de que Finanzas haya terminado de cargar el costo. No tenemos ni vamos a poder confirmarles algo más puntual sobre estos 22 casos específicos, tratenlo en función de la explicación de negocio, para esta instancia pueden eliminarlos, pero pedimos nos sugieran pasos a seguir relacionado con este tema y de cara a una implementación definitiva del modelo resultante de este proyecto.

**P3 y P4.** El responsable de IT a cargo de esos sistemas renunció hace un mes y ahí nos dimos cuenta que no hay documentación disponible, por lo tanto no tenemos una definición formal de qué incluye el costo unitario del catálogo. Nuestro análisis llega a la misma conclusión que Uds, el margen que da usar el costo de la orden de compra en estos 22 productos es de 55% aprox y es notablemente más alto que el resto del catálogo, lo que indica que no son el mismo concepto.
Lo que sí pueden hacer es calcular ustedes mismos el factor de ajuste implícito a partir de esta misma brecha: comparando el costo de la orden de compra contra el precio de lista de estos 22 productos versus la relación equivalente costo de catálogo/precio de lista del resto, para estimar cuánto habría que sumarle al costo de la orden para que el margen de estos 22 productos quede en línea con el 45% promedio del resto. Ese ajuste no es un dato del negocio: es un supuesto calculado para este proyecto, que deberán dejar explícitamente declarado como tal en su informe.

**P5, P6 y P7.** No tenemos definido quién puede entregarles el costo definitivo de estos 22 productos ni en qué plazo, así que no lo esperaría para este entregable, les enviamos novedades en cuanto Finanzas lo confirme. Mientras tanto, usen el costo de la orden de compra ajustado con el factor que sugerimos calcular en P3-P4 (para nivelar el margen de estos 22 productos con el 45% promedio del resto del catálogo) para calcular tanto el capital inmovilizado como el margen. Al ser un supuesto, déjenlo declarado explícitamente en su informe junto con el criterio que usaron para calcularlo. Si prefieren no aplicar el ajuste y usar directamente el costo de la orden sin corregir, también pueden hacerlo, pero en ese caso aclaren que el capital inmovilizado les va a quedar subestimado y el margen sobreestimado para estos 22 productos.

## Bloque 2 · Costo unitario vacío en el historial de precios

**P8.** La fuente maestra es el catálogo de productos. El tramo vigente del historial está construido para coincidir exactamente con el catálogo; si alguna vez ven una diferencia, el catálogo es el que manda, sin necesidad de consultarnos ese caso puntual.

**P9.** No se genera del catálogo ni es una carga independiente: lo reconstruimos una única vez a partir de Compras y del sistema de Inventario para este proyecto. No es un dataset vivo que se siga alimentando en paralelo.

**P10.** Hoy el sistema pisa el valor vigente en lugar de guardar un registro histórico, no existe ese mecanismo. Los tramos que ven son una reconstrucción retroactiva nuestra, no reflejan un proceso real que sigan usando.

**P11.** Ya lo tenemos identificado y en revisión con Compras caso por caso, es un error del sistema. Para el proyecto, no intenten modelar costos simultáneos por proveedor: tomen el costo único que figura en catálogo/historial como el costo vigente del SKU, sin desagregar por proveedor.

**P12.** No hay un criterio de actualización documentado. Traten las variaciones de precio entre vigencias como repricing de mercado que no se puede descomponer con la información disponible, y avancen usando el precio_lista tal como está, no hace falta que busquen una fórmula subyacente porque no existe.

**P13.** No hay un índice de referencia único de la empresa. Usen el historial de precios que les dimos para construir su propio criterio de comparación entre años (por ejemplo, deflactando con el IPC de INDEC, o usando la evolución del propio precio de lista), y justificar.

## Bloque 3.1 · Stock disponible negativo (1.209 registros)

**P14.** Confirmado: es un problema de sincronización entre el POS y el sistema de inventario (una venta se descuenta antes de que el stock esté correctamente cargado). Tratenlo como error de dato, no como información real de inventario.

**P15.** No tenemos un proceso de ajuste formal para entregarles aparte.

**P16.** Les proponemos como default: lleven estos valores a cero (piso en 0) para cualquier cálculo de cobertura o dead stock, ya que confirmamos que no son información real. Si prefieren otro criterio (excluir esas combinaciones, imputar con meses adyacentes), pueden proponerlo y justificarlo, pero ya tienen una opción válida por default.

**P17.** No, hoy no existe ningún control automático que lo evite.

## Bloque 3.2 · Unidades y venta neta negativas (2.317 registros)

**P18.** La lectura más probable para "producto sin rotación / no vendido" es que corresponda a devoluciones de stock sin rotar a proveedores con cláusula contractual de devolución parcial (ya identificado en relevamientos anteriores). No tenemos una definición operativa formal de los otros cuatro motivos más allá de sus nombres, no hace falta que profundicen más, con esta lectura alcanza para su análisis.

**P19.** Confirmado: hoy los cinco motivos se registran todos como venta negativa, no como movimiento de inventario separado. Conceptualmente el caso de "sin rotación/no vendido" debería tratarse como un movimiento de inventario, pero el sistema no distingue. Considerenlo como una limitación conocida del dato.

**P20.** Confirmado: la devolución se registra directamente como fila negativa dentro de venta_neta; no hay un descuento aparte oculto. El dataset de Devoluciones que les dimos es la vía para identificarlas y tratarlas por separado si lo necesitan.

**P21.** No hay un protocolo único documentado. Usen como criterio de trabajo la lógica que ya les dimos: un producto dañado o con defecto de fabricación no vuelve a stock vendible; un cambio de talle/color o un error de picking sí podría reingresar. Es la mejor información disponible.

**P22.** Sí, depende del proveedor: algunos contratos permiten devolución parcial de stock sin rotar, pero no es generalizado ni está sistematizado. En la mayoría de los casos no hay devolución posible.

**P23.** Dado que son devoluciones reales, no las consideren como ritmo de venta bruta. Les proponemos como default: calculen el ritmo de venta neteando estas filas (ventas menos devoluciones del mismo SKU-tienda-mes). Si prefieren excluirlas en lugar de netearlas, es una alternativa válida, pero deberán justificar.

## Bloque 3.3 · Descuentos fuera del rango 0-100%

**P24 y P25.** No tenemos identificada ninguna acción comercial real detrás de estos valores. Considerarlos directamente como error de carga (dígito de más o signo invertido) sin necesidad de mayor confirmación de nuestra parte.

**P26.** No existe una política formal escrita. Usen los rangos empíricos del resto de los datos (10%-50% en liquidaciones, 5%-40% en promociones) como referencia de lo razonable para detectar estos casos como outliers, no hay un tope oficial más preciso que ese.

**P27.** Confirmado: no, no hay validación automática al cargar el descuento, por eso se colaron estos valores.

**P28.** Les proponemos como default: excluyan estos 5 registros del cálculo de margen, tratándolos como error de carga y no como un descuento real aplicado. Si prefieren imputarles un valor dentro del rango válido en lugar de excluirlos, es una alternativa aceptable, pero solicitamos justificar.

## Bloque 3.4 · Presupuesto con valores negativos o en cero

**P29 y P30.** No tenemos una definición de negocio confirmada para ninguno de los dos casos. Lo que sí podemos decirles es que las 309 celdas en cero están concentradas entre enero y mayo de 2022, correspondiente al periodo de inicio de la ventana de datos y repartidas parejo entre las 28 tiendas, un patrón típico de que el proceso de presupuestación todavía no estaba del todo implementado en esos meses, no de una decisión real de "meta cero". Traten tanto los ceros de ese período inicial como dato no disponible / proceso inmaduro, no como una señal de negocio real, y avancen con ese supuesto sin esperar más precisión nuestra.
Sobre los negativos: a diferencia de los ceros, no están concentrados en ese arranque ya que aparecen en distintos momentos entre 2022 y 2023, así que no les aplica la misma explicación de proceso inmaduro. No tenemos una causa confirmada para ellos; es un error de carga puntual (posiblemente un signo invertido).

**P31.** Confirmado: lo arman conjuntamente Comercial (María G.) y Financiera (Carlos F.) como planificación interna, con actualización mensual/anual. No hay un aprobador formal distinto de ellos dos.

**P32.** Les proponemos como default: excluyan del cálculo de desvío contra presupuesto tanto las 309 celdas en cero del período enero-mayo 2022 como las celdas con presupuesto negativo (dondequiera que aparezcan, no están limitadas a ese período), tratando ambos grupos como dato inválido para ese cálculo, aunque por motivos distintos: los ceros por proceso inmaduro de arranque, los negativos por error de carga. Si prefieren un tratamiento distinto, propónganlo y recuerden que deberán justificarlo.

---

## Cómo se aplicó (verificado el 28-09-2026)

| Respuesta | Aplicación | Dónde |
|---|---|---|
| P1-P2 | Sugerencias para la implementación definitiva (control bloqueante, definición del costo, marcar SKUs sin costo) | Parte B §1.2 · `costo_imputado` en el dataset del modelo |
| P3-P7 | Factor 1,2321 sobre el costo de OC, declarado como supuesto | Parte B §1.2 · `EDA/factor_costo_oc.py` |
| P8-P12 | No usar el historial para revaluar ventas; manda `precio_lista` | H8 · el historial no entra al modelo (§2.1) |
| **P13** | **Nos apartamos de la sugerencia:** no se deflacta por IPC porque `venta_neta` ya está valuada ~al precio actual (se corregiría la inflación dos veces). Se compara en unidades. **La justificación está escrita en H8 y en la Parte B §1.2.** | H8 |
| P14-P17 | Stock negativo con piso en 0 | H4 · todos los scripts |
| P18-P23 | Devoluciones neteadas (default). Abierto: excluir o no el motivo "sin rotación" | H4 · `05-decisiones-modelo.md` |
| P24-P28 | 5 descuentos excluidos del margen | H9 |
| P29-P32 | Ceros ene-may 22 y negativos excluidos del desvío presupuestario | H9 |
