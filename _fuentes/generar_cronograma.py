#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera el cronograma LaTeX para el examen de admision Uniandes."""
import datetime as dt
import csv, os

INICIO = dt.date(2026, 8, 17)   # lunes
EXAMEN = dt.date(2026, 11, 23)  # lunes

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES = ["enero","febrero","marzo","abril","mayo","junio","julio",
         "agosto","septiembre","octubre","noviembre","diciembre"]
VENTANA = {0: "16:00", 1: "16:00", 2: "16:00", 3: "19:00", 4: "19:00"}


def esc(s):
    for a, b in [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"),
                 ("$", r"\$"), ("#", r"\#"), ("_", r"\_"), ("{", r"\{"),
                 ("}", r"\}"), ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}")]:
        s = s.replace(a, b)
    return s


def tt(p):
    return r"\texttt{\small " + esc(p) + "}"


# ---------------------------------------------------------------- contenido
# Cada semana: (titulo, objetivo, entregable, [(min, ext) x5], domingo)
SEM = []

SEM.append((
 "Diagnóstico y los 10 patrones",
 "El diagnóstico ya dio su número: 2 de 12, con la base en 0/6 y los patrones en 2/6. Esta semana se cierra la otra mitad y se convierte el resultado en los 10 patrones escritos a mano.",
 "\\texttt{04\\_ESTUDIO/formularios/patrones.md} con los 10 derivados, no copiados.",
 [("Los 10 patrones de 03\\_TEMARIO/00\\_mapa\\_simulacro.md. Empieza por los cuatro que fallaste: P2 Poisson, P7 contacto térmico, P8 bosones en caja, P9 escalón.",
   "Además: P3, P4, P6 y P10, que el diagnóstico no llegó a evaluar."),
  ("Cierra el diagnóstico: preguntas 13--24 del simulacro, 60 min cronometrados, sin apuntes.",
   "Además: regístralo con \\texttt{python3 06\\_SEGUIMIENTO/medidor.py simulacro}."),
  ("Corre \\texttt{medidor.py reporte} y abre \\texttt{tablero.html}. Identifica tus 2 áreas más débiles.",
   "Además: al registrar el simulacro, clasifica cada fallo por causa. Es el paso que más informa."),
  ("Sears Vol.\\,1, cinemática 1D y 2D: lee el resumen del capítulo y resuelve 8 problemas de fin de capítulo.",
   "Además: 8 problemas más + Irodov §1.1 (p.\\,11), 5 problemas."),
  ("Banco HRW caps.\\,2--4: 30 preguntas cronometradas a 2 min. Corrige con el «Ans:» al pie de cada una.",
   "60 preguntas en lugar de 30.")],
 "Comodín. Recupera lo que no alcanzaste. Si vas al día, rehaz los 5 fallos más graves del diagnóstico."))

SEM.append((
 "Newton, energía y momento",
 "Consolidar el núcleo de Física 1. Aquí viven 4 de las 24 preguntas del simulacro.",
 "04\\_ESTUDIO/formularios/mecanica\\_I.md",
 [("Sears Vol.\\,1, leyes de Newton y fricción: resumen + 8 problemas. Incluye el \\textbf{problema 5.88} (es la pregunta 2 del examen real).",
   "Además: Morin cap.\\,3 (p.\\,51), lee 3 ejemplos resueltos y haz 5 problemas."),
  ("Sears, trabajo y energía: resumen + 8 problemas.",
   "Además: Morin cap.\\,5 (p.\\,138), 6 problemas con solución completa."),
  ("Sears, momento lineal, impulso y colisiones: 8 problemas.",
   "Además: Irodov §1.3 (p.\\,30), 6 problemas."),
  ("Repaso activo: rehaz \\emph{sin mirar} 5 problemas que fallaste esta semana.",
   "Además: Morin cap.\\,2 estática (p.\\,22), 5 problemas."),
  ("Banco HRW caps.\\,5--9: 30 preguntas a 2 min.",
   "60 preguntas.")],
 "Comodín. Cierra el formulario de mecánica I si quedó pendiente."))

SEM.append((
 "Rotación, gravitación, oscilaciones y fluidos",
 "Terminar Física 1. La fórmula del oscilador forzado es pregunta directa del examen.",
 "04\\_ESTUDIO/formularios/mecanica\\_II.md + 1 tarjeta Anki (amplitud del oscilador forzado).",
 [("Sears, cinemática y dinámica rotacional, momento de inercia: 8 problemas. Incluye el \\textbf{problema 9.15} (es la pregunta 3 del examen real).",
   "Además: Morin cap.\\,8 (p.\\,309), 5 problemas."),
  ("Sears, momento angular, rodadura y torque: 8 problemas.",
   "Además: Irodov §1.5 (p.\\,47), 6 problemas."),
  ("Sears, gravitación y leyes de Kepler: 6 problemas. Luego fluidos (Arquímedes, Bernoulli): 4 problemas.",
   "Además: Irodov §1.4 (p.\\,43) y §1.7 (p.\\,62), 8 problemas."),
  ("Oscilaciones. Morin cap.\\,4 (p.\\,101), 6 problemas. \\textbf{Clave:} oscilador forzado amortiguado --- memoriza la amplitud en estado estacionario.",
   "Además: MIT 8.03 ProblemSet1 a ProblemSet3."),
  ("Banco HRW caps.\\,10--15: 30 preguntas a 2 min.",
   "60 preguntas.")],
 "Comodín. Escribe el formulario de mecánica II y la tarjeta del oscilador forzado."))

