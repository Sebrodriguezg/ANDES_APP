"""
La Hoja definitiva: todo el material de repaso en una sola página autocontenida.

Lee las mismas fuentes que alimentan la app —los cuatro JSON de `autoral/`— y
produce un HTML que no depende de nada externo: las fuentes van incrustadas en
base64 y KaTeX también, porque la hoja tiene que abrir sin conexión el 22 de
noviembre por la noche.

Decisiones que conviene dejar dichas:

- **Latin Modern** para todo. Es Computer Modern, la tipografía de los papers de
  física. Sus cortes de texto no traen griego ni operadores —eso vive en
  `latinmodern-math`—, así que la cascada es texto primero, matemática después.
- Los super e subíndices Unicode de la prosa (`10⁻¹⁰`, `Ω_A`) se convierten a
  `<sup>` y `<sub>` reales, porque esos glifos tampoco existen en Latin Modern y
  además así componen mejor.
- La paleta inferno del proyecto se usa como **escala de calor de riesgo**: lo
  que falló en el diagnóstico D1 sale caliente, lo dominado sale frío. El color
  codifica estado, no decora.

Uso:
    python3 hoja_definitiva.py
    python3 hoja_definitiva.py --salida /otra/ruta.html
"""

import argparse
import base64
import html
import json
import re
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
AUTORAL = RAIZ / "07_APP" / "autoral"
KATEX = RAIZ / "docs" / "vendor" / "katex"
SALIDA = RAIZ / "04_ESTUDIO" / "formularios" / "hoja_definitiva.html"

# Los cortes subseteados. Se generan con pyftsubset desde Latin Modern; el
# script que los produjo vive en el cuaderno de trabajo, y los .woff2 quedan
# aquí para que la hoja se pueda regenerar sin TeX Live instalado.
FUENTES = Path(__file__).parent / "fuentes_hoja"

EXAMEN = date(2026, 11, 23)

# strftime("%B") depende de la configuración regional y aquí devuelve inglés.
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def en_castellano(d):
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"

AREAS = {
    "mecanica": ("Mecánica", "mec"),
    "electromagnetismo": ("Electromagnetismo", "em"),
    "relatividad": ("Relatividad", "em"),
    "termo_estadistica": ("Termodinámica y estadística", "ter"),
    "moderna_cuantica": ("Cuántica y moderna", "cua"),
    "optica_ondas": ("Óptica y ondas", "opt"),
    "transversal": ("Transversal", "tra"),
}

# El reparto, el expediente del D1 y el protocolo viven en autoral/examen.json
# porque la vista Hoja de la app lee exactamente lo mismo. Si estuvieran fijos
# aquí, corregir una nota obligaría a tocar dos sitios y a que se desincronicen.
EXAMEN_JSON = json.loads((AUTORAL / "examen.json").read_text(encoding="utf-8"))


SUPER = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱ", "0123456789+-=()ni")
SUB = str.maketrans("₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₒₓ", "0123456789+-=()aeox")
FRACCIONES = {"½": "1/2", "⅓": "1/3", "⅔": "2/3", "¼": "1/4", "¾": "3/4",
              "⅕": "1/5", "⅖": "2/5", "⅗": "3/5", "⅘": "4/5", "⅙": "1/6",
              "⅚": "5/6", "⅛": "1/8", "⅜": "3/8", "⅝": "5/8", "⅞": "7/8"}

RE_SUPER = re.compile(r"[⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱ]+")
RE_SUB = re.compile(r"[₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₒₓ]+")
# Subíndice escrito con guion bajo: Ω_A, m_C, k_B, ε_ijk, y también la forma
# con llaves E_{Rydberg}. Solo cuando va pegado a una letra, para no tocar nada
# más —los nombres de área como `termo_estadistica` no pasan por aquí.
RE_GUION = re.compile(r"(?<=[A-Za-zΑ-Ωα-ω])_(?:\{([^{}]{1,12})\}|([A-Za-z0-9]{1,4})\b)")
RE_FUERTE = re.compile(r"\*\*(.+?)\*\*")
RE_CURSIVA = re.compile(r"(?<!\*)\*(?!\*)([^*]+?)\*(?!\*)")


