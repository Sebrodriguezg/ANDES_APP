"""
Extractor del ejemplo de examen de admisión de Uniandes 2024.

Es la única muestra que existe del examen real, y por eso vale más que
cualquier otro banco: es el molde exacto —enunciado en español, cinco opciones,
"Answer: ______"— contra el que está calibrado todo el plan.

Dos particularidades obligan a tratarlo distinto del resto:

1. **Las opciones son imágenes.** El PDF trae "a." "b." "c." "d." "e." como
   texto y las fórmulas como gráficos, así que extraer texto da cinco opciones
   vacías. Se recorta la franja que va del final del enunciado hasta antes de
   "Answer:", que contiene la figura del problema y las cinco alternativas.

2. **No trae la clave.** El Departamento no publica respuestas. Las que se usan
   aquí son las derivadas al analizar el diagnóstico D1, y van marcadas como
   tales: son razonadas, no oficiales.

Uso:
    python3 extraer_uniandes.py
"""

import argparse
import csv
import io
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

import geometria

RAIZ = Path(__file__).resolve().parents[2]
PDF = RAIZ / "01_EXAMENES/uniandes_admision/2024_ejemplo_examen_admision_MC.pdf"
MAPA = RAIZ / "06_SEGUIMIENTO/mapas/uniandes_2024.csv"
RESPUESTAS = RAIZ / "06_SEGUIMIENTO/datos/respuestas.csv"
CACHE = Path(__file__).parent / "_cache"
SALIDA = Path(__file__).parent / "crudo" / "uniandes.json"

DPI = 150
ESCALA = DPI / 72.0
ANCHO_MAX = 760
ANCHO_PAGINA = 612
ALTO_PAGINA = 792

RE_PREGUNTA = re.compile(r"^(\d{1,2})\.\s+(.*)$")
RE_OPCION = re.compile(r"^([a-e])\.\s*(.*)$")
RE_ANSWER = re.compile(r"^Answer\s*:", re.I)

LETRAS = ["A", "B", "C", "D", "E"]


def cargar_mapa():
    """Área, nivel, tema y patrón de cada pregunta, del análisis del simulacro."""
    mapa = {}
    if not MAPA.exists():
        return mapa
    with MAPA.open(encoding="utf-8") as fh:
        for fila in csv.DictReader(fh):
            mapa[int(fila["pregunta"])] = {
                "area": fila.get("area", "").strip(),
                "tema": fila.get("tema", "").strip(),
                "nivel": fila.get("nivel", "BASE").strip(),
                "patron": fila.get("patron", "").strip() or None,
            }
    return mapa


def cargar_claves():
    """Respuestas derivadas al analizar el diagnóstico D1.

    No son oficiales: el Departamento no publica la clave. Se dedujeron
    resolviendo cada pregunta, y en el análisis quedaron dos con salvedad
    explícita. Van marcadas para que se sepa lo que se está usando.
    """
    claves = {}
    if not RESPUESTAS.exists():
        return claves
    with RESPUESTAS.open(encoding="utf-8") as fh:
        for fila in csv.DictReader(fh):
            correcta = (fila.get("correcta") or "").strip().upper()
            if correcta in LETRAS:
                claves[int(fila["pregunta"])] = correcta
    return claves


def localizar(lineas):
    """Para cada pregunta: página, texto del enunciado y franja de las opciones."""
    bloques = {}
    actual = None

    def cerrar(y_fin):
        if actual and actual["y_opciones"] is not None:
            bloques[actual["numero"]] = {
                "pagina": actual["pagina"],
                "enunciado": " ".join(actual["enunciado"]).strip(),
                "y0": actual["y_opciones"],
                "y1": y_fin,
            }

    for linea in lineas:
        texto = linea.texto.strip()
        if not texto:
            continue

        m = RE_PREGUNTA.match(texto)
        if m:
            cerrar(linea.y0)
            actual = {
                "numero": int(m.group(1)), "pagina": linea.pagina,
                "enunciado": [m.group(2)], "y_opciones": None,
            }
            continue

        if actual is None:
            continue

        if RE_ANSWER.match(texto):
            cerrar(linea.y0)
            actual = None
            continue

        m = RE_OPCION.match(texto)
        if m:
            # La franja de opciones empieza en la primera de ellas. Si la
            # pregunta trae figura, queda dentro y eso es lo que se quiere.
            if actual["y_opciones"] is None:
                actual["y_opciones"] = linea.y0 - 4
            continue

        # Solo se acumula enunciado antes de que empiecen las opciones.
        if actual["y_opciones"] is None:
            actual["enunciado"].append(texto)

    return bloques


