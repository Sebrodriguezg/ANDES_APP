# PLAN — Examen de admisión Posgrados en Física, Universidad de los Andes

> Objetivo: aprobar el examen de admisión a la **Maestría en Ciencias – Física** (Uniandes).
> Fecha meta: **lunes 23 de noviembre de 2026**. Hoy: 14 de agosto de 2026 → **101 días / 14 semanas**.

---

## 1. Datos duros del proceso (verificados en la web oficial, 14-ago-2026)

| Hito | Fecha |
|---|---|
| Inscripción online | 23-jul → **18-nov-2026, 5:00 p.m.** |
| Entrega de documentos (plataforma) | hasta **19-nov-2026, 11:30 p.m.** |
| **Examen de admisión** | **23-nov-2026**, presencial (hora y salón se avisan el día anterior) |
| Entrevistas | 1 y 2 de diciembre de 2026 |
| Publicación de admitidos | 2 de diciembre de 2026 |

**Costo de inscripción a la Maestría: $0.**

### Formato del examen
- **25 preguntas de selección múltiple**, máximo **3 horas** → **7.2 min/pregunta**.
- Mismo examen para aspirantes a Maestría y a Doctorado.
- Presencial. Se evalúa "el conocimiento fundamental esperado de un egresado de pregrado en Física".
- 5 áreas oficiales:
  1. Física 1 y Física 2
  2. Termodinámica y Física Estadística
  3. Física Moderna y Mecánica Cuántica
  4. Física Clásica
  5. Electromagnetismo

### Documentos requeridos (todos en PDF, ≤1MB c/u)
- Diploma y/o acta de grado (firmados digitalmente, validables en línea)
- Certificado oficial de calificaciones de pregrado
- Hoja de vida
- **Carta de intención** (máx. 1000 palabras; debe nombrar grupo(s) de investigación de interés)
- Dos referencias académicas/profesionales (desde correos institucionales)
- Opcional: carta de solicitud de apoyo financiero (asistencia graduada: 24 h/sem, cubre hasta 100 % de matrícula + salario)

### Ruta alterna: GRE Physics
Puntaje **> percentil 60** en GRE Physics rendido después del 19-oct-2015 **sustituye** el examen y pasa **directo a entrevista**.
- Ventanas ETS: septiembre, octubre y abril (dos semanas por mes).
- Reporte de puntajes: ~5 semanas después de rendirlo.
- ⚠️ **Solo la ventana de septiembre 2026 llega a tiempo** para el corte de documentos del 19-nov.
- ⚠️ **ACCIÓN URGENTE**: verificar fechas exactas 2026 en ets.org e inscribirse. Costo ≈ USD 150.

---

## 2. Radiografía del examen (análisis del simulacro oficial 2024)

Analicé las 25 preguntas del simulacro `01_EXAMENES/uniandes_admision/`. Distribución real:

| Área | Preguntas | Peso | Ejemplos del simulacro |
|---|---|---|---|
| **Mecánica** (Física 1 + Clásica) | 1–8 | **32 %** | rizo con resorte, bloques con fricción y polea, cinemática rotacional, oscilador forzado amortiguado, **área en espacio de fase → T(E)**, **corchetes de Poisson {L_i, p_j}**, scattering esfera dura |
| **Electromagnetismo + Relatividad** | 9–15 | **28 %** | Ampère en conductor hueco, **condición de gauge en potenciales**, dilatación temporal, **esfera a tierra en campo uniforme (armónicos)**, Biot-Savart, superposición de anillos, potencial esfera-cascarón |
| **Termodinámica + Estadística** | 16–20 | **20 %** | coeficiente de expansión lineal, calorimetría con cambios de fase, trabajo por trayectoria p(V), **entropía combinatoria (monedas)**, **energía más probable de dos sistemas en contacto térmico** |
| **Cuántica + Moderna** | 21–25 | **20 %** | **2 bosones en caja 2D**, Doppler relativista + ionización, **escalón de potencial: coeficiente R**, **varianza ⟨(Δx)²⟩(t) en oscilador armónico** |
| **Óptica** | 0 en este simulacro | ~0–4 % | aparece en el temario oficial pero no en la muestra |

