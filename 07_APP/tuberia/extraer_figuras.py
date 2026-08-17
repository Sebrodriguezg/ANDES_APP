"""
Rescata las figuras de las preguntas que dependen de una imagen.

En este PDF las figuras no son imágenes incrustadas: están dibujadas con glifos
—puntos, barras, flechas— así que `pdfimages` no encuentra nada. Lo que sí se
puede es localizarlas por geometría y recortar esa región de la página.

El método:

 1. Se recorren las líneas de la pregunta, del enunciado hasta la respuesta.
 2. Las que casan con enunciado, opción o 'ans:' son texto; el resto es figura.
 3. La franja vertical que ocupan esas líneas de figura se recorta de la página
    con pdftoppm y se recorta al contenido real con PIL.
 4. La imagen se guarda en escala de grises y se mete en la tarjeta como data URI,
    para que quede dentro del cifrado igual que el resto del contenido.

Uso:
    python3 extraer_figuras.py              # escribe crudo/figuras.json
    python3 extraer_figuras.py --muestra 6  # guarda PNGs sueltos para revisarlos
"""

import argparse
import base64
import io
import json
import re
import subprocess
from pathlib import Path

from PIL import Image

import geometria
import extraer_hrw as H

RAIZ = Path(__file__).resolve().parents[2]
CACHE = Path(__file__).parent / "_cache"
SALIDA = Path(__file__).parent / "crudo" / "figuras.json"

DPI = 150
ESCALA = DPI / 72.0
ANCHO_MAX = 720          # px; más que esto no aporta nada en un celular
MARGEN = 6               # puntos de aire alrededor del recorte

# Una franja de figura tiene que tener cierto cuerpo para valer la pena.
ALTO_MINIMO = 18
# Alto típico de una línea de texto en este PDF, en puntos.
ALTO_LINEA = 13
# Cuánto abrir el recorte cuando no hay texto que enmarque el dibujo.
MARGEN_CIEGO = 46


def _lineas_por_pagina(lineas):
    porpag = {}
    for l in lineas:
        porpag.setdefault(l.pagina, []).append(l)
    return porpag


def _huele_a_dibujo(texto):
    """¿Esta línea es parte de un dibujo?

    Se detecta en positivo, no por descarte. La primera versión marcaba como
    figura todo lo que no pareciera prosa, y terminó recortando enunciados
    enteros del capítulo 1, que no tiene ni un dibujo.

    Lo que sí delata un dibujo en este PDF: hileras de puntos y barras con las
    que se trazan los ejes, y renglones sin apenas letras que son rótulos
    sueltos dentro de la figura.
    """
    t = texto.strip()
    if not t:
        return False
    if H.RE_OPCION.match(t) or H.RE_RESPUESTA.match(t) or H.RE_PREGUNTA.match(t):
        return False
    if H.RE_RESTO_FIGURA.search(t):
        return True
    # Rótulos dentro del dibujo: cortos y casi sin letras.
    letras = sum(c.isalpha() for c in t)
    return len(t) <= 24 and letras <= 3


def localizar_franjas(lineas):
    """Devuelve {(capitulo, numero): (pagina, y0, y1)} de la zona de dibujo.

    La primera versión tomaba la franja que va de la primera a la última línea
    con trazos, y cortaba 188 de 316 figuras: las curvas y las flechas se
    extienden bastante más allá de las líneas que el extractor de texto llega a
    ver, así que se quedaban fuera por arriba o por abajo.

    El dibujo vive en el hueco entre el final del enunciado y el comienzo de
    las opciones. Ese hueco es el recorte correcto: se toma entero y después
    PIL lo ajusta al contenido real.
    """
    capitulo_de_pagina, _ = H._capitulos_por_pagina(lineas)

    franjas = {}
    capitulo = 0
    numero = None
    siguiente = 1
    bloque = []          # (y0, es_dibujo, pagina) de la pregunta en curso

    def cerrar():
        nonlocal bloque, numero
        if numero is not None and bloque:
            dibujos = [b for b in bloque if b[1]]
            paginas = {b[2] for b in bloque}
            if dibujos and len(paginas) == 1:
                primero = min(b[0] for b in dibujos)
                ultimo = max(b[0] for b in dibujos)

                # Texto que enmarca el dibujo por arriba y por abajo.
                arriba = [b[0] for b in bloque if not b[1] and b[0] < primero]
                abajo = [b[0] for b in bloque if not b[1] and b[0] > ultimo]

                # Sin texto que lo enmarque se deja un margen generoso: es
                # preferible recortar de más y que PIL ajuste, que cortar la
                # figura por la mitad.
                y0 = (max(arriba) + ALTO_LINEA) if arriba else (primero - MARGEN_CIEGO)
                y1 = min(abajo) if abajo else (ultimo + MARGEN_CIEGO)

                if y1 - y0 >= ALTO_MINIMO:
                    franjas[(capitulo, numero)] = (bloque[0][2], y0, y1)
        bloque = []

    for linea in lineas:
        cap_pag = capitulo_de_pagina.get(linea.pagina, capitulo)
        if cap_pag != capitulo:
            cerrar()
            capitulo = cap_pag
            siguiente = 1
            numero = None

        texto = linea.texto.strip()
        if not texto or H._es_pie_de_pagina(linea, "") or H.RE_CAPITULO.match(texto):
            continue

        m = H.RE_PREGUNTA.match(texto)
        if m and int(m.group(1)) in (siguiente, siguiente + 1, siguiente + 2):
            cerrar()
            numero = int(m.group(1))
            siguiente = numero + 1
            bloque.append((linea.y0, False, linea.pagina))
            continue

        if numero is None:
            continue

        if H.RE_RESPUESTA.match(texto):
            bloque.append((linea.y0, False, linea.pagina))
            cerrar()
            numero = None
            continue

        bloque.append((linea.y0, _huele_a_dibujo(texto), linea.pagina))

    cerrar()
    return franjas


