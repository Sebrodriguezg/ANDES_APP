# Medidor de desempeño — instructivo

Herramienta para **entender tus debilidades**, no solo para calificar respuestas.
Corre en este computador, sin instalar nada: solo Python estándar. Las gráficas son SVG escritos a mano,
así que no se rompe cuando cambie el sistema ni depende de matplotlib.

---

## 1. Los seis comandos

Desde `~/Documents/ANDES/`:

```bash
python3 06_SEGUIMIENTO/medidor.py estado      # resumen rápido + mapa de habilidades
python3 06_SEGUIMIENTO/medidor.py sesion      # registrar una sesión de estudio
python3 06_SEGUIMIENTO/medidor.py skills      # autoevaluar el mapa de habilidades
python3 06_SEGUIMIENTO/medidor.py simulacro   # registrar y calificar un simulacro
python3 06_SEGUIMIENTO/medidor.py error       # registrar un problema fallado suelto
python3 06_SEGUIMIENTO/medidor.py reporte     # generar gráficas + REPORTE.md + tablero.html
```

Todos son interactivos y tienen valores por defecto: puedes pasar rápido dándole Enter.

---

## 2. El mapa de habilidades

Son las **24 habilidades** que evalúa el examen, sacadas del simulacro oficial: mismo listado que
`mapas/uniandes_2024.csv`, agrupadas por área, con los 10 patrones marcados.

Escala:

| | |
|---|---|
| **0** | no lo he visto |
| **1** | lo vi, no me sale |
| **2** | lo entiendo si lo miro |
| **3** | lo resuelvo solo |
| **4** | lo resuelvo rápido |

**Se actualiza solo al inicio de cada sesión:** `medidor.py sesion` y `medidor.py estado` te muestran
el mapa en la terminal antes de pedirte nada, con el promedio por área y los patrones que aún no dominas.

Para reevaluarte (una vez por semana basta):

```bash
python3 06_SEGUIMIENTO/medidor.py skills
```

Recorre las 24 habilidades, te muestra **cuántas has acertado en simulacros** al lado de cada una, y te pide tu nivel.
Enter deja el valor anterior; Ctrl-C sale guardando lo que llevas.

### Lo que hace útil el mapa

La gráfica `00_mapa_habilidades.svg` superpone **dos cosas distintas**:

- **La barra** es tu autoevaluación.
- **El triangulito** es lo que miden los simulacros.

Cuando tu barra va dos niveles o más por encima del triángulo, la fila se pinta de **rojo**.
Esas filas son el problema real de cualquier preparación: temas que crees dominar y por eso nunca
vuelves a repasar. El medidor también te lo avisa en el momento de autoevaluarte.

También hay una **versión impresa** en el cronograma (página 2): la misma tabla con 14 columnas,
una por semana, para ir escribiendo el número a mano. Sirve para verlo sin abrir el computador.

---

## 3. La rutina

### Cada día, al terminar de estudiar (1 minuto)

```bash
python3 06_SEGUIMIENTO/medidor.py sesion
```

Te pregunta área, tipo de sesión, minutos, si hiciste la mínima o la extendida, y dos cosas que
importan más de lo que parece:

- **Energía (1–5):** con qué carga llegaste a la sesión.
- **Claridad (1–5):** qué tan claro te quedó el tema.

La claridad es tu percepción. El acierto en los simulacros es la realidad. **La distancia entre las dos
es el dato más útil de todo el sistema**, porque un tema que crees dominar y no dominas es el que te
hunde el examen: nunca lo vuelves a repasar.

### Cada viernes, después de la sesión de opción múltiple

Si fue un bloque corto, regístralo como `sesion` con tipo `mc`.
Si fue un examen completo con clave, regístralo como `simulacro`.

### Cada simulacro completo

```bash
python3 06_SEGUIMIENTO/medidor.py simulacro
```

El flujo es:

1. Eliges el examen (los que tengan clave o mapa en `claves/` y `mapas/`).
2. **Antes de ver el resultado** te pregunta qué tan bien crees que te fue (1–5). No hagas trampa: es la medición de calibración.
3. Escribes tus respuestas una por una. Enter en blanco = pregunta sin responder.
4. Califica automáticamente contra la clave.
5. **Aquí está lo importante:** por cada pregunta fallada te pregunta *por qué* falló.

Las cinco causas:

