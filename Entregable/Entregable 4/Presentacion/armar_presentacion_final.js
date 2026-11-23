// Entregable 4 - final presentation deck (PowerPoint), same visual system as the Entregable 3 deck.
// Numbers come from Entregable 4/Modelo/resultados/modelo_final_v4_resultados.json and Entregable 2 insights.json.
// Run: NODE_PATH=<node_modules with pptxgenjs, react, react-dom, react-icons, sharp> node armar_presentacion_final.js
// Then: node <pptx skill>/scripts/apply_theme.js <out.pptx> ../../Entregable\ 3/Presentacion/theme.json
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");

const ROOT = path.resolve(__dirname, "../../..");
const OUT = path.join(__dirname, "Casa-Oga-Presentacion-Final.pptx");
const R = JSON.parse(fs.readFileSync(path.join(ROOT, "Entregable/Entregable 4/Modelo/resultados/modelo_final_v4_resultados.json"), "utf8"));
const INS = JSON.parse(fs.readFileSync(path.join(ROOT, "Entregable/Entregable 2/Modelo/resultados/insights.json"), "utf8"));
const THEME = JSON.parse(fs.readFileSync(path.join(ROOT, "Entregable/Entregable 3/Presentacion/theme.json"), "utf8"));
THEME.name = "Casa Oga Final";
const HEX = THEME.colors;

// ---------- number formatting (es-AR) ----------
const num = (x, d = 0) => Number(x).toLocaleString("es-AR", { minimumFractionDigits: d, maximumFractionDigits: d });
const pct = (x, d = 0) => num(100 * x, d) + "%";
const usd = (x) => "USD " + num(x);
const fv = R.flujo.validacion, ft = R.flujo.test, rv = R.roi.validacion, rt = R.roi.test;
const vb = R.insumos.valor_unitario.base_e2, kb = R.punto_operacion.k_bloque_b;
const pers = R.persistencia_sin_venta, vi = R.validacion_interna;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.title = "Casa Óga · Presentación final · Grupo 1";
pres.author = "Grupo 1";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const NAVY = C.text1, DARK = C.text2, WHITE = C.background1, LIGHT = C.background2;
const GOLD = C.accent1, TEAL = C.accent2, CORAL = C.accent3, STEEL = C.accent4, MUTED = C.accent5, LINE = C.accent6;

pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: WHITE },
  margin: [0.4, 0.6, 0.6, 0.6],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.42, w: 9.7, h: 0.85, fontSize: 30, bold: true, color: NAVY, align: "left", valign: "middle", margin: 0 }, text: "" } },
    { text: { text: "Casa Óga · Presentación final · Grupo 1", options: { x: 0.6, y: 7.0, w: 6, h: 0.3, fontSize: 10, color: MUTED, margin: 0 } } },
  ],
  slideNumber: { x: 12.23, y: 7.0, w: 0.5, h: 0.3, fontSize: 10, color: MUTED, align: "right" },
});
pres.defineSlideMaster({
  title: "DARK",
  background: { color: DARK },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.0, w: 11.7, h: 1.9, fontSize: 44, bold: true, color: WHITE, align: "left", valign: "top", margin: 0 }, text: "" } },
  ],
});

// ---------- helpers ----------
const ICONS = {};
async function iconPng(name, hex = "FFFFFF") {
  const key = name + hex;
  if (!ICONS[key]) {
    const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(fa[name], { color: "#" + hex, size: 256 }));
    const buf = await sharp(Buffer.from(svg)).resize(256, 256).png().toBuffer();
    ICONS[key] = "image/png;base64," + buf.toString("base64");
  }
  return ICONS[key];
}
async function iconCircle(slide, name, x, y, d, fill = NAVY, iconHex = "FFFFFF") {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { type: "none" }, objectName: "icon-circle-" + name });
  const s = d * 0.52;
  slide.addImage({ data: await iconPng(name, iconHex), x: x + (d - s) / 2, y: y + (d - s) / 2, w: s, h: s, altText: name.replace(/^Fa/, "") + " icon" });
}
function text(slide, t, o) {
  slide.addText(t, { isTextBox: true, margin: 0, valign: "top", fontSize: 14, color: NAVY, ...o });
}
function card(slide, x, y, w, h, fill = LIGHT, name = "card") {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill }, line: { type: "none" }, objectName: name });
}
function speaker(slide, name, role) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 10.55, y: 0.52, w: 2.18, h: 0.66, rectRadius: 0.33, fill: { color: GOLD }, line: { type: "none" }, objectName: "speaker-chip" });
  text(slide, [
    { text: name, options: { bold: true, fontSize: 13, breakLine: true } },
    { text: role, options: { fontSize: 11 } },
  ], { x: 10.55, y: 0.52, w: 2.18, h: 0.66, align: "center", valign: "middle", color: NAVY });
}
function dots(slide, x, y, score, d = 0.22) {
  for (let i = 0; i < 3; i++) {
    slide.addShape(pres.shapes.OVAL, { x: x + i * (d + 0.1), y, w: d, h: d, fill: { color: i < score ? TEAL : WHITE }, line: { color: i < score ? TEAL : LINE, width: 1.25 }, objectName: "score-dot" });
  }
}
function pill(slide, t, x, y, w, fill, color = WHITE, h = 0.34) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: h / 2, fill: { color: fill }, line: { type: "none" }, objectName: "pill" });
  text(slide, t, { x, y, w, h, fontSize: 12, bold: true, color, align: "center", valign: "middle" });
}
const CHART_BASE = () => ({
  catAxisLabelColor: HEX.accent5, valAxisLabelColor: HEX.accent5,
  catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", dataLabelFontFace: "+mn-lt", legendFontFace: "+mn-lt",
  catAxisLabelFontSize: 12, valAxisLabelFontSize: 11, dataLabelFontSize: 12, legendFontSize: 12,
  valGridLine: { color: HEX.lt2, size: 1 }, catGridLine: { style: "none" },
  catAxisLineShow: false, valAxisLineShow: false,
});
function content(sectionTitle, title) {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle });
  s.addText(title, { placeholder: "title" });
  return s;
}
function table(slide, header, rows, o) {
  const head = header.map((h) => ({ text: h, options: { bold: true, color: WHITE, fill: { color: HEX.dk1 } } }));
  slide.addTable([head, ...rows.map((r) => r.map((v) => (typeof v === "object" ? v : { text: String(v) })))], {
    fontSize: 13, color: HEX.dk1, border: { type: "solid", pt: 0.75, color: HEX.accent6 }, margin: 0.06, valign: "middle", ...o,
  });
}