### Conclusiones operativas
1. **Es un examen bimodal.** ~60 % es Física 1–2 sólida y rápida (Serway/Sears nivel), ~40 % es pregrado superior (Goldstein-lite, Griffiths E&M, Griffiths QM, Schroeder). No es un qual de doctorado — el `research.md` original apuntaba demasiado alto.
2. **7.2 min/pregunta** es el enemigo real. Muchas respuestas son simbólicas (a/b/c/d/e con fórmulas), lo que permite **análisis dimensional y casos límite** para descartar sin resolver. Esa es una habilidad entrenable y vale tanto como el contenido.
3. **No hay penalización visible por respuesta errada** (formato "Answer: ___", 5 opciones) → **responder siempre las 25**.
4. Los temas "superiores" son repetidamente los mismos 8–10 clásicos: Poisson, espacio de fase, gauge, imagen/armónicos esféricos, escalón de potencial, oscilador cuántico, bosones/fermiones en caja, contacto térmico. **Son memorizables como patrones.**

---

## 3. Inventario del material propio

Barrido completo del disco: **3.058 documentos**, filtrados a los relevantes.
Detalle completo en `02_BIBLIOTECA/INVENTARIO.md`.

### ✅ Ya tienes (y sirve)
| Área | Libro | Ubicación |
|---|---|---|
| Física general | Serway 7ed Vol. 1 y 2 | `Documents/Books/` |
| Física general | Sears-Zemansky Vol. 1 | `Downloads/` |
| Mecánica | Kleppner & Kolenkow | `Downloads/` |
| Mecánica | **Morin — Classical Mechanics with problems and solutions** | `Downloads/` |
| Mecánica clásica | Goldstein (español, Reverté) | `Documents/Metodos/` |
| Mecánica clásica | Hand & Finch — Analytical Mechanics | `Documents/Metodos/` |
| Mecánica clásica | Arnold — Mathematical Methods of CM | `Documents/Metodos/` |
| E&M | Schaum — Electromagnetismo | `Documents/Books/` |
| Termo/Estadística | Pathria & Beale; Huang; Helrich; Feynman Stat Mech; Ma | `Documents/Books/` |
| Cuántica | **Zettili** | `Downloads/` |
| Cuántica | Shankar | `Documents/Metodos/` |
| Moderna | **Eisberg & Resnick** | `Downloads/` |
| Relatividad | Schutz — First Course in GR (+ manual de soluciones) | `Downloads/` |
| **Formato MC** | **Conquering the Physics GRE** | `Downloads/` ← pieza clave |
| Matemáticas | Schaum Análisis Vectorial, Schaum Cálculo Tensorial | `Documents/Books/` |

### ✅ Brechas cerradas el 14-ago-2026

Todo lo que sigue **ya está descargado**. Se conserva la tabla como registro de por qué se pidió cada cosa.
Ver `02_BIBLIOTECA/INVENTARIO.md` para el estado real y la organización por nivel (BASE / ALTO / PROBLEMAS).
| Prioridad | Libro | Para qué |
|---|---|---|
| **P0** | **Griffiths — Introduction to Electrodynamics** | El 28 % del examen. No tienes ningún E&M de nivel intermedio. Crítico. |
| **P0** | **Griffiths — Introduction to Quantum Mechanics** | Zettili sirve pero Griffiths es más rápido para MC. |
| **P0** | **Schroeder — An Introduction to Thermal Physics** | Pathria/Huang son sobre-nivel. Schroeder es exactamente el nivel del examen. |
| **P0** | **GRE Physics — pruebas oficiales ETS** (GR8677, GR9277, GR9677, GR0177 + Practice Book actual) | Gratuitas y públicas. El mejor banco de MC cronometrado que existe. |
| P1 | **Hecht — Optics** | Única área del temario sin cobertura. |
| P1 | **Taylor — Classical Mechanics** | Puente entre Serway y Goldstein; problemas de nivel exacto. |
| P1 | **Boas — Mathematical Methods in the Physical Sciences** | Herramienta transversal. |
| P2 | **Irodov — Problems in General Physics** | Volumen de práctica en Física 1–2. |
| P2 | **Reif — Fundamentals of Statistical and Thermal Physics** | Refuerzo estadística. |
| P3 | Serie **Yung-Kuo Lim** (Mechanics, E&M, QM, Thermo) | Banco de respaldo; sobre-nivel pero útil para los temas "superiores". |

### 🗑️ Descartado (está en disco pero no sirve para este examen)
Toda la biblioteca de física médica/radiológica (`SeminarioI/BOOKS/`), QFT (Peskin, Ryder, Greiner RQM), MHD relativista, dinámica de fluidos, econofísica, HPC/CUDA, estado sólido (Kittel), partículas. Fuera de alcance — no abrir.