SEM.append((
 "Mecánica analítica --- LA SEMANA MÁS RENTABLE",
 "Tres preguntas del examen (6, 7 y 8) salen de aquí y son inaccesibles sin haberlas visto. 12\\,\\% del examen en 5 sesiones.",
 "04\\_ESTUDIO/formularios/mecanica\\_analitica.md con los 3 patrones + 3 tarjetas Anki. \\textbf{No pases a la semana 5 sin esto.}",
 [("Tong \\emph{Classical Dynamics}: coordenadas generalizadas y ecuaciones de Lagrange. Lee y \\textbf{rededuce a mano}. + Morin cap.\\,6 (p.\\,218), 3 problemas.",
   "Además: 5 problemas más de Morin cap.\\,6."),
  ("Tong: hamiltoniano, transformación de Legendre, ecuaciones canónicas. Rededuce. + Lim \\emph{Mechanics} 2068--2084, 3 problemas.",
   "Además: 4 problemas más de ese rango."),
  ("\\textbf{PATRÓN 1 --- Espacio de fase:} $T(E)=dA/dE$. Entiende la derivación completa y escríbela de memoria. Tong, variables acción-ángulo.",
   "Además: Lim \\emph{Mechanics} 2028--2067 (pequeñas oscilaciones), 4 problemas."),
  ("\\textbf{PATRÓN 2 --- Corchetes de Poisson:} $\\{q_i,p_j\\}=\\delta_{ij}$, $\\{L_i,p_j\\}=\\varepsilon_{ijk}p_k$, $\\{L_i,L_j\\}=\\varepsilon_{ijk}L_k$. Derívalos tú, no los copies.",
   "Además: Goldstein, sección de corchetes de Poisson: 4 ejercicios."),
  ("\\textbf{PATRÓN 3 --- Scattering esfera dura:} $b=R\\cos(\\theta/2)$, $d\\sigma/d\\Omega=R^2/4$, $\\sigma=\\pi R^2$. Deriva y memoriza. Luego: preguntas de mecánica analítica de GR8677 y GR9277.",
   "Además: Lim \\emph{Mechanics} 2001--2027, 5 problemas.")],
 "Comodín. Si algún patrón no quedó, hoy es el día. Es la semana que no se puede dejar a medias."))

SEM.append((
 "Electrostática",
 "Abrir el bloque de E\\&M, que pesa 28\\,\\%. Griffiths es el texto de las próximas tres semanas.",
 "04\\_ESTUDIO/formularios/em\\_I.md",
 [("Griffiths cap.\\,2: Coulomb, campo eléctrico, ley de Gauss (§2.1--2.2). 4 problemas.",
   "Además: 4 problemas más + Irodov §3.1 (p.\\,105), 5 problemas."),
  ("Griffiths §2.3, potencial eléctrico --- de ahí sale la \\textbf{pregunta 15}. 5 problemas.",
   "Además: Sears Vol.\\,2, potencial: 8 problemas."),
  ("Conductores y capacitancia: Griffiths §2.5 + Sears Vol.\\,2. 8 problemas.",
   "Además: Irodov §3.3 (p.\\,118), 6 problemas."),
  ("Dieléctricos: Griffiths cap.\\,4 (p.\\,160), §4.1--4.3. 4 problemas.",
   "Además: Lim \\emph{Electromagnetism} 1043--1061, 4 problemas."),
  ("Banco HRW caps.\\,21--25: 30 preguntas a 2 min.",
   "60 preguntas.")],
 "Comodín. Formulario de electrostática."))

SEM.append((
 "Magnetostática, circuitos e inducción",
 "La mitad mecánica del E\\&M. Los circuitos son preguntas rápidas: aprovéchalas.",
 "04\\_ESTUDIO/formularios/em\\_II.md",
 [("Griffiths cap.\\,5: fuerza de Lorentz y Biot--Savart (§5.2, p.\\,215). Memoriza $B=\\mu_0 I/2r$ en el centro de una espira (\\textbf{pregunta 13}). 5 problemas.",
   "Además: Lim \\emph{EM} 2001--2038, 5 problemas."),
  ("Griffiths §5.3.3, aplicaciones de Ampère (p.\\,225) --- de ahí sale la \\textbf{pregunta 9}. Resuelve el conductor cilíndrico hueco en las 3 regiones.",
   "Además: Irodov §3.5 (p.\\,136), 6 problemas."),
  ("Corriente, resistencia y circuitos: Sears Vol.\\,2 + Lim \\emph{EM} 3001--3026. 10 problemas.",
   "Además: Irodov §3.4 (p.\\,125), 8 problemas."),
  ("Faraday e inductancia: Griffiths §7.1--7.2 (p.\\,285--320). 5 problemas.",
   "Además: Lim \\emph{EM} 2039--2063, 5 problemas."),
  ("Banco HRW caps.\\,26--31: 30 preguntas a 2 min.",
   "60 preguntas.")],
 "Comodín. Formulario de magnetostática e inducción."))

