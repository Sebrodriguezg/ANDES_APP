"""Dos simulacros de 25 preguntas con la proporción del examen de la UNAL.

Maestría en Ciencias – Física, plan de investigación (16-oct-2026):
Newtoniana 3 · Analítica 3 · EM 5 · Moderna 4 · Cuántica 3 · Termo 2 ·
Experimental 3 · Física matemática 2.

S1 sale entero del GR0177, que no está en la app. S2 sale de las preguntas del
GR1775 que tampoco están en la app, completado con el GR0177 donde el GR1775 no
alcanza. Cada recorte se revisó a ojo: los del GR1775 que salían partidos
(1, 3, 15, 17, 18, 45, 48) se dejaron fuera.

    python3 05_SIMULACROS/unal/armar.py

Escribe en esta carpeta el examen y la clave de cada simulacro, y la clave
para el medidor en 06_SEGUIMIENTO/claves/unal_s1.csv y unal_s2.csv.
"""

import csv
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

from recortar import DPI, PDFS, Examen

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
CLAVES = RAIZ / "06_SEGUIMIENTO/claves"
RECORTES = AQUI / "_recortes"

# Área UNAL -> área del medidor
MEDIDOR = {
    "Mecánica newtoniana": "mecanica", "Mecánica analítica": "mecanica",
    "Electromagnetismo": "electromagnetismo", "Física moderna": "moderna_cuantica",
    "Mecánica cuántica": "moderna_cuantica", "Termo y estadística": "termo_estadistica",
    "Física experimental": "otros", "Física matemática": "otros",
}

SIMULACROS = {
    "S1": [
        ("Mecánica newtoniana", [("GR0177", 26), ("GR0177", 55), ("GR0177", 89)]),
        ("Mecánica analítica", [("GR0177", 74), ("GR0177", 90), ("GR0177", 92)]),
        ("Electromagnetismo", [("GR0177", 8), ("GR0177", 10), ("GR0177", 42),
                               ("GR0177", 58), ("GR0177", 61)]),
        ("Física moderna", [("GR0177", 18), ("GR0177", 31), ("GR0177", 67), ("GR0177", 80)]),
        ("Mecánica cuántica", [("GR0177", 29), ("GR0177", 44), ("GR0177", 82)]),
        ("Termo y estadística", [("GR0177", 37), ("GR0177", 49)]),
        ("Física experimental", [("GR0177", 15), ("GR0177", 16), ("GR0177", 39)]),
        ("Física matemática", [("GR0177", 28), ("GR0177", 75)]),
    ],
    "S2": [
        ("Mecánica newtoniana", [("GR1775", 14), ("GR1775", 40), ("GR1775", 62)]),
        ("Mecánica analítica", [("GR1775", 51), ("GR0177", 22), ("GR0177", 57)]),
        ("Electromagnetismo", [("GR1775", 32), ("GR1775", 33), ("GR1775", 34),
                               ("GR1775", 59), ("GR0177", 86)]),
        ("Física moderna", [("GR1775", 19), ("GR1775", 21), ("GR0177", 68), ("GR0177", 71)]),
        ("Mecánica cuántica", [("GR1775", 38), ("GR1775", 54), ("GR1775", 55)]),
        ("Termo y estadística", [("GR1775", 25), ("GR1775", 70)]),
        ("Física experimental", [("GR1775", 44), ("GR0177", 14), ("GR0177", 100)]),
        ("Física matemática", [("GR1775", 12), ("GR0177", 65)]),
    ],
}

MINUTOS = 75  # 3 min por pregunta: holgado para el GRE, apretado para pensar dos veces


def clave_gr0177():
    """{n: (letra, p+)} desde la hoja de respuestas del propio PDF."""
    txt = subprocess.run(["pdftotext", "-layout", str(PDFS["GR0177"]), "-"],
                         capture_output=True, text=True).stdout
    bloque = txt[txt.index("Worksheet for the Physics Test, Form GR0177"):]
    bloque = bloque[:bloque.index("Correct (C)")]
    return {int(n): (l, int(p)) for n, l, p in re.findall(r"(\d{1,3})\s+([A-E])\s+(\d{1,2})\b", bloque)}