def recortar(pagina, y0, y1):
    """Renderiza la franja de opciones y la ajusta al contenido."""
    y0, y1 = max(0, y0), min(ALTO_PAGINA, y1)
    if y1 - y0 < 20:
        return None

    salida = CACHE / "uni_recorte"
    subprocess.run(
        ["pdftoppm", "-png", "-r", str(DPI), "-f", str(pagina), "-l", str(pagina),
         "-x", "0", "-y", str(int(y0 * ESCALA)),
         "-W", str(int(ANCHO_PAGINA * ESCALA)),
         "-H", str(int((y1 - y0) * ESCALA)), str(PDF), str(salida)],
        check=True, capture_output=True)

    generados = sorted(CACHE.glob("uni_recorte*.png"))
    if not generados:
        return None

    with Image.open(generados[0]) as im:
        im = im.convert("L")
        caja = Image.eval(im, lambda p: 255 - p).getbbox()
        if not caja:
            for g in generados:
                g.unlink()
            return None
        pad = 10
        caja = (max(0, caja[0] - pad), max(0, caja[1] - pad),
                min(im.width, caja[2] + pad), min(im.height, caja[3] + pad))
        recorte = im.crop(caja)
        if recorte.width > ANCHO_MAX:
            alto = round(recorte.height * ANCHO_MAX / recorte.width)
            recorte = recorte.resize((ANCHO_MAX, alto), Image.LANCZOS)
        buf = io.BytesIO()
        recorte.save(buf, format="PNG", optimize=True, bits=4)
        datos, dims = buf.getvalue(), recorte.size

    for g in generados:
        g.unlink()
    return datos, dims


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()

    if not PDF.exists():
        sys.exit(f"No encuentro el PDF: {PDF}")

    CACHE.mkdir(exist_ok=True)
    xml = CACHE / "uniandes.xml"
    if not xml.exists():
        subprocess.run(["pdftotext", "-bbox-layout", str(PDF), str(xml)], check=True)

    import base64
    lineas = geometria.leer_lineas(xml)
    bloques = localizar(lineas)
    mapa = cargar_mapa()
    claves = cargar_claves()

    preguntas = []
    sin_clave = sin_imagen = 0

    for numero in sorted(bloques):
        b = bloques[numero]
        if numero not in claves:
            sin_clave += 1
            continue

        res = recortar(b["pagina"], b["y0"], b["y1"])
        if not res:
            sin_imagen += 1
            continue
        datos, (an, al) = res

        info = mapa.get(numero, {})
        preguntas.append({
            "id": f"uniandes2024-q{numero:02d}",
            "fuente": "Uniandes2024",
            "fuente_larga": "Uniandes · ejemplo de examen de admisión a posgrado, 2024",
            "idioma": "es",
            "numero": numero,
            "enunciado": b["enunciado"],
            # Vacías a propósito: las alternativas están dentro de la imagen.
            "opciones": {l: "" for l in LETRAS},
            "respuesta": claves[numero],
            "clave_derivada": True,
            "area": info.get("area") or "sin_clasificar",
            "nivel": info.get("nivel") or "BASE",
            "patron": info.get("patron"),
            "semana": None,
            "etiquetas": ["examen-real"],
            "capitulo_titulo": info.get("tema", "Examen de admisión 2024"),
            "figura": {"png": base64.b64encode(datos).decode(),
                       "ancho": an, "alto": al, "incierta": False},
        })

    SALIDA.parent.mkdir(exist_ok=True)
    SALIDA.write_text(json.dumps(preguntas, ensure_ascii=False), encoding="utf-8")

    peso = sum(len(p["figura"]["png"]) for p in preguntas)
    print(f"{len(preguntas)} preguntas de {len(bloques)} localizadas "
          f"-> {SALIDA.relative_to(RAIZ)}")
    print(f"  {sin_clave} sin clave derivada del D1")
    if sin_imagen:
        print(f"  {sin_imagen} sin imagen de opciones")
    print(f"  {peso/1024:.0f} kB de imágenes")


if __name__ == "__main__":
    main()
