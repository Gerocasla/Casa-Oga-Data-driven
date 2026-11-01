// Builds the Entregable 3 oral-presentation deck (PowerPoint) from the compiled report figures.
// Run: NODE_PATH=<node_modules with pptxgenjs, react-icons, react-dom, sharp> node armar_pptx.js
// Then apply the theme colors: node <pptx skill>/scripts/apply_theme.js <out.pptx> theme.json
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");

const OUT = path.join(__dirname, "Casa-Oga-Entregable-3-Presentacion.pptx");

const THEME = {
  name: "Casa Oga E3",
  headFontFace: "Calibri",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1B2540", lt1: "FFFFFF", dk2: "0F1A33", lt2: "EEF1F6",
    accent1: "F2B705", accent2: "2A9D8F", accent3: "D9534F", accent4: "3D5A80",
    accent5: "5E6B85", accent6: "C9D1DE", hlink: "3D5A80", folHlink: "5E6B85",
  },
};
fs.writeFileSync(path.join(__dirname, "theme.json"), JSON.stringify(THEME, null, 2));
const HEX = THEME.colors;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.title = "Casa Óga · Entregable 3 · Grupo 1";
pres.author = "Grupo 1";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const NAVY = C.text1, DARK = C.text2, WHITE = C.background1, LIGHT = C.background2;
const GOLD = C.accent1, TEAL = C.accent2, CORAL = C.accent3, STEEL = C.accent4, MUTED = C.accent5, LINE = C.accent6;

// ---------- layouts ----------
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: WHITE },
  margin: [0.4, 0.6, 0.6, 0.6],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.42, w: 9.7, h: 0.85, fontSize: 30, bold: true, color: NAVY, align: "left", valign: "middle", margin: 0 }, text: "" } },
    { text: { text: "Casa Óga · Entregable 3 · Grupo 1", options: { x: 0.6, y: 7.0, w: 6, h: 0.3, fontSize: 10, color: MUTED, margin: 0 } } },
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

