# Plan de explicaciones — que fallar enseñe algo

> Sebastián, 19 de agosto de 2026: *"en mi scroll diario en huecos en el trabajo,
> cuando me equivoco no hay margen para entender mi error, por ende siento que no
> mejoro"*.

Tiene razón, y los números lo respaldan. El corpus son **2.296 preguntas de
opción múltiple y ninguna trae explicación**: la app dice la letra correcta y
pasa a la siguiente. El diagnóstico D1 dijo que **nueve de cada diez fallos son
conceptuales**. Un banco que solo corrige la letra no ataca eso; entrena a
reconocer respuestas, no a entender física.

---

## La restricción, dicha por delante

**No existe solucionario de HRW.** Lo comprobé: en `01_EXAMENES` solo hay
soluciones para los cuatro exámenes GRE de grephysics —ya usadas, son las 95
micro-lecciones— y algunos exámenes del MIT. Las 2.208 preguntas de HRW no
tienen solución publicada en el material.

Así que las explicaciones **hay que escribirlas**. Y ahí está el riesgo que
manda sobre todo el plan:

> Una explicación equivocada es peor que ninguna. Una tarjeta sin explicación te
> deja donde estás; una tarjeta con una explicación mal razonada te enseña
> física falsa, y encima con la autoridad de estar escrita.

De ahí la regla que gobierna cada bloque:

**Toda explicación tiene que llegar a la respuesta registrada.** Si al resolver
el problema no me da la letra que el banco dice, la tarjeta no se publica con
una explicación de compromiso: se aparta a `revision.json` con el desacuerdo
anotado.

### El beneficio que eso trae de regalo

Escribir la explicación obliga a resolver la pregunta. Resolver la pregunta
**verifica la clave**. Es decir: este trabajo no solo añade explicaciones, es la
primera auditoría real de las 2.296 respuestas del banco. Cada desacuerdo que
aparezca es un error del corpus que llevaba ahí desde el principio.

---

## Bloque 0 · Sanear antes de explicar

**Va primero y no es negociable.** Explicar un enunciado corrupto no arregla
nada: congela el error y encima lo justifica.

Al revisar el formulario apareció algo que no sabíamos. `pdftotext` **borra en
silencio** los glifos que la fuente de símbolos de HRW no sabe mapear. `mutool`
sí los marca, con el carácter de reemplazo `U+FFFD`, y así se pueden contar: **968 glifos perdidos**.

| Qué se perdió | Cuántos | Gravedad |
|---|---|---|
| `≠` leído como `=` | 28 | **Invierte el enunciado** |
| Flecha de vector (`→A`) | ~290 | Borra la distinción vector/escalar |
| `ℓ`, número cuántico orbital | 10 visibles, 0 en todo el corpus | Rompe la pregunta |
| Otros sin clasificar | ~640 | Por determinar |

Los 28 del `≠` son el caso grave. Ejemplo real, de una pregunta de ondas:

```
En el PDF:   A. f_s = f_a  pero  λ_s ≠ λ_a
En el banco: A. f_s = f_a  pero  λ_s = λ_a
```

La opción dejó de decir lo que decía. Y esto explica de dónde salían las 23
preguntas con opciones duplicadas que filtramos hace unos días: no eran erratas
de HRW, **eran nuestras**.

También entran en este bloque los dos fallos del formulario del 19 de agosto:

1. **El cronómetro no se detiene** al salir de la app. *"Va por una hora"*. Se
   pausa con `visibilitychange` y se le pone un tope; sin eso, la métrica de
   tiempo —que es la que salió del D1— está contaminada.
2. **La `ℓ` perdida**, que es el caso concreto que reportaste.

*Entregable: corpus reextraído con verificación cruzada mutool/pdftotext, una
prueba congelada por cada clase de glifo, y una comprobación en el portero de
que la `ℓ` y el `≠` existen en el corpus.*

---

## Cómo es una explicación

Tres partes, y en este orden. Corta a propósito: se lee en un hueco del trabajo,
de pie, en el teléfono.

1. **La idea** — una línea. Qué concepto decide la pregunta.
2. **El camino** — de dos a cinco pasos, con las fórmulas en LaTeX.
3. **Por qué fallan las otras** — qué error concreto te lleva a cada distractor.

La tercera parte es la que más importa y la que ningún banco trae. En opción
múltiple los distractores no son aleatorios: cada uno es un error típico hecho
carne. Saber *cuál* error te llevó a marcar la `d` vale más que saber que era la
`b`. Y con nueve de diez fallos conceptuales, es exactamente tu problema.

