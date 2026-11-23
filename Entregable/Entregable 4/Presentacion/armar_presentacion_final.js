// Entregable 4 - final presentation deck (PowerPoint), business pitch to Casa Óga.
// Storyline: problem in money -> the product (monthly list per store) -> demo of the dashboard per user ->
// what the first list (Aug-2026) found -> why it can be trusted -> cost and return -> risks, plan -> decisions asked.
// Numbers come from:
//   Entregable 4/Modelo/resultados/modelo_final_v4_resultados.json  (model, flow, ROI)
//   Entregable 4/Dashboard/datos_dashboard.json                     (Aug-2026 alert list)
//   Entregable 2/Modelo/resultados/insights.json                    (monthly positions > 12 months of coverage)
// Dashboard screenshots live in Presentacion/capturas/ (light theme, 1440x1000 at 1.5x, taken with headless Edge).
// Run: NODE_PATH=<node_modules with pptxgenjs, react, react-dom, react-icons, sharp> node armar_presentacion_final.js [path/to/apply_theme.js]
// It writes Casa-Oga-Presentacion-Final.pptx and Speech-Presentacion-Final.md (the speech is the speaker notes).
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");

const ROOT = path.resolve(__dirname, "../../..");
const OUT = path.join(__dirname, "Casa-Oga-Presentacion-Final.pptx");
const SPEECH = path.join(__dirname, "Speech-Presentacion-Final.md");
const SHOTS = path.join(__dirname, "capturas");
const R = JSON.parse(fs.readFileSync(path.join(ROOT, "Entregable/Entregable 4/Modelo/resultados/modelo_final_v4_resultados.json"), "utf8"));
const D = JSON.parse(fs.readFileSync(path.join(ROOT, "Entregable/Entregable 4/Dashboard/datos_dashboard.json"), "utf8"));
const INS = JSON.parse(fs.readFileSync(path.join(ROOT, "Entregable/Entregable 2/Modelo/resultados/insights.json"), "utf8"));
const THEME = JSON.parse(fs.readFileSync(path.join(ROOT, "Entregable/Entregable 3/Presentacion/theme.json"), "utf8"));
THEME.name = "Casa Oga Final";
const HEX = THEME.colors;
const APPLY_THEME = process.argv[2];

// ---------- number formatting (es-AR) ----------
const num = (x, d = 0) => Number(x).toLocaleString("es-AR", { minimumFractionDigits: d, maximumFractionDigits: d });
const pct = (x, d = 0) => num(100 * x, d) + "%";
const usd = (x) => "USD " + num(x);
const arsM = (x) => "ARS " + num(x / 1e6, 1) + " M";

// ---------- figures ----------
const fv = R.flujo.validacion, ft = R.flujo.test, rv = R.roi.validacion;
const vb = R.insumos.valor_unitario.base_e2, kb = R.punto_operacion.k_bloque_b;
const PRESUPUESTO = 30000; // Casa Óga brief, section 9
const A = D.alertas;
const sum = (xs, f) => xs.reduce((a, x) => a + f(x), 0);
const cap = (xs) => sum(xs, (a) => a.capital_ars);
const L = {
  n: A.length, capital: cap(A),
  regla: A.filter((a) => a.bloque === "A").length, modelo: A.filter((a) => a.bloque === "B").length,
  transferir: A.filter((a) => a.accion === "Transferir"), liquidar: A.filter((a) => a.accion === "Liquidar"),
  dentro: A.filter((a) => a.dentro_capacidad),
  tiendas: D.tiendas.length, cupo: D.capacidad_tienda,
};
L.capacidad = L.tiendas * L.cupo;
const porSku = {};
A.forEach((a) => { porSku[a.sku] = (porSku[a.sku] || 0) + 1; });
const skusMulti = Object.values(porSku).filter((v) => v >= 5);
L.skusMulti = skusMulti.length; L.alertasMulti = sum(skusMulti, (v) => v);
const CAT = { Decoracion: "Decoración", "Textil hogar": "Textil hogar", "Cocina y mesa": "Cocina y mesa", Muebles: "Muebles", Iluminacion: "Iluminación", Organizacion: "Organización", Bano: "Baño" };
const porCat = Object.entries(A.reduce((m, a) => ((m[a.categoria] = (m[a.categoria] || 0) + a.capital_ars), m), {})).sort((x, y) => y[1] - x[1]);
const u = D.universo_mes;

// ---------- deck ----------
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.title = "Casa Óga · Alertas de stock inmovilizado · Grupo 1";
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
    { text: { text: "Casa Óga · Alertas de stock inmovilizado · Grupo 1", options: { x: 0.6, y: 7.0, w: 6, h: 0.3, fontSize: 10, color: MUTED, margin: 0 } } },
  ],
  slideNumber: { x: 12.23, y: 7.0, w: 0.5, h: 0.3, fontSize: 10, color: MUTED, align: "right" },
});
pres.defineSlideMaster({
  title: "DARK",
  background: { color: DARK },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 1.85, w: 11.7, h: 1.9, fontSize: 44, bold: true, color: WHITE, align: "left", valign: "top", margin: 0 }, text: "" } },
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
function pill(slide, t, x, y, w, fill, color = WHITE, h = 0.34) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: h / 2, fill: { color: fill }, line: { type: "none" }, objectName: "pill" });
  text(slide, t, { x, y, w, h, fontSize: 12, bold: true, color, align: "center", valign: "middle" });
}
const CHART_BASE = () => ({
  catAxisLabelColor: HEX.accent5, valAxisLabelColor: HEX.accent5,
  catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", dataLabelFontFace: "+mn-lt", legendFontFace: "+mn-lt", titleFontFace: "+mn-lt",
  catAxisLabelFontSize: 12, valAxisLabelFontSize: 11, dataLabelFontSize: 12, legendFontSize: 12,
  valGridLine: { color: HEX.lt2, size: 1 }, catGridLine: { style: "none" },
  catAxisLineShow: false, valAxisLineShow: false,
});
const NOTES = [];
function content(sectionTitle, title) {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle });
  s.addText(title, { placeholder: "title" });
  s._title = title;
  return s;
}
function notes(slide, who, t, title) {
  slide.addNotes(`${who.toUpperCase()}. ${t}`);
  NOTES.push({ title: title || slide._title, who, t });
}
// Dashboard screenshot: crop a region (pixels of the 2160x1500 capture) and place it inside a framed card.
async function shot(slide, file, crop, x, y, w, alt) {
  const buf = await sharp(path.join(SHOTS, file)).extract(crop).png().toBuffer();
  const h = w * crop.height / crop.width;
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x - 0.06, y: y - 0.06, w: w + 0.12, h: h + 0.12, rectRadius: 0.06, fill: { color: WHITE }, line: { color: LINE, width: 1 }, shadow: { type: "outer", color: HEX.dk1, opacity: 0.15, blur: 6, offset: 2, angle: 90 }, objectName: "screenshot-frame" });
  slide.addImage({ data: "image/png;base64," + buf.toString("base64"), x, y, w, h, altText: alt });
  return h;
}
// Numbered callout under a screenshot.
function callout(slide, n, title, body, x, y, w) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: 0.42, h: 0.42, fill: { color: GOLD }, line: { type: "none" }, objectName: "callout-number" });
  text(slide, String(n), { x, y, w: 0.42, h: 0.42, fontSize: 14, bold: true, align: "center", valign: "middle" });
  text(slide, title, { x: x + 0.55, y: y - 0.02, w: w - 0.55, h: 0.36, fontSize: 15, bold: true });
  text(slide, body, { x: x + 0.55, y: y + 0.36, w: w - 0.55, h: 0.75, fontSize: 13, color: MUTED });
}

