"""
Reconstrucción de texto con superíndices y subíndices a partir de la geometría del PDF.

`pdftotext` en modo texto plano pierde los exponentes: 10⁻⁹ sale como "10−9", que es
otro número. En modo `-bbox-layout` cada palabra trae sus coordenadas, y ahí sí se
distinguen: un exponente está más arriba y en cuerpo más pequeño que el texto de su línea.

    palabra   yMin     alto
    '10'      223.73   10.04   ← texto normal
    '9'       222.08    7.01   ← elevado y pequeño = exponente

Este módulo lee el XML de `-bbox-layout` y devuelve líneas de texto con la notación
recuperada como LaTeX: 10^{-9}, m/s^{2}, x_{1}.
"""

import re
import xml.etree.ElementTree as ET
from collections import Counter

NS = {"x": "http://www.w3.org/1999/xhtml"}

# Un desplazamiento vertical cuenta como super/subíndice a partir de esta fracción
# del alto de la línea. 0.12 separa limpiamente los exponentes del ruido de renderizado.
UMBRAL_DESPLAZAMIENTO = 0.12
# El alto solo sirve para descartar delimitadores gigantes (integrales, corchetes que
# abarcan varias líneas). No puede exigirse que el exponente sea más pequeño: el glifo
# del menos matemático viene de otra fuente y su caja es más alta que la del texto,
# de modo que "10^{-9}" quedaría sin detectar.
UMBRAL_CUERPO = 1.45


class Palabra:
    __slots__ = ("texto", "x0", "y0", "x1", "y1")

    def __init__(self, texto, x0, y0, x1, y1):
        self.texto = texto
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1

    @property
    def alto(self):
        return self.y1 - self.y0


class Linea:
    """Una línea del PDF con su texto reconstruido y su posición en la página."""

    def __init__(self, palabras, pagina):
        self.palabras = palabras
        self.pagina = pagina
        self.texto = _reconstruir(palabras)

    @property
    def y0(self):
        return min(p.y0 for p in self.palabras) if self.palabras else 0.0

    @property
    def x0(self):
        return min(p.x0 for p in self.palabras) if self.palabras else 0.0

    def __repr__(self):
        return f"Linea(p{self.pagina}, {self.texto!r})"


def _linea_base(palabras):
    """Alto y posición del cuerpo de texto dominante de la línea.

    Se toma la moda del alto redondeado, no el promedio: si media línea son exponentes
    el promedio se contamina, la moda no. Con empate gana el cuerpo más grande, que es
    siempre el texto normal.
    """
    altos = Counter(round(p.alto, 1) for p in palabras)
    alto_base = max(altos.items(), key=lambda kv: (kv[1], kv[0]))[0]
    candidatas = [p for p in palabras if abs(p.alto - alto_base) < 0.55]
    if not candidatas:
        candidatas = palabras
    y0_base = min(p.y0 for p in candidatas)
    return alto_base, y0_base


def _clasificar(palabra, alto_base, y0_base):
    """'normal', 'sup' o 'sub' según dónde se apoya la palabra respecto a su línea."""
    if alto_base <= 0:
        return "normal"
    desplazamiento = (y0_base - palabra.y0) / alto_base
    mas_pequena = palabra.alto < alto_base * UMBRAL_CUERPO

    if desplazamiento > UMBRAL_DESPLAZAMIENTO and mas_pequena:
        return "sup"
    if not mas_pequena:
        return "normal"
    # Un subíndice baja respecto a la línea; se compara contra la base inferior para no
    # confundirlo con letras que descuelgan (g, p, y) y que conservan el cuerpo completo.
    if desplazamiento < -UMBRAL_DESPLAZAMIENTO and mas_pequena:
        return "sub"
    return "normal"


def _envolver(texto, clase):
    marca = "^" if clase == "sup" else "_"
    texto = texto.strip()
    if not texto:
        return ""
    return f"{marca}{{{texto}}}"


def _reconstruir(palabras):
    """Une las palabras de una línea marcando exponentes y subíndices como LaTeX."""
    if not palabras:
        return ""

    palabras = sorted(palabras, key=lambda p: p.x0)
    alto_base, y0_base = _linea_base(palabras)

    partes = []
    buffer_texto = []
    buffer_clase = None
    x_previo = None

    def volcar():
        nonlocal buffer_texto, buffer_clase
        if not buffer_texto:
            return
        crudo = " ".join(buffer_texto)
        if buffer_clase == "normal":
            partes.append((crudo, False))
        else:
            # El super/subíndice se pega a lo anterior, sin espacio de por medio.
            partes.append((_envolver(crudo, buffer_clase), True))
        buffer_texto = []
        buffer_clase = None

    for p in palabras:
        clase = _clasificar(p, alto_base, y0_base)
        # Un hueco horizontal grande rompe la racha aunque la clase coincida:
        # son dos exponentes distintos, no uno solo.
        salto = x_previo is not None and (p.x0 - x_previo) > alto_base * 0.6
        if clase != buffer_clase or (salto and clase != "normal"):
            volcar()
            buffer_clase = clase
        buffer_texto.append(p.texto)
        x_previo = p.x1

    volcar()

    salida = ""
    for texto, pegado in partes:
        if not salida or pegado:
            salida += texto
        else:
            salida += " " + texto
    return _limpiar(salida)


