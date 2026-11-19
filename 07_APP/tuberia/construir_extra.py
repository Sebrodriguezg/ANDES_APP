"""
Material adicional de la app: simulaciones HTML y PDF de estudio.

    python3 07_APP/tuberia/construir_extra.py

Qué hace:

- Copia las simulaciones (material propio, van en claro) a docs/extra/,
  adaptadas a la app: paleta oscura de ANDES, barra para volver y botón de
  pantalla completa en horizontal, que es como se leen en el teléfono.
- Cifra los PDF (llevan problemas de libros y recortes de ETS) con la MISMA
  clave y sal que las tandas, para que la app los abra con la clave que ya
  tiene guardada. Si construir_contenido.py regenera la sal, hay que volver a
  correr este script: lo comprueba contra el canario y se niega si no casa.
- Escribe docs/contenido/extra.json, el índice que pinta la vista Material.
"""

import base64
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cifrar import CANARIO, cifrar, derivar, descifrar, obtener_frase  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
DOCS = RAIZ / "docs"
SALIDA = DOCS / "extra"
INDICE = DOCS / "contenido" / "extra.json"

VISUAL = RAIZ / "05_SIMULACROS/uniandes/visual"

SIMULACIONES = [
    {
        "fuente": VISUAL / "metodo_de_imagenes.html",
        "titulo": "Método de las imágenes",
        "desc": "Plano, esquina de 90°, esfera a tierra, esfera neutra y cavidad. "
                "Zona de interés contra zona externa, y la solución sin conductor.",
        "area": "electromagnetismo",
        "ancho": False,
    },
    {
        "fuente": VISUAL / "efectos_de_borde_linea_plano.html",
        "titulo": "Efectos de borde: línea y plano",
        "desc": "Cuándo vale la aproximación infinita: mapa de E_finito/E_infinito "
                "y la curva log–log contra la distancia.",
        "area": "electromagnetismo",
        "ancho": True,
    },
    {
        "fuente": VISUAL / "p15_isoterma_adiabatica.html",
        "titulo": "Isoterma contra adiabática",
        "desc": "Expansión de V a 2V (problema 15 de U1): trabajos como áreas, "
                "temperatura del gas y γ ajustable. Se puede grabar.",
        "area": "termo_estadistica",
        "ancho": True,
    },
]

PDFS = [
    # (grupo, título, descripción, área, ruta)
    ("Plan", "Plan de los últimos días", "Plan día a día hasta el examen, con páginas exactas.",
     "transversal", "00_ADMISION/plan_36dias/plan_final_8dias.pdf"),
    ("Problemas resueltos", "E&M: 36 problemas resueltos",
     "Conquering, Irodov y Uniandes 2024 (n.º 9, 10, 12–15). Enunciados primero, soluciones después.",
     "electromagnetismo", "05_SIMULACROS/uniandes/problemas_dia/problemas_EM_18nov.pdf"),
    ("Simulacros Uniandes", "Simulacro U1", "25 preguntas, 3 h.", "transversal",
     "05_SIMULACROS/uniandes/simulacro_U1.pdf"),
    ("Simulacros Uniandes", "Clave U1", "Respuestas del U1.", "transversal",
     "05_SIMULACROS/uniandes/clave_U1.pdf"),
    ("Simulacros Uniandes", "Soluciones U1", "Soluciones explicadas del U1.", "transversal",
     "05_SIMULACROS/uniandes/soluciones_U1.pdf"),
    ("Simulacros Uniandes", "Simulacro U2", "90 min; la parte B está en el GR9677.", "transversal",
     "05_SIMULACROS/uniandes/simulacro_U2.pdf"),
    ("Simulacros Uniandes", "Clave U2", "Respuestas del U2.", "transversal",
     "05_SIMULACROS/uniandes/clave_U2.pdf"),
    ("Simulacros Uniandes", "Simulacro U3", "Se resuelve sobre el GR9677.", "transversal",
     "05_SIMULACROS/uniandes/simulacro_U3.pdf"),
    ("Simulacros Uniandes", "Clave U3", "Respuestas del U3.", "transversal",
     "05_SIMULACROS/uniandes/clave_U3.pdf"),
    ("Formularios", "Guía final (UNAL)", "La guía de repaso que se armó para la UNAL.",
     "transversal", "04_ESTUDIO/formularios/unal/guia_final_UNAL.pdf"),
    ("Formularios", "Referencia: analítica, E&M y termo", "Formulario de referencia.",
     "electromagnetismo", "04_ESTUDIO/formularios/unal/referencia_analitica_em_termo.pdf"),
    ("Formularios", "Referencia: cuántica y moderna", "Formulario de referencia.",
     "moderna_cuantica", "04_ESTUDIO/formularios/unal/referencia_cuantica_moderna.pdf"),
    ("Formularios", "Referencia: experimental y matemática", "Formulario de referencia.",
     "transversal", "04_ESTUDIO/formularios/unal/referencia_experimental_matematica.pdf"),
    ("Formularios", "Lista: analítica, E&M y termo", "Lista de chequeo para memorizar.",
     "electromagnetismo", "04_ESTUDIO/formularios/unal/lista_analitica_em_termo.pdf"),
    ("Formularios", "Lista: cuántica y moderna", "Lista de chequeo para memorizar.",
     "moderna_cuantica", "04_ESTUDIO/formularios/unal/lista_cuantica_moderna.pdf"),
    ("Formularios", "Lista: experimental y matemática", "Lista de chequeo para memorizar.",
     "transversal", "04_ESTUDIO/formularios/unal/lista_experimental_matematica.pdf"),
    ("Notas", "Plano inclinado", "Notas propias.", "mecanica",
     "04_ESTUDIO/notas/plano_inclinado/plano_inclinado.pdf"),
    ("Notas", "Cuña móvil", "Notas propias.", "mecanica",
     "04_ESTUDIO/notas/cuna_movil/cuna_movil.pdf"),
]