SEM.append((
 "Maxwell, gauge y ondas EM --- SEGUNDA SEMANA MÁS RENTABLE",
 "Aquí están las preguntas 10 y 12, los dos patrones caros de E\\&M.",
 "04\\_ESTUDIO/formularios/em\\_III.md + 2 tarjetas Anki (gauge, armónicos esféricos).",
 [("Griffiths §7.3 (p.\\,321): ecuaciones de Maxwell completas y corriente de desplazamiento. Escríbelas de memoria.",
   "Además: cap.\\,8 (p.\\,345), vector de Poynting."),
  ("\\textbf{PATRÓN 4 --- Gauge.} Griffiths §10.1.2 (p.\\,419) y §10.1.3 (p.\\,421). De ahí sale la \\textbf{pregunta 10}. Deriva la condición de Lorenz y la de Coulomb.",
   "Además: Tong \\emph{Electromagnetism}, sección de potenciales."),
  ("\\textbf{PATRÓN 5 --- Armónicos esféricos.} Griffiths §3.3.2 (p.\\,137): esfera conductora a tierra en campo uniforme. Es la \\textbf{pregunta 12}. Resuélvela entera.",
   "Además: Griffiths §3.2, método de imágenes (p.\\,121): 4 problemas."),
  ("Ondas EM: Griffiths §9.1--9.2 (p.\\,364--381). Polarización, reflexión y transmisión. 4 problemas.",
   "Además: Lim \\emph{EM} 1062--1095, 5 problemas."),
  ("Preguntas de ondas EM y potenciales de GR9677 y GR0177, cronometradas.",
   "Además: Banco HRW caps.\\,32--33, 30 preguntas.")],
 "Comodín. Los patrones 4 y 5 deben quedar cerrados hoy."))

SEM.append((
 "Relatividad especial",
 "Cierra E\\&M y prepara las preguntas 11 y 22. Punto medio del plan: momento de reajustar.",
 "04\\_ESTUDIO/formularios/relatividad.md. \\textbf{Revisa métricas y reajusta el plan si vas atrasado.}",
 [("Griffiths §12.1 (p.\\,477): postulados, geometría, transformaciones de Lorentz (§12.1.3, p.\\,493). 4 problemas.",
   "Además: MIT 8.20 pset1 con su solución."),
  ("Dilatación y contracción. Practica la expansión para $\\beta\\ll1$: $\\gamma\\approx1+\\beta^2/2$ --- es la \\textbf{pregunta 11}. 6 problemas.",
   "Además: MIT 8.20 pset2 con su solución."),
  ("Griffiths §12.2 (p.\\,507): energía y momento relativistas, $E^2=(pc)^2+(mc^2)^2$. 6 problemas.",
   "Además: Irodov §1.8 (p.\\,67), 6 problemas."),
  ("Doppler relativista: factor $\\sqrt{(1+\\beta)/(1-\\beta)}$. Es la base de la \\textbf{pregunta 22}. Deriva y haz 4 problemas.",
   "Además: MIT 8.20 midterm1 con su solución."),
  ("Banco HRW cap.\\,37: 25 preguntas a 2 min. Luego preguntas de relatividad de los 4 GRE.",
   "Además: MIT 8.20 midterm2 con su solución.")],
 "Comodín. \\textbf{Corte de control:} corre \\texttt{medidor.py reporte} y lee las recomendaciones. Si algún área va bajo 55\\,\\%, róbale sesiones a óptica (semana 13)."))

SEM.append((
 "Termodinámica",
 "Bloque de 20\\,\\%. Schroeder cubre esta semana y la siguiente completas.",
 "04\\_ESTUDIO/formularios/termodinamica.md. \\textbf{Pide ya las 2 cartas de referencia} --- dependen de terceros.",
 [("Schroeder §1.1--1.3 (p.\\,1--16): equilibrio térmico, gas ideal, equipartición. 5 problemas.",
   "Además: Sears Vol.\\,1, temperatura y expansión térmica (\\textbf{pregunta 16}): 6 problemas."),
  ("Schroeder §1.4--1.5 (p.\\,17--27): calor, trabajo, $W=-\\int p\\,dV$. Es la \\textbf{pregunta 18}. 6 problemas.",
   "Además: Irodov §2.2 (p.\\,78), 6 problemas."),
  ("Schroeder §1.6 (p.\\,28): capacidades caloríficas y calor latente. Calorimetría con cambios de fase --- \\textbf{pregunta 17}. 6 problemas.",
   "Además: Lim \\emph{Thermodynamics}, parte I: 6 problemas."),
  ("Schroeder cap.\\,4 (p.\\,122): máquinas térmicas y ciclo de Carnot. 5 problemas.",
   "Además: cap.\\,5 §5.3 (p.\\,166), Clausius--Clapeyron."),
  ("Banco HRW caps.\\,18--20: 30 preguntas a 2 min.",
   "60 preguntas.")],
 "Comodín. Formulario de termodinámica."))