async function build() {
  // ================= 1 · Cover =================
  pres.addSection({ title: "Apertura" });
  {
    const s = pres.addSlide({ masterName: "DARK", sectionTitle: "Apertura" });
    text(s, "PROPUESTA PARA CASA ÓGA · ALERTAS DE STOCK INMOVILIZADO", { x: 0.8, y: 1.2, w: 11, h: 0.4, fontSize: 14, bold: true, color: GOLD, charSpacing: 2 });
    s.addText("Liberar el capital parado antes del conteo anual", { placeholder: "title" });
    text(s, "Una lista mensual por tienda que dice qué stock mover o liquidar, y por qué", { x: 0.8, y: 3.55, w: 11, h: 0.85, fontSize: 22, color: LINE });
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
    notes(s, "Santiago", "Buenas, somos el Grupo 1. Venimos a presentarle a Casa Óga una herramienta concreta: una lista mensual, tienda por tienda, que dice qué stock se está quedando parado, qué hacer con él y por qué, antes de que aparezca en el conteo de fin de año. Les vamos a mostrar el problema en plata, el producto funcionando con los datos de agosto, lo que encontramos, cuánto cuesta y qué necesitamos de ustedes para arrancar. Matías trabajó los datos, Simón el modelo, Gerónimo el tablero y Gianfranco la economía y el plan.", "Portada");
  }

  // ================= 2 · Problem =================
  {
    const s = content("Apertura", `Hoy hay ${arsM(u.capital_cob12_ars)} parados en stock que no rota`);
    speaker(s, "Santiago", "Comunicación");
    const m = INS.rojo_mes;
    s.addChart(pres.charts.LINE, [{ name: "Posiciones con cobertura > 12 meses", labels: m.meses.map((x) => x.slice(2).replace("-", "/")), values: m.posiciones }], {
      x: 0.6, y: 1.5, w: 7.6, h: 4.9, ...CHART_BASE(), chartColors: [HEX.accent3], lineSize: 2.5, lineDataSymbol: "none",
      showTitle: true, title: "Posiciones producto–tienda con más de un año de stock", titleFontSize: 14, titleColor: HEX.dk1,
      showLegend: false, catAxisLabelFrequency: 6, valAxisMinVal: 0, valAxisMaxVal: 1000, valAxisMajorUnit: 250,
    });
    const i0 = m.meses.indexOf("2025-12");
    const stats = [
      ["FaBoxes", num(u.posiciones_cob12), `posiciones con más de un año de stock en agosto (${num(m.posiciones[i0])} en diciembre)`, CORAL],
      ["FaMoneyBillWave", arsM(u.capital_cob12_ars), "de capital de trabajo inmovilizado, a costo", NAVY],
      ["FaCalendarTimes", "Fin de año", "es cuando hoy se detecta: en el conteo de inventario, tarde para liquidar bien", NAVY],
    ];
    for (let i = 0; i < stats.length; i++) {
      const y = 1.6 + i * 1.6;
      await iconCircle(s, stats[i][0], 8.6, y + 0.1, 0.62, stats[i][3]);
      text(s, stats[i][1], { x: 9.4, y, w: 3.4, h: 0.55, fontSize: 28, bold: true, color: stats[i][3] });
      text(s, stats[i][2], { x: 9.4, y: y + 0.6, w: 3.4, h: 0.8, fontSize: 13, color: MUTED });
    }
    text(s, "Entre 2023 y 2025 el problema era estable en proporción. En 2026, con la venta en baja, se cuadruplicó en ocho meses.", { x: 0.6, y: 6.45, w: 12, h: 0.4, fontSize: 13, italic: true, color: MUTED });
    notes(s, "Santiago", `Empecemos por el problema, en plata. En agosto hay ${num(u.posiciones_cob12)} combinaciones de producto y tienda con más de un año de stock al ritmo de venta actual: son ${num(u.capital_cob12_ars / 1e6, 1)} millones de pesos a costo que no están trabajando. En diciembre eran ${num(m.posiciones[i0])}. Entre 2023 y 2025 el problema era estable; en 2026, con la venta en baja, se cuadruplicó en ocho meses. Y hoy esto se ve recién en el conteo de fin de año, cuando ya pasaron meses de costo y liquidar sale más caro.`);
  }

  // ================= 3 · The three questions answered =================
  {
    const s = content("Apertura", "Respondemos las tres preguntas de la Dirección");
    speaker(s, "Santiago", "Comunicación");
    const cols = [
      ["FaSearch", "¿Qué productos van a quedar parados en los próximos meses?", `Cada mes, la lista de posiciones en riesgo: las que ya pasaron el año de stock y ${kb} que el modelo ve venir con tres meses de anticipación.`],
      ["FaFingerprint", "¿Qué distingue a los que rotan de los que no?", "La venta de los últimos 6 meses, la cobertura y lo irregular de la venta. Y un patrón de compra: el mismo SKU parado en muchas tiendas."],
      ["FaExchangeAlt", "¿Qué liquidar o mover, y en qué tienda?", "Cada alerta trae una acción sugerida: transferir a la tienda que lo vende rápido, o liquidar. La decisión la toma una persona."],
    ];
    for (let i = 0; i < cols.length; i++) {
      const x = 0.6 + i * 4.1;
      card(s, x, 1.6, 3.9, 3.75);
      await iconCircle(s, cols[i][0], x + 0.3, 1.85, 0.62, NAVY);
      text(s, cols[i][1], { x: x + 0.3, y: 2.65, w: 3.3, h: 0.95, fontSize: 16, bold: true });
      text(s, cols[i][2], { x: x + 0.3, y: 3.65, w: 3.3, h: 1.6, fontSize: 13, color: MUTED });
    }
    card(s, 0.6, 5.6, 12.13, 1.05, NAVY, "proposal");
    text(s, [
      { text: "Nuestra propuesta: ", options: { bold: true, color: GOLD } },
      { text: `un piloto de tres cierres mensuales con una inversión de ${usd(rv.total.inversion)}, un tercio del presupuesto disponible.`, options: { color: WHITE } },
    ], { x: 0.9, y: 5.6, w: 11.6, h: 1.05, fontSize: 17, valign: "middle" });
    notes(s, "Santiago", `Cuando arrancamos, la Dirección nos hizo tres preguntas. Qué productos van a quedar parados en los próximos meses; qué distingue a los que rotan de los que no; y qué conviene liquidar o mover, y en qué tienda. Hoy tenemos una respuesta para cada una, y la van a ver funcionando. Les adelanto la propuesta: un piloto de tres cierres mensuales, con una inversión de ${num(rv.total.inversion)} dólares, un tercio del presupuesto. Le paso a Gerónimo, que les muestra el producto.`);
  }

  // ================= 4 · How it works =================
  pres.addSection({ title: "El producto" });
  {
    const s = content("El producto", "Una semana por mes, y siempre decide una persona");
    speaker(s, "Gerónimo", "Visualización");
    const steps = [
      ["FaFileImport", "Recibimos", "Las 5 exportaciones mensuales que Casa Óga ya genera en el cierre", "Días 1-3"],
      ["FaBroom", "Ordenamos", "Se limpian con las reglas acordadas con Casa Óga", "Día 3-4"],
      ["FaListOl", "Armamos la lista", `Todo lo que ya pasó el año de stock, más ${kb} posiciones que el modelo ve venir`, "Día 4"],
      ["FaStore", "Cada área ve lo suyo", "Tienda, Operaciones, Compras, Comercial y Finanzas", "Día 5"],
      ["FaUserCheck", "Decidimos", "La tienda propone; Comercial y Compras autorizan en 30 minutos", "Semana 2"],
      ["FaSyncAlt", "Medimos", "Tres meses después: ¿acertamos? ¿cuánto capital se liberó?", "Mensual"],
    ];
    for (let i = 0; i < steps.length; i++) {
      const x = 0.6 + i * 2.05;
      card(s, x, 1.75, 1.85, 3.85);
      await iconCircle(s, steps[i][0], x + 0.6, 2.0, 0.65, i === 2 ? GOLD : NAVY, i === 2 ? HEX.dk1 : "FFFFFF");
      text(s, steps[i][1], { x: x + 0.1, y: 2.85, w: 1.65, h: 0.65, fontSize: 15, bold: true, align: "center" });
      text(s, steps[i][2], { x: x + 0.12, y: 3.5, w: 1.61, h: 1.45, fontSize: 12, color: NAVY, align: "center" });
      pill(s, steps[i][3], x + 0.27, 5.05, 1.31, WHITE, NAVY, 0.32);
    }
    text(s, "No hace falta infraestructura nueva: corre en una PC de oficina con herramientas gratuitas. El tablero es una foto mensual, no un sistema en vivo.", { x: 0.6, y: 5.95, w: 12.1, h: 0.6, fontSize: 14, italic: true, color: MUTED });
    notes(s, "Gerónimo", `Así funciona en el día a día. Con el cierre de cada mes recibimos las cinco exportaciones que Casa Óga ya genera; las ordenamos con las reglas que acordamos con ustedes; y armamos la lista: primero todo lo que ya tiene más de un año de stock, que se explica solo, y después las ${kb} posiciones que el modelo ve venir. Cada área recibe su vista. La tienda propone qué hacer, y Comercial y Compras autorizan en una reunión de media hora. Tres meses después medimos si acertamos y cuánto capital se liberó. No hace falta comprar nada: corre en una PC de oficina. Y una aclaración: el tablero es una foto mensual, no un sistema en vivo.`);
  }

  // ================= 5 · Demo · Dirección =================
  {
    const s = content("El producto", "Dirección: el mes en una pantalla");
    speaker(s, "Gerónimo", "Visualización");
    const h = await shot(s, "resumen.png", { left: 36, top: 426, width: 2088, height: 672 }, 0.97, 1.62, 11.4, "Dashboard, vista Resumen: indicadores del mes, casos detectados por mes y alertas por región");
    const y = 1.62 + h + 0.4;
    callout(s, 1, "Cuánto hay en juego", `${num(L.n)} alertas por ${arsM(L.capital)} en agosto`, 0.6, y, 4.0);
    callout(s, 2, "Si la lista acierta", "Casos detectados mes a mes contra la regla simple", 4.65, y, 4.0);
    callout(s, 3, "Dónde está el problema", "Por región, por acción y con filtros por tienda y categoría", 8.7, y, 4.0);
    notes(s, "Gerónimo", `Esta es la vista para la Dirección, con los datos reales de agosto. Arriba, lo que está en juego: ${num(L.n)} alertas por ${num(L.capital / 1e6, 1)} millones de pesos. Al medio, mes a mes, cuántos casos detectó la lista contra la regla simple, en los meses que ya sabemos cómo terminaron. A la derecha, dónde está el problema: AMBA es la región con más alertas, cuatro de cada diez. Todo se filtra por región, tienda, categoría o proveedor.`);
  }

  // ================= 6 · Demo · Tiendas =================
  {
    const s = content("El producto", "Tiendas: cada alerta llega con qué hacer y por qué");
    speaker(s, "Gerónimo", "Visualización");
    const h = await shot(s, "lista.png", { left: 36, top: 365, width: 2088, height: 612 }, 0.66, 1.62, 12.0, "Dashboard, Lista de alertas: tienda, SKU, cobertura, capital, acción sugerida y señales");
    const y = 1.62 + h + 0.4;
    callout(s, 1, "Ordenada por capital", `Cada tienda trabaja ${L.cupo} alertas por mes, empezando por las de más plata`, 0.6, y, 4.0);
    callout(s, 2, "Con destino", "Transferir dice a qué tienda, que hoy lo vende rápido", 4.65, y, 4.0);
    callout(s, 3, "Con el motivo", "Las señales que explican la alerta, en palabras", 8.7, y, 4.0);
    notes(s, "Gerónimo", `Esta es la lista que recibe cada tienda. Está ordenada por capital, y cada tienda trabaja hasta ${L.cupo} alertas por mes, el máximo que nos dijo Operaciones. Cada fila trae una acción sugerida: si otra tienda vende ese producto rápido, dice a cuál transferirlo; si no, liquidar. Y trae el motivo en palabras, por ejemplo: un año de cobertura y la venta del trimestre en cero. La versión para las tiendas se publica sin la columna de costos.`);
  }

  // ================= 7 · Demo · Compras =================
  {
    const s = content("El producto", "Compras: qué no volver a comprar");
    speaker(s, "Gerónimo", "Visualización");
    const h = await shot(s, "compras.png", { left: 36, top: 393, width: 2088, height: 590 }, 0.66, 1.62, 12.0, "Dashboard, Compras y categorías: capital en alerta por categoría y por proveedor");
    const y = 1.62 + h + 0.4;
    callout(s, 1, "Por categoría", "Dónde se concentra el capital parado", 0.6, y, 4.0);
    callout(s, 2, "Por proveedor", "Para negociar devoluciones y condiciones", 4.65, y, 4.0);
    callout(s, 3, "SKUs en varias tiendas", "Si el mismo producto está parado en muchas tiendas, el problema es la compra", 8.7, y, 4.0);
    notes(s, "Gerónimo", "Para Compras la pregunta es otra: qué no volver a comprar. Acá ven el capital en alerta por categoría y por proveedor, que sirve para negociar devoluciones y condiciones. Y abajo, los productos que están en alerta en muchas tiendas a la vez: eso no se arregla moviendo mercadería, es una señal de que se compró de más. Finanzas y quien mantenga el modelo tienen sus propias vistas, que les dejamos en el tablero. Le paso a Matías con lo que encontramos.");
  }

  // ================= 8 · What the first list found =================
  pres.addSection({ title: "Lo que encontramos" });
  {
    const s = content("Lo que encontramos", "La primera lista: agosto de 2026");
    speaker(s, "Matías", "Datos");
    s.addChart(pres.charts.BAR, [{ name: "Capital en alerta (ARS M)", labels: porCat.map(([c]) => CAT[c] || c).reverse(), values: porCat.map(([, v]) => +(v / 1e6).toFixed(1)).reverse() }], {
      x: 0.6, y: 1.5, w: 6.4, h: 4.95, barDir: "bar", ...CHART_BASE(), chartColors: [HEX.accent4], showValue: true, dataLabelPosition: "outEnd", dataLabelColor: HEX.dk1,
      dataLabelFormatCode: "0.0", showTitle: true, title: "Capital en alerta por categoría (ARS millones)", titleFontSize: 14, titleColor: HEX.dk1,
      showLegend: false, valAxisHidden: true, valGridLine: { style: "none" }, barGapWidthPct: 45,
    });
    const top2 = (porCat[0][1] + porCat[1][1]) / L.capital;
    const stats = [
      [`${num(L.n)}`, `alertas en ${L.tiendas} tiendas, por ${arsM(L.capital)} a costo`, NAVY],
      [`${num(10 * L.transferir.length / L.n)} de cada 10`, `se resuelven transfiriendo, sin rematar: ${num(L.transferir.length)} alertas por ${arsM(cap(L.transferir))}. Liquidar: ${num(L.liquidar.length)}.`, TEAL],
      [`${num(L.skusMulti)} productos`, `están parados en 5 tiendas o más y suman ${pct(L.alertasMulti / L.n)} de las alertas: es un tema de compra`, CORAL],
      [pct(top2), `del capital está en ${CAT[porCat[0][0]]} y ${CAT[porCat[1][0]]}`, STEEL],
    ];
    stats.forEach(([v, l, col], i) => {
      const y = 1.6 + i * 1.22;
      text(s, v, { x: 7.4, y, w: 5.3, h: 0.5, fontSize: 26, bold: true, color: col });
      text(s, l, { x: 7.4, y: y + 0.5, w: 5.3, h: 0.65, fontSize: 13, color: MUTED });
    });
    notes(s, "Matías", `Trabajamos con cuatro años de datos de las ${L.tiendas} tiendas, más de 200 mil registros mensuales de producto y tienda, limpiados con las reglas que acordamos con ustedes. Corrimos la lista de agosto y esto es lo que dice. Son ${num(L.n)} alertas por ${num(L.capital / 1e6, 1)} millones. La buena noticia: ${num(10 * L.transferir.length / L.n)} de cada 10 se resuelven transfiriendo, porque otra tienda vende ese producto rápido; no hace falta rematar. Segundo: ${num(L.skusMulti)} productos están parados en cinco tiendas o más y explican casi la mitad de las alertas; ahí el problema no es la ubicación, es cuánto se compró. Y tercero, ${CAT[porCat[0][0]]} y ${CAT[porCat[1][0]]} concentran ${pct(top2)} del capital.`);
  }

  // ================= 9 · Capacity finding =================
  {
    const s = content("Lo que encontramos", "Hoy la lista no entra en las tiendas: hay que ponerse al día");
    speaker(s, "Matías", "Datos");
    await shot(s, "tiendas.png", { left: 36, top: 393, width: 2088, height: 590 }, 0.66, 1.62, 7.5, "Dashboard, Tiendas: alertas por tienda contra el cupo de 25");
    card(s, 8.6, 1.56, 4.13, 4.9);
    text(s, `${num(L.regla)} > ${num(L.capacidad)}`, { x: 8.85, y: 1.75, w: 3.7, h: 0.75, fontSize: 40, bold: true, color: CORAL });
    text(s, `Sólo lo que ya pasó el año de stock supera lo que pueden trabajar las tiendas (${L.tiendas} × ${L.cupo} por mes).`, { x: 8.85, y: 2.55, w: 3.7, h: 0.95, fontSize: 13, color: NAVY });
    text(s, pct(cap(L.dentro) / L.capital), { x: 8.85, y: 3.6, w: 3.7, h: 0.65, fontSize: 32, bold: true, color: TEAL });
    text(s, `del capital entra igual en el cupo, porque cada tienda empieza por las alertas de más plata (${arsM(cap(L.dentro))}).`, { x: 8.85, y: 4.25, w: 3.7, h: 0.95, fontSize: 13, color: NAVY });
    text(s, `Quedan ${num(L.n - L.dentro.length)} para el mes siguiente.`, { x: 8.85, y: 5.4, w: 3.7, h: 0.5, fontSize: 13, color: MUTED, italic: true });
    callout(s, 1, "Tiendas desbordadas", `Cada barra que pasa la línea punteada tiene más alertas que su cupo de ${L.cupo} por mes`, 0.6, 4.1, 7.62);
    card(s, 0.6, 5.36, 7.62, 1.1, NAVY, "decision");
    text(s, [
      { text: "Decisión para la Dirección: ", options: { bold: true, color: GOLD } },
      { text: "una limpieza puntual antes del piloto, o ponerse al día en 2 o 3 meses.", options: { color: WHITE } },
    ], { x: 0.85, y: 5.36, w: 7.2, h: 1.1, fontSize: 15, valign: "middle" });
    notes(s, "Matías", `Y un hallazgo que no esperábamos. Sólo lo que ya pasó el año de stock son ${num(L.regla)} posiciones, y las tiendas pueden trabajar ${num(L.capacidad)} por mes: ${L.cupo} cada una. En el gráfico, cada barra que pasa la línea punteada es una tienda desbordada. Como cada tienda empieza por las alertas de más plata, el ${pct(cap(L.dentro) / L.capital)} del capital entra igual en el cupo; el resto pasa al mes siguiente. Pero hay una decisión que es de la Dirección: hacer una limpieza puntual antes del piloto, o ponerse al día en dos o tres meses. Le paso a Simón, que cuenta por qué pueden confiar en la lista.`);
  }

  // ================= 10 · Results =================
  pres.addSection({ title: "Por qué confiar" });
  {
    const s = content("Por qué confiar", "Con las mismas alertas, encuentra más casos que la regla simple");
    speaker(s, "Simón", "Modelado");
    s.addChart(pres.charts.BAR, [
      { name: "Ordenar por cobertura (regla simple)", labels: ["Año 2025", "Ene–may 2026"], values: [fv.regla_mismo_cupo.vp, ft.regla_mismo_cupo.vp] },
      { name: "Nuestra lista (regla + modelo)", labels: ["Año 2025", "Ene–may 2026"], values: [fv.flujo.vp, ft.flujo.vp] },
    ], {
      x: 0.6, y: 1.5, w: 7.6, h: 4.95, barDir: "col", barGrouping: "clustered", barGapWidthPct: 70, ...CHART_BASE(),
      chartColors: [HEX.accent6, HEX.accent4], showValue: true, dataLabelPosition: "outEnd", dataLabelColor: HEX.dk1,
      showTitle: true, title: "Posiciones que terminaron inmovilizadas y la lista marcó a tiempo", titleFontSize: 14, titleColor: HEX.dk1,
      showLegend: true, legendPos: "b", valAxisHidden: true, valGridLine: { style: "none" },
    });
    const st = [
      [`+${pct(fv.flujo.vp / fv.regla_mismo_cupo.vp - 1)}`, `casos detectados en 2025 con el mismo número de alertas (${fv.flujo.vp} contra ${fv.regla_mismo_cupo.vp})`, TEAL],
      [`${pct(fv.flujo.recall)} – ${pct(ft.flujo.recall)}`, "de lo que se iba a inmovilizar, marcado tres meses antes", STEEL],
      [`+${pct(ft.flujo.vp / ft.regla_mismo_cupo.vp - 1)}`, "en 2026: con tanto stock parado, la regla sola ya alcanza casi todo. Por eso el piloto lo vuelve a medir.", CORAL],
    ];
    st.forEach(([v, l, col], i) => {
      const y = 1.6 + i * 1.6;
      text(s, v, { x: 8.6, y, w: 4.1, h: 0.6, fontSize: 30, bold: true, color: col });
      text(s, l, { x: 8.6, y: y + 0.65, w: 4.1, h: 0.85, fontSize: 13, color: MUTED });
    });
    notes(s, "Simón", `¿Por qué confiar en la lista? La probamos con meses que ya sabemos cómo terminaron. Con la misma cantidad de alertas, nuestra lista detecta ${fv.flujo.vp} casos en 2025 contra ${fv.regla_mismo_cupo.vp} de ordenar por cobertura: un ${pct(fv.flujo.vp / fv.regla_mismo_cupo.vp - 1)} más. Marca entre el ${pct(fv.flujo.recall)} y el ${pct(ft.flujo.recall)} de lo que se iba a inmovilizar, tres meses antes. Y les somos honestos: en 2026 la ventaja es chica, ${pct(ft.flujo.vp / ft.regla_mismo_cupo.vp - 1)}, porque con tanto stock parado la regla sola ya encuentra casi todo. Por eso proponemos un piloto que lo vuelva a medir antes de comprometer nada más.`);
  }

  // ================= 11 · Explainability =================
  {
    const s = content("Por qué confiar", "Mira lo que miraría un comprador, pero antes");
    speaker(s, "Simón", "Modelado");
    const imp = R.importancia_permutacion.variables.slice(0, 5);
    const nombres = { u6_suma: "Venta de los últimos 6 meses", cobertura: "Cobertura actual", cv_u12: "Irregularidad de la venta", stock_sku_cadena: "Stock del SKU en la cadena", peso_posicion_en_tienda: "Peso en la tienda", u12_prom: "Venta promedio 12 meses" };
    s.addChart(pres.charts.BAR, [{ name: "Casos que se pierden sin la variable", labels: imp.map((r) => nombres[r.variable] || r.variable).reverse(), values: imp.map((r) => r.caida_vp).reverse() }], {
      x: 0.6, y: 1.5, w: 7.6, h: 4.95, barDir: "bar", ...CHART_BASE(), chartColors: [HEX.accent4], showValue: true, dataLabelPosition: "outEnd", dataLabelColor: HEX.dk1,
      showTitle: true, title: `Casos detectados que se pierden si el modelo no ve cada dato (de ${R.importancia_permutacion.vp_base})`, titleFontSize: 14, titleColor: HEX.dk1,
      showLegend: false, valAxisHidden: true, valGridLine: { style: "none" }, barGapWidthPct: 50,
    });
    const cards = [
      ["FaCommentDots", "Cada alerta trae su motivo", "«Un año de cobertura y la venta del trimestre en cero.» Se entiende sin saber de modelos."],
      ["FaUserCheck", "El modelo ordena, la persona decide", "Nada se liquida ni se mueve sin que la tienda proponga y Comercial y Compras autoricen."],
    ];
    for (let i = 0; i < cards.length; i++) {
      const y = 1.6 + i * 2.45;
      card(s, 8.6, y, 4.13, 2.2);
      await iconCircle(s, cards[i][0], 8.85, y + 0.25, 0.55, TEAL);
      text(s, cards[i][1], { x: 9.55, y: y + 0.3, w: 3.05, h: 0.5, fontSize: 15, bold: true });
      text(s, cards[i][2], { x: 8.85, y: y + 0.95, w: 3.7, h: 1.15, fontSize: 13, color: MUTED });
    }
    notes(s, "Simón", "Y no es una caja negra. Medimos qué pasa si le escondemos al modelo cada dato: lo que más pesa es la venta de los últimos seis meses, la cobertura y lo irregular de la venta. Es lo mismo que miraría un comprador con experiencia, pero combinado y antes de que el producto cruce el año de stock. Cada alerta trae su motivo en palabras, y el modelo sólo ordena: nada se liquida ni se mueve sin que una persona lo decida. Le paso a Gianfranco con los números.");
  }

  // ================= 12 · Investment and return =================
  pres.addSection({ title: "Inversión y plan" });
  {
    const s = content("Inversión y plan", "Usa un tercio del presupuesto y se paga en dos años");
    speaker(s, "Gianfranco", "Coordinación");
    // budget bar
    text(s, "Inversión inicial contra el presupuesto de la iniciativa", { x: 0.6, y: 1.55, w: 7.6, h: 0.4, fontSize: 15, bold: true });
    const bw = 7.6, used = rv.total.inversion / PRESUPUESTO;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 2.05, w: bw, h: 0.62, rectRadius: 0.1, fill: { color: LIGHT }, line: { type: "none" }, objectName: "budget-total" });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 2.05, w: bw * used, h: 0.62, rectRadius: 0.1, fill: { color: GOLD }, line: { type: "none" }, objectName: "budget-used" });
    text(s, `${usd(rv.total.inversion)} (${pct(used)})`, { x: 0.75, y: 2.05, w: bw * used, h: 0.62, fontSize: 14, bold: true, valign: "middle" });
    text(s, usd(PRESUPUESTO), { x: 0.6, y: 2.05, w: bw - 0.15, h: 0.62, fontSize: 14, color: MUTED, align: "right", valign: "middle" });
    const kpis = [
      [usd(rv.total.beneficio_anual), "beneficio por año"],
      [usd(rv.total.recurrente), "costo por año (mantenimiento y soporte)"],
      [`+${pct(rv.total.roi_3anios, 1)}`, "retorno a 3 años"],
      [`${num(rv.total.recupero_meses)} meses`, "para recuperar la inversión"],
    ];
    kpis.forEach(([v, l], i) => {
      const x = 0.6 + (i % 2) * 3.9, y = 3.05 + Math.floor(i / 2) * 1.45;
      card(s, x, y, 3.7, 1.25);
      text(s, v, { x: x + 0.25, y: y + 0.15, w: 3.3, h: 0.55, fontSize: 24, bold: true, color: i === 2 ? TEAL : NAVY });
      text(s, l, { x: x + 0.25, y: y + 0.72, w: 3.3, h: 0.45, fontSize: 13, color: MUTED });
    });
    // Horizontal bars instead of a doughnut (Clase 14: avoid pie charts). Bars are listed bottom-up, so the largest goes last.
    const beneficio = [
      ["Lo que suma el modelo", rv.valor_incremental_modelo_anual],
      ["Horas que se ahorran", rv.horas_anual],
      ["Capital liberado con la regla", rv.valor_regla_anual],
    ];
    s.addChart(pres.charts.BAR, [{ name: "Beneficio anual (USD)", labels: beneficio.map(([l]) => l), values: beneficio.map(([, v]) => Math.round(v)) }], {
      x: 8.6, y: 1.5, w: 4.13, h: 4.95, barDir: "bar", ...CHART_BASE(), chartColors: [HEX.accent4], barGapWidthPct: 60,
      showTitle: true, title: `De dónde sale el beneficio (${usd(rv.total.beneficio_anual)}/año)`, titleFontSize: 14, titleColor: HEX.dk1,
      showValue: true, dataLabelPosition: "outEnd", dataLabelColor: HEX.dk1, dataLabelFormatCode: "#,##0",
      valAxisHidden: true, valGridLine: { style: "none" }, valAxisMaxVal: Math.ceil(rv.valor_regla_anual * 1.3 / 1000) * 1000, showLegend: false,
    });
    text(s, "Año de referencia: 2025. En un año como 2026, con más stock parado, el retorno es mayor; lo tomamos como techo, no como promesa.", { x: 0.6, y: 6.05, w: 7.6, h: 0.6, fontSize: 12, italic: true, color: MUTED });
    notes(s, "Gianfranco", `Vamos a los números. La inversión inicial es de ${num(rv.total.inversion)} dólares, un tercio de los 30 mil del presupuesto, sin comprar infraestructura. En un año como 2025, el proyecto devuelve unos ${num(rv.total.beneficio_anual)} dólares por año y cuesta ${num(rv.total.recurrente)} mantenerlo: el retorno a tres años es de ${pct(rv.total.roi_3anios, 1)} y la inversión se recupera en unos ${num(rv.total.recupero_meses)} meses. Fíjense de dónde sale el beneficio: la mayor parte viene de automatizar la lista y de las horas que hoy se van en armarla a mano; el modelo suma por encima. Elegimos 2025 como referencia a propósito: en un año como 2026 los números son mucho mejores, pero eso es un techo, no una promesa.`);
  }

  // ================= 13 · Risks =================
  {
    const s = content("Inversión y plan", "Lo que puede salir mal, y cómo lo vemos a tiempo");
    speaker(s, "Gianfranco", "Coordinación");
    const dev = rv.total_desarrollo_3a4_meses[0];
    const risks = [
      ["FaChartLine", "Que el beneficio no alcance", `Señal: dos trimestres por debajo de ${usd(2288)}`, "Respuesta: seguir sólo con la lista automatizada, que se paga sola"],
      ["FaDatabase", "Que los datos lleguen incompletos", "Señal: archivos faltantes o códigos desconocidos en el cierre", "Respuesta: esas filas no se publican hasta corregirlas"],
      ["FaRobot", "Que el modelo no le gane a la regla", "Señal: dos meses seguidos con igual o menos aciertos", "Respuesta: se apaga el modelo y se reentrena, sin costo extra"],
    ];
    for (let i = 0; i < risks.length; i++) {
      const y = 1.6 + i * 1.62;
      card(s, 0.6, y, 7.6, 1.42);
      await iconCircle(s, risks[i][0], 0.85, y + 0.38, 0.62, CORAL);
      text(s, risks[i][1], { x: 1.7, y: y + 0.15, w: 6.3, h: 0.4, fontSize: 16, bold: true });
      text(s, risks[i][2], { x: 1.7, y: y + 0.55, w: 6.3, h: 0.38, fontSize: 13, color: MUTED });
      text(s, risks[i][3], { x: 1.7, y: y + 0.92, w: 6.3, h: 0.38, fontSize: 13, color: NAVY });
    }
    card(s, 8.6, 1.6, 4.13, 2.3);
    text(s, "El supuesto que más pesa", { x: 8.85, y: 1.8, w: 3.7, h: 0.4, fontSize: 15, bold: true });
    text(s, `Si el desarrollo costara tres meses de un especialista (${usd(dev.inversion)}), el retorno a 3 años queda en ${pct(dev.roi_3anios, 1)}: se recupera en ${num(dev.recupero_meses)} meses. Sigue dentro del presupuesto.`, { x: 8.85, y: 2.25, w: 3.7, h: 1.6, fontSize: 13, color: NAVY });
    card(s, 8.6, 4.1, 4.13, 2.38, NAVY, "legal");
    text(s, "Datos y confidencialidad", { x: 8.85, y: 4.3, w: 3.7, h: 0.4, fontSize: 15, bold: true, color: GOLD });
    text(s, [
      { text: "Sin datos personales de clientes.", options: { bullet: true, breakLine: true } },
      { text: "Las tiendas no ven costos ni condiciones de proveedores.", options: { bullet: true, breakLine: true } },
      { text: "Acuerdo de confidencialidad con el equipo.", options: { bullet: true } },
    ], { x: 8.85, y: 4.75, w: 3.7, h: 1.6, fontSize: 13, color: WHITE, paraSpaceAfter: 6 });
    notes(s, "Gianfranco", `Tres cosas pueden salir mal, y para cada una definimos una señal que la detecta y una respuesta. Que el beneficio no alcance: si dos trimestres quedan por debajo de lo esperado, seguimos sólo con la lista automatizada, que se paga sola. Que los datos lleguen incompletos: esas filas no se publican hasta corregirlas. Y que el modelo no le gane a la regla: se apaga y se reentrena, sin costo extra. El supuesto que más mueve el número es el costo de desarrollo: si fueran tres meses de un especialista, el retorno a tres años queda en cero, y aun así está dentro del presupuesto. Del lado legal no hay datos personales, y las tiendas no ven costos.`);
  }

  // ================= 14 · Plan =================
  {
    const s = content("Inversión y plan", "Preparación, piloto de tres cierres y decisión en el mes 6");
    speaker(s, "Gianfranco", "Coordinación");
    const ph = [
      ["Semanas 1-2", "Datos al día", "Cargar las correcciones pendientes y repetir la evaluación", NAVY],
      ["Semanas 3-4", "Puesta en marcha", "Responsable del modelo, accesos por rol y exportación mensual", NAVY],
      ["Meses 1-3", "Piloto", "Tres cierres con la lista; meta: decisión en 6 de cada 10 alertas", STEEL],
      ["Meses 4-6", "Medición", "¿Encontró más que la regla? ¿Cuánto capital liberó?", STEEL],
      ["Mes 6", "Decisión", "Finanzas decide si sigue, con el informe del piloto", GOLD],
    ];
    ph.forEach(([when, what, crit, col], i) => {
      const x = 0.6 + i * 2.45;
      s.addShape(pres.shapes.CHEVRON, { x, y: 1.75, w: 2.35, h: 0.75, fill: { color: col }, line: { type: "none" }, objectName: "phase" });
      text(s, when, { x: x + 0.3, y: 1.75, w: 1.8, h: 0.75, fontSize: 14, bold: true, color: i === 4 ? NAVY : WHITE, align: "center", valign: "middle" });
      text(s, what, { x, y: 2.75, w: 2.25, h: 0.45, fontSize: 16, bold: true });
      text(s, crit, { x, y: 3.2, w: 2.25, h: 1.1, fontSize: 13, color: MUTED });
    });
    card(s, 0.6, 4.6, 12.13, 1.85);
    text(s, "Qué pone Casa Óga", { x: 0.9, y: 4.75, w: 11.5, h: 0.4, fontSize: 16, bold: true });
    const asks = [
      ["FaUserTie", "Un responsable del modelo"],
      ["FaFileExport", "La exportación mensual de 5 archivos"],
      ["FaClock", "30 minutos por mes de Comercial y Compras"],
      ["FaDesktop", "Una PC de oficina que ya existe"],
    ];
    for (let i = 0; i < asks.length; i++) {
      const x = 0.9 + i * 2.95;
      await iconCircle(s, asks[i][0], x, 5.3, 0.55, TEAL);
      text(s, asks[i][1], { x: x + 0.7, y: 5.27, w: 2.15, h: 0.65, fontSize: 13, valign: "middle" });
    }
    notes(s, "Gianfranco", "El plan es corto. Dos semanas para poner los datos al día con las correcciones que quedaron pendientes y repetir la evaluación; dos semanas más para nombrar al responsable, configurar los accesos y estandarizar la exportación. Después, un piloto de tres cierres mensuales. Como el resultado de una alerta se conoce tres meses después, entre los meses 4 y 6 medimos si la lista encontró más que la regla y cuánto capital liberó, y en el mes 6 Finanzas decide si sigue. De parte de Casa Óga hace falta poco: un responsable, la exportación mensual, media hora por mes de Comercial y Compras, y una PC que ya tienen. Le devuelvo la palabra a Santiago.");
  }

  // ================= 15 · Close =================
  pres.addSection({ title: "Cierre" });
  {
    const s = pres.addSlide({ masterName: "DARK", sectionTitle: "Cierre" });
    text(s, "LO QUE LES PEDIMOS HOY", { x: 0.8, y: 1.2, w: 11, h: 0.4, fontSize: 14, bold: true, color: GOLD, charSpacing: 2 });
    s.addText("Tres decisiones para arrancar el piloto", { placeholder: "title" });
    const acts = [
      ["FaCheckCircle", "Aprobar el piloto", `Tres cierres, ${usd(rv.total.inversion)}`],
      ["FaUserTie", "Nombrar al responsable", "Quien mantiene la lista y el modelo"],
      ["FaBroom", "Elegir cómo ponerse al día", `Con las ${num(L.regla)} posiciones de hoy`],
    ];
    for (let i = 0; i < acts.length; i++) {
      const x = 0.8 + i * 3.95;
      await iconCircle(s, acts[i][0], x, 3.4, 0.7, GOLD, HEX.dk1);
      text(s, [
        { text: acts[i][1], options: { bold: true, fontSize: 17, color: WHITE, breakLine: true } },
        { text: acts[i][2], options: { fontSize: 14, color: LINE } },
      ], { x: x + 0.9, y: 3.4, w: 2.85, h: 1.1 });
    }
    text(s, `Si el modelo no suma en el piloto, la lista automatizada igual se paga sola: retorno a 3 años de ${pct(rv.automatizacion_sin_modelo.roi_3anios, 1)}.`, { x: 0.8, y: 5.35, w: 11.7, h: 0.7, fontSize: 16, italic: true, color: LINE });
    notes(s, "Santiago", `Cerramos. Casa Óga tiene hoy ${num(u.capital_cob12_ars / 1e6, 1)} millones de pesos parados y se entera en el conteo de fin de año. Les proponemos verlo todos los meses, tienda por tienda, con qué hacer y por qué. Para arrancar necesitamos tres decisiones: aprobar un piloto de tres cierres por ${num(rv.total.inversion)} dólares; nombrar a un responsable; y elegir cómo ponerse al día con las ${num(L.regla)} posiciones que hay hoy. El riesgo está acotado: si el modelo no suma, la lista automatizada igual se paga sola. Muchas gracias; quedamos para preguntas.`, "Cierre");
  }

  await pres.writeFile({ fileName: OUT });
  if (APPLY_THEME) {
    const { applyTheme } = require(path.resolve(APPLY_THEME));
    await applyTheme(OUT, THEME);
  }
  console.log("OK", OUT);

  // ---------- speech (same text as the speaker notes) ----------
  const order = [];
  NOTES.forEach((n, i) => {
    const last = order[order.length - 1];
    if (last && last.who === n.who) last.to = i + 1; else order.push({ who: n.who, from: i + 1, to: i + 1 });
  });
  const roles = { Santiago: "Comunicación", Gerónimo: "Visualización", Matías: "Datos", Simón: "Modelado", Gianfranco: "Coordinación" };
  const md = [
    "# Speech · Presentación final (Grupo 1)",
    "",
    `> Guion generado desde las notas del orador de \`Casa-Oga-Presentacion-Final.pptx\` (${NOTES.length} diapositivas, unos 15 minutos) por \`armar_presentacion_final.js\`. Para cambiarlo, editar el script y regenerar. Las cifras salen de \`Modelo/resultados/modelo_final_v4_resultados.json\` y \`Dashboard/datos_dashboard.json\`.`,
    "",
    "Tono: presentación de negocio a Casa Óga (Dirección, Compras, Finanzas y Operaciones), no exposición técnica. El detalle técnico y la sección «Cambios» están en el informe final.",
    "",
    "| Orden | Quién | Diapositivas |",
    "|---|---|---|",
    ...order.map((o, i) => `| ${i + 1} | ${o.who} · ${roles[o.who]} | ${o.from === o.to ? o.from : o.from + "-" + o.to} |`),
    "",
    ...NOTES.flatMap((n, i) => [`## ${i + 1} · ${n.title}`, "", `${n.who.toUpperCase()}. ${n.t}`, ""]),
  ].join("\n");
  fs.writeFileSync(SPEECH, md, "utf8");
  console.log("OK", SPEECH);
}
build().catch((e) => { console.error(e); process.exit(1); });
