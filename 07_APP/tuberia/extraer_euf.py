"""
Extractor del EUF, el examen unificado de posgrado en física de Brasil.

De los 35 exámenes descargados solo uno sirve, y conviene dejar dicho por qué:

- Los anteriores a 2020 son de desarrollo, no de opción múltiple. Sus "(a) (b)
  (c)" son apartados de un problema largo, no alternativas.
- Los cerrados de 2020-2 en adelante están compuestos en LaTeX con fuentes
  Type 1 sin tabla ToUnicode, así que `pdftotext` no puede mapear los glifos:
  el de 2023-1 devuelve diecinueve palabras en todo el documento, y son "sinh",
  "cosh" y "tanh". No hay enunciado que recuperar sin OCR.
- El de 2020-1 sí tiene capa de texto, y además trae la respuesta correcta
  marcada con [C] junto a la opción. El gabarito viene incorporado.

Son 52 preguntas. Menos de las que se esperaban, pero de la misma familia que
el examen de Uniandes: opción múltiple de nivel posgrado, en un idioma que se
lee sin esfuerzo desde el español.

Uso:
    python3 extraer_euf.py
    python3 extraer_euf.py --muestra 3
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import geometria

RAIZ = Path(__file__).resolve().parents[2]
PDF = RAIZ / "01_EXAMENES/otros_bancos/euf_brasil/EUF_euf-2020-1.pdf"
SALIDA = Path(__file__).parent / "crudo" / "euf.json"

# El "Q1." va en negrita y algo elevado respecto al párrafo, así que la lectura
# por geometría lo envuelve como superíndice: "^{Q1.} Uma partícula…".
RE_PREGUNTA = re.compile(r"^\s*\^?\{?\s*Q(\d+)\.\s*\}?\s*(.*)$")
RE_OPCION = re.compile(r"^\s*\(([a-e])\)\s*(.*)$")
# La marca de respuesta correcta que trae este examen.
RE_CORRECTA = re.compile(r"\s*\[C\]\s*")

# En Computer Modern el radical es la letra "p" de una fuente de símbolos, y
# sale elevada respecto a la línea. Leyendo por geometría queda en su sitio
# —"x_{0} = +^{p} b/a"— y de ahí se recupera como raíz. Con `pdftotext -layout`
# esas "p" acababan sueltas al final del renglón y la fórmula decía otra cosa:
# "x0 = + b/a e ω = 4b/m p p".
RE_RADICAL = re.compile(r"\^\{p\}\s*")

# Las fracciones en display quedan como numerador y denominador apilados:
# "v(t) =_{k}^{b}" es b/k. Se pasan a barra, que se lee de corrido.
RE_FRACCION = re.compile(r"_\{([^{}]{1,6})\}\^\{([^{}]{1,6})\}"
                         r"|\^\{([^{}]{1,6})\}_\{([^{}]{1,6})\}")

ILEGIBLE = "\ufffd"

LETRAS = {"a": "A", "b": "B", "c": "C", "d": "D", "e": "E"}

# El EUF no rotula las áreas, así que se clasifica por el enunciado. En
# portugués, que se parece lo bastante al español como para que las pistas
# sean casi las mismas.
PISTAS = [
    ("termo_estadistica", r"\b(entropia|termodin|temperatura|calor|gás ideal|"
                          r"boltzmann|adiabátic|isotérmic|partição)\b"),
    ("relatividad", r"\b(relativ|lorentz|referencial|velocidade da luz|"
                    r"dilatação|méson|fóton de energia)\b"),
    ("moderna_cuantica", r"\b(quântic|hamiltonian|autoestado|autovalor|"
                         r"função de onda|spin|elétron|átomo|orbital|"
                         r"schrödinger|nível de energia|poço)\b"),
    ("optica_ondas", r"\b(óptic|onda|interferência|difração|polariza|"
                     r"refração|lente|espelho|comprimento de onda)\b"),
    ("electromagnetismo", r"\b(campo elétric|campo magnétic|carga|corrente|"
                          r"capacit|circuito|potencial elétric|indutân|"
                          r"maxwell|dipolo)\b"),
    ("mecanica", r"\b(massa|velocidade|partícula|força|lagrangiana|momento|"
                 r"oscila|pêndulo|órbita|atrito|energia cinética|colisão)\b"),
]


def clasificar(texto):
    for area, patron in PISTAS:
        if re.search(patron, texto, re.I):
            return area
    return "transversal"


def _barra(m):
    """De numerador y denominador apilados a una fracción con barra."""
    if m.group(1) is not None:
        abajo, arriba = m.group(1), m.group(2)
    else:
        arriba, abajo = m.group(3), m.group(4)
    return f" ({arriba}/{abajo}) "


def limpiar(texto):
    texto = RE_CORRECTA.sub(" ", texto)
    texto = RE_RADICAL.sub("√", texto)
    texto = RE_FRACCION.sub(_barra, texto)
    return re.sub(r"\s+", " ", texto).strip()


def extraer(crudo):
    preguntas = []
    actual = None
    campo = None
    descartes = {"sin_respuesta": 0, "opciones_incompletas": 0,
                 "sin_enunciado": 0, "glifo_ilegible": 0}

    def cerrar():
        nonlocal actual, campo
        if actual is None:
            return
        enunciado = limpiar(" ".join(actual["enunciado"]))
        opciones = {LETRAS[k]: limpiar(" ".join(v))
                    for k, v in actual["opciones"].items()}
        respuesta = actual["respuesta"]
        numero = actual["numero"]
        actual, campo = None, None

        if len(enunciado) < 25:
            descartes["sin_enunciado"] += 1
            return
        if len(opciones) < 5 or any(not v for v in opciones.values()):
            descartes["opciones_incompletas"] += 1
            return
        if not respuesta:
            descartes["sin_respuesta"] += 1
            return
        # Glifos que pdftotext no supo mapear: la fórmula ya no dice lo mismo.
        if ILEGIBLE in enunciado + " ".join(opciones.values()):
            descartes["glifo_ilegible"] += 1
            return

        preguntas.append({
            "id": f"euf-2020a-q{numero:03d}",
            "fuente": "EUF2020-1",
            "fuente_larga": "EUF · Exame Unificado das Pós-graduações em Física, 2020-1",
            "idioma": "pt",
            "numero": numero,
            "enunciado": enunciado,
            "opciones": opciones,
            "respuesta": respuesta,
            "area": clasificar(enunciado + " " + " ".join(opciones.values())),
            "nivel": "ALTO",
            "semana": None,
            "etiquetas": ["euf", "posgrado"],
            "capitulo_titulo": "EUF 2020-1",
        })

    for linea in crudo.split("\n"):
        if not linea.strip():
            continue

        m = RE_PREGUNTA.match(linea)
        if m:
            cerrar()
            actual = {"numero": int(m.group(1)), "enunciado": [m.group(2)],
                      "opciones": {}, "respuesta": None}
            campo = "enunciado"
            continue

        if actual is None:
            continue

        m = RE_OPCION.match(linea)
        if m:
            campo = m.group(1)
            actual["opciones"].setdefault(campo, []).append(m.group(2))
            # La marca [C] puede venir en la misma línea o en la siguiente.
            if RE_CORRECTA.search(linea):
                actual["respuesta"] = LETRAS[campo]
            continue

        if campo == "enunciado":
            actual["enunciado"].append(linea.strip())
        elif campo in actual["opciones"]:
            actual["opciones"][campo].append(linea.strip())
            if RE_CORRECTA.search(linea):
                actual["respuesta"] = LETRAS[campo]

    cerrar()
    return preguntas, descartes


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--muestra", type=int, metavar="N")
    args = ap.parse_args()

    if not PDF.exists():
        sys.exit(f"No encuentro el PDF: {PDF}")

    xml = Path(__file__).parent / "_cache" / "euf2020a.xml"
    xml.parent.mkdir(exist_ok=True)
    if not xml.exists():
        subprocess.run(["pdftotext", "-bbox-layout", str(PDF), str(xml)], check=True)

    crudo = "\n".join(l.texto for l in geometria.leer_lineas(xml))
    preguntas, descartes = extraer(crudo)

    if args.muestra:
        for p in preguntas[:args.muestra]:
            print(f"\n--- {p['id']}  [{p['area']}]")
            print(f"    {p['enunciado'][:260]}")
            for k, v in p["opciones"].items():
                marca = "<<<" if k == p["respuesta"] else "   "
                print(f"      ({k}) {v[:66]} {marca}")
        return

    SALIDA.parent.mkdir(exist_ok=True)
    SALIDA.write_text(json.dumps(preguntas, ensure_ascii=False, indent=1),
                      encoding="utf-8")

    from collections import Counter
    print(f"{len(preguntas)} preguntas -> {SALIDA.relative_to(RAIZ)}")
    for motivo, n in descartes.items():
        if n:
            print(f"  {n:3d}  {motivo}")
    print("\nPor área:")
    for area, n in Counter(p["area"] for p in preguntas).most_common():
        print(f"  {n:3d}  {area}")


if __name__ == "__main__":
    main()
