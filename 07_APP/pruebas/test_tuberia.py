"""
Pruebas de la tubería de contenido.

Cada caso de aquí es un fallo que ya ocurrió. La regla del plan v2 es que un bug
entra como prueba antes de arreglarse, porque si no vuelve: varios de estos se
rompieron dos veces mientras se arreglaba otra cosa.

    python3 07_APP/pruebas/test_tuberia.py
"""

import sys
import collections
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


class TestSimbolosYOpciones(unittest.TestCase):
    """Tres fallos que Sebastián vio en el teléfono antes que yo."""

    def test_el_signo_de_multiplicar_no_se_desplaza(self):
        """El × viene de una fuente de símbolos y su caja mide 18 pt contra los
        10 del texto. Agrupando las líneas solo por su base formaba línea
        propia y acababa al final del renglón: "3.1 10^{-10} s ×"."""
        palabras = [
            palabra("3.1", 100, 510.08),
            palabra("×", 118, 511.72, alto=18.27),
            palabra("10", 134, 510.08),
            palabra("-10", 146, 508.4, alto=7.01),
            palabra("s", 160, 510.08),
        ]
        lineas = geometria._agrupar_en_lineas(palabras, 1)
        self.assertEqual(len(lineas), 1, "el × debe quedar en la misma línea")
        texto = lineas[0].texto
        self.assertIn("3.1", texto)
        self.assertLess(texto.index("times"), texto.index("10^"),
                        f"el × va entre el número y la potencia: {texto!r}")

    def test_la_cola_con_puntos_se_corta_aunque_traiga_palabras(self):
        """Los rótulos de dentro del dibujo también son palabras: "water air",
        "60", "30". Lo que delata la cola es la hilera de puntos."""
        t = H.truncar_en_dibujo(
            "If n = 1.33, what is the angle of refraction for the ray shown? "
            ". 60 . . . . . . . ° . . . . . . 30 . . . . . water air")
        self.assertTrue(t.endswith("shown?"), f"quedó: {t!r}")


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


class TestGlifosPerdidos(unittest.TestCase):
    """Los glifos que pdftotext borraba en silencio.

    En 2.208 preguntas la `ℓ` no aparecía ni una vez, la `ε₀` de la constante de
    Coulomb tampoco, y siete `≠` se habían quedado en `=`, que invierte el
    enunciado. Un caso congelado por clase, con la geometría real medida en el
    PDF, porque lo que decide la clase es dónde está el glifo y cuánto mide.
    """

    def setUp(self):
        import glifos
        self.G = glifos

    def _caja(self, x0, y0, x1, y1):
        return (x0, y0, x1, y1)

    def test_acento_de_vector_va_encima_de_su_letra(self):
        # Página 35: "Let →R = →S × →T". La flecha solapa en x con la R y queda
        # entera por encima de ella.
        flecha = self._caja(112.9, 72.0, 118.4, 74.2)
        erre = ("cmmi10", "R", self._caja(111.5, 75.2, 119.8, 82.9))
        self.assertEqual(
            self.G.clasificar("cmmi10", flecha, erre, None, 4.7), "vector")

    def test_barra_de_negacion_hace_un_distinto(self):
        # Misma página: "θ ≠ 90°". La barra sale de cmsy y cruza el igual.
        barra = self._caja(74.8, 74.8, 80.0, 85.0)
        igual = ("cmr10", "=", self._caja(75.0, 78.6, 81.0, 81.2))
        self.assertEqual(
            self.G.clasificar("cmsy10", barra, igual, None, 4.7), "negacion")

    def test_la_ele_cursiva_tiene_ascendente(self):
        # Página 599: "the same value of ℓ". Va en el flujo del texto y mide
        # vez y media la altura de la x.
        ele = self._caja(237.0, 237.8, 241.0, 245.6)
        sig = ("cmr10", "a", self._caja(242.0, 240.6, 246.0, 245.6))
        self.assertEqual(
            self.G.clasificar("cmmi10", ele, sig, None, 4.9), "ele")

    def test_la_epsilon_no_lo_tiene_y_lleva_el_cero_detras(self):
        # Página 327: "1/4πε₀". Sin ascendente, y el subíndice cero la sigue.
        eps = self._caja(100.0, 240.0, 104.0, 244.5)
        cero = ("cmr7", "0", self._caja(104.0, 240.0, 107.0, 244.0))
        self.assertEqual(
            self.G.clasificar("cmmi10", eps, cero, None, 4.9), "epsilon")

    def test_el_operador_se_reconoce_por_la_fuente_no_por_la_altura(self):
        # Página 479, las ecuaciones de Maxwell. Una de las cuatro integrales
        # medía 1,97 de alto y se colaba como ele: la fuente cmex la separa.
        integral = self._caja(70.0, 100.0, 75.1, 119.3)
        sig = ("cmmi10", "E", self._caja(76.0, 104.0, 82.0, 112.0))
        self.assertEqual(
            self.G.clasificar("cmex10", integral, sig, None, 4.9,
                              cuerpo=10.91), "integral")

    def test_un_glifo_solo_en_su_renglon_no_se_resuelve(self):
        # Los rótulos sueltos de las figuras: antes que arriesgar, se dejan.
        suelto = self._caja(10.0, 10.0, 14.0, 18.0)
        self.assertEqual(
            self.G.clasificar("cmmi10", suelto, None, None, 4.9,
                              en_contexto=False), "aislado")