# ── Adaptación de las simulaciones ──────────────────────────────

# La app es oscura y solamente oscura: se fuerza el modo oscuro y se cambian
# los grises neutros por los violetas de inferno.
PALETA = [
    ("matchMedia('(prefers-color-scheme: dark)').matches", "true"),
    ("bg:'#1c1d20'", "bg:'#150E2B'"),
    ("grid:'#2c2d31'", "grid:'#2A1F4A'"),
    ("cond:'#3a3b40'", "cond:'#3B2C66'"),
    ("[40, 41, 46]", "[21, 14, 43]"),
]

CSS_APP = """
  /* ── ANDES: paleta de la app (va al final para ganar) ── */
  :root { --bg:#0B0718; --panel:#150E2B; --ink:#E8E2F2; --muted:#9C93B5; --line:#2A1F4A; --acc:#FCA50A; --warn:#FF4F9A; }
  .seg button.on, button.main { color:#0B0718 !important; font-weight:600; }
  main { padding-top:8px; }
  canvas { border-radius:2px !important; touch-action:pinch-zoom; }
  input[type=range], input[type=checkbox] { accent-color:#FCA50A; }
"""


def adaptar(html, sim):
    for viejo, nuevo in PALETA:
        html = html.replace(viejo, nuevo)
    html = html.replace("</style>", CSS_APP + "</style>", 1)
    html = html.replace(
        "</head>",
        '<meta name="theme-color" content="#0B0718">\n'
        '<link rel="stylesheet" href="comun.css">\n</head>',
        1,
    )
    barra = (
        '<div class="andes-barra">'
        '<a href="../index.html#material">← Material</a>'
        f'<span class="andes-titulo">{sim["titulo"]}</span>'
        '<button type="button" id="andes-completa">⤢ Pantalla completa</button>'
        "</div>\n"
    )
    aviso = (
        '<div class="andes-girar">Gira el teléfono, o toca <b>Pantalla completa</b>: '
        "el gráfico es ancho y en vertical se ve diminuto.</div>\n"
        if sim["ancho"] else ""
    )
    html = re.sub(r"<body([^>]*)>", lambda m: f"<body{m.group(1)}>\n{barra}{aviso}", html, count=1)
    html = html.replace("</body>", '<script src="comun.js"></script>\n</body>', 1)
    return html


