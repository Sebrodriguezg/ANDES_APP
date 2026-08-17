"""
Construye `docs/contenido/cronograma.json` a partir de 03_TEMARIO/*.md y PLAN.md.

Las 14 semanas del plan, cada una desglosada en días según la estructura de semana
tipo de PLAN.md §5. Es lo que alimenta las pestañas HOY y PLAN de la app.
"""

import json
import re
import unicodedata
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
TEMARIO = RAIZ / "03_TEMARIO"
SALIDA = RAIZ / "docs" / "contenido" / "cronograma.json"

EXAMEN = date(2026, 11, 23)
ANIO = 2026

MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
}

ARCHIVOS = {
    "01_mecanica.md": "mecanica",
    "02_electromagnetismo.md": "electromagnetismo",
    "03_termo_estadistica.md": "termo_estadistica",
    "04_moderna_cuantica.md": "moderna_cuantica",
    "05_optica_ondas.md": "optica_ondas",
}

# Semanas que no viven en 03_TEMARIO porque no son de contenido nuevo.
# Fechas y foco tomados de la tabla de PLAN.md §5.
SEMANAS_EXTRA = {
    "S0": dict(numero=0, inicio=date(2026, 8, 14), fin=date(2026, 8, 23),
               titulo="Infraestructura, descargas y diagnóstico cronometrado",
               area="transversal",
               entregable="Mapa de fortalezas y debilidades real"),
    "S12": dict(numero=12, inicio=date(2026, 11, 9), fin=date(2026, 11, 15),
                titulo="Simulacros cronometrados: 3 completos, 25 preguntas en 3 h",
                area="transversal",
                entregable="Análisis de error por simulacro"),
    "S13": dict(numero=13, inicio=date(2026, 11, 16), fin=date(2026, 11, 22),
                titulo="Repaso de errores, formularios y 2 simulacros más",
                area="transversal",
                entregable="Listo. Los últimos dos días: repaso ligero y dormir"),
}

def _seccion(secciones, *prefijos):
    """Busca una sección por el principio de su título.

    Los encabezados varían entre archivos —"BASE — leer", "BASE/ALTO — leer (en
    este orden)", "ALTO — leer (núcleo de la semana)"— así que no sirve buscar
    por igualdad.
    """
    for prefijo in prefijos:
        for titulo, renglones in secciones.items():
            if titulo.upper().startswith(prefijo.upper()):
                return renglones
    return []


def _material_del_dia(bloque, secciones):
    """Qué leer o hacer hoy, en concreto.

    Antes el día solo traía la frase genérica de la semana tipo —"leer el
    capítulo y derivar los resultados"— y no decía qué capítulo ni de qué
    libro. El material está en las secciones de la semana; aquí se reparte
    entre los días según el bloque que le toque a cada uno.
    """
    base = _seccion(secciones, "BASE — leer", "BASE/ALTO")
    alto = _seccion(secciones, "ALTO — leer")
    problemas = _seccion(secciones, "PROBLEMAS")
    mc = _seccion(secciones, "Viernes")
    entregable = _seccion(secciones, "Entregable")

    if bloque == "teoria":
        # El lunes arranca por lo básico y el martes cierra con lo de nivel alto.
        return {"lunes": base[:2] or base, "martes": (base[2:] + alto) or alto}
    if bloque == "problemas":
        mitad = (len(problemas) + 1) // 2
        return {"miercoles": problemas[:mitad], "jueves": problemas[mitad:]}
    if bloque == "mc":
        return {"viernes": mc}
    if bloque == "repaso":
        return {"sabado": entregable}
    return {}


