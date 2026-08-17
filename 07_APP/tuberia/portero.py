"""
Portero del build: mide la calidad del corpus y decide si se puede publicar.

Existe porque las regresiones de datos son silenciosas. Un cambio en una regex
para arreglar una pregunta puede ensuciar doscientas sin que nada falle: el
build termina bien, las tandas se cifran, y el estropicio aparece cuando
Sebastián lo ve en el teléfono. Ya pasó dos veces.

La regla es con umbrales, no con impresiones: "se ve mejor" no sirve, "figuras
cortadas por debajo del 10 %" sí.
"""

import base64
import io
import json
import re

# Umbrales que no se pueden cruzar para publicar.
UMBRALES = {
    "enunciados_sucios_pct": 2.0,     # restos de dibujo mezclados con la prosa
    "figuras_inciertas_pct": 12.0,    # recortadas sin texto que las enmarcara
    "sin_codigo_pct": 0.0,            # toda tarjeta necesita su nombre corto
    "mc_sin_respuesta_pct": 0.0,      # una pregunta sin clave no sirve
    "opciones_vacias_pct": 0.5,       # salvo las que traen las opciones dibujadas
}

# Basura de figura, sin contar los subíndices legítimos que genera el extractor.
RE_SUBINDICE = re.compile(r"[_^]\{[^{}]*\}")
RE_BASURA = re.compile(r"(\.\s*){3,}|•|\}\s*\}")


def _sucio(texto):
    return bool(RE_BASURA.search(RE_SUBINDICE.sub("", texto or "")))


def _figura_incierta(figura):
    """¿Se recortó sin texto que enmarcara la franja?

    Cuando hay texto arriba y abajo el recorte es exacto por construcción: el
    dibujo vive en ese hueco y no puede solaparse con las letras. Sin esa
    referencia hay que recortar a ojo, y esas son las que conviene revisar.

    Las dos versiones anteriores de esta medida buscaban tinta en el borde del
    PNG, y marcaban como cortada cualquier figura que simplemente llenara el
    hueco. Medían otra cosa.
    """
    return bool(figura.get("incierta"))


def medir(tarjetas, revisar_figuras=True):
    """Devuelve las métricas de calidad del corpus, en porcentaje."""
    total = len(tarjetas) or 1
    mc = [t for t in tarjetas if t.get("tipo") == "mc"]
    con_figura = [t for t in tarjetas if t.get("figura")]

    sucios = sum(1 for t in tarjetas if _sucio(t.get("enunciado", "")))
    sin_codigo = sum(1 for t in tarjetas if not t.get("codigo"))
    sin_respuesta = sum(1 for t in mc if not t.get("respuesta"))

    # Una opción vacía solo se acepta si la alternativa está dibujada.
    vacias = sum(
        1 for t in mc
        if any(not v.strip() for v in t.get("opciones", {}).values())
        and not t.get("figura")
    )

    cortadas = 0
    if revisar_figuras and con_figura:
        cortadas = sum(1 for t in con_figura if _figura_incierta(t["figura"]))

    return {
        "total": len(tarjetas),
        "mc": len(mc),
        "con_figura": len(con_figura),
        "enunciados_sucios_pct": 100 * sucios / total,
        "figuras_inciertas_pct": 100 * cortadas / (len(con_figura) or 1),
        "sin_codigo_pct": 100 * sin_codigo / total,
        "mc_sin_respuesta_pct": 100 * sin_respuesta / (len(mc) or 1),
        "opciones_vacias_pct": 100 * vacias / (len(mc) or 1),
    }


def revisar(tarjetas, revisar_figuras=True, estricto=True):
    """Imprime el informe y devuelve la lista de umbrales cruzados."""
    m = medir(tarjetas, revisar_figuras)

    print("\n  Calidad del corpus")
    print(f"    {m['total']} tarjetas · {m['mc']} de opción múltiple · "
          f"{m['con_figura']} con figura")

    incumplidos = []
    for clave, tope in UMBRALES.items():
        valor = m[clave]
        pasa = valor <= tope
        if not pasa:
            incumplidos.append((clave, valor, tope))
        marca = "ok " if pasa else "MAL"
        print(f"    {marca}  {clave:26} {valor:5.1f} %   (tope {tope} %)")

    if incumplidos and estricto:
        print("\n  El corpus no cumple. No se publica.")
        for clave, valor, tope in incumplidos:
            print(f"    {clave}: {valor:.1f} % supera el tope de {tope} %")
    return incumplidos


def guardar_historial(m, ruta):
    """Anota las métricas para poder ver si algo empeoró entre dos builds."""
    historial = []
    if ruta.exists():
        try:
            historial = json.loads(ruta.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            historial = []
    historial.append(m)
    ruta.write_text(json.dumps(historial[-40:], ensure_ascii=False, indent=1),
                    encoding="utf-8")
