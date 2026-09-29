# -*- coding: utf-8 -*-
"""
Arma la presentacion como UN solo archivo HTML autocontenido (imagenes embebidas en base64).
Lee las diapositivas que genera generar_deck.py (deck/project/slides/*.html).

Salidas en esta carpeta:
  Casa-Oga-Entregable-2-v4-completa.html  (36 diapositivas)
  Casa-Oga-Entregable-2-v4-corta.html     (17 diapositivas)
Navegacion: flechas / espacio / clic · F pantalla completa · N notas del orador.
"""
import os, re, json, base64

BASE = os.path.dirname(os.path.abspath(__file__))
SL = os.path.join(BASE, "deck", "project", "slides")
ORDEN = json.load(open(os.path.join(BASE, "deck", "project", "deck.json"), encoding="utf-8"))["order"]
CORTA = ["portada", "partida", "catalogo", "cola", "sinventa", "mapa", "criterios", "antesdespues", "pregunta", "candidatos",
         "prevalencia", "leakage", "grupos", "excluidas", "transformaciones", "capacidad", "proximo"]

# /_blob/<id> -> archivo local (mismos ids que devolvio la subida de assets)
BLOBS = {"3c2223f1d1c6339c830ee806884f8f61": "c01_venta_mensual.png", "43c6981580a79beb1efb8097927605a1": "c02_estacionalidad.png",
         "b86da51072ea5789fd601d99c350ca93": "c03_cobertura_def.png", "b58994c3ddc7a35522592cd3d9b3ddac": "c04_venta_2526.png",
         "d8a92d1eff15dc35bd290d5587c533b5": "c05_cola_cobertura.png", "7905fa8d85c212d9ad87118976873099": "c06_prevalencia.png",
         "19331e5df80e782e71bbf913d9c492d9": "c07_capacidad.png", "2d7fd4a01dc83c89b21d974d6364c15d": "c08_senal.png",
         "bdc99ef4d31e9129611313178b39539e": "c09_antes_despues.png", "e786bd0172083880f96c23d1f3375cf5": "c10_capital_rojo.png",
         "a1c11e0000000000000000000000c011": "c11_caida_catalogo.png", "a1c12e0000000000000000000000c012": "c12_sin_venta_liquidaciones.png"}
DATA = {k: "data:image/png;base64," + base64.b64encode(open(os.path.join(BASE, "img", v), "rb").read()).decode()
        for k, v in BLOBS.items()}

TPL = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITULO__</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400..700&family=IBM+Plex+Sans:wght@400;600;700&display=swap">
<style>
*{box-sizing:border-box;margin:0}
html,body{height:100%;background:#0B1120;overflow:hidden}
#stage{position:absolute;left:50%;top:50%;width:1920px;height:1080px;transform-origin:0 0}
#stage>section{position:absolute;left:0;top:0;width:1920px;height:1080px;visibility:hidden;overflow:hidden}
#stage>section.on{visibility:visible}
section p{line-height:1.4}section h3{line-height:1.2}
section aside{display:none}
section h1,section h2,section h3,section p{margin:0}
section table{border-collapse:collapse}
section th,section td{padding:10px 14px;text-align:left;border-bottom:1px solid #D9DDE4;vertical-align:top}
section th{font-weight:700;color:#14213D}
#bar{position:fixed;left:0;bottom:0;height:4px;background:#F5B800;transition:width .2s}
#notes{position:fixed;left:16px;right:16px;bottom:16px;max-height:30vh;overflow:auto;background:rgba(15,23,42,.94);color:#E2E8F0;
  font:15px/1.5 system-ui,sans-serif;padding:14px 18px;border-radius:10px;display:none}
#hint{position:fixed;right:14px;top:10px;color:#64748B;font:12px system-ui,sans-serif}
@media print{html,body{overflow:visible;background:#fff}#stage{position:static;transform:none!important}
  #stage>section{visibility:visible!important;position:relative;page-break-after:always}#bar,#notes,#hint{display:none!important}
  @page{size:1920px 1080px;margin:0}}
</style></head><body>
<div id="stage">
__SLIDES__
</div>
<div id="bar"></div><div id="notes"></div><div id="hint">← → navegar · F pantalla completa · N notas</div>
<script>
const S=[...document.querySelectorAll('#stage>section')];let i=0;
try{const h=parseInt(location.hash.slice(1));if(h>0&&h<=S.length)i=h-1}catch(e){}
const notes=document.getElementById('notes');let showN=false;
function fit(){const st=document.getElementById('stage');const k=Math.min(innerWidth/1920,innerHeight/1080);
  st.style.transformOrigin='50% 50%';st.style.transform=`translate(-50%,-50%) scale(${k})`;}
function go(n){i=Math.max(0,Math.min(S.length-1,n));S.forEach((s,j)=>s.classList.toggle('on',j===i));
  document.getElementById('bar').style.width=((i+1)/S.length*100)+'%';history.replaceState(null,'','#'+(i+1));
  const a=S[i].querySelector('aside');notes.textContent=a?a.textContent:'(sin notas)';notes.style.display=showN?'block':'none';}
addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' ','Enter'].includes(e.key)){e.preventDefault();go(i+1)}
  else if(['ArrowLeft','PageUp','Backspace'].includes(e.key)){e.preventDefault();go(i-1)}
  else if(e.key==='Home')go(0);else if(e.key==='End')go(S.length-1);
  else if(e.key==='f'||e.key==='F'){document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen()}
  else if(e.key==='n'||e.key==='N'){showN=!showN;go(i)}});
addEventListener('click',e=>{if(e.target.closest('#notes'))return;go(e.clientX>innerWidth/3?i+1:i-1)});
addEventListener('resize',fit);fit();go(i);setTimeout(()=>document.getElementById('hint').style.display='none',4000);
</script></body></html>"""

def armar(ids, titulo, archivo):
    partes = []
    for k, sid in enumerate(ids, start=1):
        h = open(os.path.join(SL, sid + ".html"), encoding="utf-8").read()
        h = re.sub(r"/_blob/([0-9a-f]{32})", lambda m: DATA[m.group(1)], h)
        h = re.sub(r"(Grupo 1 &#160;·&#160; )\d+(</p>)", lambda m: f"{m.group(1)}{k} / {len(ids)}{m.group(2)}", h)
        h = h.replace("<section ", '<section class="" ', 1)
        partes.append(h)
    out = TPL.replace("__TITULO__", titulo).replace("__SLIDES__", "\n".join(partes))
    open(os.path.join(BASE, archivo), "w", encoding="utf-8").write(out)
    print(f"{archivo}: {len(ids)} diapositivas · {os.path.getsize(os.path.join(BASE, archivo))/1e6:.1f} MB")

armar(ORDEN, "Casa Óga · Entregable 2 · versión completa", "Casa-Oga-Entregable-2-v4-completa.html")
armar(CORTA, "Casa Óga · Entregable 2 · versión corta", "Casa-Oga-Entregable-2-v4-corta.html")