# Tareas concretas de las semanas que no salen de 03_TEMARIO. Sin esto, S0, S12
# y S13 muestran la frase genérica y nada más.
TAREAS_EXTRA = {
    "S0": {
        "teoria": ["Repasar el análisis del diagnóstico D1 en 05_SIMULACROS/D1_resultados.md",
                   "Revisar los 10 patrones en 03_TEMARIO/00_mapa_simulacro.md"],
        "problemas": ["Rehacer a mano las preguntas del D1 que fallaste",
                      "Media sesión de expansiones binomiales: (1+x)^n para x pequeño"],
        "mc": ["Sesión cronometrada en la app: 25 preguntas a 7 min"],
        "repaso": ["Dejar listo el formulario en blanco de Mecánica para S1"],
    },
    "S12": {
        "teoria": ["Repasar los formularios de las áreas más flojas"],
        "problemas": ["Simulacro completo en la app: 25 preguntas, 3 horas"],
        "mc": ["Simulacro completo y análisis de error por área"],
        "repaso": ["Rehacer de memoria lo fallado en los simulacros"],
    },
    "S13": {
        "teoria": ["Repaso de errores y formularios"],
        "problemas": ["Dos simulacros más, en condiciones reales"],
        "mc": ["Último simulacro. Meta: 18 de 25"],
        "repaso": ["Solo repaso ligero. Dormir. 18-nov cierra inscripción, 19-nov documentos"],
    },
}


# Estructura de la semana tipo (PLAN.md §5): cinco sesiones de 1 a 2 horas, con
# el fin de semana de comodín. Antes la app pedía 17 h semanales y el cronograma
# impreso 5-10, así que cada uno mandaba una cosa distinta para el mismo día.
SEMANA_TIPO = [
    ("lunes",     "teoria",    "1–2", "Leer el capítulo y derivar los resultados a mano"),
    ("martes",    "teoria",    "1–2", "Cerrar la teoría y construir el formulario del tema"),
    ("miercoles", "problemas", "1–2", "Problemas del libro de práctica, sin límite de tiempo"),
    ("jueves",    "problemas", "1–2", "Seguir con los problemas asignados de la semana"),
    ("viernes",   "mc",        "1–2", "Opción múltiple cronometrada a 7 min por pregunta"),
    ("sabado",    "comodin",   "",    "Comodín. Solo si quedó algo pendiente entre semana"),
    ("domingo",   "comodin",   "",    "Comodín o descanso. Si vas al día, libre"),
]

# Algunos encabezados traen solo el rango de fechas, sin título de semana.
TITULOS_FALLBACK = {
    "S11": "Óptica y ondas, más repaso transversal",
}

RE_SEMANA = re.compile(r"^##\s+(S\d+)\s*·\s*(.+?)(?:\s+—\s+(.*))?$")
RE_SUBSECCION = re.compile(r"^###\s+(.*)$")


def _sin_tildes(texto):
    return "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )


def _parsear_rango(crudo):
    """'31 agosto–6 septiembre' o '24–30 agosto' -> (date, date).

    Cuando el primer extremo no trae mes, hereda el del segundo.
    """
    texto = _sin_tildes(crudo.lower()).replace("-", "–")
    partes = [p.strip() for p in texto.split("–") if p.strip()]
    if len(partes) != 2:
        return None, None

    def descomponer(parte):
        m = re.match(r"(\d+)\s*(?:de\s+)?([a-z]+)?", parte)
        if not m:
            return None, None
        dia = int(m.group(1))
        nombre = m.group(2)
        mes = None
        if nombre:
            for clave, num in MESES.items():
                if _sin_tildes(clave).startswith(nombre[:4]):
                    mes = num
                    break
        return dia, mes

    dia_ini, mes_ini = descomponer(partes[0])
    dia_fin, mes_fin = descomponer(partes[1])
    if dia_ini is None or dia_fin is None:
        return None, None
    mes_ini = mes_ini or mes_fin
    mes_fin = mes_fin or mes_ini
    if not mes_ini or not mes_fin:
        return None, None
    return date(ANIO, mes_ini, dia_ini), date(ANIO, mes_fin, dia_fin)


def _limpiar_markdown(texto):
    """Deja el texto legible fuera de un renderizador de Markdown."""
    texto = re.sub(r"`([^`]*)`", r"\1", texto)
    texto = re.sub(r"\*\*([^*]*)\*\*", r"\1", texto)
    texto = re.sub(r"\*([^*]*)\*", r"\1", texto)
    texto = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", texto)
    return texto.strip()


