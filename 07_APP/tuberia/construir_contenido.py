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
import re
from collections import Counter
from pathlib import Path

import cifrar
import portero

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


# Ancho útil de la caja de fórmula en un teléfono de 414 px. Es conservador a
# propósito: las letras griegas y los superíndices no son monoespaciados ni
# siquiera dentro de una fuente mono, así que 38 caracteres contados ya se
# salían de la caja.
ANCHO_FORMULA = 33


def desplegar_formula(texto):
    """Repliega al ancho del móvil las fórmulas escritas en columnas.

    En el contenido autoral las fórmulas se escriben alineadas con espacios,
    que se lee muy bien en un editor y fatal en un teléfono: 'Contracción:
    L = L₀/γ        (L₀ = longitud propia)' se parte por la mitad y queda
    ilegible.

    Cada línea se trata como una cosa o la otra, no como una mezcla:

    - Prosa: se envuelve por palabras, con un espacio de unión.
    - Fórmula en columnas: los huecos de dos o más espacios marcan dónde
      separaba las columnas, y sirven de puntos de corte. Una fórmula continua
      que no quepa no se parte por un sitio arbitrario: se deja desbordar y la
      caja la desplaza de lado.

    Lo que continúa una línea anterior va indentado para que se vea que es lo
    mismo.
    """
    if not texto:
        return texto

    salida = []
    for linea in texto.split("\n"):
        if len(linea) <= ANCHO_FORMULA:
            salida.append(linea)
            continue

        sangria = " " * (len(linea) - len(linea.lstrip()))
        cuerpo = linea.strip()

        palabras_prosa = [w for w in cuerpo.split() if len(w) >= 3 and w[0].isalpha()]
        es_prosa = len(palabras_prosa) >= 5
        piezas = cuerpo.split() if es_prosa else re.split(r"\s{2,}", cuerpo)
        union = " " if es_prosa else "  "

        actual, prefijo = "", sangria
        for pieza in piezas:
            tentativa = f"{actual}{union}{pieza}" if actual else pieza
            if actual and len(prefijo + tentativa) > ANCHO_FORMULA:
                salida.append(prefijo + actual)
                actual, prefijo = pieza, sangria + "  "
            else:
                actual = tentativa
        if actual:
            salida.append(prefijo + actual)

    return "\n".join(salida)


def codigo_de(tarjeta):
    """Nombre corto y estable con el que referirse a una tarjeta.

    Sirve para saber dónde quedaste y para poder buscar una pregunta concreta:
    'me atoré en la HRW 5.41'. Es estable entre reconstrucciones porque sale del
    identificador, no del orden en que caiga en el feed.
    """
    ident = tarjeta.get("id", "")
    tipo = tarjeta.get("tipo")

    m = re.match(r"hrw-c(\d+)-q(\d+)", ident)
    if m:
        return f"HRW {int(m.group(1))}.{int(m.group(2))}"
    m = re.match(r"ets-gr1775-q(\d+)", ident)
    if m:
        return f"GRE {int(m.group(1))}"
    m = re.match(r"uniandes2024-q(\d+)", ident)
    if m:
        return f"UA24 {int(m.group(1))}"
    if tipo == "patron":
        return tarjeta.get("patron", "PAT")
    if tipo == "error":
        m = re.match(r"error-(\w+)-(\d+)", ident)
        return f"{m.group(1)}·{m.group(2)}" if m else "ERROR"
    if tipo == "micro":
        m = re.match(r"expl-(gr\d+)-(\d+)", ident)
        if m:
            return f"{m.group(1).upper()} {int(m.group(2))}"
    prefijos = {"ecuacion": "ECU", "descarte": "DES", "dato": "DAT", "micro": "EXP"}
    sufijo = ident.rsplit("-", 1)[-1].upper()
    return f"{prefijos.get(tipo, 'TAR')} {sufijo}"


def cargar_figuras():
    ruta = CRUDO / "figuras.json"
    if not ruta.exists():
        return {}
    return json.loads(ruta.read_text(encoding="utf-8"))


def cargar_mc(figuras):
    """Preguntas de opción múltiple de los bancos extraídos.

    Incluye las que se habían apartado por depender de una figura, siempre que
    el rescate de figuras haya conseguido el dibujo. Sin la imagen no entran:
    una pregunta que dice "en la gráfica de abajo" y no trae gráfica no se puede
    responder.
    """
    tarjetas = []
    fuentes = [CRUDO / "hrw.json", CRUDO / "hrw_pendientes_figura.json"]
    fuentes += [r for r in sorted(CRUDO.glob("*.json"))
                if r.name not in {"hrw.json", "hrw_pendientes_figura.json",
                                  "figuras.json", "explicaciones.json"}]

    for ruta in fuentes:
        if not ruta.exists():
            continue
        pendiente = ruta.name == "hrw_pendientes_figura.json"
        for r in json.loads(ruta.read_text(encoding="utf-8")):
            # Uniandes trae su imagen dentro del propio registro, porque sus
            # opciones son gráficos y no se pueden separar del enunciado.
            fig = r.get("figura") or figuras.get(r["id"])
            if pendiente and not fig:
                continue

            # Dos opciones idénticas hacen la pregunta imposible de responder.
            # El filtro va aquí y no en cada extractor para que valga también
            # para las fuentes que se añadan después.
            textos = [v.strip() for v in r.get("opciones", {}).values() if v.strip()]
            if len(set(textos)) < len(textos):
                continue
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
                "patron": r.get("patron"),
                # El porcentaje de aspirantes que acertó, cuando la fuente lo trae.
                **({"p_acierto": r["p_acierto"]} if r.get("p_acierto") else {}),
                # Uniandes no publica clave: la suya está razonada, no verificada.
                **({"clave_derivada": True} if r.get("clave_derivada") else {}),
                **({"figura": {
                    "png": fig["png"], "ancho": fig["ancho"], "alto": fig["alto"],
                    "incierta": fig.get("incierta", False),
                }} if fig else {}),
            })
    return tarjetas