| Causa | Significa | Qué implica |
|---|---|---|
| `concepto` | No sabía la física | Falta estudiar. Es la buena noticia: se arregla con el cronograma. |
| `algebra` | Sabía, me equivoqué en cuentas | Sabes física y pierdes puntos gratis. Se arregla verificando dimensiones. |
| `lectura` | Entendí mal el enunciado | En este examen las opciones suelen incluir la respuesta a la pregunta que NO te hicieron. |
| `tiempo` | Sabía hacerlo, no alcancé | No es un problema de conocimiento sino de descarte. |
| `descuido` | Lo tenía y marqué mal | Si pasa seguido, cambia cómo transcribes respuestas. |

**No te saltes este paso.** Un examen calificado sin causas te dice tu nota; con causas te dice qué hacer el lunes.

### Cada domingo (o cuando quieras verte)

```bash
python3 06_SEGUIMIENTO/medidor.py reporte
xdg-open 06_SEGUIMIENTO/tablero.html
```

---

## 4. Qué mira cada gráfica

| Archivo | Qué te dice | Cómo leerla |
|---|---|---|
| `00_mapa_habilidades.svg` | Las 24 habilidades: tu autoevaluación contra lo medido | Las filas rojas son las que crees dominar y no dominas. Empieza por ahí. |
| `01_areas.svg` | Acierto por área, con el peso de cada una en el examen | No mires el % más bajo: mira el producto **peso × déficit**. Un 60 % en Mecánica (33 % del examen) duele más que un 40 % en Óptica (0–4 %). |
| `02_nivel.svg` | **BASE contra ALTO** | La gráfica más importante. BASE = Física 1–2, el 55 % del examen. ALTO = los 10 patrones, el 40 %. Ver abajo cómo decidir. |
| `03_evolucion.svg` | Cómo cambia cada área en el tiempo | Busca líneas planas: un área que no sube en tres simulacros no se arregla con más de lo mismo. |
| `04_causas.svg` | Por qué fallas, desglosado por área | Si domina `concepto` en un área, es falta de estudio. Si domina `tiempo`, ya sabes la física y el problema es el reloj. |
| `05_horas.svg` | Horas efectivas por semana y energía media | Verifica si el presupuesto de 5–10 h se está cumpliendo de verdad. |
| `06_calibracion.svg` | Lo que creías contra lo que sacaste | Rojo = te sobreestimas. Es el sesgo más peligroso. |

---

## 5. Cómo cambiar el cronograma con esto

El reporte trae una sección **«Qué cambiar en el cronograma»** que aplica estas reglas.
Aquí está la lógica, para que puedas decidir tú también:

### Regla 1 — BASE vs ALTO manda sobre todo lo demás

```
BASE < 70 %   →  Deja de estudiar patrones. Vuelve a Sears y al banco HRW.
                 El 55 % del examen es Física 1-2 y ahí es donde se aprueba.
                 Los patrones no te salvan si la base falla.

BASE ≥ 70 % y ALTO < BASE − 15   →  El problema son los patrones.
                 Más problemas de rutina no sirven. Reserva 3 sesiones
                 a los 10 patrones de 03_TEMARIO/00_mapa_simulacro.md.

Ambos ≥ 72 %  →  Ya no es conocimiento, es velocidad.
                 Baja el cronómetro a 6 min y entrena descarte.
```

### Regla 2 — Prioriza por peso, no por debilidad

Ordena las áreas por `peso × (meta − tu %)`. Esa es tu bolsa de puntos disponible.
El reporte ya lo calcula. Óptica pesa 0–4 %: aunque vayas en 0 %, es lo último que se toca.

### Regla 3 — Los puntos baratos primero

En los simulacros del GRE, cada pregunta trae su **P+**: el porcentaje de examinados que la acierta.
Si fallas una pregunta con P+ = 85, no es un tema difícil: es un hueco tonto. El reporte las lista aparte.
**Recuperar esas cuesta menos que aprender un tema nuevo.**

### Regla 4 — De dónde sacar tiempo

Cuando el reporte diga que un área necesita refuerzo, el tiempo sale en este orden:

1. **El domingo comodín** (no rompe nada, está diseñado para eso).
2. **Pasar de MÍNIMA a EXTENDIDA** en las sesiones de esa área.
3. **Las dos sesiones de óptica de la semana 13** (pesan 0–4 %).
4. **Solo si nada de lo anterior alcanza:** recortar la semana de menor peso, nunca las semanas 4 y 7 (los patrones).