COMUN_CSS = """/* Barra común de las simulaciones dentro de ANDES. */
.andes-barra { position:sticky; top:0; z-index:5; display:flex; align-items:center; gap:10px;
  padding:10px 16px; background:#100A22; border-bottom:1px solid #2A1F4A;
  font:14px/1.3 system-ui, sans-serif; }
.andes-barra a { color:#FCA50A; text-decoration:none; font-weight:600; white-space:nowrap; }
.andes-titulo { flex:1; color:#E8E2F2; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.andes-barra button { font:inherit; font-size:13px; padding:6px 10px; border-radius:2px;
  border:1px solid #3B2C66; background:#150E2B; color:#E8E2F2; cursor:pointer; white-space:nowrap; }
.andes-girar { display:none; margin:10px 16px 0; padding:10px 12px; border:1px solid #F37819;
  border-radius:2px; color:#E8E2F2; background:#1D1439; font:14px/1.4 system-ui, sans-serif; }
@media (orientation:portrait) and (max-width:700px) { .andes-girar { display:block; } }
@media (max-width:420px) { .andes-titulo { display:none; } }
"""

COMUN_JS = """// Pantalla completa en horizontal: así se leen los lienzos anchos en el teléfono.
(() => {
  const b = document.getElementById('andes-completa');
  if (!b) return;
  const pintar = () => { b.textContent = document.fullscreenElement ? '✕ Salir' : '⤢ Pantalla completa'; };
  b.addEventListener('click', async () => {
    try {
      if (document.fullscreenElement) { await document.exitFullscreen(); return; }
      await document.documentElement.requestFullscreen();
      await screen.orientation?.lock?.('landscape');
    } catch { /* iOS o navegador sin soporte: se queda como está */ }
  });
  document.addEventListener('fullscreenchange', pintar);
})();
"""

# ── Cifrado ─────────────────────────────────────────────────────


def clave_de_la_app():
    man = json.loads((DOCS / "contenido/manifiesto.json").read_text())
    c = man["cifrado"]
    frase, _ = obtener_frase()
    clave = derivar(frase, base64.b64decode(c["sal"]))
    if descifrar(clave, base64.b64decode(c["canario"])).decode() != CANARIO:
        sys.exit("La clave de 07_APP/.clave no casa con el canario del manifiesto.")
    return clave


def nombre_bin(ruta):
    return Path(ruta).stem.lower().replace(" ", "_") + ".bin"


def main():
    SALIDA.mkdir(exist_ok=True)
    clave = clave_de_la_app()
    items = []

    for sim in SIMULACIONES:
        html = sim["fuente"].read_text(encoding="utf-8")
        destino = SALIDA / sim["fuente"].name
        destino.write_text(adaptar(html, sim), encoding="utf-8")
        items.append({
            "tipo": "html", "grupo": "Simulaciones", "titulo": sim["titulo"],
            "desc": sim["desc"], "area": sim["area"],
            "archivo": f"extra/{destino.name}",
        })
        print(f"  html  {destino.relative_to(RAIZ)}")

    (SALIDA / "comun.css").write_text(COMUN_CSS, encoding="utf-8")
    (SALIDA / "comun.js").write_text(COMUN_JS, encoding="utf-8")

    vigentes = set()
    for grupo, titulo, desc, area, ruta in PDFS:
        fuente = RAIZ / ruta
        if not fuente.exists():
            print(f"  FALTA {ruta}")
            continue
        datos = fuente.read_bytes()
        nombre = nombre_bin(ruta)
        vigentes.add(nombre)
        (SALIDA / nombre).write_bytes(cifrar(clave, datos))
        items.append({
            "tipo": "pdf", "grupo": grupo, "titulo": titulo, "desc": desc, "area": area,
            "archivo": f"extra/{nombre}", "nombre": fuente.name,
            "kb": round(len(datos) / 1024),
        })
        print(f"  pdf   {nombre:42s} {len(datos)/1024:7.0f} kB")

    # Los .bin que ya no están en la lista se borran, para no publicar basura.
    for viejo in SALIDA.glob("*.bin"):
        if viejo.name not in vigentes:
            viejo.unlink()

    INDICE.write_text(json.dumps({"items": items}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  {len(items)} elementos → {INDICE.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
