"""
Extractor del banco de preguntas de Halliday/Resnick/Walker 7ª ed.

655 páginas, 44 capítulos, ~2.650 preguntas de opción múltiple con respuesta.
Es una de las fuentes reales del examen de admisión (ver 00_ADMISION/FALTANTES.md).

La estructura del documento es regular:

    Chapter 5:
    FORCE AND MOTION
    12. Un enunciado que puede ocupar
        varias líneas.
    A. primera opción
    ...
    E. quinta opción
       Ans: C

Uso:
    python3 extraer_hrw.py                 # escribe crudo/hrw.json
    python3 extraer_hrw.py --muestra 5     # imprime 5 preguntas y no escribe nada
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import geometria

RAIZ = Path(__file__).resolve().parents[2]
PDF = RAIZ / "01_EXAMENES/banco_hrw/HRW7_Test_Bank_con_respuestas.pdf"
CACHE = Path(__file__).parent / "_cache"
SALIDA = Path(__file__).parent / "crudo" / "hrw.json"
APARTADAS = Path(__file__).parent / "crudo" / "hrw_pendientes_figura.json"

RE_CAPITULO = re.compile(r"^Chapter\s+(\d+):?\s*(.*)$", re.I)
# En el pie de página el número de página alterna de lado según la paridad:
#   impares -> 'Chapter 1: MEASUREMENT 1'
#   pares   -> '58 Chapter 5: FORCE AND MOTION - I'
# Por eso aquí se busca en cualquier posición, no solo al inicio.
RE_PIE_CAPITULO = re.compile(r"Chapter\s+(\d+):?\s*(.*)$", re.I)
RE_PREGUNTA = re.compile(r"^(\d+)\.\s+(.*)$")
RE_OPCION = re.compile(r"^([A-E])\.\s*(.*)$")
RE_RESPUESTA = re.compile(r"^ans:\s*([A-E])\b", re.I)
RE_SOLO_NUMERO = re.compile(r"^\d+$")

# Una pregunta que remite a una figura no sirve sin la imagen: se descarta.
# "known below" no es un error de tipeo mío: es una errata del banco de HRW por
# "shown below", y aparece lo suficiente como para que valga la pena atraparla.
RE_FIGURA = re.compile(
    r"\b(figure|figures|shown below|known below|shown in the|the diagram|diagram shows|"
    r"diagram represents|graph below|graph shows|graph above|shown above|as shown|"
    r"the sketch|pictured|illustrated below|configurations below)\b",
    re.I,
)

# Llaves sueltas y signos de multiplicar sin operandos: lo que queda cuando una
# figura se descompone dentro del texto. Se miran aparte de RE_RESTO_FIGURA
# porque ahí no puede entrar la llave —el propio extractor genera T_{2}— pero
# un "} }" o un "\times" al borde sí delatan basura.
RE_BASURA_FORMULA = re.compile(r"\}\s*\}|(?<![\^_])\{[^{}]*\}\s*\}|"
                               r"^\s*\\times|\\times\s*$")

# Restos de las figuras en ASCII del PDF: hileras de puntos, barras y flechas que
# `pdftotext` mezcla con el texto. Si aparecen, la pregunta viene contaminada.
# Ojo: aquí no puede entrar la llave suelta. El propio extractor genera
# subíndices como T_{2}, y tratarlas como trazo parte el texto legítimo.
RE_RESTO_FIGURA = re.compile(r"(\.\s*){4,}|[↑↓→←|]{2,}|_\{\s*\.|•")

ILEGIBLE = "�"


def limpiar_trazo(texto):
    """Borra las hileras de puntos, barras y flechas dejando el texto real."""
    t = RE_RESTO_FIGURA.sub(" ", texto)
    return re.sub(r"\s+", " ", t).strip()


def truncar_en_dibujo(texto):
    """Corta el texto donde acaba la prosa y empieza el dibujo.

    Perseguir los trazos carácter a carácter no funciona: además de puntos, las
    figuras usan viñetas, llaves de subíndice y flechas, en combinaciones
    distintas en cada página. Lo que sí es estable es que la prosa termina en
    '.', '?' o ':' y todo lo que viene después es dibujo.

    Así que se busca el final de frase tras el cual ya casi no quedan letras y
    se corta ahí. Un enunciado de varias frases no se ve afectado, porque la
    cola de las primeras sigue estando llena de texto.
    """
    corte = None
    # El final de frase tiene que estar pegado a una palabra: los puntos del
    # dibujo van sueltos entre espacios y llaves, y si se admiten como corte el
    # límite se va hasta el final de la basura.
    for m in re.finditer(r"(?<=[A-Za-z0-9)\]])[.?:]\s", texto):
        cola = texto[m.end():].strip()
        if not cola:
            continue
        proporcion_letras = sum(c.isalpha() for c in cola) / len(cola)
        # O bien la cola es casi toda símbolos, o son cuatro rótulos sueltos
        # de una o dos letras, que es como se ven los ejes etiquetados.
        palabras = cola.split()
        rotulos_sueltos = len(palabras) <= 4 and all(len(p) <= 2 for p in palabras)
        # Contar letras no basta: los diagramas rotulados con números romanos
        # (I, II, III, IV, V) parecen texto y salvan la cola de ser descartada.
        # Lo que no tienen los dibujos son palabras de verdad.
        # Los comandos que genera el propio extractor no cuentan como palabras:
        # "\times" contiene "times", y una cola de puro dibujo como
        # "1 2 3 \times _{p}" pasaba por texto legítimo gracias a eso.
        cola_sin_comandos = re.sub(r"\\[a-zA-Z]+", " ", cola)
        sin_palabras = not [w for w in re.findall(r"[A-Za-z]+", cola_sin_comandos)
                            if len(w) >= 4]
        # Una hilera de puntos en la cola es trazo de los ejes, y entonces da
        # igual que después venga una palabra suelta: los rótulos del dibujo
        # ("water air", "60", "30") también son palabras.
        con_trazo = bool(RE_RESTO_FIGURA.search(cola))
        if proporcion_letras < 0.15 or rotulos_sueltos or sin_palabras or con_trazo:
            # Se guarda el corte más tardío, no el primero: el enunciado puede
            # seguir después de una frase ("...la pista. En el punto 3:") y
            # cortar en la primera se lleva por delante la pregunta de verdad.
            corte = m.end()
    return texto[:corte].strip() if corte else texto


def es_trazo(texto):
    """¿La línea es parte del dibujo y no del texto de la pregunta?

    Los ejes de las figuras están trazados con hileras de puntos y barras. Si no
    se filtran, el enunciado termina con medio dibujo pegado en forma de
    '. . . . . . . .' y el resultado es ilegible en pantalla.
    """
    return bool(RE_RESTO_FIGURA.search(texto))


def es_rotulo(texto):
    """Rótulo suelto de dentro de la figura: '1', '2 3', 'm', 'd'."""
    t = texto.strip()
    return bool(t) and len(t) <= 24 and sum(c.isalpha() for c in t) <= 3

# Los 44 capítulos repartidos entre las áreas del examen y las semanas del cronograma.
# Las semanas siguen el calendario de PLAN.md; los capítulos 43 y 44 (energía nuclear,
# quarks y cosmología) quedan fuera de alcance según la sección 3 del plan.
MAPA_CAPITULOS = {
    1:  ("mecanica",           "S1",  ["unidades", "analisis-dimensional"]),
    2:  ("mecanica",           "S1",  ["cinematica-1d"]),
    3:  ("mecanica",           "S1",  ["vectores"]),
    4:  ("mecanica",           "S1",  ["cinematica-2d", "proyectiles"]),
    5:  ("mecanica",           "S1",  ["newton"]),
    6:  ("mecanica",           "S1",  ["friccion", "circular"]),
    7:  ("mecanica",           "S1",  ["trabajo", "energia-cinetica"]),
    8:  ("mecanica",           "S1",  ["energia-potencial", "conservacion"]),
    9:  ("mecanica",           "S1",  ["momento-lineal", "colisiones", "centro-de-masa"]),
    10: ("mecanica",           "S2",  ["rotacion", "momento-de-inercia"]),
    11: ("mecanica",           "S2",  ["rodadura", "torque", "momento-angular"]),
    12: ("mecanica",           "S2",  ["equilibrio", "elasticidad"]),
    13: ("mecanica",           "S2",  ["gravitacion", "kepler"]),
    14: ("mecanica",           "S2",  ["fluidos", "bernoulli", "arquimedes"]),
    15: ("mecanica",           "S2",  ["oscilaciones", "mas", "resonancia"]),
    16: ("optica_ondas",       "S11", ["ondas", "cuerda"]),
    17: ("optica_ondas",       "S11", ["ondas", "sonido", "doppler"]),
    18: ("termo_estadistica",  "S7",  ["temperatura", "calor", "primera-ley"]),
    19: ("termo_estadistica",  "S7",  ["teoria-cinetica", "gas-ideal"]),
    20: ("termo_estadistica",  "S8",  ["entropia", "segunda-ley", "maquinas"]),
    21: ("electromagnetismo",  "S4",  ["carga", "coulomb"]),
    22: ("electromagnetismo",  "S4",  ["campo-electrico", "dipolo"]),
    23: ("electromagnetismo",  "S4",  ["gauss"]),
    24: ("electromagnetismo",  "S4",  ["potencial"]),
    25: ("electromagnetismo",  "S4",  ["capacitancia", "dielectricos"]),
    26: ("electromagnetismo",  "S5",  ["corriente", "resistencia"]),
    27: ("electromagnetismo",  "S5",  ["circuitos", "kirchhoff", "rc"]),
    28: ("electromagnetismo",  "S5",  ["campo-magnetico", "fuerza-lorentz"]),
    29: ("electromagnetismo",  "S5",  ["biot-savart", "ampere"]),
    30: ("electromagnetismo",  "S5",  ["induccion", "faraday", "inductancia"]),
    31: ("electromagnetismo",  "S6",  ["oscilaciones-em", "lc", "corriente-alterna"]),
    32: ("electromagnetismo",  "S6",  ["maxwell", "magnetismo-materia"]),
    33: ("electromagnetismo",  "S6",  ["ondas-em", "poynting", "polarizacion"]),
    34: ("optica_ondas",       "S11", ["optica-geometrica", "espejos", "lentes"]),
    35: ("optica_ondas",       "S11", ["interferencia", "young"]),
    36: ("optica_ondas",       "S11", ["difraccion", "redes"]),
    37: ("relatividad",        "S9",  ["relatividad-especial", "dilatacion", "lorentz"]),
    38: ("moderna_cuantica",   "S9",  ["fotones", "fotoelectrico", "compton", "de-broglie"]),
    39: ("moderna_cuantica",   "S10", ["pozo-de-potencial", "funcion-de-onda", "barrera"]),
    40: ("moderna_cuantica",   "S10", ["atomo", "momento-angular", "espin", "pauli"]),
    41: ("moderna_cuantica",   "S10", ["solidos", "bandas", "semiconductores"]),
    42: ("moderna_cuantica",   "S9",  ["nuclear", "decaimiento"]),
}

FUERA_DE_ALCANCE = {43, 44}


def _huella(texto):
    """Firma de un enunciado, para agrupar variantes de la misma pregunta.

    El banco de HRW repite el mismo planteamiento cambiando un número o una
    opción: 222 preguntas forman 101 familias. Son preguntas legítimas y
    distintas, pero mostrar dos de la misma familia seguidas confunde, porque
    parecen la misma con distinta respuesta.
    """
    t = re.sub(r"[\d.,]+", "#", texto.lower())
    t = re.sub(r"[^a-z# ]+", " ", t)
    return " ".join(t.split())[:110]


class Pregunta:
    def __init__(self, capitulo, titulo_capitulo, numero):
        self.capitulo = capitulo
        self.titulo_capitulo = titulo_capitulo
        self.numero = numero
        self.enunciado = []
        self.opciones = {}
        self.orden_opciones = []
        self.respuesta = None
        self.necesita_figura = False
        self.tiene_trazos = False
        self.y_trazos = []

    def _rango_dibujo(self):
        """Franja vertical de la página que ocupa el dibujo, con algo de aire."""
        if not self.y_trazos:
            return None
        return min(self.y_trazos) - 4, max(self.y_trazos) + 4

    def _limpiar(self, fragmentos):
        """Quita del texto lo que en realidad era dibujo.

        Dos cuidados que costaron una pasada en falso:

        - La limpieza es dentro de la línea, no por líneas enteras. Una misma
          línea puede llevar el final del enunciado y el comienzo de los ejes:
          "...at the center of mass of the rod? . . . . . ." Si se descarta
          entera, la pregunta pierde el final y deja de entenderse.
        - Los rótulos sueltos ("1", "2 3") se distinguen de una continuación
          corta legítima ("3:") por dónde están: solo son rótulo si caen dentro
          de la franja vertical que ocupa el dibujo.
        """
        rango = self._rango_dibujo()
        salida = []
        for i, (frag, y) in enumerate(fragmentos):
            texto = limpiar_trazo(frag)
            if not texto:
                continue
            if i and rango and rango[0] <= y <= rango[1] and es_rotulo(texto):
                continue
            salida.append(texto)
        texto = re.sub(r"\s+", " ", " ".join(salida)).strip()
        return truncar_en_dibujo(texto) if self.tiene_trazos else texto

    def texto_enunciado(self):
        return self._limpiar(self.enunciado)

    def a_dict(self):
        area, semana, etiquetas = MAPA_CAPITULOS.get(
            self.capitulo, ("sin_clasificar", None, [])
        )
        return {
            "id": f"hrw-c{self.capitulo:02d}-q{self.numero:03d}",
            "fuente": "HRW7",
            "fuente_larga": "Halliday, Resnick & Walker — Fundamentals of Physics 7ed, banco de preguntas",
            "idioma": "en",
            "capitulo": self.capitulo,
            "capitulo_titulo": self.titulo_capitulo,
            "numero": self.numero,
            "enunciado": self.texto_enunciado(),
            "familia": _huella(self.texto_enunciado()),
            "opciones": {k: self._limpiar(self.opciones[k]) for k in self.orden_opciones},
            "respuesta": self.respuesta,
            "area": area,
            "semana": semana,
            "nivel": "BASE",
            "etiquetas": etiquetas,
        }


def _es_pie_de_pagina(linea, titulo_actual):
    """Distingue el pie de página del contenido real.

    No basta con la posición: en la última línea de una página puede caer un 'Ans: B'
    legítimo. Se filtra por forma — número de página suelto, 'Chapter N:' o el título
    del capítulo repetido.
    """
    if linea.y0 <= 700:
        return False
    t = linea.texto.strip()
    if RE_SOLO_NUMERO.match(t):
        return True
    if RE_PIE_CAPITULO.search(t):
        return True
    if titulo_actual and t.upper() == titulo_actual.upper():
        return True
    return False


def _limpiar_titulo(texto):
    """Quita el número de página que viene pegado al título en el pie."""
    return re.sub(r"^\s*\d+\s+|\s+\d+\s*$", "", texto or "").strip()


def _capitulos_por_pagina(lineas):
    """Asigna capítulo a cada página leyendo el pie, no el encabezado.

    El encabezado no es de fiar: en la página 270 el banco de HRW rotula 'Chapter 19'
    lo que en realidad es el capítulo 18, y eso funde dos capítulos en uno. El pie de
    página trae el número correcto y aparece en las 655 páginas sin ambigüedad.
    """
    capitulo_de = {}
    titulos = {}
    for i, linea in enumerate(lineas):
        if linea.y0 <= 700:
            continue
        m = RE_PIE_CAPITULO.search(linea.texto.strip())
        if not m:
            continue
        num = int(m.group(1))
        capitulo_de.setdefault(linea.pagina, num)

        # El pie a veces trae el título completo y a veces solo 'Chapter N:', con el
        # título en la línea siguiente. Se conserva la variante más larga que aparezca.
        titulo = _limpiar_titulo(m.group(2))
        if not titulo and i + 1 < len(lineas):
            siguiente = lineas[i + 1]
            candidato = siguiente.texto.strip()
            if (siguiente.pagina == linea.pagina and siguiente.y0 > 700
                    and candidato and not RE_SOLO_NUMERO.match(candidato)
                    and candidato == candidato.upper()):
                titulo = _limpiar_titulo(candidato)

        if titulo and len(titulo) > len(titulos.get(num, "")):
            titulos[num] = titulo
    return capitulo_de, titulos


def _valida(preg, descartes):
    """Filtra lo que no sirve como tarjeta de estudio."""
    enunciado = preg.texto_enunciado()

    if not preg.respuesta:
        descartes["sin_respuesta"] += 1
        return False
    if len(preg.opciones) < 4:
        descartes["opciones_incompletas"] += 1
        return False
    if preg.respuesta not in preg.opciones:
        descartes["respuesta_sin_opcion"] += 1
        return False
    if len(enunciado) < 12:
        descartes["enunciado_vacio"] += 1
        return False
    # Una opción vacía delata que la pregunta traía una figura y el texto se desarmó:
    # las alternativas quedan en blanco o amontonadas todas dentro de la última.
    opciones = {k: preg._limpiar(v) for k, v in preg.opciones.items()}
    if any(not v.strip() for v in opciones.values()):
        descartes["opcion_vacia"] += 1
        preg.necesita_figura = True
        return False

    # Dos opciones idénticas hacen la pregunta imposible de responder. La
    # mayoría son erratas del propio banco de HRW —el original repite 10^{-10}
    # en las opciones C y D—, pero unas cuantas son exponentes que se
    # perdieron. En cualquiera de los dos casos no sirve para practicar.
    textos = [v.strip() for v in opciones.values() if v.strip()]
    if len(set(textos)) < len(textos):
        descartes["opciones_repetidas"] += 1
        return False

    todo = enunciado + " " + " ".join(opciones.values())
    # Las que dependen de una figura no se tiran: se apartan. Si el extractor de
    # figuras logra rescatar el dibujo, la pregunta vuelve al corpus completa.
    if RE_FIGURA.search(todo):
        descartes["depende_de_figura"] += 1
        preg.necesita_figura = True
        return False
    # Si el texto crudo tenía bastante más que lo extraído, se perdió algo por
    # el camino: enumeraciones de varias líneas que se reordenan, listas de
    # ecuaciones. Son pocas, pero una pregunta a la que le falta media premisa
    # es peor que no tenerla.
    crudo = " ".join(frag for frag, _ in preg.enunciado)
    crudo_limpio = re.sub(r"[.\s}{•]+", " ", limpiar_trazo(crudo)).strip()
    if len(crudo_limpio) > len(enunciado) * 1.45 + 40:
        descartes["texto_incompleto"] += 1
        return False

    if preg.tiene_trazos or RE_BASURA_FORMULA.search(todo):
        descartes["resto_de_figura"] += 1
        preg.necesita_figura = True
        return False
    if ILEGIBLE in todo:
        descartes["glifo_ilegible"] += 1
        return False
    if preg.capitulo in FUERA_DE_ALCANCE:
        descartes["fuera_de_alcance"] += 1
        return False
    return True


def extraer(ruta_xml):
    lineas = geometria.leer_lineas(ruta_xml)

    preguntas = []
    apartadas = []
    descartes = {
        "sin_respuesta": 0, "opciones_incompletas": 0, "respuesta_sin_opcion": 0,
        "enunciado_vacio": 0, "opcion_vacia": 0, "opciones_repetidas": 0,
        "texto_incompleto": 0,
        "depende_de_figura": 0,
        "resto_de_figura": 0, "glifo_ilegible": 0, "fuera_de_alcance": 0,
    }

    capitulo_de_pagina, titulos = _capitulos_por_pagina(lineas)

    capitulo = 0
    titulo_capitulo = ""
    actual = None
    campo = None          # 'enunciado' o la letra de la opción en curso
    siguiente_numero = 1

    def cerrar():
        nonlocal actual, campo
        if actual is not None:
            if _valida(actual, descartes):
                preguntas.append(actual)
            elif actual.necesita_figura and actual.respuesta and len(actual.opciones) >= 4:
                apartadas.append(actual)
            actual = None
            campo = None

    for linea in lineas:
        texto = linea.texto.strip()
        if not texto:
            continue

        capitulo_pagina = capitulo_de_pagina.get(linea.pagina, capitulo)
        if capitulo_pagina != capitulo:
            cerrar()
            capitulo = capitulo_pagina
            titulo_capitulo = titulos.get(capitulo, "")
            siguiente_numero = 1

        if _es_pie_de_pagina(linea, titulo_capitulo):
            continue

        # El encabezado de capítulo no aporta contenido y además viene mal numerado
        # en al menos un caso; el número ya salió del pie.
        if RE_CAPITULO.match(texto):
            continue

        m = RE_RESPUESTA.match(texto)
        if m and actual is not None:
            actual.respuesta = m.group(1).upper()
            cerrar()
            continue

        m = RE_PREGUNTA.match(texto)
        # Se exige que el número sea el que toca, para que una línea de continuación
        # que empiece por "10. " no parta la pregunta en dos. Se tolera un salto corto
        # hacia adelante —y solo si la pregunta en curso ya está completa— porque si no
        # una sola pregunta ilegible desincroniza el contador y se pierde el resto del
        # capítulo entero.
        if m:
            numero = int(m.group(1))
            completa = actual is None or len(actual.opciones) >= 4
            if numero == siguiente_numero or (
                completa and siguiente_numero < numero <= siguiente_numero + 3
            ):
                cerrar()
                actual = Pregunta(capitulo, titulo_capitulo, numero)
                actual.enunciado.append((m.group(2), linea.y0))
                campo = "enunciado"
                siguiente_numero = numero + 1
                continue

        if actual is None:
            continue

        m = RE_OPCION.match(texto)
        if m and m.group(1) not in actual.opciones:
            letra = m.group(1)
            actual.opciones[letra] = [(m.group(2), linea.y0)]
            actual.orden_opciones.append(letra)
            campo = letra
            continue

        if es_trazo(texto):
            actual.tiene_trazos = True
            actual.y_trazos.append(linea.y0)

        if campo == "enunciado":
            actual.enunciado.append((texto, linea.y0))
        elif campo in actual.opciones:
            actual.opciones[campo].append((texto, linea.y0))

    cerrar()
    return preguntas, apartadas, descartes


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--muestra", type=int, metavar="N",
                    help="imprime N preguntas y no escribe nada")
    args = ap.parse_args()

    if not PDF.exists():
        sys.exit(f"No encuentro el PDF: {PDF}")

    CACHE.mkdir(exist_ok=True)
    xml = CACHE / "hrw.xml"
    if not xml.exists():
        print("Extrayendo geometría del PDF (655 páginas)...")
        subprocess.run(["pdftotext", "-bbox-layout", str(PDF), str(xml)], check=True)

    preguntas, apartadas, descartes = extraer(xml)

    if args.muestra:
        import random
        random.seed(7)
        for p in random.sample(preguntas, min(args.muestra, len(preguntas))):
            d = p.a_dict()
            print(f"\n--- {d['id']}  [{d['area']} · {d['semana']}] "
                  f"cap.{d['capitulo']} {d['capitulo_titulo']}")
            print(f"    {d['enunciado']}")
            for k, v in d["opciones"].items():
                marca = "<<<" if k == d["respuesta"] else "   "
                print(f"      {k}. {v} {marca}")
        return

    registros = [p.a_dict() for p in preguntas]
    SALIDA.parent.mkdir(exist_ok=True)
    SALIDA.write_text(json.dumps(registros, ensure_ascii=False, indent=1), encoding="utf-8")

    pendientes = [p.a_dict() for p in apartadas]
    APARTADAS.write_text(json.dumps(pendientes, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"\n{len(registros)} preguntas -> {SALIDA.relative_to(RAIZ)}")
    print(f"{len(pendientes)} apartadas a la espera de figura -> {APARTADAS.relative_to(RAIZ)}")
    print("\nDescartadas:")
    for motivo, n in sorted(descartes.items(), key=lambda kv: -kv[1]):
        if n:
            print(f"  {n:5d}  {motivo}")

    from collections import Counter
    print("\nPor área:")
    for area, n in Counter(r["area"] for r in registros).most_common():
        print(f"  {n:5d}  {area}")


if __name__ == "__main__":
    main()
