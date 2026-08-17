"""
Auditoría de notación del corpus.

Buscar los fallos de uno en uno no escala: cada vez que aparece uno hay que
suponer que hay cincuenta iguales que nadie ha visto. Esto barre todo el corpus
buscando las formas en que la notación se rompe al extraer texto de un PDF.

Cada patrón describe un síntoma concreto, no una sospecha vaga, y viene con
ejemplos para poder mirarlos.

Uso:
    python3 auditar.py                 # informe por patrón
    python3 auditar.py --patron exponente_perdido --ver 12
"""

import argparse
import json
import re
from collections import Counter
from pathlib import Path

CRUDO = Path(__file__).parent / "crudo"

# Cada entrada: nombre -> (expresión, explicación de por qué está mal)
PATRONES = {
    "exponente_perdido": (
        # "10-9" o "10 -9" sin marca de potencia: el superíndice no se detectó.
        re.compile(r"(?<![\^{])\b10\s*[-−]\s*\d+(?!\})"),
        "una potencia de diez sin exponente: 10-9 en vez de 10^{-9}",
    ),
    "unidad_sin_exponente": (
        # "m/s 2" con el dos separado. Se exige el espacio: "m/s2" pegado
        # aparece en prosa legítima y "100 m/s" no tiene por qué llevar nada.
        re.compile(r"\b(?:m|cm|km)\s*/\s*s\s+\d\b|\bkg\s*/\s*m\s+\d\b"),
        "una unidad con el exponente suelto: m/s 2 en vez de m/s^{2}",
    ),
    "simbolo_al_borde": (
        re.compile(r"^\s*\\times|\\times\s*$"),
        "el signo de multiplicar al principio o al final, sin nada que multiplicar",
    ),
    "potencia_sin_multiplicar": (
        # "3.1 10^{-10}" sin el × entre medias.
        re.compile(r"\d\s+10\^\{"),
        "un número y una potencia sin el signo de multiplicar entre ellos",
    ),
    "exponente_vacio": (
        re.compile(r"[\^_]\{\s*\}"),
        "una marca de exponente o subíndice sin contenido",
    ),
    "llave_huerfana": (
        # Una llave que no forma parte de ^{...} ni de _{...}. El patrón
        # anterior marcaba las 928 llaves de cierre de todos los subíndices
        # legítimos: un informe con más ruido que señal no sirve para nada.
        re.compile(r"\{(?<![\^_]\{)[^{}]*\}|\}\s*\}"),
        "una llave suelta, resto de una fórmula que se rompió",
    ),
    "grados_sueltos": (
        re.compile(r"\d\s+[°◦]"),
        "el símbolo de grados separado de su número",
    ),
}


def cargar():
    tarjetas = []
    for ruta in sorted(CRUDO.glob("*.json")):
        if ruta.name == "figuras.json":
            continue
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        if isinstance(datos, list):
            for r in datos:
                r["_archivo"] = ruta.name
                tarjetas.append(r)
    return tarjetas


def campos(t):
    """Los textos de una tarjeta donde puede haber notación rota."""
    yield "enunciado", t.get("enunciado", "")
    for letra, texto in (t.get("opciones") or {}).items():
        yield f"opción {letra}", texto
    for clave in ("texto", "titulo"):
        if t.get(clave):
            yield clave, t[clave]


def exponentes_inconsistentes(t):
    """Opciones donde unas llevan potencia y otras no.

    Parecía la señal más fiable de un exponente perdido, y no lo es. Al
    contrastar los seis casos contra el PDF, los seis eran legítimos: en
    "0 · 10^{-8} A · 10^{-6} A · 10^{-4} A · 100 A" ese 100 A es un distractor
    puesto a propósito, no una potencia mal leída. Se deja como aviso para
    mirar a mano, nunca como motivo para descartar.
    """
    opciones = {k: v for k, v in (t.get("opciones") or {}).items() if v.strip()}
    if len(opciones) < 3:
        return None

    con_potencia = [k for k, v in opciones.items() if re.search(r"10\^\{", v)]
    sin_potencia = [k for k, v in opciones.items()
                    if not re.search(r"10\^\{", v) and re.search(r"\b10\d", v)]

    if con_potencia and sin_potencia:
        return (f"{len(con_potencia)} con potencia, "
                f"{len(sin_potencia)} sin ella: {sin_potencia}")
    return None


def auditar(tarjetas, solo=None):
    hallazgos = {nombre: [] for nombre in PATRONES}
    hallazgos["exponente_inconsistente"] = []

    for t in tarjetas:
        if not solo or solo == "exponente_inconsistente":
            aviso = exponentes_inconsistentes(t)
            if aviso:
                hallazgos["exponente_inconsistente"].append(
                    (t, "opciones", aviso, " | ".join(t["opciones"].values())))

        for nombre, (patron, _) in PATRONES.items():
            if solo and nombre != solo:
                continue
            for campo, texto in campos(t):
                if not isinstance(texto, str):
                    continue
                m = patron.search(texto)
                if m:
                    hallazgos[nombre].append((t, campo, m.group(0), texto))
                    break
    return hallazgos


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--patron", help="ver solo uno")
    ap.add_argument("--ver", type=int, default=3, help="cuántos ejemplos mostrar")
    args = ap.parse_args()

    tarjetas = cargar()
    print(f"{len(tarjetas)} tarjetas en {len(set(t['_archivo'] for t in tarjetas))} archivos\n")

    hallazgos = auditar(tarjetas, args.patron)
    total = 0

    descripciones = {n: e for n, (_, e) in PATRONES.items()}
    descripciones["exponente_inconsistente"] = (
        "unas opciones con potencia y otras sin ella, en la misma pregunta")

    for nombre, explicacion in descripciones.items():
        if args.patron and nombre != args.patron:
            continue
        casos = hallazgos[nombre]
        total += len(casos)
        marca = "ok " if not casos else "MAL"
        print(f"  {marca}  {nombre:26} {len(casos):5d}   {explicacion}")

        for t, campo, coincidencia, texto in casos[:args.ver]:
            recorte = texto.strip()
            if len(recorte) > 130:
                pos = texto.find(coincidencia)
                recorte = "…" + texto[max(0, pos - 55):pos + 75].strip() + "…"
            print(f"          {t['id']} · {campo} · {coincidencia!r}")
            print(f"            {recorte}")

    print(f"\n{total} tarjetas con algún síntoma "
          f"({100 * total / max(1, len(tarjetas)):.1f} %)")

    if not args.patron:
        por_archivo = Counter(
            t["_archivo"] for casos in hallazgos.values() for t, *_ in casos)
        if por_archivo:
            print("\nPor fuente:")
            for archivo, n in por_archivo.most_common():
                print(f"  {n:5d}  {archivo}")


if __name__ == "__main__":
    main()
