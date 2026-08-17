#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Arma un PDF de examen con las 12 preguntas del diagnóstico D1,
recortadas del simulacro oficial, con espacio para responder."""
import re, os

SRC = "/home/sebastian/Documents/ANDES/01_EXAMENES/uniandes_admision/2024_ejemplo_examen_admision_MC.pdf"
XML = "sim.xml"
SEL = [1, 2, 6, 7, 9, 11, 12, 15, 17, 20, 21, 23]

META = {
    1:  ("Mecánica", "BASE", ""),
    2:  ("Mecánica", "BASE", ""),
    6:  ("Mecánica", "ALTO", "P1"),
    7:  ("Mecánica", "ALTO", "P2"),
    9:  ("Electromagnetismo", "BASE", ""),
    11: ("Relatividad", "BASE", ""),
    12: ("Electromagnetismo", "ALTO", "P5"),
    15: ("Electromagnetismo", "BASE", ""),
    17: ("Termo y estadística", "BASE", ""),
    20: ("Termo y estadística", "ALTO", "P7"),
    21: ("Moderna y cuántica", "ALTO", "P8"),
    23: ("Moderna y cuántica", "ALTO", "P9"),
}

TOP_LIM, BOT_LIM = 52.0, 748.0     # zona util de cada pagina, en pts desde arriba
LX, RX = 46.0, 44.0                # recorte lateral

d = open(XML, encoding="utf-8", errors="ignore").read()
pages = re.split(r"<page ", d)[1:]
H = float(re.search(r'height="([\d.]+)"', pages[0]).group(1))

q_start = {}
for pi, pg in enumerate(pages, 1):
    for m in re.finditer(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', pg):
        x0, y0, t = float(m.group(1)), float(m.group(2)), m.group(5)
        mm = re.fullmatch(r"(\d{1,2})\.", t)
        if mm and x0 < 115:
            n = int(mm.group(1))
            if 1 <= n <= 24 and n not in q_start:
                q_start[n] = (pi, y0)

NP = len(pages)

# ultimo contenido de texto por pagina (para no arrastrar paginas casi vacias)
fin_pag = {}
for pi, pg in enumerate(pages, 1):
    ys = [float(m.group(1)) for m in
          re.finditer(r'<word xMin="[\d.]+" yMin="[\d.]+" xMax="[\d.]+" yMax="([\d.]+)"', pg)]
    fin_pag[pi] = (max(ys) + 22.0) if ys else BOT_LIM


def tramos(q):
    """Lista de (pagina, y_top, y_bot) en coordenadas desde arriba."""
    p0, y0 = q_start[q]
    nxt = [n for n in sorted(q_start) if n > q]
    if nxt:
        p1, y1 = q_start[nxt[0]]
        y1 -= 6.0
    else:
        p1, y1 = NP, BOT_LIM
    y0 = max(TOP_LIM, y0 - 6.0)
    if p1 == p0:
        return [(p0, y0, min(BOT_LIM, y1))]
    out = [(p0, y0, min(BOT_LIM, max(fin_pag.get(p0, BOT_LIM), y0 + 40)))]
    for p in range(p0 + 1, p1):
        out.append((p, TOP_LIM, min(BOT_LIM, fin_pag.get(p, BOT_LIM))))
    if y1 > TOP_LIM + 12:
        out.append((p1, TOP_LIM, min(BOT_LIM, y1)))
    return out


def inc(p, yt, yb, ancho="\\linewidth"):
    trim_t, trim_b = yt, H - yb
    return (f"\\includegraphics[page={p},trim={LX}pt {trim_b:.1f}pt {RX}pt {trim_t:.1f}pt,"
            f"clip,width={ancho}]{{{SRC}}}")


L = []
L.append(r"""\documentclass[11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[spanish,es-noquoting]{babel}
\usepackage[a4paper,top=1.4cm,bottom=1.3cm,left=2cm,right=2cm,headheight=13pt,headsep=4mm,includehead]{geometry}
\usepackage{graphicx,xcolor,amssymb,fancyhdr,array}
\definecolor{cab}{HTML}{1F3864}
\definecolor{alto}{HTML}{B00020}
\setlength{\parindent}{0pt}
\pagestyle{fancy}\fancyhf{}
\lhead{\small\textbf{Diagnóstico D1} — Admisión Maestría en Física, Uniandes}
\rhead{\small 12 preguntas · 60 minutos}
\cfoot{\small\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\newcommand{\ch}{$\square$}
\newcommand{\bloque}{%
\vfill
\noindent\begin{minipage}[b][4.6cm][t]{\linewidth}
{\color{cab}\rule{\linewidth}{0.8pt}}\\[2mm]
\textbf{Respuesta:}\quad \ch\,a \quad \ch\,b \quad \ch\,c \quad \ch\,d \quad \ch\,e
\hfill \textbf{Tiempo:} \underline{\hspace{1.4cm}} min
\hfill \textbf{Seguridad:} 1 \; 2 \; 3 \; 4 \; 5\\[3mm]
\textbf{Cómo lo pensé:}\\[3.5mm]
\rule{\linewidth}{0.4pt}\\[5.5mm]\rule{\linewidth}{0.4pt}\\[5.5mm]\rule{\linewidth}{0.4pt}\\[5.5mm]\rule{\linewidth}{0.4pt}
\end{minipage}
}
\begin{document}
""")

# portada
L.append(r"""
\thispagestyle{empty}
\begin{center}
{\color{cab}\Huge\textbf{Diagnóstico D1}}\\[2mm]
{\large Examen de admisión --- Maestría en Ciencias, Física --- Uniandes}\\[4mm]
{\large\textbf{12 preguntas \quad · \quad 60 minutos \quad · \quad 5 min por pregunta}}
\end{center}
\vspace{6mm}

\textbf{Reglas}
\begin{itemize}
\item Cronómetro corriendo. Sin apuntes, sin formulario, sin internet.
\item \textbf{Responde las 12}, aunque tengas que adivinar. No hay penalización y quiero ver también tus adivinanzas.
\item Si te trabas más de 5 minutos, marca lo que creas y sigue. Escríbelo en «cómo lo pensé».
\end{itemize}

\vspace{2mm}
\textbf{Los cuatro campos de cada página, y para qué sirven}
\begin{itemize}
\item \textbf{Respuesta} --- marca una sola.
\item \textbf{Tiempo} --- distingue «no sé» de «sé pero soy lento». Son problemas distintos.
\item \textbf{Seguridad (1--5)} --- acertar adivinando no es saber. Y fallar con seguridad 5 es la señal más valiosa de todas.
\item \textbf{Cómo lo pensé} --- dos o tres líneas. Es lo que me deja evaluar el \emph{método} y no solo el resultado. Si te equivocas en una cuenta pero el planteamiento era correcto, eso cambia por completo el diagnóstico.
\end{itemize}

\vspace{3mm}
\textbf{Qué mide este subconjunto}\\[1mm]
Las 12 están elegidas para cubrir las cinco áreas, mitad \textbf{BASE} (Física 1--2, el 55\,\% del examen)
y mitad \textbf{\textcolor{alto}{ALTO}} (los patrones de posgrado, el 40\,\%), tocando 6 de los 10 patrones.
Por eso una hora aquí informa más que tres horas mal repartidas.

\vspace{4mm}
\begin{tabular}{@{}llll@{}}
\textbf{Área} & \textbf{Preguntas} & \textbf{Nivel} & \textbf{Patrones}\\[1mm]
Mecánica & 1, 2, 6, 7 & 2 BASE / 2 ALTO & P1, P2\\
Electromagnetismo & 9, 12, 15 & 2 BASE / 1 ALTO & P5\\
Relatividad & 11 & BASE & ---\\
Termo y estadística & 17, 20 & 1 BASE / 1 ALTO & P7\\
Moderna y cuántica & 21, 23 & 2 ALTO & P8, P9\\
\end{tabular}

\vspace{6mm}
{\color{cab}\rule{\linewidth}{0.8pt}}\\[2mm]
Un número bajo aquí no significa nada malo: es un diagnóstico \emph{antes} de estudiar, y para eso son las 14 semanas.
Lo único que lo arruina es hacerlo con ayuda, porque entonces el plan queda calibrado sobre algo que no existe.
\newpage
""")

for i, q in enumerate(SEL, 1):
    area, nivel, pat = META[q]
    col = r"\textcolor{alto}{ALTO}" if nivel == "ALTO" else "BASE"
    etq = f"{col}" + (f" · {pat}" if pat else "")
    L.append(r"\noindent{\small\textbf{%d de 12} \quad|\quad Pregunta original n.\ %d \quad|\quad %s \quad|\quad %s}\\[2mm]"
             % (i, q, area, etq))
    tr = tramos(q)
    for (p, yt, yb) in tr:
        alto_pt = yb - yt
        if alto_pt < 8:
            continue
        L.append(inc(p, yt, yb))
        L.append(r"\\[1mm]")
    L.append(r"\bloque")
    L.append(r"\newpage")

L.append(r"""
\thispagestyle{empty}
\begin{center}{\color{cab}\Large\textbf{Terminaste}}\end{center}
\vspace{3mm}
Pásame el PDF lleno, una foto de las hojas, o el texto en el bloc de notas. Con eso:
\begin{enumerate}
\item Resuelvo las 12 y las califico. El Departamento no publica las respuestas, así que las derivo yo y te digo de cuáles estoy seguro y de cuáles no.
\item Evalúo tu razonamiento aparte del resultado.
\item Cargo todo al medidor y regenero el reporte, el mapa de habilidades y las recomendaciones de ajuste al cronograma.
\end{enumerate}
\vspace{4mm}
\textbf{Antes de mandarlo, un minuto:} marca con una estrella las preguntas donde sentiste que
\emph{sabías por dónde ir pero no llegaste}. Esas son distintas de las que no supiste empezar,
y el plan cambia según cuál de las dos predomine.
\end{document}
""")

open("examen_d1.tex", "w", encoding="utf-8").write("\n".join(L))
print("examen_d1.tex generado")
for q in SEL:
    print(f"  Q{q}: {len(tramos(q))} tramo(s) -> {tramos(q)}")
