# Preguntas del jurado · Presentación final (Grupo 1)

> Preparación para la ronda de preguntas, siguiendo la Clase 14 (Storytelling, «La defensa ante el Jurado»). Todas las cifras salen del informe final (`Casa_Oga_Informe_Final_Grupo_1.pdf`); entre corchetes, la sección donde está el respaldo. Si una cifra cambia en el informe, hay que actualizarla acá.

## Tres reglas para responder

1. **Repetir la pregunta.** Antes de contestar, repetirla en voz alta con otras palabras («Si entiendo bien, la pregunta es…»). Da unos segundos para ordenar la respuesta y confirma que se entendió.
2. **No inventar números.** Si no se recuerda una cifra, decirlo: «No la tengo de memoria; está en la sección X del informe». Una cifra equivocada cuesta más credibilidad que un «no la recuerdo».
3. **Delimitar el alcance.** Para lo que no se analizó: «No lo analizamos en esta etapa, pero se puede incorporar en el próximo ciclo». Las frases para cada tema fuera de alcance están al final.

**Quién modera:** Santiago recibe cada pregunta, la repite y se la pasa a quien corresponda. Si nadie la tiene clara, la responde Gianfranco con el informe abierto.

| Tema | Responde |
|---|---|
| Datos, calidad, dataset | Matías |
| Modelo, métricas, validación | Simón |
| Tablero, acciones sugeridas, uso en tiendas | Gerónimo |
| Economía, riesgos, legal, plan del piloto | Gianfranco |
| Preguntas generales o de negocio | Santiago |

---

## Negocio y propuesta

### 1. ¿Qué hacen, en una frase?
**Responde:** Santiago
Le damos a Casa Óga una lista mensual por tienda del stock que se va a quedar parado, con qué hacer y por qué, tres meses antes de que aparezca en el conteo de fin de año.

### 2. ¿Por qué no alcanza con la regla de cobertura, que Casa Óga ya puede calcular en Excel?
**Responde:** Simón
La regla sólo ve lo que ya pasó el año de stock: describe el presente. El modelo marca posiciones que todavía no llegaron a 12 meses pero van a llegar en tres. Por eso la propuesta usa las dos: la regla entra completa y el modelo suma 150 posiciones que la regla no ve. Además, la mayor parte del beneficio viene de automatizar la regla, y eso lo decimos abiertamente. [5.5, 7.3]

### 3. ¿Qué decisión le piden a Casa Óga hoy?
**Responde:** Santiago
Tres decisiones: aprobar un piloto de tres cierres por USD 9.570, nombrar a un responsable del modelo y elegir cómo ponerse al día con las 866 posiciones actuales (una limpieza puntual o dos o tres meses de atraso). [11, 10.4]

---

## Modelo

### 4. ¿Por qué 150 alertas del modelo y no otro número?
**Responde:** Simón
El cupo lo fija el valor de cada alerta, no la capacidad de las tiendas. Un acierto vale unos USD 17 y una alerta falsa cuesta unos USD 2, así que un grupo de alertas paga si acierta más del 11,8%. Sumamos grupos de 50 mientras pagaran: el primero acertó 27%, el segundo 14%, el tercero 12% y el cuarto 11%, que ya no paga. Quedaron 150. [5.4]
**Si repreguntan:** en el piloto el cupo se ajusta de a 50 según la precisión real del último grupo. [10.2]

### 5. En 2026 el modelo casi no le gana a la regla. ¿Entonces para qué sirve?
**Responde:** Simón
Es cierto: en 2026 la ventaja es de 2% (1.475 contra 1.452 casos). 2026 es un año fácil: de las posiciones sin venta en un mes, el 82,4% siguió sin vender los tres meses siguientes, contra 9,8% en 2025. Con esa persistencia, la cobertura sola ya casi separa los casos. En un año normal como 2025 la ventaja es de 14% (404 contra 354). Por eso informamos un rango y proponemos medirlo en el piloto antes de comprometer más. [5.5]
**Si repreguntan:** si en dos cohortes seguidas el modelo no supera a la regla, se publica sólo la regla. [9.1]

