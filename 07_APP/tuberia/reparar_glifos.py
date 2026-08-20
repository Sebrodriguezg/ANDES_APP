"""
Repone en el corpus los glifos que `pdftotext` había borrado.

`glifos.py` reconstruye, desde la geometría de mutool, cómo era cada línea del
PDF de verdad. Aquí se usa esa reconstrucción para arreglar las tarjetas ya
extraídas.

El truco es que no hace falta alinear nada complicado: **lo que produce
pdftotext es lo que produce mutool menos los glifos perdidos**. Así que de cada
línea reconstruida se deriva su versión rota —quitándole justo los caracteres
recuperados— y esa versión rota es la que hay que buscar en el corpus. Si
aparece, se sustituye por la buena.

El `≠` es el único caso con una regla propia: pdftotext no perdió el `=`, solo
la barra que lo cruza, de modo que su versión rota lleva `=` donde la buena
lleva `≠`.

Uso:
    python3 reparar_glifos.py --simular     # dice qué cambiaría, sin tocar nada
    python3 reparar_glifos.py               # reescribe crudo/hrw.json
"""

import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
CRUDO = Path(__file__).parent / "crudo"
CORPUS = CRUDO / "hrw.json"
GLIFOS = Path(__file__).parent / "_cache" / "hrw_glifos.json"

# Los caracteres que `glifos.py` repone. Quitarlos de una línea reconstruida
# devuelve lo que pdftotext habría dado.
REPUESTOS = "→ℓε∫′"

# Longitud mínima de una línea para usarla como patrón. Por debajo de esto los
# fragmentos son tan comunes que sustituirlos sería una lotería.
MINIMO = 18


