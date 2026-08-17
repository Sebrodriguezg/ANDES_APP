# Plan v2 — de app que funciona a app que entrena

> Objetivo: que la app deje de ser un banco de preguntas bonito y pase a ser el
> instrumento que corrige lo que el diagnóstico D1 dejó al descubierto.

Estado al escribir esto: 2.577 tarjetas, 12 tandas cifradas, 5 MB publicados de
~1 GB disponibles. El espacio no es la restricción; el tiempo hasta el 23 de
noviembre sí.

---

## El principio que ordena todo

Cada cosa de esta lista existe porque ataca un hallazgo concreto del D1, no
porque sea una buena idea en abstracto:

| Hallazgo del D1 | Qué lo ataca |
|---|---|
| 14 min en una sola pregunta | Cronómetro por tarjeta |
| 9 de 10 fallos conceptuales | Botón de causa al fallar |
| Pregunta 8: confianza 4 y fallada | Confianza antes de revelar |
| Base 0/6 — hay que reconstruir | Repaso espaciado activo |
| El examen son 25 preguntas en 3 h | Modo simulacro |
| El banco no explica por qué | Explicaciones del GRE |

---

## F7 · Red de seguridad — va primero

Va primero a propósito. En las últimas sesiones los bugs los encontró Sebastián
antes que yo: el progreso que arrancaba en 6/30, los asteriscos crudos, `K_rot`
partido, las figuras cortadas. Eso no puede seguir pasando, y la forma de
evitarlo no es tener más cuidado sino tener pruebas.

**Cuatro capas:**

1. **Pruebas de la tubería** (`pruebas/test_tuberia.py`). Casos congelados de
   las trampas ya conocidas: el capítulo 18 mal rotulado, el pie de página que
   cambia de lado según la paridad, `4 m/s²` sin el exponente, la cola de
   dibujo con números romanos. Cada bug que aparezca entra aquí antes de
   arreglarse.

2. **Pruebas del estado** (`pruebas/test_almacen.mjs`). La lógica de contar,
   numerar, reanudar y fusionar progreso, con localStorage simulado. Es donde
   vivió el bug del 6/30.

3. **Portero del build.** `construir_contenido.py` falla si el corpus rompe un
   umbral: enunciados con basura por encima del 2 %, figuras cortadas por
   encima del 10 %, tarjetas sin código, fórmulas que KaTeX no compila. Mejor
   no publicar que publicar roto.

4. **Hoja de contacto visual.** Un comando que renderiza en Chrome headless a
   414 px una muestra de cada tipo de tarjeta y la guarda como tira de
   imágenes. Es lo que ya hicimos a mano; formalizarlo lo vuelve rutina.

*Entregable: `make pruebas` en verde antes de cada push.*

---

## F8 · Instrumentación del estudio

Las tres señales que el medidor ya sabe usar y que la app todavía no captura.

**Cronómetro.** Arranca cuando la tarjeta entra en pantalla, para cuando
respondes. Discreto —una barra fina, no un número que agobie—. En el examen son
7,2 min por pregunta; la meta del plan es bajar a 6. Sin medirlo no se entrena.
Aviso suave a los 6 min: *marca lo que creas y sigue*, que es la regla que salió
del D1.

**Causa del fallo.** Al errar aparecen cuatro botones: concepto · cuentas ·
lectura · tiempo. Un toque. Alimenta la columna `causa` de `errores.csv`, que es
la que produjo la mejor conclusión del diagnóstico.

**Confianza.** Antes de revelar, un 1–4. Con eso sale la gráfica de calibración:
dónde crees que sabes y no sabes. La pregunta 8 del D1 —confianza 4, fallada— es
el caso que esto caza, y es el más peligroso porque nunca lo repasas.

*Riesgo:* pedir dos cosas por pregunta puede volver el feed pesado. Mitigación:
la confianza solo se pide en tarjetas de nivel ALTO y en las de repaso, no en
todas; y la causa solo al fallar.

---

## F9 · Repaso espaciado activo

