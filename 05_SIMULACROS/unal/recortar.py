"""Recorta preguntas sueltas de los exámenes GRE que tienen texto (GR0177 y GR1775).

Los dos están maquetados a dos columnas, y en los GRE la figura de una pregunta
suele ir ENCIMA de su número ("In the circuit shown above..."). Por eso el corte
no se hace en el número: una pregunta termina en el primer espacio en blanco
después de su opción (E), y la siguiente empieza justo ahí, con su figura.

El blanco se busca en la imagen, no en el texto: las figuras y las fracciones
altas no son palabras para pdftotext, pero sí son tinta.

    from recortar import Examen
    ex = Examen("GR0177")
    ex.recortar(17, carpeta)   # -> lista de PNG, uno por tramo
"""

import re
import subprocess
from functools import lru_cache
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parents[2]
GRE = RAIZ / "01_EXAMENES/gre_physics"
CACHE = Path(__file__).parent / "_cache"

PDFS = {
    "GR0177": GRE / "GR0177_exam.pdf",
    "GR1775": GRE / "ETS_Practice_Book_Physics.pdf",
}

# Geometría en puntos (página carta, 612 pt de ancho).
CORTE = 300
COLUMNAS = {0: (28, 302), 1: (300, 590)}
ARRIBA, ABAJO = 30, 722   # fuera la cabecera y el pie ("Unauthorized copying...", 728)
DPI = 170
BLANCO_MIN = 7            # pt de blanco que cuentan como separación entre preguntas


def _orden(f):
    return (f[0], f[1], f[2])


