"""
Lee los reportes de error que Sebastián manda desde la app.

La app pone en cada tarjeta un botón que copia su ficha y abre el formulario;
las respuestas caen en una hoja de cálculo pública. Esto la descarga, busca el
código de tarjeta dentro del texto del reporte y lo cruza con el corpus, para
poder ir directo a la pregunta en vez de buscarla a mano.

Uso:
    python3 reportes.py               # los reportes, del más nuevo al más viejo
    python3 reportes.py --tarjeta     # solo los que identifican una tarjeta
"""

import argparse
import csv
import io
import json
import re
import urllib.request
from pathlib import Path

HOJA = ("https://docs.google.com/spreadsheets/d/"
        "1qoFcISxsPKQZa0G-OxrvBHFkKeQj6kxWWR83nsMop3g/export?format=csv")

CRUDO = Path(__file__).parent / "crudo"
CAPTURAS = Path(__file__).parent / "_cache" / "capturas"

RE_DRIVE = re.compile(r"drive\.google\.com/open\?id=([\w-]+)|/file/d/([\w-]+)")

# Los códigos que la app pone en cada tarjeta: HRW 5.41, GRE 27, UA24 3, P2...
RE_CODIGO = re.compile(
    r"\b(HRW\s*\d+\.\d+|GRE\s*\d+|UA24\s*\d+|GR\d+\s*\d+|"
    r"P\d{1,2}\b|ECU\s*\d+|DES\s*\d+|DAT\s*\d+|EXP\s*\d+)", re.I)
RE_ID = re.compile(r"\b(hrw-c\d+-q\d+|ets-gr\d+-q\d+|uniandes2024-q\d+|"
                   r"expl-gr\d+-\d+|patron-P\d+|eq-[a-z]+-\d+)\b", re.I)


def descargar():
    with urllib.request.urlopen(HOJA, timeout=30) as r:
        crudo = r.read().decode("utf-8")
    if "accounts.google.com" in crudo[:2000]:
        raise SystemExit("La hoja no es pública: no puedo leerla.")
    return list(csv.reader(io.StringIO(crudo)))


def bajar_captura(url):
    """Trae la imagen adjunta al reporte, si la hay y es accesible.

    Google Drive sirve los archivos compartidos por enlace desde
    uc?export=download. Con adjuntos de pocos MB llega la imagen directa; si
    fuera muy grande, Drive devolvería una página de confirmación en su lugar.
    """
    m = RE_DRIVE.search(url or "")
    if not m:
        return None
    ident = m.group(1) or m.group(2)

    CAPTURAS.mkdir(parents=True, exist_ok=True)
    destino = CAPTURAS / f"{ident}.img"
    if destino.exists():
        return destino

    try:
        peticion = urllib.request.Request(
            f"https://drive.google.com/uc?export=download&id={ident}",
            headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(peticion, timeout=30) as r:
            datos = r.read()
    except Exception as e:
        print(f"      (no pude bajar la captura: {e})")
        return None

    if datos[:15].lower().lstrip().startswith(b"<!doctype") or b"<html" in datos[:200].lower():
        return None
    destino.write_bytes(datos)
    return destino


def cargar_corpus():
    """id -> tarjeta, para poder mostrar la pregunta que se reporta."""
    corpus = {}
    for ruta in sorted(CRUDO.glob("*.json")):
        if ruta.name == "figuras.json":
            continue
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        if isinstance(datos, list):
            for r in datos:
                if isinstance(r, dict) and "id" in r:
                    corpus[r["id"]] = r
    return corpus


def buscar_tarjeta(texto, corpus):
    """Del texto del reporte al registro del corpus."""
    m = RE_ID.search(texto)
    if m and m.group(1) in corpus:
        return corpus[m.group(1)]

    m = RE_CODIGO.search(texto)
    if not m:
        return None
    codigo = re.sub(r"\s+", " ", m.group(1)).upper().strip()

    # El código no está guardado en el crudo —se genera al construir— así que
    # se reconstruye el identificador a partir de él.
    mh = re.match(r"HRW (\d+)\.(\d+)", codigo)
    if mh:
        return corpus.get(f"hrw-c{int(mh.group(1)):02d}-q{int(mh.group(2)):03d}")
    mg = re.match(r"GRE (\d+)", codigo)
    if mg:
        return corpus.get(f"ets-gr1775-q{int(mg.group(1)):03d}")
    mu = re.match(r"UA24 (\d+)", codigo)
    if mu:
        return corpus.get(f"uniandes2024-q{int(mu.group(1)):02d}")
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tarjeta", action="store_true",
                    help="solo los reportes que identifican una tarjeta")
    args = ap.parse_args()

    filas = descargar()
    if len(filas) < 2:
        print("Sin reportes todavía.")
        return

    cabecera = filas[0]
    corpus = cargar_corpus()

    # La marca de tiempo va en la primera columna; el resto se busca por nombre.
    def col(nombre, defecto=None):
        for i, c in enumerate(cabecera):
            if nombre.lower() in c.lower():
                return i
        return defecto

    i_tipo = col("tipo de error")
    i_desc = col("descripción")
    i_captura = col("captura")

    print(f"{len(filas) - 1} reporte(s)\n")

    for fila in reversed(filas[1:]):
        if not any(fila):
            continue
        fecha = fila[0] if fila else "?"
        tipo = fila[i_tipo] if i_tipo is not None and i_tipo < len(fila) else ""
        desc = fila[i_desc] if i_desc is not None and i_desc < len(fila) else ""
        captura = fila[i_captura] if i_captura is not None and i_captura < len(fila) else ""

        t = buscar_tarjeta(desc, corpus)
        if args.tarjeta and not t:
            continue

        print(f"── {fecha}")
        if tipo:
            print(f"   tipo: {tipo}")
        print(f"   {desc.strip()[:400]}")
        if captura:
            ruta = bajar_captura(captura)
            if ruta:
                try:
                    from PIL import Image
                    with Image.open(ruta) as im:
                        print(f"   captura: {ruta}  ({im.format}, {im.size[0]}x{im.size[1]})")
                except Exception:
                    print(f"   captura: {ruta}")
            else:
                print(f"   captura: {captura}  (no accesible)")

        if t:
            print(f"   ►  {t['id']}  [{t.get('area', '?')}]")
            print(f"      {t.get('enunciado', '')[:150]}")
            for k, v in (t.get("opciones") or {}).items():
                marca = " ←" if k == t.get("respuesta") else ""
                print(f"        {k}. {v[:70]}{marca}")
        else:
            print("   ►  sin tarjeta identificada "
                  "(el reporte no trae código ni identificador)")
        print()


if __name__ == "__main__":
    main()
