"""
Arma el contenido del feed: junta las fuentes, baraja y reparte en tandas.

Entra:  07_APP/tuberia/crudo/*.json     (extractores)
        07_APP/autoral/*.json          (tarjetas escritas a mano)
        06_SEGUIMIENTO/datos/*.csv     (tus propios fallos)
Sale:   docs/contenido/tanda-NN.json + manifiesto.json

El corpus completo no se descarga de una: se parte en tandas que la app pide solo
cuando las necesita. Así la primera carga es rápida en el celular y, al terminar una,
la siguiente ya está en el repositorio.

Uso:
    python3 construir_contenido.py                # baraja con la semilla por defecto
    python3 construir_contenido.py --semilla 42   # otro orden, contenido nuevo
"""

import argparse
import csv
import json
import random
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
CRUDO = Path(__file__).parent / "crudo"
AUTORAL = RAIZ / "07_APP" / "autoral"
SEGUIMIENTO = RAIZ / "06_SEGUIMIENTO" / "datos"
SALIDA = RAIZ / "docs" / "contenido"

POR_TANDA = 220
SEMILLA_POR_DEFECTO = 2026

AREAS = [
    "mecanica", "electromagnetismo", "termo_estadistica",
    "moderna_cuantica", "relatividad", "optica_ondas",
]


def cargar_mc():
    """Preguntas de opción múltiple de los bancos extraídos."""
    tarjetas = []
    for ruta in sorted(CRUDO.glob("*.json")):
        for r in json.loads(ruta.read_text(encoding="utf-8")):
            tarjetas.append({
                "id": r["id"],
                "tipo": "mc",
                "area": r["area"],
                "semana": r.get("semana"),
                "nivel": r.get("nivel", "BASE"),
                "idioma": r.get("idioma", "en"),
                "enunciado": r["enunciado"],
                "opciones": r["opciones"],
                "respuesta": r["respuesta"],
                "etiquetas": r.get("etiquetas", []),
                "origen": r.get("fuente", ""),
                "tema": r.get("capitulo_titulo", ""),
            })
    return tarjetas


def cargar_autoral():
    tarjetas = []
    for ruta in sorted(AUTORAL.glob("*.json")):
        tarjetas.extend(json.loads(ruta.read_text(encoding="utf-8")))
    return tarjetas


def cargar_errores():
    """Convierte tus fallos registrados en tarjetas de repaso.

    Son las de mayor valor por tarjeta: no es una pregunta cualquiera, es una que
    ya fallaste, con el motivo anotado.
    """
    ruta = SEGUIMIENTO / "respuestas.csv"
    if not ruta.exists():
        return []

    tarjetas = []
    with ruta.open(encoding="utf-8") as fh:
        for fila in csv.DictReader(fh):
            if fila.get("ok") == "1":
                continue
            tarjetas.append({
                "id": f"error-{fila['simulacro_id']}-{fila['pregunta']}",
                "tipo": "error",
                "area": fila.get("area", ""),
                "nivel": fila.get("nivel", "BASE"),
                "patron": fila.get("patron") or None,
                "titulo": fila.get("tema", ""),
                "marcaste": fila.get("marcada", ""),
                "respuesta": fila.get("correcta", ""),
                "causa": fila.get("causa", ""),
                "simulacro": fila["simulacro_id"],
                "idioma": "es",
            })
    return tarjetas


def intercalar(mc, autoral, errores, rng):
    """Mezcla las fuentes para que el feed no venga por bloques.

    Las tarjetas de patrón y de error se reparten de forma pareja entre las de opción
    múltiple, en vez de amontonarse: la gracia de un feed es que no sepas qué sigue.
    """
    rng.shuffle(mc)
    especiales = autoral + errores
    rng.shuffle(especiales)

    if not especiales:
        return mc

    salida = list(mc)
    # Se insertan a intervalos regulares, con un poco de ruido en la posición.
    paso = max(1, len(salida) // (len(especiales) + 1))
    for i, tarjeta in enumerate(especiales):
        pos = min(len(salida), (i + 1) * paso + rng.randint(-paso // 3, paso // 3))
        salida.insert(max(0, pos), tarjeta)
    return salida


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--semilla", type=int, default=SEMILLA_POR_DEFECTO,
                    help="cambia el orden de las tandas")
    ap.add_argument("--por-tanda", type=int, default=POR_TANDA)
    args = ap.parse_args()

    rng = random.Random(args.semilla)

    mc = cargar_mc()
    autoral = cargar_autoral()
    errores = cargar_errores()

    if not mc:
        raise SystemExit(
            "No hay nada en crudo/. Corre primero: python3 extraer_hrw.py"
        )

    tarjetas = intercalar(mc, autoral, errores, rng)

    SALIDA.mkdir(parents=True, exist_ok=True)
    for viejo in SALIDA.glob("tanda-*.json"):
        viejo.unlink()

    tandas = []
    for i in range(0, len(tarjetas), args.por_tanda):
        trozo = tarjetas[i:i + args.por_tanda]
        indice = len(tandas)
        nombre = f"tanda-{indice:02d}.json"
        (SALIDA / nombre).write_text(
            json.dumps(trozo, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        tandas.append({
            "archivo": nombre,
            "n": len(trozo),
            "areas": dict(Counter(t.get("area", "") for t in trozo)),
        })

    manifiesto = {
        "semilla": args.semilla,
        "total": len(tarjetas),
        "por_tanda": args.por_tanda,
        "tandas": tandas,
        "resumen": {
            "por_tipo": dict(Counter(t["tipo"] for t in tarjetas)),
            "por_area": dict(Counter(t.get("area", "") for t in tarjetas)),
            "por_nivel": dict(Counter(t.get("nivel", "") for t in tarjetas)),
        },
    }
    (SALIDA / "manifiesto.json").write_text(
        json.dumps(manifiesto, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    peso = sum(f.stat().st_size for f in SALIDA.glob("tanda-*.json"))
    print(f"{len(tarjetas)} tarjetas en {len(tandas)} tandas  ({peso/1024:.0f} kB)")
    print(f"  por tipo:  {manifiesto['resumen']['por_tipo']}")
    print(f"  por área:  {manifiesto['resumen']['por_area']}")
    print(f"  -> {SALIDA.relative_to(RAIZ)}/")


if __name__ == "__main__":
    main()