async function build() {
  // ================= 1 · Cover =================
  pres.addSection({ title: "Apertura" });
  {
    const s = pres.addSlide({ masterName: "DARK", sectionTitle: "Apertura" });
    text(s, "PRESENTACIÓN FINAL · ENTREGABLES 1 A 3 INTEGRADOS Y CORREGIDOS", { x: 0.8, y: 1.3, w: 11, h: 0.4, fontSize: 14, bold: true, color: GOLD, charSpacing: 2 });
    s.addText("Detección anticipada de inventario inmovilizado", { placeholder: "title" });
    text(s, "Casa Óga · Retail de Hogar y Decoración", { x: 0.8, y: 3.75, w: 11, h: 0.5, fontSize: 22, color: LINE });
    const team = [
      ["Santiago Javier Hernández", "Comunicación"], ["Matías Fleischer", "Datos · calidad y preparación"],
      ["Simón Volpato Escandarani", "Datos · modelado y evaluación"], ["Gerónimo Fasce", "Visualización"],
      ["Gianfranco Di Claudio", "Coordinación"],
    ];
    team.forEach(([n, r], i) => {
      const col = i < 3 ? 0 : 1, row = i < 3 ? i : i - 3;
      text(s, [
        { text: n, options: { bold: true, color: WHITE, fontSize: 15, breakLine: true } },
        { text: r, options: { color: LINE, fontSize: 12 } },
      ], { x: 0.8 + col * 4.6, y: 4.85 + row * 0.62, w: 4.4, h: 0.6 });
    });
    text(s, "Grupo 1 · Noviembre 2026", { x: 9.2, y: 6.55, w: 3.35, h: 0.4, fontSize: 14, color: GOLD, align: "right", bold: true });
    s.addNotes("SANTIAGO. Buenas, somos el Grupo 1. Esta es la presentación final del proyecto de Casa Óga: integra los tres entregables y todas las correcciones que nos hicieron la cátedra y Casa Óga. En una frase: queremos que Casa Óga intervenga el stock que se va a inmovilizar antes de que pase, no en el conteo anual. Cada uno presenta la parte de la que es responsable: Matías los datos, Simón el modelo, Gerónimo la solución, Gianfranco la economía, los riesgos y el plan, y yo abro y cierro.");
  }

  // ================= 2 · Problem =================
  {
    const s = content("Apertura", "En 2026 el stock que no rota se cuadruplicó");
    speaker(s, "Santiago", "Comunicación");
    const m = INS.rojo_mes;
    s.addChart(pres.charts.LINE, [{ name: "Posiciones con cobertura > 12 meses", labels: m.meses.map((x) => x.slice(2).replace("-", "/")), values: m.posiciones }], {
      x: 0.6, y: 1.5, w: 7.6, h: 4.9, ...CHART_BASE(), chartColors: [HEX.accent4], lineSize: 2.5, lineDataSymbol: "none",
      showTitle: true, title: "Posiciones SKU–tienda con más de 12 meses de cobertura", titleFontFace: "+mn-lt", titleFontSize: 14, titleColor: HEX.dk1,
      showLegend: false, catAxisLabelFrequency: 6, valAxisMinVal: 0, valAxisMaxVal: 1000, valAxisMajorUnit: 250,
    });
    const stats = [
      ["FaBoxes", "866", "posiciones en agosto de 2026 (200 en diciembre de 2025)"],
      ["FaMoneyBillWave", "ARS 178,6 M", "de capital inmovilizado, a costo"],
      ["FaArrowDown", "−13,4%", "venta ene-ago 2026 contra 2025: 2 de cada 3 pesos son SKUs discontinuados"],
    ];
    for (let i = 0; i < stats.length; i++) {
      const y = 1.6 + i * 1.6;
      await iconCircle(s, stats[i][0], 8.6, y + 0.1, 0.62, i === 0 ? CORAL : NAVY);
      text(s, stats[i][1], { x: 9.4, y, w: 3.4, h: 0.55, fontSize: 28, bold: true, color: i === 0 ? CORAL : NAVY });
      text(s, stats[i][2], { x: 9.4, y: y + 0.6, w: 3.4, h: 0.8, fontSize: 13, color: MUTED });
    }
    text(s, "Entre 2023 y 2025 el problema era estable en proporción: crecía el monto porque crecía el negocio.", { x: 0.6, y: 6.45, w: 12, h: 0.4, fontSize: 13, italic: true, color: MUTED });
    s.addNotes("SANTIAGO. Primero el problema, de afuera hacia adentro. En 2026 la venta cae 13,4% y el stock que no rota se dispara: las posiciones con más de 12 meses de cobertura pasan de 200 en diciembre a 866 en agosto, con 178,6 millones de pesos parados a costo. Una corrección importante respecto del Entregable 1: entre 2023 y 2025 el problema era estable en proporción; crecía el monto porque crecía el negocio. No es alarmismo: lo nuevo es 2026, y parte del salto puede venir del nuevo reporte de datos de ese año. Hoy esto se ve en el conteo anual: tarde.");
  }

  // ================= 3 · Recommendation =================
  {
    const s = content("Apertura", "Recomendamos un piloto supervisado de tres cierres");
    speaker(s, "Santiago", "Comunicación");
    const cards = [
      ["FaCogs", "Técnica", "Media · 2,25", "Los datos alcanzan; falta un responsable del modelo", TEAL],
      ["FaChartLine", "Económica", `ROI 3 años ${pct(rv.total.roi_3anios, 1)}`, `Recupero en ${num(rv.total.recupero_meses)} meses en un año como 2025; sensible al costo de desarrollo`, GOLD],
      ["FaBalanceScale", "Legal", "Viable · 2,2", "Accesos por rol y adenda de confidencialidad", TEAL],
      ["FaBullseye", "Modelo", `+${pct(fv.flujo.vp / fv.regla_mismo_cupo.vp - 1)} sobre la regla`, `A igual cupo en 2025 (${fv.flujo.vp} vs ${fv.regla_mismo_cupo.vp} casos); +${pct(ft.flujo.vp / ft.regla_mismo_cupo.vp - 1)} en 2026`, TEAL],
    ];
    for (let i = 0; i < 4; i++) {
      const x = 0.6 + i * 3.08;
      card(s, x, 1.6, 2.85, 3.6);
      await iconCircle(s, cards[i][0], x + 0.25, 1.85, 0.6, NAVY);
      text(s, cards[i][1], { x: x + 0.25, y: 2.6, w: 2.4, h: 0.4, fontSize: 15, bold: true, color: MUTED });
      text(s, cards[i][2], { x: x + 0.25, y: 3.0, w: 2.45, h: 0.6, fontSize: 21, bold: true, color: NAVY });
      text(s, cards[i][3], { x: x + 0.25, y: 3.75, w: 2.4, h: 1.3, fontSize: 13, color: NAVY });
    }
    card(s, 0.6, 5.45, 12.13, 1.2, NAVY, "verdict");
    text(s, [
      { text: "Viable con condiciones como piloto supervisado. ", options: { bold: true, color: GOLD } },
      { text: "Sin compras nuevas, con decisión humana, y el modelo sigue sólo si en el piloto le gana a la regla a igual cupo.", options: { color: WHITE } },
    ], { x: 0.9, y: 5.6, w: 11.6, h: 0.9, fontSize: 16, valign: "middle" });
    s.addNotes(`SANTIAGO. Les adelantamos la conclusión y después el equipo la justifica. Técnicamente es factible con score 2,25: los datos alcanzan, lo que falta es alguien en Casa Óga que sostenga el modelo. Legalmente es viable con condiciones, 2,2. Económicamente, con los números corregidos, en un año como 2025 el proyecto recupera la inversión en unos ${num(rv.total.recupero_meses)} meses; pero es sensible al costo real de desarrollo. Y el modelo le gana a la regla simple en los dos años, con una ventaja chica en 2026. Por eso recomendamos un piloto supervisado de tres cierres. Le paso a Gianfranco, que cuenta qué corregimos.`);
  }

  // ================= 4 · What we corrected =================
  pres.addSection({ title: "Correcciones" });
  {
    const s = content("Correcciones", "Qué cambió respecto de las entregas anteriores");
    speaker(s, "Gianfranco", "Coordinación");
    const items = [
      ["FaEquals", "Una cifra, un valor", "Un solo indicador reproducible del problema y un solo dataset (v4) en todo el informe"],
      ["FaListOl", "Backlog y plan", "Backlog con épicas e historias, fases, hitos, precondiciones y roles"],
      ["FaUsers", "Stakeholders", "Influencia técnica y de decisión separadas; Sistemas/IT y proveedores en el mapa"],
      ["FaFilter", "Modelo elegido sin sesgo", "Selección en una validación interna 2024; el test 2026 sólo para reportar"],
      ["FaSlidersH", "Cupo por valor", "Se agregan alertas mientras paguen, no hasta llenar las 600"],
      ["FaCoins", "Dos ROI", "Automatizar la lista y el incremental del modelo, con valor por posición reproducible"],
    ];
    for (let i = 0; i < items.length; i++) {
      const col = i % 2, row = Math.floor(i / 2);
      const x = 0.6 + col * 6.15, y = 1.6 + row * 1.68;
      card(s, x, y, 5.95, 1.45);
      await iconCircle(s, items[i][0], x + 0.25, y + 0.38, 0.68, STEEL);
      text(s, items[i][1], { x: x + 1.15, y: y + 0.22, w: 4.6, h: 0.4, fontSize: 17, bold: true });
      text(s, items[i][2], { x: x + 1.15, y: y + 0.65, w: 4.6, h: 0.7, fontSize: 13, color: MUTED });
    }
    s.addNotes("GIANFRANCO. Antes de los resultados, qué corregimos. Del Entregable 1: había dos juegos de cifras que no cerraban; ahora hay un solo indicador reproducible y un solo dataset en todo el informe. Agregamos el backlog que el título prometía y separamos la influencia técnica de la de decisión en el mapa de stakeholders, sumando Sistemas y los proveedores. Del Entregable 3: el modelo se elige en una validación interna para que la de 2025 siga siendo independiente; el cupo de alertas lo fija el valor de cada alerta y no la capacidad; y la economía se presenta como dos ROI separados. Todo está detallado en la sección 12 del informe. Le paso a Matías.");
  }

  // ================= 5 · Data =================
  pres.addSection({ title: "Datos" });
  {
    const s = content("Datos", "Los datos alcanzan, con reglas acordadas con Casa Óga");
    speaker(s, "Matías", "Datos · calidad");
    const stats = [["201.310", "filas SKU–tienda–mes"], ["60", "variables calculadas al cierre del mes"], ["3,22%", "posiciones que terminan con más de 12 meses de cobertura"], ["13", "hallazgos de calidad con tratamiento y acción en origen"]];
    stats.forEach(([v, l], i) => {
      const y = 1.6 + i * 1.22;
      text(s, v, { x: 0.6, y, w: 2.6, h: 0.6, fontSize: 32, bold: true, color: STEEL });
      text(s, l, { x: 3.2, y: y + 0.12, w: 3.4, h: 0.8, fontSize: 14, color: NAVY });
    });
    card(s, 6.9, 1.6, 5.83, 4.9);
    text(s, "Lo que cuidamos", { x: 7.2, y: 1.8, w: 5.3, h: 0.4, fontSize: 17, bold: true });
    text(s, [
      { text: "Duplicados: se conserva el registro de mayor venta, como pidió Casa Óga.", options: { bullet: true, breakLine: true } },
      { text: "Devoluciones al proveedor por «sin rotación» fuera del neteo.", options: { bullet: true, breakLine: true } },
      { text: "2026 viene de otro reporte (H13): validación 2025 y test 2026 se miran por separado.", options: { bullet: true, breakLine: true } },
      { text: "Sin fuga de información: todo con datos hasta el mes t.", options: { bullet: true, breakLine: true } },
      { text: "Pendiente: incorporar la Ronda 3 (22 costos, 11 duplicados, 4 multiproveedor, 6 aperturas) antes del piloto.", options: { bullet: true, bold: true } },
    ], { x: 7.2, y: 2.35, w: 5.3, h: 4.0, fontSize: 14, paraSpaceAfter: 8 });
    s.addNotes("MATÍAS. Los datos alcanzan: 201 mil filas a nivel producto–tienda–mes, 60 variables calculadas al cierre de cada mes, y un 3,22% de casos positivos. Encontramos 13 problemas de calidad y cada uno tiene tratamiento en el proyecto y una acción para corregirlo en origen. Aplicamos las reglas que pidió Casa Óga: ante duplicados nos quedamos con el registro de mayor venta y las devoluciones al proveedor no se restan de la venta. Como 2026 viene de otro reporte, siempre mostramos 2025 y 2026 por separado. Queda un pendiente que no depende de nosotros: incorporar las correcciones de la Ronda 3; es condición previa al piloto, con fecha y responsable.");
  }

  // ================= 6 · Technical feasibility =================
  {
    const s = content("Datos", "Técnicamente factible, con una condición");
    speaker(s, "Matías", "Datos · calidad");
    const rows = [["Datos suficientes", 3, "51 meses y 6.490 casos; la granularidad es la de la decisión"], ["Calidad utilizable", 2, "Reglas acordadas; tres problemas estructurales excluyen variables"], ["Infraestructura", 2, "PC de oficina existente y herramientas gratuitas; integración manual"], ["Capacidad humana", 2, "No hay área de datos ni mantenedor nombrado"]];
    rows.forEach(([n, sc, d], i) => {
      const y = 1.65 + i * 1.05;
      card(s, 0.6, y, 8.2, 0.88);
      text(s, n, { x: 0.85, y: y + 0.14, w: 2.8, h: 0.6, fontSize: 16, bold: true, valign: "middle" });
      dots(s, 3.75, y + 0.33, sc);
      text(s, d, { x: 4.85, y: y + 0.14, w: 3.8, h: 0.6, fontSize: 13, color: MUTED, valign: "middle" });
    });
    card(s, 9.1, 1.65, 3.63, 4.03, NAVY, "score");
    text(s, "2,25", { x: 9.1, y: 2.0, w: 3.63, h: 1.0, fontSize: 54, bold: true, color: GOLD, align: "center" });
    text(s, "Factibilidad media", { x: 9.1, y: 3.05, w: 3.63, h: 0.4, fontSize: 17, bold: true, color: WHITE, align: "center" });
    text(s, "Si no se nombra mantenedor antes del piloto, capacidad humana baja a 1 y el promedio a 2,0.", { x: 9.4, y: 3.7, w: 3.05, h: 1.6, fontSize: 13, color: LINE, align: "center" });
    s.addNotes("MATÍAS. Evaluamos cuatro condiciones técnicas de 1 a 3. Datos suficientes tiene 3. Calidad, infraestructura y capacidad humana tienen 2: hay problemas, pero son superables. Una corrección: la PC de oficina existe y es el entorno del piloto, no compramos equipo. La condición que más pesa es la humana: si antes del piloto no se nombra un responsable del modelo, el score baja a 2,0. Le paso a Simón con el modelo.");
  }

  // ================= 7 · Model selection =================
  pres.addSection({ title: "Modelo" });
  {
    const s = content("Modelo", "Elegimos el modelo más simple que rinde igual");
    speaker(s, "Simón", "Modelado");
    const v = (k, m) => vi["top_" + k][m].vp;
    table(s, ["Validación interna (jul-dic 2024)", "Top-175", "Top-300", "Top-420", "Top-600"], [
      ["Regla ordenada por cobertura", v(175, "Regla"), v(300, "Regla"), v(420, "Regla"), v(600, "Regla")],
      ["Regresión logística", v(175, "Logistica"), v(300, "Logistica"), v(420, "Logistica"), v(600, "Logistica")],
      [{ text: "Gradient boosting (elegido)", options: { bold: true } }, v(175, "HistGradientBoosting"), v(300, "HistGradientBoosting"), v(420, "HistGradientBoosting"), v(600, "HistGradientBoosting")],
      ["Ensamble de 3 árboles", v(175, "Ensamble"), v(300, "Ensamble"), v(420, "Ensamble"), v(600, "Ensamble")],
    ], { x: 0.6, y: 1.65, w: 7.9, colW: [3.5, 1.1, 1.1, 1.1, 1.1], rowH: 0.55 });
    text(s, `Casos detectados de ${vi.positivos}. Entrenamiento hasta mar-24, embargo de 3 meses.`, { x: 0.6, y: 4.6, w: 7.9, h: 0.4, fontSize: 12, color: MUTED });
    card(s, 8.85, 1.65, 3.88, 4.6);
    await iconCircle(s, "FaCheckCircle", 9.1, 1.9, 0.6, TEAL);
    text(s, "Regla fijada antes de mirar", { x: 9.1, y: 2.65, w: 3.4, h: 0.4, fontSize: 16, bold: true });
    text(s, "El ensamble se adopta sólo si le gana al gradient boosting en 175, 300 y 420 alertas. No lo hace: nos quedamos con un solo modelo, que sobreajusta menos y se explica y mantiene más fácil.", { x: 9.1, y: 3.1, w: 3.4, h: 2.4, fontSize: 13, color: NAVY });
    s.addNotes("SIMÓN. Una de las correcciones de la cátedra fue que habíamos elegido el ensamble mirando la validación 2025, con lo que esa validación dejaba de ser independiente. Ahora elegimos en una validación interna de 2024, con una regla fijada antes de mirar: el ensamble entra sólo si le gana al gradient boosting en todos los cupos. No le gana, así que nos quedamos con un solo modelo de gradient boosting: sobreajusta menos y es más fácil de explicar y de mantener. La logística queda cerca y sigue siendo la alternativa si hiciera falta algo más simple.");
  }

  // ================= 8 · Quota by value =================
  {
    const s = content("Modelo", "El cupo lo fija el valor de cada alerta, no la capacidad");
    speaker(s, "Simón", "Modelado");
    const cur = R.periodos.validacion.curva;
    const ks = Object.keys(cur).map(Number).filter((k) => k % 50 === 0).sort((a, b) => a - b);
    s.addChart(pres.charts.LINE, [
      { name: "Modelo", labels: ks.map(String), values: ks.map((k) => cur[k].HistGradientBoosting.valor_neto_mes_usd) },
      { name: "Regla por cobertura", labels: ks.map(String), values: ks.map((k) => cur[k].Regla.valor_neto_mes_usd) },
    ], {
      x: 0.6, y: 1.5, w: 7.9, h: 4.9, ...CHART_BASE(), chartColors: [HEX.accent4, HEX.accent3], lineSize: 2.5, lineDataSymbolSize: 6,
      showTitle: true, title: "Valor neto por mes (USD) según alertas por mes · validación 2025", titleFontFace: "+mn-lt", titleFontSize: 14, titleColor: HEX.dk1,
      showLegend: true, legendPos: "b", showCatAxisTitle: true, catAxisTitle: "Alertas por mes", catAxisTitleColor: HEX.accent5, catAxisTitleFontSize: 12,
    });
    const tr = R.punto_operacion.tramos_bloque_b_validacion.slice(0, 5);
    text(s, `Una alerta paga si el tramo acierta más del ${pct(vb.precision_equilibrio, 1)}`, { x: 8.85, y: 1.6, w: 3.9, h: 0.8, fontSize: 17, bold: true });
    tr.forEach((t, i) => {
      const y = 2.55 + i * 0.58, ok = t.precision_tramo > vb.precision_equilibrio;
      text(s, `Tramo ${i + 1} (50 alertas)`, { x: 8.85, y: y + 0.05, w: 2.3, h: 0.4, fontSize: 13, valign: "middle" });
      pill(s, pct(t.precision_tramo), 11.2, y, 1.4, ok ? TEAL : CORAL);
    });
    text(s, `Resultado: la regla completa + ${kb} alertas del modelo ≈ ${num(fv.flujo.alertas_mes)} por mes (${num(fv.flujo.alertas_mes / 28)} por tienda).`, { x: 8.85, y: 5.55, w: 3.9, h: 0.9, fontSize: 13, color: MUTED });
    s.addNotes(`SIMÓN. Antes llenábamos la capacidad: 600 alertas por mes. La cátedra nos marcó que la capacidad es un techo, no una meta, y que las últimas alertas costaban más de lo que recuperaban. Con el valor por posición reproducible, una alerta paga si acierta más del ${pct(vb.precision_equilibrio, 1)}. Entonces armamos la lista así: entra completa la regla de cobertura y el modelo agrega tramos de 50 mientras el tramo pague. En 2025 los tres primeros tramos pagan y el cuarto no: el modelo suma ${kb} alertas por mes. El gráfico muestra que el valor deja de crecer mucho antes de las 600.`);
  }

  // ================= 9 · Results =================
  {
    const s = content("Modelo", "Le gana a la regla en los dos años; en 2026, por poco");
    speaker(s, "Simón", "Modelado");
    s.addChart(pres.charts.BAR, [
      { name: "Solo regla", labels: ["Validación 2025", "Test 2026"], values: [fv.bloque_a.vp, ft.bloque_a.vp] },
      { name: "Cobertura, mismo cupo", labels: ["Validación 2025", "Test 2026"], values: [fv.regla_mismo_cupo.vp, ft.regla_mismo_cupo.vp] },
      { name: "Flujo regla + modelo", labels: ["Validación 2025", "Test 2026"], values: [fv.flujo.vp, ft.flujo.vp] },
    ], {
      x: 0.6, y: 1.5, w: 7.6, h: 4.9, barDir: "col", barGrouping: "clustered", barGapWidthPct: 60, ...CHART_BASE(),
      chartColors: [HEX.accent3, HEX.accent6, HEX.accent4], showValue: true, dataLabelPosition: "outEnd", dataLabelColor: HEX.dk1,
      showTitle: true, title: "Casos en riesgo detectados (mismas alertas por mes)", titleFontFace: "+mn-lt", titleFontSize: 14, titleColor: HEX.dk1,
      showLegend: true, legendPos: "b", valAxisHidden: true, valGridLine: { style: "none" },
    });
    const st = [
      [`${pct(fv.flujo.recall)} – ${pct(ft.flujo.recall)}`, "recall esperado (2025 a 2026)"],
      [`${pct(fv.flujo.precision)} – ${pct(ft.flujo.precision)}`, "precisión esperada"],
      [`${pct(pers["2025"].proporcion, 1)} → ${pct(pers["2026"].proporcion, 1)}`, "posiciones sin venta que siguen sin vender 3 meses: por eso 2026 es más fácil"],
    ];
    st.forEach(([v, l], i) => {
      const y = 1.6 + i * 1.55;
      text(s, v, { x: 8.6, y, w: 4.1, h: 0.6, fontSize: 26, bold: true, color: STEEL });
      text(s, l, { x: 8.6, y: y + 0.62, w: 4.1, h: 0.8, fontSize: 13, color: MUTED });
    });
    s.addNotes(`SIMÓN. Con el mismo número de alertas, el flujo regla más modelo detecta ${fv.flujo.vp} casos en 2025 contra ${fv.regla_mismo_cupo.vp} de ordenar por cobertura: 14% más. En 2026, ${num(ft.flujo.vp)} contra ${num(ft.regla_mismo_cupo.vp)}: apenas 2% más. Le gana en los dos años, así que es robusto, pero la ventaja es chica justo en el año fácil. ¿Por qué 2026 es más fácil? De las posiciones sin venta en un mes, las que siguen sin vender tres meses pasan de 9,8% en 2025 a 82,4% en 2026: con esa persistencia la cobertura sola casi alcanza. Por eso informamos el desempeño como un rango.`);
  }

  // ================= 10 · Explainability =================
  {
    const s = content("Modelo", "El modelo mira lo que miraría un comprador, antes");
    speaker(s, "Simón", "Modelado");
    const imp = R.importancia_permutacion.variables.slice(0, 6);
    const nombres = { u6_suma: "Venta de 6 meses", cobertura: "Cobertura actual", cv_u12: "Variabilidad de la venta", stock_sku_cadena: "Stock del SKU en la cadena", peso_posicion_en_tienda: "Peso en la tienda", u12_prom: "Venta promedio 12 m" };
    s.addChart(pres.charts.BAR, [{ name: "Puntos de recall perdidos", labels: imp.map((r) => nombres[r.variable] || r.variable).reverse(), values: imp.map((r) => +r.caida_recall_pp.toFixed(1)).reverse() }], {
      x: 0.6, y: 1.5, w: 7.6, h: 4.9, barDir: "bar", ...CHART_BASE(), chartColors: [HEX.accent4], showValue: true, dataLabelPosition: "outEnd", dataLabelColor: HEX.dk1,
      dataLabelFormatCode: "0.0", showTitle: true, title: "Recall que se pierde al mezclar cada variable (puntos)", titleFontFace: "+mn-lt", titleFontSize: 14, titleColor: HEX.dk1,
      showLegend: false, valAxisHidden: true, valGridLine: { style: "none" }, barGapWidthPct: 50,
    });
    card(s, 8.6, 1.6, 4.13, 2.2);
    text(s, "Cada alerta trae su motivo", { x: 8.85, y: 1.8, w: 3.7, h: 0.4, fontSize: 16, bold: true });
    text(s, "«Sin ventas en 6 meses y 4 unidades en stock». La persona decide; el modelo sólo ordena.", { x: 8.85, y: 2.25, w: 3.7, h: 1.4, fontSize: 13, color: NAVY });
    card(s, 8.6, 4.0, 4.13, 2.4);
    text(s, "Segmentos con intervalo de confianza", { x: 8.85, y: 4.2, w: 3.7, h: 0.4, fontSize: 16, bold: true });
    text(s, "Patagonia (7 de 18) no es peor: su intervalo, 20% a 61%, incluye el global. Cocina y mesa sí queda debajo en 2026 y se monitorea aparte.", { x: 8.85, y: 4.65, w: 3.7, h: 1.6, fontSize: 13, color: NAVY });
    s.addNotes("SIMÓN. Para explicar el modelo mezclamos al azar cada variable y medimos cuántos casos se pierden: así vemos qué usa el sistema completo y en la métrica del negocio. Lo que más pesa es la venta de los últimos 6 meses, la cobertura actual y la variabilidad de la venta: lo mismo que miraría un comprador, pero combinado antes de que la cobertura cruce los 12 meses. También corregimos la lectura por segmento: con 18 casos, Patagonia tiene un intervalo de 20% a 61%, así que no podemos decir que el modelo funcione peor ahí. Cocina y mesa sí, y tiene su propio umbral de monitoreo. Le paso a Gerónimo con la solución.");
  }

  // ================= 11 · Solution flow =================
  pres.addSection({ title: "Solución" });
  {
    const s = content("Solución", "Una lista mensual por tienda, y una persona decide");
    speaker(s, "Gerónimo", "Visualización");
    const steps = [
      ["FaFileImport", "Ingesta", "5 archivos con clave fija; control de recepción", "Días 1-3"],
      ["FaBroom", "Preparación", "Reglas del E2 y 60 variables al cierre del mes", "Días 3-4"],
      ["FaSortAmountDown", "Scoring", `Regla completa + ${kb} posiciones del modelo`, "Día 4"],
      ["FaStore", "Entrega", "Cada tienda ve sus alertas, sin costos, con motivo", "Día 5"],
      ["FaUserCheck", "Decisión", "La tienda propone; Comercial y Compras autorizan", "30 min"],
      ["FaSyncAlt", "Aprendizaje", "A t+3: aciertos, valor y ajuste del cupo", "Mensual"],
    ];
    for (let i = 0; i < steps.length; i++) {
      const x = 0.6 + i * 2.05;
      card(s, x, 1.8, 1.85, 3.7);
      await iconCircle(s, steps[i][0], x + 0.6, 2.05, 0.65, i === 2 ? GOLD : NAVY, i === 2 ? HEX.dk1 : "FFFFFF");
      text(s, steps[i][1], { x: x + 0.12, y: 2.9, w: 1.61, h: 0.4, fontSize: 15, bold: true, align: "center" });
      text(s, steps[i][2], { x: x + 0.12, y: 3.35, w: 1.61, h: 1.4, fontSize: 12, color: NAVY, align: "center" });
      pill(s, steps[i][3], x + 0.27, 4.9, 1.31, LIGHT, NAVY, 0.32);
    }
    text(s, "Bloque A explica solo (ya está sobrestockeado). Bloque B anticipa (va a superar 12 meses dentro de 3).", { x: 0.6, y: 5.85, w: 12.1, h: 0.5, fontSize: 14, italic: true, color: MUTED });
    s.addNotes(`GERÓNIMO. Así llega el modelo a una decisión. Cada cierre se reciben cinco archivos con formato fijo; se limpian con las reglas del Entregable 2; se arma la lista: primero todo lo que ya tiene más de 12 meses de cobertura, que se explica solo, y después las ${kb} posiciones que el modelo anticipa. Cada tienda ve sólo sus alertas, sin costos y con el motivo. La tienda propone liquidar, transferir, frenar compras o desestimar, y Comercial y Compras autorizan en una sesión de 30 minutos. Tres meses después medimos si acertamos y ajustamos el cupo.`);
  }

  // ================= 12 · Who sees what =================
  {
    const s = content("Solución", "Cada usuario ve lo que necesita para decidir");
    speaker(s, "Gerónimo", "Visualización");
    table(s, ["Usuario", "Qué recibe", "Qué decide"], [
      ["Responsables de tienda (28)", "Su lista de ~11 posiciones con SKU, cobertura, ventas y motivo; sin costos", "Proponer la acción o desestimar con motivo"],
      ["María G. · Comercial", "Resumen por categoría y tienda; acciones pendientes", "Autoriza liquidaciones y descuentos"],
      ["Diego P. · Compras", "SKUs en riesgo en varias tiendas, con OC y proveedor (vista restringida)", "Frenar compras, devolver, discontinuar"],
      ["Lucía O. · Operaciones", "Lista consolidada, cupo por tienda y seguimiento", "Transferencias y prioridad"],
      ["Carlos F. · Finanzas", "Capital en riesgo, valor recuperado y horas evitadas", "Continuidad y expansión"],
    ], { x: 0.6, y: 1.6, w: 12.13, colW: [3.0, 5.4, 3.73], rowH: 0.72, fontSize: 13 });
    text(s, "El tablero es un corte mensual con carga manual de datos, no un tablero en vivo.", { x: 0.6, y: 6.1, w: 12, h: 0.4, fontSize: 13, italic: true, color: MUTED });
    s.addNotes("GERÓNIMO. Cada usuario recibe sólo lo que necesita. La tienda ve su lista corta, alrededor de 11 posiciones por mes, sin costos. Comercial autoriza, Compras ve el riesgo por SKU y proveedor en una vista restringida, Operaciones coordina las transferencias y Finanzas sigue el valor recuperado. Una aclaración que nos pidió la cátedra: el tablero es un corte mensual, con carga manual, no un tablero en vivo. Le paso a Gianfranco con la economía.");
  }

  // ================= 13 · Economics =================
  pres.addSection({ title: "Viabilidad y plan" });
  {
    const s = content("Viabilidad y plan", "La lista ya paga sola; el modelo suma por encima");
    speaker(s, "Gianfranco", "Coordinación");
    const cols = [
      ["Automatizar la lista (sin modelo)", rv.automatizacion_sin_modelo, "Horas evitadas + valor de la regla"],
      ["Incremental del modelo", rv.incremental_modelo, "Casos que agrega el bloque B"],
      ["Total del flujo propuesto", rv.total, "Inversión USD 9.570 · USD 5.960 por año"],
    ];
    cols.forEach(([t, q, sub], i) => {
      const x = 0.6 + i * 4.1, fill = i === 2 ? NAVY : LIGHT, ink = i === 2 ? WHITE : NAVY;
      card(s, x, 1.6, 3.9, 3.45, fill);
      text(s, t, { x: x + 0.3, y: 1.8, w: 3.3, h: 0.7, fontSize: 16, bold: true, color: ink });
      text(s, pct(q.roi_3anios, 1), { x: x + 0.3, y: 2.55, w: 3.3, h: 0.8, fontSize: 40, bold: true, color: i === 2 ? GOLD : STEEL });
      text(s, "ROI a 3 años · año tipo 2025", { x: x + 0.3, y: 3.35, w: 3.3, h: 0.35, fontSize: 12, color: i === 2 ? LINE : MUTED });
      text(s, `Beneficio ${usd(q.beneficio_anual)}/año · recupero ${num(q.recupero_meses)} meses`, { x: x + 0.3, y: 3.8, w: 3.3, h: 0.6, fontSize: 13, color: ink });
      text(s, sub, { x: x + 0.3, y: 4.45, w: 3.3, h: 0.5, fontSize: 12, color: i === 2 ? LINE : MUTED });
    });
    text(s, `Valor por posición reproducible del E2: ARS ${num(vb.capital_por_posicion_ars)}. Un acierto vale ${usd(vb.valor_vp_usd)}; una alerta falsa cuesta ${usd(vb.costo_fp_usd)}. En un año como 2026 el total llega a ${pct(rt.total.roi_3anios)}: es un techo, no la expectativa.`, { x: 0.6, y: 5.35, w: 12.13, h: 1.0, fontSize: 13, color: MUTED });
    s.addNotes(`GIANFRANCO. La economía cambió con las correcciones. La cátedra nos pidió usar el valor por posición reproducible del Entregable 2, 208 mil pesos, en lugar del del Entregable 1, y separar dos cosas: cuánto vale automatizar la lista con la regla, sin modelo, y cuánto agrega el modelo. En un año como 2025, automatizar la lista da un ROI a tres años de ${pct(rv.automatizacion_sin_modelo.roi_3anios, 1)}; el modelo agrega unos ${usd(rv.valor_incremental_modelo_anual)} por año, con un ROI propio de ${pct(rv.incremental_modelo.roi_3anios, 1)}; y el total recupera la inversión en ${num(rv.total.recupero_meses)} meses. En un año como 2026 los números son mucho mejores, pero lo tomamos como techo, no como expectativa.`);
  }

  // ================= 14 · Sensitivity =================
  {
    const s = content("Viabilidad y plan", "Dos supuestos mueven el resultado");
    speaker(s, "Gianfranco", "Coordinación");
    const rows = [
      ["Base: valor por posición del E2, desarrollo USD 3.000", rv.total],
      ["Desarrollo real: 3 meses de un científico de datos", rv.total_desarrollo_3a4_meses[0]],
      ["Desarrollo real: 4 meses de un científico de datos", rv.total_desarrollo_3a4_meses[1]],
      ["Valor por posición del E1 (no reproducible)", rv.total_valor_posicion_e1],
    ];
    text(s, "ROI a 3 años del flujo propuesto, año tipo 2025", { x: 0.6, y: 1.6, w: 7.9, h: 0.4, fontSize: 16, bold: true });
    rows.forEach(([l, q], i) => {
      const y = 2.2 + i * 1.02, pos = q.roi_3anios >= 0;
      card(s, 0.6, y, 7.9, 0.85);
      text(s, l, { x: 0.85, y: y + 0.12, w: 4.9, h: 0.6, fontSize: 14, valign: "middle" });
      pill(s, pct(q.roi_3anios, 1), 5.85, y + 0.22, 1.2, pos ? TEAL : CORAL, WHITE, 0.42);
      text(s, q.recupero_meses ? num(q.recupero_meses) + " meses" : "No recupera", { x: 7.15, y: y + 0.12, w: 1.25, h: 0.6, fontSize: 13, color: MUTED, valign: "middle" });
    });
    card(s, 8.85, 1.6, 3.88, 4.8);
    await iconCircle(s, "FaExclamationTriangle", 9.1, 1.85, 0.6, CORAL);
    text(s, "El límite del caso", { x: 9.1, y: 2.6, w: 3.4, h: 0.4, fontSize: 16, bold: true });
    text(s, "Con USD 80 a 134 de capital por posición, cada acierto vale USD 10 a 17. El proyecto rinde por volumen y por las horas ahorradas, no por el valor de cada caso. Por eso el modelo tiene que ganarse su lugar en el piloto.", { x: 9.1, y: 3.05, w: 3.4, h: 3.2, fontSize: 13 });
    s.addNotes(`GIANFRANCO. Fuimos honestos con la sensibilidad. Si el desarrollo cuesta lo que costaría de verdad, tres o cuatro meses de un científico de datos, el ROI a tres años pasa a ${pct(rv.total_desarrollo_3a4_meses[0].roi_3anios, 1)} y ${pct(rv.total_desarrollo_3a4_meses[1].roi_3anios, 1)}. Y si usáramos el valor por posición del Entregable 1, no se recupera. La cátedra lo dijo bien: con 80 a 134 dólares de capital por posición, cada acierto vale poco; el proyecto rinde por volumen y por las horas que ahorra. Sacamos además el criterio de recupero de 12 meses, que no venía de Casa Óga: usamos ROI a tres años mayor o igual a cero.`);
  }

  // ================= 15 · Legal & risks =================
  {
    const s = content("Viabilidad y plan", "Legal viable con condiciones; los riesgos, medidos");
    speaker(s, "Gianfranco", "Coordinación");
    card(s, 0.6, 1.6, 4.3, 4.8, NAVY, "legal");
    text(s, "Legal", { x: 0.9, y: 1.8, w: 3.7, h: 0.4, fontSize: 16, bold: true, color: LINE });
    text(s, "2,2", { x: 0.9, y: 2.2, w: 3.7, h: 0.9, fontSize: 48, bold: true, color: GOLD });
    text(s, [
      { text: "Sin datos personales (Ley 25.326 no se activa).", options: { bullet: true, breakLine: true } },
      { text: "Accesos por rol: las tiendas no ven costos.", options: { bullet: true, breakLine: true } },
      { text: "Adenda de confidencialidad y titularidad del código.", options: { bullet: true, breakLine: true } },
      { text: "Explicabilidad 2: aplica al bloque B; la regla se explica sola.", options: { bullet: true } },
    ], { x: 0.9, y: 3.2, w: 3.8, h: 3.0, fontSize: 13, color: WHITE, paraSpaceAfter: 6 });
    const risks = [
      ["Beneficio < USD 9.150 por año", "Beneficio trimestral < USD 2.288 dos veces", "Quedarse con la regla"],
      ["Datos inválidos o sin Ronda 3", "Archivos faltantes o claves desconocidas", "No publicar las filas afectadas"],
      ["El modelo no le gana a la regla", "Flujo ≤ cobertura en dos cohortes", "Sólo bloque A y reentrenar"],
    ];
    text(s, "Top 3 riesgos (escenario de referencia 2025)", { x: 5.2, y: 1.6, w: 7.5, h: 0.4, fontSize: 16, bold: true });
    risks.forEach(([r, sig, resp], i) => {
      const y = 2.15 + i * 1.42;
      card(s, 5.2, y, 7.53, 1.25);
      text(s, r, { x: 5.45, y: y + 0.15, w: 7.1, h: 0.4, fontSize: 15, bold: true });
      text(s, [{ text: "Señal: ", options: { bold: true } }, { text: sig + "   " }, { text: "Respuesta: ", options: { bold: true } }, { text: resp }], { x: 5.45, y: y + 0.62, w: 7.1, h: 0.5, fontSize: 13, color: MUTED });
    });
    s.addNotes("GIANFRANCO. Legalmente es viable con condiciones, 2,2: no hay datos personales, y el riesgo real es que costos y condiciones de proveedores lleguen a quien no corresponde; se resuelve con accesos por rol y una adenda de confidencialidad. Aclaramos que el 2 en explicabilidad aplica al modelo, no a la regla. Los riesgos ahora están construidos sobre el escenario de referencia, no el optimista: el primero es que el beneficio no llegue a los 9.150 dólares por año que hacen viable el proyecto. Cada riesgo tiene una señal medible y una respuesta.");
  }

  // ================= 16 · Plan =================
  {
    const s = content("Viabilidad y plan", "Plan: un mes de preparación y un piloto de seis");
    speaker(s, "Gianfranco", "Coordinación");
    const ph = [
      ["Semana 1-2", "Target aprobado y Ronda 3 incorporada", "Dataset v5 y reevaluación", NAVY],
      ["Semana 3-4", "Mantenedor, adenda, accesos y exportación", "Criterios de go-live", NAVY],
      ["Meses 1-3", "Tres cierres del piloto", "Adopción ≥ 60%", STEEL],
      ["Meses 4-6", "Cohortes maduradas a t+3", "Flujo > regla a igual cupo", STEEL],
      ["Mes 6", "Decisión de continuidad", "Carlos F. con el informe del piloto", GOLD],
    ];
    ph.forEach(([when, what, crit, col], i) => {
      const x = 0.6 + i * 2.45;
      s.addShape(pres.shapes.CHEVRON, { x, y: 1.75, w: 2.35, h: 0.75, fill: { color: col }, line: { type: "none" }, objectName: "phase" });
      text(s, when, { x: x + 0.3, y: 1.75, w: 1.8, h: 0.75, fontSize: 14, bold: true, color: i === 4 ? NAVY : WHITE, align: "center", valign: "middle" });
      text(s, what, { x, y: 2.75, w: 2.25, h: 0.9, fontSize: 14, bold: true });
      text(s, crit, { x, y: 3.65, w: 2.25, h: 0.8, fontSize: 13, color: MUTED });
    });
    card(s, 0.6, 4.7, 12.13, 1.7);
    text(s, "Criterios de go-live (sí / no)", { x: 0.9, y: 4.85, w: 11.5, h: 0.4, fontSize: 16, bold: true });
    text(s, "Dataset con la Ronda 3 y el flujo sigue ganándole a la regla · corrida real válida (5 archivos, 0 claves desconocidas) · mantenedor nombrado · adenda y accesos por rol · protocolo de decisión humana aprobado", { x: 0.9, y: 5.3, w: 11.5, h: 0.95, fontSize: 14 });
    s.addNotes("GIANFRANCO. El plan tiene dos partes. Cuatro semanas de preparación: aprobar el target, incorporar la Ronda 3 y reevaluar, nombrar al mantenedor, firmar la adenda, configurar los accesos y estandarizar la exportación. Después, un piloto de tres cierres; como el resultado se conoce tres meses después, las cohortes maduran entre los meses 4 y 6, y en el mes 6 Finanzas decide si continúa. El go-live tiene cinco criterios de sí o no. Una corrección de la cátedra: el desempeño ya no se da por cumplido con el test de 2026; se mide con las cohortes del piloto. Le devuelvo la palabra a Santiago.");
  }

  // ================= 17 · Close =================
  pres.addSection({ title: "Cierre" });
  {
    const s = pres.addSlide({ masterName: "DARK", sectionTitle: "Cierre" });
    text(s, "VEREDICTO", { x: 0.8, y: 1.3, w: 11, h: 0.4, fontSize: 14, bold: true, color: GOLD, charSpacing: 2 });
    s.addText("Viable con condiciones como piloto supervisado", { placeholder: "title" });
    const acts = [
      ["FaUserTie", "Nombrar al mantenedor y firmar la adenda con accesos por rol"],
      ["FaFileExport", "Estandarizar la exportación mensual de los cinco archivos"],
      ["FaDatabase", "Reconstruir el dataset con la Ronda 3 y repetir la evaluación"],
    ];
    for (let i = 0; i < acts.length; i++) {
      const x = 0.8 + i * 3.95;
      await iconCircle(s, acts[i][0], x, 4.0, 0.7, GOLD, HEX.dk1);
      text(s, acts[i][1], { x: x + 0.9, y: 4.0, w: 2.85, h: 1.1, fontSize: 15, color: WHITE });
    }
    text(s, "Si el modelo no le gana a la regla en el piloto, el proyecto sigue siendo útil con la lista automatizada y las horas ahorradas.", { x: 0.8, y: 5.6, w: 11.7, h: 0.7, fontSize: 15, italic: true, color: LINE });
    s.addNotes("SANTIAGO. Cerramos. Nuestra recomendación es avanzar con un piloto supervisado de tres cierres, sin compras nuevas. Antes de empezar hay tres acciones: nombrar al mantenedor y firmar la adenda con accesos por rol, estandarizar la exportación mensual y reconstruir el dataset con la Ronda 3. El riesgo residual es que la ventaja del modelo sea chica en la práctica, como en 2026; si pasa, el proyecto igual vale por la lista automatizada y las horas que ahorra, y el modelo se retira sin costo adicional. Gracias; quedamos para preguntas.");
  }

  await pres.writeFile({ fileName: OUT });
  console.log("OK", OUT);
}
build().catch((e) => { console.error(e); process.exit(1); });