SEM.append((
 "Física estadística",
 "Tres patrones caros seguidos: entropía combinatoria, contacto térmico y estadística cuántica.",
 "04\\_ESTUDIO/formularios/estadistica.md + 3 tarjetas Anki.",
 [("Schroeder §2.1--2.2 (p.\\,49--55): multiplicidad, sistemas de dos estados, sólido de Einstein. 4 problemas.",
   "Además: §2.4, aproximación de Stirling (p.\\,60)."),
  ("\\textbf{PATRÓN 6 --- Entropía combinatoria.} Schroeder §2.6 (p.\\,74): $S=k\\ln\\Omega$. Es la \\textbf{pregunta 19}. Resuelve el caso de las monedas.",
   "Además: MIT 8.044 ps1 con su solucionario pss1."),
  ("\\textbf{PATRÓN 7 --- Contacto térmico.} Schroeder §2.3 (p.\\,56) y §3.1 (p.\\,85): maximizar $\\Omega_A\\Omega_B$. Es la \\textbf{pregunta 20}.",
   "Además: MIT 8.044 ps2 con pss2."),
  ("Schroeder cap.\\,6 (p.\\,220): factor de Boltzmann, función de partición, distribución de Maxwell (§6.4, p.\\,242). 5 problemas.",
   "Además: Lim \\emph{Thermodynamics}, parte II: 6 problemas."),
  ("\\textbf{PATRÓN 8 --- Bosones y fermiones.} Schroeder §7.2 (p.\\,262) y §7.4, cuerpo negro (p.\\,288). Luego preguntas de estadística de los 4 GRE.",
   "Además: MIT 8.044 exam1\\_03 con su solución.")],
 "Comodín. Formulario de estadística y las 3 tarjetas."))

SEM.append((
 "Física moderna y cuántica I",
 "Arranca el bloque más caro: todas las preguntas de cuántica son de nivel superior.",
 "04\\_ESTUDIO/formularios/moderna.md. \\textbf{Borrador de la carta de intención} (máx.\\ 1000 palabras, nombra grupos de investigación).",
 [("Eisberg \\& Resnick: radiación de cuerpo negro y efecto fotoeléctrico. 6 problemas.",
   "Además: efecto Compton, 6 problemas."),
  ("Eisberg: modelo de Bohr, series espectrales, energía de ionización, De Broglie. 6 problemas.",
   "Además: Lim \\emph{Atomic}, sección de física atómica: 5 problemas."),
  ("Griffiths QM cap.\\,1 y §2.1--2.2: función de onda, Schrödinger, pozo infinito. Memoriza el espectro. 4 problemas.",
   "Además: Lim \\emph{QM} 1001--1071, 5 problemas."),
  ("\\textbf{PATRÓN 9 --- Escalón de potencial.} Griffiths QM cap.\\,2. Deriva $R=\\left(\\frac{k_1-k_2}{k_1+k_2}\\right)^2$ y resuelve el caso $E=9V_0/8$ (da $k_1/k_2=3$, luego $R=1/4$) --- es la \\textbf{pregunta 23}.",
   "Además: barrera y tunelamiento, 4 problemas."),
  ("Banco HRW caps.\\,38--40: 25 preguntas a 2 min. Luego preguntas de moderna de los 4 GRE.",
   "Además: MIT 8.04 ps1 a ps3.")],
 "Comodín. Formulario de moderna. Avanza la carta de intención."))

SEM.append((
 "Cuántica II",
 "Cierra los 10 patrones. Aquí están las preguntas 21 y 24.",
 "04\\_ESTUDIO/formularios/cuantica.md + 4 tarjetas Anki. \\textbf{Los 10 patrones completos.}",
 [("\\textbf{PATRÓN 10 --- Oscilador armónico.} Griffiths QM §2.3.1, método algebraico: $a$, $a^\\dagger$, espectro. Deriva $\\langle x\\rangle(t)$.",
   "Además: evolución de $\\langle(\\Delta x)^2\\rangle(t)$ --- es la \\textbf{pregunta 24}. Resuélvela entera."),
  ("Griffiths QM cap.\\,3: formalismo, operadores hermíticos, notación de Dirac, incertidumbre. 4 problemas.",
   "Además: MIT 8.05 Chap\\_01 a Chap\\_03."),
  ("Griffiths QM cap.\\,4: Schrödinger 3D, átomo de hidrógeno, momento angular. Autovalores de $L^2$ y $L_z$. 4 problemas.",
   "Además: Lim \\emph{QM} 3001--3048, 5 problemas."),
  ("Griffiths QM §5.1, partículas idénticas. Bosones vs.\\ fermiones en caja 2D --- es la \\textbf{pregunta 21}. Resuélvela.",
   "Además: Lim \\emph{QM} 7001--7037, 4 problemas."),
  ("Preguntas de cuántica de los 4 GRE, cronometradas.",
   "Además: Cahn \\& Nadgorny parte 2, cap.\\,5: problemas 5.1 a 5.21.")],
 "Comodín. Repasa los 10 patrones de corrido. Si alguno falla, hoy se arregla."))

