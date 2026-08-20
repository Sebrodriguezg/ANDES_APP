"""
Extractor del GRE Physics Practice Test (forma GR1775) del ETS.

Es el examen oficial de práctica del GRE de física. Vale por dos razones: son
preguntas reales del formato de opción múltiple cronometrado, y la clave trae
el porcentaje de aspirantes que acertó cada una, así que se sabe cuáles son
difíciles de verdad y no solo cuáles lo parecen.

La dificultad del PDF es que está maquetado **a dos columnas**. Leerlo en orden
lineal intercala las preguntas: la 61 aparece partida por la mitad de la 63. Se
separan por su posición horizontal, que es exactamente para lo que sirve leer
la geometría en vez del texto plano.

La clave de respuestas ya está transcrita en 06_SEGUIMIENTO/claves/.

Uso:
    python3 extraer_ets.py
    python3 extraer_ets.py --muestra 4
"""

import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

import geometria

RAIZ = Path(__file__).resolve().parents[2]
PDF = RAIZ / "01_EXAMENES/gre_physics/ETS_Practice_Book_Physics.pdf"
CLAVE = RAIZ / "06_SEGUIMIENTO/claves/ets_gr1775.csv"
CACHE = Path(__file__).parent / "_cache"
SALIDA = Path(__file__).parent / "crudo" / "ets.json"

# La frontera entre columnas. La página mide 612 pt y el corte cae holgado
# entre el final de la columna izquierda y el comienzo de la derecha.
CORTE_COLUMNA = 300

RE_PREGUNTA = re.compile(r"^(\d{1,3})\.\s+(.*)$")
RE_OPCION = re.compile(r"^\(([A-E])\)\s*(.*)$")
RE_FIGURA = re.compile(
    r"\b(figure above|figures above|shown above|graph above|diagram above|"
    r"represented in the figure|as shown|above shows)\b", re.I)

# Pie de página que pdftotext mezcla con la última opción de cada columna.
RE_PIE = re.compile(r"\s*GRE\s*[®\u00ae]?\s*Physics Test Practice Book.*$", re.I)

# La clave deja 27 preguntas como "otros". Se clasifican por lo que dice el
# enunciado, que para el examen de Uniandes importa: el reparto por áreas es lo
# que decide cuánto pesa cada tema en el feed y en los simulacros.
PISTAS_AREA = [
    ("optica_ondas", r"\b(lens|telescope|microscope|diffraction|interference|"
                     r"polariz|refract|wavelength of light|mirror|optical)\b"),
    ("termo_estadistica", r"\b(entropy|thermodynamic|temperature|heat|carnot|"
                          r"ideal gas|partition function|boltzmann|adiabatic|"
                          r"specific heat)\b"),
    ("relatividad", r"\b(relativis|lorentz|rest frame|speed of light|"
                    r"time dilation|proper time|quasar)\b"),
    ("moderna_cuantica", r"\b(quantum|electron|photon|atom|nucle|orbital|"
                         r"spin|wave function|hydrogen|decay|eigen)\b"),
    ("electromagnetismo", r"\b(charge|current|capacit|magnetic|electric|"
                          r"circuit|resistor|voltage|inductan|field)\b"),
    ("mecanica", r"\b(mass|velocity|momentum|force|energy|pendulum|orbit|"
                 r"friction|rotat|oscillat|collision|spring)\b"),
]


def clasificar_area(enunciado, opciones, area_clave):
    if area_clave and area_clave not in ("otros", "area", ""):
        return area_clave
    texto = f"{enunciado} {' '.join(opciones.values())}"
    for area, patron in PISTAS_AREA:
        if re.search(patron, texto, re.I):
            return area
    return "transversal"


LETRAS = ["A", "B", "C", "D", "E"]


def cargar_clave():
    """Número de pregunta -> (respuesta, % que acertó, área, nivel)."""
    clave = {}
    with CLAVE.open(encoding="utf-8") as fh:
        for fila in csv.DictReader(fh):
            clave[int(fila["pregunta"])] = {
                "respuesta": fila["correcta"].strip().upper(),
                "p_acierto": int(fila["p_mas"]) if fila.get("p_mas") else None,
                "area": fila.get("area", "").strip(),
                "nivel": fila.get("nivel", "").strip() or "BASE",
            }
    return clave