def prosa(texto):
    """Prosa a HTML: negritas, fracciones y super/subíndices reales."""
    for cru, limpio in FRACCIONES.items():
        texto = texto.replace(cru, limpio)
    texto = html.escape(texto)
    texto = RE_FUERTE.sub(r"<strong>\1</strong>", texto)
    texto = RE_CURSIVA.sub(r"<em>\1</em>", texto)
    texto = RE_SUPER.sub(lambda m: f"<sup>{m.group().translate(SUPER)}</sup>", texto)
    texto = RE_SUB.sub(lambda m: f"<sub>{m.group().translate(SUB)}</sub>", texto)
    texto = RE_GUION.sub(lambda m: f"<sub>{m.group(1) or m.group(2)}</sub>", texto)
    return texto


def b64(ruta, mime="font/woff2"):
    return f"data:{mime};base64," + base64.b64encode(ruta.read_bytes()).decode()


def cara(familia, archivo, peso="400", estilo="normal"):
    return (f"@font-face{{font-family:'{familia}';src:url({b64(FUENTES / archivo)}) "
            f"format('woff2');font-weight:{peso};font-style:{estilo};font-display:block}}")


def fuentes_css():
    """Las siete caras de Latin Modern más la de símbolos, incrustadas."""
    partes = [
        cara("LM Roman", "roman.woff2"),
        cara("LM Roman", "roman-bold.woff2", "700"),
        cara("LM Roman", "roman-italic.woff2", "400", "italic"),
        cara("LM Sans", "sans.woff2"),
        cara("LM Sans", "sans-bold.woff2", "700"),
        cara("LM Sans", "sans-italic.woff2", "400", "italic"),
        cara("LM Mono", "mono.woff2"),
        # Griego y operadores. Va al final de cada pila como respaldo.
        cara("LM Simbolos", "simbolos.woff2"),
    ]
    return "".join(partes)


def katex_css():
    """El CSS de KaTeX con sus veinte fuentes metidas como data URI."""
    css = (KATEX / "katex.min.css").read_text(encoding="utf-8")

    def sustituir(m):
        nombre = m.group(1)
        f = KATEX / "fonts" / nombre
        return f"url({b64(f)}) format('woff2')" if f.exists() else "local('x')"

    # Solo sobrevive el woff2; los url() de woff y ttf se quedarían colgando.
    css = re.sub(r"url\(fonts/([^)]+\.woff2)\)\s*format\(['\"]woff2['\"]\)",
                 sustituir, css)
    css = re.sub(r",\s*url\(fonts/[^)]+\.(?:woff|ttf)\)\s*format\(['\"][^'\"]+['\"]\)",
                 "", css)
    return css


def formulas(lista):
    """Las entradas que empiezan por # son rótulos; el resto es TeX."""
    fuera = []
    for linea in lista:
        if linea.startswith("#"):
            fuera.append(f'<p class="rotulo">{prosa(linea[1:].strip())}</p>')
        else:
            fuera.append(f'<div class="tex" data-tex="{html.escape(linea)}"></div>')
    return "".join(fuera)


def ficha_patron(p):
    estado = p.get("estado_d1")
    clase = {"fallado": "falla", "acertado": "acierta"}.get(estado, "virgen")
    marca = {"fallado": "Fallado en el D1",
             "acertado": "Acertado en el D1"}.get(estado, "Sin evaluar aún")
    area, _ = AREAS[p["area"]]
    return f"""
<article class="patron {clase}" id="{p['patron']}">
  <header>
    <span class="num">{p['patron']}</span>
    <div class="cab">
      <h3>{prosa(p['titulo'])}</h3>
      <p class="meta"><span class="area a-{AREAS[p['area']][1]}">{area}</span>
         <span class="sem">{p['semana']}</span>
         <span class="estado">{marca}</span></p>
    </div>
  </header>
  <p class="idea">{prosa(p['idea'])}</p>
  <div class="cajaformula">{formulas(p['formula'])}</div>
  <div class="notas">
    <div class="nota"><h4>Cuándo aparece</h4><p>{prosa(p['cuando'])}</p></div>
    <div class="nota trampa"><h4>La trampa</h4><p>{prosa(p['trampa'])}</p></div>
  </div>
</article>"""


def ficha_ecuacion(e):
    return f"""
<article class="ecuacion" id="{e['id']}">
  <h3>{prosa(e['titulo'])}</h3>
  <div class="cajaformula">{formulas(e['formula'])}</div>
  <p class="significa">{prosa(e['significa'])}</p>
  <p class="trampilla"><span>Trampa</span> {prosa(e['trampa'])}</p>
</article>"""