### Dónde vive y cómo se sirve

- Un archivo por capítulo: `07_APP/explicaciones/hrw-c06.json`, indexado por id
  de tarjeta. Un bloque = unos pocos archivos, y el diff se puede revisar.
- `construir_contenido.py` las une a la tarjeta como campo `explicacion`.
- `tarjetas.js` la pinta en `revelar()`, justo debajo del veredicto, al
  responder. Sin toque extra: si fallaste, la explicación ya está ahí.
- El portero mide el porcentaje de tarjetas con explicación y **falla si alguna
  explicación contradice la clave**.

---

## Los bloques

Ordenados por valor, que es peso en el examen cruzado con lo que el D1 dejó al
descubierto. No por número de capítulo.

| # | Bloque | Tarjetas | % examen | D1 | Por qué aquí |
|---|---|---|---|---|---|
| **0** | Saneamiento | — | — | — | Bloqueante |
| **1** | Examen real: ETS + EUF + Uniandes | 88 | — | — | Máximo valor por tarjeta: es el molde real. Y sirve para calibrar el ritmo |
| **2** | Termodinámica y estadística (caps. 18–20) | 218 | 20 % | **0/2** | Mucho peso, cero base, solo tres capítulos |
| **3** | Cuántica y moderna (caps. 38–42) | 267 | 20 % | **0/2** | Igual: mucho peso, cero base |
| **4** | Mecánica I — cinemática y Newton (caps. 1–5) | 212 | 32 % | 1/4 | El bloque más grande del examen |
| **5** | Mecánica II — energía y momento (caps. 6–10) | 285 | 32 % | 1/4 | |
| **6** | Mecánica III — rotación y oscilaciones (caps. 11–15) | 255 | 32 % | 1/4 | |
| **7** | E&M I — campo y potencial (caps. 21–25) | 188 | 28 % | 1/3 | |
| **8** | E&M II — circuitos y magnetismo (caps. 26–30) | 230 | 28 % | 1/3 | |
| **9** | E&M III — inducción y Maxwell (caps. 31–33) + relatividad (37) | 276 | 28 % | 1/3 | |
| **10** | Ondas y óptica I (caps. 16–17, 34) | 183 | 4 % | — | Óptica no salió en el simulacro de 2024 |
| **11** | Ondas y óptica II (caps. 35–36) | 94 | 4 % | — | Lo último, y sacrificable si aprieta |

Los ocho bloques de HRW suman 1.723, más 218 de termo y 267 de cuántica: 2.208.
Con las 88 de examen real, **2.296**.

**El orden no es caprichoso.** Termo y cuántica van antes que mecánica aunque
mecánica pese más, porque en mecánica sacaste 1/4 y en termo y cuántica sacaste
0/2 y escribiste «no sé nada». Ahí el rendimiento por explicación escrita es
mayor.

---

## Ritmo, y por qué el bloque 1 va primero

No sé todavía cuántas explicaciones por sesión puedo escribir **con
verificación de verdad**, y prefiero no inventarme una cifra. Por eso el bloque
1 son 88 tarjetas: es lo bastante pequeño para terminarlo y lo bastante grande
para medir. Al acabarlo sabremos el ritmo real y el calendario de los diez
bloques restantes deja de ser una suposición.

Lo que sí se puede decir ahora: quedan **96 días** para el examen, y la app está
en mantenimiento justamente para que el tiempo vaya al estudio. Este trabajo lo
hago yo; el tuyo sigue siendo el cronograma.

---

## Cómo sabremos que no se degradó

1. **Ninguna explicación se publica sin llegar a la clave registrada.** El
   desacuerdo va a `revision.json` y lo miramos juntos.
2. **Cada clase de glifo perdido entra como prueba** antes de arreglarse, como
   el resto de la tubería.
3. **El portero gana dos medidas**: cobertura de explicaciones y contradicciones
   con la clave, esta última con tope cero.
4. **Nada se da por bueno sin verlo renderizado a 414 px.** Una explicación de
   cinco pasos con fórmulas ocupa mucho más que un enunciado, y el sitio donde
   se lee es un teléfono en un hueco de veinte minutos.

---

*Escrito el 19 de agosto de 2026 · 96 días para el examen · 2.296 tarjetas sin
explicación, 968 glifos que recuperar*