class Examen:
    def __init__(self, nombre):
        self.nombre = nombre
        self.pdf = PDFS[nombre]
        xml = subprocess.run(["pdftotext", "-bbox", str(self.pdf), "-"],
                             capture_output=True, text=True).stdout
        self.numeros, self.opciones_e = self._fichas(xml)
        self.inicios = self._cadena()

    def _fichas(self, xml):
        numeros, es = [], []
        for pag, cuerpo in enumerate(xml.split("<page ")[1:], 1):
            for x0, y0, y1, txt in re.findall(
                    r'xMin="([\d.]+)" yMin="([\d.]+)" xMax="[\d.]+" yMax="([\d.]+)">([^<]*)<', cuerpo):
                col = 0 if float(x0) < CORTE else 1
                if re.fullmatch(r"\d{1,3}\.", txt):
                    numeros.append((pag, col, float(y0), int(txt[:-1])))
                elif txt.startswith("(E)"):
                    es.append((pag, col, float(y0)))
        return sorted(numeros), sorted(es)

    def _cadena(self):
        """La cadena 1, 2, 3... más larga en orden de lectura: así no se cuelan
        los ejemplos de las instrucciones ni números sueltos del texto."""
        mejor = {}
        for i, f in enumerate(self.numeros):
            if f[3] != 1:
                continue
            cadena, esperado = {}, 1
            for g in self.numeros[i:]:
                if g[3] == esperado:
                    cadena[esperado] = g[:3]
                    esperado += 1
            # A igual largo gana la que empieza más tarde: el índice de temas
            # ("1. CLASSICAL MECHANICS, 2. ...") también se numera.
            if len(cadena) >= len(mejor):
                mejor = cadena
        return mejor

    # ── Imagen ────────────────────────────────────────────────

    @lru_cache(maxsize=64)
    def _pagina(self, pag):
        CACHE.mkdir(parents=True, exist_ok=True)
        base = CACHE / f"{self.nombre}_p{pag:03d}"
        png = base.with_suffix(".png")
        if not png.exists():
            subprocess.run(["pdftoppm", "-png", "-gray", "-r", str(DPI), "-f", str(pag), "-l", str(pag),
                            "-singlefile", str(self.pdf), str(base)], check=True)
        return Image.open(png).convert("L")

    def _fila_vacia(self, img, col, y_pt):
        e = DPI / 72
        x0, x1 = COLUMNAS[col]
        fila = img.crop((int(x0 * e), int(y_pt * e), int(x1 * e), int(y_pt * e) + 1))
        return min(fila.getdata()) > 200

    def _blanco_despues(self, pag, col, y_pt, limite):
        """Primer tramo en blanco de BLANCO_MIN pt a partir de y_pt; devuelve su mitad."""
        img = self._pagina(pag)
        paso, corrida, y = 0.5, 0.0, y_pt
        while y < limite:
            corrida = corrida + paso if self._fila_vacia(img, col, y) else 0.0
            if corrida >= BLANCO_MIN:
                return y - corrida / 2
            y += paso
        return limite

    # ── Límites de cada pregunta ─────────────────────────────

    def _tope(self, n):
        """Dónde empieza la pregunta n: tras el blanco que sigue a la (E) de la n-1,
        si está en la misma columna; si no, arriba de la columna."""
        pag, col, y = self.inicios[n]
        if n - 1 in self.inicios:
            previo = self.inicios[n - 1]
            e = next((f for f in self.opciones_e if _orden(f) > previo), None)
            if e and e[0] == pag and e[1] == col and e[2] < y:
                return pag, col, self._blanco_despues(pag, col, e[2], y)
        return pag, col, ARRIBA

    def _fin(self, n):
        """Dónde termina la pregunta n: en el blanco que sigue a su propia (E)."""
        e = next((f for f in self.opciones_e if _orden(f) > self.inicios[n]), None)
        if e is None:
            return None
        return e[0], e[1], self._blanco_despues(e[0], e[1], e[2], ABAJO)

    def _tramos(self, n):
        """Del tope al fin. Si cruzan de columna, dos tramos; las páginas de
        SCRATCH WORK quedan fuera porque se salta directo a la página de la (E)."""
        pag, col, y = self._tope(n)
        fin = self._fin(n)
        if fin is None or fin[:2] == (pag, col):
            x0, x1 = COLUMNAS[col]
            return [(pag, x0, y, x1, fin[2] if fin else ABAJO)]
        x0, x1 = COLUMNAS[col]
        fx0, fx1 = COLUMNAS[fin[1]]
        return [(pag, x0, y, x1, ABAJO), (fin[0], fx0, ARRIBA, fx1, fin[2])]

    def recortar(self, n, carpeta):
        carpeta.mkdir(parents=True, exist_ok=True)
        e = DPI / 72
        salida = []
        for i, (pag, x0, y0, x1, y1) in enumerate(self._tramos(n)):
            img = self._pagina(pag)
            # Pregunta a todo el ancho (figura grande): hay tinta en el canal
            # entre columnas, así que se recorta la página entera.
            canal = img.crop((int(292 * e), int(y0 * e), int(308 * e), int(y1 * e)))
            if canal.height > 4 and min(canal.getdata()) < 120:
                x0, x1 = COLUMNAS[0][0], COLUMNAS[1][1]
            caja = img.crop((int(x0 * e), int(y0 * e), int(x1 * e), int(y1 * e)))
            # Un tramo sin tinta (la pregunta acabó justo al pie) no se guarda.
            if caja.height < 4 or min(caja.getdata()) > 200:
                continue
            ruta = carpeta / f"{self.nombre}_{n:03d}_{i}.png"
            _recortar_blanco(caja).save(ruta)
            salida.append(ruta)
        return salida


def _recortar_blanco(img):
    """Quita el margen blanco sobrante de arriba y abajo."""
    negativo = img.point(lambda v: 255 if v < 200 else 0)
    caja = negativo.getbbox()
    if not caja:
        return img
    return img.crop((0, max(0, caja[1] - 6), img.width, min(img.height, caja[3] + 6)))


if __name__ == "__main__":
    for nombre in PDFS:
        ex = Examen(nombre)
        print(nombre, len(ex.inicios), "preguntas ubicadas")
