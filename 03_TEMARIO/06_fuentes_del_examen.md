# De dónde salen las preguntas del examen

**Hallazgo del 14 de agosto de 2026.** Un contacto en Uniandes indicó que el Departamento arma el examen a partir de ciertos documentos. Lo verifiqué cruzando el simulacro oficial de 2024 contra esas fuentes. **Se confirma.**

Esto cambia la estrategia de estudio para el ~55 % del examen.

---

## Evidencia

### Coincidencias literales con Sears–Zemansky (Young & Freedman), *Física Universitaria* Vol. 1

| Simulacro | Fuente | Grado de coincidencia |
|---|---|---|
| **Pregunta 2** (bloques A y B, polea, bloque C colgante) | **Sears–Zemansky problema 5.88** | **Verbatim.** Mismo enunciado palabra por palabra: "El bloque B con masa de 5.00 kg descansa sobre el bloque A, cuya masa es de 8.00 kg… ¿Qué masa máxima puede tener el bloque C, de modo que A y B aún se deslicen juntos cuando el sistema se suelte del reposo?" |
| **Pregunta 3** (volante a 500 rpm, 30 s, 200 revoluciones) | **Sears–Zemansky problema 9.15** | **Verbatim.** El simulacro toma el literal (b) del problema y lo vuelve opción múltiple |

El patrón: **toman un problema de fin de capítulo de Sears, conservan el enunciado en español y añaden cinco opciones.**

### Coincidencias con el banco de preguntas de Halliday–Resnick–Walker

| Simulacro | Fuente | Grado de coincidencia |
|---|---|---|
| **Pregunta 9** (conductor cilíndrico hueco, radio interno a y externo b, corriente uniforme) | **HRW Test Bank cap. 29, pregunta 37** | Casi verbatim: *"A hollow cylindrical conductor (inner radius = a, outer radius = b) carries a current i uniformly spread over its cross section."* El banco pide la gráfica de B(r); el simulacro pide B en a<r<b |
| **Pregunta 1** (rizo vertical, condición para no perder contacto) | **HRW Test Bank cap. 8, preguntas 39–40** | Misma familia. El banco usa una caída desde altura y; el simulacro cambia el lanzamiento por un resorte |

### Lo que NO encontré

Las preguntas **6, 7, 8, 10, 12, 20, 21, 23, 24** —los patrones de pregrado superior— no están en ninguna de estas dos fuentes. Esas se escriben aparte, probablemente a partir de los cursos de posgrado del Departamento (para eso sirven los 34 exámenes de conocimientos y los temarios oficiales en este directorio).

---

## Las tres fuentes, y qué cubre cada una

| Fuente | Archivo | Cubre | Peso estimado |
|---|---|---|---|
| **Sears–Zemansky Vol. 1 y 2** | `BIB/1_fisica_general/Sears_Zemansky_Fisica_Universitaria_Vol1.pdf` | Física 1 y 2, problemas de fin de capítulo | ~30 % |
| **Banco HRW 7ª ed.** | `EX/banco_hrw/HRW7_Test_Bank_con_respuestas.pdf` | 44 capítulos, **~2.200 preguntas de opción múltiple con respuesta** | ~25 % |
| **Material de posgrado propio** | `EX/uniandes_conocimientos/` + `03_TEMARIO/*.pdf` | Los ~10 patrones de nivel superior | ~40 % |

---

## El banco HRW en detalle

`EX/banco_hrw/HRW7_Test_Bank_con_respuestas.pdf` — 655 páginas, **~2.200 preguntas de cinco opciones, todas con `Ans:`**.
Es el banco del editor para *Fundamentals of Physics*, 7ª ed. Tiene capa de texto: **se puede buscar dentro**.

### Mapa capítulo HRW → semana del plan