---

## 4. Plan de descarga, búsqueda, filtrado y organización

### Fase 0 — Infraestructura ✅ HECHO
Estructura de directorios creada, `research.md` archivado en `_fuentes/`, simulacro incorporado.

### Fase 1 — Cosecha oficial (hoy) 🔄 EN CURSO
1. ✅ **34 exámenes de conocimientos Uniandes 2003–2024** desde
   `fisica.uniandes.edu.co/files/programas/doctorado/examen-conocimientos/` → `01_EXAMENES/uniandes_conocimientos/`
   *(Nota: son exámenes de desarrollo del doctorado, no MC. Sirven para el 40 % "superior" del examen y para saber qué temas obsesionan al departamento — no como simulacro de formato.)*
2. ✅ Temarios oficiales (Electrodinámica, Mecánica Analítica, Mecánica Estadística), reglamento de candidatura y estadísticas históricas → `03_TEMARIO/`
3. ✅ **ETS Practice Book for the GRE Physics Test** (1 examen completo oficial) → `01_EXAMENES/gre_physics/`
4. ⬜ Pruebas oficiales retiradas GR8677 / GR9277 / GR9677 / GR0177 — ya no están en ets.org, hay que buscarlas en mirrors académicos.
5. ⬜ Verificar fechas GRE 2026 en ets.org e inscribirse a la ventana de septiembre.

### Fase 2 — Cierre de brechas bibliográficas ✅ HECHO (14-ago)
Todas las brechas cerradas. Ver `02_BIBLIOTECA/INVENTARIO.md`. Resumen:
- **P0**: Griffiths *Electrodynamics*, Griffiths *QM* 3ª ed., Schroeder *Thermal Physics* ✅
- **Alto calibre libre**: 7 cursos de **David Tong** (Cambridge), **BSc Optics** de TU Delft (CC-BY) ✅
- **Bancos de problemas**: Irodov, serie **Lim** ×4, **Cahn & Nadgorny** parte 2, **Arfken** ✅
- **Formato MC**: 4 exámenes GRE retirados completos + soluciones, ETS Practice Book ✅
- **221 archivos de MIT OCW** (9 cursos, problem sets + exámenes + soluciones) ✅
- **EUF/Brasil**: **35 exámenes 2010–2025** (los de 2020-2 en adelante son de 40 preguntas cerradas) + gabarito oficial UNICAMP + 4 exámenes UFG ✅

Faltantes y dónde conseguirlos: **`00_ADMISION/FALTANTES.md`**. Nada de esa lista es bloqueante.

No se consiguieron en fuente abierta: Taylor *CM*, Boas, Hecht, Purcell, Cahn parte 1, Princeton Problems, Cronin. **Ninguno hace falta** — cada uno tiene sustituto de igual o mayor nivel ya descargado.

⛔ **La fase de descarga queda CERRADA.** A partir de aquí solo se estudia. La trampa de este proyecto es seguir acumulando PDFs.

### Fase 3 — Filtrado y consolidación (semana 1)
- Un archivo por libro, renombrado `Autor_Titulo_ed.pdf`, colocado en su carpeta de área.
- Eliminar duplicados detectados (Sears aparece 2×, Eisberg 3×, Introduction to Magnetism 2×, etc.).
- **Regla de oro: máximo 2 libros por área.** Uno de teoría/referencia + uno de problemas.
- Los libros descartados NO se copian a `02_BIBLIOTECA/`.

### Fase 4 — Desglose tema → fuente → problemas ✅ HECHO (14-ago)
En **`03_TEMARIO/`**, con todas las referencias verificadas contra el índice real de cada PDF:
- `README.md` — cómo usar los tres niveles (BASE / ALTO / PROBLEMAS) y las 4 técnicas de descarte
- `00_mapa_simulacro.md` — **las 24 preguntas del simulacro → tema → capítulo exacto donde estudiarlo**, más los **10 patrones** que hay que memorizar
- `01_mecanica.md` (S1–S3) · `02_electromagnetismo.md` (S4–S6) · `03_termo_estadistica.md` (S7–S8) · `04_moderna_cuantica.md` (S9–S10) · `05_optica_ondas.md` (S11)

