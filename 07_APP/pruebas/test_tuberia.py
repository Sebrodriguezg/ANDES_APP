"""
Pruebas de la tubería de contenido.

Cada caso de aquí es un fallo que ya ocurrió. La regla del plan v2 es que un bug
entra como prueba antes de arreglarse, porque si no vuelve: varios de estos se
rompieron dos veces mientras se arreglaba otra cosa.

    python3 07_APP/pruebas/test_tuberia.py
"""

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "07_APP" / "tuberia"))

import geometria                      # noqa: E402
import extraer_hrw as H               # noqa: E402
import construir_contenido as C       # noqa: E402


def palabra(texto, x0, y0, alto=10.04, ancho=None):
    """Palabra sintética con la geometría que emite pdftotext -bbox-layout."""
    ancho = ancho if ancho is not None else len(texto) * 5.5
    return geometria.Palabra(texto, x0, y0, x0 + ancho, y0 + alto)


class TestExponentes(unittest.TestCase):
    """La reconstrucción de super y subíndices desde la geometría.

    En texto plano 10⁻⁹ sale como '10-9' y '4 m/s²' como '4 m/s', que es otra
    física. Todo esto existe para evitar eso.
    """

    def reconstruir(self, palabras):
        return geometria.Linea(palabras, 1).texto

    def test_exponente_simple(self):
        # 'Kr' seguido de un '86' elevado y en cuerpo menor.
        linea = [palabra("Kr", 100, 223.73), palabra("86", 111, 222.08, alto=7.01)]
        self.assertEqual(self.reconstruir(linea), "Kr^{86}")

    def test_exponente_negativo(self):
        """El menos matemático viene de otra fuente y su caja es MÁS alta que la
        del texto. Exigir que el exponente sea más pequeño dejaba 10^{-9} sin
        detectar, que fue el primer intento fallido."""
        linea = [
            palabra("B.", 91, 236.69),
            palabra("10", 111, 236.69),
            palabra("−9", 122, 235.04, alto=12.71),
            palabra("s", 135, 236.69),
        ]
        self.assertEqual(self.reconstruir(linea), "B. 10^{-9} s")

    def test_subindice(self):
        linea = [palabra("x", 100, 223.73), palabra("i", 106, 225.5, alto=7.0)]
        self.assertEqual(self.reconstruir(linea), "x_{i}")

    def test_texto_normal_sin_marcas(self):
        linea = [palabra("the", 100, 223.73), palabra("force", 120, 223.73)]
        self.assertEqual(self.reconstruir(linea), "the force")

    def test_delimitador_gigante_no_es_exponente(self):
        """Un corchete que abarca varias líneas está desplazado pero no es un
        exponente: se distingue por ser mucho más alto que el cuerpo."""
        linea = [palabra("A", 100, 223.73), palabra("[", 111, 200.0, alto=40.8)]
        self.assertNotIn("^{", self.reconstruir(linea))


class TestAgrupacionDeLineas(unittest.TestCase):
    """pdftotext saca a veces el exponente a una línea propia."""

    def test_exponente_en_linea_aparte_se_reune(self):
        """El '2' de '4 m/s²' salía en su propio <line> y se perdía, dejando
        'acelera a 4 m/s'. Las palabras se reagrupan por solape vertical."""
        palabras = [
            palabra("acelera", 100, 209.33),
            palabra("a", 140, 209.33),
            palabra("4", 150, 209.33),
            palabra("m/s", 160, 209.33),
            palabra("2", 180, 206.12, alto=7.01),
        ]
        lineas = geometria._agrupar_en_lineas(palabras, 1)
        self.assertEqual(len(lineas), 1, "debería quedar una sola línea")
        self.assertIn("m/s^{2}", lineas[0].texto)

    def test_dos_lineas_distintas_no_se_funden(self):
        palabras = [
            palabra("primera", 100, 223.73),
            palabra("segunda", 100, 236.69),
        ]
        lineas = geometria._agrupar_en_lineas(palabras, 1)
        self.assertEqual(len(lineas), 2)


class TestPieDePagina(unittest.TestCase):
    """El número de página cambia de lado según la paridad."""

    def linea_pie(self, texto):
        return geometria.Linea([palabra(texto, 90, 729.0)], 1)

    def test_pie_impar_y_par(self):
        impar = self.linea_pie("Chapter 1: MEASUREMENT 1")
        par = self.linea_pie("58 Chapter 5: FORCE AND MOTION - I")

        cap, _ = H._capitulos_por_pagina([impar])
        self.assertEqual(cap[1], 1)

        cap, _ = H._capitulos_por_pagina([par])
        self.assertEqual(cap[1], 5, "en páginas pares el número va delante")

    def test_titulo_sin_numero_de_pagina(self):
        _, titulos = H._capitulos_por_pagina([self.linea_pie("Chapter 1: MEASUREMENT 1")])
        self.assertEqual(titulos[1], "MEASUREMENT")