_REEMPLAZOS = [
    ("−", "-"),      # menos matemático
    ("×", " \\times "),
    ("·", " \\cdot "),
    ("ﬀ", "ff"), ("ﬁ", "fi"), ("ﬂ", "fl"),
    ("ﬃ", "ffi"), ("ﬄ", "ffl"),
    ("‘", "'"), ("’", "'"),
    ("“", '"'), ("”", '"'),
    ("–", "-"), ("—", "--"),
]


def _limpiar(texto):
    for viejo, nuevo in _REEMPLAZOS:
        texto = texto.replace(viejo, nuevo)
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


# Caracteres de control que pdftotext emite sin escapar cuando el PDF usa fuentes de
# símbolos (delimitadores grandes, integrales). Son XML inválido y revientan el parser.
# Se sustituyen por U+FFFD para poder marcar después las preguntas que los contienen.
_CONTROL_INVALIDO = re.compile(
    rb"[\x00-\x08\x0b\x0c\x0e-\x1f]"
)


def _sanear(ruta_xml):
    crudo = open(ruta_xml, "rb").read()
    limpio, sustituciones = _CONTROL_INVALIDO.subn("�".encode("utf-8"), crudo)
    return limpio, sustituciones


def _agrupar_en_lineas(palabras, pagina):
    """Reagrupa las palabras de una página en líneas de lectura.

    No se puede confiar en los elementos <line> que emite pdftotext: cuando un exponente
    queda muy desplazado lo saca a una línea propia. Así, el "2" de "4 m/s²" aparecía
    suelto y la pregunta terminaba diciendo "acelera a 4 m/s", que es otra física.

    Se reconstruye en dos pasadas: primero las líneas del cuerpo de texto, agrupadas por
    su base; después las palabras pequeñas —los super y subíndices— se pegan a la línea
    con la que más se solapan verticalmente.
    """
    if not palabras:
        return []

    altos = Counter(round(p.alto, 1) for p in palabras)
    alto_cuerpo = max(altos.items(), key=lambda kv: (kv[1], kv[0]))[0] or 10.0

    es_pequena = lambda p: p.alto < alto_cuerpo * 0.85
    cuerpo = [p for p in palabras if not es_pequena(p)]
    pequenas = [p for p in palabras if es_pequena(p)]

    # Las líneas del cuerpo se agrupan por su base (y1), que es estable dentro de una
    # misma línea aunque cambie la fuente de algún símbolo.
    grupos = []
    for p in sorted(cuerpo, key=lambda p: (p.y1, p.x0)):
        if grupos and abs(p.y1 - grupos[-1]["y1"]) <= alto_cuerpo * 0.4:
            g = grupos[-1]
            g["palabras"].append(p)
            g["y0"] = min(g["y0"], p.y0)
            g["y1"] = max(g["y1"], p.y1)
        else:
            grupos.append({"palabras": [p], "y0": p.y0, "y1": p.y1})

    for p in pequenas:
        mejor, mejor_solape = None, 0.0
        for g in grupos:
            solape = min(p.y1, g["y1"]) - max(p.y0, g["y0"])
            if solape > mejor_solape:
                mejor, mejor_solape = g, solape
        # Se exige un solape mínimo para no arrastrar una palabra suelta de otra línea.
        if mejor is not None and mejor_solape > p.alto * 0.3:
            mejor["palabras"].append(p)
        else:
            grupos.append({"palabras": [p], "y0": p.y0, "y1": p.y1})

    grupos.sort(key=lambda g: g["y0"])
    return [Linea(g["palabras"], pagina) for g in grupos]


def leer_lineas(ruta_xml):
    """Devuelve todas las líneas del documento, en orden de lectura."""
    from io import BytesIO

    limpio, sustituciones = _sanear(ruta_xml)
    if sustituciones:
        print(f"  aviso: {sustituciones} glifos ilegibles marcados con �")

    lineas = []
    pagina = 0
    acumulado = []
    for evento, elem in ET.iterparse(BytesIO(limpio), events=("start", "end")):
        etiqueta = elem.tag.split("}")[-1]
        if evento == "start" and etiqueta == "page":
            pagina += 1
            acumulado = []
        elif evento == "end" and etiqueta == "word":
            if (elem.text or "").strip():
                acumulado.append(
                    Palabra(
                        elem.text,
                        float(elem.get("xMin")), float(elem.get("yMin")),
                        float(elem.get("xMax")), float(elem.get("yMax")),
                    )
                )
        elif evento == "end" and etiqueta == "page":
            lineas.extend(_agrupar_en_lineas(acumulado, pagina))
            acumulado = []
            elem.clear()
    return lineas