def ficha_dato(d):
    filas = []
    for linea in d["tabla"].split("\n"):
        if not linea.strip():
            filas.append('<tr class="hueco"><td colspan="2"></td></tr>')
            continue
        # Las tablas vienen como "clave = valor" o "clave: valor" o alineadas.
        m = re.match(r"^(.*?)\s{2,}(.+)$", linea) or re.match(r"^(.*?[:=])\s*(.+)$", linea)
        if m:
            filas.append(f"<tr><td>{prosa(m.group(1).rstrip(':'))}</td>"
                         f"<td>{prosa(m.group(2))}</td></tr>")
        else:
            filas.append(f'<tr><td colspan="2">{prosa(linea)}</td></tr>')
    return f"""
<article class="dato" id="{d['id']}">
  <h3>{prosa(d['titulo'])}</h3>
  <p class="porque">{prosa(d['porque'])}</p>
  <table>{''.join(filas)}</table>
</article>"""


def ficha_descarte(x):
    falsas = "".join(f"<li>{prosa(o)}</li>" for o in x["opciones_falsas"])
    marca = ('<span class="estado falla">Lo fallaste en el D1</span>'
             if x.get("estado_d1") == "fallado" else "")
    return f"""
<article class="descarte" id="{x['id']}">
  <header>
    <span class="tecnica">{prosa(x['tecnica'])}</span>{marca}
  </header>
  <h3>{prosa(x['titulo'])}</h3>
  <p class="situacion">{prosa(x['situacion'])}</p>
  <p class="muere">Muere por descarte</p>
  <ul class="falsas">{falsas}</ul>
  <p class="conclusion">{prosa(x['conclusion'])}</p>
  <p class="regla"><span>La regla</span> {prosa(x['regla'])}</p>
</article>"""


def tabla_d1():
    filas = []
    for p in EXAMEN_JSON["d1"]["preguntas"]:
        lento = " lento" if p.get("lento") else ""
        etiqueta = (f'<span class="pat">{p["patron"]}</span>'
                    if p.get("patron") else "")
        filas.append(f"""<tr class="{'bien' if p['ok'] else 'mal'}">
  <td class="n">{p['n']}</td>
  <td class="tema">{prosa(p['tema'])} {etiqueta}</td>
  <td class="resp"><span>{p['tuya']}</span></td>
  <td class="resp buena"><span>{p['buena']}</span></td>
  <td class="t{lento}">{p['tiempo']}</td>
  <td class="conf c{p['confianza']}">{p['confianza']}</td>
  <td class="nota">{prosa(p['nota'])}</td>
</tr>""")
    return "".join(filas)