def _parsear_secciones(cuerpo):
    """Convierte las subsecciones ### de una semana en listas de renglones."""
    secciones = {}
    actual = None
    for linea in cuerpo.split("\n"):
        m = RE_SUBSECCION.match(linea)
        if m:
            actual = _limpiar_markdown(m.group(1))
            secciones[actual] = []
            continue
        if actual is None:
            continue
        texto = linea.strip()
        if not texto or texto.startswith("---"):
            continue
        # Las tablas de PROBLEMAS se aplanan a "fuente — asignación".
        if texto.startswith("|"):
            celdas = [c.strip() for c in texto.strip("|").split("|")]
            celdas = [c for c in celdas if c and not set(c) <= set("-: ")]
            if not celdas or celdas[0].lower() in ("fuente", "libro"):
                continue
            secciones[actual].append(_limpiar_markdown(" — ".join(celdas)))
            continue
        texto = re.sub(r"^[-*]\s+", "", texto)
        secciones[actual].append(_limpiar_markdown(texto))
    return {k: v for k, v in secciones.items() if v}


def _dias_de(semana):
    """Reparte la semana en días concretos según la estructura de semana tipo."""
    dias = []
    cursor = semana["inicio"]
    fin = semana["fin"]
    # El primer día se alinea con el lunes de la plantilla; si la semana arranca
    # a media semana (S0), se recorta lo que sobre por delante.
    plantilla = {nombre: (bloque, horas, que)
                 for nombre, bloque, horas, que in SEMANA_TIPO}
    nombres = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]

    secciones = semana.get("secciones") or {}
    extra = TAREAS_EXTRA.get(semana["id"], {})

    while cursor <= fin:
        nombre = nombres[cursor.weekday()]
        bloque, horas, que = plantilla[nombre]
        material = _material_del_dia(bloque, secciones).get(nombre, [])
        if not material:
            material = extra.get(bloque, [])
        dias.append({
            "fecha": cursor.isoformat(),
            "dia": nombre,
            "bloque": bloque,
            "horas": horas,
            "que": que,
            "material": material,
        })
        cursor += timedelta(days=1)
    return dias


def parsear_temario():
    semanas = {}
    for archivo, area in ARCHIVOS.items():
        ruta = TEMARIO / archivo
        if not ruta.exists():
            continue
        texto = ruta.read_text(encoding="utf-8")
        # Se parte por encabezados de nivel 2 conservando el encabezado.
        trozos = re.split(r"(?m)^(?=##\s+S\d+\s*·)", texto)
        for trozo in trozos:
            m = RE_SEMANA.match(trozo.split("\n", 1)[0])
            if not m:
                continue
            ident, rango, titulo = m.group(1), m.group(2), m.group(3) or ""
            inicio, fin = _parsear_rango(rango)
            if inicio is None:
                print(f"  aviso: no pude leer las fechas de {ident} ({rango!r})")
                continue
            cuerpo = trozo.split("\n", 1)[1] if "\n" in trozo else ""
            secciones = _parsear_secciones(cuerpo)
            semanas[ident] = {
                "id": ident,
                "numero": int(ident[1:]),
                "inicio": inicio,
                "fin": fin,
                "titulo": (_limpiar_markdown(titulo)
                           or TITULOS_FALLBACK.get(ident)
                           or _limpiar_markdown(rango)),
                "area": area,
                "fuente": f"03_TEMARIO/{archivo}",
                "secciones": secciones,
                "entregable": " · ".join(secciones.get("Entregable", [])),
            }
    return semanas


def main():
    semanas = parsear_temario()

    for ident, extra in SEMANAS_EXTRA.items():
        semanas[ident] = {
            "id": ident, "fuente": "PLAN.md", "secciones": {}, **extra,
        }

    ordenadas = sorted(semanas.values(), key=lambda s: s["numero"])
    for s in ordenadas:
        s["dias"] = _dias_de(s)
        s["inicio"] = s["inicio"].isoformat()
        s["fin"] = s["fin"].isoformat()

    datos = {
        "examen": EXAMEN.isoformat(),
        "generado": date.today().isoformat(),
        "semana_tipo": [
            {"dia": d, "bloque": b, "horas": h, "que": q}
            for d, b, h, q in SEMANA_TIPO
        ],
        "semanas": ordenadas,
    }

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"{len(ordenadas)} semanas -> {SALIDA.relative_to(RAIZ)}")
    for s in ordenadas:
        secc = len(s["secciones"])
        print(f"  {s['id']:4s} {s['inicio']} a {s['fin']}  "
              f"{secc} secciones  {s['titulo'][:52]}")


if __name__ == "__main__":
    main()