SEM.append((
 "Óptica express y primeros simulacros",
 "Óptica en dos sesiones (pesa 0--4\\,\\%) y arranque de simulacros completos.",
 "04\\_ESTUDIO/formularios/optica.md (media página basta) + 2 simulacros registrados.",
 [("Óptica geométrica: Sears Vol.\\,2. Snell, reflexión total interna, lentes delgadas, aumento. Formulario de media página.",
   "Además: Delft \\emph{BSc Optics} cap.\\,2 (p.\\,39), §2.5 óptica gaussiana (p.\\,46)."),
  ("Interferencia y difracción: Young, red de difracción, criterio de Rayleigh, Malus, Brewster. Añade al formulario. 6 problemas.",
   "Además: Irodov §5.2--5.4 (p.\\,210--226), 6 problemas."),
  ("\\textbf{SIMULACRO 1:} GR8677, primera mitad. 85 min cronometrados, condiciones reales.",
   "El examen completo: 170 min seguidos."),
  ("Termina y corrige el SIMULACRO 1. Regístralo con \\texttt{medidor.py simulacro}.",
   "Además: analiza cada fallo con GR8677\\_solutions\\_grephysics.pdf."),
  ("\\textbf{SIMULACRO 2:} REA Test 1 (p.\\,79), primera mitad. 60 min.",
   "Completo, más la corrección con las explicaciones detalladas (p.\\,110).")],
 "Comodín. \\textbf{Aviso:} la inscripción online cierra el miércoles 18 de noviembre a las 5:00 p.m."))

SEM.append((
 "Simulacros finales, trámites y repaso",
 "Nada nuevo. Solo simulacros, corrección de errores y cerrar la inscripción.",
 "Inscripción y documentos entregados. Los 5 formularios repasados.",
 [("\\textbf{SIMULACRO 3:} GR9677, primera mitad. 85 min.",
   "El examen completo: 170 min."),
  ("Corrige el simulacro 3. Repasa los 10 patrones en voz alta, sin mirar.",
   "Además: REA Test 2 (p.\\,153), primera mitad."),
  ("\\textcolor{alerta}{\\textbf{HOY CIERRA LA INSCRIPCIÓN ONLINE, 5:00 p.m. Hazlo antes de estudiar.}} Luego: repaso de errores.md, rehaz los 10 fallos más repetidos.",
   "Además: REA Test 3 (p.\\,233), primera mitad."),
  ("\\textcolor{alerta}{\\textbf{HOY CIERRA LA CARGA DE DOCUMENTOS, 11:30 p.m.}} Luego: repasa los 5 formularios. Nada nuevo.",
   "Además: pasa todas las tarjetas Anki."),
  ("Repaso ligero: los 10 patrones y la tabla de constantes (REA p.\\,76). \\textbf{Máximo 1 hora. No estudies nada nuevo.}",
   "\\textbf{Hoy no hay versión extendida.} Descansa: rinde más que estudiar.")],
 "Descanso. Prepara documento de identidad, lápiz, borrador y reloj. Duerme temprano: el examen es mañana."))



# ---------------------------------------------------------------- mapa skills
AREA_NOM = {"mecanica": "Mecánica", "electromagnetismo": "Electromagnetismo",
            "relatividad": "Relatividad", "termo_estadistica": "Termo y estadística",
            "moderna_cuantica": "Moderna y cuántica", "optica": "Óptica y ondas"}
ORDEN = ["mecanica", "electromagnetismo", "relatividad",
         "termo_estadistica", "moderna_cuantica", "optica"]