| Capítulos HRW | Tema | Semana |
|---|---|---|
| 1–9 | Medición, cinemática, vectores, Newton, trabajo y energía, momento | **S1** |
| 10–15 | Rotación, rodadura, torque, equilibrio, gravitación, fluidos, oscilaciones | **S2** |
| 16–17 | Ondas | S11 |
| 18–20 | Temperatura, calor, primera ley, teoría cinética, entropía y segunda ley | **S7–S8** |
| 21–25 | Carga, campo eléctrico, Gauss, potencial, capacitancia | **S4** |
| 26–31 | Corriente, resistencia, circuitos, campo magnético, campos por corrientes, inducción, oscilaciones EM | **S5** |
| 32–33 | Ecuaciones de Maxwell, ondas EM | **S6** |
| 34–36 | Imágenes, interferencia, difracción | **S11** |
| 37 | Relatividad especial | **S6** |
| 38–40 | Fotones, ondas de materia, átomos | **S9** |
| 41–44 | Sólidos, física nuclear, partículas | *fuera de alcance* |

### Cómo usarlo

**Sustituye a la sesión de opción múltiple del viernes durante S1, S2, S4, S5, S7 y S8.** Es más parecido al examen real que el GRE: mismo formato de cinco opciones, mismo nivel, y en varios casos la misma pregunta.

Regla: al terminar cada semana, resolver **entre 60 y 100 preguntas** de los capítulos correspondientes, cronometradas a 2 min (son más cortas que las del examen real). Corregir con el `Ans:` y anotar los fallos en `06_SEGUIMIENTO/errores.md`.

---

## REA — *The Best Test Preparation for the GRE in Physics* (Molitoris)

`EX/gre_physics/REA_GRE_Physics_Molitoris_4_examenes.pdf` — 406 páginas. Es un escaneo, no se puede buscar dentro.

Dos partes:

**1. GRE Physics Review (pp. 3–76)** — repaso condensado en 7 áreas. Es esencialmente un formulario extendido y coincide con el temario de Uniandes:
- 1 Classical Mechanics (p. 3) — incluye **Lagrangian Mechanics (p. 22)**
- 2 Electromagnetism (p. 26)
- 3 Atomic Physics (p. 45) — Rutherford, espectros, Bohr, láser
- 4 Thermodynamics (p. 50) — incluye **Coefficient of Thermal Expansion (p. 51)** ← pregunta 16 del simulacro
- 5 Quantum Mechanics (p. 57) — pozos, oscilador armónico, **Reflection and Transmission by a Barrier (p. 60)** ← pregunta 23
- 6 Special Relativity (p. 63)
- 7 Optics (p. 66) — ondas mecánicas, óptica geométrica, lentes, interferencia, difracción
- **Table of Information (p. 76)** — tabla de constantes

**2. Cuatro exámenes completos** (pp. 78–406), cada uno con hoja de respuestas, **clave de respuestas y explicaciones detalladas**:

| Test | Examen | Clave | Explicaciones |
|---|---|---|---|
| 1 | p. 79 | p. 109 | p. 110 |
| 2 | p. 153 | p. 185 | p. 186 |
| 3 | p. 233 | p. 264 | p. 265 |
| 4 | p. 317 | p. 351 | p. 352 |

### Cómo usarlo
- El **Review** es el mejor material para armar tus formularios: ya está condensado al nivel correcto. Úsalo como plantilla en cada semana.
- Los **4 exámenes** se suman a los 4 GRE reales → **8 simulacros completos** para S12 y S13. Más que suficiente.

---

## Cambios al plan

1. **Sears–Zemansky sube de "secundario" a fuente primaria** en S1, S2, S4 y S5. Resolver sus problemas de fin de capítulo directamente — algunos van a aparecer en el examen tal cual.
2. **El viernes de opción múltiple cambia de fuente**: banco HRW para las semanas de Física 1–2, GRE para las de nivel superior.
3. **Los formularios se arman sobre el Review de REA**, no desde cero.
4. **S12–S13 tienen 8 simulacros completos** disponibles, no 4.
5. La distribución de estudio no cambia: el 40 % de nivel superior sigue siendo lo que decide el resultado, porque es donde nadie más va preparado.

---

## Nota sobre la página de Ohio State

`https://physics.osu.edu/physics_gre` — revisada. Contiene los cuatro exámenes GRE retirados (GR9277, GR8677, GR9677, GR0177) y el Practice Book de ETS. **Ya los teníamos todos**; de hecho es de ahí que los bajé. No hay nada nuevo en esa página.

---

*Verificado por cruce directo entre el simulacro oficial y las fuentes, el 14 de agosto de 2026.*
