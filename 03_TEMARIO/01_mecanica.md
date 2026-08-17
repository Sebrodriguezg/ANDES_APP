# Mecánica — S1, S2, S3 · peso 32 %

El bloque más pesado del examen. Preguntas 1–8 del simulacro.
Estructura: dos semanas de mecánica newtoniana (donde se aprueba) + una de analítica (donde se diferencia).

---

## S1 · 24–30 agosto — Mecánica I: cinemática, Newton, energía, momento

### Temas
Cinemática 1D y 2D · leyes de Newton · fuerzas de ligadura · fricción estática y cinética · planos inclinados y poleas · trabajo y energía · potencia · energía potencial y conservación · momento lineal · impulso · colisiones elásticas e inelásticas · centro de masa

### BASE — leer
- **Serway Vol. 1**, capítulos de cinemática, dinámica, energía y momento (`BIB/1_fisica_general/Serway_Fisica_Vol1_7ed.pdf`)
- **Morin cap. 2** *Statics* (p. 22) y **cap. 3** *Using F = ma* (p. 51)
- **Morin cap. 5** *Conservation of energy and momentum* (p. 138)

### ALTO — leer
- **Kleppner & Kolenkow**, capítulos de dinámica y energía — es Serway con rigor real
- **Tong *Dynamics and Relativity***, parte newtoniana (`BIB/1_fisica_general/Tong_Dynamics_and_Relativity_Cambridge.pdf`)

### PROBLEMAS
| Fuente | Asignación |
|---|---|
| **Irodov** | §1.1 *Kinematics* (p. 11) · §1.2 *The Fundamental Equation of Dynamics* (p. 20) · §1.3 *Laws of Conservation of Energy, Momentum and Angular Momentum* (p. 30) |
| **Morin** | Problemas y ejercicios de caps. 2, 3 y 5 — vienen con solución completa |
| **Lim *Mechanics*** | Parte I §1 *Dynamics of a Point Mass*, problemas **1001–1108** · §2 *Dynamics of a System of Point Masses*, **1109–1144** |
| **MIT OCW 8.01** | `EX/otros_bancos/mit_ocw/8-01sc/` — psets 1 a 6 |

### Viernes — MC cronometrado
GR8677 y GR9277: todas las preguntas de mecánica clásica. Verificar con `GR8677_solutions_grephysics.pdf`.

### Entregable
`../04_ESTUDIO/formularios/mecanica_I.md` + 60 problemas resueltos.

---

## S2 · 31 agosto–6 septiembre — Mecánica II: rotación, gravitación, oscilaciones, fluidos

### Temas
Cinemática y dinámica rotacional · momento de inercia y teorema de ejes paralelos · torque · momento angular y su conservación · rodadura · gravitación universal · leyes de Kepler · energía potencial gravitacional · MAS · péndulos · **oscilaciones amortiguadas y forzadas, resonancia** · estática de fluidos, Arquímedes · ecuación de Bernoulli

### BASE — leer
- **Serway Vol. 1**, capítulos de rotación, gravitación, oscilaciones y fluidos
- **Morin cap. 4** *Oscillations* (p. 101) ← **crítico, es la pregunta 5 del simulacro**
- **Morin cap. 7** *Central forces* (p. 281)
- **Morin cap. 8** *Angular momentum, Part I* (p. 309)

### ALTO — leer
- **Morin cap. 9** *Angular momentum, Part II* (p. 371) — tensor de inercia, precesión
- **Morin cap. 10** *Accelerating frames of reference* (p. 457) — Coriolis, centrífuga
- **Tong *Classical Dynamics***, secciones de cuerpo rígido y fuerzas centrales

### PROBLEMAS
| Fuente | Asignación |
|---|---|
| **Irodov** | §1.4 *Universal Gravitation* (p. 43) · §1.5 *Dynamics of a Solid Body* (p. 47) · §1.7 *Hydrodynamics* (p. 62) · §4.1 *Mechanical Oscillations* (p. 166) |
| **Morin** | Problemas de caps. 4, 7, 8, 9 |
| **Lim *Mechanics*** | Parte I §3 *Dynamics of Rigid Bodies*, **1145–1223** · Parte II §2 *Small Oscillations*, **2028–2067** |
| **MIT OCW 8.01** | psets 7 a 12 |
| **MIT OCW 8.03** | `8-03sc/MIT8_03SCF16_ProblemSet1.pdf` a `ProblemSet3.pdf` — osciladores acoplados y amortiguados |