class TestFormaDeLasExplicaciones(unittest.TestCase):
    """Que una explicación mal escrita no llegue al teléfono.

    Al escribirlas a mano se cuela con facilidad una llave donde iba un
    corchete: el JSON sigue siendo válido, `pasos` queda como objeto vacío y
    la app pinta la explicación sin ningún paso. Pasó dos veces el mismo día.
    """

    BUENA = {"idea": "x", "pasos": ["a"], "porque_fallan": {}, "confirma": "A"}

    def test_una_explicacion_correcta_pasa(self):
        C.comprobar_forma("t.json", "x-1", self.BUENA)

    def test_pasos_como_objeto_revienta(self):
        with self.assertRaises(SystemExit):
            C.comprobar_forma("t.json", "x-1", dict(self.BUENA, pasos={"a": "b"}))

    def test_pasos_vacios_revientan(self):
        with self.assertRaises(SystemExit):
            C.comprobar_forma("t.json", "x-1", dict(self.BUENA, pasos=[]))

    def test_sin_letra_confirmada_revienta(self):
        with self.assertRaises(SystemExit):
            C.comprobar_forma("t.json", "x-1", dict(self.BUENA, confirma="Z"))

    def test_idea_vacia_revienta(self):
        with self.assertRaises(SystemExit):
            C.comprobar_forma("t.json", "x-1", dict(self.BUENA, idea="   "))


class TestReparacionDeGlifos(unittest.TestCase):
    """Que reponer los glifos no se lleve por delante otra cosa."""

    def setUp(self):
        import reparar_glifos
        self.R = reparar_glifos

    def test_no_borra_el_marcado_de_exponentes(self):
        # El fallo que casi cometo: normalizar para comparar está bien, pero
        # escribir ese resultado devolvía 10^{8} a 10 8.
        texto = "a speed of 3.0 × 10^{8} m/s"
        salida = self.R.reparar_texto(texto, {}, collections.Counter())
        self.assertIn("10^{8}", salida)

    def test_repone_la_epsilon_de_la_constante_de_coulomb(self):
        c = collections.Counter()
        self.assertEqual(
            self.R.reparar_texto("The units of 1/4π_{0} are:", {}, c),
            "The units of 1/4πε_{0} are:")

    def test_repone_la_epsilon_tras_una_division(self):
        c = collections.Counter()
        self.assertEqual(self.R.reparar_texto("is q/_{0}", {}, c), "is q/ε_{0}")

    def test_la_reparacion_es_idempotente(self):
        c = collections.Counter()
        una = self.R.reparar_texto("The units of 1/4π_{0} are:", {}, c)
        dos = self.R.reparar_texto(una, {}, c)
        self.assertEqual(una, dos)

    def test_colapsa_los_glifos_que_se_repitieron(self):
        # Cuando el mismo hueco cae dentro de varias ventanas, el glifo se
        # reponía una vez por ventana: «→→→→F», «ℓ ℓ ℓ ℓ». Y como el texto ya
        # reparado volvía a coincidir, el corpus crecía un glifo por ejecución
        # hasta que alguien lo mirara. Tres capítulos llegaron a seis ℓ.
        c = collections.Counter()
        self.assertEqual(
            self.R.reparar_texto("→→→→F is the net external force", {}, c),
            "→F is the net external force")
        self.assertEqual(
            self.R.reparar_texto("depend on both n and ℓ ℓ ℓ ℓ", {}, c),
            "depend on both n and ℓ")

    def test_las_recetas_por_tarjeta_no_se_reaplican(self):
        # Una receta que *añade* un glifo al final vuelve a encontrar su patrón
        # en la pasada siguiente. Sin la guarda, «depend on ℓ» acababa siendo
        # «depend on ℓ ℓ ℓ ℓ ℓ ℓ».
        tarjeta = {"id": "hrw-c40-q020",
                   "enunciado": "",
                   "opciones": {"B": "depend on"}}
        una = self.R.aplicar_por_tarjeta(dict(tarjeta, opciones={"B": "depend on"}))
        self.assertEqual(una["opciones"]["B"], "depend on ℓ")
        dos = self.R.aplicar_por_tarjeta(una)
        self.assertEqual(dos["opciones"]["B"], "depend on ℓ")

    def test_separa_la_opcion_que_se_fundio_con_la_anterior(self):
        # La B de 11.18 venía incrustada dentro de la A y la tarjeta se
        # quedaba en cuatro opciones.
        t = self.R.separar_opciones_fundidas({
            "id": "hrw-c11-q018",
            "opciones": {
                "A": "mass \\cdot length \\cdot time^{-1} _{B.}_{mass}",
                "C": "mass^{2} \\cdot time^{-1}",
            }})
        self.assertEqual(len(t["opciones"]), 3)
        self.assertNotIn("_{B.}", t["opciones"]["A"])
        self.assertIn("length^{-2}", t["opciones"]["B"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