def clave_gr1775():
    with open(CLAVES / "ets_gr1775.csv", encoding="utf-8") as f:
        return {int(r["pregunta"]): (r["correcta"], int(r["p_mas"])) for r in csv.DictReader(f)}


def unir(rutas, destino):
    """Los tramos de una pregunta, uno debajo del otro, en una sola imagen."""
    ims = [Image.open(r) for r in rutas]
    w = max(i.width for i in ims)
    lienzo = Image.new("L", (w, sum(i.height for i in ims)), 255)
    y = 0
    for i in ims:
        lienzo.paste(i, (0, y))
        y += i.height
    lienzo.save(destino)
    return lienzo.width


PRE = r"""\documentclass[10pt]{article}
\usepackage[utf8]{inputenc}\usepackage[T1]{fontenc}\usepackage[spanish,es-noquoting]{babel}
\usepackage[letterpaper,top=1.5cm,bottom=1.5cm,left=1.6cm,right=1.6cm]{geometry}
\usepackage{graphicx,xcolor,fancyhdr,lastpage,array,booktabs,longtable}
\definecolor{cab}{HTML}{1F3864}
\setlength{\parindent}{0pt}
\pagestyle{fancy}\fancyhf{}
\lhead{\small\textbf{%s}}\rhead{\small UNAL Física \textperiodcentered\ 16-oct \textperiodcentered\ \thepage/\pageref{LastPage}}
\renewcommand{\headrulewidth}{0.4pt}
\begin{document}
"""


def examen_tex(nombre, preguntas):
    p = [PRE % f"Simulacro {nombre} --- 25 preguntas, {MINUTOS} minutos"]
    p.append(r"{\color{cab}\LARGE\textbf{Simulacro " + nombre + r"}}\par\vspace{2mm}")
    p.append(
        r"\fbox{\parbox{\dimexpr\linewidth-2\fboxsep}{"
        rf"\textbf{{Reglas.}} {MINUTOS} minutos con cronómetro, sin libros ni formulario. Proporción del examen de la UNAL: "
        r"newtoniana 3, analítica 3, EM 5, moderna 4, cuántica 3, termo 2, experimental 3, matemática 2. "
        r"Si una pregunta pasa de 4 minutos, márcala y sigue. Marca en la hoja del final, no en las preguntas. "
        r"Al terminar: \texttt{python3 06\_SEGUIMIENTO/medidor.py simulacro} y elige \texttt{unal\_"
        + nombre.lower() + r"}. Después, la clave.}}\par\vspace{4mm}")
    for i, (area, fuente, n, img, ancho_px) in enumerate(preguntas, 1):
        ancho_pt = min(ancho_px * 72 / DPI, 520)
        p.append(r"\noindent\begin{minipage}{\linewidth}")
        p.append(rf"{{\color{{cab}}\large\textbf{{{i}}}}}\par\vspace{{1mm}}")
        p.append(rf"\includegraphics[width={ancho_pt:.0f}pt]{{{img}}}\par\vspace{{5mm}}")
        p.append(r"\end{minipage}\par")
    p.append(r"\newpage{\color{cab}\Large\textbf{Hoja de respuestas}}\par\vspace{4mm}")
    p.append(r"\renewcommand{\arraystretch}{1.6}\begin{tabular}{r|ccccc|l}")
    p.append(r"\# & A & B & C & D & E & Tiempo / dudé \\ \hline")
    for i in range(1, len(preguntas) + 1):
        p.append(rf"{i} & $\circ$ & $\circ$ & $\circ$ & $\circ$ & $\circ$ & \rule{{5cm}}{{0.3pt}} \\")
    p.append(r"\end{tabular}\par\vspace{5mm}Hora de inicio: \rule{3cm}{0.3pt} \qquad Hora de fin: \rule{3cm}{0.3pt}")
    p.append(r"\end{document}")
    return "\n".join(p)