def pagina_mapa():
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "06_SEGUIMIENTO", "mapas", "uniandes_2024.csv")
    if not os.path.exists(ruta):
        ruta = "/home/sebastian/Documents/ANDES/06_SEGUIMIENTO/mapas/uniandes_2024.csv"
    filas = []
    with open(ruta, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            filas.append(r)
    filas.sort(key=lambda r: (ORDEN.index(r["area"]) if r["area"] in ORDEN else 9,
                              int(r["pregunta"])))
    L = []
    L.append(r"\seccion{Mapa de habilidades}")
    L.append(r"""Una fila por habilidad evaluada en el examen. Cada semana escribe tu nivel del 0 al 4. Misma escala que
\texttt{medidor.py skills}, para contrastar lo que sientes con lo que miden los simulacros.\\[0.5mm]
\textbf{0} no lo he visto \quad \textbf{1} lo vi, no me sale \quad \textbf{2} lo entiendo si lo miro \quad
\textbf{3} lo resuelvo solo \quad \textbf{4} lo resuelvo rápido\\[1mm]
Las filas en negrita son los \textbf{10 patrones}: son el 40\,\% del examen. Ninguna debería quedar bajo 3 en noviembre.
\par\vspace{2.5mm}""")
    cols = "@{}|p{10.4cm}|" + "c|" * 14
    L.append(r"{\renewcommand{\arraystretch}{1.34}\setlength{\tabcolsep}{5.2pt}")
    L.append(r"\noindent\begin{tabular}{" + cols + "}")
    L.append(r"\hline")
    L.append(r"\rowcolor{cab}\color{white}\textbf{\ Habilidad} & "
             + " & ".join(r"\color{white}\scriptsize\textbf{S%d}" % i for i in range(1, 15))
             + r"\\ \hline")
    area_ant = None
    for r in filas:
        if r["area"] != area_ant:
            area_ant = r["area"]
            L.append(r"\rowcolor{gris}\multicolumn{15}{|l|}{\textbf{\small "
                     + AREA_NOM.get(area_ant, area_ant) + r"}}\\ \hline")
        pat = r["patron"].strip()
        tema = r["tema"].replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")
        et = (r"\textbf{" + pat + " — " + tema + "}") if pat else tema
        L.append(r"\scriptsize " + et + " & " + " & ".join([" "] * 14) + r"\\ \hline")
    L.append(r"\end{tabular}}")
    L.append(r"\newpage")
    return "\n".join(L)


# ---------------------------------------------------------------- generación
out = []
A = out.append

A(r"""\documentclass[10pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[spanish,es-noquoting]{babel}
\usepackage[a4paper,landscape,includehead,top=0.8cm,bottom=0.8cm,left=1.2cm,right=1.2cm,headheight=14pt,headsep=5mm]{geometry}
\usepackage{longtable,array,xcolor,amssymb,amsmath,colortbl,tabularx,enumitem,fancyhdr,titlesec}
\usepackage{lastpage}

\definecolor{cab}{HTML}{1F3864}
\definecolor{gris}{HTML}{EFEFEF}
\definecolor{gris2}{HTML}{F8F8F8}
\definecolor{alerta}{HTML}{B00020}
\definecolor{clave}{HTML}{0B6E4F}
\definecolor{libre}{HTML}{DDDDDD}

\setlength{\parindent}{0pt}
\renewcommand{\arraystretch}{1.28}
\setlength{\tabcolsep}{3pt}

\pagestyle{fancy}\fancyhf{}
\lhead{\small\textbf{Cronograma --- Examen de admisión, Maestría en Física, Uniandes}}
\rhead{\small Examen: lunes 23 de noviembre de 2026 \quad|\quad Página \thepage\ de \pageref{LastPage}}
\renewcommand{\headrulewidth}{0.4pt}

\newcommand{\ch}{$\square$}
\newcommand{\seccion}[1]{\vspace{2mm}{\color{cab}\large\textbf{#1}}\vspace{1mm}\hrule\vspace{2mm}}

\titleformat{\section}{\color{cab}\Large\bfseries}{}{0pt}{}

\begin{document}
""")

# ---- portada / instrucciones
A(r"""
\begin{center}
{\color{cab}\Huge\textbf{Cronograma de estudio}}\\[2mm]
{\Large Examen de admisión --- Maestría en Ciencias, Física --- Universidad de los Andes}\\[3mm]
{\large\textbf{Del lunes 17 de agosto al domingo 22 de noviembre de 2026} \quad ---\quad 14 semanas, S0 a S13}\\[2mm]
{\large\color{alerta}\textbf{Examen: lunes 23 de noviembre de 2026}}
\end{center}

\vspace{1mm}
\small
\begin{minipage}[t]{0.48\textwidth}
\seccion{Cómo usar este documento}
Cada día tiene \textbf{dos versiones de la misma sesión}:
\begin{itemize}[leftmargin=5mm,itemsep=0.5mm]
\item \textbf{MÍNIMA (1 hora).} El piso. Si un día solo puedes esto, el plan sigue en pie.
\item \textbf{EXTENDIDA (2 horas).} La mínima \emph{más} lo que dice esa columna. No es una alternativa: es la mínima ampliada.
\end{itemize}
Marca la casilla \ch{} del día cuando termines. Si hiciste la extendida, marca también la de esa columna.

\seccion{Restricciones aplicadas}
\begin{itemize}[leftmargin=5mm,itemsep=0.5mm]
\item Lunes, martes y miércoles: desde las \textbf{16:00}.
\item Jueves y viernes: desde las \textbf{19:00}.
\item \textbf{Sábados: comodín.} Sin asignación fija; se usan solo si quedó algo pendiente entre semana.
\item \textbf{Domingos: comodín.} No traen material nuevo. Son para recuperar, cerrar el entregable de la semana o descansar. Puedes dejarlos libres sin romper nada.
\item \textbf{Los días 12 de cada mes están libres} (12 de septiembre, 12 de octubre y 12 de noviembre). Si caen entre semana, la tarea de ese día se corre al domingo comodín.
\end{itemize}

\seccion{Presupuesto de horas --- léelo}
Cinco sesiones semanales de 1 a 2 horas dan entre \textbf{5 y 10 horas por semana}, es decir entre 70 y 140 horas en total. Es un presupuesto ajustado para este examen.\\[1mm]
Consecuencia práctica: \textbf{el plan está podado al hueso}. No hay lectura de relleno ni capítulos «por cultura». Si un día tienes que elegir, haz siempre la MÍNIMA completa antes que media EXTENDIDA.\\[1mm]
Si puedes sostener la EXTENDIDA tres o más días por semana, llegas holgado. Si solo alcanzas las mínimas, llegas justo pero llegas.
\end{minipage}
\hfill
\begin{minipage}[t]{0.48\textwidth}
\seccion{Dónde está cada cosa}
Todo cuelga de \texttt{\textasciitilde/Documents/ANDES/}:
\begin{itemize}[leftmargin=5mm,itemsep=0.3mm]
\item \texttt{02\_BIBLIOTECA/} --- los libros, ordenados por área.
\item \texttt{01\_EXAMENES/uniandes\_admision/} --- el simulacro oficial.
\item \texttt{01\_EXAMENES/gre\_physics/} --- 4 exámenes GRE con soluciones, ETS y el REA.
\item \texttt{01\_EXAMENES/banco\_hrw/} --- 2.200 preguntas con respuesta.
\item \texttt{01\_EXAMENES/otros\_bancos/mit\_ocw/} --- problem sets y exámenes del MIT.
\item \texttt{03\_TEMARIO/} --- el desglose detallado de cada semana.
\item \texttt{04\_ESTUDIO/formularios/} --- aquí escribes tus formularios.
\item \texttt{06\_SEGUIMIENTO/} --- el medidor. Lee su \texttt{INSTRUCTIVO.md}.
\end{itemize}

\seccion{Las tres reglas}
\begin{enumerate}[leftmargin=5mm,itemsep=0.8mm]
\item \textbf{El viernes es sagrado.} Siempre opción múltiple cronometrada. Es el único entrenamiento del formato real. Sin esto, sabrás física pero no aprobarás.
\item \textbf{Todo fallo se anota.} Con \texttt{medidor.py error}, o al registrar el simulacro, indicando la causa: concepto, álgebra, lectura, tiempo o descuido. Se rehace a los 3 y a los 14 días.
\item \textbf{Los 10 patrones mandan.} Están marcados en negrita a lo largo del cronograma. Son el 40\,\% del examen y lo que separa a quien entra de quien no.
\end{enumerate}

\seccion{Ritmo objetivo por problema}
\begin{tabular}{@{}ll@{}}
Semanas 1--3 & Resolver bien, sin reloj \\
Semanas 4--9 & Con reloj: 10 min por problema \\
Semanas 10--12 & 7 min por problema \\
Semanas 13--14 & 6 min, en simulacro completo \\
\end{tabular}\\[2mm]
En el examen real tienes \textbf{7,2 minutos por pregunta}: 25 preguntas en 3 horas.
\end{minipage}

\newpage
""")

A(pagina_mapa())

# ---- semanas
lunes = INICIO
# Se numeran S0..S13 igual que PLAN.md y que la app. Antes iban de 1 a 14 y la
# "Semana 1" del PDF era la S0 del plan: al mirar los dos, cada uno decía una
# cosa distinta para el mismo día.
for i, (titulo, objetivo, entregable, dias, dom) in enumerate(SEM, start=0):
    fin = lunes + dt.timedelta(days=6)
    rango = f"{lunes.day} de {MESES[lunes.month-1]} -- {fin.day} de {MESES[fin.month-1]}"
    A(r"\seccion{S%d \quad\textnormal{\normalsize %s}}" % (i, rango))
    A(r"\textbf{Foco:} %s\\[0.5mm]" % titulo)
    A(r"\textbf{Por qué:} %s\\[0.5mm]" % objetivo)
    A(r"\textbf{Entregable de la semana:} %s" % entregable)
    A(r"\par\vspace{2.5mm}")
    A(r"""\noindent\begin{tabular}{@{}p{0.45cm}p{2.5cm}p{1.05cm}|p{0.45cm}p{9.75cm}|p{0.45cm}p{9.75cm}@{}}
\rowcolor{cab}
\multicolumn{3}{@{}l}{\color{white}\textbf{\ Día}} & \multicolumn{2}{l}{\color{white}\textbf{MÍNIMA --- 1 hora}} & \multicolumn{2}{l}{\color{white}\textbf{EXTENDIDA --- 2 horas (la mínima + esto)}}\\""")

    for d in range(5):
        fecha = lunes + dt.timedelta(days=d)
        etiq = f"{DIAS[d]} {fecha.day}"
        if fecha.day == 12:
            A(r"\rowcolor{libre}")
            A(r"\ch & \textbf{%s} & --- & \multicolumn{4}{l@{}}{\textit{\textbf{LIBRE} --- día 12 del mes. La sesión de hoy se corre al domingo comodín.}}\\" % etiq)
        else:
            mn, ex = dias[d]
            bg = r"\rowcolor{gris2}" if d % 2 else ""
            if bg:
                A(bg)
            A(r"\ch & \textbf{%s} & %s & \ch & %s & \ch & %s\\" % (etiq, VENTANA[d], mn, ex))

    sab = lunes + dt.timedelta(days=5)
    A(r"\rowcolor{libre}")
    A(r" & \textbf{Sábado %d} & --- & \multicolumn{4}{l@{}}{\textit{Comodín. Sin asignación fija.}}\\" % sab.day)
    domd = lunes + dt.timedelta(days=6)
    A(r"\rowcolor{gris}")
    A(r"\ch & \textbf{Domingo %d} & libre & \multicolumn{4}{l@{}}{\textit{%s}}\\" % (domd.day, dom))
    A(r"\end{tabular}")
    A(r"""\vspace{2mm}

\noindent\begin{tabular}{@{}p{2.0cm}p{22.8cm}@{}}
\textbf{\small Notas} & \rule{\linewidth}{0.4pt}\\[5mm]
 & \rule{\linewidth}{0.4pt}\\[5mm]
 & \rule{\linewidth}{0.4pt}\\[5mm]
 & \rule{\linewidth}{0.4pt}\\[5mm]
 & \rule{\linewidth}{0.4pt}\\
\end{tabular}""")
    A(r"\newpage")
    lunes = lunes + dt.timedelta(days=7)

# ---- cierre
A(r"""
\begin{center}{\color{alerta}\Huge\textbf{LUNES 23 DE NOVIEMBRE DE 2026 --- EXAMEN}}\\[2mm]
{\large Presencial. Hora y salón se informan el día anterior. 25 preguntas, 3 horas.}\end{center}
\vspace{1mm}
\footnotesize

\begin{minipage}[t]{0.48\textwidth}
\seccion{Los 10 patrones --- lista de verificación}
Si el 22 de noviembre solo alcanzas a repasar diez cosas, son estas. Marca cuando puedas explicarla sin mirar:
\begin{enumerate}[leftmargin=6mm,itemsep=1.2mm]
\item \ch\ $T(E)=dA/dE$ en el espacio de fase
\item \ch\ Corchetes de Poisson: $\{L_i,p_j\}=\varepsilon_{ijk}p_k$
\item \ch\ Scattering esfera dura: $b=R\cos(\theta/2)$
\item \ch\ Condición de gauge de Lorenz y de Coulomb
\item \ch\ Esfera conductora en campo uniforme: $(Ar+B/r^2)\cos\theta$
\item \ch\ $S=k\ln\Omega$ y entropía combinatoria
\item \ch\ Equilibrio térmico maximizando $\Omega_A\Omega_B$
\item \ch\ Bosones vs.\ fermiones en caja: quién comparte estado
\item \ch\ Coeficiente $R$ del escalón de potencial
\item \ch\ Oscilador armónico con $a$, $a^\dagger$ y evolución temporal
\end{enumerate}

\seccion{Las 4 técnicas de descarte}
Con 7,2 min por pregunta, muchas veces descartar es más rápido que resolver:
\begin{enumerate}[leftmargin=6mm,itemsep=0.8mm]
\item \textbf{Dimensional:} ¿las unidades de cada opción cierran?
\item \textbf{Casos límite:} $x\to0$, $x\to\infty$, $m_1=m_2$, sin fricción, $v\ll c$, $T\to0$.
\item \textbf{Signos y simetrías:} ¿el campo apunta a donde debe? ¿la energía crece o decrece?
\item \textbf{Orden de magnitud:} descarta lo que difiere por factores absurdos.
\end{enumerate}
\textbf{Responde las 25.} No hay penalización por error: dejar en blanco solo pierde puntos.
\end{minipage}
\hfill
\begin{minipage}[t]{0.48\textwidth}
\seccion{Fechas administrativas --- no se negocian}
\begin{tabular}{@{}p{3.2cm}p{9cm}@{}}
\textbf{18 de nov, 5:00 p.m.} & \ch\ Cierre de la inscripción online\\
\textbf{19 de nov, 11:30 p.m.} & \ch\ Cierre de carga de documentos\\
\textbf{23 de nov} & \ch\ Examen de admisión\\
\textbf{1--2 de dic} & Entrevistas\\
\textbf{2 de dic} & Publicación de admitidos\\
\end{tabular}
\vspace{2mm}

\textbf{Documentos (PDF, máximo 1 MB cada uno):}
\begin{itemize}[leftmargin=6mm,itemsep=0.4mm]
\item \ch\ Diploma y/o acta de grado, con firma digital validable en línea
\item \ch\ Certificado oficial de calificaciones de pregrado
\item \ch\ Hoja de vida
\item \ch\ Carta de intención (máx.\ 1000 palabras; debe nombrar grupos de investigación)
\item \ch\ Dos referencias académicas, desde correos institucionales
\item \ch\ Carta de solicitud de apoyo financiero (opcional)
\end{itemize}
\textbf{Tenlos listos antes del 31 de octubre.} Las referencias dependen de terceros: pídelas en la semana 9.
\vspace{2mm}

\seccion{Entregables por semana}
\begin{tabular}{@{}p{1.3cm}p{11cm}@{}}
S1 & \ch\ Diagnóstico corregido y registrado\\
S2 & \ch\ Formulario mecánica I\\
S3 & \ch\ Formulario mecánica II\\
S4 & \ch\ Formulario mecánica analítica + patrones 1--3\\
S5 & \ch\ Formulario electrostática\\
S6 & \ch\ Formulario magnetostática e inducción\\
S7 & \ch\ Formulario Maxwell/ondas + patrones 4--5\\
S8 & \ch\ Formulario relatividad + corte de control\\
S9 & \ch\ Formulario termodinámica + cartas pedidas\\
S10 & \ch\ Formulario estadística + patrones 6--8\\
S11 & \ch\ Formulario moderna + patrón 9 + carta de intención\\
S12 & \ch\ Formulario cuántica + patrón 10\\
S13 & \ch\ Formulario óptica + simulacros 1 y 2\\
S14 & \ch\ Simulacros 3 y 4 + inscripción cerrada\\
\end{tabular}
\end{minipage}

\end{document}
""")

with open("cronograma.tex", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("cronograma.tex generado:", sum(len(x) for x in out), "caracteres")
