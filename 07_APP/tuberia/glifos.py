"""
Recupera los glifos que `pdftotext` borra en silencio.

El banco de HRW está compuesto en LaTeX con las fuentes Computer Modern, y
algunas —cmmi (matemática itálica) y cmsy (símbolos)— no traen tabla ToUnicode
para ciertos caracteres. `pdftotext` los descarta sin avisar; `mutool` los deja
marcados con U+FFFD. La diferencia importa: en 2.208 preguntas extraídas la `ℓ`
no aparecía **ni una vez**, y veintiocho signos `≠` habían quedado como `=`,
que invierte el enunciado.

Los glifos no se identifican por su código —no lo hay— sino por su geometría,
que en Computer Modern es inequívoca:

- **Acento de vector.** La caja del glifo solapa horizontalmente con la del
  carácter siguiente y queda entera por encima de ella. Es la flecha de `\\vec`.
- **Barra de negación.** Viene de cmsy10, solapa con el `=` que le sigue y lo
  cruza en vertical. Los dos juntos son `≠`.
- **Ele cursiva.** No solapa con nada: va en el flujo del texto, con altura de
  ascendente. Es `\\ell`, el número cuántico orbital.

Uso:
    python3 glifos.py --resumen          # cuántos hay de cada clase
    python3 glifos.py --resolver         # escribe crudo/hrw_glifos.json
    python3 glifos.py --pagina 35        # inspecciona una página
"""

import argparse
import json
import re
from collections import Counter
from statistics import median
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
STEXT = Path(__file__).parent / "_cache" / "hrw_stext.xml"
# Dato intermedio, no corpus: vive en _cache para que `cargar_mc` no lo
# confunda con un archivo de tarjetas al recorrer crudo/*.json.
SALIDA = Path(__file__).parent / "_cache" / "hrw_glifos.json"

PERDIDO = "�"

# Margen en puntos para decidir si dos cajas se tocan. Las cajas de Computer
# Modern son ajustadas; medio punto basta y evita falsos positivos por el
# espaciado entre caracteres.
HOLGURA = 0.6


def _caja(quad):
    """El `quad` de mutool son cuatro esquinas; se reduce a (x0, y0, x1, y1)."""
    v = [float(n) for n in quad.split()]
    xs, ys = v[0::2], v[1::2]
    return min(xs), min(ys), max(xs), max(ys)


# Altura del glifo dividida por la altura de la x de su línea. Computer Modern
# separa las clases con holgura: la épsilon no tiene ascendente y se queda por
# debajo de 1,1; la ele cursiva lo tiene y ronda 1,6; los operadores grandes
# —la integral de contorno— pasan de 2.
ALTO_SIN_ASCENDENTE = 1.10
ALTO_OPERADOR = 2.00


# Los operadores grandes salen siempre de cmex, la fuente de extensiones de
# TeX. Distinguirlos por altura no vale —una integral de la página 479 medía
# 1,97 y se colaba como ele—, pero la fuente los separa sin ambigüedad. Entre
# ellos no se pueden separar: las cuatro ecuaciones de Maxwell de la página 479
# son integrales de contorno y miden lo mismo que una integral corriente, así
# que se escriben todas como ∫. Es una imprecisión de notación, no un cambio de
# significado, y queda anotada como residuo conocido. Los glifos cmex anchos son
# delimitadores —llaves, paréntesis grandes— y se dejan sin resolver.
FUENTE_OPERADORES = "cmex"
ANCHO_DELIMITADOR = 0.80


def clasificar(fuente, caja, siguiente, anterior=None, x_altura=None,
               en_contexto=True, cuerpo=None):
    """Qué era el glifo perdido, a partir de dónde está y cuánto mide.

    `siguiente` y `anterior` son (fuente, caracter, caja) de sus vecinos en la
    línea, o None en los bordes. `x_altura` es la altura de las minúsculas sin
    ascendente de esa línea, que sirve de patrón de medida.
    """
    if siguiente is not None:
        f_sig, c_sig, b_sig = siguiente[0], siguiente[1], siguiente[2]
        solapa_x = not (caja[2] < b_sig[0] or b_sig[2] < caja[0])

        if solapa_x:
            # Encima del carácter siguiente y sin invadirlo: es un acento.
            if caja[3] <= b_sig[1] + HOLGURA:
                return "vector"
            # Lo cruza. Sobre un igual y saliendo de cmsy, es la barra de \not.
            if c_sig == "=" and fuente.startswith("cmsy"):
                return "negacion"

    if fuente.startswith(FUENTE_OPERADORES):
        ancho = (caja[2] - caja[0]) / cuerpo if cuerpo else 0
        return "delimitador" if ancho >= ANCHO_DELIMITADOR else "integral"

    # Un glifo solo en su renglón no es texto: son los rótulos sueltos de las
    # figuras. Se deja sin resolver antes que arriesgar una sustitución.
    if not en_contexto:
        return "aislado"

    # A partir de aquí el glifo va en el flujo del texto. Lo decide su altura.
    if x_altura:
        alto = (caja[3] - caja[1]) / x_altura
        if alto >= ALTO_OPERADOR:
            return "operador"
        if alto < ALTO_SIN_ASCENDENTE:
            # Sin ascendente. La épsilon lleva detrás el subíndice cero, que es
            # como aparece siempre: 1/4πε₀.
            if siguiente is not None and siguiente[1] == "0":
                return "epsilon"
            # La prima marca sistemas de referencia —X—X', ∆t'—: va pegada a
            # una letra latina y detrás no lleva otra letra. Sin esa segunda
            # condición se colaba en sitios como "λ? charge per unit length".
            if (anterior is not None and anterior[1].isascii()
                    and anterior[1].isalnum()
                    and (siguiente is None or not siguiente[1].isalpha())):
                return "prima"
            return "desconocido"
        return "ele"

    return "desconocido"


