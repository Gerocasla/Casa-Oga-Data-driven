# Presentación del Entregable 2

Dos versiones para elegir; el contenido es el mismo, la corta es un subconjunto.

| Versión | Diapositivas | Archivos | Para qué |
|---|---|---|---|
| **v1 completa** | 34 | `Casa-Oga-Entregable-2-v1-completa.html` · `.pdf` | Documento de respaldo o presentación larga (~25-30 min) |
| **v2 corta** | 14 | `Casa-Oga-Entregable-2-v2-corta.html` · `.pdf` | Presentación de pocos minutos (~8-10 min) |

**Cómo usar el HTML:** abrirlo en el navegador. Flechas, espacio o clic para avanzar · `F` pantalla completa · `N` muestra las notas del orador · `Ctrl+P` imprime a PDF (tamaño 1920×1080). Es un único archivo: las imágenes van embebidas. Las tipografías (DM Sans e IBM Plex Sans) se cargan de Google Fonts; sin internet se usa Arial.

**Qué tiene la v2 corta** (en orden): portada · punto de partida · la cola de cobertura en 2026 · mapa de calidad · por qué tratamos cada problema así · antes y después · la pregunta del target · por qué este target · prevalencia y partición · qué ve el modelo (leakage) · las 67 variables · las excluidas · capacidad operativa · próximo paso.
Quedan fuera: divisores de sección, EDA detallado (crecimiento, estacionalidad, caída 2026), detalle de los 12 hallazgos, supuesto de costo, ficha y solidez del target, ficha del dataset, transformaciones, mapa de riesgo, señal por variable, capital en riesgo y limitaciones. Para cambiar la selección: lista `CORTA` en `armar_html.py`.

## Cómo se genera

```
python graficos_presentacion.py   # gráficos → img/
python generar_deck.py            # una diapositiva por archivo → deck/project/slides/ + deck.json
python armar_html.py              # junta todo en los dos HTML autocontenidos
```

PDF (Edge sin ventana), desde esta carpeta:

```
python -c "import subprocess,pathlib,tempfile;e=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe';[subprocess.run([e,'--headless=new','--disable-gpu','--no-first-run','--user-data-dir='+tempfile.mkdtemp(),'--no-pdf-header-footer','--virtual-time-budget=10000','--print-to-pdf='+str(pathlib.Path(f'Casa-Oga-Entregable-2-{v}.pdf').resolve()),pathlib.Path(f'Casa-Oga-Entregable-2-{v}.html').resolve().as_uri()]) for v in ['v1-completa','v2-corta']]"
```

Si un PDF no aparece, correr de nuevo (Edge a veces falla la primera vez).

## Versión online

La v1 completa también está publicada como presentación editable: https://claude.ai/artifact/3ggL4DDAvfEwxBzwtHLVso (privada; compartir desde Share; exporta a PPTX o PDF desde Share › Export).
Usa las mismas diapositivas de `deck/project/`, pero las imágenes se referencian como `/_blob/<id>` (assets subidos al artifact; el mapeo id → archivo está en `armar_html.py`). **Si se edita online, esos cambios no vuelven a estos archivos.**