Cada semana trae: temas, lectura BASE, lectura ALTO, problemas asignados con rangos concretos, sesión MC del viernes, entregable y checklist de autoevaluación.

Plantillas de seguimiento creadas en `06_SEGUIMIENTO/`: `errores.md` y `metricas.md`.

---

## 5. Calendario — 14 semanas

**Presupuesto sugerido: 15–20 h/semana.** Ajustable, pero por debajo de 12 h/sem el plan no cierra.

| Semana | Fechas | Foco | Entregable |
|---|---|---|---|
| **S0** | 14–23 ago | Infraestructura + descargas + **diagnóstico cronometrado** con el simulacro 2024 | Mapa de fortalezas/debilidades real |
| **S1** | 24–30 ago | **Mecánica I**: cinemática, Newton, energía, momento, colisiones | Formulario Mecánica + 60 problemas |
| **S2** | 31 ago–6 sep | **Mecánica II**: rotación, gravitación, oscilaciones (incl. forzado/amortiguado), fluidos | Formulario + 60 problemas |
| **S3** | 7–13 sep | **Mecánica III**: Lagrange, Hamilton, espacio de fase, Poisson, scattering | Los 10 patrones "superiores" de mecánica dominados |
| **S4** | 14–20 sep | **E&M I**: Coulomb, Gauss, potencial, conductores, dieléctricos, capacitancia | Formulario E&M + 60 problemas |
| **S5** | 21–27 sep | **E&M II**: corrientes, circuitos, Biot-Savart, Ampère, Faraday, inductancia | Formulario + 60 problemas |
| **S6** | 28 sep–4 oct | **E&M III**: Maxwell, potenciales y gauge, ondas EM, imágenes, armónicos esféricos | Patrones "superiores" de E&M |
| **S7** | 5–11 oct | **Termodinámica**: leyes, procesos, calorimetría, máquinas térmicas, entropía | Formulario Termo + 50 problemas |
| **S8** | 12–18 oct | **Física Estadística**: ensambles, contacto térmico, distribuciones, gases cuánticos | Formulario + 50 problemas |
| **S9** | 19–25 oct | **Moderna + Relatividad**: relatividad especial, fotón, átomo, Doppler, De Broglie | Formulario + 50 problemas |
| **S10** | 26 oct–1 nov | **Cuántica**: pozo, escalón/barrera, oscilador, momento angular, operadores, evolución | Formulario + 50 problemas |
| **S11** | 2–8 nov | **Óptica + repaso transversal** | Cerrar el hueco de óptica |
| **S12** | 9–15 nov | **Simulacros cronometrados** (3 completos, 25 preg / 3 h) | Análisis de error por simulacro |
| **S13** | 16–22 nov | **Repaso de errores + formularios + 2 simulacros más**. Últimos 2 días: solo repaso ligero, dormir. ⚠️ **18-nov: cierre inscripción. 19-nov: cierre documentos.** | Listo |
| — | **23 nov** | **EXAMEN** | 🎯 |

### Estructura de una semana tipo
- **Lun–Mar (teoría, ~5 h)**: leer el capítulo, derivar los resultados a mano, construir el formulario del tema.
- **Mié–Jue (problemas, ~7 h)**: 40–60 problemas del libro de práctica, sin límite de tiempo al inicio.
- **Vie (formato MC, ~3 h)**: mismo tema pero en preguntas de opción múltiple cronometradas a 7 min. Aquí entra el GRE.
- **Sáb (repaso activo, ~2 h)**: rehacer de memoria los problemas fallados de la semana + repasar Anki de semanas previas.
- **Dom**: descanso o colchón.

---

## 6. Método de estudio

### Principios
1. **El formato manda.** No es un examen de desarrollo. Entrenar *resolver rápido y descartar*, no *demostrar rigurosamente*. Ojo: tu instinto (y el `research.md` original) apunta a lo contrario.
2. **Técnicas de descarte** como habilidad explícita a entrenar cada viernes:
   - análisis dimensional
   - casos límite (x→0, x→∞, m₁=m₂, sin fricción)
   - signos y simetrías
   - órdenes de magnitud
3. **Práctica deliberada**: cada problema fallado se anota en `06_SEGUIMIENTO/errores.md` con *por qué* falló (concepto / álgebra / lectura / tiempo). Se re-resuelve a los 3 y a los 14 días.
4. **Repetición espaciada** para constantes, fórmulas y los ~10 patrones recurrentes → mazo Anki en `04_ESTUDIO/anki/`.
5. **Formulario propio escrito a mano.** Uno por área. No sirve el de otro.