def clave_tex(nombre, filas):
    p = [PRE % f"Clave del simulacro {nombre} --- abrir solo después de calificar"]
    p.append(r"{\color{cab}\LARGE\textbf{Clave --- Simulacro " + nombre + r"}}\par\vspace{3mm}")
    p.append(r"\small P+ es el porcentaje de quienes presentaron el GRE que la acertaron: menos de 40 es difícil de verdad."
             r" Las del GR0177 tienen solución detallada en \texttt{01\_EXAMENES/gre\_physics/GR0177\_solutions\_grephysics.pdf}"
             r" (busca ``Problem N'').\par\vspace{3mm}\normalsize")
    p.append(r"\renewcommand{\arraystretch}{1.35}\begin{longtable}{r c l l r}")
    p.append(r"\# & Resp. & Área UNAL & Fuente & P+ \\ \midrule")
    for i, (area, fuente, n, letra, pmas) in enumerate(filas, 1):
        p.append(rf"{i} & \textbf{{{letra}}} & {area} & {fuente} n.º {n} & {pmas}\,\% \\")
    p.append(r"\end{longtable}")
    p.append(r"\vspace{4mm}\textbf{Qué hacer con lo fallado.} Para cada error: (1) clasifícalo con el medidor "
             r"(concepto, álgebra, lectura, tiempo, descuido); (2) busca el tema en la lista de la Hoja y escríbelo en rojo; "
             r"(3) rehaz la pregunta mañana sin mirar la solución.")
    p.append(r"\end{document}")
    return "\n".join(p)


def compilar(base, fuente):
    tex = AQUI / f"{base}.tex"
    tex.write_text(fuente, encoding="utf-8")
    for _ in range(2):
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex.name],
                           cwd=AQUI, capture_output=True, text=True, errors="replace")
        if r.returncode:
            print(r.stdout[-2000:])
            sys.exit(f"falló {base}")
    for ext in ("aux", "log", "tex"):
        (AQUI / f"{base}.{ext}").unlink(missing_ok=True)
    print(f"ok  {base}.pdf")


def main():
    examenes = {n: Examen(n) for n in PDFS}
    claves = {"GR0177": clave_gr0177(), "GR1775": clave_gr1775()}
    assert len(claves["GR0177"]) == 100, f"clave GR0177 incompleta: {len(claves['GR0177'])}"

    usadas = set()
    for nombre, bloques in SIMULACROS.items():
        preguntas, filas = [], []
        for area, lista in bloques:
            for fuente, n in lista:
                assert (fuente, n) not in usadas, f"repetida: {fuente} {n}"
                usadas.add((fuente, n))
                tramos = examenes[fuente].recortar(n, RECORTES / "tramos")
                img = RECORTES / f"{fuente}_{n:03d}.png"
                ancho = unir(tramos, img)
                preguntas.append((area, fuente, n, img.relative_to(AQUI).as_posix(), ancho))
                letra, pmas = claves[fuente][n]
                filas.append((area, fuente, n, letra, pmas))
        assert len(preguntas) == 25, f"{nombre}: {len(preguntas)} preguntas"

        compilar(f"simulacro_{nombre}", examen_tex(nombre, preguntas))
        compilar(f"clave_{nombre}", clave_tex(nombre, filas))

        with open(CLAVES / f"unal_{nombre.lower()}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["pregunta", "correcta", "p_mas", "area", "nivel", "tema"])
            for i, (area, fuente, n, letra, pmas) in enumerate(filas, 1):
                w.writerow([i, letra, pmas, MEDIDOR[area], "ALTO" if pmas < 45 else "BASE",
                            f"{area} ({fuente} n.º {n})"])
        print(f"ok  06_SEGUIMIENTO/claves/unal_{nombre.lower()}.csv")


if __name__ == "__main__":
    main()