def construir(doctype=True):
    patrones = json.loads((AUTORAL / "patrones.json").read_text(encoding="utf-8"))
    ecuaciones = json.loads((AUTORAL / "ecuaciones.json").read_text(encoding="utf-8"))
    datos = json.loads((AUTORAL / "datos.json").read_text(encoding="utf-8"))
    descartes = json.loads((AUTORAL / "descarte.json").read_text(encoding="utf-8"))

    # Las ecuaciones se agrupan por área, en el orden en que caen en el examen.
    orden = ["mecanica", "electromagnetismo", "termo_estadistica", "relatividad",
             "moderna_cuantica", "optica_ondas", "transversal"]
    grupos = []
    for a in orden:
        del_area = [e for e in ecuaciones if e["area"] == a]
        if del_area:
            grupos.append((AREAS[a][0], AREAS[a][1],
                           "".join(ficha_ecuacion(e) for e in del_area)))

    barra = "".join(
        f'<div class="tramo t-{AREAS[r["area"]][1]}" style="flex:{r["pct"]}">'
        f'<span class="pc">{r["pct"]}%</span>'
        f'<span class="nb">{prosa(r["nombre"])}</span>'
        f'<span class="np">{r["preguntas"]} preg.</span></div>'
        for r in EXAMEN_JSON["reparto"])

    protocolo = "".join(
        f'<li><h4>{prosa(r["titulo"])}</h4><p>{prosa(r["texto"])}</p></li>'
        for r in EXAMEN_JSON["protocolo"])

    avisos = "".join(
        f'<div class="aviso"><h4>{prosa(a["titulo"])}</h4>'
        f'<p>{prosa(a["texto"])}</p></div>'
        for a in EXAMEN_JSON["d1"]["avisos"])

    fallados = sum(1 for p in patrones if p.get("estado_d1") == "fallado")
    acertados = sum(1 for p in patrones if p.get("estado_d1") == "acertado")
    virgenes = len(patrones) - fallados - acertados

    plantilla = (Path(__file__).parent / "hoja_definitiva.css").read_text(encoding="utf-8")

    # Dos cabeceras que no son opcionales:
    #
    # - El charset. Sin él el navegador decodifica en latin-1 y la prosa se
    #   llena de mojibake.
    # - El DOCTYPE. Sin él la página va en *quirks mode* y KaTeX se niega a
    #   renderizar —literalmente devuelve "KaTeX doesn't work in quirks
    #   mode"—, así que las fórmulas salen en crudo. Se omite solo cuando la
    #   hoja se publica como artifact, porque allí el envoltorio lo pone.
    cabecera = "<!DOCTYPE html>\n" if doctype else ""

    return f"""{cabecera}<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hoja definitiva</title>
<style>{fuentes_css()}</style>
<style>{katex_css()}</style>
<style>{plantilla}</style>

<a class="saltar" href="#patrones">Ir a los patrones</a>

<header class="portada">
  <p class="sello">Maestría en Física · Universidad de los Andes</p>
  <h1>Hoja definitiva</h1>
  <p class="bajada">Todo lo que hay que tener en la cabeza el 22 de noviembre por
     la noche. Los diez patrones, las ecuaciones que sostienen el resto, las
     constantes, las cuatro formas de descartar sin calcular, y el expediente de
     lo que ya falló una vez.</p>
  <dl class="instrumento">
    <div><dt>Faltan</dt><dd id="cuenta">—</dd><dd class="u">días</dd></div>
    <div><dt>Preguntas</dt><dd>25</dd><dd class="u">opción múltiple</dd></div>
    <div><dt>Tiempo</dt><dd>3</dd><dd class="u">horas</dd></div>
    <div><dt>Por pregunta</dt><dd>7,2</dd><dd class="u">minutos</dd></div>
  </dl>
  <p class="fecha">Examen: lunes 23 de noviembre de 2026 ·
     sin penalización por error</p>
</header>

<nav class="indice">
  <a href="#reparto">Reparto</a>
  <a href="#patrones">Los diez patrones</a>
  <a href="#ecuaciones">Ecuaciones</a>
  <a href="#constantes">Constantes</a>
  <a href="#descarte">Descarte</a>
  <a href="#expediente">Expediente D1</a>
  <a href="#protocolo">Protocolo</a>
</nav>

<main>

<section id="reparto">
  <h2><span class="ord">01</span> Cómo se reparte el examen</h2>
  <div class="barra">{barra}</div>
  <p class="lectura">Poco más de la mitad se responde con Física 1–2 bien hecha y
     rápida: <strong>ahí es donde se aprueba</strong>. El resto son patrones de
     pregrado superior, que no son difíciles <em>si los has visto</em> y son
     imposibles <em>si no</em>. Óptica no apareció en el simulacro de 2024 pese a
     estar en el temario.</p>
</section>

<section id="patrones">
  <h2><span class="ord">02</span> Los diez patrones</h2>
  <p class="entrada">Si el 22 de noviembre solo alcanza para repasar diez cosas,
     son estas. Cada una se estudia una vez y se memoriza como patrón; después
     se resuelven de memoria. El color dice cómo te fue en el diagnóstico:
     <span class="clave falla">{fallados} fallados</span>
     <span class="clave acierta">{acertados} acertados</span>
     <span class="clave virgen">{virgenes} sin evaluar</span>.</p>
  <div class="patrones">{''.join(ficha_patron(p) for p in patrones)}</div>
</section>

<section id="ecuaciones">
  <h2><span class="ord">03</span> Las ecuaciones que sostienen el resto</h2>
  <p class="entrada">Estas no son los patrones caros: son el 60 % del examen,
     lo que hay que tener automatizado para que sobre tiempo.</p>
  {''.join(f'<div class="grupo"><h3 class="areatitulo a-{c}">{n}</h3>{f}</div>'
           for n, c, f in grupos)}
</section>

<section id="constantes">
  <h2><span class="ord">04</span> Constantes, atajos y órdenes de magnitud</h2>
  <div class="datos">{''.join(ficha_dato(d) for d in datos)}</div>
</section>

<section id="descarte">
  <h2><span class="ord">05</span> Descartar sin calcular</h2>
  <p class="entrada">Cuatro técnicas y ocho casos. En un examen de opción
     múltiple sin penalización, descartar es tan valioso como resolver, y cuesta
     un cuarto del tiempo.</p>
  <div class="descartes">{''.join(ficha_descarte(x) for x in descartes)}</div>
</section>

<section id="expediente">
  <h2><span class="ord">06</span> Tu expediente del D1</h2>
  <p class="entrada">{en_castellano(date.fromisoformat(EXAMEN_JSON['d1']['fecha']))}.
     {EXAMEN_JSON['d1']['aciertos']} de {EXAMEN_JSON['d1']['total']}, con
     {EXAMEN_JSON['d1']['minutos_usados']} minutos de
     {EXAMEN_JSON['d1']['minutos_disponibles']}. El
     resultado salió invertido respecto a lo normal —<strong>{EXAMEN_JSON['d1']['base']}
     en lo básico y {EXAMEN_JSON['d1']['alto']} en lo de posgrado</strong>— y eso
     importa más que el porcentaje:
     lo caro de construir sigue ahí, y lo que falta es óxido, que se quita en
     semanas.</p>
  <div class="tablaenvoltura">
  <table class="d1">
    <thead><tr><th>#</th><th>Tema</th><th>Tú</th><th>Buena</th><th>Tiempo</th>
      <th>Conf.</th><th>Qué pasó</th></tr></thead>
    <tbody>{tabla_d1()}</tbody>
  </table>
  </div>
  <div class="avisos">{avisos}</div>
</section>

<section id="protocolo">
  <h2><span class="ord">07</span> Protocolo del día</h2>
  <p class="entrada">Seis reglas, todas sacadas de lo que pasó en el
     diagnóstico y no de un manual.</p>
  <ol class="protocolo">{protocolo}</ol>
</section>

</main>

<footer>
  <p>Generada el {en_castellano(date.today())} desde el
     corpus de <span class="mono">ANDES</span> ·
     {len(patrones)} patrones · {len(ecuaciones)} bloques de ecuaciones ·
     {len(datos)} tablas de datos · {len(descartes)} casos de descarte</p>
  <p class="chico">Se regenera con <span class="mono">python3
     07_APP/tuberia/hoja_definitiva.py</span></p>
</footer>

<script>{(KATEX / 'katex.min.js').read_text(encoding='utf-8')}</script>
<script>
(function () {{
  // La cuenta atrás se calcula en el navegador para que no envejezca.
  var examen = new Date(2026, 10, 23);
  var hoy = new Date(); hoy.setHours(0, 0, 0, 0);
  var dias = Math.round((examen - hoy) / 86400000);
  var casilla = document.getElementById('cuenta');
  casilla.textContent = dias > 0 ? dias : (dias === 0 ? 'hoy' : '—');

  function marcarAncha(nodo) {{
    var alFinal = nodo.scrollLeft + nodo.clientWidth >= nodo.scrollWidth - 2;
    nodo.classList.toggle(
      'ancha', nodo.scrollWidth > nodo.clientWidth + 2 && !alFinal);
  }}

  document.querySelectorAll('.tex').forEach(function (nodo) {{
    try {{
      katex.render(nodo.dataset.tex, nodo, {{
        displayMode: true, throwOnError: false, strict: false
      }});
    }} catch (e) {{
      nodo.textContent = nodo.dataset.tex;
      nodo.classList.add('crudo');
    }}
    marcarAncha(nodo);
    nodo.addEventListener('scroll', function () {{ marcarAncha(nodo); }},
                          {{ passive: true }});
  }});
  addEventListener('resize', function () {{
    document.querySelectorAll('.tex').forEach(marcarAncha);
  }});

  // El índice marca la sección en la que estás.
  var enlaces = Array.prototype.slice.call(
    document.querySelectorAll('.indice a'));
  var vigia = new IntersectionObserver(function (entradas) {{
    entradas.forEach(function (e) {{
      if (!e.isIntersecting) return;
      enlaces.forEach(function (a) {{
        a.classList.toggle('aqui', a.getAttribute('href') === '#' + e.target.id);
      }});
    }});
  }}, {{ rootMargin: '-20% 0px -70% 0px' }});
  document.querySelectorAll('main section').forEach(function (s) {{
    vigia.observe(s);
  }});
}})();
</script>"""


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--salida", type=Path, default=SALIDA)
    ap.add_argument("--sin-doctype", action="store_true",
                    help="para publicar como artifact, que ya pone el suyo")
    args = ap.parse_args()

    args.salida.parent.mkdir(parents=True, exist_ok=True)
    pagina = construir(doctype=not args.sin_doctype)
    args.salida.write_text(pagina, encoding="utf-8")

    kb = len(pagina.encode()) / 1024
    try:
        donde = args.salida.relative_to(RAIZ)
    except ValueError:            # --salida puede apuntar fuera del repositorio
        donde = args.salida
    print(f"{donde}  ·  {kb:.0f} KB")
    print(f"Faltan {(EXAMEN - date.today()).days} días para el examen.")


if __name__ == "__main__":
    main()