def normalizar(texto):
    """Deja el texto comparable entre las dos extracciones.

    Difieren en espaciado y en algunos signos tipográficos, así que se aplanan
    los espacios y se unifican guiones y comillas. Los `^{}` y `_{}` que añade
    nuestra lectura por geometría se retiran: lo que se compara es la letra.
    """
    # NFC y no NFKC: la compatibilidad convierte ℓ en una ele corriente y ′ en
    # un apóstrofo, que son justo dos de los glifos que estamos reponiendo.
    texto = unicodedata.normalize("NFC", texto)
    texto = re.sub(r"[\^_]\{([^{}]*)\}", r"\1", texto)
    texto = texto.replace("−", "-").replace("–", "-").replace("—", "-")
    texto = texto.replace("’", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", texto).strip()


def romper(linea):
    """La versión de una línea tal y como la habría dejado pdftotext."""
    roto = linea.replace("≠", "=")          # la barra se cae, el igual queda
    return "".join(c for c in roto if c not in REPUESTOS)


# Cuánto contexto se toma a cada lado del glifo recuperado. Una línea entera
# casi nunca casa —nuestra lectura por geometría reagrupa el texto en párrafos,
# así que los saltos caen en otro sitio—, pero una ventana corta sí. Con 34
# caracteres a cada lado el patrón sigue siendo específico y encaja mucho más.
VENTANA = 34


def construir_parches():
    """Pares (roto, arreglado) listos para buscar y sustituir.

    Se emite una ventana por cada glifo recuperado, no la línea entera. Si dos
    ventanas distintas comparten la misma versión rota, la sustitución sería
    ambigua y se descartan las dos: es preferible dejar un glifo sin reponer a
    ponerlo donde no iba.
    """
    paginas = json.loads(GLIFOS.read_text(encoding="utf-8"))
    parches, ambiguos = {}, set()

    for lineas in paginas.values():
        for buena in lineas:
            for m in re.finditer(f"[{REPUESTOS}≠]", buena):
                i, j = max(0, m.start() - VENTANA), m.end() + VENTANA
                trozo = buena[i:j]
                n_buena = compactar(trozo)
                n_rota = compactar(romper(trozo))
                if len(n_rota) < MINIMO or n_rota == n_buena:
                    continue
                # El menos tipográfico y el guion se usan indistintamente entre
                # las dos extracciones: se registran las dos formas.
                # Variantes de escritura entre las dos extracciones: el menos
                # tipográfico frente al guion, y el signo de multiplicar frente
                # al comando LaTeX que produce nuestra lectura por geometría.
                # Sin esta última, la pregunta del producto vectorial se quedó
                # con "θ = 90°" en vez de "θ ≠ 90°", que invierte el enunciado.
                variantes = []
                for x, y in ((n_rota, n_buena),):
                    for cambio in (lambda s: s,
                                   lambda s: s.replace("−", "-"),
                                   lambda s: s.replace("-", "−"),
                                   lambda s: s.replace("×", "\\times"),
                                   lambda s: s.replace("×", "\\times").replace("−", "-")):
                        variantes.append((cambio(x), cambio(y)))
                for a, b in variantes:
                    if a == b:
                        continue
                    if a in parches and parches[a] != b:
                        ambiguos.add(a)
                    parches.setdefault(a, b)

    for k in ambiguos:
        parches.pop(k, None)
    # Los patrones largos primero: si uno corto es subcadena de otro largo,
    # aplicar antes el largo evita dejar el resto a medio arreglar.
    return dict(sorted(parches.items(), key=lambda kv: -len(kv[0])))


# Reparaciones que el emparejamiento por ventana no puede alcanzar, porque
# nuestro marcado de subíndices cae justo dentro del hueco: `1/4πε₀` sale del
# PDF como `1/4π_{0}`, y el patrón de mutool —`1/4π0`— ya no encaja.
#
# Son patrones cortos, pero inequívocos en este corpus: un subíndice cero
# pegado a una pi o a una barra de división solo puede ser la permitividad del
# vacío, y dos subíndices cero seguidos son µ₀ε₀. Verificados uno a uno contra
# el PDF sobre las 33 tarjetas afectadas.
DIRECTOS = [
    (re.compile(r"(?<=π)(\s*)_\{0\}"), r"\1ε_{0}"),
    (re.compile(r"(?<=/)(\s*)_\{0\}"), r"\1ε_{0}"),
    (re.compile(r"(µ_\{0\})(\s*)_\{0\}"), r"\1\2ε_{0}"),
]


# Reparaciones por tarjeta, para los sitios donde el emparejamiento por ventana
# no llega porque nuestro marcado de subíndices y superíndices cae justo dentro
# del hueco. Son pocas y están verificadas una a una contra el PDF.
POR_TARJETA = {
    # "θ ≠ 90°". Con el igual, la opción E pasa a ser verdadera y la pregunta
    # se queda sin respuesta correcta. El grado sale como ^{◦} en nuestra
    # lectura y como ◦ en la de mutool, y ahí se rompía la coincidencia.
    "hrw-c03-q037": [
        ("enunciado", "θ = 90^{◦}", "θ ≠ 90^{◦}"),
    ],
    # Las cuatro primeras opciones quedaron idénticas al perderse los signos de
    # distinto, y por eso el filtro de opciones repetidas descartaba la tarjeta
    # entera. Con los ≠ repuestos vuelve al corpus.
    "hrw-c17-q007": [
        ("A", "f_{s} = f_{a} but λ_{s} = λ_{a}", "f_{s} = f_{a} but λ_{s} ≠ λ_{a}"),
        ("C", "λ_{s} = λ_{a} but f_{s} = f_{a}", "λ_{s} = λ_{a} but f_{s} ≠ f_{a}"),
        ("D", "λ_{s} = λ_{a} and f_{s} = f_{a}", "λ_{s} ≠ λ_{a} and f_{s} ≠ f_{a}"),
    ],
}


def aplicar_por_tarjeta(tarjeta):
    """Las correcciones declaradas para esa tarjeta, si las hay."""
    for campo, viejo, nuevo in POR_TARJETA.get(tarjeta["id"], []):
        if campo == "enunciado":
            tarjeta["enunciado"] = tarjeta["enunciado"].replace(viejo, nuevo)
        else:
            op = tarjeta.get("opciones") or {}
            if campo in op:
                op[campo] = op[campo].replace(viejo, nuevo)
    return tarjeta


def compactar(texto):
    """Solo aplana espacios. Lo que se escribe de vuelta pasa por aquí.

    `normalizar` sirve para *comparar* y por eso se lleva por delante los
    `^{}` y `_{}`. Si su resultado se escribiera en la tarjeta, borraría la
    reconstrucción de exponentes y subíndices —`10^{-9}` volvería a ser
    `10-9`—, que es precisamente el fallo que costó arreglar en su día.
    """
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", texto)).strip()


def reparar_texto(texto, parches, contador):
    """Repone los glifos conservando el resto del texto tal cual estaba.

    La sustitución se hace sobre el texto compactado, no sobre el normalizado:
    solo se tocan los caracteres que faltaban.
    """
    salida = compactar(texto)
    for rota, buena in parches.items():
        if rota in salida:
            salida = salida.replace(rota, buena)
            contador[rota] += 1
    for patron, reemplazo in DIRECTOS:
        salida, n = patron.subn(reemplazo, salida)
        if n:
            contador[f"directo:{patron.pattern[:20]}"] += n
    return salida


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--simular", action="store_true")
    ap.add_argument("--muestra", type=int, default=8)
    args = ap.parse_args()

    if not GLIFOS.exists():
        raise SystemExit("Falta crudo/hrw_glifos.json. Corre antes:\n"
                         "  python3 glifos.py --resolver")

    parches = construir_parches()
    print(f"{len(parches)} patrones de reparación")

    tarjetas = json.loads(CORPUS.read_text(encoding="utf-8"))
    usados = Counter()
    tocadas, ejemplos = 0, []

    for t in tarjetas:
        antes = json.dumps(t, ensure_ascii=False)
        nuevo = reparar_texto(t["enunciado"], parches, usados)
        if compactar(t["enunciado"]) != nuevo:
            if not args.simular:
                t["enunciado"] = nuevo
            if len(ejemplos) < args.muestra:
                ejemplos.append((t["id"], t["enunciado"], nuevo))
        for k, v in (t.get("opciones") or {}).items():
            n = reparar_texto(v, parches, usados)
            if compactar(v) != n:
                if not args.simular:
                    t["opciones"][k] = n
                if len(ejemplos) < args.muestra:
                    ejemplos.append((f"{t['id']} ({k})", v, n))
        if not args.simular:
            aplicar_por_tarjeta(t)
        if json.dumps(t, ensure_ascii=False) != antes or args.simular:
            pass
        tocadas += 1 if usados else 0

    afectadas = len({e[0].split(" ")[0] for e in ejemplos})
    print(f"{sum(usados.values())} sustituciones aplicadas")
    print(f"{len(usados)} patrones distintos usaron\n")

    for ident, antes, despues in ejemplos:
        print(f"  {ident}")
        print(f"    antes:   {antes[:104]}")
        print(f"    después: {despues[:104]}")

    if args.simular:
        print("\n(simulación: no se escribió nada)")
        return

    CORPUS.write_text(json.dumps(tarjetas, ensure_ascii=False, indent=1),
                      encoding="utf-8")
    print(f"\n  -> {CORPUS.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