def extraer(ruta_xml, clave):
    lineas = geometria.leer_lineas(ruta_xml, corte_columna=CORTE_COLUMNA)

    preguntas = []
    actual = None
    campo = None
    descartes = {"sin_clave": 0, "opciones_incompletas": 0, "depende_de_figura": 0,
                 "enunciado_corto": 0}

    def cerrar():
        nonlocal actual, campo
        if actual is None:
            return
        num = actual["numero"]
        enunciado = RE_PIE.sub("", " ".join(actual["enunciado"])).strip()
        opciones = {k: RE_PIE.sub("", " ".join(v)).strip()
                    for k, v in actual["opciones"].items()}

        actual, campo = None, None

        if num not in clave:
            descartes["sin_clave"] += 1
            return
        if len(opciones) < 5 or any(not v for v in opciones.values()):
            descartes["opciones_incompletas"] += 1
            return
        if len(enunciado) < 15:
            descartes["enunciado_corto"] += 1
            return
        if RE_FIGURA.search(enunciado + " " + " ".join(opciones.values())):
            descartes["depende_de_figura"] += 1
            return

        info = clave[num]
        if info["respuesta"] not in opciones:
            descartes["sin_clave"] += 1
            return

        preguntas.append({
            "id": f"ets-gr1775-q{num:03d}",
            "fuente": "ETS-GR1775",
            "fuente_larga": "ETS · GRE Physics Practice Test, forma GR1775",
            "idioma": "en",
            "numero": num,
            "enunciado": enunciado,
            "opciones": opciones,
            "respuesta": info["respuesta"],
            "area": clasificar_area(enunciado, opciones, info["area"]),
            "nivel": info["nivel"],
            "semana": None,
            "etiquetas": ["gre"],
            # Cuántos aspirantes la acertaron: sirve para saber si fallarla es
            # normal o es una señal.
            "p_acierto": info["p_acierto"],
            "capitulo_titulo": "GRE Physics",
        })

    for linea in lineas:
        texto = linea.texto.strip()
        if not texto:
            continue

        m = RE_OPCION.match(texto)
        if m and actual is not None:
            campo = m.group(1)
            actual["opciones"].setdefault(campo, []).append(m.group(2))
            continue

        m = RE_PREGUNTA.match(texto)
        # Solo abre pregunta nueva si el número avanza: los números sueltos
        # dentro de un enunciado no deben partirlo.
        if m and (actual is None or int(m.group(1)) > actual["numero"]):
            numero = int(m.group(1))
            if numero in clave:
                cerrar()
                actual = {"numero": numero, "enunciado": [m.group(2)], "opciones": {}}
                campo = "enunciado"
                continue

        if actual is None:
            continue
        if campo == "enunciado":
            actual["enunciado"].append(texto)
        elif campo in actual["opciones"]:
            actual["opciones"][campo].append(texto)

    cerrar()
    return preguntas, descartes


# El PDF del ETS también pierde notación, pero de otra manera que el de HRW.
# Aquí los glifos sí llegan: llegan como caracteres de área de uso privado,
# porque la fuente los codifica en el rango de Symbol y no hay tabla que los
# traduzca. Son tres apariciones en todo el banco, y el contexto las identifica
# sin margen de duda.
PUA = {
    # "the ℓ = 2 state" y "the quantum number m_{ℓ}". Sin esto la pregunta 10
    # pierde justo la variable por la que pregunta.
    "\uf06c": "ℓ",
    # "How many states have energy (7/2) ℏω". Con eta el enunciado no dice nada;
    # con hache barrada sale la degeneración 6 que registra la clave.
    "\uf068": "ℏ",
}

# Pérdidas de verdad, no PUA: el glifo no llegó y se repone declarándolo.
CORRECCIONES = {
    # La micro de microsegundo. Con milisegundos la partícula recorrería 450 km
    # y ninguna opción pasa de 750 m; con microsegundos sale justo la opción
    # registrada, 450 m.
    "ets-gr1775-q029": [("decays in 2.0 ms", "decays in 2.0 µs")],
}


def corregir(tarjeta):
    """Traduce los caracteres de uso privado y aplica lo declarado a mano."""
    def limpiar(texto):
        for crudo, bueno in PUA.items():
            texto = texto.replace(crudo, bueno)
        return texto

    tarjeta["enunciado"] = limpiar(tarjeta["enunciado"])
    tarjeta["opciones"] = {k: limpiar(v) for k, v in tarjeta["opciones"].items()}
    for viejo, nuevo in CORRECCIONES.get(tarjeta["id"], []):
        tarjeta["enunciado"] = tarjeta["enunciado"].replace(viejo, nuevo)
    return tarjeta


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--muestra", type=int, metavar="N")
    args = ap.parse_args()

    if not PDF.exists():
        sys.exit(f"No encuentro el PDF: {PDF}")

    CACHE.mkdir(exist_ok=True)
    xml = CACHE / "ets.xml"
    if not xml.exists():
        print("Extrayendo geometría...")
        subprocess.run(["pdftotext", "-bbox-layout", str(PDF), str(xml)], check=True)

    clave = cargar_clave()
    preguntas, descartes = extraer(xml, clave)

    if args.muestra:
        import random
        random.seed(3)
        for p in random.sample(preguntas, min(args.muestra, len(preguntas))):
            print(f"\n--- {p['id']}  [{p['area']} · {p['nivel']}] "
                  f"acertó el {p['p_acierto']} %")
            print(f"    {p['enunciado'][:220]}")
            for k, v in p["opciones"].items():
                marca = "<<<" if k == p["respuesta"] else "   "
                print(f"      ({k}) {v[:60]} {marca}")
        return

    SALIDA.parent.mkdir(exist_ok=True)
    preguntas = [corregir(x) for x in preguntas]
    SALIDA.write_text(json.dumps(preguntas, ensure_ascii=False, indent=1),
                      encoding="utf-8")

    print(f"\n{len(preguntas)} preguntas de {len(clave)} en la clave "
          f"-> {SALIDA.relative_to(RAIZ)}")
    for motivo, n in sorted(descartes.items(), key=lambda kv: -kv[1]):
        if n:
            print(f"  {n:4d}  {motivo}")

    from collections import Counter
    print("\nPor área:")
    for area, n in Counter(p["area"] for p in preguntas).most_common():
        print(f"  {n:4d}  {area}")


if __name__ == "__main__":
    main()