### Métricas de seguimiento (`06_SEGUIMIENTO/metricas.md`)
- % de acierto por área, por semana
- Tiempo medio por pregunta (meta: ≤ 6 min al llegar a S12)
- Curva de simulacros: meta ≥ 18/25 (72 %) en el último simulacro

---

## 7. Riesgos identificados

| Riesgo | Mitigación |
|---|---|
| **Acumular material y no estudiar** | Regla de 2 libros por área. Fase de descarga cerrada al final de la semana 1, sin excepciones. |
| **Sobre-preparar los temas "de posgrado"** y descuidar Física 1–2 | El 60 % del examen es Física 1–2. S1–S2 y S4–S5 son intocables. |
| **No entrenar contra el reloj** | Cronómetro obligatorio desde S3. Los simulacros de S12–S13 se hacen en condiciones reales: 3 h seguidas, sin celular, papel y lápiz. |
| **Ventana GRE de septiembre se cierra** | Verificar ets.org **esta semana**. Si ya cerró, la ruta GRE muere y todo el peso queda en el 23-nov. |
| ~~Óptica es punto ciego total~~ **resuelto** | Ya hay *BSc Optics* (TU Delft) + MIT 8.03. S11 dedicada. Si el tiempo aprieta, sigue siendo lo primero que se sacrifica (peso ~0–4 %). |
| **Exceso de material** (nuevo riesgo) | 581 MB y ~40 textos. Usar la tabla BASE/ALTO/PROBLEMAS del inventario y no desviarse. Un texto por nivel por semana. |
| **Documentos de admisión a última hora** | Diploma, notas, cartas de referencia y carta de intención listos **antes del 31 de octubre**, no en noviembre. Las referencias dependen de terceros. |

---

## 8. Acciones inmediatas

| # | Acción | Responsable | Plazo |
|---|---|---|---|
| 1 | Verificar fechas GRE Physics 2026 en ets.org e inscribirse (ventana septiembre) | Sebastián | **esta semana** |
| 2 | Descargar pruebas oficiales GRE (ETS) | Claude | hoy |
| 3 | Descargar libros P0 (Griffiths ×2, Schroeder) | Claude + Sebastián | semana 1 |
| 4 | **Simulacro diagnóstico**: el examen 2024, 3 h cronometradas, sin apuntes | Sebastián | antes del 23 ago |
| 5 | Consolidar y deduplicar biblioteca en `02_BIBLIOTECA/` | Claude | semana 1 |
| 6 | Pedir cartas de referencia (2, correos institucionales) | Sebastián | septiembre |
| 7 | Borrador de carta de intención (≤1000 palabras, nombrar grupos de investigación) | Sebastián + Claude | octubre |
| 8 | Inscripción online en la plataforma | Sebastián | **antes del 18-nov** |

---

## 9. Estructura del directorio

```
ANDES/
├── PLAN.md                          ← este archivo
├── 00_ADMISION/                     requisitos, fechas, carta de intención, CV
│   ├── uniandes/
│   └── gre/
├── 01_EXAMENES/
│   ├── uniandes_admision/           simulacro MC oficial (el molde real)
│   ├── uniandes_conocimientos/      34 exámenes de desarrollo 2003–2024
│   ├── gre_physics/                 pruebas oficiales ETS
│   └── otros_bancos/                IPhO, EUF, Balseiro (opcional)
├── 02_BIBLIOTECA/                   máx. 2 libros por área
│   ├── 0_resolucion_problemas/      Conquering the Physics GRE, Irodov, Lim
│   ├── 1_fisica_general/  2_mecanica_clasica/  3_electromagnetismo/
│   ├── 4_termo_estadistica/  5_cuantica_moderna/  6_optica_ondas/  7_matematicas/
│   └── INVENTARIO.md
├── 03_TEMARIO/                      temarios oficiales + desglose tema→fuente
├── 04_ESTUDIO/
│   ├── formularios/                 uno por área, escritos a mano/LaTeX
│   ├── notas/
│   └── anki/
├── 05_SIMULACROS/                   simulacros armados + hojas de respuesta
├── 06_SEGUIMIENTO/                  errores.md, metricas.md, banco_problemas.md
└── _fuentes/                        research.md original y material de investigación
```

---

*Última actualización: 14 de agosto de 2026*
