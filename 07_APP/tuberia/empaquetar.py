"""
Empaqueta todo el material de estudio en un ZIP para subir a Drive.

La app enlaza a la carpeta de Drive donde vive el paquete, para poder bajarse
todo de golpe: los libros, los bancos de examen, el plan, el temario y el
seguimiento. Es lo que el repositorio no puede llevar, porque son 650 MB de
material con copyright que no debe estar en un sitio público.

El PDF de cada libro es enorme, así que el ZIP se parte en volúmenes: Drive
sube mejor varios archivos medianos que uno gigante, y si uno falla no hay que
repetirlo todo.

Uso:
    python3 empaquetar.py                    # todo, en volúmenes de 400 MB
    python3 empaquetar.py --sin-libros       # solo el trabajo propio, ligero
    python3 empaquetar.py --volumen 200
"""

import argparse
import zipfile
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DESTINO = RAIZ / "_paquete"

# Lo que entra, en orden de importancia. Cada entrada es una carpeta o archivo
# de ANDES/ y una nota de qué contiene.
CONTENIDO = [
    ("PLAN.md", "el plan maestro de las 14 semanas"),
    ("README.md", "guía del repositorio"),
    ("cronograma.pdf", "el calendario en PDF"),
    ("cronograma.tex", "fuente del calendario"),
    ("00_ADMISION", "requisitos del proceso y material faltante"),
    ("03_TEMARIO", "desglose semana → tema → capítulo, y los 10 patrones"),
    ("04_ESTUDIO", "formularios, notas y mazos"),
    ("05_SIMULACROS", "simulacros y su análisis"),
    ("06_SEGUIMIENTO", "medidor, datos y tablero"),
    ("07_APP", "la tubería de contenido y el plan de la app"),
    ("02_BIBLIOTECA", "los libros por área"),
    ("01_EXAMENES", "bancos de examen: HRW, GRE, EUF, Uniandes"),
]

PESADAS = {"02_BIBLIOTECA", "01_EXAMENES"}

# Nada de esto tiene sentido dentro del paquete.
EXCLUIR = {".git", "__pycache__", "_cache", "crudo", "_paquete", ".clave",
           "node_modules"}


def se_excluye(ruta):
    return any(parte in EXCLUIR for parte in ruta.parts)


def reunir(sin_libros):
    """Todos los archivos a empaquetar, con su ruta relativa."""
    archivos = []
    for nombre, _ in CONTENIDO:
        if sin_libros and nombre in PESADAS:
            continue
        origen = RAIZ / nombre
        if not origen.exists():
            continue
        if origen.is_file():
            archivos.append(origen)
            continue
        for f in sorted(origen.rglob("*")):
            if f.is_file() and not se_excluye(f.relative_to(RAIZ)):
                archivos.append(f)
    return archivos


def escribir_indice(archivos, sin_libros):
    """Un índice legible dentro del paquete, para saber qué es cada cosa."""
    total = sum(f.stat().st_size for f in archivos)
    lineas = [
        "PAQUETE DE ESTUDIO — ANDES",
        f"Examen de admisión a la Maestría en Física, Uniandes · 23-nov-2026",
        f"Generado el {date.today().isoformat()}",
        "",
        f"{len(archivos)} archivos · {total / 1024 / 1024:.0f} MB",
        "",
        "QUÉ HAY AQUÍ",
        "",
    ]
    for nombre, nota in CONTENIDO:
        if sin_libros and nombre in PESADAS:
            continue
        origen = RAIZ / nombre
        if not origen.exists():
            continue
        n = 1 if origen.is_file() else sum(
            1 for f in origen.rglob("*")
            if f.is_file() and not se_excluye(f.relative_to(RAIZ)))
        lineas.append(f"  {nombre:20} {n:5d} archivos   {nota}")

    lineas += [
        "",
        "POR DÓNDE EMPEZAR",
        "",
        "  1. PLAN.md — qué es el examen y cómo está repartido el trabajo",
        "  2. 03_TEMARIO/00_mapa_simulacro.md — los 10 patrones que hay que",
        "     tener memorizados el 22 de noviembre",
        "  3. 05_SIMULACROS/D1_resultados.md — el diagnóstico y qué dijo",
        "",
        "  El seguimiento se lleva con:",
        "     python3 06_SEGUIMIENTO/medidor.py estado",
        "",
        "La app está en github.com/Sebrodriguezg/ANDES_APP",
        "",
        "Los libros y bancos de examen son material con copyright, para uso",
        "personal de estudio. No se redistribuyen.",
    ]
    return "\n".join(lineas)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sin-libros", action="store_true",
                    help="solo el trabajo propio, sin PDF de biblioteca ni exámenes")
    ap.add_argument("--volumen", type=int, default=400,
                    help="tamaño máximo de cada volumen, en MB")
    args = ap.parse_args()

    archivos = reunir(args.sin_libros)
    if not archivos:
        raise SystemExit("No encontré nada que empaquetar.")

    DESTINO.mkdir(exist_ok=True)
    for viejo in DESTINO.glob("ANDES_*.zip"):
        viejo.unlink()

    indice = escribir_indice(archivos, args.sin_libros)
    (DESTINO / "CONTENIDO.txt").write_text(indice, encoding="utf-8")

    tope = args.volumen * 1024 * 1024
    sufijo = "trabajo" if args.sin_libros else "completo"
    volumen, acumulado, n = None, 0, 0
    creados = []

    def abrir():
        nonlocal volumen, acumulado, n
        n += 1
        ruta = DESTINO / f"ANDES_{sufijo}_{n:02d}.zip"
        creados.append(ruta)
        # ZIP_STORED para los PDF: ya vienen comprimidos y deflate solo gasta
        # tiempo. El texto sí se comprime.
        volumen = zipfile.ZipFile(ruta, "w", zipfile.ZIP_DEFLATED, compresslevel=6)
        volumen.writestr("CONTENIDO.txt", indice)
        acumulado = 0

    abrir()
    for f in archivos:
        tam = f.stat().st_size
        if acumulado + tam > tope and acumulado > 0:
            volumen.close()
            abrir()
        modo = zipfile.ZIP_STORED if f.suffix.lower() in (".pdf", ".zip", ".png",
                                                          ".jpg", ".woff2") else None
        volumen.write(f, f.relative_to(RAIZ),
                      compress_type=modo)
        acumulado += tam
    volumen.close()

    print(f"{len(archivos)} archivos en {len(creados)} volumen(es)\n")
    for ruta in creados:
        print(f"  {ruta.name:28} {ruta.stat().st_size / 1024 / 1024:7.1f} MB")
    print(f"\n  -> {DESTINO.relative_to(RAIZ)}/")
    print("\nSúbelos a la carpeta de Drive y la app ya enlaza ahí.")


if __name__ == "__main__":
    main()
