# Desglose tema → fuente → problemas

Este directorio convierte el calendario de `PLAN.md` en asignaciones concretas.
**Todas las referencias a capítulos, secciones y rangos de problemas fueron verificadas contra el índice real de cada PDF** — no son de memoria.

## Archivos

| Archivo | Cubre | Semanas | Peso en el examen |
|---|---|---|---|
| `00_mapa_simulacro.md` | Las 24 preguntas del simulacro oficial → tema → dónde estudiarlo | — | — |
| `01_mecanica.md` | Física 1 + mecánica analítica | S1–S3 | **32 %** |
| `02_electromagnetismo.md` | Física 2 + E&M intermedio + relatividad | S4–S6 | **28 %** |
| `03_termo_estadistica.md` | Termodinámica + física estadística | S7–S8 | **20 %** |
| `04_moderna_cuantica.md` | Física moderna + mecánica cuántica | S9–S10 | **20 %** |
| `05_optica_ondas.md` | Óptica y ondas | S11 | **0–4 %** |
| **`06_fuentes_del_examen.md`** | **De dónde salen literalmente las preguntas.** Léelo antes que nada | — | — |

También hay aquí los **temarios oficiales en PDF** del Departamento (Electrodinámica, Mecánica Analítica, Mecánica Estadística), el reglamento del examen de candidatura y las estadísticas históricas.

## Convenciones de ruta

- `BIB/` = `../02_BIBLIOTECA/`
- `EX/`  = `../01_EXAMENES/`

## Los tres niveles

Cada semana tiene tres bloques. **No se leen los tres textos completos.**

| Nivel | Qué es | Cuánto tiempo |
|---|---|---|
| **BASE** | El 60 % del examen. Nivel Física 1–2. Se lee rápido y se resuelve mucho. | ~30 % |
| **ALTO** | El 40 % restante: los patrones de pregrado superior. Son pocos y repetidos. | ~20 % |
| **PROBLEMAS** | Donde se gana el examen. Resolver, fallar, anotar, repetir. | ~50 % |

## Ritmo objetivo

| Momento | Meta |
|---|---|
| S1–S3 | Resolver bien, sin reloj |
| S4–S8 | Reloj activo: 10 min/problema |
| S9–S11 | 7 min/problema |
| S12–S13 | 6 min/problema en simulacro completo |

## Regla de los viernes

Cada viernes, **sin excepción**, una sesión de opción múltiple cronometrada sobre el tema de la semana. Registrar el resultado en `../06_SEGUIMIENTO/metricas.md`.

**De dónde sacar las preguntas** (ver `06_fuentes_del_examen.md`):

| Semanas | Fuente | Por qué |
|---|---|---|
| S1, S2, S4, S5, S7, S8 | **Banco HRW** (`EX/banco_hrw/`) | ~2.200 preguntas de 5 opciones con respuesta. Es una de las fuentes reales del examen |
| S3, S6, S9, S10, S11 | **GRE** (`EX/gre_physics/`) | Cubre el nivel superior, que el banco HRW no alcanza |

## Las cuatro técnicas de descarte

A entrenar explícitamente cada viernes. Con 7.2 min/pregunta, muchas veces es más rápido descartar que resolver:

1. **Análisis dimensional** — ¿las unidades de cada opción cierran?
2. **Casos límite** — x→0, x→∞, m₁=m₂, sin fricción, v≪c, T→0
3. **Signos y simetrías** — ¿el campo apunta hacia donde debe? ¿la energía crece o decrece?
4. **Órdenes de magnitud** — descarta opciones que difieren por factores absurdos

---

*Creado el 14 de agosto de 2026*
