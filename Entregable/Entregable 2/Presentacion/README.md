# Presentación del Entregable 2

Dos versiones para elegir; el contenido es el mismo, la corta es un subconjunto.

| Versión | Diapositivas | Archivos | Para qué |
|---|---|---|---|
| **v4 completa** | 36 | `Casa-Oga-Entregable-2-v4-completa.html` · `.pdf` | Documento de respaldo o presentación larga (~25-30 min) |
| **v4 corta** | 16 | `Casa-Oga-Entregable-2-v4-corta.html` · `.pdf` | Presentación de pocos minutos (~8-10 min) |
| **v4 corta · modelo (final)** | — | `Casa-Oga-Entregable-2-v4-corta-modelo.html` | **Presentación final** del Entregable 2 |

**v4 (vigente):** dos diapositivas nuevas en el EDA sobre qué cambió en 2026: de dónde sale la caída (catálogo) y el salto de posiciones sin venta con menos liquidaciones (`catalogo`, `sinventa`; números en `EDA/resultados/cambio_2026.json`). **v3:** criterio explícito OK / Menor / Crítico en el mapa de calidad, mapa alineado con la Parte A, capacidad operativa medida también en test 2026, prevalencia en valores absolutos y transformaciones en la versión corta. **v3, v1 completa y v2 corta** quedan como versión anterior, sin regenerar.

**Cómo usar el HTML:** abrirlo en el navegador. Flechas, espacio o clic para avanzar · `F` pantalla completa · `N` muestra las notas del orador · `Ctrl+P` imprime a PDF (tamaño 1920×1080). Es un único archivo: las imágenes van embebidas. Las tipografías (DM Sans e IBM Plex Sans) se cargan de Google Fonts; sin internet se usa Arial.

**Qué tiene la v3 corta** (en orden): portada · mapa de calidad · por qué tratamos cada problema así · antes y después · punto de partida · de dónde sale la caída de 2026 · posiciones sin venta y liquidaciones · la pregunta del target · por qué este target · prevalencia y partición · qué ve el modelo (leakage) · las variables elegidas · las excluidas · transformaciones · capacidad operativa · próximo paso.
Quedan fuera: divisores de sección, EDA detallado (crecimiento, estacionalidad, caída 2026, cola de cobertura), detalle de los 12 hallazgos, supuesto de costo, ficha y solidez del target, ficha del dataset, mapa de riesgo, señal por variable, capital en riesgo y limitaciones. Para cambiar la selección: lista `CORTA` en `armar_html.py`.

## Cómo se genera

```
python graficos_presentacion.py   # gráficos → img/
python generar_deck.py            # una diapositiva por archivo → deck/project/slides/ + deck.json
python armar_html.py              # junta todo en los dos HTML autocontenidos
```

PDF (Edge sin ventana), desde esta carpeta:

```
python -c "import subprocess,pathlib,tempfile;e=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe';[subprocess.run([e,'--headless=new','--disable-gpu','--no-first-run','--user-data-dir='+tempfile.mkdtemp(),'--no-pdf-header-footer','--virtual-time-budget=10000','--print-to-pdf='+str(pathlib.Path(f'Casa-Oga-Entregable-2-{v}.pdf').resolve()),pathlib.Path(f'Casa-Oga-Entregable-2-{v}.html').resolve().as_uri()]) for v in ['v4-completa','v4-corta']]"
```

Si un PDF no aparece, correr de nuevo (Edge a veces falla la primera vez).

## Versión online

La v1 completa también está publicada como presentación editable: https://claude.ai/artifact/3ggL4DDAvfEwxBzwtHLVso (privada; compartir desde Share; exporta a PPTX o PDF desde Share › Export).
Usa las mismas diapositivas de `deck/project/`, pero las imágenes se referencian como `/_blob/<id>` (assets subidos al artifact; el mapeo id → archivo está en `armar_html.py`). **Si se edita online, esos cambios no vuelven a estos archivos.**