def cargar_explicaciones():
    """Micro-lecciones del GRE. Van con el contenido autoral porque se leen, no
    se responden."""
    ruta = CRUDO / "explicaciones.json"
    if not ruta.exists():
        return []
    return json.loads(ruta.read_text(encoding="utf-8"))


def cargar_autoral():
    tarjetas = []
    for ruta in sorted(AUTORAL.glob("*.json")):
        for t in json.loads(ruta.read_text(encoding="utf-8")):
            # Solo las tablas de texto se repliegan. Las fórmulas son LaTeX y
            # el ancho lo resuelve KaTeX con su propio desplazamiento.
            if isinstance(t.get("tabla"), str):
                t["tabla"] = desplegar_formula(t["tabla"])
            tarjetas.append(t)
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
    ap.add_argument("--clave", help="frase de cifrado; por defecto usa 07_APP/.clave")
    ap.add_argument("--en-claro", action="store_true",
                    help="no cifrar (solo para depurar en local)")
    ap.add_argument("--sin-portero", action="store_true",
                    help="publica aunque el corpus no cumpla los umbrales")
    ap.add_argument("--rapido", action="store_true",
                    help="omite la revisión de figuras, que es la parte lenta")
    args = ap.parse_args()

    rng = random.Random(args.semilla)

    figuras = cargar_figuras()
    mc = cargar_mc(figuras)
    autoral = cargar_autoral() + cargar_explicaciones()
    errores = cargar_errores()

    if not mc:
        raise SystemExit(
            "No hay nada en crudo/. Corre primero: python3 extraer_hrw.py"
        )

    tarjetas = intercalar(mc, autoral, errores, rng)

    for t in tarjetas:
        t["codigo"] = codigo_de(t)

    # El portero va antes de escribir nada: si el corpus se degradó, es mejor
    # dejar publicado lo de ayer que sustituirlo por algo peor.
    incumplidos = portero.revisar(
        tarjetas, revisar_figuras=not args.rapido, estricto=not args.sin_portero
    )
    if incumplidos and not args.sin_portero:
        raise SystemExit(1)

    SALIDA.mkdir(parents=True, exist_ok=True)
    for patron in ("tanda-*.json", "tanda-*.bin"):
        for viejo in SALIDA.glob(patron):
            viejo.unlink()

    clave = bloque_cripto = None
    frase = nueva = None
    if not args.en_claro:
        frase, nueva = cifrar.obtener_frase(args.clave)
        clave, bloque_cripto = cifrar.preparar(frase)

    tandas = []
    for i in range(0, len(tarjetas), args.por_tanda):
        trozo = tarjetas[i:i + args.por_tanda]
        indice = len(tandas)
        if clave:
            nombre = f"tanda-{indice:02d}.bin"
            cifrar.escribir_tanda(SALIDA / nombre, clave, trozo)
        else:
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
        "cifrado": bloque_cripto,
        "semilla": args.semilla,
        "total": len(tarjetas),
        "por_tanda": args.por_tanda,
        "tandas": tandas,
        "resumen": {
            "por_tipo": dict(Counter(t["tipo"] for t in tarjetas)),
            "por_area": dict(Counter(t.get("area", "") for t in tarjetas)),
            "por_nivel": dict(Counter(t.get("nivel", "") for t in tarjetas)),
            "con_figura": sum(1 for t in tarjetas if t.get("figura")),
        },
    }
    (SALIDA / "manifiesto.json").write_text(
        json.dumps(manifiesto, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    peso = sum(f.stat().st_size for f in SALIDA.glob("tanda-*"))
    print(f"{len(tarjetas)} tarjetas en {len(tandas)} tandas  ({peso/1024:.0f} kB)")
    print(f"  por tipo:  {manifiesto['resumen']['por_tipo']}")
    print(f"  por área:  {manifiesto['resumen']['por_area']}")
    print(f"  con figura: {manifiesto['resumen']['con_figura']}")
    print(f"  -> {SALIDA.relative_to(RAIZ)}/")

    if clave:
        print(f"\n  cifrado AES-256-GCM, {cifrar.ITERACIONES:,} iteraciones")
        if nueva:
            print(f"\n  CLAVE NUEVA: {frase}")
            print(f"  guardada en {cifrar.ARCHIVO_CLAVE.relative_to(RAIZ)} (fuera de git)")
            print("  la escribes una sola vez en la app; anótala donde no se pierda")
        else:
            print(f"  clave tomada de {cifrar.ARCHIVO_CLAVE.relative_to(RAIZ)}")
    else:
        print("\n  SIN CIFRAR — no publiques esto en un repositorio público")


if __name__ == "__main__":
    main()