def leer_lineas(ruta=STEXT):
    """Recorre el stext y devuelve, por línea, sus caracteres con caja.

    Se lee en streaming: el XML de 655 páginas pesa 153 MB y no cabe cómodo en
    memoria como árbol.
    """
    import xml.etree.ElementTree as ET

    pagina = 0
    for evento, elem in ET.iterparse(ruta, events=("start", "end")):
        if evento == "start" and elem.tag == "page":
            pagina += 1
        elif evento == "end" and elem.tag == "line":
            chars = []
            for f in elem.iter("font"):
                nombre = f.get("name", "")
                tam = float(f.get("size", 0) or 0)
                for ch in f.iter("char"):
                    chars.append(
                        (nombre, ch.get("c", ""), _caja(ch.get("quad")), tam))
            if chars:
                yield pagina, chars
            elem.clear()
        elif evento == "end" and elem.tag == "page":
            elem.clear()


def resolver(chars):
    """Convierte los caracteres de una línea en texto con los glifos repuestos.

    El acento de vector se escribe *delante* de su letra, como `→R`, que es como
    se lee y como lo espera el resto de la tubería.
    """
    fuera = []
    saltar = set()
    clases = Counter()

    # Patrón de medida de la línea: la altura de las minúsculas que no tienen
    # ascendente ni descendente.
    bajas = [b[3] - b[1] for _, c, b, _t in chars if c in "aceimnorsuvwxz"]
    if bajas:
        x_altura = median(bajas)
    else:
        # Las líneas de fórmula suelen no tener minúsculas de referencia. El
        # cuerpo de la fuente sirve igual: en Computer Modern la x mide unos
        # 0,43 del cuerpo.
        cuerpos = [t for _f, _c, _b, t in chars if t]
        x_altura = median(cuerpos) * 0.43 if cuerpos else None

    SIGNO = {"vector": "→", "negacion": "≠", "ele": "ℓ",
             "epsilon": "ε", "prima": "′",
             "integral": "∫"}
    # `aislado`, `desconocido` y todo lo que no esté aquí se queda marcado.

    for i, (fuente, c, caja, _tam) in enumerate(chars):
        if i in saltar:
            continue
        if c != PERDIDO:
            fuera.append(c)
            continue

        siguiente = chars[i + 1] if i + 1 < len(chars) else None
        anterior = chars[i - 1] if i else None
        clase = clasificar(fuente, caja, siguiente, anterior, x_altura,
                           en_contexto=len(chars) > 2, cuerpo=_tam)
        clases[clase] += 1

        fuera.append(SIGNO.get(clase, PERDIDO))
        if clase == "negacion":
            saltar.add(i + 1)          # el '=' ya va dentro del ≠

    return "".join(fuera), clases


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--resumen", action="store_true")
    ap.add_argument("--resolver", action="store_true")
    ap.add_argument("--pagina", type=int)
    args = ap.parse_args()

    if not STEXT.exists():
        raise SystemExit(
            f"Falta {STEXT}. Genéralo con:\n"
            f"  mutool draw -F stext -o {STEXT} "
            f"01_EXAMENES/banco_hrw/HRW7_Test_Bank_con_respuestas.pdf 1-655")

    total = Counter()
    paginas = {}
    for pagina, chars in leer_lineas():
        if args.pagina and pagina != args.pagina:
            continue
        texto, clases = resolver(chars)
        total.update(clases)
        if clases:
            paginas.setdefault(pagina, []).append(texto)

    if args.pagina:
        for linea in paginas.get(args.pagina, []):
            print("  ", linea)
        return

    if args.resumen or not args.resolver:
        print("Glifos recuperados por clase:\n")
        nombres = {"vector": "→  acento de vector",
                   "negacion": "≠  barra de negación sobre el igual",
                   "ele": "ℓ  ele cursiva (número cuántico orbital)",
                   "epsilon": "ε  épsilon (constante de Coulomb)",
                   "prima": "′  prima (sistema de referencia)",
                   "integral": "∫  integral",
                   "delimitador": "·  delimitador grande (sin resolver)",
                   "aislado": "·  glifo suelto en figura (sin resolver)",
                   "desconocido": "?  sin clasificar"}
        for clase, n in total.most_common():
            print(f"  {n:5}  {nombres.get(clase, clase)}")
        print(f"\n  {sum(total.values()):5}  total")
        print(f"  {len(paginas):5}  páginas afectadas")
        if not args.resolver:
            return

    SALIDA.parent.mkdir(exist_ok=True)
    SALIDA.write_text(
        json.dumps({str(p): ls for p, ls in paginas.items()},
                   ensure_ascii=False, indent=1),
        encoding="utf-8")
    print(f"\n  -> {SALIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