class TestLimpiezaDeDibujo(unittest.TestCase):
    """Separar la prosa del dibujo trazado con glifos."""

    def test_corta_la_cola_de_puntos(self):
        t = H.truncar_en_dibujo(
            "Which of the rods could be in static equilibrium? . .} • . . .} . } . .}"
        )
        self.assertEqual(t, "Which of the rods could be in static equilibrium?")

    def test_conserva_la_ultima_frase(self):
        """Cortar en el PRIMER final de frase se llevaba por delante la pregunta
        de verdad: '...horizontal track. At point 3:' se quedaba en 'track.'"""
        t = H.truncar_en_dibujo(
            "The block passes points 1, 2, 3, 4, 1 before returning to the "
            "horizontal track. At point 3: } • } 1 } . } . } . } . } •"
        )
        self.assertTrue(t.endswith("At point 3:"), f"quedó: {t!r}")

    def test_numeros_romanos_no_salvan_la_cola(self):
        """Los diagramas rotulados con I, II, III, IV, V parecen texto y
        engañaban a la heurística de 'cola sin letras'."""
        t = H.truncar_en_dibujo(
            "Rank the five processes according to the change in entropy of the "
            "gas, least to greatest. p T . . . .} . } I } . II III IV V } T V"
        )
        self.assertTrue(t.endswith("least to greatest."), f"quedó: {t!r}")

    def test_no_toca_un_enunciado_de_varias_frases(self):
        original = ("A block slides down a ramp. The ramp is frictionless. "
                    "What is the speed of the block at the bottom?")
        self.assertEqual(H.truncar_en_dibujo(original), original)

    def test_la_llave_de_subindice_no_es_trazo(self):
        """Meter '}' en el patrón de trazo partía T_{2} y destrozaba el texto."""
        self.assertFalse(H.es_trazo("a la misma temperatura T_{2} ."))


class TestReplegadoDeFormulas(unittest.TestCase):
    """Las tablas de constantes se parten al ancho del móvil."""

    def test_columnas_se_separan(self):
        r = C.desplegar_formula("Dilatación:   Δt = γΔt₀        (Δt₀ = tiempo propio)")
        self.assertEqual(len(r.split("\n")), 2)
        for linea in r.split("\n"):
            self.assertLessEqual(len(linea), C.ANCHO_FORMULA)

    def test_prosa_se_envuelve_con_un_espacio(self):
        r = C.desplegar_formula("25 preguntas · 3 horas · 7,2 min por pregunta")
        self.assertNotIn("  ·", r, "la prosa no debe unirse con espacios dobles")

    def test_linea_corta_no_se_toca(self):
        self.assertEqual(C.desplegar_formula("v = v₀ + at"), "v = v₀ + at")


class TestDeteccionDeFiguras(unittest.TestCase):
    """Qué cuenta como figura y qué no."""

    def setUp(self):
        sys.path.insert(0, str(RAIZ / "07_APP" / "tuberia"))
        import extraer_figuras
        self.F = extraer_figuras

    def test_una_opcion_matematica_no_es_dibujo(self):
        """Las opciones cortas con fórmulas tienen pocas letras y se colaban
        como 'rótulo de figura'. A 339 preguntas sin figura se les llegó a
        adjuntar una imagen que era texto de sus propias opciones."""
        self.assertFalse(H.es_trazo("A. x_{i} = 4 m, x_{f} = 6 m"))

    def test_hace_falta_trazo_de_verdad(self):
        """Un rótulo suelto huele a dibujo, pero solo los trazos —hileras de
        puntos, barras de eje— confirman que hay figura."""
        self.assertTrue(self.F._huele_a_dibujo("1 2 3"))
        self.assertFalse(H.es_trazo("1 2 3"), "un rótulo no basta")
        self.assertTrue(H.es_trazo(". . . . . . . ."), "esto sí es un eje")

    def test_cierre_de_enunciado_es_estructura(self):
        """La frontera del recorte la ponen las líneas de estructura. Si una
        línea corta de cierre no cuenta, el recorte se come el enunciado."""
        self.assertTrue(self.F._es_estructura("whose speed is increasing?"))
        self.assertFalse(self.F._es_estructura("v P"))
        self.assertFalse(self.F._es_estructura("1 2 3"))


class TestPortero(unittest.TestCase):
    """El portero tiene que dejar pasar lo bueno y parar lo malo."""

    def setUp(self):
        import portero
        self.P = portero

    def test_detecta_enunciado_sucio(self):
        self.assertTrue(self.P._sucio("La masa sube . . . . . }"))
        self.assertFalse(self.P._sucio("La masa sube por el plano inclinado."))

    def test_los_subindices_no_son_basura(self):
        self.assertFalse(self.P._sucio("a temperatura T_{2} y presión P_{1}"))

    def test_para_un_corpus_degradado(self):
        malas = [{"tipo": "mc", "enunciado": "x . . . . }", "codigo": "",
                  "respuesta": "", "opciones": {"A": ""}}]
        incumplidos = self.P.revisar(malas, revisar_figuras=False, estricto=False)
        self.assertTrue(incumplidos, "debería marcar varios umbrales")


class TestCodigos(unittest.TestCase):
    """El nombre corto con el que Sebastián puede referirse a una tarjeta."""

    def test_codigos_por_tipo(self):
        casos = [
            ({"id": "hrw-c05-q041", "tipo": "mc"}, "HRW 5.41"),
            ({"id": "patron-P2", "tipo": "patron", "patron": "P2"}, "P2"),
            ({"id": "error-D1-7", "tipo": "error"}, "D1·7"),
            ({"id": "eq-mec-03", "tipo": "ecuacion"}, "ECU 03"),
            ({"id": "descarte-05", "tipo": "descarte"}, "DES 05"),
        ]
        for tarjeta, esperado in casos:
            self.assertEqual(C.codigo_de(tarjeta), esperado)


if __name__ == "__main__":
    unittest.main(verbosity=2)