def recortar(pdf, pagina, y0, y1, alto_pagina=792):
    """Renderiza la franja y la recorta al contenido real."""
    y0 = max(0, y0)
    y1 = min(alto_pagina, y1)
    if y1 - y0 < ALTO_MINIMO:
        return None

    salida = CACHE / "recorte"
    subprocess.run(
        ["pdftoppm", "-png", "-r", str(DPI),
         "-f", str(pagina), "-l", str(pagina),
         "-x", "0", "-y", str(int(y0 * ESCALA)),
         "-W", str(int(612 * ESCALA)), "-H", str(int((y1 - y0) * ESCALA)),
         str(pdf), str(salida)],
        check=True, capture_output=True,
    )

    generados = sorted(CACHE.glob("recorte*.png"))
    if not generados:
        return None

    with Image.open(generados[0]) as im:
        im = im.convert("L")
        # Recorte al contenido: se busca lo que no es blanco.
        invertida = Image.eval(im, lambda p: 255 - p)
        caja = invertida.getbbox()
        if not caja:
            im.close()
            for g in generados:
                g.unlink()
            return None

        pad = 8
        caja = (max(0, caja[0] - pad), max(0, caja[1] - pad),
                min(im.width, caja[2] + pad), min(im.height, caja[3] + pad))
        recorte = im.crop(caja)

        if recorte.width > ANCHO_MAX:
            alto = round(recorte.height * ANCHO_MAX / recorte.width)
            recorte = recorte.resize((ANCHO_MAX, alto), Image.LANCZOS)

        buf = io.BytesIO()
        recorte.save(buf, format="PNG", optimize=True, bits=4)
        datos = buf.getvalue()
        dims = recorte.size

    for g in generados:
        g.unlink()

    return datos, dims


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--muestra", type=int, metavar="N",
                    help="guarda N figuras como PNG suelto para revisarlas")
    ap.add_argument("--limite", type=int, help="procesa solo las primeras N")
    args = ap.parse_args()

    xml = CACHE / "hrw.xml"
    if not xml.exists():
        raise SystemExit("Falta _cache/hrw.xml. Corre antes: python3 extraer_hrw.py")

    print("Leyendo geometría...")
    lineas = geometria.leer_lineas(xml)

    print("Localizando franjas de figura...")
    franjas = localizar_franjas(lineas)
    print(f"  {len(franjas)} preguntas con zona de dibujo")

    # Solo interesan las que el extractor de texto descartó por figura, más las
    # que sí entraron pero tienen dibujo de apoyo.
    preguntas, _apartadas, _desc = H.extraer(xml)
    validas = {(p.capitulo, p.numero) for p in preguntas}

    objetivo = sorted(franjas.items())
    if args.limite:
        objetivo = objetivo[:args.limite]

    salida = {}
    muestras = 0
    fallos = 0

    for i, ((cap, num), (pagina, y0, y1)) in enumerate(objetivo, 1):
        if i % 100 == 0:
            print(f"  {i}/{len(objetivo)}…")
        try:
            res = recortar(H.PDF, pagina, y0, y1)
        except subprocess.CalledProcessError:
            fallos += 1
            continue
        if not res:
            fallos += 1
            continue

        datos, (an, al) = res
        # Una tira muy plana o muy diminuta suele ser un renglón suelto, no un dibujo.
        if al < 30 or an < 60 or len(datos) < 400:
            continue

        ident = f"hrw-c{cap:02d}-q{num:03d}"
        salida[ident] = {
            "png": base64.b64encode(datos).decode(),
            "ancho": an, "alto": al,
            "bytes": len(datos),
            "en_corpus": (cap, num) in validas,
        }

        if args.muestra and muestras < args.muestra:
            ruta = CACHE / f"muestra_{ident}.png"
            ruta.write_bytes(datos)
            print(f"  {ruta.name}  {an}x{al}  {len(datos)/1024:.1f} kB")
            muestras += 1

    SALIDA.parent.mkdir(exist_ok=True)
    SALIDA.write_text(json.dumps(salida, ensure_ascii=False), encoding="utf-8")

    peso = sum(v["bytes"] for v in salida.values())
    en_corpus = sum(1 for v in salida.values() if v["en_corpus"])
    print(f"\n{len(salida)} figuras -> {SALIDA.relative_to(RAIZ)}")
    print(f"  {en_corpus} en preguntas que ya están en el corpus")
    print(f"  {len(salida) - en_corpus} en preguntas descartadas por figura")
    print(f"  peso total {peso/1024/1024:.2f} MB  (media {peso/max(1,len(salida))/1024:.1f} kB)")
    if fallos:
        print(f"  {fallos} franjas sin contenido renderizable")


if __name__ == "__main__":
    main()
