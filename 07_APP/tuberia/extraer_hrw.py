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

# Restos de las figuras en ASCII del PDF: hileras de puntos, barras y flechas que
# `pdftotext` mezcla con el texto. Si aparecen, la pregunta viene contaminada.
RE_RESTO_FIGURA = re.compile(r"(\.\s*){4,}|[↑↓→←|]{2,}|_\{\s*\.")

ILEGIBLE = "�"

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

    def texto_enunciado(self):
        return " ".join(self.enunciado).strip()

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
            "opciones": {k: self.opciones[k].strip() for k in self.orden_opciones},
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
    if any(not v.strip() for v in preg.opciones.values()):
        descartes["opcion_vacia"] += 1
        preg.necesita_figura = True
        return False

    todo = enunciado + " " + " ".join(preg.opciones.values())
    # Las que dependen de una figura no se tiran: se apartan. Si el extractor de
    # figuras logra rescatar el dibujo, la pregunta vuelve al corpus completa.
    if RE_FIGURA.search(todo):
        descartes["depende_de_figura"] += 1
        preg.necesita_figura = True
        return False
    if RE_RESTO_FIGURA.search(todo):
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
        "enunciado_vacio": 0, "opcion_vacia": 0, "depende_de_figura": 0,
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
                actual.enunciado.append(m.group(2))
                campo = "enunciado"
                siguiente_numero = numero + 1
                continue

        if actual is None:
            continue

        m = RE_OPCION.match(texto)
        if m and m.group(1) not in actual.opciones:
            letra = m.group(1)
            actual.opciones[letra] = m.group(2)
            actual.orden_opciones.append(letra)
            campo = letra
            continue

        if campo == "enunciado":
            actual.enunciado.append(texto)
        elif campo in actual.opciones:
            actual.opciones[campo] += " " + texto

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