`pendientesDeRepaso()` ya calcula qué toca a los 3 y 14 días, pero solo pinta un
número. Falta que el feed lo sirva: cuando haya pendientes, abren la sesión con
etiqueta propia y peso máximo. Es la regla de práctica deliberada del plan, y
está a medio camino.

Añadir: una tarjeta falla dos veces seguidas y sube a "hueso" — reaparece cada
tres días hasta que salga bien dos veces.

---

## F10 · Modo simulacro

25 preguntas, 3 horas, sin retroalimentación hasta el final, con la distribución
real del examen: 8 mecánica · 7 E&M y relatividad · 5 termo y estadística ·
5 cuántica y moderna. Pantalla completa, sin barra de navegación, con reloj.

Al terminar: corrección, tiempo por pregunta, acierto por área, y exportación en
el formato exacto de `simulacros.csv` y `respuestas.csv` para que el tablero que
ya existe lo absorba sin tocar nada.

Esto es literalmente S12 y S13 del cronograma. Sin ello la app se queda corta
justo en las dos semanas que deciden.

---

## F11 · Corpus ampliado — aquí es donde el espacio importa

Usamos 5 MB de ~1 GB. Cabe todo esto:

| Fuente | Qué aporta | Dificultad |
|---|---|---|
| **ETS Practice Book** | 100 preguntas del GRE oficial, con capa de texto | baja |
| **Uniandes 2024** | 25 preguntas: **el molde real del examen** | media — las opciones son imágenes y no trae clave |
| **GRE retirados** ×4 | ~400 preguntas del formato más parecido | alta — están escaneados, hay que recortar cada pregunta como imagen |
| **EUF 2020-2 en adelante** | ~400 preguntas cerradas, con texto | media — falta el gabarito |

El simulacro de Uniandes merece trato aparte: es la única muestra del examen
real. Sus opciones son fórmulas en imagen, así que hay que recortarlas una por
una, y la clave hay que tomarla del análisis del D1, marcando cuáles están
derivadas y no confirmadas.

---

## F12 · Explicaciones

El banco HRW da la respuesta y no el porqué. Fallas, ves la letra correcta y
sigues sin entender.

Los solucionarios de grephysics traen el razonamiento completo y ya vienen
etiquetados por tema (`Mechanics → Gauss Law`). Emparejarlos con las preguntas
del GRE da varios cientos de explicaciones de verdad, escritas por físicos.

Para las de HRW más falladas —las que el propio uso vaya señalando— se escriben
a mano, que es donde el esfuerzo rinde más.

---

## F13 · Navegación y cierre

- **Ir a una tarjeta por su código**: escribes `HRW 5.41` y saltas ahí.
- **Filtro por área o por semana**, para cuando estudias un tema concreto.
- **Formulario acumulado**: vista por área con las ecuaciones que más fallas.
  El plan pide "un formulario propio por área"; esto lo genera solo.
- **Marcar para después**, para volver sin perder el hilo.

---

## Orden de ejecución

```
F7  red de seguridad        ← primero, sin excepción
F8  instrumentación          cronómetro · causa · confianza
F9  repaso espaciado
F11 corpus: ETS y Uniandes   las dos de mayor valor por esfuerzo
F10 modo simulacro
F12 explicaciones del GRE
F13 navegación
F11 corpus: GRE escaneados y EUF
```

F7 primero porque todo lo demás se apoya en él. F11 partido en dos porque ETS y
Uniandes son baratas y valiosas, mientras que los GRE escaneados son caros.

---

## Cómo evitamos fallar

1. **Nada se da por bueno sin verlo renderizado.** Lo que se ve en el código no
   es lo que se ve en el teléfono.
2. **Cada bug entra como prueba antes de arreglarse.** Si no, vuelve.
3. **Umbrales, no impresiones.** "Se ve mejor" no es un criterio; "figuras
   cortadas por debajo del 10 %" sí.
4. **Un cambio grande a la vez.** El desastre de los subíndices vino de aplicar
   un reemplazo automático a todo el JSON en vez de a un campo.
5. **Lo que toca datos se prueba contra casos congelados**, porque el corpus se
   regenera y una regresión silenciosa no la ve nadie.

---

*Escrito el 16 de agosto de 2026 · 99 días para el examen*