### Viernes — MC cronometrado
GR9677 y GR0177: preguntas de rotación, gravitación y oscilaciones.

### Entregable
`../04_ESTUDIO/formularios/mecanica_II.md` + 60 problemas. **La fórmula de amplitud del oscilador forzado debe quedar memorizada.**

---

## S3 · 7–13 septiembre — Mecánica III: formalismo analítico

**La semana más rentable del plan.** Tres preguntas del simulacro (6, 7, 8) salen de aquí y son inaccesibles sin haberlas visto. Son ~12 % del examen concentrado en pocos conceptos.

### Temas
Ligaduras y coordenadas generalizadas · principio de Hamilton · **ecuaciones de Lagrange** · coordenadas cíclicas y cantidades conservadas · teorema de Noether · momentos conjugados · transformación de Legendre · **hamiltoniano y ecuaciones canónicas** · **espacio de fase y área encerrada** · variables acción-ángulo · **corchetes de Poisson** · transformaciones canónicas · **scattering, parámetro de impacto y sección eficaz**

### BASE/ALTO — leer (en este orden)
1. **Tong *Classical Dynamics*** (`BIB/2_mecanica_clasica/Tong_Classical_Dynamics_Cambridge.pdf`) — **texto principal de la semana.** Cubre Lagrange, Hamilton, espacio de fase, Poisson y transformaciones canónicas con la concisión adecuada
2. **Morin cap. 6** *The Lagrangian method* (p. 218) — la introducción más suave, con problemas resueltos
3. **Hand & Finch** — segunda pasada, más legible que Goldstein
4. **Goldstein** (español) — solo consulta puntual: scattering y corchetes de Poisson

### Los tres patrones, uno por día
| Día | Patrón | Resultado que debe quedar memorizado |
|---|---|---|
| Mar | **T(E) = dA/dE** | El período de una órbita periódica es la derivada respecto a E del área encerrada en el espacio de fase |
| Mié | **Corchetes de Poisson** | {L_i, p_j} = ε_ijk p_k · {q_i, p_j} = δ_ij · {L_i, L_j} = ε_ijk L_k |
| Jue | **Scattering esfera dura** | b = R cos(θ/2), dσ/dΩ = R²/4 (isótropa), σ_total = πR² |

### PROBLEMAS
| Fuente | Asignación |
|---|---|
| **Lim *Mechanics*** | Parte II §1 *Lagrange's Equations*, **2001–2027** · §3 *Hamilton's Canonical Equations*, **2068–2084** ← el bloque más valioso |
| **Morin** | Problemas del cap. 6 |
| **MIT OCW 8.09** | `8-09/MIT8_09F14_pset1.pdf` a `pset4.pdf` + `MIT8_09F14_Chapter_1.pdf` a `Chapter_4.pdf` |
| **Uniandes** | Exámenes de conocimientos de **Mecánica Analítica** en `EX/uniandes_conocimientos/` — buscar los años con esa sección. Son de desarrollo y sobre-nivel, pero muestran exactamente qué le importa al departamento |

### Viernes — MC cronometrado
Todas las preguntas de mecánica analítica de los 4 exámenes GRE. Son pocas pero siempre caen.

### Entregable
`../04_ESTUDIO/formularios/mecanica_analitica.md` con los tres patrones + 40 problemas.
**Tarjetas Anki** para los tres patrones — se repasan cada semana hasta noviembre.

---

## Autoevaluación del bloque

Antes de pasar a S4, deberías poder responder sin consultar:

- [ ] Bloque sobre bloque con fricción y polea: ¿cuál es la condición de deslizamiento conjunto?
- [ ] Rizo vertical: ¿cuál es la condición en el punto más alto?
- [ ] Oscilador forzado amortiguado: ¿cuál es la amplitud en estado estacionario?
- [ ] ¿Cómo se obtiene el período desde el área en el espacio de fase?
- [ ] ¿Cuánto vale {L_i, p_j}?
- [ ] ¿Cuál es b(θ) para esfera dura y por qué la sección eficaz es isótropa?
- [ ] Dado un lagrangiano, ¿cómo identificas coordenadas cíclicas y qué conservan?

Si fallas alguna, esa es la que repasas — no vuelvas a leer el capítulo entero.