async function build() {
  // ================= 1 · Cover =================
  pres.addSection({ title: "Apertura" });
  {
    const s = pres.addSlide({ masterName: "DARK", sectionTitle: "Apertura" });
    text(s, "ENTREGABLE 3 · FACTIBILIDAD, MODELO Y DISEÑO DE LA SOLUCIÓN", { x: 0.8, y: 1.3, w: 11, h: 0.4, fontSize: 14, bold: true, color: GOLD, charSpacing: 2 });
    s.addText("Detección anticipada de inventario inmovilizado", { placeholder: "title" });
    text(s, "Casa Óga · Retail de Hogar y Decoración", { x: 0.8, y: 3.75, w: 11, h: 0.5, fontSize: 22, color: LINE });
    const team = [
      ["Gianfranco Di Claudio", "Coordinación"], ["Matías Fleischer", "Datos · calidad y preparación"],
      ["Simón Volpato Escandarani", "Datos · modelado y evaluación"], ["Gerónimo Fasce", "Visualización"],
      ["Santiago Javier Hernández", "Comunicación"],
    ];
    team.forEach(([n, r], i) => {
      const col = i < 3 ? 0 : 1, row = i < 3 ? i : i - 3;
      text(s, [
        { text: n, options: { bold: true, color: WHITE, fontSize: 15, breakLine: true } },
        { text: r, options: { color: LINE, fontSize: 12 } },
      ], { x: 0.8 + col * 4.6, y: 4.85 + row * 0.62, w: 4.4, h: 0.6 });
    });
    text(s, "Grupo 1 · 03/11/2026", { x: 9.6, y: 6.55, w: 2.95, h: 0.4, fontSize: 14, color: GOLD, align: "right", bold: true });
    s.addNotes("Santiago abre. Presenta el proyecto en una frase: queremos que Casa Óga detecte el stock que se va a inmovilizar tres meses antes de que pase, no en el conteo anual. Presenta al equipo y aclara que cada integrante expone la parte de la que es responsable.");
  }

  // ================= 2 · Problem =================
  {
    const s = content("Apertura", "Casa Óga detecta tarde el stock que no rota");
    speaker(s, "Santiago", "Comunicación");
    const stats = [
      ["FaBoxes", "882", "posiciones SKU–tienda con más de 12 meses de cobertura (ago-2026)"],
      ["FaMoneyBillWave", "ARS 184,1 M", "inmovilizados, valuados a costo"],
      ["FaClock", "480 h/año", "de armado manual del análisis en Excel"],
    ];
    for (let i = 0; i < stats.length; i++) {
      const y = 1.7 + i * 1.65;
      await iconCircle(s, stats[i][0], 0.6, y + 0.15, 0.8, NAVY);
      text(s, stats[i][1], { x: 1.65, y, w: 4.6, h: 0.75, fontSize: 40, bold: true, valign: "middle" });
      text(s, stats[i][2], { x: 1.65, y: y + 0.78, w: 4.6, h: 0.6, fontSize: 14, color: MUTED });
    }
    card(s, 6.8, 1.7, 5.93, 2.25, LIGHT);
    await iconCircle(s, "FaHourglassHalf", 7.1, 2.0, 0.6, MUTED);
    text(s, "Hoy", { x: 7.9, y: 2.0, w: 4.5, h: 0.6, fontSize: 20, bold: true, valign: "middle" });
    text(s, "El inmovilizado aparece en el conteo anual o cuando ya acumuló meses de costo de capital, góndola y depósito. La liquidación llega tarde y más profunda.", { x: 7.1, y: 2.75, w: 5.35, h: 1.1, fontSize: 14 });
    card(s, 6.8, 4.2, 5.93, 2.45, DARK);
    await iconCircle(s, "FaBell", 7.1, 4.5, 0.6, GOLD, HEX.dk2);
    text(s, "Lo que proponemos", { x: 7.9, y: 4.5, w: 4.6, h: 0.6, fontSize: 20, bold: true, color: WHITE, valign: "middle" });
    text(s, "Una lista mensual de hasta 600 posiciones a revisar (15 a 25 por tienda), tres meses antes de que superen 12 meses de cobertura. El modelo prioriza; las personas deciden.", { x: 7.1, y: 5.25, w: 5.35, h: 1.25, fontSize: 14, color: WHITE });
    s.addNotes("El problema no es que haya stock lento: es que se detecta tarde. A agosto de 2026 había 882 posiciones con más de 12 meses de cobertura, ARS 184 millones a costo. Proponemos anticiparlo: cada mes, una lista corta por tienda de lo que conviene revisar antes de que se inmovilice. Importante: el modelo no decide nada, ordena qué mirar primero.");
  }

  // ================= 3 · Recommendation =================
  {
    const s = content("Apertura", "Recomendamos un piloto supervisado");
    speaker(s, "Santiago", "Comunicación");
    const tiles = [
      ["FaCogs", "Técnica", "2,25", "Factibilidad media. Falta un responsable del modelo.", TEAL],
      ["FaBalanceScale", "Legal", "2,2", "Viable con condiciones: accesos por rol y confidencialidad.", TEAL],
      ["FaCoins", "Económica", "35–59 m", "de recupero, contra un máximo de 12. ROI 3 años: −13,7% a +0,9%.", CORAL],
      ["FaBrain", "Modelo", "71–77%", "de los casos detectados con 600 alertas por mes. Supera a la regla.", TEAL],
    ];
    for (let i = 0; i < tiles.length; i++) {
      const x = 0.6 + i * 3.07, [ic, lab, val, desc, col] = tiles[i];
      card(s, x, 1.65, 2.8, 3.05, LIGHT);
      await iconCircle(s, ic, x + 0.3, 1.95, 0.6, NAVY);
      text(s, lab, { x: x + 1.05, y: 1.95, w: 1.6, h: 0.6, fontSize: 16, bold: true, valign: "middle" });
      text(s, val, { x: x + 0.3, y: 2.75, w: 2.3, h: 0.75, fontSize: 34, bold: true, color: col, valign: "middle" });
      text(s, desc, { x: x + 0.3, y: 3.55, w: 2.3, h: 1.05, fontSize: 13, color: MUTED });
    }
    card(s, 0.6, 5.0, 12.13, 1.65, DARK);
    text(s, [
      { text: "Viable con condiciones como piloto supervisado; todavía no como inversión de expansión. ", options: { bold: true, color: GOLD } },
      { text: "Tres cierres mensuales sobre la infraestructura que ya existe. El ensamble pasa a ser el motor principal sólo si en el piloto supera a la regla con el mismo cupo de alertas.", options: { color: WHITE } },
    ], { x: 0.95, y: 5.2, w: 11.45, h: 1.25, fontSize: 16, valign: "middle" });
    s.addNotes("Arrancamos por la conclusión. Técnica y legalmente se puede: 2,25 y 2,2 sobre 3. El modelo funciona: detecta entre 71% y 77% de los casos con el cupo de 600 alertas. Lo que no cierra es la economía: el recupero tarda entre 35 y 59 meses. Por eso no pedimos una inversión grande: pedimos un piloto de tres meses, sin gasto adicional, para medir con datos propios si el modelo paga su costo.");
  }

  // ================= 4 · Team roles =================
  {
    const s = content("Apertura", "Un responsable por resultado");
    speaker(s, "Santiago", "Comunicación");
    const hdrY = 1.55;
    [["Integrante y rol", 1.55], ["Responsabilidad", 5.0], ["Entregable clave", 8.55], ["Expone", 11.0]].forEach(([t, x]) =>
      text(s, t.toUpperCase(), { x, y: hdrY, w: 3.2, h: 0.3, fontSize: 11, bold: true, color: MUTED, charSpacing: 1 }));
    const rows = [
      ["FaProjectDiagram", "Gianfranco Di Claudio", "Coordinación", "Controla avance, hitos y bloqueos; arma el plan.", "Plan de proyecto y minutas", "Economía, legal, go-live y plan"],
      ["FaDatabase", "Matías Fleischer", "Datos · calidad y preparación", "Limpieza, reglas del E2 y pipeline mensual.", "Dataset limpio y pipeline", "Factibilidad técnica y experimento"],
      ["FaBrain", "Simón Volpato Escandarani", "Datos · modelado y evaluación", "Baseline, ensamble, test final y ficha.", "Modelo y ficha del modelo", "Modelo"],
      ["FaChartBar", "Gerónimo Fasce", "Visualización", "Tablero por rol y gráficos finales.", "Tablero y gráficos", "Diseño de la solución"],
      ["FaBullhorn", "Santiago Javier Hernández", "Comunicación", "Narrativa y comunicación con el negocio.", "Presentación final", "Apertura y cierre"],
    ];
    for (let i = 0; i < rows.length; i++) {
      const y = 1.95 + i * 0.95, [ic, n, r, resp, ent, exp] = rows[i];
      if (i % 2 === 0) card(s, 0.6, y - 0.08, 12.13, 0.88, LIGHT, "row-band");
      await iconCircle(s, ic, 0.75, y + 0.06, 0.6, NAVY);
      text(s, [{ text: n, options: { bold: true, breakLine: true } }, { text: r, options: { fontSize: 12, color: MUTED } }], { x: 1.55, y, w: 3.3, h: 0.72, valign: "middle", fontSize: 14 });
      text(s, resp, { x: 5.0, y, w: 3.35, h: 0.72, valign: "middle", fontSize: 13 });
      text(s, ent, { x: 8.55, y, w: 2.3, h: 0.72, valign: "middle", fontSize: 13, bold: true });
      text(s, exp, { x: 11.0, y, w: 1.65, h: 0.72, valign: "middle", fontSize: 12, color: MUTED });
    }
    s.addNotes("Cada resultado tiene un dueño. Gianfranco coordina y es dueño del plan. Matías es dueño del dataset y del pipeline. Simón, del modelo y su ficha. Gerónimo, del tablero. Yo, de la narrativa. Cada uno va a explicar su parte en ese orden: datos, modelo, solución, viabilidad y plan.");
  }

  // ================= 5 · Technical feasibility =================
  pres.addSection({ title: "Datos y factibilidad técnica" });
  {
    const s = content("Datos y factibilidad técnica", "Técnicamente factible, con una condición");
    speaker(s, "Matías", "Datos · calidad");
    const conds = [
      ["Datos suficientes", 3, "51 meses de historia y 6.853 casos positivos. Las claves del target cruzan al 100%."],
      ["Calidad utilizable", 2, "0% de nulos en el target, pero 1,59% de duplicados y tres problemas estructurales que obligan a excluir variables."],
      ["Infraestructura", 2, "Python, GitHub y un tablero HTML alcanzan para el MVP. La integración entre sistemas es manual."],
      ["Capacidad humana", 2, "El equipo puede construir el modelo, pero Casa Óga no tiene área de datos ni responsable nombrado."],
    ];
    conds.forEach(([n, sc, ev], i) => {
      const y = 1.65 + i * 1.25;
      text(s, n, { x: 0.6, y, w: 5.5, h: 0.4, fontSize: 18, bold: true });
      dots(s, 6.45, y + 0.08, sc);
      text(s, ev, { x: 0.6, y: y + 0.45, w: 6.9, h: 0.7, fontSize: 13, color: MUTED });
    });
    card(s, 8.1, 1.65, 4.63, 5.0, DARK);
    text(s, "PROMEDIO", { x: 8.45, y: 1.95, w: 4, h: 0.3, fontSize: 12, bold: true, color: LINE, charSpacing: 2 });
    text(s, "2,25", { x: 8.45, y: 2.3, w: 4, h: 1.1, fontSize: 66, bold: true, color: GOLD, valign: "middle" });
    text(s, "Factibilidad media (rango 2,1 a 2,5)", { x: 8.45, y: 3.45, w: 4, h: 0.4, fontSize: 15, color: WHITE });
    await iconCircle(s, "FaUserTie", 8.45, 4.25, 0.55, CORAL);
    text(s, "Condición crítica", { x: 9.15, y: 4.25, w: 3.3, h: 0.55, fontSize: 15, bold: true, color: WHITE, valign: "middle" });
    text(s, "Nadie en Casa Óga está nombrado para sostener el modelo. Sin ese responsable, cambios como el de 2026 pasan sin detectarse.", { x: 8.45, y: 4.95, w: 3.95, h: 1.5, fontSize: 14, color: LINE });
    s.addNotes("Evaluamos cuatro condiciones de 1 a 3. Los datos no son el cuello de botella: hay 51 meses y casi 7 mil casos, y las fuentes del target cruzan sin pérdida. Calidad tiene 2 porque hay duplicados por la migración de 2024 y tres problemas que no se corrigen sin cambiar sistemas, así que esas variables se excluyeron. Lo que baja el score es la operación: integración manual y nadie designado para mantener el modelo. Esa es la condición que puede cambiar el veredicto.");
  }

  // ================= 6 · Experiment =================
  {
    const s = content("Datos y factibilidad técnica", "Un experimento que respeta el tiempo");
    speaker(s, "Matías", "Datos · calidad");
    card(s, 0.6, 1.6, 12.13, 1.15, LIGHT);
    await iconCircle(s, "FaBullseye", 0.85, 1.8, 0.75, NAVY);
    text(s, [
      { text: "Target: ", options: { bold: true } },
      { text: "1 si en t+3 (dentro de 3 meses) la posición SKU–tienda supera 12 meses de cobertura.", options: {} },
    ], { x: 1.85, y: 1.7, w: 10.7, h: 0.48, fontSize: 16, valign: "middle" });
    text(s, "Una fila por posición y mes · 201.306 filas · 60 variables calculables al cierre de t · prevalencia 3,4%", { x: 1.85, y: 2.2, w: 10.7, h: 0.4, fontSize: 13, color: MUTED });
    const segs = [
      ["Entrenamiento", "mar-22 a dic-24 · 2.466 casos · 2,5%", 4.9, STEEL],
      ["Embargo", "3 meses", 1.0, LINE],
      ["Validación", "abr-sep 25 · 854 · 2,2%", 2.35, TEAL],
      ["Embargo", "3 meses", 1.0, LINE],
      ["Test reservado", "ene-may 26 · 2.535 · 9,0%", 2.68, CORAL],
    ];
    let x = 0.6;
    text(s, "PARTICIÓN TEMPORAL", { x: 0.6, y: 3.05, w: 6, h: 0.3, fontSize: 11, bold: true, color: MUTED, charSpacing: 1 });
    segs.forEach(([n, d, w, col], i) => {
      const dark = col !== LINE;
      s.addShape(pres.shapes.RECTANGLE, { x, y: 3.4, w: w - 0.05, h: 0.95, fill: { color: col }, line: { type: "none" }, objectName: "partition-" + i });
      text(s, [{ text: n, options: { bold: true, breakLine: true, fontSize: dark ? 15 : 12 } }, { text: d, options: { fontSize: 11 } }],
        { x: x + 0.1, y: 3.4, w: w - 0.25, h: 0.95, valign: "middle", color: dark ? WHITE : NAVY });
      x += w;
    });
    text(s, "El test 2026 no se tocó hasta la evaluación final. El embargo evita que una etiqueta caiga en el bloque siguiente.", { x: 0.6, y: 4.45, w: 12, h: 0.35, fontSize: 12, color: MUTED, italic: true });
    text(s, "CONTROL DE FUGA DE INFORMACIÓN", { x: 0.6, y: 5.0, w: 6, h: 0.3, fontSize: 11, bold: true, color: MUTED, charSpacing: 1 });
    const leaks = [
      ["Excluido", "Ventas y stock de t+1 a t+3"],
      ["Excluido", "Precio, costo y margen del catálogo (el sistema pisa la historia)"],
      ["Excluido", "Presupuesto futuro (se actualiza con la venta real)"],
      ["Recalculado", "Liquidaciones, transferencias y OC sólo hasta t"],
    ];
    leaks.forEach(([tag, d], i) => {
      const cx = 0.6 + i * 3.07;
      card(s, cx, 5.4, 2.9, 1.25, LIGHT);
      pill(s, tag, cx + 0.2, 5.55, 1.35, tag === "Excluido" ? CORAL : STEEL);
      text(s, d, { x: cx + 0.2, y: 5.98, w: 2.55, h: 0.62, fontSize: 12 });
    });
    s.addNotes("La pregunta es simple: qué posiciones van a superar 12 meses de cobertura en tres meses. Como los datos son en el tiempo, entrenamos con el pasado y evaluamos con el futuro, con tres meses de embargo entre bloques para que no se filtre ninguna etiqueta. El test de 2026 quedó guardado hasta el final. Y revisamos cada variable: si no se conoce al cierre del mes, se excluye o se recalcula. Ojo con 2026: la prevalencia sube a 9%, cuatro veces más que en validación.");
  }

  // ================= 7 · Baseline & metric =================
  pres.addSection({ title: "Modelo" });
  {
    const s = content("Modelo", "La regla actual detecta 3 de cada 10 casos");
    speaker(s, "Simón", "Modelado");
    text(s, "BASELINE · VALIDACIÓN 2025", { x: 0.6, y: 1.6, w: 5.5, h: 0.3, fontSize: 11, bold: true, color: MUTED, charSpacing: 1 });
    text(s, "Alertar toda posición cuya cobertura actual ya supera 12 meses. Se calcula hoy en Excel.", { x: 0.6, y: 1.95, w: 5.6, h: 0.7, fontSize: 15 });
    s.addChart(pres.charts.DOUGHNUT, [{ name: "Casos reales", labels: ["Detectados", "Omitidos"], values: [258, 596] }], {
      x: 0.6, y: 2.75, w: 2.9, h: 2.9, holeSize: 68, chartColors: [HEX.accent2, HEX.lt2], showLegend: false, showValue: false, showPercent: false, showLabel: false,
      dataLabelFontFace: "+mn-lt", legendFontFace: "+mn-lt", altText: "Regla de cobertura: 258 de 854 casos detectados en validación",
    });
    text(s, "30%", { x: 0.6, y: 3.7, w: 2.9, h: 0.65, fontSize: 32, bold: true, align: "center", valign: "middle" });
    text(s, "recall", { x: 0.6, y: 4.3, w: 2.9, h: 0.3, fontSize: 12, color: MUTED, align: "center" });
    [["258 de 854", "casos reales detectados"], ["24,6%", "de precisión"], ["175", "alertas por mes"]].forEach(([v, l], i) => {
      text(s, [{ text: v, options: { bold: true, fontSize: 22, breakLine: true } }, { text: l, options: { fontSize: 12, color: MUTED } }], { x: 3.75, y: 2.95 + i * 0.9, w: 2.6, h: 0.8 });
    });
    text(s, "Lejos de la meta del negocio: recall ≥ 75%.", { x: 0.6, y: 5.95, w: 5.8, h: 0.4, fontSize: 14, bold: true, color: CORAL });
    card(s, 6.9, 1.6, 5.83, 5.05, DARK);
    await iconCircle(s, "FaListOl", 7.2, 1.9, 0.65, GOLD, HEX.dk2);
    text(s, "Métrica principal: Recall@600", { x: 8.0, y: 1.9, w: 4.5, h: 0.65, fontSize: 19, bold: true, color: WHITE, valign: "middle" });
    text(s, [
      { text: "La cadena absorbe unas 600 intervenciones por mes (15 a 25 por tienda).", options: { bullet: true, breakLine: true } },
      { text: "Medimos cuántos casos reales caen dentro de las 600 posiciones de mayor riesgo de cada mes.", options: { bullet: true, breakLine: true } },
      { text: "Comparamos siempre a igual cupo: más alertas siempre detectan más, pero cuestan más trabajo.", options: { bullet: true, breakLine: true } },
      { text: "El falso negativo es el error caro: su costo se acumula mes a mes.", options: { bullet: true } },
    ], { x: 7.2, y: 2.8, w: 5.25, h: 3.6, fontSize: 15, color: WHITE, paraSpaceAfter: 10 });
    s.addNotes("Todo modelo tiene que ganarle a algo que el negocio ya pueda hacer. Ese piso es la regla: cobertura actual mayor a 12 meses. En validación detecta 258 de 854 casos, un 30%. Para comparar usamos Recall@600: cuántos casos reales caen en las 600 alertas mensuales que la operación puede trabajar. Comparamos siempre con el mismo cupo, porque si no, gana el que más alerta.");
  }

  // ================= 8 · Ensemble =================
  {
    const s = content("Modelo", "El ensamble supera a la regla a igual cupo");
    speaker(s, "Simón", "Modelado");
    const labels = ["Regla por cobertura", "CatBoost", "LightGBM", "XGBoost", "HistGradientBoosting", "ExtraTrees", "LightGBM Ranker", "Ensamble final"];
    const vals = [52.46, 66.74, 68.03, 68.38, 68.5, 68.5, 68.85, 70.96];
    const only = (pred) => vals.map((v, i) => (pred(i) ? v : 0));
    s.addChart(pres.charts.BAR, [
      { name: "Regla", labels, values: only((i) => i === 0) },
      { name: "Modelos individuales", labels, values: only((i) => i > 0 && i < 7) },
      { name: "Ensamble", labels, values: only((i) => i === 7) },
    ], {
      ...CHART_BASE(), x: 0.5, y: 1.55, w: 7.4, h: 5.2, barDir: "bar", barGrouping: "stacked", barGapWidthPct: 45,
      chartColors: [HEX.accent3, HEX.accent5, HEX.accent2], showLegend: false,
      showValue: true, dataLabelPosition: "inEnd", dataLabelColor: "FFFFFF", dataLabelFormatCode: "0.0\"%\";;;",
      valAxisHidden: true, valAxisMinVal: 0, valAxisMaxVal: 80, valGridLine: { style: "none" },
      showTitle: true, title: "Recall@600 en validación 2025 (%)", titleFontFace: "+mn-lt", titleFontSize: 13, titleColor: HEX.dk1,
      altText: "Recall@600 en validación: regla 52,5%, modelos individuales 66,7% a 68,9%, ensamble 71,0%",
    });
    const calls = [
      ["FaPlusCircle", "+158 casos", "frente a la regla con el mismo cupo: 606 contra 448 de 854.", TEAL],
      ["FaLayerGroup", "3 modelos", "HistGradientBoosting + ExtraTrees + LightGBM, promediando su ranking mensual.", NAVY],
      ["FaExclamationTriangle", "Sobreajuste", "99,7% de recall en entrenamiento contra 71,0% en validación: se usa con revisión humana.", CORAL],
    ];
    for (let i = 0; i < calls.length; i++) {
      const y = 1.7 + i * 1.7, [ic, h, d, col] = calls[i];
      await iconCircle(s, ic, 8.3, y, 0.65, col);
      text(s, h, { x: 9.15, y, w: 3.6, h: 0.5, fontSize: 22, bold: true, valign: "middle" });
      text(s, d, { x: 9.15, y: y + 0.55, w: 3.55, h: 0.95, fontSize: 13, color: MUTED });
    }
    s.addNotes("Probamos siete familias de árboles con validación temporal y el test sin tocar. Individualmente todos rondan el 68%. El ensamble de tres llega al 71%: 606 de 854 casos, 158 más que la regla con el mismo cupo. Pero hay que decirlo: en entrenamiento llega casi al 100%, así que hay sobreajuste. Por eso no lo usamos solo ni sin revisión humana.");
  }

  // ================= 9 · Final test =================
  {
    const s = content("Modelo", "En el test 2026 el modelo generaliza");
    speaker(s, "Simón", "Modelado");
    const labels = ["Regla fija", "Ensamble con el cupo de la regla", "Regla ordenada, Top-600", "Ensamble, Top-600"];
    s.addChart(pres.charts.BAR, [
      { name: "Validación 2025", labels, values: [30.2, 37.9, 52.5, 71.0] },
      { name: "Test 2026", labels, values: [40.8, 42.1, 69.9, 76.9] },
    ], {
      ...CHART_BASE(), x: 0.5, y: 1.55, w: 7.6, h: 5.2, barDir: "col", barGrouping: "clustered", barGapWidthPct: 60,
      chartColors: [HEX.accent5, HEX.accent2], showLegend: true, legendPos: "b", legendFontColor: HEX.accent5,
      showValue: true, dataLabelPosition: "inEnd", dataLabelColor: "FFFFFF", dataLabelFormatCode: "0.0\"%\"",
      valAxisHidden: true, valAxisMinVal: 0, valAxisMaxVal: 85, valGridLine: { style: "none" },
      showTitle: true, title: "Recall por método y período (%)", titleFontFace: "+mn-lt", titleFontSize: 13, titleColor: HEX.dk1,
      altText: "Recall de regla y ensamble en validación 2025 y test 2026",
    });
    text(s, "76,9%", { x: 8.5, y: 1.65, w: 2.1, h: 0.8, fontSize: 38, bold: true, color: TEAL, valign: "middle" });
    text(s, "recall en test", { x: 8.5, y: 2.45, w: 2.1, h: 0.3, fontSize: 12, color: MUTED });
    text(s, "65,0%", { x: 10.65, y: 1.65, w: 2.1, h: 0.8, fontSize: 38, bold: true, color: TEAL, valign: "middle" });
    text(s, "precisión en test", { x: 10.65, y: 2.45, w: 2.1, h: 0.3, fontSize: 12, color: MUTED });
    card(s, 8.5, 3.05, 4.23, 1.55, LIGHT);
    text(s, [
      { text: "Pero la ventaja se achica", options: { bold: true, breakLine: true, fontSize: 15 } },
      { text: "A igual cupo, +26% de aciertos en 2025 y sólo +3% en 2026: un año más fácil, con 9% de positivos y la cobertura sola en AUC 0,94.", options: { fontSize: 13, color: MUTED } },
    ], { x: 8.75, y: 3.12, w: 3.8, h: 1.41, valign: "middle" });
    card(s, 8.5, 4.8, 4.23, 1.85, DARK);
    text(s, [
      { text: "Desempeño esperado, como rango", options: { bold: true, color: GOLD, breakLine: true, fontSize: 15 } },
      { text: "Recall 71% a 77%", options: { color: WHITE, fontSize: 20, bold: true, breakLine: true } },
      { text: "Precisión 17% a 65%", options: { color: WHITE, fontSize: 20, bold: true } },
    ], { x: 8.75, y: 4.95, w: 3.8, h: 1.55, valign: "middle" });
    s.addNotes("Evaluamos una sola vez sobre el test de 2026, sin reajustar nada. El ensamble detecta el 77% de los casos con una precisión del 65%. Como pidió la cátedra, mostramos regla y modelo por separado en cada período. El modelo gana en los dos años, pero en 2026 la ventaja es chica, porque fue un año más fácil: cuatro veces más positivos. Por eso no prometemos un número: informamos un rango.");
  }

  // ================= 10 · Explainability =================
  {
    const s = content("Modelo", "Cada alerta se puede explicar");
    speaker(s, "Simón", "Modelado");
    const labels = ["Venta promedio 12 m", "Cobertura actual", "Subcategoría", "Unidades vendidas 6 m", "Variabilidad de la venta 12 m"];
    s.addChart(pres.charts.BAR, [{ name: "Importancia", labels, values: [5.3, 8.6, 8.9, 12.1, 23.6] }], {
      ...CHART_BASE(), x: 0.5, y: 1.55, w: 6.6, h: 4.0, barDir: "bar", barGapWidthPct: 50, chartColors: [HEX.accent4], showLegend: false,
      showValue: true, dataLabelPosition: "inEnd", dataLabelColor: "FFFFFF", dataLabelFormatCode: "0.0\"%\"",
      valAxisHidden: true, valAxisMinVal: 0, valGridLine: { style: "none" },
      showTitle: true, title: "Variables con más peso (gain de LightGBM, %)", titleFontFace: "+mn-lt", titleFontSize: 13, titleColor: HEX.dk1,
      altText: "Importancia de variables: variabilidad de la venta 23,6%, unidades 6 meses 12,1%, subcategoría 8,9%, cobertura 8,6%, venta promedio 5,3%",
    });
    text(s, "La señal está en la demanda y el stock, no en variables sospechosas de fuga. La importancia no implica causalidad.", { x: 0.6, y: 5.7, w: 6.4, h: 0.8, fontSize: 13, color: MUTED });
    card(s, 7.45, 1.6, 5.28, 3.0, LIGHT);
    await iconCircle(s, "FaSearch", 7.7, 1.85, 0.6, NAVY);
    text(s, "Así se lee una alerta real", { x: 8.45, y: 1.85, w: 4.1, h: 0.6, fontSize: 17, bold: true, valign: "middle" });
    text(s, [
      { text: "SKU00206 · tienda T12 · Cocina y mesa · abr-2025", options: { bold: true, breakLine: true } },
      { text: "4 unidades en stock, 0 vendidas en 6 meses y 5 meses sin ventas. Los tres modelos la ponen arriba del ranking: entra en el Top-600. A los 3 meses superó 12 meses de cobertura.", options: { color: MUTED } },
    ], { x: 7.7, y: 2.6, w: 4.85, h: 1.9, fontSize: 14 });
    card(s, 7.45, 4.8, 5.28, 1.85, DARK);
    text(s, [
      { text: "Lo que el modelo NO hace", options: { bold: true, color: GOLD, breakLine: true } },
      { text: "No ordena liquidar. No evalúa encargados ni tiendas. No es una probabilidad. Rinde menos en Cocina y mesa (61,8%, −9 pp).", options: { color: WHITE } },
    ], { x: 7.75, y: 4.95, w: 4.75, h: 1.6, fontSize: 14, valign: "middle" });
    s.addNotes("Explicabilidad: las variables que más pesan tienen sentido de negocio. Variabilidad de la venta, unidades vendidas recientes, subcategoría y cobertura. Un ejemplo real: un SKU de cocina en la tienda 12, con stock y seis meses sin vender; el modelo lo marcó y a los tres meses efectivamente se inmovilizó. Y la ficha del modelo deja claro para qué no sirve: no liquida solo, no evalúa personas y no es una probabilidad calibrada.");
  }

  // ================= 11 · Alternatives =================
  pres.addSection({ title: "Diseño de la solución" });
  {
    const s = content("Diseño de la solución", "Regla + modelo, con decisión humana");
    speaker(s, "Gerónimo", "Visualización");
    const alts = [
      ["FaTimes", "No hacer nada", "Nada: la detección sigue en el conteo anual.", "No", CORAL],
      ["FaDesktop", "Tablero descriptivo", "Muestra la cobertura actual por tienda, pero no anticipa.", "Sí · canal", TEAL],
      ["FaRulerHorizontal", "Regla de negocio", "Estable, explicable y la más precisa. No ve lo que aún no llegó a 12 meses.", "Sí · bloque A", TEAL],
      ["FaBrain", "Modelo predictivo", "Anticipa lo que todavía no llegó. Tiene sobreajuste y ventaja chica en 2026.", "Sí · bloque B", TEAL],
      ["FaRobot", "Automatizar la decisión", "Se automatiza la lista, no la decisión: necesita contexto comercial.", "Parcial", GOLD],
    ];
    for (let i = 0; i < alts.length; i++) {
      const x = 0.6 + i * 2.47, [ic, n, d, v, col] = alts[i];
      card(s, x, 1.65, 2.27, 3.65, LIGHT);
      await iconCircle(s, ic, x + 0.25, 1.9, 0.6, NAVY);
      text(s, n, { x: x + 0.25, y: 2.65, w: 1.85, h: 0.7, fontSize: 15, bold: true });
      text(s, d, { x: x + 0.25, y: 3.35, w: 1.85, h: 1.35, fontSize: 12, color: MUTED });
      pill(s, v, x + 0.25, 4.78, 1.77, col, col === GOLD ? NAVY : WHITE);
    }
    card(s, 0.6, 5.55, 5.93, 1.1, DARK);
    text(s, [{ text: "Bloque A · regla: ", options: { bold: true, color: GOLD } }, { text: "cobertura > 12 meses, ordenada por capital inmovilizado.", options: { color: WHITE } }], { x: 0.85, y: 5.6, w: 5.5, h: 1.0, fontSize: 14, valign: "middle" });
    card(s, 6.8, 5.55, 5.93, 1.1, DARK);
    text(s, [{ text: "Bloque B · ensamble: ", options: { bold: true, color: GOLD } }, { text: "completa el cupo hasta 600 con lo que la regla todavía no ve.", options: { color: WHITE } }], { x: 7.05, y: 5.6, w: 5.5, h: 1.0, fontSize: 14, valign: "middle" });
    s.addNotes("Comparamos el modelo con alternativas más simples. No hacer nada no es opción. Un tablero sirve como canal, pero no anticipa. La regla es estable y explicable, así que es la base: bloque A. El modelo agrega lo que la regla todavía no ve: bloque B, completando el cupo de 600. Y automatizamos el armado de la lista, nunca la decisión.");
  }

  // ================= 12 · Monthly flow =================
  {
    const s = content("Diseño de la solución", "Un ciclo mensual de cinco días");
    speaker(s, "Gerónimo", "Visualización");
    const steps = [
      ["FaFileExport", "Ingesta", "Días 1–3", "5 archivos con clave fija; 0 claves desconocidas."],
      ["FaBroom", "Preparación", "Días 3–4", "Reglas de limpieza del E2, 60 variables y bitácora con hash."],
      ["FaCalculator", "Scoring", "Día 4", "Bloque A (regla) + bloque B (ensamble) hasta 600."],
      ["FaChartBar", "Entrega", "Día 5", "Tablero y planilla por rol en SharePoint."],
      ["FaHandshake", "Decisión", "2–4 semanas", "La tienda propone; Comercial y Compras autorizan."],
      ["FaSyncAlt", "Aprendizaje", "t+3", "Se mide modelo contra regla y se reentrena cada trimestre."],
    ];
    for (let i = 0; i < steps.length; i++) {
      const x = 0.6 + i * 2.06, [ic, n, when, d] = steps[i];
      card(s, x, 1.7, 1.86, 3.3, i === 2 ? DARK : LIGHT);
      const dark = i === 2;
      text(s, String(i + 1).padStart(2, "0"), { x: x + 0.2, y: 1.85, w: 0.8, h: 0.4, fontSize: 14, bold: true, color: dark ? GOLD : MUTED });
      await iconCircle(s, ic, x + 1.1, 1.85, 0.55, dark ? GOLD : NAVY, dark ? HEX.dk2 : "FFFFFF");
      text(s, n, { x: x + 0.2, y: 2.6, w: 1.5, h: 0.4, fontSize: 16, bold: true, color: dark ? WHITE : NAVY });
      text(s, when, { x: x + 0.2, y: 3.0, w: 1.5, h: 0.3, fontSize: 12, bold: true, color: dark ? GOLD : TEAL });
      text(s, d, { x: x + 0.2, y: 3.4, w: 1.5, h: 1.5, fontSize: 14, color: dark ? LINE : MUTED });
      if (i < steps.length - 1) {
        s.addShape(pres.shapes.LINE, { x: x + 1.88, y: 3.47, w: 0.16, h: 0, line: { color: LINE, width: 2, endArrowType: "triangle" }, objectName: "flow-arrow" });
      }
    }
    // Feedback loop from step 6 back to step 3.
    const yc = 5.0, yb = 5.3;
    s.addShape(pres.shapes.LINE, { x: 11.83, y: yc, w: 0, h: yb - yc, line: { color: TEAL, width: 1.75, dashType: "dash" }, objectName: "feedback-down" });
    s.addShape(pres.shapes.LINE, { x: 5.65, y: yb, w: 11.83 - 5.65, h: 0, line: { color: TEAL, width: 1.75, dashType: "dash" }, objectName: "feedback-across" });
    s.addShape(pres.shapes.LINE, { x: 5.65, y: yc, w: 0, h: yb - yc, line: { color: TEAL, width: 1.75, dashType: "dash", endArrowType: "triangle" }, flipV: true, objectName: "feedback-up" });
    text(s, "Las etiquetas reales, maduradas a t+3, vuelven para medir y reentrenar", { x: 5.75, y: 5.4, w: 6.0, h: 0.4, fontSize: 13, color: TEAL, italic: true, align: "center" });
    text(s, [
      { text: "Responsables en el proyecto: ", options: { bold: true } },
      { text: "Matías (ingesta y preparación) · Simón (scoring) · Gerónimo (tablero). En Casa Óga: un mantenedor del pipeline y Lucía O. como dueña funcional.", options: { color: MUTED } },
    ], { x: 0.6, y: 6.0, w: 12.1, h: 0.6, fontSize: 14 });
    s.addNotes("Así funciona cada mes. Del día 1 al 3 llegan cinco archivos con formato fijo y se controla que estén completos. Se limpian con las reglas del Entregable 2 y se calculan las variables. El día 4 corre el scoring: primero la regla, después el ensamble completa el cupo. El día 5 cada rol ve su tablero. La tienda propone la acción y Comercial y Compras autorizan. A los tres meses sabemos qué pasó de verdad, y eso vuelve para medir y reentrenar.");
  }

  // ================= 13 · Who sees what =================
  {
    const s = content("Diseño de la solución", "Cada rol ve solo lo que necesita");
    speaker(s, "Gerónimo", "Visualización");
    card(s, 0.6, 1.6, 7.2, 5.05, LIGHT);
    await iconCircle(s, "FaStore", 0.85, 1.8, 0.55, NAVY);
    text(s, "Vista de tienda · T12 · alertas del mes", { x: 1.55, y: 1.8, w: 4.1, h: 0.55, fontSize: 16, bold: true, valign: "middle" });
    pill(s, "Maqueta ilustrativa", 5.65, 1.9, 1.95, MUTED);
    const hdr = ["SKU", "Cobertura", "Ventas 6 m", "Bloque", "Motivo"];
    const rows = [
      ["SKU00206", "Sin ventas", "0", "B", "5 meses sin vender"],
      ["SKU00418", "14,2 m", "3", "A", "Cobertura > 12 meses"],
      ["SKU00733", "13,1 m", "5", "A", "Cobertura > 12 meses"],
      ["SKU00091", "9,8 m", "7", "B", "Venta en caída"],
      ["SKU00560", "8,4 m", "6", "B", "OC pendiente + venta baja"],
    ];
    const tbl = [hdr.map((h) => ({ text: h, options: { bold: true, color: "FFFFFF", fill: { color: HEX.dk1 } } }))]
      .concat(rows.map((r) => r.map((c, j) => ({ text: c, options: { color: HEX.dk1, fill: { color: "FFFFFF" }, bold: j === 3 } }))));
    s.addTable(tbl, { x: 0.85, y: 2.6, w: 6.7, colW: [1.25, 1.2, 1.15, 0.85, 2.25], fontSize: 12, fontFace: "Calibri", border: { type: "solid", pt: 0.75, color: HEX.lt2 }, rowH: 0.42, margin: 0.06 });
    text(s, "Sin costos ni datos de otras tiendas. Cada fila se resuelve como liquidar, transferir, frenar compras o desestimar con motivo.", { x: 0.85, y: 5.35, w: 6.7, h: 0.8, fontSize: 13, color: MUTED });
    const users = [
      ["FaUserTie", "María G. · Comercial", "Resumen por categoría; autoriza liquidaciones."],
      ["FaTruck", "Diego P. · Compras", "SKUs en riesgo con OC y costo; frena compras."],
      ["FaCoins", "Carlos F. · Finanzas", "Valor recuperado y horas; decide continuidad."],
      ["FaUsers", "Lucía O. · Operaciones", "Lista consolidada; coordina y transfiere."],
      ["FaStore", "28 tiendas", "Su lista de 15 a 25 posiciones, sin costos."],
    ];
    for (let i = 0; i < users.length; i++) {
      const y = 1.65 + i * 1.0, [ic, n, d] = users[i];
      await iconCircle(s, ic, 8.1, y + 0.08, 0.55, i === 4 ? GOLD : NAVY, i === 4 ? HEX.dk2 : "FFFFFF");
      text(s, [{ text: n, options: { bold: true, breakLine: true, fontSize: 14 } }, { text: d, options: { fontSize: 12, color: MUTED } }], { x: 8.8, y, w: 3.95, h: 0.85, valign: "middle" });
    }
    s.addNotes("La salida del modelo llega a cada persona con lo que necesita para decidir y nada más. La tienda ve su lista de 15 a 25 posiciones con un motivo legible, sin costos ni otras tiendas. Compras ve OC y costos; Finanzas, el valor recuperado; Operaciones, el consolidado. La tabla es una maqueta para mostrar el formato, no datos reales salvo el primer SKU.");
  }

  // ================= 14 · Monitoring =================
  {
    const s = content("Diseño de la solución", "Cómo sabemos si sigue funcionando");
    speaker(s, "Gerónimo", "Visualización");
    [["Qué se mira", 1.55], ["Umbral de alerta", 5.6], ["Qué hacemos", 9.05]].forEach(([t, x]) =>
      text(s, t.toUpperCase(), { x, y: 1.55, w: 3.3, h: 0.3, fontSize: 11, bold: true, color: MUTED, charSpacing: 1 }));
    const mon = [
      ["FaDatabase", "Calidad de los datos", "Cada cierre", "Menos de 5 archivos, claves desconocidas o stock negativo en alertas", "No se publican esas filas; se corrigen antes"],
      ["FaBullseye", "Desempeño del modelo", "Mensual, a t+3", "Recall@600 < 60% o el modelo no supera a la regla dos cierres seguidos", "Sólo bloque A y reentrenar"],
      ["FaRandom", "Cambio en los datos", "Mensual", "Mediana de cobertura varía > 20% o prevalencia fuera de 2,2%–9,0%", "Alertas provisionales; adelantar reentrenamiento"],
      ["FaUserCheck", "Adopción", "Mensual", "Menos de 60% de alertas con acción registrada", "Revisar motivos con tiendas; ajustar cupo"],
      ["FaChartLine", "Impacto de negocio", "Trimestral", "Beneficio anualizado < USD 9.150 o ahorro de horas < 70%", "Congelar expansión y recalcular"],
    ];
    for (let i = 0; i < mon.length; i++) {
      const y = 1.95 + i * 0.95, [ic, n, f, th, act] = mon[i];
      if (i % 2 === 0) card(s, 0.6, y - 0.08, 12.13, 0.88, LIGHT, "row-band");
      await iconCircle(s, ic, 0.75, y + 0.06, 0.6, NAVY);
      text(s, [{ text: n, options: { bold: true, breakLine: true } }, { text: f, options: { fontSize: 12, color: MUTED } }], { x: 1.55, y, w: 3.8, h: 0.72, valign: "middle", fontSize: 14 });
      text(s, th, { x: 5.6, y, w: 3.25, h: 0.72, valign: "middle", fontSize: 12, color: CORAL, bold: true });
      text(s, act, { x: 9.05, y, w: 3.55, h: 0.72, valign: "middle", fontSize: 13 });
    }
    s.addNotes("Un modelo en producción se degrada si nadie lo mira. Medimos cinco cosas, cada una con un umbral y una acción. La más importante: si el Recall@600 cae por debajo de 60% o el modelo deja de ganarle a la regla, publicamos sólo la regla y reentrenamos. Y si el beneficio no llega al equilibrio de USD 9.150 por año, se congela la expansión.");
  }

  // ================= 15 · Economics =================
  pres.addSection({ title: "Viabilidad y plan" });
  {
    const s = content("Viabilidad y plan", "La economía todavía no cierra");
    speaker(s, "Gianfranco", "Coordinación");
    [["USD 9.570", "inversión inicial"], ["USD 5.960", "de mantenimiento por año"], ["USD 7.899–9.230", "de beneficio esperado por año"]].forEach(([v, l], i) => {
      card(s, 0.6 + i * 4.1, 1.6, 3.93, 1.25, LIGHT);
      text(s, [{ text: v, options: { bold: true, fontSize: 26, breakLine: true } }, { text: l, options: { fontSize: 13, color: MUTED } }], { x: 0.85 + i * 4.1, y: 1.7, w: 3.5, h: 1.05, valign: "middle" });
    });
    s.addChart(pres.charts.BAR, [{
      name: "ROI a 3 años", labels: ["Conservador", "Esperado (E2)", "Esperado · validación", "Esperado · test", "Optimista"], values: [-45.6, -19.3, -13.7, 0.9, 27.1],
    }], {
      ...CHART_BASE(), x: 0.5, y: 3.05, w: 7.5, h: 3.7, barDir: "col", barGapWidthPct: 55, chartColors: [HEX.accent2], invertedColors: [HEX.accent3], showLegend: false,
      showValue: true, dataLabelPosition: "outEnd", dataLabelColor: HEX.dk1, dataLabelFormatCode: "+0.0\"%\";−0.0\"%\"",
      valAxisHidden: true, valAxisMinVal: -55, valAxisMaxVal: 35, valGridLine: { style: "none" }, catAxisLabelPos: "low",
      showTitle: true, title: "ROI a 3 años por escenario (%)", titleFontFace: "+mn-lt", titleFontSize: 13, titleColor: HEX.dk1,
      altText: "ROI a 3 años: conservador −45,6%, esperado −19,3%, esperado con Etapa 4 entre −13,7% y +0,9%, optimista +27,1%",
    });
    card(s, 8.3, 3.05, 4.43, 3.6, DARK);
    text(s, "35–59", { x: 8.6, y: 3.25, w: 3.9, h: 0.95, fontSize: 54, bold: true, color: GOLD, valign: "middle" });
    text(s, "meses de recupero en el escenario esperado, contra un máximo propuesto de 12", { x: 8.6, y: 4.2, w: 3.9, h: 0.75, fontSize: 14, color: WHITE });
    text(s, "Entre el 44% y el 51% del beneficio es tiempo liberado: sólo es ahorro si evita costos reales. Equilibrio a 3 años: USD 9.150 por año.", { x: 8.6, y: 5.1, w: 3.9, h: 1.4, fontSize: 13, color: LINE });
    s.addNotes("La inversión entra holgada en el presupuesto de USD 30.000: 9.570 iniciales y casi 6.000 por año. El problema es el retorno. Con los aciertos del test, el escenario esperado queda entre −13,7% y +0,9% a tres años, y el recupero entre 35 y 59 meses. Además, casi la mitad del beneficio es tiempo liberado, que sólo vale si evita un costo real. Por eso no recomendamos expandir: recomendamos un piloto que mida el valor recuperado de verdad.");
  }

  // ================= 16 · Legal & risks =================
  {
    const s = content("Viabilidad y plan", "Legal viable; tres riesgos a vigilar");
    speaker(s, "Gianfranco", "Coordinación");
    text(s, "FACTIBILIDAD LEGAL · 2,2 · VIABLE CON CONDICIONES", { x: 0.6, y: 1.6, w: 6, h: 0.3, fontSize: 11, bold: true, color: MUTED, charSpacing: 1 });
    const legal = [
      ["Datos personales", 3, "No se usan: sólo SKU, tienda y mes."],
      ["Seguridad y accesos", 2, "Matriz por rol en SharePoint y MFA."],
      ["Trazabilidad fiscal", 2, "CSV originales, hash y bitácora del ETL."],
      ["Contratos externos", 2, "Adenda de confidencialidad sin firmar."],
      ["Explicabilidad", 2, "Ranking trazable; no liquida solo."],
    ];
    legal.forEach(([n, sc, d], i) => {
      const y = 2.05 + i * 0.92;
      text(s, [{ text: n, options: { bold: true, breakLine: true, fontSize: 15 } }, { text: d, options: { fontSize: 12, color: MUTED } }], { x: 0.6, y, w: 4.4, h: 0.8, valign: "middle" });
      dots(s, 5.0, y + 0.29, sc);
    });
    const risks = [
      ["FaCoins", "Los ahorros no se materializan", "Señal: < 80% de alertas con acción u horas ahorradas por debajo de lo previsto.", "Carlos F. congela la expansión y recalcula."],
      ["FaDatabase", "Stock o maestros inconsistentes", "Señal: archivo ausente, clave desconocida o stock negativo en una alerta.", "Esas filas no se publican hasta corregirse."],
      ["FaExclamationTriangle", "Sobreajuste y drift del ensamble", "Señal: Recall@600 < 60% o una categoría 15 pp debajo del global.", "Se usa la regla en ese segmento y se reentrena."],
    ];
    text(s, "TOP 3 RIESGOS CRÍTICOS", { x: 6.55, y: 1.6, w: 6, h: 0.3, fontSize: 11, bold: true, color: MUTED, charSpacing: 1 });
    for (let i = 0; i < risks.length; i++) {
      const y = 2.0 + i * 1.57, [ic, n, sig, resp] = risks[i];
      card(s, 6.55, y, 6.18, 1.42, LIGHT);
      await iconCircle(s, ic, 6.8, y + 0.2, 0.55, CORAL);
      text(s, [
        { text: n, options: { bold: true, fontSize: 15, breakLine: true } },
        { text: sig, options: { fontSize: 12, color: MUTED, breakLine: true } },
        { text: resp, options: { fontSize: 12, bold: true, color: TEAL } },
      ], { x: 7.55, y: y + 0.12, w: 5.0, h: 1.2, valign: "middle" });
    }
    s.addNotes("Legalmente es viable con condiciones: 2,2. No hay datos personales, así que la Ley 25.326 casi no aplica hoy. El riesgo legal real es que circulen costos y condiciones de proveedores: se resuelve con accesos por rol y una adenda de confidencialidad con la consultora. Los tres riesgos críticos son que no aparezcan los ahorros, que los datos de stock vengan inconsistentes y que el ensamble se degrade. Cada uno tiene una señal medible y una respuesta definida.");
  }

  // ================= 17 · Go-live criteria =================
  {
    const s = content("Viabilidad y plan", "Cinco criterios para salir a producción");
    speaker(s, "Gianfranco", "Coordinación");
    const crit = [
      ["Exportación completa y válida: 5 archivos, 0 claves desconocidas, 0 alertas con stock negativo", "Lucía O. y Sistemas", false],
      ["Modelo con Recall@600 ≥ 60% en test temporal y no inferior a la regla a igual cupo", "María G. y responsable del modelo", true],
      ["Responsable del modelo nombrado por escrito, con 5 a 6 h por semana", "Dirección y Carlos F.", false],
      ["Adenda de confidencialidad firmada, accesos por rol con MFA y PC cifrada", "Dirección, Legal, Sistemas y Diego P.", false],
      ["Protocolo de decisión humana aprobado y usuarios del piloto capacitados", "Lucía O., María G. y Diego P.", false],
    ];
    for (let i = 0; i < crit.length; i++) {
      const y = 1.65 + i * 1.0, [c, who, ok] = crit[i];
      if (i % 2 === 0) card(s, 0.6, y - 0.08, 8.4, 0.92, LIGHT, "row-band");
      await iconCircle(s, ok ? "FaCheck" : "FaHourglassHalf", 0.75, y + 0.09, 0.58, ok ? TEAL : LINE, ok ? "FFFFFF" : HEX.dk1);
      text(s, [{ text: c, options: { bold: true, breakLine: true, fontSize: 14 } }, { text: "Aprueba: " + who, options: { fontSize: 12, color: MUTED } }], { x: 1.55, y, w: 7.3, h: 0.76, valign: "middle" });
    }
    card(s, 9.3, 1.57, 3.43, 5.08, DARK);
    text(s, "1 de 5", { x: 9.6, y: 1.85, w: 2.9, h: 0.95, fontSize: 52, bold: true, color: GOLD, valign: "middle" });
    text(s, "criterios cumplidos hoy", { x: 9.6, y: 2.8, w: 2.9, h: 0.4, fontSize: 14, color: WHITE });
    text(s, [
      { text: "El modelo ya cumple: ", options: { bold: true, color: WHITE } },
      { text: "76,9% en test y 1.067 contra 1.034 aciertos de la regla.", options: { color: LINE, breakLine: true } },
      { text: " ", options: { breakLine: true } },
      { text: "Los otros cuatro dependen de Casa Óga, ", options: { bold: true, color: WHITE } },
      { text: "no del equipo: son las precondiciones del plan.", options: { color: LINE } },
    ], { x: 9.6, y: 3.45, w: 2.9, h: 3.0, fontSize: 13 });
    s.addNotes("Para salir a producción definimos cinco criterios verificables, cada uno con quién lo aprueba. Hoy se cumple uno: el del modelo, que supera el piso de 60% y no pierde contra la regla. Los otros cuatro no son técnicos: dependen de que Casa Óga estandarice la exportación, nombre al responsable, firme la adenda y apruebe el protocolo de decisión. Por eso son las precondiciones del plan.");
  }

  // ================= 18 · Project plan =================
  {
    const s = content("Viabilidad y plan", "Plan: de precondiciones a la decisión");
    speaker(s, "Gianfranco", "Coordinación");
    const W0 = 4.55, W1 = 12.7, WEEKS = 28, wk = (W1 - W0) / WEEKS;
    const xOf = (w) => W0 + (w - 1) * wk;
    [1, 6, 10, 14, 18, 22, 28].forEach((w) => text(s, "S" + w, { x: xOf(w) - 0.2, y: 1.55, w: 0.6, h: 0.3, fontSize: 11, color: MUTED, align: "center" }));
    const phases = [
      ["Precondiciones", "Gianfranco + Dirección · responsable nombrado y adenda firmada", 1, 2, STEEL],
      ["Pipeline y datos", "Matías · corrida con 5 archivos y 0 claves desconocidas", 2, 4, STEEL],
      ["Modelo y scoring", "Simón · bloques A y B reproducibles y versionados", 3, 5, STEEL],
      ["Tablero, accesos y taller", "Gerónimo + Santiago · prueba de acceso de tienda; acta del taller", 4, 6, STEEL],
      ["Piloto: 3 cierres", "Gianfranco + Lucía O. · ≥ 60% de alertas con acción", 7, 16, TEAL],
      ["Evaluación y decisión", "Simón + Carlos F. · modelo vs. regla a igual cupo, valor recuperado", 17, 28, GOLD],
    ];
    const RH = 0.62;
    phases.forEach(([n, d, a, b, col], i) => {
      const y = 1.95 + i * RH;
      if (i % 2 === 0) s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: y - 0.03, w: 12.13, h: RH - 0.02, fill: { color: LIGHT }, line: { type: "none" }, objectName: "gantt-band" });
      text(s, [{ text: n, options: { bold: true, fontSize: 14, breakLine: true } }, { text: d, options: { fontSize: 10, color: MUTED } }], { x: 0.7, y, w: 3.75, h: 0.54, valign: "middle" });
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: xOf(a), y: y + 0.12, w: (b - a + 1) * wk, h: 0.3, rectRadius: 0.15, fill: { color: col }, line: { type: "none" }, objectName: "gantt-bar-" + i });
    });
    const ms = [[2, "H1 · Precondiciones"], [6, "H2 · Go-live"], [16, "H3 · Tercer cierre"], [28, "H4 · Decisión"]];
    const yM = 1.95 + 6 * RH + 0.08;
    ms.forEach(([w, l], i) => {
      const cx = xOf(w + 1); // milestone sits at the end of its week, where the phase bar ends
      s.addShape(pres.shapes.LINE, { x: cx, y: 1.9, w: 0, h: yM - 1.9, line: { color: CORAL, width: 1, dashType: "dash" }, objectName: "milestone-line" });
      s.addShape(pres.shapes.DIAMOND, { x: cx - 0.13, y: yM, w: 0.26, h: 0.26, fill: { color: CORAL }, line: { type: "none" }, objectName: "milestone" });
      const lx = Math.min(cx - 0.9, W1 - 1.8);
      // Stagger labels on two rows so neighbouring milestones never overlap.
      text(s, l, { x: lx, y: yM + 0.3 + (i % 2) * 0.27, w: 1.8, h: 0.27, fontSize: 11, bold: true, color: CORAL, align: lx < cx - 0.9 ? "right" : "center" });
    });
    text(s, "Semanas relativas: S1 = inicio de las precondiciones. Las etiquetas del tercer cierre maduran a t+3, por eso la decisión llega cerca de la semana 28.", { x: 0.6, y: 6.66, w: 12.1, h: 0.3, fontSize: 11, color: MUTED, italic: true });
    s.addNotes("El plan tiene seis fases, cada una con un responsable y un criterio de cierre. Dos semanas de precondiciones: sin responsable nombrado y sin adenda firmada no arrancamos. Después pipeline, modelo y tablero, en paralelo parcial, hasta el go-live en la semana 6. El piloto dura tres cierres mensuales. Y como la verdad llega tres meses después, la decisión de si el modelo pasa a motor principal y si se expande se toma cerca de la semana 28, con el valor recuperado medido.");
  }

  // ================= 19 · Closing =================
  pres.addSection({ title: "Cierre" });
  {
    const s = pres.addSlide({ masterName: "DARK", sectionTitle: "Cierre" });
    text(s, "VEREDICTO INTEGRADO", { x: 0.8, y: 0.75, w: 8, h: 0.4, fontSize: 14, bold: true, color: GOLD, charSpacing: 2 });
    text(s, "Avanzar con un piloto supervisado de tres cierres, sin inversión de expansión", { x: 0.8, y: 1.2, w: 11.7, h: 1.4, fontSize: 36, bold: true, color: WHITE });
    text(s, "ANTES DE IMPLEMENTAR", { x: 0.8, y: 2.95, w: 6, h: 0.3, fontSize: 12, bold: true, color: LINE, charSpacing: 1 });
    const acts = [
      ["FaUserTie", "Nombrar al responsable del modelo, con 5 a 6 h por semana"],
      ["FaFileExport", "Estandarizar la exportación mensual con control de recepción"],
      ["FaFileContract", "Firmar la adenda de confidencialidad y activar los accesos por rol"],
    ];
    for (let i = 0; i < acts.length; i++) {
      const x = 0.8 + i * 3.95;
      await iconCircle(s, acts[i][0], x, 3.4, 0.62, GOLD, HEX.dk2);
      text(s, acts[i][1], { x: x + 0.8, y: 3.35, w: 2.95, h: 0.95, fontSize: 15, color: WHITE, valign: "middle" });
    }
    text(s, [
      { text: "Riesgo residual: ", options: { bold: true, color: GOLD } },
      { text: "que el beneficio no se materialice. Casi la mitad del valor esperado es tiempo liberado, y el valor de cada alerta depende de supuestos de recupero todavía no observados.", options: { color: LINE } },
    ], { x: 0.8, y: 4.7, w: 11.7, h: 0.9, fontSize: 15 });
    text(s, [
      { text: "Próximo paso · Entregable 4: ", options: { bold: true, color: WHITE } },
      { text: "PoC / MVP del piloto con la lista mensual y el tablero por rol.", options: { color: LINE } },
    ], { x: 0.8, y: 5.75, w: 9, h: 0.5, fontSize: 15 });
    text(s, "¿Preguntas?", { x: 9.6, y: 6.35, w: 2.95, h: 0.6, fontSize: 24, bold: true, color: GOLD, align: "right" });
    s.addNotes("Cierra Santiago. Recomendamos avanzar, pero con un piloto supervisado y sin aprobar la expansión. El modelo funciona; la pregunta abierta es si paga su costo, y eso sólo lo responde el piloto con datos propios. Antes de implementar hacen falta tres cosas, las tres en manos de Casa Óga. El riesgo que la dirección tiene que conocer: que el beneficio no aparezca. Lo vamos a medir desde el primer cierre. Abrimos a preguntas.");
  }

  await pres.writeFile({ fileName: OUT });
  console.log("wrote", OUT);
}

build().catch((e) => { console.error(e); process.exit(1); });