### Regla 5 — La calibración cambia cómo estudias, no cuánto

- **Te sobreestimas** (creías más de lo que sacaste): tu sensación de «ya lo sé» no es confiable.
  Deja de decidir qué repasar por sensación; usa la tabla de errores.
- **Te subestimas:** estás gastando sesiones en cosas que ya dominas. Suelta y avanza.

---

## 6. Claves de respuesta

El medidor califica contra archivos en `claves/` (con respuestas) o `mapas/` (solo clasificación de temas).
Formato CSV: `pregunta,correcta,p_mas,area,nivel,tema` — no todas las columnas son obligatorias.

### Lo que ya está cargado

| Archivo | Qué es | Estado |
|---|---|---|
| `claves/ets_gr1775.csv` | Examen oficial del ETS Practice Book, 70 preguntas | **Completo**: respuesta + área + P+ (dificultad real medida sobre examinados reales) |
| `mapas/uniandes_2024.csv` | El simulacro oficial de Uniandes, 24 preguntas | **Sin clave de respuestas.** Trae área, tema, nivel BASE/ALTO y el patrón asociado |

### El caso Uniandes

El Departamento **no publica las respuestas** de su ejemplo de examen. Cuando lo registres, el medidor
te preguntará pregunta por pregunta si acertaste, y tú decides tras resolverlo.
La clasificación por área, nivel y patrón sí funciona igual, que es lo que alimenta el diagnóstico.

Si quieres, pídele a Claude que derive las 24 respuestas contigo en una sesión: se pueden resolver todas.

### Agregar los otros exámenes GRE

Los cuatro GRE retirados (GR8677, GR9277, GR9677, GR0177) traen su clave en los PDF de soluciones
de `01_EXAMENES/gre_physics/`. Para cargarlos, crea `claves/gr8677.csv` así:

```csv
pregunta,correcta,p_mas,area,nivel,tema
1,C,,mecanica,BASE,
2,E,,electromagnetismo,ALTO,
```

`p_mas` puede ir vacío. El área es lo que hace útil el diagnóstico, así que vale la pena llenarla.
Áreas válidas: `mecanica`, `electromagnetismo`, `relatividad`, `termo_estadistica`,
`moderna_cuantica`, `optica`, `otros`. Nivel: `BASE` o `ALTO`.

---

## 7. Los datos

Todo son CSV planos en `datos/`, editables a mano si prefieres:

| Archivo | Qué guarda |
|---|---|
| `sesiones.csv` | Una fila por sesión de estudio, con energía y claridad |
| `simulacros.csv` | Una fila por simulacro, con confianza previa y ánimo |
| `respuestas.csv` | Una fila **por pregunta**: qué marcaste, si acertaste, área, nivel, patrón, causa del fallo |
| `errores.csv` | Problemas fallados fuera de simulacro, con fecha de repaso a 3 y 14 días |
| `habilidades.csv` | Histórico de autoevaluaciones: una fila por habilidad y fecha |

Nada se borra nunca: el histórico completo es lo que permite ver la evolución.
Haz copia de `datos/` de vez en cuando.

---

## 8. Para Claude

`REPORTE.md` se regenera con cada `reporte` y empieza con un bloque dirigido a ti.
**Léelo al inicio de cada sesión de trabajo sobre este proyecto** para saber dónde está Sebastián
sin volver a preguntar: acierto por área, BASE vs ALTO, patrones pendientes, causas dominantes
y las recomendaciones ya calculadas.

Si el reporte tiene más de una semana de antigüedad, pídele que corra `reporte` antes de decidir
cambios al cronograma.

---

## 9. Lo que este sistema no hace

Para que no le pidas lo que no puede dar:

- **No sabe si estudiaste bien**, solo cuánto tiempo dijiste que estudiaste. Los datos valen lo que valga tu honestidad al registrarlos.
- **No predice tu nota.** Los simulacros del GRE son más difíciles y más largos que el examen de Uniandes; un 60 % ahí no es un 60 % allá.
- **Con pocos datos, las conclusiones son ruido.** Necesita al menos 2 simulacros y 3 semanas de sesiones antes de que las recomendaciones signifiquen algo.
- **No reemplaza el criterio.** Si el reporte dice una cosa y tú sabes que ese día estabas enfermo, tienes razón tú.

---

*Creado el 14 de agosto de 2026.*
