#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
medidor.py — Seguimiento de preparación para el examen de admisión
             Maestría en Ciencias-Física, Universidad de los Andes.

Sin dependencias externas: solo la librería estándar. Las gráficas se
escriben como SVG a mano, así que esto funciona con cualquier Python 3.8+
y no se rompe cuando cambie el sistema.

Uso:
    python3 medidor.py sesion       registrar una sesión de estudio
    python3 medidor.py simulacro    registrar y calificar un simulacro
    python3 medidor.py error        registrar un problema fallado
    python3 medidor.py skills       autoevaluar el mapa de habilidades
    python3 medidor.py estado       resumen rápido en la terminal
    python3 medidor.py reporte      generar gráficas + REPORTE.md + tablero.html

Lee el INSTRUCTIVO.md que está al lado antes de empezar.
"""
import csv
import os
import sys
import datetime as dt
from collections import defaultdict, Counter

BASE = os.path.dirname(os.path.abspath(__file__))
DATOS = os.path.join(BASE, "datos")
MAPAS = os.path.join(BASE, "mapas")
CLAVES = os.path.join(BASE, "claves")
GRAF = os.path.join(BASE, "graficas")

EXAMEN = dt.date(2026, 11, 23)
META = 72.0   # % de acierto objetivo

AREAS = ["mecanica", "electromagnetismo", "relatividad",
         "termo_estadistica", "moderna_cuantica", "optica", "otros"]
AREA_NOM = {
    "mecanica": "Mecánica",
    "electromagnetismo": "Electromagnetismo",
    "relatividad": "Relatividad",
    "termo_estadistica": "Termo y estadística",
    "moderna_cuantica": "Moderna y cuántica",
    "optica": "Óptica y ondas",
    "otros": "Otros",
}
# Peso de cada área en el examen real, estimado del simulacro oficial 2024
PESO = {"mecanica": 33, "electromagnetismo": 25, "relatividad": 8,
        "termo_estadistica": 21, "moderna_cuantica": 13, "optica": 0, "otros": 0}

CAUSAS = ["concepto", "algebra", "lectura", "tiempo", "descuido"]
CAUSA_NOM = {
    "concepto": "No sabía la física",
    "algebra": "Error de cuentas",
    "lectura": "Entendí mal el enunciado",
    "tiempo": "Sabía hacerlo, no alcancé",
    "descuido": "Descuido / marqué mal",
}

PALETA = ["#1F3864", "#0B6E4F", "#C2571A", "#6B3FA0", "#B00020", "#00707A", "#7A7A7A"]

ESQUEMAS = {
    "sesiones": ["fecha", "semana", "area", "tipo", "minutos", "version",
                 "energia", "claridad", "notas"],
    "simulacros": ["id", "fecha", "examen", "n_preguntas", "minutos",
                   "aciertos", "pct", "animo", "confianza_previa", "notas"],
    "respuestas": ["simulacro_id", "pregunta", "marcada", "correcta", "ok",
                   "area", "nivel", "tema", "patron", "p_mas", "causa"],
    "errores": ["fecha", "area", "tema", "fuente", "problema", "causa",
                "nivel", "repaso3", "repaso14"],
    "habilidades": ["fecha", "skill", "nivel"],
}

# Escala del mapa de habilidades
NIVELES = {0: "no lo he visto", 1: "lo vi, no me sale",
           2: "lo entiendo si lo miro", 3: "lo resuelvo solo",
           4: "lo resuelvo rápido"}


# ---------------------------------------------------------------- utilidades
def ruta(tabla):
    return os.path.join(DATOS, tabla + ".csv")


def asegurar():
    for d in (DATOS, MAPAS, CLAVES, GRAF):
        os.makedirs(d, exist_ok=True)
    for tabla, cols in ESQUEMAS.items():
        p = ruta(tabla)
        if not os.path.exists(p):
            with open(p, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(cols)


def leer(tabla):
    p = ruta(tabla)
    if not os.path.exists(p):
        return []
    with open(p, newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f)]


def agregar(tabla, fila):
    with open(ruta(tabla), "a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=ESQUEMAS[tabla]).writerow(fila)


def num(x, d=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d


def preguntar(txt, defecto=None, opciones=None):
    suf = ""
    if opciones:
        suf = " [" + "/".join(opciones) + "]"
    if defecto is not None:
        suf += f" ({defecto})"
    while True:
        r = input(f"  {txt}{suf}: ").strip()
        if not r and defecto is not None:
            return defecto
        if not r:
            continue
        if opciones and r not in opciones:
            print(f"    -> debe ser uno de: {', '.join(opciones)}")
            continue
        return r


def escala(txt, defecto=3):
    while True:
        r = input(f"  {txt} [1-5] ({defecto}): ").strip()
        if not r:
            return defecto
        if r in "12345" and len(r) == 1:
            return int(r)
        print("    -> un número del 1 al 5")


def dias_restantes():
    return (EXAMEN - dt.date.today()).days


def semana_actual():
    inicio = dt.date(2026, 8, 17)
    d = (dt.date.today() - inicio).days
    return max(1, min(14, d // 7 + 1))


# ---------------------------------------------------------------- SVG
def _esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


class Lienzo:
    """Constructor mínimo de SVG."""

    def __init__(self, w=760, h=380, titulo=""):
        self.w, self.h, self.titulo = w, h, titulo
        self.p = []
        self.ml, self.mr, self.mt, self.mb = 130, 30, 46, 58

    @property
    def x0(self): return self.ml

    @property
    def y0(self): return self.h - self.mb

    @property
    def aw(self): return self.w - self.ml - self.mr

    @property
    def ah(self): return self.h - self.mt - self.mb

    def linea(self, x1, y1, x2, y2, c="#CCC", w=1, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.p.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                      f'stroke="{c}" stroke-width="{w}"{d}/>')

    def rect(self, x, y, w, h, c, op=1.0):
        if w <= 0 or h <= 0:
            return
        self.p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
                      f'fill="{c}" fill-opacity="{op}" rx="2"/>')

    def texto2(self, x, y, l1, l2, size=9, c="#777", anchor="middle"):
        self.p.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{c}" '
                      f'text-anchor="{anchor}" font-family="DejaVu Sans, Helvetica, Arial, sans-serif">'
                      f'<tspan x="{x:.1f}" dy="0">{_esc(l1)}</tspan>'
                      f'<tspan x="{x:.1f}" dy="12">{_esc(l2)}</tspan></text>')

    def texto(self, x, y, t, size=11, c="#333", anchor="start", peso="normal"):
        self.p.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{c}" '
                      f'text-anchor="{anchor}" font-weight="{peso}" '
                      f'font-family="DejaVu Sans, Helvetica, Arial, sans-serif">{_esc(t)}</text>')

    def poli(self, pts, c, w=2.4):
        s = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.p.append(f'<polyline points="{s}" fill="none" stroke="{c}" stroke-width="{w}" '
                      f'stroke-linejoin="round" stroke-linecap="round"/>')

    def punto(self, x, y, c, r=3.6):
        self.p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{c}" '
                      f'stroke="#FFF" stroke-width="1.2"/>')

    def render(self):
        cab = (f'<text x="{self.w/2}" y="24" font-size="14" font-weight="bold" fill="#1F3864" '
               f'text-anchor="middle" font-family="DejaVu Sans, Helvetica, Arial, sans-serif">'
               f'{_esc(self.titulo)}</text>')
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}"><rect width="{self.w}" height="{self.h}" fill="#FFF"/>'
                + cab + "".join(self.p) + "</svg>")

    def guardar(self, nombre):
        p = os.path.join(GRAF, nombre)
        with open(p, "w", encoding="utf-8") as f:
            f.write(self.render())
        return p

    # -- ejes porcentuales 0-100
    def eje_pct(self, meta=None):
        for v in range(0, 101, 20):
            y = self.y0 - self.ah * v / 100.0
            self.linea(self.x0, y, self.x0 + self.aw, y, "#EEE")
            self.texto(self.x0 - 8, y + 4, f"{v}%", 10, "#888", "end")
        if meta is not None:
            y = self.y0 - self.ah * meta / 100.0
            self.linea(self.x0, y, self.x0 + self.aw, y, "#B00020", 1.4, "5,4")
            self.texto(self.x0 + self.aw, y - 5, f"meta {meta:.0f}%", 10, "#B00020", "end")
        self.linea(self.x0, self.y0, self.x0 + self.aw, self.y0, "#999", 1.4)


def grafica_barras_h(titulo, filas, meta=None, archivo="barras.svg", nota=""):
    """filas: [(etiqueta, valor_pct, subtexto, color)]"""
    h = max(220, 78 + 34 * len(filas))
    c = Lienzo(820, h, titulo)
    c.mt, c.mb, c.ml = 46, 40, 200
    if not filas:
        c.texto(c.w / 2, h / 2, "sin datos todavía", 12, "#999", "middle")
        return c.guardar(archivo)
    aw = c.w - c.ml - c.mr
    for i in range(0, 101, 25):
        x = c.ml + aw * i / 100.0
        c.linea(x, c.mt - 6, x, h - c.mb + 4, "#EEE")
        c.texto(x, h - c.mb + 18, f"{i}%", 10, "#999", "middle")
    if meta is not None:
        x = c.ml + aw * meta / 100.0
        c.linea(x, c.mt - 6, x, h - c.mb + 4, "#B00020", 1.4, "5,4")
    for i, (et, val, sub, col) in enumerate(filas):
        y = c.mt + 6 + i * 34
        c.texto(c.ml - 10, y + 15, et, 11, "#333", "end", "bold")
        c.rect(c.ml, y, aw, 22, "#F2F2F2")
        c.rect(c.ml, y, aw * max(0.0, min(100.0, val)) / 100.0, 22, col)
        c.texto(c.ml + aw * min(100.0, val) / 100.0 + 7, y + 15, sub, 10, "#555")
    if nota:
        c.texto(c.ml, h - 8, nota, 10, "#888")
    return c.guardar(archivo)


def grafica_lineas(titulo, xlabels, series, meta=None, archivo="lineas.svg"):
    """series: [(nombre, [valores o None], color)]"""
    c = Lienzo(820, 410, titulo)
    c.mb = 86
    if not xlabels:
        c.texto(c.w / 2, 200, "sin datos todavía", 12, "#999", "middle")
        return c.guardar(archivo)
    c.eje_pct(meta)
    n = len(xlabels)
    paso = c.aw / max(1, n - 1) if n > 1 else 0
    for i, xl in enumerate(xlabels):
        x = c.x0 + paso * i if n > 1 else c.x0 + c.aw / 2
        partes = str(xl).split("\n")
        c.texto2(x, c.y0 + 16, partes[0], partes[1] if len(partes) > 1 else "")
    for k, (nom, vals, col) in enumerate(series):
        pts = []
        for i, v in enumerate(vals):
            if v is None:
                continue
            x = c.x0 + paso * i if n > 1 else c.x0 + c.aw / 2
            y = c.y0 - c.ah * v / 100.0
            pts.append((x, y))
        if len(pts) > 1:
            c.poli(pts, col)
        for x, y in pts:
            c.punto(x, y, col)
        ly = c.h - 40 + (k // 3) * 15
        lx = 24 + (k % 3) * 262
        c.rect(lx, ly - 8, 18, 4, col)
        c.texto(lx + 24, ly - 3, nom, 10, "#444")
    return c.guardar(archivo)


def grafica_apiladas(titulo, categorias, series, archivo="apiladas.svg"):
    """series: [(nombre, {categoria: cantidad}, color)] — barras verticales apiladas."""
    c = Lienzo(820, 380, titulo)
    c.ml, c.mb = 55, 84
    if not categorias:
        c.texto(c.w / 2, 190, "sin datos todavía", 12, "#999", "middle")
        return c.guardar(archivo)
    tot = {k: sum(s[1].get(k, 0) for s in series) for k in categorias}
    mx = max(list(tot.values()) + [1])
    for i in range(0, 6):
        v = mx * i / 5.0
        y = c.y0 - c.ah * i / 5.0
        c.linea(c.x0, y, c.x0 + c.aw, y, "#EEE")
        c.texto(c.x0 - 8, y + 4, f"{v:.0f}", 10, "#888", "end")
    c.linea(c.x0, c.y0, c.x0 + c.aw, c.y0, "#999", 1.4)
    bw = c.aw / len(categorias)
    for i, cat in enumerate(categorias):
        x = c.x0 + bw * i + bw * 0.18
        w = bw * 0.64
        acc = 0.0
        for nom, d, col in series:
            v = d.get(cat, 0)
            if v <= 0:
                continue
            hh = c.ah * v / mx
            c.rect(x, c.y0 - c.ah * acc / mx - hh, w, hh, col)
            acc += v
        et = cat if len(cat) <= 14 else cat[:13] + "."
        c.texto(x + w / 2, c.y0 + 15, et, 9, "#666", "middle")
    for k, (nom, d, col) in enumerate(series):
        ly = c.h - 44 + (k // 3) * 15
        lx = 24 + (k % 3) * 262
        c.rect(lx, ly - 8, 18, 8, col)
        c.texto(lx + 24, ly - 1, nom, 10, "#444")
    return c.guardar(archivo)


# ---------------------------------------------------------------- carga mapas
def cargar_mapa(nombre):
    """Devuelve {pregunta:int -> dict} desde claves/ o mapas/."""
    for carpeta in (CLAVES, MAPAS):
        p = os.path.join(carpeta, nombre + ".csv")
        if os.path.exists(p):
            out = {}
            with open(p, newline="", encoding="utf-8") as f:
                for r in csv.DictReader(f):
                    try:
                        out[int(r["pregunta"])] = r
                    except (KeyError, ValueError):
                        pass
            return out
    return {}


def examenes_disponibles():
    v = set()
    for carpeta in (CLAVES, MAPAS):
        if os.path.isdir(carpeta):
            for f in os.listdir(carpeta):
                if f.endswith(".csv"):
                    v.add(f[:-4])
    return sorted(v)


# ---------------------------------------------------------------- comandos
def cmd_sesion():
    asegurar()
    mapa_terminal()
    print("== Registrar sesión de estudio ==")
    hoy = dt.date.today().isoformat()
    fila = {
        "fecha": preguntar("Fecha", hoy),
        "semana": preguntar("Semana del cronograma", str(semana_actual())),
        "area": preguntar("Área", "mecanica", AREAS),
        "tipo": preguntar("Tipo", "problemas",
                          ["teoria", "problemas", "mc", "repaso", "simulacro"]),
        "minutos": preguntar("Minutos efectivos", "60"),
        "version": preguntar("Versión", "minima", ["minima", "extendida"]),
        "energia": escala("Energía con la que llegaste"),
        "claridad": escala("Qué tan claro te quedó el tema"),
        "notas": input("  Nota libre (qué costó, qué no entendiste): ").strip(),
    }
    agregar("sesiones", fila)
    print("  -> guardado.\n")


def cmd_simulacro():
    asegurar()
    print("\n== Registrar simulacro ==")
    disp = examenes_disponibles()
    if not disp:
        print("  No hay claves. Crea una en claves/ (ver INSTRUCTIVO.md).")
        return
    print("  Exámenes con clave o mapa disponibles:")
    for d in disp:
        print(f"    - {d}")
    ex = preguntar("¿Cuál?", disp[0], disp)
    mapa = cargar_mapa(ex)
    if not mapa:
        print("  No pude leer ese archivo.")
        return
    tiene_clave = any(m.get("correcta") for m in mapa.values())
    qs = sorted(mapa)
    print(f"\n  {len(qs)} preguntas. "
          + ("Escribe tus respuestas." if tiene_clave
             else "Este examen NO tiene clave cargada: te preguntaré si acertaste."))
    print("  Enter en blanco = dejaste la pregunta sin responder.\n")

    conf = escala("Antes de ver el resultado: ¿qué tan bien crees que te fue?")
    animo = escala("¿Cómo te sentiste durante el examen?")
    minutos = preguntar("Minutos que tardaste", "180")

    sid = str(int(dt.datetime.now().timestamp()))
    respuestas, aciertos = [], 0
    for q in qs:
        m = mapa[q]
        if tiene_clave:
            marcada = input(f"    Q{q:>3} -> ").strip().upper()
            correcta = (m.get("correcta") or "").strip().upper()
            ok = 1 if (marcada and marcada == correcta) else 0
        else:
            marcada = ""
            correcta = ""
            r = input(f"    Q{q:>3} ¿acertaste? [s/n] -> ").strip().lower()
            ok = 1 if r.startswith("s") else 0
        aciertos += ok
        respuestas.append({
            "simulacro_id": sid, "pregunta": q, "marcada": marcada,
            "correcta": correcta, "ok": ok,
            "area": m.get("area", "otros"), "nivel": m.get("nivel", ""),
            "tema": m.get("tema", ""), "patron": m.get("patron", ""),
            "p_mas": m.get("p_mas", ""), "causa": "",
        })

    print("\n  -- Ahora lo importante: por qué fallaste --")
    print("     concepto = no sabía | algebra = cuentas | lectura = leí mal")
    print("     tiempo = sabía pero no alcancé | descuido = marqué mal\n")
    for r in respuestas:
        if r["ok"]:
            continue
        t = r["tema"] or "(sin tema)"
        print(f"    Q{r['pregunta']}: {t[:66]}")
        r["causa"] = preguntar("      causa", "concepto", CAUSAS)

    with open(ruta("respuestas"), "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ESQUEMAS["respuestas"])
        for r in respuestas:
            w.writerow(r)

    pct = 100.0 * aciertos / max(1, len(qs))
    agregar("simulacros", {
        "id": sid, "fecha": dt.date.today().isoformat(), "examen": ex,
        "n_preguntas": len(qs), "minutos": minutos, "aciertos": aciertos,
        "pct": f"{pct:.1f}", "animo": animo, "confianza_previa": conf,
        "notas": input("\n  Nota libre sobre el simulacro: ").strip(),
    })
    print(f"\n  -> {aciertos}/{len(qs)} = {pct:.1f}%")
    esperado = (conf - 1) * 25
    if pct < esperado - 12:
        print(f"  OJO: esperabas ~{esperado:.0f}% y sacaste {pct:.0f}%. Te estás sobreestimando.")
    elif pct > esperado + 12:
        print(f"  Esperabas ~{esperado:.0f}% y sacaste {pct:.0f}%. Te subestimas: confía más.")
    print("  Corre 'python3 medidor.py reporte' para ver el análisis.\n")


def cmd_error():
    asegurar()
    print("\n== Registrar problema fallado ==")
    fila = {
        "fecha": preguntar("Fecha", dt.date.today().isoformat()),
        "area": preguntar("Área", "mecanica", AREAS),
        "tema": preguntar("Tema (concreto)", "—"),
        "fuente": preguntar("Fuente (libro/banco)", "—"),
        "problema": preguntar("Número o identificador", "—"),
        "causa": preguntar("Causa", "concepto", CAUSAS),
        "nivel": preguntar("Nivel", "BASE", ["BASE", "ALTO"]),
        "repaso3": "", "repaso14": "",
    }
    agregar("errores", fila)
    print("  -> guardado. Reháztelo en 3 y en 14 días.\n")


# ---------------------------------------------------------------- análisis
def analizar():
    sims = leer("simulacros")
    resp = leer("respuestas")
    ses = leer("sesiones")
    errs = leer("errores")

    por_area = defaultdict(lambda: [0, 0])       # area -> [ok, total]
    por_nivel = defaultdict(lambda: [0, 0])
    causas_area = defaultdict(Counter)
    causas = Counter()
    patrones = defaultdict(lambda: [0, 0])
    baratos = []                                  # fallos en preguntas fáciles
    for r in resp:
        a = r.get("area") or "otros"
        ok = int(num(r.get("ok")))
        por_area[a][0] += ok
        por_area[a][1] += 1
        nv = (r.get("nivel") or "").upper()
        if nv in ("BASE", "ALTO"):
            por_nivel[nv][0] += ok
            por_nivel[nv][1] += 1
        p = (r.get("patron") or "").strip()
        if p:
            patrones[p][0] += ok
            patrones[p][1] += 1
        if not ok:
            cz = r.get("causa") or "sin_clasificar"
            causas[cz] += 1
            causas_area[a][cz] += 1
            pm = num(r.get("p_mas"), -1)
            if pm >= 60:
                baratos.append((r.get("tema") or f"Q{r.get('pregunta')}", pm, a))

    # evolución por simulacro
    sims_ord = sorted(sims, key=lambda s: (s.get("fecha", ""), s.get("id", "")))
    evol_x, evol = [], defaultdict(list)
    for s in sims_ord:
        evol_x.append(s.get("fecha", "")[5:] + "\n" + (s.get("examen", "")[:12]))
        rs = [r for r in resp if r.get("simulacro_id") == s.get("id")]
        for a in AREAS:
            sub = [r for r in rs if (r.get("area") or "otros") == a]
            evol[a].append(100.0 * sum(int(num(r["ok"])) for r in sub) / len(sub) if sub else None)

    # horas y ánimo por semana
    horas, energia, claridad = defaultdict(float), defaultdict(list), defaultdict(list)
    for s in ses:
        w = s.get("semana", "?")
        horas[w] += num(s.get("minutos")) / 60.0
        if s.get("energia"):
            energia[w].append(num(s["energia"]))
        if s.get("claridad"):
            claridad[w].append(num(s["claridad"]))

    # calibración
    calib = []
    for s in sims_ord:
        c = num(s.get("confianza_previa"), 0)
        if c:
            calib.append(((c - 1) * 25.0, num(s.get("pct"))))

    return dict(sims=sims_ord, resp=resp, ses=ses, errs=errs,
                por_area=por_area, por_nivel=por_nivel, causas=causas,
                causas_area=causas_area, patrones=patrones, baratos=baratos,
                evol_x=evol_x, evol=evol, horas=horas, energia=energia,
                claridad=claridad, calib=calib)


def color_pct(p):
    if p >= META:
        return "#0B6E4F"
    if p >= 55:
        return "#C2571A"
    return "#B00020"


def generar_graficas(A):
    hechas = []
    m = mapa_habilidades_svg()
    if m:
        hechas.append(m)
    # 1. acierto por área
    filas = []
    for a in AREAS:
        ok, tot = A["por_area"].get(a, [0, 0])
        if not tot:
            continue
        p = 100.0 * ok / tot
        filas.append((f"{AREA_NOM[a]} ({PESO[a]}%)", p, f"{ok}/{tot} = {p:.0f}%", color_pct(p)))
    hechas.append(grafica_barras_h(
        "Acierto por área — el número entre paréntesis es su peso en el examen",
        filas, META, "01_areas.svg",
        "Rojo: bajo 55%. Naranja: entre 55% y la meta. Verde: en meta."))

    # 2. BASE vs ALTO
    filas = []
    for nv, et in (("BASE", "BASE — Física 1-2"), ("ALTO", "ALTO — patrones")):
        ok, tot = A["por_nivel"].get(nv, [0, 0])
        if tot:
            p = 100.0 * ok / tot
            filas.append((et, p, f"{ok}/{tot} = {p:.0f}%", color_pct(p)))
    hechas.append(grafica_barras_h(
        "Base contra patrones — dónde estás perdiendo puntos",
        filas, META, "02_nivel.svg",
        "Si BASE va bajo, no sirve estudiar patrones. Si ALTO va bajo, es donde se decide el examen."))

    # 3. evolución
    series = []
    for i, a in enumerate(AREAS):
        vals = A["evol"].get(a, [])
        if any(v is not None for v in vals):
            series.append((AREA_NOM[a], vals, PALETA[i % len(PALETA)]))
    hechas.append(grafica_lineas("Evolución del acierto por área",
                                 A["evol_x"], series, META, "03_evolucion.svg"))

    # 4. causas de error por área
    cats = [AREA_NOM[a] for a in AREAS if A["causas_area"].get(a)]
    series = []
    for i, cz in enumerate(CAUSAS + ["sin_clasificar"]):
        d = {AREA_NOM[a]: A["causas_area"][a].get(cz, 0)
             for a in AREAS if A["causas_area"].get(a)}
        if sum(d.values()):
            series.append((CAUSA_NOM.get(cz, cz), d, PALETA[i % len(PALETA)]))
    hechas.append(grafica_apiladas("Por qué fallaste, por área", cats, series, "04_causas.svg"))

    # 5. horas por semana
    sem = sorted(A["horas"], key=lambda x: int(x) if str(x).isdigit() else 99)
    filas = []
    for w in sem:
        h = A["horas"][w]
        e = sum(A["energia"][w]) / len(A["energia"][w]) if A["energia"][w] else 0
        col = "#0B6E4F" if h >= 8 else ("#C2571A" if h >= 5 else "#B00020")
        filas.append((f"Semana {w}", min(100.0, h / 12.0 * 100),
                      f"{h:.1f} h · energía {e:.1f}/5", col))
    hechas.append(grafica_barras_h("Horas efectivas por semana (barra llena = 12 h)",
                                   filas, 10 / 12.0 * 100, "05_horas.svg",
                                   "Objetivo: 5-10 h/semana. Verde a partir de 8 h."))

    # 6. calibración
    filas = []
    for i, (esp, real) in enumerate(A["calib"], 1):
        d = real - esp
        col = "#0B6E4F" if abs(d) <= 10 else ("#C2571A" if d > 0 else "#B00020")
        filas.append((f"Simulacro {i}", max(0.0, real),
                      f"creías {esp:.0f}% · sacaste {real:.0f}% ({d:+.0f})", col))
    hechas.append(grafica_barras_h("Calibración: lo que creías contra lo que sacaste",
                                   filas, META, "06_calibracion.svg",
                                   "Rojo: te sobreestimas. Es el sesgo más peligroso en un examen cronometrado."))
    return hechas


def recomendaciones(A):
    R = []
    # áreas críticas, ponderadas por peso
    debiles = []
    for a in AREAS:
        ok, tot = A["por_area"].get(a, [0, 0])
        if tot >= 3:
            p = 100.0 * ok / tot
            if p < META:
                debiles.append((PESO[a] * (META - p), a, p))
    debiles.sort(reverse=True)
    if debiles:
        _, a, p = debiles[0]
        R.append(f"**Tu mayor bolsa de puntos es {AREA_NOM[a]}**: va en {p:.0f}% y pesa "
                 f"{PESO[a]}% del examen. Súmale las sesiones del domingo comodín hasta que suba.")
        if len(debiles) > 1:
            resto = ", ".join(f"{AREA_NOM[x[1]]} ({x[2]:.0f}%)" for x in debiles[1:3])
            R.append(f"Después de esa, en orden de rentabilidad: {resto}.")

    base = A["por_nivel"].get("BASE", [0, 0])
    alto = A["por_nivel"].get("ALTO", [0, 0])
    if base[1] and alto[1]:
        pb = 100.0 * base[0] / base[1]
        pa = 100.0 * alto[0] / alto[1]
        if pb < 70:
            R.append(f"**La base está floja ({pb:.0f}%).** No sigas puliendo patrones: "
                     f"el 55% del examen es Física 1-2 y ahí se aprueba. "
                     f"Prioriza Sears y el banco HRW sobre Tong y Griffiths.")
        elif pa < pb - 15:
            R.append(f"**La base está bien ({pb:.0f}%) pero los patrones no ({pa:.0f}%).** "
                     f"Ese es exactamente el 40% que decide el examen. "
                     f"Reserva las próximas 3 sesiones a los 10 patrones, no a más problemas de rutina.")
        elif pb >= META and pa >= META:
            R.append("Base y patrones en meta. Ahora el margen está en **velocidad**: "
                     "baja el cronómetro a 6 min por pregunta y entrena descarte.")

    if A["causas"]:
        cz, n = A["causas"].most_common(1)[0]
        tot = sum(A["causas"].values())
        if cz == "tiempo" and n / tot > 0.3:
            R.append("**Tu problema principal no es saber, es el reloj.** "
                     "Entrena las 4 técnicas de descarte cada viernes y practica saltarte "
                     "preguntas caras en la primera pasada.")
        elif cz == "algebra" and n / tot > 0.3:
            R.append("**Sabes la física y pierdes por cuentas.** "
                     "Antes de calcular, escribe el resultado simbólico y verifica dimensiones; "
                     "muchas opciones se descartan sin llegar al número.")
        elif cz == "lectura" and n / tot > 0.25:
            R.append("**Estás leyendo mal los enunciados.** "
                     "Subraya qué te piden exactamente antes de resolver: en este examen "
                     "las cinco opciones suelen incluir el resultado de la pregunta que NO te hicieron.")
        elif cz == "concepto" and n / tot > 0.5:
            R.append("**Predomina el vacío conceptual.** Es la buena noticia: "
                     "se arregla estudiando, no con trucos. Sigue el cronograma sin saltarte teoría.")

    if A["baratos"]:
        c = Counter(a for _, _, a in A["baratos"])
        area, n = c.most_common(1)[0]
        R.append(f"Fallaste **{len(A['baratos'])} preguntas que la mayoría acierta** "
                 f"(P+ ≥ 60), sobre todo en {AREA_NOM.get(area, area)}. "
                 f"Son los puntos más baratos de recuperar: revísalas antes que cualquier tema nuevo.")

    pend = sorted([p for p, (ok, tot) in A["patrones"].items() if tot and ok < tot],
                  key=lambda z: int(z[1:]) if z[1:].isdigit() else 99)
    if pend:
        R.append(f"Patrones aún fallados: **{', '.join(pend)}**. "
                 f"Están en `03_TEMARIO/00_mapa_simulacro.md`. "
                 f"Cada uno vale ~4% del examen y se estudia en una sesión.")

    if A["calib"]:
        gaps = [real - esp for esp, real in A["calib"]]
        g = sum(gaps) / len(gaps)
        if g < -12:
            R.append(f"**Te sobreestimas en {abs(g):.0f} puntos en promedio.** "
                     f"Peligroso: te va a hacer saltarte repasos que sí necesitas. "
                     f"Confía en las métricas, no en la sensación.")
        elif g > 12:
            R.append(f"**Te subestimas en {g:.0f} puntos.** "
                     f"Estás mejor de lo que crees; no gastes sesiones repasando lo que ya dominas.")

    h = sum(A["horas"].values())
    ns = len({s.get("semana") for s in A["ses"]})
    if ns >= 2:
        prom = h / ns
        if prom < 5:
            R.append(f"Vas a **{prom:.1f} h/semana**, por debajo del piso de 5 h. "
                     f"Con este ritmo no alcanzan las 14 semanas: o subes horas, "
                     f"o recortamos el temario a las áreas de mayor peso.")
    if not R:
        R.append("Todavía no hay datos suficientes. Registra el diagnóstico y unas cuantas sesiones.")
    return R


def cmd_reporte():
    asegurar()
    A = analizar()
    svgs = generar_graficas(A)
    R = recomendaciones(A)
    hoy = dt.date.today()
    dias = dias_restantes()
    total_ok = sum(v[0] for v in A["por_area"].values())
    total_n = sum(v[1] for v in A["por_area"].values())
    glob = 100.0 * total_ok / total_n if total_n else 0.0

    L = []
    L.append("# Reporte de seguimiento\n")
    L.append(f"*Generado el {hoy.isoformat()} — faltan **{dias} días** para el examen "
             f"(23 de noviembre de 2026). Semana {semana_actual()} de 14.*\n")
    L.append("> **Para Claude:** este archivo es el estado actual de la preparación. "
             "Léelo al inicio de la sesión para saber dónde está Sebastián sin volver a preguntar. "
             "Se regenera con `python3 06_SEGUIMIENTO/medidor.py reporte`.\n")
    L.append("---\n")
    L.append("## Resumen\n")
    L.append(f"- Simulacros registrados: **{len(A['sims'])}**")
    L.append(f"- Preguntas respondidas: **{total_n}** — acierto global **{glob:.1f}%** (meta {META:.0f}%)")
    L.append(f"- Sesiones registradas: **{len(A['ses'])}** — "
             f"**{sum(A['horas'].values()):.1f} h** en total")
    L.append(f"- Errores en bitácora: **{len(A['errs'])}**\n")

    L.append("## Acierto por área\n")
    L.append("| Área | Peso | Aciertos | % | Estado |")
    L.append("|---|---|---|---|---|")
    for a in AREAS:
        ok, tot = A["por_area"].get(a, [0, 0])
        if not tot:
            continue
        p = 100.0 * ok / tot
        est = "en meta" if p >= META else ("hay que reforzar" if p >= 55 else "crítico")
        L.append(f"| {AREA_NOM[a]} | {PESO[a]}% | {ok}/{tot} | {p:.0f}% | {est} |")
    L.append("")

    if A["por_nivel"]:
        L.append("## Base contra patrones\n")
        L.append("| Nivel | Aciertos | % | Qué significa |")
        L.append("|---|---|---|---|")
        for nv, sig in (("BASE", "Física 1-2. Es el 55% del examen: aquí se aprueba."),
                        ("ALTO", "Los 10 patrones. Es el 40%: aquí se decide.")):
            ok, tot = A["por_nivel"].get(nv, [0, 0])
            if tot:
                L.append(f"| {nv} | {ok}/{tot} | {100.0*ok/tot:.0f}% | {sig} |")
        L.append("")

    if A["patrones"]:
        L.append("## Los 10 patrones\n")
        L.append("| Patrón | Intentos | Aciertos | Estado |")
        L.append("|---|---|---|---|")
        for p in sorted(A["patrones"], key=lambda z: int(z[1:]) if z[1:].isdigit() else 99):
            ok, tot = A["patrones"][p]
            L.append(f"| {p} | {tot} | {ok} | {'dominado' if ok == tot else 'PENDIENTE'} |")
        L.append("")

    if A["causas"]:
        L.append("## Por qué fallas\n")
        tot = sum(A["causas"].values())
        L.append("| Causa | Veces | % |")
        L.append("|---|---|---|")
        for cz, n in A["causas"].most_common():
            L.append(f"| {CAUSA_NOM.get(cz, cz)} | {n} | {100.0*n/tot:.0f}% |")
        L.append("")

    if A["baratos"]:
        L.append("## Puntos baratos que estás regalando\n")
        L.append("Preguntas que la mayoría de examinados acierta y tú fallaste. "
                 "Recuperarlas cuesta menos que aprender un tema nuevo.\n")
        L.append("| Tema | La acierta el | Área |")
        L.append("|---|---|---|")
        for t, pm, a in sorted(A["baratos"], key=lambda x: -x[1])[:12]:
            L.append(f"| {t[:70]} | {pm:.0f}% | {AREA_NOM.get(a, a)} |")
        L.append("")

    L.append("## Qué cambiar en el cronograma\n")
    for r in R:
        L.append(f"- {r}")
    L.append("")

    L.append("## Gráficas\n")
    for s in svgs:
        n = os.path.basename(s)
        L.append(f"![{n}](graficas/{n})")
    L.append("\n*Ábrelas todas juntas en `tablero.html`.*\n")

    with open(os.path.join(BASE, "REPORTE.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))

    # tablero html
    H = ["<!doctype html><html lang='es'><head><meta charset='utf-8'>",
         "<title>Tablero — Admisión Física Uniandes</title>",
         "<style>body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;",
         "max-width:820px;margin:2rem auto;padding:0 1rem;color:#222;background:#fff}",
         "h1{color:#1F3864}h2{color:#1F3864;border-bottom:1px solid #ddd;padding-bottom:.3rem;margin-top:2rem}",
         "img,svg{max-width:100%;border:1px solid #eee;border-radius:6px;margin:.6rem 0}",
         ".kpi{display:flex;gap:1rem;flex-wrap:wrap;margin:1rem 0}",
         ".kpi div{background:#F4F6FA;border-radius:8px;padding:.8rem 1.1rem;min-width:130px}",
         ".kpi b{display:block;font-size:1.5rem;color:#1F3864}",
         "li{margin:.45rem 0;line-height:1.45}@media print{body{max-width:none}}</style></head><body>",
         "<h1>Tablero de preparación</h1>",
         f"<p>{hoy.isoformat()} — faltan <b>{dias} días</b> para el examen. Semana {semana_actual()} de 14.</p>",
         "<div class='kpi'>",
         f"<div><b>{glob:.0f}%</b>acierto global</div>",
         f"<div><b>{len(A['sims'])}</b>simulacros</div>",
         f"<div><b>{sum(A['horas'].values()):.0f} h</b>estudiadas</div>",
         f"<div><b>{total_n}</b>preguntas</div></div>",
         "<h2>Qué cambiar en el cronograma</h2><ul>"]
    for r in R:
        H.append("<li>" + r.replace("**", "<b>", 1).replace("**", "</b>", 1)
                 .replace("**", "<b>", 1).replace("**", "</b>", 1)
                 .replace("`", "<code>", 1).replace("`", "</code>", 1) + "</li>")
    H.append("</ul>")
    for s in svgs:
        with open(s, encoding="utf-8") as f:
            H.append("<h2>" + os.path.basename(s)[3:-4].replace("_", " ").title() + "</h2>")
            H.append(f.read())
    H.append("</body></html>")
    with open(os.path.join(BASE, "tablero.html"), "w", encoding="utf-8") as f:
        f.write("\n".join(H))

    print(f"\n  REPORTE.md y tablero.html actualizados ({len(svgs)} gráficas).")
    print(f"  Ábrelo con:  xdg-open {os.path.join(BASE,'tablero.html')}\n")
    for r in R:
        print("  - " + r.replace("**", "").replace("`", ""))
    print()


def cmd_estado():
    asegurar()
    A = analizar()
    ok = sum(v[0] for v in A["por_area"].values())
    tot = sum(v[1] for v in A["por_area"].values())
    mapa_terminal()
    print(f"  Faltan {dias_restantes()} días. Semana {semana_actual()} de 14.")
    print(f"  Acierto global: {100.0*ok/tot if tot else 0:.1f}%  ({ok}/{tot})")
    print(f"  Horas acumuladas: {sum(A['horas'].values()):.1f}")
    if A["por_area"]:
        print("\n  Por área:")
        for a in AREAS:
            o, t = A["por_area"].get(a, [0, 0])
            if t:
                p = 100.0 * o / t
                barra = "#" * int(p / 5) + "." * (20 - int(p / 5))
                print(f"    {AREA_NOM[a]:<22} {barra} {p:5.1f}%  ({o}/{t})")
    print()



# ---------------------------------------------------------------- habilidades
def lista_skills():
    """Las habilidades salen del mapa del simulacro: una fuente de verdad."""
    mapa = cargar_mapa("uniandes_2024")
    out = []
    for q in sorted(mapa):
        m = mapa[q]
        out.append({
            "id": f"Q{q}",
            "area": m.get("area", "otros"),
            "tema": m.get("tema", ""),
            "nivel": (m.get("nivel") or "").upper(),
            "patron": (m.get("patron") or "").strip(),
        })
    out.sort(key=lambda s: (AREAS.index(s["area"]) if s["area"] in AREAS else 99, s["id"]))
    return out


def autoevaluacion():
    """Última autoevaluación por skill."""
    out = {}
    for r in leer("habilidades"):
        out[r["skill"]] = (r.get("fecha", ""), int(num(r.get("nivel"), 0)))
    return {k: v[1] for k, v in out.items()}


def evidencia_skills():
    """Acierto medido por skill, cruzando respuestas.csv por tema."""
    ev = defaultdict(lambda: [0, 0])
    skills = {s["tema"]: s["id"] for s in lista_skills() if s["tema"]}
    for r in leer("respuestas"):
        t = (r.get("tema") or "").strip()
        sid = skills.get(t)
        if sid:
            ev[sid][0] += int(num(r.get("ok")))
            ev[sid][1] += 1
    return ev


def nivel_medido(ok, tot):
    if not tot:
        return None
    p = ok / tot
    if p == 0:
        return 1
    if p < 0.5:
        return 2
    if p < 1.0:
        return 3
    return 4


def mapa_habilidades_svg():
    skills = lista_skills()
    auto = autoevaluacion()
    ev = evidencia_skills()
    if not skills:
        return None
    filas = 0
    areas_pres = []
    for a in AREAS:
        sub = [s for s in skills if s["area"] == a]
        if sub:
            areas_pres.append((a, sub))
            filas += len(sub) + 1
    h = 96 + 21 * filas + 3 * len(areas_pres)
    c = Lienzo(880, h, "Mapa de habilidades — barra: tu autoevaluación · marca: lo que miden los simulacros")
    c.ml, c.mt = 430, 46
    x0, ancho = c.ml, 300
    for i in range(5):
        x = x0 + ancho * i / 4.0
        c.linea(x, c.mt + 4, x, h - 42, "#EEE")
        c.texto(x, c.mt - 4, str(i), 9, "#AAA", "middle")
    y = c.mt + 18
    for a, sub in areas_pres:
        c.texto(14, y + 9, AREA_NOM[a].upper(), 10, "#1F3864", "start", "bold")
        y += 21
        for s in sub:
            n = auto.get(s["id"])
            ok, tot = ev.get(s["id"], [0, 0])
            med = nivel_medido(ok, tot)
            et = s["tema"][:58] + ("." if len(s["tema"]) > 58 else "")
            pre = (s["patron"] + " ") if s["patron"] else ""
            c.texto(28, y + 9, pre + et, 9, "#333" if s["nivel"] != "ALTO" else "#000",
                    "start", "bold" if s["patron"] else "normal")
            c.rect(x0, y, ancho, 13, "#F4F4F4")
            if n:
                col = "#B00020" if n <= 1 else ("#C2571A" if n == 2 else
                                                ("#0B6E4F" if n >= 4 else "#4A8C6F"))
                if med is not None and n - med >= 2:
                    col = "#B00020"
                c.rect(x0, y, ancho * n / 4.0, 13, col)
            if med is not None:
                mx = x0 + ancho * med / 4.0
                c.p.append(f'<polygon points="{mx:.1f},{y+13.5} {mx-4.5:.1f},{y+19.5} '
                           f'{mx+4.5:.1f},{y+19.5}" fill="#1F3864"/>')
                c.texto(x0 + ancho + 8, y + 10, f"{ok}/{tot}", 8, "#777")
            elif not n:
                c.texto(x0 + ancho + 8, y + 10, "sin datos", 8, "#BBB")
            y += 21
        y += 2
    c.texto(14, h - 12, "0 no lo he visto · 1 lo vi, no me sale · 2 lo entiendo si lo miro · "
                        "3 lo resuelvo solo · 4 lo resuelvo rápido", 9, "#888")
    c.texto(c.w - 14, h - 12, "rojo = crees saberlo más de lo que muestran los simulacros",
            9, "#B00020", "end")
    return c.guardar("00_mapa_habilidades.svg")


def mapa_terminal(compacto=True):
    skills = lista_skills()
    auto = autoevaluacion()
    ev = evidencia_skills()
    if not skills:
        return
    print("\n  ── Mapa de habilidades ──")
    flojas = []
    for a in AREAS:
        sub = [s for s in skills if s["area"] == a]
        if not sub:
            continue
        ns = [auto.get(s["id"], 0) for s in sub]
        prom = sum(ns) / len(ns)
        barra = "#" * int(round(prom * 5)) + "." * (20 - int(round(prom * 5)))
        sd = sum(1 for s in sub if s["id"] not in auto)
        print(f"    {AREA_NOM[a]:<21} {barra} {prom:.1f}/4"
              + (f"   ({sd} sin evaluar)" if sd else ""))
        for s in sub:
            n = auto.get(s["id"])
            ok, tot = ev.get(s["id"], [0, 0])
            med = nivel_medido(ok, tot)
            if n is not None and med is not None and n - med >= 2:
                flojas.append((s, n, med))
    if flojas and not compacto:
        print("\n  Ojo, crees que las sabes y los simulacros dicen otra cosa:")
        for s, n, med in flojas[:5]:
            print(f"    - {s['tema'][:64]}  (tú {n}, medido {med})")
    pend = [s for s in skills if s["patron"] and auto.get(s["id"], 0) < 3]
    if pend:
        print(f"\n  Patrones sin dominar ({len(pend)}): "
              + ", ".join(s["patron"] for s in pend))
    print()


def cmd_skills():
    asegurar()
    skills = lista_skills()
    if not skills:
        print("  Falta mapas/uniandes_2024.csv")
        return
    auto = autoevaluacion()
    ev = evidencia_skills()
    print("\n== Mapa de habilidades: autoevaluación ==")
    print("  0 no lo he visto | 1 lo vi, no me sale | 2 lo entiendo si lo miro")
    print("  3 lo resuelvo solo | 4 lo resuelvo rápido")
    print("  Enter deja el valor anterior. Ctrl-C para salir y guardar lo hecho.\n")
    hoy = dt.date.today().isoformat()
    guardadas = 0
    area_ant = None
    try:
        for s in skills:
            if s["area"] != area_ant:
                area_ant = s["area"]
                print(f"\n  --- {AREA_NOM[s['area']].upper()} ---")
            ok, tot = ev.get(s["id"], [0, 0])
            med = nivel_medido(ok, tot)
            pista = f"  [simulacros: {ok}/{tot}]" if tot else ""
            prev = auto.get(s["id"])
            pre = (s["patron"] + " — ") if s["patron"] else ""
            print(f"\n  {pre}{s['tema']}{pista}")
            r = input(f"    nivel [0-4]" + (f" ({prev})" if prev is not None else "") + ": ").strip()
            if not r:
                if prev is None:
                    continue
                n = prev
            elif r in "01234" and len(r) == 1:
                n = int(r)
            else:
                print("    -> valor inválido, salto")
                continue
            agregar("habilidades", {"fecha": hoy, "skill": s["id"], "nivel": n})
            guardadas += 1
            if med is not None and n - med >= 2:
                print(f"    OJO: los simulacros te dan un {med} ahí, no un {n}.")
    except KeyboardInterrupt:
        print("\n  (interrumpido)")
    print(f"\n  {guardadas} habilidades actualizadas.")
    mapa_terminal(compacto=False)


# ---------------------------------------------------------------- main
def main():
    cmds = {"sesion": cmd_sesion, "simulacro": cmd_simulacro, "error": cmd_error,
            "reporte": cmd_reporte, "estado": cmd_estado, "skills": cmd_skills}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        print(__doc__)
        print("  Exámenes con clave/mapa disponibles:", ", ".join(examenes_disponibles()) or "(ninguno)")
        return 1
    cmds[sys.argv[1]]()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n  cancelado.\n")
        sys.exit(1)