### 6. Un recall de 51% a 59% quiere decir que se les escapa casi la mitad. ¿No es poco?
**Responde:** Simón
Es lo que detecta con unas 314 alertas por mes, que es lo que conviene trabajar. Con 600 alertas detectaría 69%, pero esas alertas extra cuestan más de lo que recuperan. Y la comparación justa es contra la regla con el mismo cupo, donde el modelo gana en los dos años. [5.4, 5.5]

### 7. ¿Por qué eligieron gradient boosting y no el ensamble del Entregable 3?
**Responde:** Simón
Fijamos la regla antes de mirar los resultados: el ensamble sólo se adoptaba si le ganaba al gradient boosting en tres cupos de una validación interna de 2024. No le ganó. Además, sobreajusta más (PR-AUC de 0,60 en entrenamiento contra 0,27 en validación) y es más difícil de mantener. La regresión logística quedó cerca y es la alternativa si el responsable necesita algo más simple. [5.2, 5.3]

### 8. ¿Cómo saben que no hay fuga de información (leakage)?
**Responde:** Simón
Todas las variables se calculan con información hasta el mes t, y el objetivo es t+3. La partición es temporal, con tres meses de separación: entrenamiento hasta dic-24, validación abr-sep 2025 y test ene-may 2026. Excluimos precio y costo del catálogo (son el valor de hoy), stock en tránsito, presupuesto revisado y cualquier acción posterior a t. [4.3]

### 9. ¿Es una caja negra? ¿Cómo le explican una alerta a una tienda?
**Responde:** Simón
Medimos cuántos casos se pierden si se le esconde cada dato al modelo. Lo que más pesa es la venta de 6 meses, la cobertura y la variabilidad de la venta, que es lo mismo que miraría un comprador. Cada alerta llega con su motivo en palabras, por ejemplo «sin ventas en 6 meses y 4 unidades en stock». Y el modelo sólo ordena: decide una persona. [5.6]

### 10. ¿Funciona igual en todas las regiones y categorías?
**Responde:** Simón
En Patagonia 2025 parece peor (7 de 18), pero con 18 casos el intervalo va de 20% a 61% e incluye el promedio, así que no se puede afirmar. Donde sí rinde menos, con muestra suficiente, es en Cocina y mesa en 2026, y por eso tiene un umbral de monitoreo propio. [5.6]

---

## Datos

### 11. ¿Qué tan confiables son los datos?
**Responde:** Matías
Encontramos 13 problemas de calidad, todos con tratamiento y con una acción en origen (por ejemplo, claves duplicadas o ventas de tiendas antes de su apertura). Las reglas de limpieza las acordamos con Casa Óga. Hay dos limitaciones que declaramos: los datos de 2026 vienen de otro reporte con reglas no documentadas, y las correcciones de la Ronda 3 (22 costos, 11 duplicados, 4 SKUs con dos proveedores y 6 fechas de apertura) todavía no están incorporadas. Incorporarlas es condición para arrancar el piloto. [4.2, 9.2]

### 12. ¿Por qué definieron el riesgo como «más de 12 meses de cobertura»?
**Responde:** Matías
Al principio usamos «sin venta en 3 meses», pero en productos de bajo volumen eso pasaba por azar en el 22% de los casos. La cobertura (stock dividido por la venta promedio de 12 meses) es más estable y es algo que Casa Óga ya entiende. Falta la aprobación formal de María G. [3.5, 2.2]

---

## Tablero y operación

### 13. ¿Quién decide si transferir o liquidar? ¿Lo decide el modelo?
**Responde:** Gerónimo
No. La acción sugerida sale de reglas simples, no del modelo: transferir si otra tienda vende ese producto rápido, frenar compras si hay órdenes pendientes y, si no, liquidar. La tienda propone y Comercial y Compras autorizan en una reunión de media hora. Nada se liquida en forma automática. [3.6, 10.1]

