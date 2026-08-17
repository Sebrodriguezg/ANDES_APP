"""
Extractor de las soluciones comentadas del GRE (grephysics.net).

Son 333 razonamientos escritos por físicos sobre los cuatro exámenes retirados
del GRE, cada uno etiquetado por tema: "Electromagnetism → Image Charges",
"Mechanics → Vector".

Aquí hay un límite que conviene tener claro. La idea original era emparejarlas
con sus preguntas para que, al fallar, la app explicara el porqué. No se puede:
los exámenes a los que corresponden están escaneados sin capa de texto, y los
enunciados no se pueden recuperar. Lo que sí se aprovecha es el razonamiento en
sí, como micro-lecciones de los temas que el GRE pregunta una y otra vez.

Se filtra por calidad, y con criterio estrecho a propósito:

- Fuera las que remiten a una figura que no tenemos.
- Fuera las que son sobre todo fórmula, porque el PDF viene de LaTeX y las
  ecuaciones salen destrozadas al extraer texto: "c12 ∂∂tφ2 = ∂∂xφ2".
- Quedan las que razonan en prosa, que además son las que más rinden: el 40 %
  difícil del examen se gana entendiendo el argumento, no recordando la
  fórmula.

Uso:
    python3 extraer_explicaciones.py
    python3 extraer_explicaciones.py --muestra 3
"""

import argparse
import json
import re
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
CARPETA = RAIZ / "01_EXAMENES/gre_physics"
SALIDA = Path(__file__).parent / "crudo" / "explicaciones.json"

EXAMENES = ["GR8677", "GR9277", "GR9677", "GR0177"]

# Los temas de grephysics, traducidos a las áreas del examen de Uniandes.
MAPA_AREA = {
    "mechanics": ("mecanica", "S3"),
    "electromagnetism": ("electromagnetismo", "S6"),
    "quantum mechanics": ("moderna_cuantica", "S10"),
    "atomic": ("moderna_cuantica", "S10"),
    "special relativity": ("relatividad", "S9"),
    "statistical mechanics": ("termo_estadistica", "S8"),
    "thermodynamics": ("termo_estadistica", "S7"),
    "optics": ("optica_ondas", "S11"),
    "wave phenomena": ("optica_ondas", "S11"),
    "lab methods": ("transversal", None),
    "advanced topics": ("moderna_cuantica", "S10"),
}

RE_PROBLEMA = re.compile(r"\nProblem\s+(\d+)\s*\n")
RE_TIPO = re.compile(r"Subject Type\s*\n(.+?)\n(.*)", re.S)
RE_FIGURA = re.compile(r"\b(figure|shown|diagram|above|below|as in the)\b", re.I)
RE_PIE = re.compile(r"c\s*\d{4}\s*Yosu.*$|^\d+$", re.M)
# Las frases que remiten a una opción —"as in choice (E)"— no dicen nada sin el
# enunciado. Se quita la frase entera, no solo el fragmento: recortar a media
# oración dejaba restos como "This is. (If one had to guess".
RE_FRASE_ELECCION = re.compile(r"[^.!?]*\bchoice\s*\([A-E]\)[^.!?]*[.!?]", re.I)

LARGO_MINIMO = 220
LARGO_MAXIMO = 1400


def proporcion_prosa(texto):
    """Cuánto del texto son palabras de verdad y no restos de fórmula.

    El PDF viene de LaTeX y al extraer texto las ecuaciones quedan como ruido.
    Una solución con poca prosa es ilegible; una con mucha se entiende sola.
    """
    palabras = re.findall(r"[A-Za-z]{3,}", texto)
    if not texto:
        return 0.0
    return sum(len(w) for w in palabras) / len(texto)


def limpiar(texto):
    texto = RE_PIE.sub(" ", texto)
    # El texto plano de grephysics pierde los exponentes: "10−4 m/s" era 10^{-4}.
    # Aquí no hay geometría que consultar, pero el patrón es inequívoco.
    texto = re.sub(r"\b10\s*[-−]\s*(\d+)", r"10^{-\1}", texto)
    texto = RE_FRASE_ELECCION.sub(" ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    # Se corta en el último final de frase, para no dejar la explicación a
    # medias por el recorte de longitud.
    fin = max(texto.rfind("."), texto.rfind("!"), texto.rfind("?"))
    if fin > LARGO_MINIMO * 0.6:
        texto = texto[:fin + 1]
    return texto.strip()


def extraer_de(examen):
    ruta = CARPETA / f"{examen}_solutions_grephysics.pdf"
    if not ruta.exists():
        return []
    crudo = subprocess.run(["pdftotext", str(ruta), "-"],
                           capture_output=True, text=True).stdout

    salida = []
    trozos = RE_PROBLEMA.split(crudo)
    # split deja [antes, num, cuerpo, num, cuerpo, ...]
    for i in range(1, len(trozos) - 1, 2):
        numero, cuerpo = trozos[i], trozos[i + 1]
        m = RE_TIPO.search(cuerpo)
        if not m:
            continue

        tema = m.group(1).strip()
        texto = limpiar(m.group(2))

        if not (LARGO_MINIMO <= len(texto) <= LARGO_MAXIMO):
            continue
        if RE_FIGURA.search(texto):
            continue
        if proporcion_prosa(texto) < 0.55:
            continue

        raiz = tema.split("→")[0].strip().lower()
        area, semana = MAPA_AREA.get(raiz, ("transversal", None))
        detalle = tema.split("→")[-1].strip() if "→" in tema else tema

        salida.append({
            "id": f"expl-{examen.lower()}-{int(numero):03d}",
            "tipo": "micro",
            "area": area,
            "semana": semana,
            "nivel": "ALTO",
            "titulo": detalle,
            "tema": tema,
            "texto": texto,
            "origen": f"grephysics.net · {examen}",
            "idioma": "en",
        })
    return salida


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--muestra", type=int, metavar="N")
    args = ap.parse_args()

    todas = []
    for examen in EXAMENES:
        de_este = extraer_de(examen)
        todas.extend(de_este)
        print(f"  {examen}: {len(de_este)}")

    if args.muestra:
        import random
        random.seed(9)
        for e in random.sample(todas, min(args.muestra, len(todas))):
            print(f"\n--- {e['id']}  [{e['area']}] {e['tema']}")
            print(f"    {e['texto'][:400]}")
        return

    SALIDA.parent.mkdir(exist_ok=True)
    SALIDA.write_text(json.dumps(todas, ensure_ascii=False, indent=1), encoding="utf-8")

    from collections import Counter
    print(f"\n{len(todas)} explicaciones -> {SALIDA.relative_to(RAIZ)}")
    for area, n in Counter(e["area"] for e in todas).most_common():
        print(f"  {n:4d}  {area}")


if __name__ == "__main__":
    main()