### 14. Si hay 1.016 alertas y las tiendas pueden trabajar 700, ¿qué pasa con el resto?
**Responde:** Gerónimo
Cada tienda trabaja primero las de más capital, así que las 700 que entran en el cupo concentran el 93% del capital en alerta. Las otras 316 pasan al mes siguiente. Por eso le pedimos a la Dirección que elija entre una limpieza puntual o ponerse al día en dos o tres meses. [10.4]
**Si repreguntan por el cupo de 25:** es el máximo que informó Operaciones; nunca se midió, y el piloto lo va a medir. [9.2]

### 15. ¿Por qué no es un tablero en tiempo real?
**Responde:** Gerónimo
Porque los sistemas de Casa Óga no tienen integración ni API: los datos llegan como exportaciones mensuales. Una foto mensual alcanza para una decisión que se toma una vez por mes y se ejecuta en 2 a 4 semanas. [2.4, 3.2]

---

## Economía, riesgos y legal

### 16. El ROI de 18,6% depende de que el desarrollo cueste USD 3.000. ¿No es poco?
**Responde:** Gianfranco
Sí, es el supuesto más sensible, y lo mostramos. Con 3 meses de un científico de datos, el ROI a 3 años queda en -3,3%; con 4 meses, en -11,6%. Aun así, la inversión está dentro del presupuesto de USD 30.000. Y si se cuenta sólo lo que sale de caja (el mantenedor es tiempo de personal que ya existe), el ROI a 3 años es 79,9%. [7.4]

### 17. ¿Por qué usan 2025 como referencia si 2026 da mucho mejor?
**Responde:** Gianfranco
Porque 2026 es un año atípico: tiene cuatro veces más casos y los datos vienen de otro reporte. Con 2026 el ROI a 3 años pasa de 557%, pero eso es un techo, no una promesa. Preferimos presentar el escenario prudente. [7.3]

### 18. ¿Cuánto vale cada acierto? Parece poco.
**Responde:** Gianfranco
Es poco: cada posición inmoviliza unos USD 134 de capital y un acierto vale unos USD 17. El proyecto no rinde por el valor de cada caso, sino por volumen y por las 480 horas por año que hoy se van en armar la lista a mano. [7.2, 7.4]

### 19. ¿Qué pasa si el piloto sale mal?
**Responde:** Gianfranco
Cada riesgo tiene una señal y una respuesta. Si el beneficio trimestral queda por debajo de USD 2.288 durante dos trimestres, se sigue sólo con la lista automatizada. Si el modelo no le gana a la regla en dos cohortes seguidas, se apaga sin costo adicional. Si los datos llegan incompletos, esas filas no se publican. [9.1]

### 20. ¿Hay algún problema legal o de datos personales?
**Responde:** Gianfranco
No hay datos personales, así que la Ley 25.326 no aplica hoy; el riesgo aparece si se suma e-commerce. Lo sensible son los costos y las condiciones con proveedores: las tiendas ven su lista sin costos, y antes del primer acceso se firma una adenda de confidencialidad que también cubre la propiedad del código. [8]

### 21. ¿Quién mantiene esto cuando ustedes se vayan?
**Responde:** Gianfranco
Un responsable interno, 5 a 6 horas por semana, con apoyo externo trimestral para reentrenar. Es la condición más crítica: si no se nombra antes del piloto, la factibilidad técnica baja de media a baja. Propusimos un analista del equipo de Sofía R. [6, 9.2]

---

## Fuera de alcance: frases para responder

| Si preguntan por… | Respuesta |
|---|---|
| E-commerce | «No lo incluimos en esta etapa: es otra plataforma y tiene datos personales. Está en el backlog para una segunda versión.» |
| Precio óptimo de liquidación | «No estimamos el precio de liquidación ni el recupero real por acción. El piloto va a registrar esos datos y se pueden incorporar en el próximo ciclo.» |
| Productos nuevos | «El modelo necesita al menos 3 meses de historia, así que no cubre productos nuevos. Es una mejora prevista para después de la V1.» |
| Optimización de compras | «Quedó fuera de alcance. La vista de Compras ya muestra qué productos están en alerta en muchas tiendas, que es la señal de que se compró de más.» |
| Automatizar la liquidación | «Fue una decisión de diseño: decide siempre una persona. El modelo ordena la lista, no ejecuta.» |
